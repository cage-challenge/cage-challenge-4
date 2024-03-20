import pytest
    
import numpy as np
import random
import networkx as nx
from pettingzoo.test import parallel_api_test
from gymnasium import spaces

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import SUBNET
from CybORG.Agents import SleepAgent
from CybORG.Agents.Wrappers import BlueEnterpriseWrapper, BaseWrapper
from CybORG.Simulator.Actions import Sleep, Monitor
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import BlockTrafficZone
from CybORG.Simulator.HostEvents import NetworkConnection

from CybORG.Agents.Wrappers.BlueEnterpriseWrapper import (
    MESSAGE_LENGTH,
    EMPTY_MESSAGE,
    NUM_MESSAGES,
)

#NUM_MESSAGES = 4
#MESSAGE_LENGTH = 8
NUM_SUBNETS = len(SUBNET)
MAX_SERVER_HOSTS = EnterpriseScenarioGenerator.MAX_SERVER_HOSTS
MAX_USER_HOSTS = EnterpriseScenarioGenerator.MAX_USER_HOSTS
MAX_NUM_HOSTS = MAX_USER_HOSTS + MAX_SERVER_HOSTS 
CURRENT_MISSION_INDEX = 0
START_INDEX = CURRENT_MISSION_INDEX + 1
AGENT_ZONE_SLICE = slice(START_INDEX, START_INDEX + NUM_SUBNETS)
BLOCKED_SUBNETS_SLICE = slice(AGENT_ZONE_SLICE.stop, AGENT_ZONE_SLICE.stop + NUM_SUBNETS)
COMMS_POLICY_SLICE = slice(BLOCKED_SUBNETS_SLICE.stop, BLOCKED_SUBNETS_SLICE.stop + NUM_SUBNETS)
MALICIOUS_PROCESS_SLICE = slice(COMMS_POLICY_SLICE.stop, COMMS_POLICY_SLICE.stop + MAX_NUM_HOSTS)
NETWORK_CONNECTIONS_SLICE = slice(MALICIOUS_PROCESS_SLICE.stop, MALICIOUS_PROCESS_SLICE.stop + MAX_NUM_HOSTS)
MESSAGE_SLICE = slice(NETWORK_CONNECTIONS_SLICE.stop, NETWORK_CONNECTIONS_SLICE.stop + NUM_MESSAGES * MESSAGE_LENGTH)

HQ_AGENT = 'blue_agent_4'
NUM_HQ_SUBNETS = 3
REPEATABLE_LENGTH = NETWORK_CONNECTIONS_SLICE.stop - START_INDEX
LONG_ENDPOINT = START_INDEX + NUM_HQ_SUBNETS * REPEATABLE_LENGTH + NUM_MESSAGES * MESSAGE_LENGTH
LONG_MESSAGE_SLICE = slice(LONG_ENDPOINT - NUM_MESSAGES * MESSAGE_LENGTH, LONG_ENDPOINT)

STEP_TUPLE_LENGTH = 5
NUM_AGENTS = 5

@pytest.fixture
def cyborg():
    sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent, red_agent_class=SleepAgent, steps=3)
    cyborg = CybORG(scenario_generator=sg)
    cyborg = BlueEnterpriseWrapper(cyborg)
    cyborg.reset(seed=123)

    return cyborg

def test_BlueEnterpriseWrapper_inheritence(cyborg):
    assert isinstance(cyborg, BaseWrapper)

@pytest.mark.skip
def test_BlueEnterpriseWrapper_pettingzoo_interface(cyborg):
    parallel_api_test(cyborg, num_cycles=1000)

@pytest.fixture(params=range(NUM_AGENTS), ids=[f'blue_agent_{x}' for x in range(NUM_AGENTS)])
def blue_agent(request):
    return f'blue_agent_{request.param}'

@pytest.fixture
def observation_space(cyborg, blue_agent):
    return cyborg.observation_space(blue_agent)

def test_BlueEnterpriseWrapper_observation_space_type(observation_space):
    assert isinstance(observation_space, spaces.MultiDiscrete)

def test_BlueEnterpriseWrapper_observation_space_length(observation_space, blue_agent):
    assert len(observation_space) == LONG_ENDPOINT if blue_agent==HQ_AGENT else MESSAGE_SLICE.stop

@pytest.fixture
def action_space(cyborg, blue_agent):
    return cyborg.action_space(blue_agent)

