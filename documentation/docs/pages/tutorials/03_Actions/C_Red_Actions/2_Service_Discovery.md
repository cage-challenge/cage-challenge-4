# Service Discovery
`Service Discovery` outputs all processes (which have services) on a known host.
This action is a prerequisite for getting a shell on the host, as you must know about the services that exist before exploiting one of those services.

## Identify the Host IP
In order to discover services on a host, we must first find that host. We will be investigating the host Red starts with knowledge of, so there is no need to conduct a [DiscoverRemoteSystems](1_Discover_Remote_Systems.md) action. We just need to look at Red's initial observations.

```python title="red_service_discovery.py" linenums="1"
from pprint import pprint
from ipaddress import IPv4Network, IPv4Address

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import AggressiveServiceDiscovery, StealthServiceDiscovery, Sleep

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
??? quote "Code Output"
    ```
    {'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
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

Looking in `contractor_network_subnet_user_host_4`, the dictionary containing information about the Red's first known host, we can see its IP address, under `Interface` and `ip_address`: `IPv4Address('10.0.96.73')`. This is the host ip we will be investigating.

## Aggressive VS Stealth Versions

There are two kinds of service discovery: Aggressive and Stealth. They both find the services present on the host, but Aggressive is faster and more likely to alert Blue, whereas Stealth is slower but less likely to alert Blue.

Some type of service discovery must always be run on a host before attempting any other actions, as it enables them (e.g. exploits, discover deceptions).

As shown in the results, the same services are detected with both types of service discovery.

=== "Aggressive Service Discovery"

    Here, we run the `AggressiveServiceDiscovery` action on the target host.

    ```python title="red_service_discovery.py" linenums="23"
    action = AggressiveServiceDiscovery(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.73'))
    results = cyborg.step(agent=red_agent_name, action=action)
    obs = results.observation
    pprint(obs)
    ```
    ???+ quote "Code Output"
        ```
        {'10.0.96.73': {'Interface': [{'ip_address': IPv4Address('10.0.96.73')}],
                        'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                                                        'local_port': 22}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                                                        'local_port': 25}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                                                        'local_port': 80}]}]},
        'action': AggressiveServiceDiscovery 10.0.96.73,
        'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                                'ip_address': IPv4Address('10.0.96.73')}],
                                                'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```

    The services are visible in the resulting observations within `10.0.96.73`, `Processes`, along with brief information about each, including their local address and port. In this case, these are as follows:
    ```
    [{'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                        'local_port': 22}]},
    {'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                        'local_port': 25}]},
    {'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                        'local_port': 80}]}]
    ```

=== "Stealth Service Discovery"

    The Stealth version is carried out in exactly the same way as Aggressive, but with more time to wait for a response.

    ```python title="red_service_discovery.py" linenums="27"
    action = StealthServiceDiscovery(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.73'))
    cyborg.step(agent=red_agent_name, action=action)
    cyborg.step(agent=red_agent_name, action=Sleep())
    cyborg.step(agent=red_agent_name, action=Sleep())
    cyborg.step(agent=red_agent_name, action=Sleep())
    results = cyborg.step(agent=red_agent_name, action=Sleep())
    obs = results.observation
    pprint(obs)
    ```
    ???+ quote "Code Output"
        ```
        {'10.0.96.73': {'Interface': [{'ip_address': IPv4Address('10.0.96.73')}],
                        'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                                                        'local_port': 22}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                                                        'local_port': 25}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                                                        'local_port': 80}]}]},
        'action': StealthServiceDiscovery 10.0.96.73,
        'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                                'ip_address': IPv4Address('10.0.96.73')}],
                                                'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```

