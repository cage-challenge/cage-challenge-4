import pytest
import pytest_mock
from ipaddress import IPv4Network, IPv4Address

from CybORG import CybORG
from CybORG.Shared.Enums import SessionType
from CybORG.Simulator.Actions.GreenActions.GreenLocalWork import GreenLocalWork
from CybORG.Simulator.Actions.ConcreteActions.PhishingEmail import PhishingEmail
from CybORG.Tests.test_cc4.cyborg_env_creation import create_cyborg_env


""" Tests for GreenLocalWork Action and associated (sub-action) PhishingEmail Action. """

def test_green_local_work_clear_run():
    """ Test GreenLocalWork Action executes, without false-positive detection and phishing email subaction, successfully with no errors. """

    FP_DETECTION_RATE = 0.00
    PHISHING_ERROR_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )
    result_obs = action.execute(state)

    assert result_obs.data['success']

def test_zero_rates_none_occur(mocker):
    """ Test when fp_detection_rate and phishing_error_rate are zero, neither run when GreenLocalWork is executed. """

    FP_DETECTION_RATE = 0.00
    PHISHING_ERROR_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    agent = agent_interface.agent
    state = cyborg.environment_controller.state
    hostname = cyborg.environment_controller.state.ip_addresses[agent.own_ip]

    host = cyborg.environment_controller.state.hosts[hostname]
    past_process_creation_host_events = host.events.process_creation

    assert not past_process_creation_host_events

    spy = mocker.spy(PhishingEmail, "execute")

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )
    action.execute(state)
    
    assert spy.call_count == 0

    host = cyborg.environment_controller.state.hosts[hostname]
    new_process_creation_host_events = host.events.process_creation

    assert not new_process_creation_host_events

def test_fp_detection_rate_occurs():
    """ Test when fp_detection_rate = 1.00, fp_detection occurs. """

    FP_DETECTION_RATE = 1.00
    PHISHING_ERROR_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    agent = agent_interface.agent
    state = cyborg.environment_controller.state
    hostname = cyborg.environment_controller.state.ip_addresses[agent.own_ip]

    host = cyborg.environment_controller.state.hosts[hostname]
    past_process_creation_host_events = host.events.process_creation

    assert not past_process_creation_host_events

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )
    action.execute(state)

    host = cyborg.environment_controller.state.hosts[hostname]
    new_process_creation_host_events = host.events.process_creation

    assert len(new_process_creation_host_events) == 1
    assert new_process_creation_host_events[0]['local_address'] == agent.own_ip


@pytest.mark.skip("Tests blue monitor functionality, doesn't pick up host.events 100% of the time causing failures")
def test_fp_detection_rate():
    """ Test that when fp_detection occurs, the host appears in the appropriate blue observation spaces.

    fp_detection works by adding a host event to the process_creation.
    Before the end of the step when this action happens, the subAction of the blue_agents (Monitor) occurs.
    Monitor.execute() causes the host.event to be removed and the host is then put into the observation space of a blue agent.
    Only blue agents that have a session on that host will be affected.
    """

    FP_DETECTION_RATE = 1.00
    PHISHING_ERROR_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    agent = agent_interface.agent

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )

    cyborg.step(action=action, agent=agent.name)

    hostname_via_ip = cyborg.environment_controller.state.ip_addresses[agent.own_ip]
    host = cyborg.environment_controller.state.hosts[hostname_via_ip]

    # Check that the host checked has the agent as a session
    assert host.sessions[agent.name] == [0]

    # Find corresponding blue agent(s)
    host_blue_agents = []
    for agent_session, sid in host.sessions.items():
        if 'blue' in agent_session and not sid == []:
            host_blue_agents.append(agent_session)

    # If there are no blue agents with sessions on the host, then no blue agents will see the fp_deception
    if not host_blue_agents:
        assert True
        return

    # For each blue agent, check if host in observation space
    for blue_agent in host_blue_agents:
        blue_obs = cyborg.environment_controller.observation[blue_agent]
        for blue_ob in blue_obs.observations:
            if hostname_via_ip in blue_ob.data.keys():
                assert True
                return

    assert False


def test_phishing_error_rate_occur(mocker):
    """ This test checks that, when phishing_error_rate = 1.00, phishing action occurs. """

    FP_DETECTION_RATE = 0.00
    PHISHING_ERROR_RATE = 1.00
    
    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state

    spy = mocker.spy(PhishingEmail, "execute")
    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )
    action.execute(state)
    assert spy.call_count == 1


def test_phishing_error_rate_session_creation():
    """ This test checks that when the Phishing Action occurs, a red abstract session is created on that host 

    Note: currently agent outside subnet is put as new session agent. May need to be changed to dormant red agent in subnet
    """

    FP_DETECTION_RATE = 0.00
    PHISHING_ERROR_RATE = 1.00
    
    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state
    hostname = cyborg.environment_controller.state.ip_addresses[agent_interface.agent.own_ip]

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )
    result_obs = action.execute(state)

    list_of_host_sessions = result_obs.data[hostname]['Sessions']

    check_red_session = False
    for session in list_of_host_sessions:
        if 'red_agent' in session['agent'] and session['Type'] == SessionType.RED_ABSTRACT_SESSION:
            check_red_session = True

    assert check_red_session

def test_failure_on_fully_degraded_services():
    """Tests that the action can fail when the services on the host have no reliability (due to being degraded)."""

    FP_DETECTION_RATE = 0.00
    PHISHING_ERROR_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state
    hostname = state.ip_addresses[agent_interface.agent.own_ip]

    # change all service percent reliability to 0
    for service in state.hosts[hostname].services.values():
        service._percent_reliable = 0

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )
    result_obs = action.execute(state)
    assert result_obs.data['success'] == False
