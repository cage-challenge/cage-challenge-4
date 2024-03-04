# Impact
`Impact` attempts to affect services used by green in the mission. This is achieved by stopping the OT (operational technology) service currently running on a host that red has root priviliges on. 

This is a powerful action for red, as OT services are essential to the mission and have a large affect on Blue's reward, however OT services are only present on servers in the Operational Zones - which limits this. Consequently, if the OT service is not present on the host that has been impacted, the action will fail.

This action has a few other actions as prerequisities to run successfully. This tutorial will go over them briefly, but for more information on them, check their individual tutorial pages. 

## Red Agent Preamble

The red agent will only be successful with the Impact action, if they are in Operational Zones A and B. However it can take a while to expand from the contractor network into the operational networks. For this example, a OT service has been created on `contractor_network_subnet_server_host_0` to demonstrate a successful Impact action quickly, however this means that this tutorial is not directly repeatable.

The Impact action also requires a red root shell on the host. To get this the following actions must be run:

- `DiscoverRemoteSystems` - to find all the hosts on the contractor network.
- `AggressiveServiceDiscovery` (or `StealthServiceDiscovery`) - to find the services on host `contractor_network_subnet_server_host_0`.
- `ExploitRemoteService_cc4` - to get a user level shell on the host.
- `PrivilegeEscalate` - to get a root level shell on the host.

You can refer to the [DegradeServices preamble](6_Degrade_Services.md#red-agent-preamble) for more details.

Here is the observation space output for the PrivilegeEscalate action, for comparison later:
??? quote "Code Output"
    ```
    {'action': PrivilegeEscalate contractor_network_subnet_server_host_0,
    'contractor_network_subnet_server_host_0': {'Interface': [{'Subnet': IPv4Network('10.0.120.0/24'),
                                                                'ip_address': IPv4Address('10.0.120.254')}],
                                                'Sessions': [{'Type': <SessionType.SSH: 2>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 1,
                                                            'username': 'root'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_server_host_0'}},
    'contractor_network_subnet_user_host_3': {'Interface': [{'Subnet': IPv4Network('10.0.120.0/24'),
                                                            'ip_address': IPv4Address('10.0.120.47')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_3'}},
    'public_access_zone_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.188.254')}]},
    'restricted_zone_a_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.28.254')}]},
    'restricted_zone_b_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.15.254')}]},
    'success': <TernaryEnum.TRUE: 1>}

    ```

## Impact Action

To perform the Impact action, you only require the hostname, session, and agent parameters.

``` python
def perform_impact_action(cyborg):
    action = Impact(hostname='contractor_network_subnet_server_host_0', session=0, agent='red_agent_0')
    return cyborg.step(agent='red_agent_0', action=action)
```

A successful observation is shown below:
???+ quote "Code Output"
    ```
    {'action': Impact contractor_network_subnet_server_host_0,
    'contractor_network_subnet_server_host_0': {'Interface': [{'Subnet': IPv4Network('10.0.120.0/24'),
                                                                'ip_address': IPv4Address('10.0.120.254')}],
                                                'Processes': [{'Known Process': <ProcessName.OTSERVICE: 29>,
                                                                'PID': 8029,
                                                                'process_name': <ProcessName.OTSERVICE: 29>,
                                                                'process_type': <ProcessType.UNKNOWN: 1>,
                                                                'username': 'user'}],
                                                'Sessions': [{'Type': <SessionType.SSH: 2>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 1,
                                                            'username': 'root'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_server_host_0'}},
    'contractor_network_subnet_user_host_3': {'Interface': [{'Subnet': IPv4Network('10.0.120.0/24'),
                                                            'ip_address': IPv4Address('10.0.120.47')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_3'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```

In the processes dictionary of the observation space, you can see the stopped OT service.
```
'Processes': [{'Known Process': <ProcessName.OTSERVICE: 29>,
    'PID': 8029,
    'process_name': <ProcessName.OTSERVICE: 29>,
    'process_type': <ProcessType.UNKNOWN: 1>,
    'username': 'user'}],
```

This information, alongside `'success': <TernaryEnum.TRUE: 1>`, shows that the OT service was stopped.
