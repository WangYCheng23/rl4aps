import os, sys


class BaseAgent:
    def __init__(self, **kwargs):
        super(BaseAgent, self).__init__(**kwargs)

    def pick_action(self, observation):
        raise NotImplementedError

    def add_to_replay_buffer(self, experiences):
        raise NotImplementedError

    def sample(self, batch_size):
        raise NotImplementedError

    def update(self) -> dict:
        raise NotImplementedError
    
    def save(self, path):
        raise NotImplementedError