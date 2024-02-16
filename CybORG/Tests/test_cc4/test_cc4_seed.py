import inspect
from copy import deepcopy

import pytest

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import EnterpriseGreenAgent, FiniteStateRedAgent, SleepAgent

@pytest.fixture
def cc4():
    sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=EnterpriseGreenAgent, red_agent_class=FiniteStateRedAgent, steps=10)
    cyborg = CybORG(scenario_generator=sg)
    return cyborg
    
def test_cc4_seed(cc4):
    cc4.reset(seed=123)
    first_actions = []
    for step in range(5):
        cc4.step()
        first_actions.append({a:cc4.get_last_action(a)[0] for a in cc4.agents})
    cc4.reset(seed=123)
    second_actions = []
    for step in range(5):
        cc4.step()
        second_actions.append({a:cc4.get_last_action(a)[0] for a in cc4.agents})
    
    for step in range(5):
       for agent in cc4.agents:
           first = first_actions[step][agent]
           second = second_actions[step][agent]
           assert first.name == second.name