# Degrade Services
`DegradeServices` attempts to degrade services used by green in the mission. This is achieved by lowering the reliability of each service on the host, making a green agent's local work less likely to succeed. The more a service is degraded, the less likely green is to succeed in performing their local work for the mission.

This action has a few other actions as prerequisities to run successfully. This tutorial will go over them briefly, but for more information on them, check their individual tutorial pages. 

## Red Agent Preamble
Here we will first find the known subnet, discover the hosts present on that subnet, choose a host and discover its services, exploit a remote service on that host to gain a user shell on it, privilege escalate that shell to root, then finally degrade services.

=== "Step 0: Initial Observation"

    First, we check Red's initial observations to find the subnet Red starts the scenario knowing.

    ```python title="red_degrade_services.py" linenums="1"
    from pprint import pprint
    from ipaddress import IPv4Network, IPv4Address

    from CybORG import CybORG
    from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
    from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
    from CybORG.Simulator.Actions import DiscoverRemoteSystems, AggressiveServiceDiscovery, Sleep, PrivilegeEscalate, DegradeServices
    from CybORG.Simulator.Actions.ScenarioActions.EnterpriseActions import ExploitRemoteService_cc4

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

=== "Step 1: Discover Remote Systems"
    We then execute [DiscoverRemoteSystems](1_Discover_Remote_Systems.md) to discover the other hosts present on the subnet.

    ```python title="red_degrade_services.py" linenums="20"
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

=== "Step 2: Service Discovery"

    We then execute [ServiceDiscovery](2_Service_Discovery.md) on a host for `ExploitRemoteService_cc4` to work. Here, we are using `AggressiveServiceDiscovery` as stealth is not important for this demonstration. We are investigating the host `10.0.96.108`, but this is an abitrary choice.

    ```python title="red_degrade_services.py" linenums="24"
    action = AggressiveServiceDiscovery(session=0, agent=red_agent_name, ip_address=IPv4Address('10.0.96.108'))
    results = cyborg.step(agent=red_agent_name, action=action)
    obs = results.observation
    pprint(obs)
    ```
    ???+ quote "Code Output"
        ```
        {'10.0.96.108': {'Interface': [{'ip_address': IPv4Address('10.0.96.108')}],
                        'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                                                        'local_port': 22}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                                                        'local_port': 80}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                                                        'local_port': 25}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                                                        'local_port': 3390}]}]},
        'action': AggressiveServiceDiscovery 10.0.96.108,
        'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                                'ip_address': IPv4Address('10.0.96.73')}],
                                                'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```

    The services are visible in the resulting observations within `10.0.96.108`, `Processes`. In this case, these are as follows:
    ```
    'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                            'local_port': 22}]},
        {'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                            'local_port': 80}]},
        {'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                            'local_port': 25}]},
        {'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                            'local_port': 3390}]}],
    ```
    Keep these in mind for later...

=== "Step 3: Exploit Service"

    Now, we run [ExploitRemoteService_cc4](4_Exploit_Remote_Service.md) on `10.0.96.108` to gain a user shell on it.

    ```python title="red_degrade_services.py" linenums="28"
    action = ExploitRemoteService_cc4(ip_address=IPv4Address('10.0.96.108'), session=0, agent=red_agent_name)
    cyborg.step(agent=red_agent_name, action=action)
    cyborg.step(agent=red_agent_name, action=Sleep())
    results = cyborg.step(agent=red_agent_name, action=Sleep())
    obs = results.observation
    pprint(obs)
    ```
    ???+ quote "Code Output"
        ```
        {'10.0.96.108': {'Interface': [{'ip_address': IPv4Address('10.0.96.108')}],
                        'Processes': [{'Connections': [{'Status': <ProcessState.OPEN: 2>,
                                                        'local_address': IPv4Address('10.0.96.108'),
                                                        'local_port': 22}],
                                        'process_type': <ProcessType.SSH: 2>},
                                    {'Connections': [{'local_address': IPv4Address('10.0.96.108'),
                                                        'local_port': 22,
                                                        'remote_address': IPv4Address('10.0.96.73'),
                                                        'remote_port': 54893}],
                                        'process_type': <ProcessType.SSH: 2>}],
                        'Sessions': [{'Type': <SessionType.SSH: 2>,
                                    'agent': 'red_agent_0',
                                    'session_id': 1,
                                    'username': 'user'}],
                        'System info': {'Hostname': 'contractor_network_subnet_user_host_5',
                                        'OSType': <OperatingSystemType.LINUX: 3>}},
        '10.0.96.73': {'Interface': [{'ip_address': IPv4Address('10.0.96.73')}],
                        'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.96.73'),
                                                        'local_port': 54893,
                                                        'remote_address': IPv4Address('10.0.96.108'),
                                                        'remote_port': 22}]}]},
        'action': ExploitRemoteService_cc4 10.0.96.108,
        'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                                'ip_address': IPv4Address('10.0.96.73')}],
                                                'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
        'contractor_network_subnet_user_host_5': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                                'ip_address': IPv4Address('10.0.96.108')}],
                                                'Sessions': [{'Type': <SessionType.SSH: 2>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 1,
                                                                'username': 'user'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_5'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```

    The important takeaway from the results observation is `10.0.96.108`'s hostname: `contractor_network_subnet_user_host_5`.

