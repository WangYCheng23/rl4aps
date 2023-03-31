import yaml
from Agents import DQN_Agent
from Environments import JSSP_Environment

def train(parameters):
    logs = []
    env = JSSP_Environment(parameters)
    agent = DQN_Agent(env, parameters)
    
    next_observation = env.reset()
    for itr in range(parameters["num_iterations"]):
        observation = next_observation
        action = agent.pick_action(observation)
        next_observation, reward, terminal, info = env.step(action)

        logs.append(info)
        agent.add_to_replay_buffer([observation, action, next_observation, reward, terminal])
        
        if terminal:
            break

    return logs


if __name__ == "__main__":
    with open("./config.yaml", "r", encoding="utf-8") as f:
        parameters = yaml.load(f.read(), Loader=yaml.FullLoader)
    logs = train(parameters)