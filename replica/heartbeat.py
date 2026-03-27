# Leader heartbeat sender (every 150ms)
import asyncio
import httpx
from state import NodeState

HEARTBEAT_INTERVAL = 0.15  # 150ms

async def heartbeat_loop(state):
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL)

        if state.state != NodeState.LEADER:
            continue

        async with httpx.AsyncClient(timeout=1.0) as client:
            for peer in state.peers:
                try:
                    await client.post(f"{peer}/heartbeat", json={
                        "term": state.current_term,
                        "leader_id": state.replica_id,
                    })
                except Exception as e:
                    print(f"[{state.replica_id}] Heartbeat failed to {peer}: {e}")
                    