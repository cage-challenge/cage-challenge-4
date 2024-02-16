# DeployDecoy

`DeployDecoy` creates a decoy service on the specified host, reminiscent of a honeypot. 

This results in red wasting their time on a service that they cannot use, and gives blue more alerts on what is happening in the environment.

## Red Preamble
For this tutorial, red has successfully gained a root shell on `contractor_network_subnet_server_host_0`, and is starting to branch out into other networks.

This is difficult to orchestrate, so a full function has been provided to get you to this point, with environment seed 100. 

??? info "Helper Function"
    ```python
    red_agent_name = ['red_agent_0', 'red_agent_1']
    blue_agent_name = 'blue_agent_0'


    def cyborg_with_root_shell_on_cns0() -> CybORG:
        """Get red_agent_0 a root shell on 'contractor_network_subnet_server_host_0' 
        
        Observation gained from last PrivilegeEscalate:
            'public_access_zone_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.176.254')}]},
            'restricted_zone_a_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.7.254')}]},
            'restricted_zone_b_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.100.254')}]},

        Returns
        -------
        cyborg : CybORG
            a cyborg environment with a root shell on cns0
        """
        ent_sg = EnterpriseScenarioGenerator(
                blue_agent_class=SleepAgent,
                red_agent_class=SleepAgent,
                green_agent_class=SleepAgent,
                steps=100
            )
        cyborg = CybORG(scenario_generator=ent_sg, seed=100)
        cyborg.reset()
        env = cyborg.environment_controller

        s0_hostname = 'contractor_network_subnet_server_host_0'
        s0_ip_addr = env.state.hostname_ip_map[s0_hostname]
        cn_subnet_ip = env.subnet_cidr_map[env.state.hostname_subnet_map[s0_hostname]]

        action = DiscoverRemoteSystems(subnet=cn_subnet_ip, session=0, agent=red_agent_name[0])
        results = cyborg.step(agent=red_agent_name[0], action=action)
        obs = results.observation
        print(obs['action'], obs['success'])

        action = AggressiveServiceDiscovery(session=0, agent=red_agent_name[0], ip_address=s0_ip_addr)
        results = cyborg.step(agent=red_agent_name[0], action=action)
        obs = results.observation
        print(obs['action'], obs['success'])

        action = ExploitRemoteService(ip_address=s0_ip_addr, session=0, agent=red_agent_name[0])
        action.duration = 1
        results = cyborg.step(agent=red_agent_name[0], action=Sleep())
        obs = results.observation
        print(obs['action'], obs['success'])

        action = PrivilegeEscalate(hostname=s0_hostname, session=0, agent=red_agent_name[0])
        results = cyborg.step(agent=red_agent_name[0], action=action)
        obs = results.observation
        print(obs['action'], obs['success'])

        return cyborg
    ```

This function then needs to be called, and some host knowledge defined. Additional processes and services have been removed from the target host in this example.

??? info "Tutorial set-up code"
    ```python
    cyborg = cyborg_with_root_shell_on_cns0()

    target_subnet = 'restricted_zone_a_subnet'
    target_host = target_subnet + '_server_host_0'
    target_ip = cyborg.environment_controller.state.hostname_ip_map[target_host]
    shell_ip = cyborg.environment_controller.state.hostname_ip_map['contractor_network_subnet_server_host_3']

    cyborg.environment_controller.state.hosts[target_host].processes = []
    cyborg.environment_controller.state.hosts[target_host].services = {}
    ```

However, feel free to follow along without implementing the code. The summary of the red actions performed is:

```
DiscoverRemoteSystems 10.0.157.0/24 TRUE
AggressiveServiceDiscovery 10.0.157.254 TRUE
ExploitRemoteService 10.0.157.254 TRUE
PrivilegeEscalate contractor_network_subnet_server_host_0 TRUE
```

???+ warning
    For demonstration purposes, the action durations in these tutorial scripts are sometimes set to 1 in order to show the immediate results.

    **This is _NOT_ permitted in challenge submissions!**

