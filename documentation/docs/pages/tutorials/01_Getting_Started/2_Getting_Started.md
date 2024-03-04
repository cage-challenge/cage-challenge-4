# Getting Started With CybORG

## Importing CybORG

To use the CybORG environment, it is necessary to import the `CybORG` class. 

!!! tip "Capitalisation"
    CybORG stands for '**C**yber **O**perations **R**esearch **G**ym', so remember to capitalise correctly when importing!

```python title="getting_started.py" linenums="1"
from CybORG import CybORG
```

## Instantiating CybORG

CybORG has to be manually instantiated by calling the class constructor. This must be passed a `ScenarioGenerator` class, which contains the details of the scenario.
For Challenge 4, we will be using the `EnterpriseScenarioGenerator`, which creates the correct scenario.

```python linenums="2"
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator

sg = EnterpriseScenarioGenerator()
cyborg = CybORG(scenario_generator=sg)
```

## Interfacing with the Environment 

CAGE Challenge 4 (CC4) is a multi-agent scenario consisting of several teams of agents. The Red team will be attacking the network, Blue team will be defending the network, while Green team represents the network users who will be passing messages to each other via the enterpise network. For this challenge, the roles of Red and Green will be handled by internal rules-based agents, while your task is to use an external API to train the Blue Team. This guide will walk you through the first steps for interfacing with the Blue agents.

A good starting point for developing your own rule-based agent is the `BlueFixedActionWrapper`. This wrapper provides a covenient API for enumerating all the actions that are available to each Blue agent in each episode, while providing direct access to CybORG's observations.

```python linenums="6"
from CybORG.Agents.Wrappers import BlueFixedActionWrapper

env = BlueFixedActionWrapper(env=cyborg)
obs, _ = env.reset()

# optional pretty-printing
from rich import print

print(obs.keys())
```

???+ Quote "Code Output"
    ```
    dict_keys(['blue_agent_0', 'blue_agent_1', 'blue_agent_2', 'blue_agent_3', 'blue_agent_4'])
    ```

```python linenums="15"
print(obs['blue_agent_0'])
```

??? Quote "Code Output (CybORG Observation)"
    ???+ Note
        For more information on CybORG observations, see [Tutorial 2 - Looking Around](../02_Looking_Around/1_Observations.md).

    ```python
    {
        'success': <TernaryEnum.UNKNOWN: 2>,
        'restricted_zone_a_subnet_router': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.28'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 1, 'username': 'ubuntu', 'timeout': 0, 'PID': 3, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 3, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_router',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_0': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.192'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 2, 'username': 'ubuntu', 'timeout': 0, 'PID': 8580, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 8580, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_0',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_1': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.214'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 3, 'username': 'ubuntu', 'timeout': 0, 'PID': 9865, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 9865, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_1',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_2': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.209'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 4, 'username': 'ubuntu', 'timeout': 0, 'PID': 6978, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 6978, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_2',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_3': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.64'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 5, 'username': 'ubuntu', 'timeout': 0, 'PID': 4406, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 4406, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_3',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_4': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.215'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 6, 'username': 'ubuntu', 'timeout': 0, 'PID': 9400, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 9400, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_4',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_5': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.204'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 7, 'username': 'ubuntu', 'timeout': 0, 'PID': 5630, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 5630, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_5',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_6': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.195'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 8, 'username': 'ubuntu', 'timeout': 0, 'PID': 5546, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 5546, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_6',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_user_host_7': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.54'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 9, 'username': 'ubuntu', 'timeout': 0, 'PID': 4990, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 4990, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_user_host_7',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_server_host_0': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.254'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [
                {'session_id': 0, 'username': 'ubuntu', 'timeout': 0, 'PID': 7023, 'Type': <SessionType.VELOCIRAPTOR_SERVER: 8>, 'agent': 'blue_agent_0'}
            ],
            'Processes': [{'PID': 7023, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_server_host_0',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_server_host_1': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.253'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 10, 'username': 'ubuntu', 'timeout': 0, 'PID': 8838, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 8838, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_server_host_1',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_server_host_2': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.252'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 11, 'username': 'ubuntu', 'timeout': 0, 'PID': 1443, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 1443, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_server_host_2',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        },
        'restricted_zone_a_subnet_server_host_3': {
            'Interface': [{'interface_name': 'eth0', 'ip_address': IPv4Address('10.0.143.251'), 'Subnet': IPv4Network('10.0.143.0/24')}],
            'Sessions': [{'session_id': 12, 'username': 'ubuntu', 'timeout': 0, 'PID': 8640, 'Type': <SessionType.UNKNOWN: 1>, 'agent': 'blue_agent_0'}],
            'Processes': [{'PID': 8640, 'username': 'ubuntu'}],
            'User Info': [{'username': 'root', 'Groups': [{'GID': 0}]}, {'username': 'user', 'Groups': [{'GID': 1}]}],
            'System info': {
                'Hostname': 'restricted_zone_a_subnet_server_host_3',
                'OSType': <OperatingSystemType.LINUX: 3>,
                'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                'Architecture': <Architecture.x64: 2>,
                'position': array([0., 0.])
            }
        }
    }
    ```

