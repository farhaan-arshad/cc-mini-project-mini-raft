# AppendEntries sender and majority-commit tracker
import httpx
from state import NodeState

GATEWAY_URL = "http://gateway:8000"

async def replicate_entry(state, log, entry: dict):
    if state.state != NodeState.LEADER:
        return False

    index = log.get_last_log_index()
    term = state.current_term

    payload = {
        "term": term,
        "leader_id": state.replica_id,
        "prev_log_index": index - 1,
        "prev_log_term": log.get_last_log_term() if index > 0 else 0,
        "entry": entry,
        "commit_index": state.commit_index,
    }

    acks = 1  # Leader counts itself
    async with httpx.AsyncClient(timeout=1.0) as client:
        for peer in state.peers:
            try:
                response = await client.post(f"{peer}/append-entries", json=payload)
                data = response.json()

                if data.get("term", 0) > state.current_term:
                    state.reset_to_follower(data["term"])
                    return False

                if data.get("success"):
                    acks += 1

            except Exception as e:
                print(f"[{state.replica_id}] Replication failed to {peer}: {e}")

    majority = (len(state.peers) + 1) // 2 + 1
    if acks >= majority:
        log.commit(index)
        print(f"[{state.replica_id}] Majority reached. Broadcasting to gateway...")
        await broadcast_to_gateway(entry)
        return True

    return False

async def broadcast_to_gateway(entry: dict):
    async with httpx.AsyncClient(timeout=2.0) as client:
        try:
            await client.post(f"{GATEWAY_URL}/broadcast", json=entry)
        except Exception as e:
            print(f"[Replication] Failed to broadcast to gateway: {e}")
            