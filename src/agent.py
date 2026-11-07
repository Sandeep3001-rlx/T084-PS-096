
class CommissionAgent:
    def __init__(self, agent_id, name):
        self.agent_id = str(agent_id).strip()
        self.name = str(name).strip()

        if not self.agent_id:
            raise ValueError("Agent ID cannot be empty")

        if not self.name:
            raise ValueError("Agent name cannot be empty")

    def __repr__(self):
        return f"CommissionAgent(agent_id='{self.agent_id}', name='{self.name}')"


if __name__ == "__main__":
    agent = CommissionAgent("A001", "Suresh Agency")
    print(agent)
