import pytest
import random

from CybORG import CybORG
from CybORG.Shared.Enums import ProcessName
from CybORG.Shared.Session import Session
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Simulator.Actions.AbstractActions.DegradeServices import DegradeServices
from .test_Impact import create_sleep_cyborg, get_agent_with_shell
from CybORG.Shared.Enums import TernaryEnum


# Global test variables
AGENT_NAME = 'red_agent_0'
S0_HOSTNAME = 'contractor_network_subnet_server_host_0'

def test_degrade_services_runs_with_priv():
    cyborg = create_sleep_cyborg()
    get_agent_with_shell(cyborg=cyborg)

    action = DegradeServices(hostname=S0_HOSTNAME, session=0, agent=AGENT_NAME)
    action.duration = 1
    result = cyborg.step(agent=AGENT_NAME, action=action)

    assert result.observation['success'] == TernaryEnum.TRUE

def test_degrade_services_not_run_without_priv():
    cyborg = create_sleep_cyborg()
    get_agent_with_shell(cyborg=cyborg, priv_shell=False)

    action = DegradeServices(hostname=S0_HOSTNAME, session=0, agent=AGENT_NAME)
    action.duration = 1
    result = cyborg.step(agent=AGENT_NAME, action=action)

    assert result.observation['success'] == TernaryEnum.FALSE

def test_service_is_degraded():
    cyborg = create_sleep_cyborg()
    get_agent_with_shell(cyborg=cyborg)

    before_services_reliability = [service._percent_reliable for s_name, service in cyborg.environment_controller.state.hosts[S0_HOSTNAME].services.items()]

    action = DegradeServices(hostname=S0_HOSTNAME, session=0, agent=AGENT_NAME)
    action.duration = 1
    result = cyborg.step(agent=AGENT_NAME, action=action)

    after_services_reliability = [service._percent_reliable for s_name, service in cyborg.environment_controller.state.hosts[S0_HOSTNAME].services.items()]

    for i in range(len(before_services_reliability)):
        if not after_services_reliability[i] == (before_services_reliability[i] - 20):
            assert False





# @pytest.mark.parametrize('user_type', ['user', 'root', 'SYSTEM'])
# def test_red_agent_degrades(user_type):
#     """Test that we remove the service running on a specific host. Seed 1 will force the 
#         selected host to have SSHD as the randomly selected service we're degrading"""
#     esg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent,
#                                         red_agent_class=SleepAgent)
#     cyborg = CybORG(scenario_generator=esg, seed=0)
#     env = cyborg.environment_controller
#     env.reset()

#     red_agent_str = 'red_agent_0'
#     agent = env.agent_interfaces[red_agent_str]
#     session = env.state.sessions[red_agent_str][0]
#     hostname = env.state.sessions[red_agent_str][0].hostname
    
#     # ensure the environment is reset until the red agents host only has the single SSHD service running. 
#     while len(env.state.hosts[hostname].services.keys())!=1:
#         env.reset()
#         agent = env.agent_interfaces[red_agent_str]
#         session = env.state.sessions[red_agent_str][0]
#         hostname = session.hostname

#     obs = cyborg.get_observation(red_agent_str)
#     action_space = cyborg.get_action_space(red_agent_str)

#     for i in range(30):
#         # base action for each step - Sleep unless overwritten
#         action = agent.get_action(obs, action_space)

#         # on step 1, set the action to be Degrade - this will fail
#         if i == 1:
#             action = DegradeServices(hostname=hostname, session=session.ident, agent=red_agent_str)
#         # add a root shell session on the host that is controlled by the red agent
#         if i == 5:
#             session = Session(
#                 hostname=hostname, username=user_type, agent=red_agent_str, parent=session.ident,
#                 session_type='shell', pid=None, ident=None
#             )
#             env.state.add_session(session)
#         # on step 10, set the action to be Degrade - this should pass
#         if i == 10:
#             action = DegradeServices(hostname=hostname, session=session.ident, agent=red_agent_str)

#         # env step and get results
#         results = cyborg.step(action=action, agent=red_agent_str, skip_valid_action_check=True)
#         obs = results.observation

#         # assert statements on results
#         if i == 1:
#             action_details = env.get_last_action(red_agent_str)[0].__str__().split(' ')
#             assert action_details[0] == 'DegradeServices'
#             assert action_details[1] == hostname
#             assert obs['success'] != True
#             assert len([(pro.name) for pro in list(env.state.hosts[hostname].processes) if pro.name == ProcessName.SSHD]) == 1
#             assert env.state.hosts[hostname].services[ProcessName.SSHD].active is True
#         if i == 10:
#             action_details = env.get_last_action(red_agent_str)[0].__str__().split(' ')
#             assert action_details[0] == 'DegradeServices'
#             assert action_details[1] == hostname
#             # the action should fail is the new session is not root/system level
#             if user_type == 'user':
#                 assert obs['success'] == False
#                 assert env.state.hosts[hostname].services[ProcessName.SSHD].active is True
#             else:
#                 assert obs['success'] == True
#                 assert obs[hostname]['Processes'][0]['process_name'] == ProcessName.SSHD
#                 assert len([(pro.name) for pro in list(env.state.hosts[hostname].processes) if pro.name == ProcessName.SSHD]) == 0
#                 assert env.state.hosts[hostname].services[ProcessName.SSHD].active is False

#         action_space = results.action_space