=== "Step 4: Privilege Escalate Shell"

    With the user shell acquired, we execute [PrivilegeEscalate](5_Privilege_Escalate.md) on `contractor_network_subnet_user_host_5` to escalate the shell we have on it to root privileges.

    ```python title="red_degrade_services.py" linenums="34"
    action = PrivilegeEscalate(hostname='contractor_network_subnet_user_host_5', session=0, agent=red_agent_name)
    cyborg.step(agent=red_agent_name, action=action)
    ```

    ???+ quote "Code Output"
        ```
        {'action': PrivilegeEscalate contractor_network_subnet_user_host_5,
        'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                                'ip_address': IPv4Address('10.0.96.73')}],
                                                'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
        'contractor_network_subnet_user_host_5': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                                'ip_address': IPv4Address('10.0.96.108')}],
                                                'Sessions': [{'Type': <SessionType.RED_REVERSE_SHELL: 11>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 1,
                                                                'username': 'root'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_5'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```
---

## Degrade Services 

Finally, we can run `DegradeServices` on `contractor_network_subnet_user_host_5`.

```python title="red_degrade_services.py" linenums="36"
action = DegradeServices(hostname='contractor_network_subnet_user_host_5', session=0, agent=red_agent_name)
results = cyborg.step(agent=red_agent_name, action=action)
obs = results.observation
pprint(obs)
```
??? quote "Code Output"
    ```
    {'action': DegradeServices contractor_network_subnet_user_host_5,
    'contractor_network_subnet_user_host_4': {
        'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                        'ip_address': IPv4Address('10.0.96.73')}],
        'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                        'agent': 'red_agent_0',
                        'session_id': 0,
                        'username': 'ubuntu'}],
        'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
    'contractor_network_subnet_user_host_5': {
        'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                        'ip_address': IPv4Address('10.0.96.108')}],
        'Processes': [{'Connections': [{'Transport Protocol': <TransportProtocol.UNKNOWN: 1>,
                                        'local_address': IPv4Address('0.0.0.0'),
                                        'local_port': 22}],
                        'Known Path': <Path.UNKNOWN: 1>,
                        'Known Process': <ProcessName.SSHD: 7>,
                        'PID': 3761,
                        'Path': '/ usr / '
                                'sbin',
                        'process_name': <ProcessName.SSHD: 7>,
                        'process_type': <ProcessType.SSH: 2>,
                        'username': 'user'},
                        {'Connections': [{'Transport Protocol': <TransportProtocol.UNKNOWN: 1>,
                                        'local_address': IPv4Address('0.0.0.0'),
                                        'local_port': 80}],
                        'Known Path': <Path.UNKNOWN: 1>,
                        'Known Process': <ProcessName.APACHE2: 13>,
                        'PID': 5783,
                        'Path': '/ usr / '
                                'sbin',
                        'process_name': <ProcessName.APACHE2: 13>,
                        'process_type': <ProcessType.WEBSERVER: 7>,
                        'username': 'user'},
                        {'Connections': [{'Transport Protocol': <TransportProtocol.UNKNOWN: 1>,
                                        'local_address': IPv4Address('0.0.0.0'),
                                        'local_port': 25}],
                        'Known Path': <Path.UNKNOWN: 1>,
                        'Known Process': <ProcessName.SMTP: 11>,
                        'PID': 6815,
                        'Path': '/ usr / '
                                'sbin',
                        'Process Version': <ProcessVersion.HARAKA_2_8_9: 8>,
                        'process_name': <ProcessName.SMTP: 11>,
                        'process_type': <ProcessType.SMTP: 5>,
                        'username': 'user'},
                        {'Connections': [{'Transport Protocol': <TransportProtocol.UNKNOWN: 1>,
                                        'local_address': IPv4Address('0.0.0.0'),
                                        'local_port': 3390}],
                        'Known Path': <Path.UNKNOWN: 1>,
                        'Known Process': <ProcessName.MYSQLD: 9>,
                        'PID': 8372,
                        'Path': '/ usr / '
                                'sbin',
                        'process_name': <ProcessName.MYSQLD: 9>,
                        'process_type': <ProcessType.MYSQL: 12>,
                        'username': 'user'}],
        'Sessions': [{'Type': <SessionType.RED_REVERSE_SHELL: 11>,
                        'agent': 'red_agent_0',
                        'session_id': 1,
                        'username': 'root'}],
        'System info': {'Hostname': 'contractor_network_subnet_user_host_5'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```
This output is quite long, but in summary it tells us three things:

- The action `DegradeServices` ran.
- The action was executed successfully.
- All the processes listed on the host that the action was run on were degraded.

While the observation space output does not directly tell red (or blue) how much each service has been degraded by, the rewards received when green fails their [`GreenLocalWork`](../../../reference/actions/green_actions/local_work.md) action should be taken as the indication of the 'health' of the host and how much the operation is being affected by red.