## Deploying a Decoy
The DeployDecoy action for blue is quite simple. Specify the agent performing the action (`blue_agent_name = 'blue_agent_0'`), the name of the host to have the decoy on it, and the agent session.

```python
action = DeployDecoy(session=0, agent=blue_agent_name, hostname=target_host)
action.duration = 1
obs, _, _, _ = cyborg.parallel_step(actions={blue_agent_name: action})

print("DeployDecoy:")
print("Blue:")
pprint(obs[blue_agent_name])
print("\n")
```

This results in the following output that shows the new process, linked to the new service, on the host. The action and success is also displayed as standard.

???+ quote "Code Output"
    ```
    DeployDecoy:
    Blue:
    {'action': DeployDecoy restricted_zone_a_subnet_server_host_0,
    'restricted_zone_a_subnet_server_host_0': {'Processes': [{'PID': 4,
                                                            'PPID': 1,
                                                            'service_name': 'haraka',
                                                            'username': 'ubuntu'}]},
    'success': <TernaryEnum.TRUE: 1>}
    ```

## Red Discovering the Service
It is then only a matter of time before red attempts to discover the services running on the host.

```python
red_action = StealthServiceDiscovery(session=0, agent=red_agent_name[0], ip_address=target_ip)
red_action.duration = 1
red_action.detection_rate = 0
obs, _, _, _ = cyborg.parallel_step(actions={red_agent_name[0]: red_action})

print("StealthServiceDiscovery:")
print("Red:")
pprint(obs[red_agent_name[0]])
print("\n")
print("Blue:")
pprint(obs[blue_agent_name])
print("\n")
```

The `detection_rate` of the red action is this example has been affectively 'turned off' so that you only see the detections resulting from the decoy service.

=== "Red Observation"
    In red's observation you can see a number of things:

    - the action - StealthServiceDiscovery
    - the action's success - which is successful
    - the services that red has discovered - a process with local port 25
    - the two shells the red agent currently has:
        1. contractor_network_subnet_server_host_0
        2. contractor_network_subnet_server_host_3

    ??? quote "Code Output"
        ```
        Red:
        {'10.0.7.254': {'Interface': [{'ip_address': IPv4Address('10.0.7.254')}],
                        'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.7.254'),
                                                        'local_port': 25}]}]},
        'action': StealthServiceDiscovery 10.0.7.254,
        'contractor_network_subnet_server_host_0': {'Interface': [{'Subnet': IPv4Network('10.0.157.0/24'),
                                                                    'ip_address': IPv4Address('10.0.157.254')}],
                                                    'Sessions': [{'Type': <SessionType.RED_REVERSE_SHELL: 11>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 1,
                                                                'username': 'root'}],
                                                    'System info': {'Hostname': 'contractor_network_subnet_server_host_0'}},
        'contractor_network_subnet_server_host_3': {'Interface': [{'Subnet': IPv4Network('10.0.157.0/24'),
                                                                    'ip_address': IPv4Address('10.0.157.250')}],
                                                    'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                    'System info': {'Hostname': 'contractor_network_subnet_server_host_3'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```


=== "Blue Observation"
    In blue's observation, you can see a network connection alert has come in from the Monitor default action that runs every step (even when the agent is sleeping).

    This connection is from the local host 'restricted_zone_a_subnet_server_host_0', on their local port 25 (where the decoy service is). The connection is coming from an IP address in the contractor network... how mysterious.

    ??? quote "Code Output"
        ```
        Blue:
        {'action': Sleep,
        'restricted_zone_a_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.7.254')}],
                                                    'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.7.254'),
                                                                                    'local_port': 25,
                                                                                    'remote_address': IPv4Address('10.0.157.250'),
                                                                                    'remote_port': 58659}]}],
                                                    'System info': {'Architecture': <Architecture.x64: 2>,
                                                                    'Hostname': 'restricted_zone_a_subnet_server_host_0',
                                                                    'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                                                                    'OSType': <OperatingSystemType.LINUX: 3>,
                                                                    'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                                                                    'position': array([0., 0.])}},
        'success': <TernaryEnum.UNKNOWN: 2>}
        ```

    The eagle-eyed may have noticed that '10.0.157.250' is the IP address of the original red shell (with session id 0), not the host that has the red reverse shell.

