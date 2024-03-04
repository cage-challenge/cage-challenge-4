# Remove
`Remove` results in a red user level shell being removed from the target host.

As this action takes a few time steps, is is worthwhile being sure that a red agent is actually on the host. 
The feedback in the observation space every step, from the `Monitor` action, can be used as evidence however `Analyse` will provide better proof of a shell being on the host.

???+ warning "User vs Root Shells"
    `Remove` is not as powerful an action as `Restore`, which is the equivalent of starting from scratch via backups, which is partially why it takes less time steps to perform. Therefore `Remove` will **NOT** be effective against red root shells, only against user shells.


## Red Preamble

This tutorial will use the same initial [red preamble](3_Decoy.md#red-preamble) as the `DeployDecoy` tutorial, please refer to that for more details about getting a root shell on `contractor_network_subnet_server_host_0`.

However this tutorial will also require another helper function to get a shell on `restricted_zone_a_subnet_server_host_0`. In this example, `target_subnet` and `target_host` are global variables.

??? info "Helper Function"
    ```python
    target_subnet = 'restricted_zone_a_subnet'
    target_host = target_subnet + '_server_host_0'

    def get_shell_on_rzas0(cyborg:CybORG, shell_type:str = 'root'):
        # shell_type = user or root

        env = cyborg.environment_controller
        target_ip = env.state.hostname_ip_map[target_host]

        # Discover a service on restricted_zone_a_subnet_server_host_0
        red_action = AggressiveServiceDiscovery(session=0, agent=red_agent_name[0], ip_address=target_ip)
        results = cyborg.step(agent=red_agent_name[0], action=red_action)
        obs = results.observation
        assert 'AggressiveServiceDiscovery' in str(obs['action'])
        print(obs['action'], obs['success'])
        assert obs['success'] == True

        # Red exploits restricted_zone_a_subnet_server_host_0 to gain a user shell
        action = ExploitRemoteService(ip_address=target_ip, session=0, agent=red_agent_name[0])
        action.duration = 1
        results = cyborg.step(agent=red_agent_name[0], action=action)
        obs = results.observation
        print(obs['action'], obs['success'])
        assert 'Exploit' in str(obs['action'])
        assert obs['success'] == True

        if shell_type == 'user':
            return cyborg

        # Red privilege escalates restricted_zone_a_subnet_server_host_0 to gain a user shell
        red_action = PrivilegeEscalate(hostname=target_host, session=0, agent=red_agent_name[1])
        action.duration = 1
        results = cyborg.step(agent=red_agent_name[1], action=red_action)
        obs = results.observation
        print(obs['action'], obs['success'])
        assert 'PrivilegeEscalate' in str(obs['action'])
        assert obs['success'] == True

        return cyborg
    ```

When nesting both helper functions, as shown here:
```python
cyborg = get_shell_on_rzas0(cyborg=cyborg_with_root_shell_on_cns0(), shell_type='user')
```

You should get the following list of actions:
```
DiscoverRemoteSystems 10.0.157.0/24 TRUE
AggressiveServiceDiscovery 10.0.157.254 TRUE
ExploitRemoteService 10.0.157.254 TRUE
PrivilegeEscalate contractor_network_subnet_server_host_0 TRUE
AggressiveServiceDiscovery 10.0.7.254 TRUE
ExploitRemoteService 10.0.7.254 TRUE
```

## Successfully Removing a User Shell
The aim of using the `Remove` action is to remove a user shell from a target host.

So let's see from both a blue and red perspective, how this action functions successfully.
In this scenario, red has managed to get a user shell on `restricted_zone_a_subnet_server_host_0`.

```python
# start with a cyborg environment with a user shell on `restricted_zone_a_subnet_server_host_0`
cyborg = get_shell_on_rzas0(cyborg=cyborg_with_root_shell_on_cns0(), shell_type='user')
env = cyborg.environment_controller
target_ip = env.state.hostname_ip_map[target_host]

print("Red: Before Remove")
pprint(cyborg.get_observation(agent=red_agent_name[1]))
print("\n")

# Run the Remove action
blue_action = Remove(session=0, agent=blue_agent_name, hostname=target_host)
blue_action.duration = 1
obs, _, _, _ = cyborg.parallel_step(actions={blue_agent_name: blue_action})
assert obs['blue_agent_0']['success'] == True

print("Blue: Remove Step")
pprint(obs['blue_agent_0'])
print("\n")

print("Red: Remove Step")
pprint(obs[red_agent_name[1]] if red_agent_name[1] in cyborg.active_agents else "not an active agents")
```

=== "Red: Before Remove"

    Before the shell is removed, you can tell from red's observation that they have managed to get a red abstract session (shell) with username 'user' (indicating it is a user level shell) on `restricted_zone_a_subnet_server_host_0`. This is the shell that blue will be trying to remove.

    There are no other shells that this agent has in this network.

    ??? quote "Code Output"
        ```
        Red: Before Remove
        {'10.0.7.254': {'Interface': [{'ip_address': IPv4Address('10.0.7.254')}],
                        'Processes': [{'Connections': [{'Status': <ProcessState.OPEN: 2>,
                                                        'local_address': IPv4Address('10.0.7.254'),
                                                        'local_port': 22}],
                                    'process_type': <ProcessType.SSH: 2>},
                                    {'Connections': [{'local_address': IPv4Address('10.0.7.254'),
                                                        'local_port': 22,
                                                        'remote_address': IPv4Address('10.0.157.250'),
                                                        'remote_port': 55532}],
                                    'process_type': <ProcessType.SSH: 2>}],
                        'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                    'agent': 'red_agent_1',
                                    'session_id': 0,
                                    'username': 'user'}],
                        'System info': {'Hostname': 'restricted_zone_a_subnet_server_host_0',
                                        'OSType': <OperatingSystemType.LINUX: 3>}},
        'action': Sleep,
        'restricted_zone_a_subnet_server_host_0': {'Interface': [{'Subnet': IPv4Network('10.0.7.0/24'),
                                                                'ip_address': IPv4Address('10.0.7.254')}],
                                                    'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_1',
                                                                'session_id': 0,
                                                                'username': 'user'}],
                                                    'System info': {'Hostname': 'restricted_zone_a_subnet_server_host_0'}},
        'success': <TernaryEnum.UNKNOWN: 2>}
        ```


=== "Blue: Remove Step"

    It is confirmed through blue's observation that their action was successful. But there is nothing in the observation space to indicate that the shell has been removed.

    ???+ quote "Code Output"
        ```
        Blue: Remove Step
        {'action': Remove restricted_zone_a_subnet_server_host_0,
        'success': <TernaryEnum.TRUE: 1>}
        ```


=== "Red: Remove Step"
    
    We can confirm through the active agents list in cyborg that the red agent is no longer active.
    This is because their only shell has been removed - if they had another shell, the observation would show that one of the shells had disappeared.

    ???+ quote "Code Output"
        ```
        Red: Remove Step
        'not an active agents'
        ```

## Attempting to Remove a Root Shell
Here is an example of what would happen if blue tried to remove a root shell.

It only requires changing one line in our python file. Now instead of a user shell, we have a root shell.
```python
cyborg = get_shell_on_rzas0(cyborg=cyborg_with_root_shell_on_cns0(), shell_type='root')
```

=== "Red: Before Remove"
    You can see from red's observation that the PrivilegeEscalate action was successfull and they now have a red abstract session (shell) with username 'root' (indicating root level privileges).

    ??? quote "Code Output"
        ```
        Red: Before Remove
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
    The blue observation is the same as for the user level shell. That is because the `Remove` action has successfully removed any user level shells, there just weren't any to remove.

    ???+ quote "Code Output"
        ```
        Blue: Remove Step
        {'action': Remove restricted_zone_a_subnet_server_host_0,
        'success': <TernaryEnum.TRUE: 1>}
        ```

=== "Red: Remove Step"
    You can then see from red's observation that the root shell is still there. This action has been a waste of time for blue.

    ???+ quote "Code Output"
        ```
        Red: Remove Step
        {'action': Sleep,
        'restricted_zone_a_subnet_server_host_0': {'Interface': [{'Subnet': IPv4Network('10.0.7.0/24'),
                                                                'ip_address': IPv4Address('10.0.7.254')}],
                                                    'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_1',
                                                                'session_id': 0,
                                                                'username': 'root'}],
                                                    'System info': {'Hostname': 'restricted_zone_a_subnet_server_host_0'}},
        'success': <TernaryEnum.UNKNOWN: 2>}
        ```