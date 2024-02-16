# Restore

`Restore` reimages a host, removing all malicious activity. Any files altered by the Red Agent will be restored to their previous state.

<!-- This function has a flat penalty of -1, representing the downtime of the host. -->

## Red Preamble
The red preamble is the same as for the [Remove](4_Remove.md) tutorial, but with `shell_type='root'`.

The series of actions is as follows:
```
DiscoverRemoteSystems 10.0.157.0/24 TRUE
AggressiveServiceDiscovery 10.0.157.254 TRUE
ExploitRemoteService 10.0.157.254 TRUE
PrivilegeEscalate contractor_network_subnet_server_host_0 TRUE
AggressiveServiceDiscovery 10.0.7.254 TRUE
ExploitRemoteService 10.0.7.254 TRUE
PrivilegeEscalate restricted_zone_a_subnet_server_host_0 TRUE
```

## Restore a Host with a Root Shell
Here is an example of a blue agent successfully removing a red root level shell from a host.

```python
cyborg = get_shell_on_rzas0(cyborg=cyborg_with_root_shell_on_cns0(), shell_type='root')
env = cyborg.environment_controller
target_ip = env.state.hostname_ip_map[target_host]

print("Red: Before Restore")
pprint(cyborg.get_observation(agent=red_agent_name[1]))
print("\n")

blue_action = Restore(session=0, agent=blue_agent_name, hostname=target_host)
blue_action.duration = 1
obs, _, _, _ = cyborg.parallel_step(actions={blue_agent_name: blue_action})

assert obs['blue_agent_0']['success'] == True

print("Blue: Restore Step")
pprint(obs['blue_agent_0'])
print("\n")

print("Red: Restore Step")
pprint(obs[red_agent_name[1]] if red_agent_name[1] in cyborg.active_agents else "not an active agents")
```

=== "Red: Before Restore"
    You can see from red's observation that the PrivilegeEscalate action was successfull and they now have a red abstract session (shell) with username 'root' (indicating root level privileges).

    ??? quote "Code Output"
        ````
        Red: Before Restore
        {'action': PrivilegeEscalate restricted_zone_a_subnet_server_host_0,
        'contractor_network_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.157.254')}]},
        'operational_zone_a_subnet_server_host_0': {'Interface': [{'ip_address': IPv4Address('10.0.58.254')}]},
        'restricted_zone_a_subnet_server_host_0': {'Interface': [{'Subnet': IPv4Network('10.0.7.0/24'),
                                                                'ip_address': IPv4Address('10.0.7.254')}],
                                                    'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_1',
                                                                'session_id': 0,
                                                                'username': 'root'}],
                                                    'System info': {'Hostname': 'restricted_zone_a_subnet_server_host_0'}},
        'success': <TernaryEnum.TRUE: 1>}
        ```
=== "Blue: Remove Step"
    The `Restore` actions executes successfully. Remember that the success is an indication of whether the action has successful run through. In this case everything has been restored from a backup so if it is successful then there is no red presence on the host.

    ???+ quote "Code Output"
        ```
        Blue: Restore Step
        {'action': Restore restricted_zone_a_subnet_server_host_0,
        'success': <TernaryEnum.TRUE: 1>}
        ```

=== "Red: Remove Step"
    The contents of cyborg's active agent variable shows that the red is no longer active, due to their only shell being removed.

    ???+ quote "Code Output"
        ```
        Red: Restore Step
        'not an active agents'
        ```