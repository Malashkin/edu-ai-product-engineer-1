from typing import Dict
from .agent import Agent

class Runner:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}

    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the runner."""
        self.agents[agent.name] = agent

    def remove_agent(self, agent_name: str) -> None:
        """Remove an agent from the runner."""
        if agent_name in self.agents:
            del self.agents[agent_name]

    def get_agent(self, agent_name: str) -> Agent:
        """Get an agent by name."""
        return self.agents.get(agent_name)

    def clear_all_histories(self) -> None:
        """Clear conversation histories for all agents."""
        for agent in self.agents.values():
            agent.clear_history()

    def run_conversation(self, agent_name: str, prompt: str) -> str:
        """Run a conversation with a specific agent."""
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent {agent_name} not found")
        
        return agent.get_response(prompt) 