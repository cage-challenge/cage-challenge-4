import pytest
from CybORG.Agents.SimpleAgents.EnterpriseGreenAgent import EnterpriseGreenAgent
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Agents.SimpleAgents.FiniteStateRedAgent import FiniteStateRedAgent
from CybORG.Agents.Wrappers.BlueEnterpriseWrapper import BlueEnterpriseWrapper
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.env import CybORG

@pytest.fixture()
def cc4_cyborg():
    return create_cc4_cyborg()

@pytest.fixture()
def cc4_cyborg_list():
    return [create_cc4_cyborg(seed=i) for i in range(5)]

@pytest.fixture()
def cc4_cyborg_min_steps():
    return create_cc4_cyborg(steps=6)

@pytest.fixture()
def enterprise_cyborg():
    return create_cyborg()

@pytest.fixture()
def enterprise_cyborg_min_steps():
    return create_cyborg(steps=6)

@pytest.fixture()
def cc4_blue_wrapper():
    return BlueEnterpriseWrapper(create_cc4_cyborg())

def create_cc4_cyborg(seed = 123, steps: int = 100):
    ent_sg = EnterpriseScenarioGenerator(green_agent_class=EnterpriseGreenAgent, steps=steps)
    cyborg = CybORG(scenario_generator=ent_sg, seed=seed)
    cyborg.reset()
    return cyborg

def create_cyborg(seed = 123, steps: int = 100):
    ent_sg = EnterpriseScenarioGenerator(steps=steps)
    cyborg = CybORG(scenario_generator=ent_sg, seed=seed)
    cyborg.reset()
    return cyborg

def create_sleep_cyborg(seed: int = 123, steps: int = 100):
    ent_sg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent,
        red_agent_class=SleepAgent,
        green_agent_class=SleepAgent,
        steps=steps
    )
    cyborg = CybORG(scenario_generator=ent_sg, seed=seed)
    cyborg.reset()
    return cyborg

def create_cc4_complex_cyborg(seed: int = 123, steps: int = 100):
    ent_sg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent,
        red_agent_class=FiniteStateRedAgent,
        green_agent_class=EnterpriseGreenAgent,
        steps=steps
    )
    cyborg = CybORG(scenario_generator=ent_sg, seed=seed)
    cyborg.reset()
    return cyborg
