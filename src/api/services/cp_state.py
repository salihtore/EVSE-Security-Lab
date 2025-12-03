class CPState:
    def __init__(self):
        self.state = {}

    def update(self, cp_id: str, status: str):
        self.state[cp_id] = {
            "status": status
        }

    def get_all(self):
        return self.state


cp_state = CPState()
