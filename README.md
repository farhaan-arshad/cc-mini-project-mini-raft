# Mini-RAFT Distributed Drawing Board

A distributed real-time collaborative drawing board built with a Mini-RAFT consensus protocol. Multiple users can draw on a shared canvas simultaneously, and the system maintains consistency and availability even when individual servers crash or restart.

---

## Team Members

| Member | Name | SRN | Responsibility |
|--------|------|-----|----------------|
| 1 | Dhriti | PES2UG23AM032 | Frontend + Canvas |
| 2 | Farhaan | PES2UG23AM035 | Gateway Service |
| 3 | Aryan | PES2UG23AM912 | RAFT Core Logic (Replicas) |
| 4 | Nandu | PES2UG23AM055 | Docker + DevOps + Docs |

---

## Project Overview

Users draw on a browser canvas, and drawing strokes are propagated in real-time to all connected clients. The backend is a cluster of three replica nodes that maintain a shared stroke log through a Mini-RAFT consensus protocol. A Gateway service manages all WebSocket connections from the browser.

Even if any replica is restarted, hot-reloaded, or replaced, the system maintains availability and preserves consistent state with zero downtime.

---

## Folder Structure

```
mini-raft-drawing-board/
├── docker-compose.yml          # Full cluster setup
├── .env                        # Shared environment variables
├── README.md
│
├── frontend/                   # Member 1 — Dhriti
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── gateway/                    # Member 2 — Farhaan
│   ├── Dockerfile
│   ├── requirements.txt
│   └── gateway.py
│
├── replica/                    # Member 3 — Aryan
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── replica.py
│   ├── state.py
│   ├── election.py
│   ├── heartbeat.py
│   ├── replication.py
│   ├── log.py
│   ├── sync.py
│   └── routes.py
│
├── scripts/                    # Member 4 — Nandu
│   ├── kill_leader.sh
│   ├── restart_replica.sh
│   └── stress_test.py
│
└── docs/                       # Member 4 — Nandu
    ├── architecture.md
    ├── api_spec.md
    └── state_transitions.md
```

---

## Member Contributions

### Member 1 — Dhriti (PES2UG23AM032) — Frontend + Canvas
**Folder:** `/frontend`

- Browser canvas with mouse and touch drawing support
- WebSocket client that sends stroke data as JSON to the Gateway
- Real-time rendering of incoming strokes from other users
- Reconnect logic when the WebSocket drops during a leader failover
- Multi-tab testing to verify consistent canvas state across clients
- No flicker or canvas reset during backend failures

---

### Member 2 — Farhaan (PES2UG23AM035) — Gateway Service
**Folder:** `/gateway`

- Async WebSocket server that accepts all browser connections
- Maintains a `current_leader` reference, updated during leader changes
- Forwards incoming stroke JSON to the active leader via HTTP POST
- Broadcasts committed strokes back to all connected clients
- Probes replicas on startup to discover the current leader
- Handles failover by detecting leader downtime and re-routing to the new leader

---

### Member 3 — Aryan (PES2UG23AM912) — RAFT Core Logic
**Folder:** `/replica`

- Node state machine: `FOLLOWER → CANDIDATE → LEADER`
- RPC endpoints: `/request-vote`, `/append-entries`, `/heartbeat`, `/sync-log`, `/client-stroke`, `/status`
- Election timeout loop with random 500–800ms delay
- Leader heartbeat loop every 150ms to suppress elections
- Majority-commit logic: marks a stroke committed when ≥2 replicas acknowledge
- Catch-up synchronisation for restarted nodes via `/sync-log`
- Term safety: immediately reverts to Follower when a higher term is seen

---

### Member 4 — Nandu (PES2UG23AM055) — Docker + DevOps + Docs
**Folders:** `/scripts`, `/docs`, root files

- `docker-compose.yml` defining all 4 services, shared network, ports, and env vars
- Bind-mount hot-reload for all 3 replicas using `uvicorn --reload`
- Each replica assigned `REPLICA_ID`, `REPLICA_PORT`, and `PEERS` via environment variables
- Chaos scripts: `kill_leader.sh`, `restart_replica.sh`, `stress_test.py`
- Observability: verified logs for elections, term changes, commits, and catch-up events
- Architecture document, API specification, and state transition diagrams
- Demo video (8–10 minutes) showing all failure and recovery scenarios

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML5 Canvas, Vanilla JS, WebSocket API |
| Gateway | Python, FastAPI, websockets, httpx, uvicorn |
| Replicas | Python, FastAPI, asyncio, httpx, uvicorn |
| Infrastructure | Docker, docker-compose |

---

## Running the Project

```bash
# Clone the repo
git clone <repo-url>
cd mini-raft-drawing-board

# Start all services
docker-compose up --build

# Open the drawing board
# Visit http://localhost:3000 in your browser
# Open multiple tabs to test real-time collaboration
```

---

## Mini-RAFT Protocol Summary

| Parameter | Value |
|-----------|-------|
| Election timeout | Random 500–800 ms |
| Heartbeat interval | 150 ms |
| Majority quorum | ≥ 2 of 3 replicas |
| Commit rule | Entry committed when majority acknowledges |
| Catch-up | Restarted node syncs via `/sync-log` from leader |

---

## Key Features

- **Leader election** — automatic with term-based voting
- **Log replication** — strokes replicated to all followers before commit
- **Zero-downtime reload** — editing a replica file triggers hot-reload without dropping clients
- **Catch-up sync** — restarted nodes automatically recover their full stroke log
- **Fault tolerance** — system stays live as long as ≥ 2 of 3 replicas are running

---

## Viva Topics

- Consensus and fault tolerance (etcd, Consul, CockroachDB)
- Zero-downtime deployments (blue-green / rolling upgrades)
- State replication and event ordering
- Containerisation and service isolation
- Real-time systems with WebSockets
