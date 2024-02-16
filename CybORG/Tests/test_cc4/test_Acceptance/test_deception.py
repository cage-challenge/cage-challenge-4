from typing import Type
import pytest
import pytest_mock
from CybORG.Shared.Enums import ProcessName
from CybORG.Shared.Session import Session
from CybORG.Simulator.Actions.AbstractActions.DegradeServices import DegradeServices
from CybORG.Simulator.Actions.AbstractActions.DiscoverDeception import DiscoverDeception
from CybORG.Simulator.Actions.AbstractActions.DiscoverNetworkServices import AggressiveServiceDiscovery
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions import DecoyAction, DeployDecoy
from CybORG.Simulator.Actions.GreenActions.GreenLocalWork import GreenLocalWork
# Decoys below are unavailable in CC4 given they require a windows machine and the scenario is only creating linux machines.
#from CybORG.Simulator.Actions.ScenarioActions.EnterpriseActions import DecoyApache_cc4, DecoyHarakaSMPT_cc4, DecoyTomcat_cc4, DecoyVsftpd_cc4
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyApache import ApacheDecoyFactory
from CybORG.Simulator.Actions.ConcreteActions.Withdraw import Withdraw
from CybORG.Simulator.SimulationController import SimulationController
from CybORG.Simulator.State import State
from CybORG.env import CybORG

