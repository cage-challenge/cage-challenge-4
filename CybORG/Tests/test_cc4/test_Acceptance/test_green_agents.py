import pytest
from CybORG.Simulator.Actions.ConcreteActions.PhishingEmail import PhishingEmail
from CybORG.Simulator.Actions.GreenActions.GreenAccessService import GreenAccessService
from CybORG.Simulator.Actions.GreenActions.GreenLocalWork import GreenLocalWork
from CybORG.Simulator.SimulationController import SimulationController
from CybORG.env import CybORG

def test_green_agents_on_every_host(cc4_cyborg: CybORG):
    """
    From Green agents, paragraph 1:
    Users are represented by green agents, which are present on every host.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    hosts = set()
    sessions = sim_controller.state.sessions
    user_hosts = [host for host in sim_controller.state.hosts if "user" in host]
    green_session_sets = [value for key, value in sessions.items() if "green" in key]
    for green_session_set in green_session_sets:
        for green_session in green_session_set.values():
            hosts.add(green_session.hostname)
    assert len(hosts) == len(user_hosts)

def test_green_agents_do_local_work(cc4_cyborg: CybORG):
    """
    From Green agents, paragraph 1:
    Green agents randomly do local work or attempt to reach out to external services, either in
    their local or a remote zone. The service and zone a green agent chooses will be determined
    randomly, but are restricted to valid connections for the current mission phase as governed by
    the communication policy tables below.
    """
    actions = set()
    for _ in range(10):
        cc4_cyborg.step()
        agents = cc4_cyborg.environment_controller.agent_interfaces
        for agent in agents.values():
            if "green" in agent.agent_name:
                actions.add(type(agent.last_action))
    for action in [GreenAccessService, GreenLocalWork]:
        assert action in actions, f"Green agents don't seem to have {action} available to them!"

def test_false_alerts(cc4_cyborg: CybORG):
    """
    From Green agents, paragraph 3:
    Green agents occasionally generate false alerts while going about their work by exhibiting
    behavior similar to a red agent, such as transferring data between hosts. 
    """
    FP_DETECTION_RATE = 1.00
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    
    # get green agent
    agents = sim_controller.agent_interfaces.items()
    agent_interface = next((agent for agent_name, agent in agents if 'green' in agent_name), None)

    # Check there are no pre-existing network_connections events
    for host in sim_controller.state.hosts.values():
        assert not host.events.network_connections

    # initialise and execute the action
    action = GreenAccessService(
        agent=agent_interface.agent.name,
        session_id=0,
        src_ip=agent_interface.agent.own_ip,
        allowed_subnets=agent_interface.allowed_subnets,
        fp_detection_rate=FP_DETECTION_RATE
    )
    action.execute(sim_controller.state)

    # Check for newly created network_connections events
    new_network_connection_events = []
    for host in sim_controller.state.hosts.values():
        new_network_connection_events += host.events.network_connections

    # Check dictionary contents
    dest_ip_flag = False
    for event in new_network_connection_events:
        assert action.ip_address == event.local_address
        if action.dest_ip == event.remote_address:
            dest_ip_flag = True
    assert dest_ip_flag

def test_phishing_attacks(cc4_cyborg: CybORG, mocker):
    """
    From Green agents, paragraph 3:
    They also sometimes introduce red agents into the network via succumbing to phishing attacks,
    installing unapproved software, and general poor security hygiene.
    """
    FP_DETECTION_RATE = 0.00
    PHISHING_ERROR_RATE = 1.00
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    spy = mocker.spy(PhishingEmail, "execute")
    
    # get green agent
    agents = sim_controller.agent_interfaces.items()
    agent_interface = next((agent for agent_name, agent in agents if 'green' in agent_name), None)

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE
    )
    action.execute(sim_controller.state)
    assert spy.call_count == 1
