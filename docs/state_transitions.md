# FOLLOWER → CANDIDATE → LEADER state diagram
# State Transitions

## Node State Machine
```
          ┌─────────────────────────────┐
          │         FOLLOWER            │
          │  - Waits for heartbeats     │
          │  - Votes for candidates     │
          └────────────┬────────────────┘
                       │
                       │ Election timeout
                       │ (no heartbeat received)
                       ▼
          ┌─────────────────────────────┐
          │         CANDIDATE           │
          │  - Increments term          │
          │  - Votes for self           │
          │  - Requests votes from peers│
          └────────────┬────────────────┘
                       │
          ┌────────────┴────────────────┐
          │                             │
          │ Majority votes received     │ Higher term seen
          │                             │ OR split vote timeout
          ▼                             ▼
┌──────────────────┐          ┌──────────────────────┐
│      LEADER      │          │       FOLLOWER        │
│ - Sends          │          │ (reset, retry later)  │
│   heartbeats     │          └──────────────────────-┘
│ - Replicates log │
│ - Commits on     │
│   majority ack   │
└────────┬─────────┘
         │
         │ Higher term seen
         ▼
┌──────────────────┐
│     FOLLOWER     │
│ (steps down)     │
└──────────────────┘
```

---

## Election Flow
```
Follower misses heartbeat (500-800ms timeout)
         │
         ▼
Become Candidate
  - current_term += 1
  - voted_for = self
  - votes = 1
         │
         ▼
Send /request-vote to all peers
         │
    ┌────┴────┐
    │         │
  Vote      No vote /
 granted    peer down
    │         │
    └────┬────┘
         │
  votes >= 2 ? ──── No ──── Wait / retry election
         │
        Yes
         │
         ▼
    Become LEADER
  - Start heartbeat loop (150ms)
  - Accept strokes from gateway
```

---

## Log Replication Flow
```
Gateway sends stroke to Leader
         │
         ▼
Leader appends to local log
         │
         ▼
Leader sends /append-entries to all followers
         │
    ┌────┴────┐
    │         │
Follower   Follower
 acks       behind
    │         │
    │         ▼
    │   Follower returns log_length
    │         │
    │         ▼
    │   Leader calls /sync-log
    │   (sends missing entries)
    │         │
    └────┬────┘
         │
  acks >= 2 ?
         │
        Yes
         │
         ▼
  Leader commits entry
         │
         ▼
  Leader calls /broadcast on Gateway
         │
         ▼
  Gateway sends stroke to all browser clients
```

---

## Catch-Up Sync Flow
```
Replica restarts (empty log)
         │
         ▼
Starts as FOLLOWER
         │
         ▼
Receives /append-entries from leader
prev_log_index check fails
         │
         ▼
Returns { success: false, log_length: 0 }
         │
         ▼
Leader calls /sync-log with all missing entries
         │
         ▼
Follower appends all entries
Updates commit_index
         │
         ▼
Follower is now in sync
Participates normally
```