def test_agents_can_create_decoy_services(cc4_cyborg: CybORG):
    """
    From Deception, paragraph 1:
    Both blue and red agents may employ deception to further their goals. Blue agents can stand up
    decoy services in any host or server. Decoy services resemble normal ones, but cannot replace
    or be instantiated along with existing services (they can use the Discover Network Services
    action to determine which services are already running on a given host).
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    agents = sim_controller.agent_interfaces.items()
    blue_agent = next(agent for agent_name, agent in agents if 'blue' in agent_name)
    blue_actions = blue_agent.action_space.actions.keys()

    assert DeployDecoy in blue_actions

    # Check that the red and blue agents have the decoy actions available to them.
    # decoy_actions = {DecoyApache_cc4, DecoyHarakaSMPT_cc4, DecoyTomcat_cc4, DecoyVsftpd_cc4}
    # for decoy_action in decoy_actions:
    #     assert decoy_action in blue_actions, f"Blue agent is missing decoy action '{decoy_action}' from its action space!"

def test_red_decoys_alert_blue_agents(cc4_cyborg: CybORG):
    """
    From Deception, paragraph 1:
    When a red agent attempts to compromise a decoy service, blue will be alerted and can then see
    any further actions taken by red agents originating from that host.
    """
    decoy_type = DeployDecoy
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    required_port = next(iter(decoy_type.CANDIDATE_DECOYS)).PORT
    blue_agents_sessions_hosts = [
        (agent, session, sim_controller.state.hosts[session.hostname])
        for agent, sessions in sim_controller.state.sessions.items()
        if "blue" in agent
        for session in sessions.values()
    ]
    # Filter out options where the host is already using the required port
    selected_agent, selected_session, selected_host = next(
        (agent, session, host)
        for agent, session, host in blue_agents_sessions_hosts
        if not host.is_using_port(required_port)
    )
    blue_agent = sim_controller.agent_interfaces[selected_agent]
    action = decoy_type(
        agent=blue_agent.agent_name,
        session=selected_session.ident,
        hostname=selected_host.hostname
    )

    obs = action.execute(sim_controller.state)
    assert obs.success == True, "Decoy was not successfully set-up on host!"

    # Get green agent on that host to spawn a red agent via phishing attack.
    green_agent_name, green_sessions = next(
        ((agent, sessions) for agent, sessions in selected_host.sessions.items() if "green" in agent and sessions),
        (None, None)
    )
    green_agent = sim_controller.agent_interfaces[green_agent_name]
    action = GreenLocalWork(
        agent=green_agent_name,
        session_id=green_sessions[0],
        ip_address=green_agent.agent.own_ip,
        fp_detection_rate=0.00,
        phishing_error_rate=1.00,
    )
    action.execute(sim_controller.state)

    # Get the new red agent that's on the green host.
    red_sessions = []
    for agent, sessions in selected_host.sessions.items():
        if sessions and "red" in agent:
            red_sessions.append((agent, sessions))
    assert red_sessions, "Could not find red session on host!"

    # Now the red agent needs to perform an action against the decoy service.



@pytest.mark.parametrize('decoy_fp_rate',[0,1])
def test_red_agents_can_discover_deception(cc4_cyborg: CybORG, decoy_fp_rate):
    """
    From Deception, paragraph 1:
    Red agents can use the DiscoverDeception action to determine if they are interacting with decoy
    services.
    """
    RED_AGENT='red_agent_0'
    SESSION_ID=0
    env: SimulationController = cc4_cyborg.environment_controller
    
    # get the hostname for the blue_agent session
    hostname = env.state.sessions[RED_AGENT][SESSION_ID].hostname

    # ensure the Apache service isn't running initially
    while ProcessName.APACHE2 in env.state.hosts[hostname].services.keys():
        env.reset()
        hostname = env.state.sessions[RED_AGENT][SESSION_ID].hostname

    # this action is only successful if the service doesnt already exist on the host \
    # which is true for the current seed set in the environment (1)
    action = DeployDecoy(agent=RED_AGENT, session=SESSION_ID, hostname=hostname)
    action.CANDIDATE_DECOYS = [ApacheDecoyFactory()]
    obs = action.execute(env.state)
    assert obs.data['success']==True
    # confirm the decoy has been added to the host
    decoy_list = [pro.name for pro in env.state.hosts[hostname].processes if pro.decoy_type.name=='EXPLOIT']
    assert len(decoy_list)>0
    assert decoy_list[0]=='apache2'

    # identify the target host and detect the decoy with a 100% success rate (detection_rate)
    target_ip = env.hostname_ip_map[hostname]
    action = DiscoverDeception(agent=RED_AGENT, session=SESSION_ID, ip_address=target_ip)
    action.detection_rate = 1.0
    action.fp_rate = decoy_fp_rate

    obs = action.execute(env.state)
    # ensure the action was a success and that the rfi properties exist from the decoy
    assert obs.data['success']==True
    apache_process = [process for process in obs.data[hostname]['Processes'] if process['service_name']=='apache2']
    assert "decoy" in apache_process[0]['Properties']
    # check for false negatives from the detected decoys - all detected with detection_rate 100%, but non contain the 'decoy' property
    non_decoys = [process for process in obs.data[hostname]['Processes'] if process['service_name']!='apache2']
    if decoy_fp_rate==0:
        assert len(non_decoys)==0
    elif decoy_fp_rate==1:
        assert len(non_decoys)>0

def add_sessions(state: State, agent_name, hostname, user_type, num_sessions=1):
    """Add num_sessions with a parent session"""
    for session_int in range(0, num_sessions):
        parent = None if session_int == 0 else 0
        state.add_session(Session(
            hostname=hostname, username=user_type, agent=agent_name, parent=parent,
            session_type='shell', ident=None, pid=None
        ))

@pytest.mark.parametrize('update_phishing_email_rate',[0, 0.01, 0.25, 1])
@pytest.mark.parametrize('num_sessions',[1,3,5])
@pytest.mark.parametrize('user_type',['user', 'root', 'SYSTEM'])
@pytest.mark.parametrize('red_agent_str',['red_agent_0', 'red_agent_1'])
def test_red_agents_can_withdraw(cc4_cyborg: CybORG, num_sessions, user_type, red_agent_str, update_phishing_email_rate):
    """
    From Deception, paragraph 1:
    Red agents can use their Withdraw action to remove their presence.
    """
    env: SimulationController = cc4_cyborg.environment_controller
    
    # test variations of the phising_email_rate to spawn greater numbers of red agents
    for agent_name, agent in env.agent_interfaces.items():
        if 'green' in agent_name: agent.agent.phishing_error_rate = update_phishing_email_rate

    session_id=0
    agent = env.agent_interfaces[red_agent_str]
    
    # if agent has sessions then
    if env.state.sessions_count[red_agent_str]>0:
        local_hostname = env.state.sessions[red_agent_str][0].hostname
        # randomly select a host from the available hosts the agent can access on the subnet that isn't its own hostname
        target_hostname = [host for host in env.state.hosts if env.agent_interfaces[red_agent_str].allowed_subnets[0] in host if host!= local_hostname and 'router' not in host][0]
    else:
        # randomly select a host from the available hosts the agent can access on the subnet
        target_hostname = [host for host in env.state.hosts if env.agent_interfaces[red_agent_str].allowed_subnets[0] in host if 'router' not in host][0]
        local_hostname = target_hostname
    
    own_ip = env.hostname_ip_map[local_hostname]

    obs = cc4_cyborg.get_observation(red_agent_str)
    action_space = cc4_cyborg.get_action_space(red_agent_str)
    
    phishing_email_increment_red = 0
    num_withdrawing=0
    original_session_count = 1 if red_agent_str=='red_agent_0' else 0

    for i in range(30):
        # check the red_agent_1 starts inactive
        if i==0:
            if red_agent_str=='red_agent_0':
                assert env.agent_interfaces[red_agent_str].active==True
                assert env.is_active(red_agent_str)==True
                assert env.state.sessions_count[red_agent_str]>0
            elif red_agent_str=='red_agent_1':
                assert env.agent_interfaces[red_agent_str].active==False
                assert env.is_active(red_agent_str)==False 
                assert env.state.sessions_count[red_agent_str]== phishing_email_increment_red

        action = agent.get_action(obs, action_space)
        # add 1 session for red_agent_0 
        if i==5:
            add_sessions(env.state, red_agent_str, target_hostname, user_type=user_type, num_sessions=num_sessions)
        # withdraw and delete all sessions from red_agent_1
        if i==15:
            action = Withdraw(
                session=session_id,
                agent=red_agent_str,
                ip_address=own_ip,
                hostname=target_hostname
            )
            num_withdrawing = len([s for s in env.state.sessions[red_agent_str].values() if s.hostname == target_hostname])
        red_agent_active = env.agent_interfaces[red_agent_str].active
        # skip action check as Withdaw isn't in the red SleepAgent's valid action space
        results = cc4_cyborg.step(action=action, agent=red_agent_str, skip_valid_action_check=True)
        red_allowed_subnets_map = { agent_name : agent.allowed_subnets for agent_name, agent in env.agent_interfaces.items() if 'red' in agent_name}

        for agent_name, agent in env.agent_interfaces.items():
            if 'green' in agent_name:
                if env.get_last_action(agent_name)[0].__str__().split(' ')[0]=='GreenLocalWork':
                    obs_ph = env.get_last_observation(agent_name)
                    hostname = [k for k in obs_ph.data.keys() if k not in ['success', 'action']]
                    if len(hostname)>0:
                        ## if there is a phishing email in a subnet with an initially inactive red agent
                        ## then the session is reassigned to the red agent to activate it
                        subnet = env.state.hostname_subnet_map[hostname[0]].value
                        for red_agent_name, subnets in red_allowed_subnets_map.items():
                            if subnet in subnets and red_agent_name==red_agent_str:
                                if red_agent_active==False:
                                    phishing_email_increment_red += 1
                        ## if the agent is already active then the appropriate agent is captured in the greens oberservation
                        red_agent = obs_ph.data[hostname[0]]['Sessions'][0]['agent']
                        if red_agent==red_agent_str and red_agent_active and subnet in red_allowed_subnets_map[red_agent_str]:
                            phishing_email_increment_red += 1
        
        # check that after the action and step method, red_agent_1 is now active given the new session
        if i==5:
            assert env.agent_interfaces[red_agent_str].active==True
            assert env.is_active(red_agent_str)==True
            assert env.state.sessions_count[red_agent_str]== (num_sessions + phishing_email_increment_red + original_session_count)
        if i==15:
            assert str(cc4_cyborg.get_last_action(red_agent_str)[0]) == f"Withdraw {target_hostname}"
            # check that after the Withdraw action, red_agent_0 remains active
            if red_agent_str=='red_agent_0':
                assert env.agent_interfaces[red_agent_str].active==True 
                assert env.is_active(red_agent_str)==True
                assert env.state.sessions_count[red_agent_str]>0
            # check that after the Withdraw action, red_agent_1 is no longer active
            elif red_agent_str=='red_agent_1':
                if (phishing_email_increment_red + num_sessions - num_withdrawing) > 0:
                    assert env.agent_interfaces[red_agent_str].active==True 
                    assert env.is_active(red_agent_str)==True
                    assert env.state.sessions_count[red_agent_str]>0
                else:
                    assert env.agent_interfaces[red_agent_str].active==False 
                    assert env.is_active(red_agent_str)==False 
                    assert env.state.sessions_count[red_agent_str] == (phishing_email_increment_red + num_sessions - num_withdrawing)
        obs = results.observation
        action_space = results.action_space


# @pytest.mark.skip('Test unfinished.')
def test_red_agents_can_use_aggressive_service_discovery(cc4_cyborg: CybORG, mocker: pytest_mock.MockerFixture):
    """
    From Deception paragraph 2:
    For their part, red agents can generate extra alerts for blue defenders using the Aggressive
    Service Discovery action on a selected host. This action is faster than the Service Discovery
    action but has a higher probability of generating an alert, so it may also be used simply to
    trade off speed over stealth.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    agent  = 'red_agent_0'
    target_ip = cc4_cyborg.get_ip_map()["restricted_zone_a_subnet_user_host_0"]
    session = 0
    action = AggressiveServiceDiscovery(ip_address=target_ip, agent=agent, session=session)
    
    # For the purposes of testing
    action.detection_rate = 1
    assert target_ip not in sim_controller.state.sessions[agent][session].ports
    action.execute(sim_controller.state)
    assert target_ip in sim_controller.state.sessions[agent][session].ports

