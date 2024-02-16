import pytest

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent
from CybORG.Simulator.Actions import *


@pytest.fixture()
def cyborg():
    sg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent,
        green_agent_class=EnterpriseGreenAgent,
        red_agent_class=FiniteStateRedAgent,
        steps=1000
    )

    cyborg = CybORG(scenario_generator=sg)
    cyborg.reset()

    return cyborg

@pytest.mark.skip("Test failing - under investigation")
def test_degrade_deception_interaction(cyborg: CybORG):
    '''
    Here we wait until red gets onto an appropriate host. Then we create haraka decoy process,
    kill it with degrade services, then bring it back up with another decoy action. This can create
    a contradiction between the service pid and process pid
    '''
    cyborg.reset(seed=85)
    state = cyborg.environment_controller.state
    red_agent = 'red_agent_1'
    for i in range(100):
        cyborg.step()
        if red_agent in cyborg.active_agents:
            break
    else:
        raise ValueError(f'{red_agent} not active')

    red_session_id = 0
    hostname = state.sessions[red_agent][red_session_id].hostname
    host = state.hosts[hostname]
    agents = [a for a,s in host.sessions.items() if s]
    blue_agent = next((a for a in agents if 'blue' in a), None)

    red_action = DegradeServices(hostname=hostname, session=0, agent=red_agent)
    red_action.duration = 1
    blue_action = DecoyHarakaSMPT_cc4(hostname=hostname, session=0, agent=blue_agent)
    blue_action.duration = 1

    '''
    If you have no empty steps below, then the test crashes due to Finite Red State agent.
    If you only have one, then the Decoy actions gets lucky and recreates the right pid.
    '''
    cyborg.step()
    cyborg.step()
    cyborg.step(action=blue_action, agent=blue_agent)
    services = host.services
    assert 'haraka' in services

    for i in range(10):
        cyborg.step(action=red_action, agent=red_agent)
        if not services['haraka'].active:
            break
    else:
        raise ValueError('Degrade Services failed to stop haraka service')

    cyborg.step(action=blue_action, agent=blue_agent)

    processes = {p.name:p.pid for p in host.processes}
    assert processes['haraka'] == services['haraka'].process
