# Monitor 

` Monitor` collects events on hosts and informs the Blue Agent. Events are limited to Network Connection events and Process Creation events.

???+ tip
    The Monitor action runs _automatically_ at the end of each step and if a Blue Agent calls it, it will have no additional effect. 

## Understanding Blue's Network
In CC4, the scenario is too vast for one blue agent to monitor everything happening and be able to respond.
Therefore the scenario is broken down into multiple networks that are connected to eachother; each with a blue agent.

In this example we will look at what `blue_agent_0` has visibility over and can act on.

```python title="blue_monitor_with_red.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import Monitor

sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=200)
cyborg = CybORG(scenario_generator=sg, seed=1000)
blue_agent_name = 'blue_agent_0'

reset = cyborg.reset(agent=blue_agent_name)
initial_obs = reset.observation

pprint(initial_obs)
```

??? quote "Code Output"
    ```
    {
        'restricted_zone_a_subnet_router': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.70')}],
            'Processes': [{'PID': 7,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 7,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 1,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_router',
                            'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                        {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_server_host_0': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.254')}],
            'Processes': [{'PID': 8263,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 8263,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 11,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_server_host_0',
                            'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_0': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.217')}],
            'Processes': [{'PID': 5243,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 5243,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 2,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_0',
                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_1': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.210')}],
            'Processes': [{'PID': 9300,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 9300,
                            'Type': <SessionType.VELOCIRAPTOR_SERVER: 8>,
                            'agent': 'blue_agent_0',
                            'session_id': 0,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_1',
                            'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_2': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.249')}],
            'Processes': [{'PID': 7061,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 7061,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 3,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_2',
                            'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_3': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.2')}],
            'Processes': [{'PID': 5707,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 5707,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 4,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_3',
                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_4': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.139')}],
            'Processes': [{'PID': 5956,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 5956,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 5,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_4',
                            'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_5': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.220')}],
            'Processes': [{'PID': 9148,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 9148,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 6,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_5',
                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_6': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.150')}],
            'Processes': [{'PID': 9879,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 9879,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 7,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_6',
                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_7': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.218')}],
            'Processes': [{'PID': 6681,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 6681,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 8,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_7',
                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_8': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.137')}],
            'Processes': [{'PID': 3109,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 3109,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 9,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_8',
                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'restricted_zone_a_subnet_user_host_9': {
            'Interface': [{'Subnet': IPv4Network('10.0.114.0/24'),
                            'interface_name': 'eth0',
                            'ip_address': IPv4Address('10.0.114.165')}],
            'Processes': [{'PID': 3557,
                            'username': 'ubuntu'}],
            'Sessions': [{'PID': 3557,
                            'Type': <SessionType.UNKNOWN: 1>,
                            'agent': 'blue_agent_0',
                            'session_id': 10,
                            'timeout': 0,
                            'username': 'ubuntu'}],
            'System info': {'Architecture': <Architecture.x64: 2>,
                            'Hostname': 'restricted_zone_a_subnet_user_host_9',
                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                            'OSType': <OperatingSystemType.LINUX: 3>,
                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                            'position': array([0., 0.])},
            'User Info': [{'Groups': [{'GID': 0}],
                            'username': 'root'},
                            {'Groups': [{'GID': 1}],
                            'username': 'user'}]},
        'success': <TernaryEnum.UNKNOWN: 2>
    }
    ```
In `blue_agent_0`'s initial observation space (before any steps are taken), you can see all the hosts that it is responsible for.
As you can see, the observation space is quite large to accommodate for all the hosts and their details.

The output shows that `'Subnet': IPv4Network('10.0.114.0/24'`, the network that `blue_agent_0` is responsible for, consists of 12 hosts in total. 
That is 10 user hosts (0-9), 1 server host, and a router. In this scenario, routers are seen as connective devices that provide a firewall to the network and can therefore not be taken control of by red. You can also tell by the naming convention of the hosts that this network is called 'Restricted Zone A'.


## Monitoring the Subnet

Here we execute the `Monitor` action in the first step, and collect events on the subnet.

Only events that have been raised on the current step will be visible to the blue agent. Past records of observations are not maintained.

```python title="blue_monitor_with_red.py" linenums="20"
action = Monitor(0, blue_agent_name)
results = cyborg.step(agent=blue_agent_name, action=action)

step = 1
base_obs = results.observation          

print(f"Step count: {step}")
pprint(base_obs)
```

