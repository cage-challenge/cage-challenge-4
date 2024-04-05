import pytest
import pytest_mock
import networkx as nx

from random import choice as rand_choice

from CybORG import CybORG
from CybORG.Simulator.State import State
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import SUBNET
from CybORG.Simulator.Actions.GreenActions.GreenAccessService import GreenAccessService
from CybORG.Tests.test_cc4.cyborg_env_creation import create_cyborg_env


def test_GreenAccessService():
    """Test that GreenAccessService Action initialises and executes without exceptions, and the observation returned is successful."""
    
    FP_DETECTION_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state
    agent = agent_interface.agent

    action = GreenAccessService(agent=agent.name, session_id=0, src_ip = agent.own_ip, allowed_subnets=agent_interface.allowed_subnets, fp_detection_rate = FP_DETECTION_RATE)
    result_obs = action.execute(state)

    assert result_obs.data['success']


def test_execute_no_host_events():
    """Tests that when GreenAccessService.execute() is run, in a situation when no host events should be created, no host events are created.
    
    Conditions
        - fp_detection_rate is set to 0.00
        - a new environment is utilised (step = 0) with SleepAgents for all blue and red agents. 
        - there are no pre-existing host events
    """
    FP_DETECTION_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state
    agent = agent_interface.agent
    hostname = cyborg.environment_controller.state.ip_addresses[agent.own_ip]

    # Check there are no pre-existing network_connections events
    for host in cyborg.environment_controller.state.hosts.values():
        assert not host.events.network_connections

    # initialise and execute the action
    action = GreenAccessService(agent=agent.name, session_id=0, src_ip=agent.own_ip, 
                                allowed_subnets=agent_interface.allowed_subnets, fp_detection_rate=FP_DETECTION_RATE)
    
    result_obs = action.execute(state)

    # Check for no newly created network_connections events
    for host in cyborg.environment_controller.state.hosts.values():
        assert not host.events.network_connections

    assert True

@pytest.mark.skip("Links are never removed during episode, so test not necessary")
def test_obs_fail_on_no_route():
    """Tests that when a route is not possible, the observation is unsuccessful.
    
    Conditions:
        - route is forced go between subnets
        - the internet node is removed so a route between subnets is not possible
    """
    FP_DETECTION_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state 
    agent = agent_interface.agent
    hostname = cyborg.environment_controller.state.ip_addresses[agent.own_ip]

    # Take out the internet node so that there is no route between subnets
    state.link_diagram.remove_node("root_internet_host_0")

    # initialise and execute the action
    action = GreenAccessService(
        agent=agent.name,
        session_id=0,
        src_ip=agent.own_ip,
        allowed_subnets=agent_interface.allowed_subnets,
        fp_detection_rate=FP_DETECTION_RATE
    )
    
    same_subnet_flag = True
    while same_subnet_flag:
        result_obs = action.execute(state)

        src_subnet = state.hostname_subnet_map[hostname]
        dest_subnet = state.hostname_subnet_map[state.ip_addresses[action.dest_ip]]

        if not src_subnet == dest_subnet:
            interconnected_subnets = [
                [SUBNET.ADMIN_NETWORK, SUBNET.OFFICE_NETWORK, SUBNET.PUBLIC_ACCESS_ZONE], 
                [SUBNET.OPERATIONAL_ZONE_A, SUBNET.RESTRICTED_ZONE_A],
                [SUBNET.OPERATIONAL_ZONE_B, SUBNET.RESTRICTED_ZONE_B],
                [SUBNET.CONTRACTOR_NETWORK]
            ]
            for grouping in interconnected_subnets:
                if src_subnet in grouping and not dest_subnet in grouping:
                    same_subnet_flag = False
                    break

    assert result_obs.data["success"] == False

def set_action_attributes(state:State, action: GreenAccessService, target_hostname: str):
    action.dest_ip = state.hostname_ip_map[target_hostname]
    service = rand_choice(list(state.hosts[target_hostname].services.keys()))
    action.dest_port = state.hosts[target_hostname].services[service].process

@pytest.mark.skip("Green blocking changed to only functions on (source, destination) blocks, not on routing inbetween. New functionality tested in test_BlueRewardMachine.")
@pytest.mark.parametrize('block_type', ['host', 'subnet'])
def test_execute_host_events_blocked(mocker, block_type):
    """Test that, when locations along the route are blocked, the appropriate network_connections events are added."""
    
    FP_DETECTION_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state 
    agent = agent_interface.agent
    hostname = cyborg.environment_controller.state.ip_addresses[agent.own_ip]

    past_network_connections_events = []
    for _, host in cyborg.environment_controller.state.hosts.items():
        network_connections = host.events.network_connections
        if network_connections:
            past_network_connections_events.append(network_connections)

    # Check there are no pre-existing network_connections events
    assert not past_network_connections_events

    # initialise and execute the action
    action = GreenAccessService(
        agent=agent.name,
        session_id=0,
        src_ip=agent.own_ip,
        allowed_subnets=agent_interface.allowed_subnets,
        fp_detection_rate=FP_DETECTION_RATE
    )

    # get new target host                           
    has_services = False
    while not has_services:
        target_hostname = rand_choice(list(state.hosts.keys()))
        if len(state.hosts[target_hostname].services) > 0 and (not state.hostname_subnet_map[target_hostname] == state.hostname_subnet_map[hostname]):
            has_services = True
    target_ip = state.hostname_ip_map[target_hostname]

    # get new route
    new_route = action.get_route(state=state, target=target_hostname, source=hostname, routing=True)

    # mock the random_reachable_ip_and_port function to insert the new target host and port
    mocker.patch( __name__ + '.' + GreenAccessService.__name__ + ".random_reachable_ip", return_value=target_ip)
    # mock the get_used_route function to insert the new route
    mocker.patch( __name__ + '.' + GreenAccessService.__name__ + "._get_my_used_route", return_value=new_route)
    
    # add a block in the route
    if block_type == 'host':
        state.blocks[new_route[1]] = [new_route[0]]
    elif block_type == 'subnet':
        state.blocks[state.hostname_subnet_map[new_route[-1]]] = state.hostname_subnet_map[new_route[0]]
    else:
        assert False

    # execute the action with the blocked route
    result_obs = action.execute(state)

    # check action success is FALSE
    assert result_obs.data['success'] == False

    # Check for newly created network_connections events
    new_network_connection_events = []
    for hostname, host in cyborg.environment_controller.state.hosts.items():
        list_network_connections_events = host.events.network_connections
        if len(list_network_connections_events) > 0:
            for event in list_network_connections_events:
                new_network_connection_events.append(event)

    assert len(new_network_connection_events) == 1

    local_addr = new_network_connection_events[0].local_address
    remote_addr = new_network_connection_events[0].remote_address

    if block_type == 'host':
        assert (state.hostname_ip_map[new_route[0]] == local_addr and 
                state.hostname_ip_map[new_route[1]] == remote_addr)
    elif block_type == 'subnet':
        assert (state.hostname_subnet_map[new_route[0]] == state.hostname_subnet_map[state.ip_addresses[local_addr]] and 
                state.hostname_subnet_map[new_route[-1]] == state.hostname_subnet_map[state.ip_addresses[remote_addr]])
    else:
        assert False

