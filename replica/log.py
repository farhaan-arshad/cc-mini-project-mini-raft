# Append-only stroke log and commit logic
class Log:
    def __init__(self, state):
        self.state = state

    def append(self, entry: dict, term: int):
        self.state.log.append({"term": term, "entry": entry})
        print(f"[{self.state.replica_id}] Log appended. Size: {len(self.state.log)}")

    def get_last_log_index(self) -> int:
        return len(self.state.log) - 1

    def get_last_log_term(self) -> int:
        if not self.state.log:
            return 0
        return self.state.log[-1]["term"]

    def get_entries_from(self, index: int) -> list:
        return self.state.log[index:]

    def commit(self, index: int):
        if index > self.state.commit_index:
            self.state.commit_index = index
            print(f"[{self.state.replica_id}] Committed up to index {index}")
            