???+ quote "Code Output"
    ```
    Step count: 1
    {'action': Monitor, 'success': <TernaryEnum.TRUE: 1>}
    ```

The output shows that the action ran successfully, however there were no events to collect.


## When Red makes a move ...
In this example, steps are taken until the previous agent observation is different from the current one - indicating that an event has been collected.

Due to green agents being sleep agents, we can assume red has caused the alert.

The printed `Monitor` output returns the step where the red agent has broken out of the contractor network and has compromised a host on the blue agent's network.

```python title="blue_monitor_with_red.py" linenums="28"
new_obs = base_obs

while new_obs == base_obs and step < steps:
    results = cyborg.step(agent=blue_agent_name, action=action)
    step = step + 1
    new_obs = results.observation

print(f"Step count: {step}")
pprint(new_obs)

```
??? quote "Code Output"
    ```
    Step count: 127
    {'action': Monitor,
    'restricted_zone_a_subnet_router': {'Interface': [{'ip_address': IPv4Address('10.0.114.254')}],
                    'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                    'remote_address': IPv4Address('10.0.96.73'),
                                    'remote_port': 3390}]}],
                    'System info': {'Architecture': <Architecture.x64: 2>,
                                    'Hostname': 'restricted_zone_a_subnet_router',
                                    'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                                    'OSType': <OperatingSystemType.LINUX: 3>,
                                    'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                                    'position': array([0., 0.])}},
    'restricted_zone_a_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.114.254')}],
                    'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                    'remote_address': IPv4Address('10.0.96.73'),
                                    'remote_port': 3390}]},
                                {'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                    'local_port': 3390,
                                    'remote_address': IPv4Address('10.0.96.73'),
                                    'remote_port': 49190}]},
                                    {'PID': 8264}],
                    'System info': {'Architecture': <Architecture.x64: 2>,
                                    'Hostname': 'restricted_zone_a_subnet_server_host_0',
                                    'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                                    'OSType': <OperatingSystemType.LINUX: 3>,
                                    'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                                    'position': array([0., 0.])}},
    'success': <TernaryEnum.TRUE: 1>}
    ```
The output tells us that at step 127, there were network connection events at both 'restricted_zone_a_subnet_router' and 'restricted_zone_a_subnet_server_host_0', as well as a process creation event on 'restricted_zone_a_subnet_server_host_0'.

???+ tip "Hint"
    This output indicates that red has managed to get a user shell on host 'restricted_zone_a_subnet_server_host_0'.

## Green False Positives

While red agents are performing actions that may alert blue agents to their presence, green agents are also just trying to do their jobs.

Green actions, though not malicious, have the chance to create misleading events for blue agents. These false positives are going to be explored in this example.

To isolate the events caused by the Green Agent, the Red Agent is set to 'SleepAgent' and the `Monitor` function is executed, iterating through steps until there is an observation space change.

```python title="blue_monitor_with_green.py" linenums="1"
from pprint import pprint
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import Monitor

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()

blue_agent_name = 'blue_agent_0'
blue_action_space = cyborg.get_action_space(blue_agent_name)

action = Monitor(0, blue_agent_name)
results = cyborg.step(agent=blue_agent_name, action=action)

step = 1
base_obs = results.observation
new_obs = base_obs

while new_obs == base_obs and step < steps:
    results = cyborg.step(agent=blue_agent_name, action=action)
    step = step + 1
    new_obs = results.observation

print(f"Step count: {step}")
pprint(new_obs)

```
???+ quote "Code Output"
    ```
    Step count: 51
    {'action': Monitor,
    'restricted_zone_a_subnet_user_host_6': {'Interface': [{'ip_address': IPv4Address('10.0.114.150')}],
                    'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.114.150'),
                                    'local_port': 56672}]}],
                    'System info': {'Architecture': <Architecture.x64: 2>,
                                    'Hostname': 'restricted_zone_a_subnet_user_host_6',
                                    'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                                    'OSType': <OperatingSystemType.LINUX: 3>,
                                    'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                                    'position': array([0., 0.])}},
    'success': <TernaryEnum.TRUE: 1>}
    ```

The action has executed successfully and found an event at step 51 on 'restricted_zone_a_subnet_user_host_6' that is caused by a green agent's action. 

