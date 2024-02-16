# Discover Deception
`DiscoverDeception` probes a remote host to see if it is running any decoy services. This action has a few other actions as prerequisities to run successfully. This tutorial will go over them briefly, but for more information on them, check their individual tutorial pages. 

Here we will first find the known subnet, discover the hosts present on that subnet, choose two hosts and discover the services on each, then finally discover deception on both hosts.

## Red Agent Preamble
=== "Step 0: Initial Observation"

    First, we check Red's initial observations to find the subnet Red starts the scenario knowing.

    ```python title="red_discover_deception.py" linenums="1"
    from pprint import pprint
    from ipaddress import IPv4Network, IPv4Address

    from CybORG import CybORG
    from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
    from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
    from CybORG.Simulator.Actions import DiscoverRemoteSystems, AggressiveServiceDiscovery, Sleep, DiscoverDeception

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

    Here, the subnet is `10.0.96.0/24`.

=== "Step 1: DiscoverRemoteSystems"
    We then execute [DiscoverRemoteSystems](1_Discover_Remote_Systems.md) to discover the other hosts present on the subnet.
        
    ```python title="red_discover_deception.py" linenums="19"
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

    These are: `10.0.96.108`, `10.0.96.119`, `10.0.96.172`, `10.0.96.177`, `10.0.96.211`, `10.0.96.252`, `10.0.96.253`, `10.0.96.254`, and `10.0.96.73`.

=== "Step 2: ServiceDiscovery"

    Running [ServiceDiscovery](2_Service_Discovery.md) on a host is necessary for `DiscoverDeception` to work, as Red needs to know the services the host is running to ascertain if any of those services are decoys. 
    
    Here, we are using `AggressiveServiceDiscovery` as stealth is not important for this demonstration. We are also investigating both hosts `10.0.96.177` and `10.0.96.108`, to demonstrate the different results `DiscoverDeception` can produce.

    ```python title="red_discover_deception.py" linenums="23"
    action = AggressiveServiceDiscovery(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.177'))
    cyborg.step(agent=red_agent_name, action=action)
    ```

    ```python title="red_discover_deception.py" linenums="25"
    action = AggressiveServiceDiscovery(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.108'))
    cyborg.step(agent=red_agent_name, action=action)
    ```

    We are omitting the observation output here, as it is not necessary in this tutorial.
    
---

## Discover Deception - Decoy Found
This first execution of `DiscoverDeception` is on host `10.0.96.177`, which does have a decoy service. This action takes two ticks, so we must wait. 

```python title="red_discover_deception.py" linenums="27"
action = DiscoverDeception(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.177'))
cyborg.step(agent=red_agent_name, action=action)
results = cyborg.step(agent=red_agent_name, action=Sleep())
obs = results.observation
pprint(obs)
```
???+ quote "Code Output"
    ```
    {'action': DiscoverDeception contractor_network_subnet_user_host_0,
    'contractor_network_subnet_user_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.96.177')}],
                                            'Processes': [{'PID': 9877,
                                                            'Properties': ['decoy'],
                                                            'service_name': <ProcessName.MYSQLD: 9>,
                                                            'username': 'user'}]},
    'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                            'ip_address': IPv4Address('10.0.96.73')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```

The observation result includes a key `contractor_network_subnet_user_host_0`, whose value contains information about the host we just investigated: `10.0.96.177`. Under `Processes` within that information is the decoy process: 

```
'Processes': [{'PID': 9877,
    'Properties': ['decoy'],
    'service_name': <ProcessName.MYSQLD: 9>,
    'username': 'user'}]
```

Now Red knows not to attempt to exploit this service.
        
## Discover Deception - Decoy Not Found
This next execution of `DiscoverDeception` is on host `10.0.96.108`, which does NOT have a decoy service. 

```python title="red_discover_deception.py" linenums="32"
action = DiscoverDeception(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.108'))
cyborg.step(agent=red_agent_name, action=action)
results = cyborg.step(agent=red_agent_name, action=Sleep())
obs = results.observation
pprint(obs)
```
???+ quote "Code Output"
    ```
    {'action': DiscoverDeception contractor_network_subnet_user_host_5,
    'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                            'ip_address': IPv4Address('10.0.96.73')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```
    
Unlike the first execution on `10.0.96.177`, the observation result for `10.0.96.108` does not include an entry for this host. This is the result when no decoy services have been detected. 

It should be noted that the action's `success` key in the observation result has the value TRUE for `DiscoverDeception` regardless of whether a decoy has been found.