---

## Red Attempts to Exploit the Decoy
Once red has discovered the service, they can now try to exploit it. However it may not go as they planned :smiling_imp:.

In the code below, 'red_agent_0' attempts to exploit the target host which has only a decoy service on it.
```python
action = ExploitRemoteService(ip_address=target_ip, session=0, agent=red_agent_name[0])
action.duration = 1
obs, _, _, _ = cyborg.parallel_step(actions={red_agent_name[0]: action})

print("ExploitRemoteService:")
print("Red:")
pprint(obs[red_agent_name[0]])
print("\n")
print("Blue:")
pprint(obs[blue_agent_name])
print("\n")
```

=== "Red's Observation"
    In red's observation, they get a confirmation that there is an process at port 25 with an SMTP service running.
    However their action failed for some reason. The ExploitRemoteService action is not 100% successful everytime, so why not try again?

    This results in red wasting more of their steps on a service they can never properly utilise. 

    ??? quote "Code Output"
        ```
        Red:
        {'10.0.7.254': {'Interface': [{'ip_address': IPv4Address('10.0.7.254')}],
                        'Processes': [{'Connections': [{'Status': <ProcessState.OPEN: 2>,
                                                        'local_address': IPv4Address('10.0.7.254'),
                                                        'local_port': 25}],
                                    'process_type': <ProcessType.SMTP: 5>}]},
        'action': ExploitRemoteService 10.0.7.254,
        'contractor_network_subnet_server_host_0': {'Interface': [{'Subnet': IPv4Network('10.0.157.0/24'),
                                                                    'ip_address': IPv4Address('10.0.157.254')}],
                                                    'Sessions': [{'Type': <SessionType.RED_REVERSE_SHELL: 11>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 1,
                                                                'username': 'root'}],
                                                    'System info': {'Hostname': 'contractor_network_subnet_server_host_0'}},
        'contractor_network_subnet_server_host_3': {'Interface': [{'Subnet': IPv4Network('10.0.157.0/24'),
                                                                    'ip_address': IPv4Address('10.0.157.250')}],
                                                    'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                    'System info': {'Hostname': 'contractor_network_subnet_server_host_3'}},
        'success': <TernaryEnum.FALSE: 3>}
        ```

    **Note:** If there are services that are not decoys on the host, red may be able to exploit those services to get a shell on the host.
    Having one decoy on a host does not make the host immune to compromise, it is designed to give blue better visibility.


=== "Blue's Observation"
    In blue's observation, they have two additional alerts. One is the connection between the red and the open port 25, and the other between the host and red on epherimeral ports that represents an attempted C2 connection. 

    Due to there being no PID value in the connection, a process was not created by this.

    ??? quote "Code Output"
        ```
        Blue:
        {'action': Sleep,
        'restricted_zone_a_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.7.254')}],
                                                    'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.7.254'),
                                                                                    'local_port': 25,
                                                                                    'remote_address': IPv4Address('10.0.157.250'),
                                                                                    'remote_port': 57563}]},
                                                                {'Connections': [{'local_address': IPv4Address('10.0.7.254'),
                                                                                    'local_port': 51672,
                                                                                    'remote_address': IPv4Address('10.0.157.250'),
                                                                                    'remote_port': 58056}]}],
                                                    'System info': {'Architecture': <Architecture.x64: 2>,
                                                                    'Hostname': 'restricted_zone_a_subnet_server_host_0',
                                                                    'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                                                                    'OSType': <OperatingSystemType.LINUX: 3>,
                                                                    'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                                                                    'position': array([0., 0.])}},
        'success': <TernaryEnum.UNKNOWN: 2>}
        ```