@pytest.mark.skip('Requirement demonstrated in other tests')
def test_red_agents_can_use_degrade():
    """
    From Deception paragraph 2:
    In addition, red agents with elevated privileges can use the Degrade action to cause green
    agent actions on the target host to fail much more frequently.

    Shown in tests:

    - Tests/test_cc4/test_Red/test_DegradeServices.py
    - Tests/test_cc4/test_Green/test_GreenLocalWork.py::test_failure_on_fully_degraded_services()
    """
    pass
    # env: SimulationController = cc4_cyborg.environment_controller

    # red_agent_str = 'red_agent_0'
    # session = env.state.sessions[red_agent_str][0]
    # hostname = env.state.sessions['red_agent_0'][0].hostname
    # agent = env.agent_interfaces[red_agent_str]

    # obs = cc4_cyborg.get_observation(red_agent_str)
    # action_space = cc4_cyborg.get_action_space(red_agent_str)

    # for i in range(30):
    #     # base action for each step - Sleep unless overwritten
    #     action = agent.get_action(obs, action_space)

    #     # on step 1, set the action to be Degrade - this will fail
    #     if i == 1:
    #         action = DegradeServices(hostname=hostname, session=session.ident, agent=red_agent_str)
    #     # add a root shell session on the host that is controlled by the red agent
    #     if i == 5:
    #         session = Session(
    #             hostname=hostname, username=user_type, agent=red_agent_str, parent=session.ident,
    #             session_type='shell', ident=None, pid=None
    #         )
    #         env.state.add_session(session)
    #     # on step 10, set the action to be Degrade - this should pass
    #     if i == 10:
    #         action = DegradeServices(hostname=hostname, session=session.ident, agent=red_agent_str)

    #     # env step and get results
    #     results = cc4_cyborg.step(action=action, agent=red_agent_str, skip_valid_action_check=True)
    #     obs = results.observation

    #     # assert statements on results
    #     if i == 1:
    #         action_details = env.get_last_action(red_agent_str)[0].__str__().split(' ')
    #         assert action_details[0] == 'DegradeServices'
    #         assert action_details[1] == hostname
    #         assert obs['success'] != True
    #         assert len([(pro.name) for pro in list(env.state.hosts[hostname].processes) if pro.name == ProcessName.SSHD]) == 1
    #         assert env.state.hosts[hostname].services[ProcessName.SSHD].active is True
    #     if i == 10:
    #         action_details = env.get_last_action(red_agent_str)[0].__str__().split(' ')
    #         assert action_details[0] == 'DegradeServices'
    #         assert action_details[1] == hostname
    #         # the action should fail is the new session is not root/system level
    #         if user_type == 'user':
    #             assert obs['success'] == False
    #             assert env.state.hosts[hostname].services[ProcessName.SSHD].active is True
    #         else:
    #             assert obs['success'] == True
    #             services = env.state.hosts[hostname].services
    #             inactive_services = [name for name, service in services.items() if not service.active]
    #             assert obs[hostname]['Processes'][0]['process_name'] in inactive_services
