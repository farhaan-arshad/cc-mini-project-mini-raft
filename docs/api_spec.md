# Full API definitions for all RPC endpoints
# API Specification

## Gateway Endpoints

### WebSocket /ws
Browser clients connect here to send and receive strokes.

**Client → Gateway (stroke)**
```json
{
  "type": "stroke",
  "x1": 100, "y1": 150,
  "x2": 110, "y2": 155,
  "color": "#000000",
  "width": 4
}
```

**Gateway → Client (broadcast)**
```json
{
  "type": "stroke",
  "x1": 100, "y1": 150,
  "x2": 110, "y2": 155,
  "color": "#000000",
  "width": 4
}
```

### POST /broadcast
Called by the leader replica to push a committed stroke to all clients.

### GET /health
Returns gateway status and current leader.

---

## Replica Endpoints

### POST /request-vote
**Request**
```json
{
  "term": 4,
  "candidate_id": "replica2",
  "last_log_index": 4,
  "last_log_term": 3
}
```
**Response**
```json
{
  "term": 4,
  "vote_granted": true
}
```

### POST /append-entries
**Request**
```json
{
  "term": 3,
  "leader_id": "replica1",
  "prev_log_index": 4,
  "prev_log_term": 2,
  "entry": { "type": "stroke", "x1": 100, "y1": 150, "x2": 110, "y2": 155, "color": "#000000", "width": 4 },
  "commit_index": 4
}
```
**Response**
```json
{
  "term": 3,
  "success": true
}
```

### POST /heartbeat
**Request**
```json
{
  "term": 3,
  "leader_id": "replica1"
}
```
**Response**
```json
{
  "term": 3,
  "success": true
}
```

### POST /sync-log
**Request**
```json
{
  "term": 3,
  "leader_id": "replica1",
  "from_index": 2,
  "entries": [
    { "term": 2, "entry": { "type": "stroke" } },
    { "term": 3, "entry": { "type": "stroke" } }
  ],
  "commit_index": 3
}
```
**Response**
```json
{
  "term": 3,
  "success": true
}
```

### POST /client-stroke
Called by the gateway to submit a stroke to the leader.

### GET /status
Returns replica state, term, leader, log length, and commit index.
