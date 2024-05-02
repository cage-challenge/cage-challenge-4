from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import Monitor, Analyze, DiscoverNetworkServices, AggressiveServiceDiscovery, DiscoverDeception, ExploitRemoteService, PrivilegeEscalate, Impact
import numpy as np

MAX_STEPS = 200

def _check_processes(process_events: dict) -> int:
    '''
    Checks how many processes/connections are in the process events. Number will increase with AggresiveServiceDiscovery 
    
    param: process_events: dict - the event to check

    return: int - 0 if no indicator of compromise, otherwhise 1
    '''
    MAX_NORMAL_CONNECTIONS = 2 
    return 1 if len(process_events) > MAX_NORMAL_CONNECTIONS else 0
 
def _check_sessions(session_events: dict) -> int:
    '''
    Checks how many sessions are open in the session events.
    
    param: session_events: dict - the event to check
    
    return: int - 0 if no indicator of compromise, otherwhise 1
    '''
    MAX_NORMAL_SESSIONS = 1
    return 1 if len(session_events) > MAX_NORMAL_SESSIONS else 0

def _check_files(file_events: dict) -> int:
    '''
    Checks if a file is created in the event. Currently, these are the only possible values:
    - cmd.{extension} is a user-level compromise
    - escalate.{extension} is an admin-level compromise
    
    param: file_events: dict - the events to check

    return: int - 0 if no indicator of compromise, 1 if user compromise, 2 if admin compromise
    '''
    compromise_level = 0
    ioc_files_user = ['cmd.sh, cmd.exe']
    ioc_files_admin = ['escalate.sh, escalate.exe']
    for file in file_events:
        if file['Filename'] in ioc_files_admin:
            compromise_level = 3
            break
        if file['Filename'] in ioc_files_user:
            compromise_level = 2
    return compromise_level

def _calculate_compromise_level(obs: dict) -> int:
    '''
    Calculates the compromise level of the agent's network.
    The observation only contains the current state of the agent's network
    
    How to calculate the compromise level:
    
    param: obs: dict - the observation of the agent
    
    return: int - the compromise level of the agent's network
    '''
    compromise_level = 0

    if len(obs) > 2: # Only true if there are events 
        for key in obs.keys():
            if key == 'success' or key == 'action':
                continue
            else: 
                system_name = key
                for event in obs[system_name]: 
                    if event == 'Processes': # Monitor action returns Processes events
                        compromise_level = max(compromise_level, _check_processes(obs[system_name][event]))
                    elif event == 'Files': # Analyze action returns Files events
                        compromise_level = max(compromise_level, _check_files(obs[system_name][event]))
                    elif event == 'Sessions': # Check who has a current session open 
                        compromise_level = max(compromise_level, _check_sessions(obs[system_name][event]))
            if compromise_level == 3:
                break  # No need to check further if admin-level compromise is detected 
    return compromise_level
    
def _validate_connections(obs: dict) -> np.array:
    '''
    Validate the connections to the agent's network. Then, maps the source IP to the respective agent's network
    Returns a list 
    
    param: connections: dict - the connections to validate
    
    return: np.array - the 
    '''
    remote_connections = np.zeros(5)
    #TODO: Finish this function!
    #TODO: Get list of IPv4 networks per agent

    
    for key in obs.keys():
        if key == 'success' or key == 'action':
            continue
        else:
            system_name = key
            for event in obs[system_name]:
                if event == 'Processes':
                    for process in obs[system_name][event]:
                        remote_connections[0] = 1
                        return 0
    
    
    
def create_comm_message(agent_name: str, obs: dict, agent_messages: dict = {}) -> np.array:
    '''
    Creates the 1-byte message for each agent after running the Monitor action.
    Remember that Monitor action runs automatically at the end of each step.
    
    param: agent_name: str - the name of the agent (e.g. 'blue_agent_0')
    param: obs: dict - the observation of the agent
    
    return: np.array - the 1-byte message for the agent
    
    Message structure:
        - Bit 0 (Agent 0 status): Malicious action detected from agent 0 network (1) or not (0)
        - Bit 1 (Agent 1 status): Malicious action detected from agent 1 network (1) or not (0)
        - Bit 2 (Agent 2 status): Malicious action detected from agent 2 network (1) or not (0)
        - Bit 3 (Agent 3 status): Malicious action detected from agent 3 network (1) or not (0)
        - Bit 4 (Agent 4 status): Malicious action detected from agent 4 network (1) or not (0)
        - Bits 5-6 (Compromise level of current agent's network): 
            00 - No compromise
            01 - Netscan/Remote exploit detected
            10 - User-level compromise
            11 - Admin-level compromise
        - Bit 7 (Unset): Reserved for future use
        - Should we use the last bit to record previous observations of status?
    '''
    agent_id = int(agent_name.split('_')[-1])
    message = np.zeros(8)
    
    # Calculate compromise level for agent's network and set bits 
    compromise_level = _calculate_compromise_level(obs)
    message[5] = (compromise_level & 0b10) >> 1
    message[6] = compromise_level & 0b01
    
    # If compromise is detected, check connections from other networks
    if compromise_level:
        remote_connections = _validate_connections(obs)
        
        
    
    return message



steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=200)
cyborg = CybORG(scenario_generator=sg, seed=1000)
blue_agent_name = 'blue_agent_0'

reset = cyborg.reset(agent=blue_agent_name)
initial_obs = reset.observation
pprint(initial_obs)

action = Monitor(0, blue_agent_name)
results = cyborg.step(agent=blue_agent_name, action=action)

step = 1
base_obs = results.observation
new_obs = base_obs

while new_obs == base_obs and step < steps:
    results = cyborg.step(agent=blue_agent_name, action=action)
    message = create_comm_message(blue_agent_name, new_obs)
    step = step + 1
    new_obs = results.observation
    

# Create the communication message after obtaining the results from Monitor
print(f"Step count: {step}")
pprint(new_obs)
message = create_comm_message(blue_agent_name, new_obs)
print(f"Message: {message}")