def test_BlueEnterpriseWrapper_action_space_type(action_space):
    assert isinstance(action_space, spaces.Discrete)

@pytest.fixture
def num_actions(blue_agent):
    num_agent_subnets = NUM_HQ_SUBNETS if blue_agent==HQ_AGENT else 1
    command_parameter_count = {'AllowTrafficZone': num_agent_subnets * (NUM_SUBNETS - 1),
                'BlockTrafficZone': num_agent_subnets * (NUM_SUBNETS - 1),
                'Restore': num_agent_subnets * MAX_NUM_HOSTS,
                'Remove': num_agent_subnets * MAX_NUM_HOSTS,
                'DeployDecoy': num_agent_subnets * MAX_NUM_HOSTS,
                'Analyse': num_agent_subnets * MAX_NUM_HOSTS, 
                'Monitor': 1,
                'Sleep': 1,
                }

    return sum(command_parameter_count.values())

@pytest.fixture
def num_actions_hq(num_actions):
    command_parameter_count = {k:NUM_HQ_SUBNETS*v for k,v in num_actions}
    command_parameter_count['Monitor'] = 1
    command_parameter_count['Sleep'] = 1

    return sum(command_parameter_count.values())

def test_BlueEnterpriseWrapper_action_space_length(action_space, num_actions, blue_agent):
    assert action_space.n == num_actions

@pytest.fixture
def reset_results(cyborg, blue_agent):
    results = cyborg.reset(blue_agent)
    return results

@pytest.fixture
def reset_obs(reset_results, blue_agent):
    return reset_results[0][blue_agent]

def test_BlueEnterpriseWrapper_reset_obs_type(reset_obs):
    assert type(reset_obs) == np.ndarray

def test_BlueEnterpriseWrapper_reset_obs_length(reset_obs, blue_agent):
    assert len(reset_obs) == LONG_ENDPOINT if blue_agent==HQ_AGENT else MESSAGE_SLICE.stop

@pytest.fixture
def reset_info(reset_results, blue_agent):
    return reset_results[1]

def test_BlueEnterpriseWrapper_reset_info_type(reset_info):
    assert isinstance(reset_info, dict)

@pytest.fixture
def step_results(cyborg, blue_agent):
    cyborg.reset(blue_agent)
    results = cyborg.step(actions={blue_agent:Sleep()})

    return results

def test_BlueEnterpriseWrapper_step_results_type(step_results):
    assert isinstance(step_results, tuple)

def test_BlueEnterpriseWrapper_step_results_length(step_results):
    assert len(step_results) == STEP_TUPLE_LENGTH

@pytest.mark.parametrize("index", range(STEP_TUPLE_LENGTH))
def test_BlueEnterpriseWrapper_step_results_element_types(step_results, index):
    assert isinstance(step_results[index], dict)

@pytest.fixture
def step_obs(step_results, blue_agent):
    return step_results[0][blue_agent]

def test_BlueEnterpriseWrapper_step_obs_type(step_obs):
    assert type(step_obs) == np.ndarray

def test_BlueEnterpriseWrapper_step_obs_length(step_obs, blue_agent):
    assert len(step_obs) == LONG_ENDPOINT if blue_agent==HQ_AGENT else MESSAGE_SLICE.stop

@pytest.fixture
def reward(step_results, blue_agent):
    return step_results[1][blue_agent]

def test_BlueEnterpriseWrapper_reward_type(reward):
    assert isinstance(reward, (int,float))
    
@pytest.fixture
def terminated(step_results, blue_agent):
    return step_results[2][blue_agent]

def test_BlueEnterpriseWrapper_terminated_type(terminated):
    assert isinstance(terminated, bool)

@pytest.fixture
def truncated(step_results, blue_agent):
    return step_results[3][blue_agent]

def test_BlueEnterpriseWrapper_truncated_type(truncated):
    assert isinstance(truncated, bool)

@pytest.fixture
def info(step_results, blue_agent):
    return step_results[4]

def test_BlueEnterpriseWrapper_info_type(info):
    assert isinstance(info, dict)

@pytest.fixture
def mission_phase_list(cyborg, blue_agent):
    '''Run several steps, which will proceed through all mission phases. Extract relevant obs value and actual mission phase and append it to output list for comparison'''
    results, _ = cyborg.reset()
    mission_value = results[blue_agent][CURRENT_MISSION_INDEX]
    mission_phase = cyborg.get_attr("environment_controller").state.mission_phase
    blue_observations = [(mission_value, mission_phase)]
    for i in range(3):
        cyborg.step()
        mission_value = cyborg.get_observation(blue_agent)[CURRENT_MISSION_INDEX]
        mission_phase = cyborg.get_attr("environment_controller").state.mission_phase
        blue_observations.append((mission_value, mission_phase))

    return blue_observations

