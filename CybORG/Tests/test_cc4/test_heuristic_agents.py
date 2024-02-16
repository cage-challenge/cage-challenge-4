import pytest
import random

from CybORG import CybORG
from CybORG.Agents.Wrappers import BlueEnterpriseWrapper
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, RandomSelectRedAgent, EnterpriseGreenAgent, FiniteStateRedAgent, cc4BlueRandomAgent


@pytest.fixture(params=[RandomSelectRedAgent, FiniteStateRedAgent])
def cyborg(request):
    """CybORG is given a 1000 step time limit to give enough time for wierd agent behaviour to occur."""
    seed = random.randint(0, 9999)
    print("Seed:", seed)
    sg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent,
        green_agent_class=EnterpriseGreenAgent,
        red_agent_class=request.param,
        steps=1000
    )

    cyborg = CybORG(scenario_generator=sg, seed=seed)
    cyborg = BlueEnterpriseWrapper(cyborg, seed=seed)
    cyborg.reset()

    return cyborg

def test_cyborg_empty_step(cyborg: BlueEnterpriseWrapper):
    for i in range(1000):
        cyborg.step()

def test_cyborg_random_blue_steps(cyborg: BlueEnterpriseWrapper):
    for i in range(1000):
        blue_actions = {a:cyborg.action_space(a).sample() for a in cyborg.agents}
        cyborg.step(actions=blue_actions)

@pytest.mark.parametrize('seed', [6065])
def test_issue_finite_state_agent(seed):
    sg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent,
        green_agent_class=EnterpriseGreenAgent,
        red_agent_class=FiniteStateRedAgent,
        steps=1000
    )
    my_cyborg = BlueEnterpriseWrapper(CybORG(scenario_generator=sg, seed=seed), seed=seed)
    my_cyborg.reset()

    for i in range(1000):
        blue_actions = {a:my_cyborg.action_space(a).sample() for a in my_cyborg.agents}
        # if i in (501, 543):
        #     print('Potential error case')
        my_cyborg.step(actions=blue_actions)

@pytest.mark.parametrize('seed', [5712, 9283, 3669, 4095])
def test_sessions_issue_no_blue(seed):

    sg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent,
        green_agent_class=EnterpriseGreenAgent,
        red_agent_class=RandomSelectRedAgent,
        steps=1000)
        
    cyborg = CybORG(scenario_generator=sg, seed=seed)
    cyborg.reset()

    for i in range(1000):
        if i == 160:
            print('Potential error case')
        cyborg.step()

@pytest.mark.parametrize('seed', [87, 1148, 2742, 9556, 2812, 9251])
def test_sessions_issue_with_blue(seed):

    sg = EnterpriseScenarioGenerator(
        blue_agent_class=cc4BlueRandomAgent,
        green_agent_class=EnterpriseGreenAgent,
        red_agent_class=RandomSelectRedAgent,
        steps=1000)
        
    cyborg = CybORG(scenario_generator=sg, seed=seed)
    cyborg.reset()

    for i in range(1000):
        cyborg.step()
