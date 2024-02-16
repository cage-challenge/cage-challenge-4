
from gym import Space
from CybORG.Agents import BaseAgent

class DummyAgent(BaseAgent):
    def __init__(self, name: str = None):
        super().__init__(name)

    def get_action(self, observation: dict, action_space: Space):
        return action_space.n - 1
