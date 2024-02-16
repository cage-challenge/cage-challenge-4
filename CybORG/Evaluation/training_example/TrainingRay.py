import inspect
import time
import os

from statistics import mean, stdev
from typing import Any
from rich import print

from CybORG import CybORG
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents.Wrappers import BaseWrapper, BlueFlatWrapper, BlueFixedActionWrapper, EnterpriseMAE

import numpy as np

from ray.rllib.env import MultiAgentEnv
from ray.rllib.algorithms.ppo import PPOConfig, PPO
from ray.rllib.algorithms.dqn import DQNConfig, DQN
from ray.rllib.policy.policy import PolicySpec
from ray.rllib.utils import check_env
from ray.tune import register_env

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


def env_creator_CC4(env_config: dict):
    sg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent,
        green_agent_class=EnterpriseGreenAgent,
        red_agent_class=FiniteStateRedAgent,
        #red_agent_class=SleepAgent,
        steps=100,
    )
    cyborg = CybORG(scenario_generator=sg)
    cyborg = EnterpriseMAE(cyborg)
    return cyborg


NUM_AGENTS = 5
POLICY_MAP = {f"blue_agent_{i}": f"Agent{i}" for i in range(NUM_AGENTS)}


def policy_mapper(agent_id, episode, worker, **kwargs):
    return POLICY_MAP[agent_id]


# register_env(name="CC4", env_creator=lambda config: ParallelPettingZooEnv(env_creator_CC4(config)))
register_env(name="CC4", env_creator=lambda config: env_creator_CC4(config))
env = env_creator_CC4({})


# Note:     will allow different action space sizes but not different observation space sizes in one property
#           current implementation may cause issues - seems to want all same size???
algo_config = (
    DQNConfig().framework("torch")
    # .debugging(seed=0, log_level="ERROR")
    .debugging(logger_config={"logdir":"logs/DQN_Complicated_SleepRed", "type":"ray.tune.logger.TBXLogger"})
    .environment(env="CC4")
    # .training(model={"fcnet_hiddens":[32:32]})``
    .multi_agent(
        policies={
            ray_agent: PolicySpec(
                policy_class=None,
                observation_space=env.observation_space(cyborg_agent),
                action_space=env.action_space(cyborg_agent),
                config={"gamma": 0.85},
            )
            for cyborg_agent, ray_agent in POLICY_MAP.items()
        },
        policy_mapping_fn=policy_mapper,
    )
)

check_env(env)
algo = algo_config.build()

for i in range(1000):
    train_info = algo.train()

#algo.save("experiment1a")
#output = algo.evaluate()

print(output)
print(
    "Avg episode length for trained agent: %.1f"
    % output["evaluation"]["episode_len_mean"]
)
