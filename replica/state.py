# Node state machine: FOLLOWER, CANDIDATE, LEADER
from enum import Enum

class NodeState(Enum):
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER = "LEADER"

class State:
    def __init__(self, replica_id: str, peers: list[str]):
        self.replica_id = replica_id
        self.peers = peers

        # RAFT state
        self.current_term = 0
        self.voted_for = None
        self.state = NodeState.FOLLOWER

        # Log
        self.log = []           # list of {"term": int, "entry": dict}
        self.commit_index = -1

        # Leader info
        self.current_leader = None

        # Vote tracking
        self.votes_received = 0

    def reset_to_follower(self, term: int):
        self.current_term = term
        self.voted_for = None
        self.state = NodeState.FOLLOWER
        self.votes_received = 0

    def become_candidate(self):
        self.current_term += 1
        self.voted_for = self.replica_id
        self.state = NodeState.CANDIDATE
        self.votes_received = 1
        print(f"[{self.replica_id}] Became CANDIDATE for term {self.current_term}")

    def become_leader(self):
        self.state = NodeState.LEADER
        self.current_leader = self.replica_id
        print(f"[{self.replica_id}] Became LEADER for term {self.current_term}")