# Main entry point, reads env vars for REPLICA_ID etc
import asyncio
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from state import State
from log import Log
import election
import heartbeat
import replication
import sync
import routes

# --- Load env vars ---
REPLICA_ID = os.getenv("REPLICA_ID", "replica1")
REPLICA_PORT = int(os.getenv("REPLICA_PORT", "8001"))
PEERS = os.getenv("PEERS", "").split(",")
PEERS = [p.strip() for p in PEERS if p.strip()]

# --- Init shared state ---
node_state = State(replica_id=REPLICA_ID, peers=PEERS)
node_log = Log(state=node_state)

# --- Init FastAPI ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Inject dependencies into routes ---
routes.init(node_state, node_log, replication, sync)
app.include_router(routes.router)

# --- Background tasks ---
@app.on_event("startup")
async def startup():
    print(f"[{REPLICA_ID}] Starting up on port {REPLICA_PORT} | Peers: {PEERS}")
    asyncio.create_task(election.election_loop(node_state, node_log))
    asyncio.create_task(heartbeat.heartbeat_loop(node_state))