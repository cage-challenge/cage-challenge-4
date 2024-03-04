# Training RLlib Agents
This section is a tutorial to train the defensive blue agents in the CybORG environment. 

This example is a most basic training example using RLlib. More indepth tutorials of RLlib use can be found in [Ray's documentation of RLlib](https://docs.ray.io/en/latest/rllib/rllib-training.html).

The code for this example is provided as `CybORG/Evaluation/training_examples/TrainingRay.py`.

???+ Question "What if I don't want to use RLlib?"
    The submissions to CAGE challenge 4 are not limited to reinforcement learning approaches or use of RLlib. Please feel free to make your own custom wrappers!

## Importing CybORG
The initial steps are identical to the intial steps of the interfacing with the environment in the Getting Started Guide. 

As per [Getting Started With CybORG](2_Getting_Started.md), it is necessary to import the `CybORG` class, the `EnterpriseScenarioGenerator` and the `EnterpriseMAE` wrapper. 

```python title="training_agents.py" linenums="1"
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents.Wrappers import EnterpriseMAE
```

To train an agent, we need a Blue Agent to be interacting with the external API while Red and Green take their actions automatically in the background.

We can achieve this by specifying an agents dictionary to pass into CybORG when instantiating the class. Now, whenever the step function is called, the agents will take turns to perform their actions. In this example, this instantiates the `SleepAgent`, `EnterpriseGreenAgent` and `FiniteStateRedAgent`.

 

```python linenums="4"
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent
```

This section imports key RLLib libraries, such as the register environment class and the algorithms that have been chosen to train upon.

```python linenums="5"
from ray.tune import register_env
from ray.rllib.algorithms.ppo import PPOConfig, PPO
from ray.rllib.algorithms.dqn import DQNConfig, DQN
from ray.rllib.policy.policy import PolicySpec

```

## Instantiating CybORG

Although CybORG uses an OpenAI gym API, it is not run by calling `gym.make()`. Instead, it has to be manually instantiated by calling the envionment creator constructor. The constructor has two mandatory string parameters: a mode-type which specifies which engine will be used under the hood and the class for the scenario which defines the network layout and agent action spaces. The `EnterpriseMAE` wrapper then wraps the environment so it is compatible with RLlib

Challenge 4 is instantiated as follows:

```python linenums="9"
def env_creator_CC4(env_config: dict):
    sg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent,
        green_agent_class=EnterpriseGreenAgent,
        red_agent_class=FiniteStateRedAgent,
        steps=500
    )
    cyborg = CybORG(scenario_generator=sg)
    env = EnterpriseMAE(env=cyborg)
    return env
```

Register a custom env creator function with a string name. This function must take a single `env_config(dict)` parameter and return an env instance.
Then, to get it to work with the `tune.register_env()`, you can use your custom env with a lambda function.

```python linenums="19"
register_env(name="CC4", env_creator=lambda config: env_creator_CC4(config))
env = env_creator_CC4({})
```

For environments with multiple groups, or mixtures of agent groups and individual agents, you can use grouping in conjunction with the policy mapping API described in prior sections. This creates a policy mapping function to map the agent to the config below.

```python linenums="21"
NUM_AGENTS = 5
POLICY_MAP = {f"blue_agent_{i}": f"Agent{i}" for i in range(NUM_AGENTS)}

def policy_mapper(agent_id, episode, worker, **kwargs):
    return POLICY_MAP[agent_id]
```

To configure the environment, use the standard RLlib config formant. For multi-agent environments such as CybORG, with five types of agents, their experiences are aggregated by policy, so from RLlib’s perspective it’s just optimizing three different types of policy. The configuration might look something like this:

```python linenums="26"
algo_config = (
    PPOConfig()
    .environment(env="CC4")
    .debugging(logger_config={"logdir":"logs/PPO_Example", "type":"ray.tune.logger.TBXLogger"})
    .multi_agent(policies={
        ray_agent: PolicySpec(
            policy_class=None,
            observation_space=env.observation_space(cyborg_agent),
            action_space=env.action_space(cyborg_agent),
            config={"gamma": 0.85},
        ) for cyborg_agent, ray_agent in POLICY_MAP.items()
    },
    policy_mapping_fn=policy_mapper
))

```

## Agent Training

To train the agents with the above config, three steps are then required - building the alogrithm, setting the number of steps you wish to run the algorithm for and then saving the results for further analysis. 

```python linenums="40"
algo = algo_config.build()

for i in range(50):
    train_info=algo.train()

algo.save("results")
```

After the training has occurred you can analyse the results on your prefered platfrom. To use tensorboard run the following command:

`tensorboard --logdir logs/`

The link that comes up will display graphs that correspond to what the agent is learning and reward. 

