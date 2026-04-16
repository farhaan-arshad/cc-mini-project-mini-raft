# Mini-RAFT Distributed Drawing Board

A distributed real-time collaborative drawing board with Mini-RAFT consensus protocol. Multiple users draw simultaneously with automatic leader election and zero-downtime failover.

## Team

| Member | Name | Role |
|--------|------|------|
| Dhriti | PES2UG23AM032 | Frontend + Canvas |
| Farhaan | PES2UG23AM035 | Gateway Service |
| Aryan | PES2UG23AM912 | RAFT Core Logic |
| Nandu | PES2UG23AM055 | Docker + DevOps |

## Tech Stack

- **Frontend:** HTML5 Canvas, Vanilla JS, WebSocket
- **Backend:** Python, FastAPI, asyncio, uvicorn
- **Infrastructure:** Docker, docker-compose
- **Consensus:** Mini-RAFT (3 replicas, majority quorum)

## Quick Start

```bash
# Start all services (frontend, gateway, 3 replicas)
docker-compose up --build

# View all services
docker-compose ps

# Stop all services
docker-compose down
```

Open browser: **http://localhost:3000**

---

## Monitoring

```bash
# View logs
docker-compose logs -f                  # All services
docker-compose logs -f replica1         # Specific replica

# Check replica status (LEADER/FOLLOWER, term, log size)
curl -s http://localhost:8001/status | python3 -m json.tool
curl -s http://localhost:8002/status | python3 -m json.tool
curl -s http://localhost:8003/status | python3 -m json.tool
```

---

## Testing & Chaos Scripts

### 1. Kill the Leader

```bash
chmod +x scripts/kill_leader.sh
./scripts/kill_leader.sh
```
Simulates leader failure. New leader elected within 800ms, drawing continues with zero downtime.

### 2. Restart a Replica

```bash
chmod +x scripts/restart_replica.sh
./scripts/restart_replica.sh replica1   # Restart replica1, 2, or 3
```
Replica rejoin cluster and syncs log automatically.

### 3. Stress Test

```bash
pip install websockets
python3 scripts/stress_test.py
```
Sends 100 concurrent strokes (5 clients × 20 strokes). Shows throughput and timing.

---

## Architecture

- **3 Replicas:** RAFT consensus, leader election, log replication
- **Gateway:** WebSocket server, manages client connections, routes to leader
- **Frontend:** Browser canvas, real-time rendering via WebSocket

### RAFT Parameters

| Parameter | Value |
|-----------|-------|
| Election timeout | 500–800 ms (random) |
| Heartbeat interval | 150 ms |
| Quorum | ≥ 2 of 3 replicas |

---

## Key Features

✓ Leader election with term-based voting  
✓ Log replication to majority before commit  
✓ Automatic catch-up sync for restarted nodes  
✓ Zero-downtime hot-reload (edit code, services restart via `--reload`)  
✓ Fault tolerance while ≥2 replicas running
