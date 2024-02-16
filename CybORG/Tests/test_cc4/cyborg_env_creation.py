import pprint
from random import choice, randint

import pytest

from CybORG import CybORG
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.EnterpriseGreenAgent import EnterpriseGreenAgent
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent

pp = pprint.PrettyPrinter(indent=4)

def create_cyborg_env(param_seed: int = None):
    """ Function that creates a CybORG environment with a specifc green agent.

    A new CybORG environment is created from the EnterpriseScenario of CC4, with green agents as EnterpriseGreenAgents, and the remaining agents (blue and red) as SleepAgents. This environment is created from a random seed.
    Green agents in the scenario are collected and a single green agent interface is chosen at random, to be passed back for further testing.

    Note: This function has not been made as a pytest fixture due to the tests needing to be run from a clean environment.

    Returns:
        cyborg (CybORG): a new cyborg environment
        agent_interface (AgentInterface): an agent interface of a random green agent in the scenario
    """
    if param_seed is None:
        seed = randint(10, 100000)
    else:
        seed = param_seed
    print("environment seed: " + str(seed))

    sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=EnterpriseGreenAgent, red_agent_class=SleepAgent)
    cyborg = CybORG(scenario_generator=sg, seed=seed)
    cyborg.environment_controller.reset()

    scenario_green_agents = []
    for entity_name, entity_val in cyborg.environment_controller.agent_interfaces.items():
        if 'green' in entity_name:
            scenario_green_agents.append(entity_val)

    np_random = cyborg.np_random
    agent_interface = np_random.choice(scenario_green_agents)

    return cyborg, agent_interface