def test_BlueEnterpriseWrapper_mission_phase(mission_phase_list):
    '''Here we test the first entry in the vector corresponds to the mission phase'''
    assert [x==y for x,y in mission_phase_list] == [True for x in range(len(mission_phase_list))]

@pytest.fixture(params=range(NUM_AGENTS-1), ids=[f'blue_agent_{x}' for x in range(NUM_AGENTS-1)])
def blue_agent_short(request):
    '''Blue agents 0-3 which are responsible for 1 subnet only.'''
    return f'blue_agent_{request.param}'

@pytest.fixture
def blue_subnet(cyborg, blue_agent_short):
    state = cyborg.get_attr("environment_controller").state
    blue_agent_hostname = state.sessions[blue_agent_short][0].hostname
    blue_agent_subnet_name = state.hostname_subnet_map[blue_agent_hostname]
    blue_agent_subnet_cidr = state.subnet_name_to_cidr[blue_agent_subnet_name]

    return blue_agent_subnet_cidr

@pytest.fixture
def reset_obs_short(cyborg, blue_agent_short):
    results = cyborg.reset(blue_agent_short)
    return results[0][blue_agent_short]

def test_BlueEnterpriseWrapper_blocked_reset(reset_obs_short, blue_agent_short):
    '''Test there are no blocked values at begining of episode'''
    blocked_values = reset_obs_short[BLOCKED_SUBNETS_SLICE]

    assert (blocked_values == np.zeros(NUM_SUBNETS)).all()

def test_BlueEnterpriseWrapper_blocked_step(cyborg, blue_agent_short, blue_subnet):
    '''Manually block several hosts and check observation contains them'''
    state = cyborg.get_attr("environment_controller").state
    subnet_names = sorted([k.lower() for k in state.subnet_name_to_cidr])
    blue_subnet_name = state.subnets_cidr_to_name[blue_subnet]
    blocked_subnet_name = random.choice([s for s in subnet_names if s != blue_subnet])
    blocked_index = subnet_names.index(blocked_subnet_name)

    proto_vector = NUM_SUBNETS * [0]
    proto_vector[blocked_index] = 1
    expected_values = np.array(proto_vector)

    action = BlockTrafficZone(
        session=0,
        agent=blue_agent_short,
        from_subnet=blocked_subnet_name,
        to_subnet=blue_subnet_name,
    )

    observations, _, _, _, _ = cyborg.step(actions={blue_agent_short: action})
    blocked_values = observations[blue_agent_short][BLOCKED_SUBNETS_SLICE]

    assert (blocked_values == expected_values).all()

@pytest.fixture(params=['Preplanning', 'MissionA', 'MissionB'])
def mission_phase(request):
    return request.param

