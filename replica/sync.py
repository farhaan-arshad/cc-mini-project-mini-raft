# Catch-up sync logic for restarted nodes
import httpx
from state import NodeState

async def sync_log_to_follower(state, log, follower_url: str, from_index: int):
    if state.state != NodeState.LEADER:
        return

    missing_entries = log.get_entries_from(from_index)
    print(f"[{state.replica_id}] Syncing {len(missing_entries)} entries to {follower_url}")

    async with httpx.AsyncClient(timeout=2.0) as client:
        try:
            await client.post(f"{follower_url}/sync-log", json={
                "term": state.current_term,
                "leader_id": state.replica_id,
                "from_index": from_index,
                "entries": missing_entries,
                "commit_index": state.commit_index,
            })
        except Exception as e:
            print(f"[{state.replica_id}] Sync failed to {follower_url}: {e}")
            