A full list of human-readable action labels can be accessed using the `action_labels` function.
This list will always show all the actions that the given agent could take in CC4.
However, some hosts might not exist for the duration of an episode, and as a result, their corresponding
actions will have no effect. This is reflected in the list with a `[Invalid]` prefix.

```python linenums="16"
print(env.action_space('blue_agent_0'))
print(env.action_labels('blue_agent_0'))
```

??? Quote "Code Output (Actions)"
    ???+ Note
        For more information on the action helpers, see
        [Wrappers - BlueFixedActionWrapper](../02_Looking_Around/3_Wrappers.md#bluefixedactionwrapper).

    ```python
    Discrete(82)
    [
        'Analyse restricted_zone_a_subnet_server_host_0',
        'Analyse restricted_zone_a_subnet_server_host_1',
        'Analyse restricted_zone_a_subnet_server_host_2',
        'Analyse restricted_zone_a_subnet_server_host_3',
        '[Invalid] Analyse restricted_zone_a_subnet_server_host_4',
        '[Invalid] Analyse restricted_zone_a_subnet_server_host_5',
        'Analyse restricted_zone_a_subnet_user_host_0',
        'Analyse restricted_zone_a_subnet_user_host_1',
        'Analyse restricted_zone_a_subnet_user_host_2',
        'Analyse restricted_zone_a_subnet_user_host_3',
        'Analyse restricted_zone_a_subnet_user_host_4',
        'Analyse restricted_zone_a_subnet_user_host_5',
        'Analyse restricted_zone_a_subnet_user_host_6',
        'Analyse restricted_zone_a_subnet_user_host_7',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_8',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_9',
        'Monitor',
        'Remove restricted_zone_a_subnet_server_host_0',
        'Remove restricted_zone_a_subnet_server_host_1',
        'Remove restricted_zone_a_subnet_server_host_2',
        'Remove restricted_zone_a_subnet_server_host_3',
        '[Invalid] Remove restricted_zone_a_subnet_server_host_4',
        '[Invalid] Remove restricted_zone_a_subnet_server_host_5',
        'Remove restricted_zone_a_subnet_user_host_0',
        'Remove restricted_zone_a_subnet_user_host_1',
        'Remove restricted_zone_a_subnet_user_host_2',
        'Remove restricted_zone_a_subnet_user_host_3',
        'Remove restricted_zone_a_subnet_user_host_4',
        'Remove restricted_zone_a_subnet_user_host_5',
        'Remove restricted_zone_a_subnet_user_host_6',
        'Remove restricted_zone_a_subnet_user_host_7',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_8',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_9',
        'Restore restricted_zone_a_subnet_server_host_0',
        'Restore restricted_zone_a_subnet_server_host_1',
        'Restore restricted_zone_a_subnet_server_host_2',
        'Restore restricted_zone_a_subnet_server_host_3',
        '[Invalid] Restore restricted_zone_a_subnet_server_host_4',
        '[Invalid] Restore restricted_zone_a_subnet_server_host_5',
        'Restore restricted_zone_a_subnet_user_host_0',
        'Restore restricted_zone_a_subnet_user_host_1',
        'Restore restricted_zone_a_subnet_user_host_2',
        'Restore restricted_zone_a_subnet_user_host_3',
        'Restore restricted_zone_a_subnet_user_host_4',
        'Restore restricted_zone_a_subnet_user_host_5',
        'Restore restricted_zone_a_subnet_user_host_6',
        'Restore restricted_zone_a_subnet_user_host_7',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_8',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_9',
        'Sleep',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- admin_network_subnet (10.0.88.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- contractor_network_subnet (10.0.48.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- internet_subnet (10.0.131.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- office_network_subnet (10.0.57.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- operational_zone_a_subnet (10.0.173.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- operational_zone_b_subnet (10.0.235.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- public_access_zone_subnet (10.0.115.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- restricted_zone_b_subnet (10.0.21.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- admin_network_subnet (10.0.88.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- contractor_network_subnet (10.0.48.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- internet_subnet (10.0.131.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- office_network_subnet (10.0.57.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- operational_zone_a_subnet (10.0.173.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- operational_zone_b_subnet (10.0.235.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- public_access_zone_subnet (10.0.115.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.143.0/24) <- restricted_zone_b_subnet (10.0.21.0/24)',
        'DeployDecoy restricted_zone_a_subnet_server_host_0',
        'DeployDecoy restricted_zone_a_subnet_server_host_1',
        'DeployDecoy restricted_zone_a_subnet_server_host_2',
        'DeployDecoy restricted_zone_a_subnet_server_host_3',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_server_host_4',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_server_host_5',
        'DeployDecoy restricted_zone_a_subnet_user_host_0',
        'DeployDecoy restricted_zone_a_subnet_user_host_1',
        'DeployDecoy restricted_zone_a_subnet_user_host_2',
        'DeployDecoy restricted_zone_a_subnet_user_host_3',
        'DeployDecoy restricted_zone_a_subnet_user_host_4',
        'DeployDecoy restricted_zone_a_subnet_user_host_5',
        'DeployDecoy restricted_zone_a_subnet_user_host_6',
        'DeployDecoy restricted_zone_a_subnet_user_host_7',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_8',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_9'
    ]
    ```

To take an action in the CybORG environment, we use the `env.step()` method.
This method takes a dictionary where the keys are the agent names and whose
values are an index corresponding to an action within the agent's action space.
If the specified action is invalid for the current episode, the agent will simply
do nothing. This function returns the next observation, rewards for the agents,
the termination and truncation signals for each agent, and the info dictionary.

```python linenums="18"
actions = {'blue_agent_0': 42} # 'Restore restricted_zone_a_subnet_user_host_3'
obs, reward, terminated, truncated, info = env.step(actions)
print(reward['blue_agent_0'])
```

???+ Quote "Code Output"
    ```python
    -4.0
    ```

Challenge 4 provides a mechanism to optionally send 8-bit messages between agents.
This is achieved by supplying the `step` function with a dictionary of agents and
a corresponding `np.array` with 8 binary elements.

```python linenums="21"
import numpy as np
messages = {'blue_agent_0': np.array([1, 0, 0, 0, 0, 0, 0, 0])}
obs, reward, terminated, truncated, info = env.step(actions, messages=messages)
print(obs['blue_agent_1']['message'])
```

???+ Quote "Code Output (Messages)"
    ```python
    [
        array([ True, False, False, False, False, False, False, False]), # Blue 0
        array([False, False, False, False, False, False, False, False]), # Blue 2
        array([False, False, False, False, False, False, False, False]), # Blue 3
        array([False, False, False, False, False, False, False, False])  # Blue 4
    ]
    ```

## Reinforcement Learning Agents

Since CybORG observations can be quite verbose, we have included the `BlueFlatWrapper` to
convert the observations into a fixed-size vector format that is convenient for RL agents.

```python linenums="6"
from CybORG.Agents.Wrappers import BlueFlatWrapper

env = BlueFlatWrapper(env=cyborg)
obs, _ = env.reset()

# optional pretty-printing
from rich import print

print('Space:', env.observation_space('blue_agent_0'), '\n')
print('Observation:', obs['blue_agent_0'])
```

???+ Quote "Code Output"
    ???+ Note
        For a full breakdown of how the observation vectors are structured,
        see [Appendix B](../../README.md#appendix-b-agent-observation).

    ```python 
    Space: MultiDiscrete(
        [3 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2
         2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2
         2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2])

    Observation: 
        [0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
         0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
         0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
    ```

???+ Note
    Some RL libraries require all agents to have observation spaces and action spaces of the same size.
    This can be enabled by passing `pad_spaces = True` to the `BlueFlatWrapper`. This will pad the
    observation space with zeros, and pad the action space with the `Sleep` action.

???+ Note "RLlib"
    For an RLlib-compatible, `MultiAgentEnvironment` version of the above wrapper use
    `from CybORG.Agents.Wrappers import EnterpriseMAE` in place of `BlueFlatWrapper`.
    
