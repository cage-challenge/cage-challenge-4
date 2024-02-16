from ipaddress import IPv4Address
import random
from typing import List, Tuple
import pytest
from CybORG.Agents.Wrappers.BlueEnterpriseWrapper import BlueEnterpriseWrapper
from CybORG.Shared.AgentInterface import AgentInterface
from CybORG.Shared.Session import Session
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import BlockTrafficZone
from CybORG.Simulator.Actions.ConcreteActions.ExploitActions import SSHBruteForce
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import SUBNET
from CybORG.Simulator.SimulationController import SimulationController
from CybORG.env import CybORG

@pytest.mark.skip('Test unfinished.')
def test_phases_have_communication_policy():
    """
    From Network Connectivity and Communication policy, paragraph 1:
    Each mission phase has an associated communication policy governing how zones are intended to
    connect to one another.
    """

@pytest.mark.skip('Test unfinished.')
def test_policies_implemented_automatically():
    """
    From Network Connectivity and Communication policy, paragraph 1:
    When the mission phase changes the intended policy is implemented automatically, overwriting
    the current configuration if necessary.
    """

@pytest.mark.skip('Test unfinished.')
def test_only_associated_connections_are_changed():
    """
    From Network Connectivity and Communication policy, paragraph 1:
    Only connections associated with the given mission are changed (for example, when mission 2A is
    activated, only connections with Restricted Zone A and Operational Zone A are affected).
    """


def test_intended_and_firewall_state_communicated_to_blue_agents(cc4_blue_wrapper: BlueEnterpriseWrapper):
    """
    From Network Connectivity and Communication policy, paragraph 1:
    The intended policy and actual firewall state is also communicated to blue agents in their
    observation vector.
    """
    NUM_SUBNETS = len(SUBNET)
    CURRENT_MISSION_INDEX = 0
    START_INDEX = CURRENT_MISSION_INDEX + 1
    BLOCKED_SUBNETS_SLICE = slice(START_INDEX,START_INDEX + NUM_SUBNETS)
    COMMS_POLICY_SLICE = slice(BLOCKED_SUBNETS_SLICE.stop, BLOCKED_SUBNETS_SLICE.stop + NUM_SUBNETS)
    
    results, _ = cc4_blue_wrapper.reset()
    for agent, value in results.items():
        comms_block = value[COMMS_POLICY_SLICE]
        assert comms_block is not None, f"agent '{agent}' does not have a comms block!"

def test_blue_agents_can_open_and_close_firewalls(cc4_cyborg: CybORG):
    """
    From Network Connectivity and Communication policy, paragraph 1:
    Blue agents can open and close firewalls between their zone and other networks, for example to
    prevent infections from red agents, but may incur penalties if their changes prevent green
    agents from accomplishing their own goals. Firewalls are present in each zone, so connections
    must be open in both zones for a green agent to communicate between them.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    from_subnet = "contractor_network_subnet"
    to_subnet = 'operational_zone_b_subnet'
    red_agent_interface, red_session = get_agent(sim_controller, from_subnet, "red")
    red_agent = red_agent_interface.agent_name
    blue_agent_interface, blue_session = get_agent(sim_controller, to_subnet, "blue")
    blue_agent = blue_agent_interface.agent_name

    # Attempt SSHBruteForce from User0 to Enterprise0.
    # Not blocked -> should succeed.
    ip_address = IPv4Address(sim_controller.hostname_ip_map[blue_session.hostname])
    actions = { red_agent: SSHBruteForce(session=0, agent=red_agent, ip_address=ip_address) }
    obs, rew, done, info = cc4_cyborg.parallel_step(actions, skip_valid_action_check=True)
    assert obs[red_agent]['success'] == True

    # Block User Zone -> Enterprise Zone traffic
    # This is a simultaneous block action and exploit action ->
    # Block and Exploit will both return success == True
    ip_address = IPv4Address(sim_controller.hostname_ip_map[blue_session.hostname])
    actions = {
        red_agent: SSHBruteForce(session=0, agent=red_agent, ip_address=ip_address),
        blue_agent: BlockTrafficZone(
            session=0, agent=blue_agent, from_subnet=from_subnet, to_subnet=to_subnet
        )
    }
    obs, rew, done, info = cc4_cyborg.parallel_step(actions, skip_valid_action_check = True)
    assert obs[red_agent]['success'] == True
    assert obs[blue_agent]['success'] == True

    # Attempt SSHBruteForce from User0 to Enterprise0.
    # Blocked -> should fail.
    action = SSHBruteForce(session=0, agent=red_agent, ip_address=ip_address)
    obs, rew, done, info = cc4_cyborg.parallel_step({red_agent: action}, skip_valid_action_check = True)
    assert obs[red_agent]['success'] == False

@pytest.mark.skip('Blue wrapper test')
def test_8_bit_messages(cc4_blue_wrapper: BlueEnterpriseWrapper):
    """
    From Network Connectivity and Communication policy, paragraph 1:
    Some blue agents may communicate with each other regardless of firewall policy via 8-bit
    messages.
    """

@pytest.mark.skip('Test unfinished.')
def test_defender_inter_agent_communication(cc4_blue_wrapper: BlueEnterpriseWrapper):
    """
    From Network Connectivity and Communication policy, paragraph 2:
    Some defending agents have the capability to communicate 8-bit messages with each other.
    Specifically, the Headquarters agent can communicate with everybody, agents in Restricted zones
    can communicate with their corresponding operational zone, but the two agents in the
    operational zone cannot communicate with anybody. Figure 2 shows how information can flow only
    into Operational Zone A, but never out. See Table 1 for the complete (initial) network
    communication security policy for the mission pre-planning phase.
    """

def get_agent(sim_controller: SimulationController, subnet: str, team: str) -> Tuple[AgentInterface, Session]:
    """
    This method chooses a random agent of a given team that is found in the subnet provided.
    """
    valid_sessions: List[Session] = []
    for agent, sessions in sim_controller.state.sessions.items():
        if team in agent:
            for session in sessions.values():
                if subnet in session.hostname:
                    valid_sessions.append(session)
    assert valid_sessions, f"Could not find valid agent within subnet {subnet}"
    session = random.choice(valid_sessions)
    agent_interface = sim_controller.agent_interfaces[session.agent]
    return agent_interface, session
