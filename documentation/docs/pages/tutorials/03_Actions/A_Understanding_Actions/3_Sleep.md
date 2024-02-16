
# Sleep - The Universal Action

Sleep is a valid action for all agents, and results in the agent not choosing to affect the environment on their turn.
The action also does not require any parameters to be performed.

```python title="example_sleep_action.py" linenums="18"
example_action = Sleep()

results = cyborg.step(agent=example_agent_name, action=example_action)
pprint(results.observation)
```


However, the returned observations vary slightly between the different agent types, as can be seen below.

=== "'blue_agent_0'" 
    ``` shell
    {'action': Sleep, 'success': <TernaryEnum.UNKNOWN: 2>}
    ```

=== "'red_agent_0'"
    ``` shell
    {'action': Sleep,
    'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                            'ip_address': IPv4Address('10.0.96.73')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
    'success': <TernaryEnum.UNKNOWN: 2>}
    ```

=== "'green_agent_0'"
    ``` shell
    {'action': Sleep, 'success': <TernaryEnum.UNKNOWN: 2>}
    ```

All agents have the same action and success value, however red receives information about what active shell sessions it has in the environment.