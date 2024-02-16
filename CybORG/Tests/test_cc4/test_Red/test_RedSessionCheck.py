import pytest

from CybORG import CybORG
from CybORG.Shared.Session import Session
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Simulator.Actions.ConcreteActions.RemoveOtherSessions import RemoveOtherSessions_AlwaysSuccessful
from CybORG.Simulator.State import State

def add_sessions(state: State, agent_name, hostname):
    """Add 3 sessions with a parent session"""
    state.add_session(Session(
        hostname=hostname, username='user', agent=agent_name, parent=None, session_type='shell',
        ident=0, pid=None
    ))
    state.add_session(Session(
        hostname=hostname, username='user', agent=agent_name, parent=0, session_type='shell',
        ident=1, pid=None
    ))
    state.add_session(Session(
        hostname=hostname, username='user', agent=agent_name, parent=0, session_type='shell',
        ident=2, pid=None
    ))

def remove_session(state, agent_name, ident):
    """Remove the agents parent session"""
    host_name = state.sessions[agent_name][0].hostname
    state.sessions[agent_name].pop(0)

    state.sessions_count[agent_name]-=1
    state.hosts[host_name].sessions[agent_name].remove(0)


# @pytest.mark.skip
# def test_session_creation_actions():
#     pass


def test_remove_sessions_action_and_red_agent_deactivation():
    """
    Test that the action RemoveOtherSessions_AlwaysSuccessful will 
    result in the deactivation of the red agent.
    """
    esg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent,
                                        red_agent_class=SleepAgent)
    cyborg = CybORG(scenario_generator=esg, seed=124)
    env = cyborg.environment_controller
    env.reset()
    red_agent_str='red_agent_1'

    # find the blue agent thats on the same subnet as red_agent_0
    for agent_name, agent in env.agent_interfaces.items():
        if 'blue' in agent_name:
            if agent.allowed_subnets==env.agent_interfaces[red_agent_str].allowed_subnets:
                blue_agent_str=agent_name
                break
    
    session_id=0

    obs = cyborg.get_observation(blue_agent_str)
    action_space = cyborg.get_action_space(blue_agent_str)

    hostname = [int.hostname for int in env.state.sessions[blue_agent_str].values() if int.ident==0][0]

    for i in range(30):
        # action steps
        action = agent.get_action(obs, action_space)
        # add sessions for red_agent_1 on the same host as blue_agent_1 - to activate red_agent_1
        if i==5: add_sessions(env.state, red_agent_str, hostname); 
        # remove the sessions from blue_agent_0 - to deactivate red_agent_1
        if i==15: action = RemoveOtherSessions_AlwaysSuccessful(session=session_id, agent=blue_agent_str)
        # skip action check as RemoveAll isn't in the blue agents valid action space
        results = cyborg.step(action=action, agent=blue_agent_str, skip_valid_action_check=True)
        # check that after the action and step method, red_agent_1 is now active given the new sessions
        if i==5: assert env.agent_interfaces[red_agent_str].active==True and env.is_active(red_agent_str)==True
        # check that after the RemoveOtherSessions_AlwaysSuccessful action, red_agent_1 is no longer active
        if i==15: assert env.agent_interfaces[red_agent_str].active==False and env.is_active(red_agent_str)==False

        obs = results.observation
        action_space = results.action_space



def test_red_agent_activation():
    """Test that CybORG runs an episode with specific sessions added and remove"""
    sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent,
                                        red_agent_class=SleepAgent)

    cyborg = CybORG(scenario_generator=sg, seed=124)
    env = cyborg.environment_controller
    env.reset()
    red_agent_str='red_agent_1'
    agent = env.agent_interfaces[red_agent_str]
    hostname = list(cyborg.environment_controller.hostname_ip_map.keys())[0]
    obs = cyborg.get_observation(red_agent_str)
    action_space = cyborg.get_action_space(red_agent_str)
    for i in range(30):
        red_agent_count= [(entity_name, env.state.sessions_count[entity_name]) for entity_name, entity_val in env.agent_interfaces.items() if entity_val.active and 'red' in entity_name]
        if i==5: add_sessions(env.state, red_agent_str, hostname); assert red_agent_count==[('red_agent_0', 1)]
        if i==10: remove_session(env.state, red_agent_str, 2); assert red_agent_count==[('red_agent_0', 1), ('red_agent_1', 3)]
        if i==15: remove_session(env.state, red_agent_str, 1); assert red_agent_count==[('red_agent_0', 1), ('red_agent_1', 2)]
        if i==20: remove_session(env.state, red_agent_str, 0); assert red_agent_count==[('red_agent_0', 1), ('red_agent_1', 1)]
        action = agent.get_action(obs, action_space)
        results = cyborg.step(action=action, agent=red_agent_str)
        obs = results.observation
        action_space = results.action_space


def test_scenario_reset():
    """Test the initial set up for red agent activation"""
    sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent,
                                     red_agent_class=SleepAgent)

    cyborg = CybORG(scenario_generator=sg, seed=124)
    env = cyborg.environment_controller
    env.reset()
    
    assert len(env.state.sessions['red_agent_0'].keys())==1 \
        and env.agent_interfaces['red_agent_0'].active==True \
        and env.is_active('red_agent_0') == True \
        and env.has_active_non_parent_sessions('red_agent_0')==False
    
    assert len(env.state.sessions['red_agent_1'].keys())==0 \
        and env.agent_interfaces['red_agent_1'].active==False \
        and env.is_active('red_agent_1') == False \
        and env.has_active_non_parent_sessions('red_agent_1')==False
    