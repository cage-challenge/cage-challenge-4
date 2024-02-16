# Discover Remote Systems
`DiscoverRemoteSystems` outputs, in the red agent's observation space, the IP addresses of all other hosts in a subnet. 

## Identify the Subnet
To perform this action, we must first find a known subnet to investigate. We do this here by looking at Red's initial observations.

```python title="red_discover_remote_systems.py" linenums="1"
from pprint import pprint
from ipaddress import IPv4Network

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import DiscoverRemoteSystems

sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=200)
cyborg = CybORG(scenario_generator=sg, seed=1000)
red_agent_name = 'red_agent_0'

reset = cyborg.reset(agent=red_agent_name)
initial_obs = reset.observation

pprint(initial_obs)
```
???+ quote "Code Output"
    ```
    {'contractor_network_subnet_user_host_4': {
        'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                        'interface_name': 'eth0',
                        'ip_address': IPv4Address('10.0.96.73')}],
        'Processes': [{'PID': 5753,
                        'username': 'ubuntu'}],
        'Sessions': [{'PID': 5753,
                        'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                        'agent': 'red_agent_0',
                        'session_id': 0,
                        'timeout': 0,
                        'username': 'ubuntu'}],
        'System info': {'Architecture': <Architecture.x64: 2>,
                        'Hostname': 'contractor_network_subnet_user_host_4',
                        'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                        'OSType': <OperatingSystemType.LINUX: 3>,
                        'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                        'position': array([0., 0.])},
        'User Info': [{'Groups': [{'GID': 0}],
                        'username': 'root'},
                        {'Groups': [{'GID': 1}],
                        'username': 'user'}]},
    'success': <TernaryEnum.UNKNOWN: 2>}
    ```

The observation space is a dictionary that contains with information about the hosts Red is currently aware of. In this situation, the only host that Red is aware of is `contractor_network_subnet_user_host_4`. 

You can tell from the `Sessions` dictionary that this red is not only aware of this host, but also has a user shell on the host. However, having a shell on the host is not necessary for the Discover Remote Systems action to be valid. 

In the `Interface` and `Subnet` dictionaries is written the subnet that the host exists in: `IPv4Network('10.0.96.0/24')`. This is the subnet we will be investigating.

## Discover Hosts on the Subnet
To discover the rest of the hosts on this host's subnet, `IPv4Network('10.0.96.0/24')`, we must run the `DiscoverRemoteSystems` action on the subnet, as shown below.

```python title="red_discover_remote_systems.py" linenums="20"
action = DiscoverRemoteSystems(subnet=IPv4Network('10.0.96.0/24'), session=0, agent=red_agent_name)
results = cyborg.step(agent=red_agent_name, action=action)
obs = results.observation

pprint(obs)
```
???+ quote "Code Output"
    ```
    {'10.0.96.108': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.108')}]},
    '10.0.96.119': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.119')}]},
    '10.0.96.172': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.172')}]},
    '10.0.96.177': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.177')}]},
    '10.0.96.211': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.211')}]},
    '10.0.96.252': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.252')}]},
    '10.0.96.253': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.253')}]},
    '10.0.96.254': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                    'ip_address': IPv4Address('10.0.96.254')}]},
    '10.0.96.73': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                'ip_address': IPv4Address('10.0.96.73')}]},
    'action': DiscoverRemoteSystems 10.0.96.0/24,
    'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                            'ip_address': IPv4Address('10.0.96.73')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```

The outputted observation contains the IP addresses of all hosts on the subnet.

In this case, there are 9 hosts on subnet `10.0.96.0/24`: 

```10.0.96.108, 10.0.96.119, 10.0.96.172, 10.0.96.177, 10.0.96.211, 10.0.96.252, 10.0.96.253, 10.0.96.254, 10.0.96.73```.