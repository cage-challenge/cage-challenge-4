import pytest
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Shared.Enums import ProcessName, TernaryEnum, ProcessType
from CybORG.Simulator.Service import Service
from CybORG.Simulator.Process import Process
from CybORG.Simulator.Actions import DiscoverRemoteSystems, AggressiveServiceDiscovery, PrivilegeEscalate, Impact, ExploitRemoteService


# Global test variables
AGENT_NAME = 'red_agent_0'
S0_HOSTNAME = 'contractor_network_subnet_server_host_0'

def test_impact_run_with_priv(cyborg = None):
    """Test that the Impact action will run through and succeed when given the correct conditions and privileges.
    
    Conditions:
    - an OT Service is placed on server 0
    - the action history has the server correctly found and a root session added

    Privileges:
    - has a session on the host with root privileges
    
    """
    if cyborg == None:
        cyborg = create_sleep_cyborg()
    
    add_OT_service_to_server0(cyborg=cyborg)
    get_agent_with_shell(cyborg=cyborg)
    result = perform_impact_action(cyborg=cyborg)

    assert result.observation['success'] == TernaryEnum.TRUE

def test_impact_not_run_without_priv():
    """Test that the Impact action fails with only a user level shell."""

    cyborg = create_sleep_cyborg()
    
    add_OT_service_to_server0(cyborg=cyborg)
    get_agent_with_shell(cyborg=cyborg, priv_shell=False)
    result = perform_impact_action(cyborg=cyborg)

    assert result.observation['success'] == TernaryEnum.FALSE

def test_impact_causes_service_removal():
    """Test that a successful Impact action results in the OT service being deactivated."""
    cyborg = create_sleep_cyborg()
    test_impact_run_with_priv(cyborg)

    host = cyborg.environment_controller.state.hosts[S0_HOSTNAME]
    ot_process = ProcessName.OTSERVICE

    assert host.services[ot_process].active == False


def test_impact_fail_when_no_ot_service():
    """Test that the Impact action fails when there is no OT service on the host."""
    cyborg = create_sleep_cyborg()
    
    get_agent_with_shell(cyborg=cyborg)
    result = perform_impact_action(cyborg=cyborg)

    print(result.observation['action'])
    assert result.observation['success'] == TernaryEnum.FALSE


                ### Enabling functions ###

# Copy from conftest.py but could not get to run from this script
def create_sleep_cyborg(seed: int = 123, steps: int = 100):
    ent_sg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent,
        red_agent_class=SleepAgent,
        green_agent_class=SleepAgent,
        steps=steps
    )
    cyborg = CybORG(scenario_generator=ent_sg, seed=seed)
    cyborg.reset()
    return cyborg

def add_OT_service_to_server0(cyborg):
    #op_s0_hostname = 'operational_zone_b_subnet_server_host_0'
    host = cyborg.environment_controller.state.hosts[S0_HOSTNAME]
    
    ot_process = ProcessName.OTSERVICE
    pid = host.create_pid()
    process = Process(pid=pid, process_name=ot_process, process_type=ProcessType.UNKNOWN, username='user')
    host.processes.append(process)

    service = Service(process=pid)
    host.add_service(service_name=ot_process, service=service)

    assert host.services[ot_process]

def _get_action_list(cyborg, priv_shell: bool):
    subnet = cyborg.environment_controller.state.subnet_name_to_cidr['contractor_network_subnet']
    ip_address = cyborg.environment_controller.state.hostname_ip_map[S0_HOSTNAME]

    if priv_shell:
        action_list = [
            DiscoverRemoteSystems(subnet=subnet, session=0, agent=AGENT_NAME), 
            AggressiveServiceDiscovery(ip_address=ip_address, session=0, agent=AGENT_NAME), 
            ExploitRemoteService(ip_address=ip_address, session=0, agent=AGENT_NAME),
            PrivilegeEscalate(hostname=S0_HOSTNAME, session=0, agent=AGENT_NAME)
        ]
    else:
        action_list = [
            DiscoverRemoteSystems(subnet=subnet, session=0, agent=AGENT_NAME), 
            AggressiveServiceDiscovery(ip_address=ip_address, session=0, agent=AGENT_NAME), 
            ExploitRemoteService(ip_address=ip_address, session=0, agent=AGENT_NAME)
        ]

    for action in action_list:
        action.duration = 1
    
    return action_list
    

def get_agent_with_shell(cyborg, priv_shell: bool = True):
    
    action_list = _get_action_list(cyborg, priv_shell)
    
    action_num = 0
    session_on_s0_host = False

    while len(action_list) > action_num :
        result = cyborg.step(agent=AGENT_NAME, action=action_list[action_num])
        success = result.observation['success']

        if success == TernaryEnum.FALSE:
            print(result.error, result.error_msg)
            assert False
        elif success == TernaryEnum.TRUE or success == TernaryEnum.UNKNOWN:
            action_num = action_num + 1

    if priv_shell:
        assert isinstance(result.observation['action'], PrivilegeEscalate)
    else:
        assert isinstance(result.observation['action'], ExploitRemoteService)
    assert result.observation['success'] == TernaryEnum.TRUE

def perform_impact_action(cyborg):
    action = Impact(hostname='contractor_network_subnet_server_host_0', session=0, agent=AGENT_NAME)
    action.duration = 1
    return cyborg.step(agent=AGENT_NAME, action=action)