def test_execute_host_events_fp():
    """Test that when false positive detection happens, a network_connections event is added to the host.
    
    When fp_detection_rate is at 1, an event will be added to every host along the route (not src), with the local_address being src.
    """
    FP_DETECTION_RATE = 1.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state 
    agent = agent_interface.agent
    hostname = cyborg.environment_controller.state.ip_addresses[agent.own_ip]

    # Check there are no pre-existing network_connections events
    for host in cyborg.environment_controller.state.hosts.values():
        assert not host.events.network_connections

    # initialise and execute the action
    action = GreenAccessService(
        agent=agent.name,
        session_id=0,
        src_ip=agent.own_ip, 
        allowed_subnets=agent_interface.allowed_subnets,
        fp_detection_rate=FP_DETECTION_RATE
    )
    
    result_obs = action.execute(state)

    # Check for newly created network_connections events
    new_network_connection_events = []
    for host in cyborg.environment_controller.state.hosts.values():
        new_network_connection_events += host.events.network_connections

    # Check dictionary contents
    dest_ip_flag = False
    for event in new_network_connection_events:
        assert action.ip_address == event.local_address
        if action.dest_ip == event.remote_address:
            dest_ip_flag = True
    assert dest_ip_flag


def test_random_reachable_ip():
    """Test that function random_reachable_ip_and_port outputs correctly for mission phase.

    Checked properties of output:
        1) dest_ip and dest_port are changed once run on initial state (this may not alway be the case throughout the episode).
        2) dest_ip is not the same as src_ip
        3) dest_ip is not in a subnet that is not reachable for that mission phase, unless in that subnet
        4) destination host is a server

    """

    FP_DETECTION_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state
    agent = agent_interface.agent

    mission_phase = state.mission_phase
    sg_allowed_subnets = cyborg.environment_controller.scenario_generator._set_allowed_subnets_per_mission_phase()[mission_phase]

    action = GreenAccessService(
        agent=agent.name,
        session_id=0,
        src_ip=agent.own_ip,
        allowed_subnets=agent_interface.allowed_subnets,
        fp_detection_rate=FP_DETECTION_RATE
    )
    
    # vars should be empty initally
    assert action.dest_ip == ""
    assert action.dest_port == ""
    
    action.dest_ip = action.random_reachable_ip(state=state)

    # vars should be changed once function run
    assert not action.dest_ip == ""

    # ip should not be the same as itself
    assert action.dest_ip != agent.own_ip

    # ip should not be in a subnet that is not reachable for that mission phase, unless in that subnet
    dest_hostname = state.ip_addresses[action.dest_ip]
    dest_subnet = state.hostname_subnet_map[dest_hostname]
    src_subnet = state.hostname_subnet_map[state.ip_addresses[action.ip_address]]

    all_subnets = list(state.subnet_name_to_cidr.keys())
    all_subnets.remove(src_subnet)

    if dest_subnet != src_subnet:
        for idx in range(len(sg_allowed_subnets)):
            s1, s2 = sg_allowed_subnets[idx]
            if s1 is src_subnet:
                all_subnets.remove(s2)
            elif s2 is src_subnet:
                all_subnets.remove(s1)

        for subnet in all_subnets:
            assert dest_subnet != subnet

    # host should be a server
    assert 'server' in dest_hostname


def test_get_used_route():
    """Test for getting the used route between the source and destination hosts.
    
    First and last host in list checked to be source and destination host.
    The route itself in calculated in function from RemoteAction parent class, therefore not tested directly for truth.
    """

    FP_DETECTION_RATE = 0.00

    cyborg, agent_interface = create_cyborg_env()
    state = cyborg.environment_controller.state
    agent = agent_interface.agent

    action = GreenAccessService(
        agent=agent.name,
        session_id=0,
        src_ip=agent.own_ip,
        allowed_subnets=agent_interface.allowed_subnets,
        fp_detection_rate=FP_DETECTION_RATE
    )
    action.dest_ip = action.random_reachable_ip(state=state)
    used_route = action._get_my_used_route(state)
    assert used_route[0] == state.ip_addresses[action.ip_address]
    assert used_route[-1] == state.ip_addresses[action.dest_ip]