import asyncio
from fastapi import APIRouter
from pydantic import BaseModel
from state import NodeState
from election import record_heartbeat

router = APIRouter()

# These will be injected from replica.py
state = None
log = None
replication = None
sync = None

def init(s, l, rep, syn):
    global state, log, replication, sync
    state = s
    log = l
    replication = rep
    sync = syn

# --- Models ---
class VoteRequest(BaseModel):
    term: int
    candidate_id: str
    last_log_index: int
    last_log_term: int

class AppendEntriesRequest(BaseModel):
    term: int
    leader_id: str
    prev_log_index: int
    prev_log_term: int
    entry: dict
    commit_index: int

class HeartbeatRequest(BaseModel):
    term: int
    leader_id: str

class SyncLogRequest(BaseModel):
    term: int
    leader_id: str
    from_index: int
    entries: list
    commit_index: int

class StrokeRequest(BaseModel):
    type: str
    x1: float
    y1: float
    x2: float
    y2: float
    color: str
    width: int

# --- /request-vote ---
@router.post("/request-vote")
async def request_vote(req: VoteRequest):
    if req.term < state.current_term:
        return {"term": state.current_term, "vote_granted": False}

    if req.term > state.current_term:
        state.reset_to_follower(req.term)

    already_voted = state.voted_for not in (None, req.candidate_id)
    if already_voted:
        return {"term": state.current_term, "vote_granted": False}

    state.voted_for = req.candidate_id
    print(f"[{state.replica_id}] Voted for {req.candidate_id} in term {req.term}")
    return {"term": state.current_term, "vote_granted": True}

# --- /append-entries ---
@router.post("/append-entries")
async def append_entries(req: AppendEntriesRequest):
    if req.term < state.current_term:
        return {"term": state.current_term, "success": False}

    record_heartbeat()  # treat append-entries as heartbeat too
    state.reset_to_follower(req.term)
    state.current_leader = req.leader_id

    # Check if log is behind
    if req.prev_log_index >= 0:
        if len(state.log) <= req.prev_log_index:
            return {
                "term": state.current_term,
                "success": False,
                "log_length": len(state.log)
            }

    log.append(req.entry, req.term)

    if req.commit_index > state.commit_index:
        log.commit(req.commit_index)

    return {"term": state.current_term, "success": True}

# --- /heartbeat ---
@router.post("/heartbeat")
async def heartbeat(req: HeartbeatRequest):
    if req.term < state.current_term:
        return {"term": state.current_term, "success": False}

    record_heartbeat()  # reset election timer
    state.reset_to_follower(req.term)
    state.current_leader = req.leader_id
    return {"term": state.current_term, "success": True}

# --- /sync-log ---
@router.post("/sync-log")
async def sync_log(req: SyncLogRequest):
    if req.term < state.current_term:
        return {"term": state.current_term, "success": False}

    state.reset_to_follower(req.term)
    state.current_leader = req.leader_id

    for item in req.entries:
        log.append(item["entry"], item["term"])

    log.commit(req.commit_index)
    print(f"[{state.replica_id}] Synced {len(req.entries)} entries from leader")
    return {"term": state.current_term, "success": True}

# --- /client-stroke ---
@router.post("/client-stroke")
async def client_stroke(req: StrokeRequest):
    if state.state != NodeState.LEADER:
        return {"success": False, "reason": "not leader", "leader": state.current_leader}

    entry = req.dict()
    log.append(entry, state.current_term)
    success = await replication.replicate_entry(state, log, entry)
    return {"success": success}

# --- /status ---
@router.get("/status")
async def status():
    return {
        "replica_id": state.replica_id,
        "state": state.state.value,
        "term": state.current_term,
        "leader": state.current_leader,
        "log_length": len(state.log),
        "commit_index": state.commit_index,
    }