@pytest.fixture
def network(mission_phase):
    adjacency_matrices = {
        "Preplanning": np.array(
            [[0, 1, 1, 1, 1, 0, 1, 0, 1],
             [1, 0, 1, 1, 1, 0, 1, 0, 1],
             [1, 1, 0, 1, 1, 0, 1, 0, 1],
             [1, 1, 1, 0, 1, 0, 1, 0, 1],
             [1, 1, 1, 1, 0, 1, 1, 0, 1],
             [0, 0, 0, 0, 1, 0, 0, 0, 0],
             [1, 1, 1, 1, 1, 0, 0, 1, 1],
             [0, 0, 0, 0, 0, 0, 1, 0, 0],
             [1, 1, 1, 1, 1, 0, 1, 0, 0,]]
        ), 
        "MissionA": np.array(
            [[0, 1, 1, 1, 1, 0, 1, 0, 1],
             [1, 0, 1, 1, 1, 0, 1, 0, 1],
             [1, 1, 0, 1, 1, 0, 1, 0, 1],
             [1, 1, 1, 0, 0, 0, 1, 0, 1],
             [1, 1, 1, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 1, 1, 1, 0, 0, 0, 1, 1],
             [0, 0, 0, 0, 0, 0, 1, 0, 0],
             [1, 1, 1, 1, 0, 0, 1, 0, 0,]]
        ),
        "MissionB": np.array(
            [[0, 1, 1, 1, 1, 0, 1, 0, 1],
             [1, 0, 1, 1, 1, 0, 1, 0, 1],
             [1, 1, 0, 1, 1, 0, 1, 0, 1],
             [1, 1, 1, 0, 1, 0, 0, 0, 1],
             [1, 1, 1, 1, 0, 1, 0, 0, 1],
             [0, 0, 0, 0, 1, 0, 0, 0, 0],
             [1, 1, 1, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [1, 1, 1, 1, 1, 0, 0, 0, 0,]]
        ),
    }

    # The above matrix corresponds to the documentation
    names = [
        'office_network_subnet',
        'admin_network_subnet',
        'public_access_zone_subnet',
        'contractor_network_subnet',
        'restricted_zone_a_subnet',
        'operational_zone_a_subnet',
        'restricted_zone_b_subnet',
        'operational_zone_b_subnet',
        'internet_subnet', 
    ]
    node_mapping = dict(enumerate(names))
    network = nx.from_numpy_array(adjacency_matrices[mission_phase])
    network = nx.relabel_nodes(network, node_mapping)
    return network

@pytest.fixture
def expected_comms_policy(network, blue_agent_short, cyborg):
    state = cyborg.get_attr("environment_controller").state
    agent_hostname = state.sessions[blue_agent_short][0].hostname
    agent_subnet = state.hostname_subnet_map[agent_hostname]

    nodelist = sorted(network.nodes)
    matrix = nx.to_numpy_array(network, nodelist=nodelist)
    return np.logical_not(matrix[nodelist.index(agent_subnet)])

def test_BlueEnterpriseWrapper_comms_policy_reset(reset_obs_short, blue_agent_short, expected_comms_policy, mission_phase):
    """Tests the ideal comms policy for the mission phase."""
    if mission_phase != 'Preplanning':
        return

    comms_block = reset_obs_short[COMMS_POLICY_SLICE]
    assert (comms_block == expected_comms_policy).all()

def test_BlueEnterpriseWrapper_comms_policy_step(cyborg, blue_agent_short, expected_comms_policy, mission_phase):
    step_options = {'Preplanning':1, 'MissionA': 2, 'MissionB':3}
    for i in range(step_options[mission_phase]):
        cyborg.step()
    observation = cyborg.get_observation(blue_agent_short)
    comms_block = observation[COMMS_POLICY_SLICE]

    assert (comms_block == expected_comms_policy).all()

def test_BlueEnterpriseWrapper_process_events_reset(reset_obs_short):
    '''Beginning of episode has no process alerts'''
    host_events_block = reset_obs_short[MALICIOUS_PROCESS_SLICE]
    assert (host_events_block == np.zeros(MAX_NUM_HOSTS)).all()

@pytest.fixture(params=range(MAX_NUM_HOSTS), ids=[f'Host{i}' for i in range(MAX_NUM_HOSTS)])
def hostname_index(request):
    return request.param

@pytest.fixture()
def hostname(cyborg, blue_agent_short, hostname_index):
    state = cyborg.get_attr("environment_controller").state
    agent_hostname = state.sessions[blue_agent_short][0].hostname
    agent_subnet_name = state.hostname_subnet_map[agent_hostname]
    subnet_hosts = [h for h,s in state.hostname_subnet_map.items() if s.value == agent_subnet_name.value]
    subnet_user_hosts = [h for h in subnet_hosts if 'user' in h]
    subnet_server_hosts = [h for h in subnet_hosts if 'user' in h]
    subnet_hosts = subnet_user_hosts + subnet_server_hosts

    return subnet_hosts[hostname_index] if hostname_index < len(subnet_hosts) else None

def test_BlueEnterpriseWrapper_process_events_step(cyborg, blue_agent_short, hostname, hostname_index):
    '''Here we check process creation on a host is detected. If the subnet has less than maximum number of hosts, there will be several hosts will value None. In this case the test automatically passes'''
    if hostname is None:
        return

    state = cyborg.get_attr("environment_controller").state
    host = state.hosts[hostname]
    processes = host.events.process_creation
    processes.append({'local_address': '0.0.0.0', 'local_port': 999})

    index = 0 if 'server_host' in hostname else MAX_SERVER_HOSTS
    index += int(hostname.rsplit('_', 1)[1])
    subvector = [int(i==index) for i in range(MAX_NUM_HOSTS)]

    observations, _, _, _, _ = cyborg.step(actions={blue_agent_short: Sleep()})
    process_observations = observations[blue_agent_short][MALICIOUS_PROCESS_SLICE]

    assert (process_observations == np.array(subvector)).all()

def test_BlueEnterpriseWrapper_connection_events_reset(reset_obs_short):
    subnet_events_block = reset_obs_short[NETWORK_CONNECTIONS_SLICE]
    assert (subnet_events_block == np.zeros(MAX_NUM_HOSTS)).all()

def test_BlueEnterpriseWrapper_connection_events_step(cyborg, blue_agent_short, hostname, hostname_index):
    if hostname is None:
        return

    state = cyborg.get_attr("environment_controller").state
    host = state.hosts[hostname]
    connections = host.events.network_connections

    event = NetworkConnection(local_address='0.0.0.0', remote_address='0.0.0.1', remote_port=999)
    connections.append(event)

    index = 0 if 'server_host' in hostname else MAX_SERVER_HOSTS
    index += int(hostname.rsplit('_', 1)[1])
    subvector = [int(i==index) for i in range(MAX_NUM_HOSTS)]

    observations, _, _, _, _ = cyborg.step(actions={blue_agent_short: Sleep()})
    connection_observations = observations[blue_agent_short][NETWORK_CONNECTIONS_SLICE]

    assert (connection_observations == np.array(subvector)).all()

def test_BlueEnterpriseWrapper_zone_reset(cyborg, reset_obs_short, blue_agent_short):
    state = cyborg.get_attr("environment_controller").state
    agent_hostname = state.sessions[blue_agent_short][0].hostname
    agent_subnet_name = state.hostname_subnet_map[agent_hostname]
    subnet_names = sorted([k.lower() for k in state.subnet_name_to_cidr])
    subvector = [int(s==agent_subnet_name) for s in subnet_names]

    subnet_events_block = reset_obs_short[AGENT_ZONE_SLICE]

    assert (subnet_events_block==np.array(subvector)).all()

@pytest.fixture
def step_obs_short(cyborg, step_results, blue_agent_short):
    cyborg.reset(blue_agent_short)
    results = cyborg.step(actions={blue_agent_short:Sleep()})
    return step_results[0][blue_agent_short]

def test_BlueEnterpriseWrapper_zone_step(step_obs_short, cyborg, blue_agent_short):
    state = cyborg.get_attr("environment_controller").state
    agent_hostname = state.sessions[blue_agent_short][0].hostname
    agent_subnet_name = state.hostname_subnet_map[agent_hostname]
    subnet_names = sorted([k.lower() for k in state.subnet_name_to_cidr])
    subvector = [int(s==agent_subnet_name) for s in subnet_names]

    subnet_events_block = step_obs_short[AGENT_ZONE_SLICE]
    assert (subnet_events_block==np.array(subvector)).all()

def test_BlueEnterpriseWrapper_message_reset(reset_obs, blue_agent):
    '''Check there are no messages sent during the reset phase.'''
    message_slice = LONG_MESSAGE_SLICE if blue_agent == HQ_AGENT else MESSAGE_SLICE
    message_block = reset_obs[message_slice]
    assert (message_block == np.zeros(NUM_MESSAGES * MESSAGE_LENGTH)).all()

def test_BlueEnterpriseWrapper_message_step(blue_agent, cyborg):
    first_sender = cyborg.get_attr("np_random").choice([agent for agent in cyborg.agents if agent!=blue_agent])
    second_sender = cyborg.get_attr("np_random").choice([agent for agent in cyborg.agents if agent not in (blue_agent, first_sender)])
    
    first_message = cyborg.get_message_space(first_sender).sample()
    second_message = cyborg.get_message_space(second_sender).sample()
    messages = {first_sender: first_message, second_sender: second_message}

    observations, _, _, _, _ = cyborg.step(messages=messages)
    observation = observations[blue_agent]
    message_slice = LONG_MESSAGE_SLICE if blue_agent == HQ_AGENT else MESSAGE_SLICE
    message_block = observation[message_slice]

    messages = []
    for agent in sorted(cyborg.agents):
        if agent == first_sender:
            messages.append(first_message)
        elif agent == second_sender:
            messages.append(second_message)
        elif agent != blue_agent:
            messages.append(EMPTY_MESSAGE)
    expected_message = np.concatenate(messages)

    assert (message_block == expected_message).all()
