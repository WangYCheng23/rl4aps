from Base_Agent import BaseAgent
from Utils.Rules_Set import pick_rules

class DQNAgent(BaseAgent):
    def __init__(self, env, parameters):
        super().__init__(env, parameters)
        self.env = env
        self.parameters = parameters

    def pick_action(self, observation):
        return pick_rules(observation)