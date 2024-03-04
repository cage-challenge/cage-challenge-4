# Debugging Tools

## The True State

In order to help users understand what is going on, it is necessary to be able to pull out the true state of the network at any time. This is obtained by calling the `get_agent_state` method and passing in agent's name. 

```python title="debugging_tools_example.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent


seed = 1234
sg = EnterpriseScenarioGenerator(
    blue_agent_class=SleepAgent,
    green_agent_class=EnterpriseGreenAgent,
    red_agent_class=FiniteStateRedAgent,
    steps=100
)
cyborg = CybORG(scenario_generator=sg, seed=seed)
cyborg.reset()

true_state = cyborg.get_agent_state('red_agent_0')
pprint(true_state)
```

??? quote "Code Output"
    ```
    {'contractor_network_subnet_user_host_2': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                                            'interface_name': 'eth0',
                                                            'ip_address': IPv4Address('10.0.74.39')}],
                                            'Processes': [{'PID': 9267,
                                                            'username': 'ubuntu'}],
                                            'Sessions': [{'PID': 9267,
                                                            'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'timeout': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Architecture': <Architecture.x64: 2>,
                                                            'Hostname': 'contractor_network_subnet_user_host_2',
                                                            'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                                                            'OSType': <OperatingSystemType.LINUX: 3>,
                                                            'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                                                            'position': array([0., 0.])},
                                            'User Info': [{'Groups': [{'GID': 0}],
                                                            'username': 'root'},
                                                            {'Groups': [{'GID': 1}],
                                                            'username': 'user'}]},
    'success': <TernaryEnum.UNKNOWN: 2>}
    ```

Red's observation is relatively readable, however as Blue and Green have larger observation spaces it can be better to visualise this data as a table.

The [TrueStateTableWrapper](3_Wrappers.md#truestatetablewrapper) can show you how to use this wrapper to get out more information about the true state of the environment.

## Other Debugging Tools

CybORG has a host of other tools to help understand the agent state. 

### Get Observation

You can use the `get_observation` method instead of examining the return from `step` or `parallel_step` functions.

```python title="debugging_tools_example.py" linenums="21"

cyborg.step()

obs = cyborg.get_observation('red_agent_0')
pprint(obs)
```


??? quote "Code Output"
    ```
    {'10.0.74.157': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.157')}]},
    '10.0.74.171': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.171')}]},
    '10.0.74.183': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.183')}]},
    '10.0.74.241': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.241')}]},
    '10.0.74.252': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.252')}]},
    '10.0.74.253': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.253')}]},
    '10.0.74.254': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.254')}]},
    '10.0.74.39': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                'ip_address': IPv4Address('10.0.74.39')}]},
    '10.0.74.45': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                'ip_address': IPv4Address('10.0.74.45')}]},
    '10.0.74.49': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                'ip_address': IPv4Address('10.0.74.49')}]},
    '10.0.74.72': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                'ip_address': IPv4Address('10.0.74.72')}]},
    '10.0.74.95': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                'ip_address': IPv4Address('10.0.74.95')}]},
    'action': DiscoverRemoteSystems 10.0.74.0/24,
    'contractor_network_subnet_user_host_2': {'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                                            'ip_address': IPv4Address('10.0.74.39')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_2'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```

Here you can see the observation that `red_agent_0` gained from its last action `DiscoverRemoteSystems`.

### Get Last Action

We have also seen the `get_last_action` method.

```python title="debugging_tools_example.py" linenums="26"
red_last_action = cyborg.get_last_action('red_agent_0')
green_last_action = cyborg.get_last_action('green_agent_0')
blue_last_action = cyborg.get_last_action('blue_agent_0')

print("red_agent_0 last action: ", red_last_action)
print("green_agent_0 last action: ", green_last_action)
print("blue_agent_0 last action: ", blue_last_action)
```

???+ quote "Code Output"
    ```
    red_agent_0 last action:  [DiscoverRemoteSystems 10.0.74.0/24]
    green_agent_0 last action:  [GreenLocalWork 10.0.26.88]
    blue_agent_0 last action:  [Sleep]
    ```

Note that though blue agent's last action is Sleep, blue has also run its default action 'Monitor'. However, due to it being run every time it is not displayed.

### Get Action Space

The `get_action_space` method allows us to get the action space of any agent. This is space is quite large, so only the keys are printed in this example.

```python title="debugging_tools_example.py" linenums="34"
red_action_space = cyborg.get_action_space('red_agent_0')
print(list(red_action_space.keys()))
```

???+ quote "Code Output"
    ```
    ['action', 'allowed_subnets', 'subnet', 'ip_address', 'session', 'username', 'password', 'process', 'port', 'target_session', 'agent', 'hostname']
    ```

### Get IP Addresses Map

The `get_ip_map` method allows us to see which hostnames are associated with each ip. 

???+ info "Remember"
    Blue agents are aware of the whole network from the start, however red finds out more depending on its actions.

The CC4 scenario has a large number of hosts, so a smaller subsection is shown in the example.

```python title="debugging_tools_example.py" linenums="37"
ip_map = cyborg.get_ip_map()
router_ip_maps = {host: ip for host, ip in ip_map.items() if 'router' in host}
pprint(router_ip_maps)
```

???+ quote "Code Output"
    ```
    {'admin_network_subnet_router': IPv4Address('10.0.90.243'),
    'contractor_network_subnet_router': IPv4Address('10.0.74.121'),
    'office_network_subnet_router': IPv4Address('10.0.32.51'),
    'operational_zone_a_subnet_router': IPv4Address('10.0.27.208'),
    'operational_zone_b_subnet_router': IPv4Address('10.0.183.241'),
    'public_access_zone_subnet_router': IPv4Address('10.0.177.163'),
    'restricted_zone_a_subnet_router': IPv4Address('10.0.26.209'),
    'restricted_zone_b_subnet_router': IPv4Address('10.0.86.23')}
    ```

### Get Rewards

The `get_rewards` method allows us to see the rewards for all agents.

```python title="debugging_tools_example.py" linenums="41"
rewards = cyborg.get_rewards()
pprint(rewards)
```
???+ quote "Code Output"
    ```
    {'Blue': {'BlueRewardMachine': 0, 'action_cost': 0},
    'Green': {'None': 0.0, 'action_cost': 0},
    'Red': {'None': 0.0, 'action_cost': 0}}
    ```

