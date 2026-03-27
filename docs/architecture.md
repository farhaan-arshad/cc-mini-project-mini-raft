# Cluster diagram, RAFT design, failure scenarios
# Architecture Document

## Project Overview
A distributed real-time collaborative drawing board backed by a Mini-RAFT 
consensus protocol. Users draw on a shared browser canvas and strokes are 
replicated across a cluster of three replica nodes.

---

## Cluster Diagram
```
Browser Clients
      |
      | WebSocket
      |
   Gateway (port 8000)
      |
      | HTTP (forward stroke to leader)
      |
  ┌───┴────────────────────┐
  │                        │
Replica1     Replica2     Replica3
(port 8001)  (port 8002)  (port 8003)
  │                        │
  └──── RAFT RPCs ─────────┘
       (votes, heartbeats,
        append-entries)
```

---

## Component Responsibilities

### Gateway
- Accepts WebSocket connections from browsers
- Discovers the current leader by probing replicas
- Forwards strokes to the leader via HTTP POST
- Broadcasts committed strokes back to all clients

### Replicas
- Implement Mini-RAFT consensus
- Maintain an append-only stroke log
- Elect a leader via term-based voting
- Replicate log entries to followers
- Commit entries on majority acknowledgement

### Frontend
- HTML5 canvas for drawing
- WebSocket client for sending and receiving strokes
- Auto-reconnects on disconnect

---

## RAFT Protocol Design

### Node States
- FOLLOWER — waits for heartbeats from leader
- CANDIDATE — requests votes from peers
- LEADER — replicates entries, sends heartbeats

### Timings
| Parameter | Value |
|-----------|-------|
| Election timeout | Random 500–800ms |
| Heartbeat interval | 150ms |
| Majority quorum | 2 of 3 replicas |

### Log Entry Format
```json
{
  "term": 3,
  "entry": {
    "type": "stroke",
    "x1": 100, "y1": 150,
    "x2": 110, "y2": 155,
    "color": "#000000",
    "width": 4
  }
}
```

---

## Failure Handling

| Scenario | Behaviour |
|----------|-----------|
| Leader crashes | Followers time out, new election starts within 800ms |
| Follower crashes | Leader continues, restarted node catches up via /sync-log |
| Network partition | Higher term wins when partition heals |
| Split vote | Election retries with new incremented term |
| Gateway restart | Clients auto-reconnect, gateway re-discovers leader |
