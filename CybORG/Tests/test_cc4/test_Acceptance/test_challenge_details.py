from collections import defaultdict
from typing import List
import pytest
from pytest_mock import MockerFixture
from CybORG.Simulator.Actions import Sleep
from CybORG.Simulator.SimulationController import SimulationController
from CybORG.env import CybORG
from CybORG.Tests.test_cc4.cyborg_env_creation import create_cyborg_env
from CybORG.Simulator.Actions.GreenActions.GreenLocalWork import GreenLocalWork

def test_has_four_subnetworks(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 1:
    The network for this challenge is split into four smaller networks as can be seen in Figure 1.
    Two of these are deployed networks, one is the Headquarters (HQ) network and another is the
    Contractor network. These networks connect together via the internet.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    internet_node = sim_controller.state.hosts['root_internet_host_0']
    internet_connections = internet_node.interfaces[0].data_links
    assert len(internet_connections) == 4, f"Network is split into {len(internet_connections)} subnetworks, not 4!"

def test_has_correct_security_zones(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 2:
    Each deployed network consists of two security zones: a restricted zone and an operational
    zone. The Headquarters network consists of three security zones: a Public Access Zone, an Admin
    Zone and an Office Network. The Contractor network only contains a single UAV control zone.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    subnets = sim_controller.subnet_cidr_map

    assert subnets["restricted_zone_a_subnet"] is not None
    assert subnets["operational_zone_a_subnet"] is not None
    assert len([s for s in subnets.keys() if "zone_a" in s]) == 2

    assert subnets["restricted_zone_b_subnet"] is not None
    assert subnets["operational_zone_b_subnet"] is not None
    assert len([s for s in subnets.keys() if "zone_b" in s]) == 2

    assert subnets["public_access_zone_subnet"] is not None
    assert subnets["admin_network_subnet"] is not None
    assert subnets["office_network_subnet"] is not None

    assert subnets["contractor_network_subnet"] is not None
    assert len([s for s in subnets.keys() if "contractor" in s]) == 1

def test_host_counts_are_random(cc4_cyborg_list: List[CybORG]):
    """
    From Challenge details, paragraph 3:
    In order to encourage the development of robust agents, the number of hosts in each security
    zone
    """
    host_counts_set = {len(cyborg.environment_controller.state.hosts) for cyborg in cc4_cyborg_list}
    assert len(host_counts_set) > 1, "All instances have same number of hosts"

def test_host_services_are_random(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 3:
    and their services will be randomised.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    hosts = sim_controller.state.hosts.values()
    host_services = {frozenset(host.services.keys()) for host in hosts}
    assert len(host_services) > 1, "All hosts have identical services"

def test_zones_have_correct_number_of_servers(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 3:
    Each zone will have between 1-6 servers.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    server_counts = defaultdict(int)
    servers = [host for host in sim_controller.state.hosts.values() if "server" in host.hostname]
    for server in servers:
        subnet = sim_controller.state.hostname_subnet_map[server.hostname]
        server_counts[subnet] += 1
    for count in server_counts.values():
        assert 0 < count < 7, f"{subnet} has an invalid number of server hosts, {count}!"

def test_zones_have_correct_number_of_user_hosts(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 3:
    Each zone will have between 3-10 user hosts.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    user_host_counts = defaultdict(int)
    user_hosts = [host for host in sim_controller.state.hosts.values() if "user" in host.hostname]
    for user_host in user_hosts:
        subnet = sim_controller.state.hostname_subnet_map[user_host.hostname]
        user_host_counts[subnet] += 1
    for subnet, count in user_host_counts.items():
        assert 2 < count < 11, f"{subnet} has an invalid number of user hosts, {count}!"

def test_hosts_have_correct_number_of_services(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 3:
    Each host will have a minimum of 1 service with a maximum of 10.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    hosts_with_no_services = ['root_internet_host_0']
    for host in sim_controller.state.hosts.values():
        if not host.hostname in hosts_with_no_services and 'router' not in host.hostname:
            assert 0 < len(host.services) < 11

def test_defenders_are_on_correct_networks(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 4:
    The network will have 5 network defenders. Each deployed network will have two, one for each
    security zone. The Headquarters will have a single defensive agent for all zones, while the
    Contractor network will be undefended.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    agents = sim_controller.agent_interfaces.values()
    defenders = [agent for agent in agents if "blue" in agent.agent_name]
    assert len(defenders) == 5
    allowed_subnets = [
        ["restricted_zone_a_subnet"],
        ["operational_zone_a_subnet"],
        ["restricted_zone_b_subnet"],
        ["operational_zone_b_subnet"],
        ["public_access_zone_subnet", "admin_network_subnet", "office_network_subnet"]
    ]
    for subnets in allowed_subnets:
        assert len([d for d in defenders if d.allowed_subnets == subnets]) == 1

def test_red_team_starts_in_contractor_network(cc4_cyborg_list: List[CybORG]):
    """
    From Challenge details, paragraph 5:
    Red team begins the operation with access to a random machine in the contractor network. 
    """
    all_hosts = []
    for cyborg in cc4_cyborg_list:
        sim_controller: SimulationController = cyborg.environment_controller
        agents = sim_controller.agent_interfaces.values()
        attackers = [agent for agent in agents if "red" in agent.agent_name and agent.active]
        assert len(attackers) == 1
        all_hosts.append(sim_controller.state.sessions[attackers[0].agent_name][0].hostname)

    assert len(set(all_hosts)) > 1
    assert 'contractor_network' in all_hosts[0]

def test_red_agents_can_spawn(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 5:
    Every turn there is also a small chance that a red agent will spawn in the HQ network.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller

    # Assert that there's only one active red agent to begin with.
    agents = sim_controller.agent_interfaces.values()
    red_agents = [agent for agent in agents if "red" in agent.agent_name and agent.active]
    assert len(red_agents) == 1
    
    # Assert that a new red agent will activate in the HQ subnet within 100 steps.
    hq_network_subnets = [
        'public_access_zone_subnet', 'admin_network_subnet', 'office_network_subnet'
    ]
    passed = False
    for _ in range(100):
        cc4_cyborg.step()
        agents = sim_controller.agent_interfaces.values()
        red_agents = [agent for agent in agents if "red" in agent.agent_name and agent.active]
        if len(red_agents) > 1:
            passed = any(
                agent for agent in red_agents if agent.allowed_subnets == hq_network_subnets
            )
            if passed: break
    assert passed, "No additional red agents spawned after 100 steps!"

def test_red_can_enter_network_via_compromised_service(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 5:
    Otherwise, red can only enter the deployed networks when a green user accesses a compromised
    service.
    """

    FP_DETECTION_RATE = 0.00
    PHISHING_ERROR_RATE = 1.00 # forces PhishingEmail action

    preexisting_red_on_host = True
    while preexisting_red_on_host:
        cyborg, agent_interface = create_cyborg_env()
        state = cyborg.environment_controller.state
        green_hostname = state.ip_addresses[agent_interface.agent.own_ip]

        before_agent_sessions_on_host = [agent for agent, arr_sessions in state.hosts[green_hostname].sessions.items() if len(arr_sessions) > 0]
        preexisting_red_on_host = False
        for agent_name in before_agent_sessions_on_host:
            if 'red' in agent_name:
                preexisting_red_on_host = True

    action = GreenLocalWork(
        agent=agent_interface.agent_name,
        session_id=0,
        ip_address=agent_interface.agent.own_ip,
        fp_detection_rate=FP_DETECTION_RATE,
        phishing_error_rate=PHISHING_ERROR_RATE,
    )
    action.execute(state)

    after_agent_sessions_on_host = [agent for agent, arr_sessions in state.hosts[green_hostname].sessions.items() if len(arr_sessions) > 0]

    red_on_host = False
    for agent_name in after_agent_sessions_on_host:
        if 'red' in agent_name:
            red_on_host = True
    assert red_on_host


def test_only_one_red_agent_per_zone(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 5:
    There is a maximum of one red agent in each zone.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    zone_red_agent_counts = defaultdict(int)
    agents = sim_controller.agent_interfaces.values()
    attackers = [agent for agent in agents if "red" in agent.agent_name]
    for attacker in attackers:
        for zone in attacker.allowed_subnets:
            zone_red_agent_counts[zone] += 1
    for zone, count in zone_red_agent_counts.items():
        assert count == 1, f"{zone} has more than one ({count}) red agent!"

def test_red_agents_can_be_on_multiple_hosts(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 5:
    Red agents can maintain a presence on multiple hosts.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    for _ in range(100):
        cc4_cyborg.step()
        sessions = defaultdict(set)
        for agent, session_dict in sim_controller.state.sessions.items():
            if "red" not in agent:
                continue
            for session in session_dict.values():
                sessions[agent].add(session.hostname)
        passed = any(len(hosts) > 1 for hosts in sessions.values())
        if passed:
            break
    assert passed, "Did not see any instances of a red agent being on multiple hosts after 100 steps!"

def test_red_can_respawn_in_contractor_network(cc4_cyborg: CybORG):
    """
    From Challenge details, paragraph 5:
    While Blue team may succeed in removing all traces of red team from a network, red will always
    respawn in the Contractor Network.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller

    # Set all red agents to inactive.
    agents = sim_controller.agent_interfaces.values()
    for agent in agents:
        if "red" in agent.agent_name:
            agent.active = False
    assert not [agent for agent in agents if "red" in agent.agent_name and agent.active]
    
    # Assert that a red agent will re-activate in the contractor subnet within 100 steps
    passed = False
    for _ in range(100):
        cc4_cyborg.step()
        agents = sim_controller.agent_interfaces.values()
        red_agent = next(agent for agent in agents if "red" in agent.agent_name and agent.active)
        if red_agent:
            passed = red_agent.allowed_subnets == ['contractor_network_subnet']
            break
    assert passed

def test_red_agents_select_random_strategies(cc4_cyborg_list: List[CybORG]):
    """
    From Challenge details, paragraph 6:
    The red agents will each use a randomly selected strategy.
    """
    action_lists = defaultdict(list)
    for cyborg in cc4_cyborg_list:
        sim_controller: SimulationController = cyborg.environment_controller
        agents = sim_controller.agent_interfaces.values()
        red_agent = next(agent for agent in agents if "red" in agent.agent_name and agent.active)
        index = cc4_cyborg_list.index(cyborg)
        for _ in range(10):
            cyborg.step()
            action_lists[index].append(type(red_agent.last_action))
    unique_action_lists = set(map(tuple, action_lists.values()))

    # will fail as the red agent is sleep agent
    if red_agent.agent.__str__()=='SleepAgent':
        assert len(unique_action_lists)== 1
    else:
        assert len(unique_action_lists) > 1

def test_action_durations(cc4_cyborg: CybORG, mocker: MockerFixture):
    """
    From Challenge details, paragraph 7:
    Agent actions now have a specified time duration, which varies depending on the action chosen.
    Agents must wait until their action is completed before they are prompted to launch another
    action. Once an agent has chosen it cannot be cancelled.
    """
    sim_controller: SimulationController = cc4_cyborg.environment_controller
    agents = sim_controller.agent_interfaces.values()
    blue_agent = next(agent for agent in agents if "blue" in agent.agent_name)

    # Create an action with a duration > 1
    action = Sleep()
    action.duration = 2
    assert action.duration == 2

    # Assert we're starting with zero calls
    spy = mocker.spy(action, "execute")
    assert spy.call_count == 0

    # Since the action has a duration of 2, we would not expect it to execute after one step.
    cc4_cyborg.step(agent=blue_agent.agent_name, action=action, skip_valid_action_check=True)
    assert spy.call_count == 0

    # Assert the action *is* executed after a second step.
    cc4_cyborg.step(skip_valid_action_check=True)
    assert spy.call_count == 1
