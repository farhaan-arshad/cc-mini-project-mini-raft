import asyncio
import random
import httpx
from state import NodeState

ELECTION_TIMEOUT_MIN = 0.5
ELECTION_TIMEOUT_MAX = 0.8

# Shared heartbeat tracker
last_heartbeat_time = 0.0

def record_heartbeat():
    global last_heartbeat_time
    import time
    last_heartbeat_time = time.time()

async def election_loop(state, log):
    import time
    record_heartbeat()  # initialise on startup

    while True:
        timeout = random.uniform(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX)
        start_time = time.time()
        
        # Poll until timeout or heartbeat received
        while True:
            await asyncio.sleep(0.05)  # Check every 50ms
            
            if state.state == NodeState.LEADER:
                break  # Leader doesn't participate in elections
            
            elapsed = time.time() - start_time
            time_since_heartbeat = time.time() - last_heartbeat_time
            
            if time_since_heartbeat < timeout:
                break  # Heartbeat received, reset timer
            
            if elapsed >= timeout:
                # Timeout reached with no heartbeat — start election
                print(f"[{state.replica_id}] Election timeout! Starting election...")
                await start_election(state, log)
                break

async def start_election(state, log):
    state.become_candidate()

    vote_request = {
        "term": state.current_term,
        "candidate_id": state.replica_id,
        "last_log_index": log.get_last_log_index(),
        "last_log_term": log.get_last_log_term(),
    }

    async with httpx.AsyncClient(timeout=1.0) as client:
        for peer in state.peers:
            try:
                response = await client.post(
                    f"{peer}/request-vote", json=vote_request
                )
                data = response.json()

                if data.get("term", 0) > state.current_term:
                    state.reset_to_follower(data["term"])
                    return

                if data.get("vote_granted"):
                    state.votes_received += 1
                    print(
                        f"[{state.replica_id}] Got vote from {peer}. "
                        f"Total: {state.votes_received}"
                    )

                majority = (len(state.peers) + 1) // 2 + 1
                if state.votes_received >= majority:
                    state.become_leader()
                    return

            except Exception as e:
                print(f"[{state.replica_id}] Could not reach {peer}: {e}")