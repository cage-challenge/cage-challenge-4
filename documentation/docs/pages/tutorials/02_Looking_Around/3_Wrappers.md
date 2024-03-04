# Wrappers

## Table Wrappers

Table Wrappers attempt to use basic logic to infer a human-friendly picture of the state by keeping track of past observations. This allows for a simplified state space and much greater human readibility. 

### TrueStateTableWrapper

This wrapper contains functions that format the raw true state, gained from the CybORG environment, into tables using the [PrettyTables package](https://pypi.org/project/prettytable/). The raw true state dictionary can instead be returned as a dictionary by the `get_raw_full_true_state()` function.



This information should not be made available to the agents, as it contains the ground truth of the environment. Part of the CAGE challenges is about dealing with a limited observation space, to mimic real-life. In reality, Blue teams rely heavily on IDS tooling via SIEMS that produce alerts, however the tools can generate false positives alerts or can miss actual indicators of compromise (IoC). This is replicated in CC4.

Nevertheless, it is worthwhile for the contestants and development team to have access to this 'true state' information for understanding of the environment and debugging. 

`true_state_wrapper_example.py` shows how this wrapper would be implemented:

```python title="true_state_wrapper_example.py" linenums="1"
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent, 
from CybORG.Agents.Wrappers.TrueStateWrapper import TrueStateTableWrapper

steps = 1000
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)
env = TrueStateTableWrapper(cyborg)
cyborg.reset()
```

This wrapper produces 3 types of output: an overview, a process perspective, and an agent perspective. The usage and outputs from these functions are further demonstrated next. The functions are further documented in the [reference section](../../reference/reference.md#outputs-and-wrappers).

=== "Host Overview"
    ```python title="true_state_wrapper_example.py" linenums="15"
    env.print_host_overview_table()
    ```
    The function above makes a single table with these headings:
    
    - **Hostname** - The host's name
    - **IP Address** - The IP address of the host
    - **Sessions** - A list of names of the agents with sessions linked to that host
    - **No. Processes** - The number of processes running on the host

    A reduced output is shown below:

    ???+ quote "Code Output"
        ```
        +-----------------------------------------+--------------+------------------------------------+---------------+
        |                 Hostname                |  IP Address  |              Sessions              | No. Processes |
        +-----------------------------------------+--------------+------------------------------------+---------------+
        |     restricted_zone_a_subnet_router     | 10.0.26.209  |          ['blue_agent_0']          |       1       |
        |   restricted_zone_a_subnet_user_host_0  |  10.0.26.88  | ['blue_agent_0', 'green_agent_0']  |       3       |
        |   restricted_zone_a_subnet_user_host_1  |  10.0.26.43  | ['blue_agent_0', 'green_agent_1']  |       5       |
        |   restricted_zone_a_subnet_user_host_2  | 10.0.26.173  | ['blue_agent_0', 'green_agent_2']  |       5       |
        |  restricted_zone_a_subnet_server_host_0 | 10.0.26.254  |          ['blue_agent_0']          |       5       |
        |  restricted_zone_a_subnet_server_host_1 | 10.0.26.253  |          ['blue_agent_0']          |       4       |
        |  restricted_zone_a_subnet_server_host_2 | 10.0.26.252  |          ['blue_agent_0']          |       2       |
        |     operational_zone_a_subnet_router    | 10.0.27.208  |          ['blue_agent_1']          |       1       |
        |  operational_zone_a_subnet_user_host_0  | 10.0.27.142  | ['blue_agent_1', 'green_agent_5']  |       6       |
        |                   ...                   |     ...      |                ...                 |      ...      |
        |           root_internet_host_0          | 10.0.30.214  |                 -                  |       0       |
        +-----------------------------------------+--------------+------------------------------------+---------------+
        ```
    

    ---

=== "Host Processes"
    ```python title="true_state_wrapper_example.py" linenums="16"
    env.print_host_processes_tables()
    ```
    The function above makes multiple tables, one for each subnet.
    
    The tables have the following headings:
    
    - **Hostname** - The host's name
    - **PID** - The process identifier
    - **Name** - The process name
    - **Type** - The process type
    - **Username** - The username associated with the process
    - **Sessions** - The name of the agent with linked to that host PID (if it exists)
    - **SID** - The session identifier linked to the PID (if it exists)

    A reduced output is shown below:
    ???+ quote "Code Output"
        ```
        Host Processes Table: Subnet RESTRICTED_ZONE_A 

        +----------------------------------------+------+---------------------+-----------+----------+---------------+-----+
        |                Hostname                | PID  |         Name        |    Type   | Username |    Session    | SID |
        +----------------------------------------+------+---------------------+-----------+----------+---------------+-----+
        |    restricted_zone_a_subnet_router     |  8   |       UNKNOWN       |     -     |  ubuntu  |  blue_agent_0 |  1  |
        +----------------------------------------+------+---------------------+-----------+----------+---------------+-----+
        |  restricted_zone_a_subnet_user_host_0  | 7515 |   ProcessName.SSHD  |    SSH    |   user   |       -       |  -  |
        |                   "                    | 7519 |       UNKNOWN       |     -     |  ubuntu  |  blue_agent_0 |  2  |
        |                   "                    | 7526 |     GREY_SESSION    |     -     |  ubuntu  | green_agent_0 |  0  |
        +----------------------------------------+------+---------------------+-----------+----------+---------------+-----+
        |  restricted_zone_a_subnet_user_host_1  | 9481 |   ProcessName.SSHD  |    SSH    |   user   |       -       |  -  |
        |                   "                    | 3814 |  ProcessName.MYSQLD |   MYSQL   |   user   |       -       |  -  |
        |                   "                    | 8111 | ProcessName.APACHE2 | WEBSERVER |   user   |       -       |  -  |
        |                   "                    | 9487 |       UNKNOWN       |     -     |  ubuntu  |  blue_agent_0 |  3  |
        |                   "                    | 9496 |     GREY_SESSION    |     -     |  ubuntu  | green_agent_1 |  0  |
        +----------------------------------------+------+---------------------+-----------+----------+---------------+-----+
        |  restricted_zone_a_subnet_user_host_2  | 6161 |   ProcessName.SSHD  |    SSH    |   user   |       -       |  -  |
        |                   "                    | 1062 | ProcessName.APACHE2 | WEBSERVER |   user   |       -       |  -  |
        |                   "                    | 3599 |  ProcessName.MYSQLD |   MYSQL   |   user   |       -       |  -  |
        |                   "                    | 6168 |       UNKNOWN       |     -     |  ubuntu  |  blue_agent_0 |  4  |
        |                   "                    | 6177 |     GREY_SESSION    |     -     |  ubuntu  | green_agent_2 |  0  |
        +----------------------------------------+------+---------------------+-----------+----------+---------------+-----+
        | restricted_zone_a_subnet_server_host_0 | 7770 |   ProcessName.SSHD  |    SSH    |   user   |       -       |  -  |
        |                  ...                   | ...  |          ...        |    ...    |   ...    |      ...      | ... |

        ```
    ---

=== "Agent Sessions"
    ```python title="true_state_wrapper_example.py" linenums="17"
    env.print_agent_session_tables()
    ```
    The function above makes multiple tables, one for each agent type (red, blue, green).
    
    The tables have the following headings:
    
    - **Agent** - The agent name
    - **SID** - The session identifier for the agent
    - **Hostname** - The name of the host that the agent has a session on
    - **Username** - The username associated with the session
    - **Type** - The session type
    - **PID** - The process identifier associated with the session

    A reduced output is shown below:
    ???+ quote "Code Output"
        ```
        Agent Session Table: Team red 

        +-------------+-----+---------------------------------------+----------+----------------------+------+
        |    Agent    | SID |                Hostname               | Username |         Type         | PID  |
        +-------------+-----+---------------------------------------+----------+----------------------+------+
        | red_agent_0 |  0  | contractor_network_subnet_user_host_2 |  ubuntu  | RED_ABSTRACT_SESSION | 9267 |
        +-------------+-----+---------------------------------------+----------+----------------------+------+
        

        Agent Session Table: Team blue 

        +--------------+-----+-----------------------------------------+----------+---------------------+------+
        |    Agent     | SID |                 Hostname                | Username |         Type        | PID  |
        +--------------+-----+-----------------------------------------+----------+---------------------+------+
        | blue_agent_0 |  0  |  restricted_zone_a_subnet_server_host_1 |  ubuntu  | VELOCIRAPTOR_SERVER | 9811 |
        |      -       |  1  |     restricted_zone_a_subnet_router     |  ubuntu  |       UNKNOWN       |  8   |
        |      -       |  2  |   restricted_zone_a_subnet_user_host_0  |  ubuntu  |       UNKNOWN       | 7519 |
        |      -       |  3  |   restricted_zone_a_subnet_user_host_1  |  ubuntu  |       UNKNOWN       | 9487 |
        |      -       |  4  |   restricted_zone_a_subnet_user_host_2  |  ubuntu  |       UNKNOWN       | 6168 |
        |      -       |  7  |  restricted_zone_a_subnet_server_host_0 |  ubuntu  |       UNKNOWN       | 7778 |
        |      -       |  8  |  restricted_zone_a_subnet_server_host_2 |  ubuntu  |       UNKNOWN       | 4345 |
        +--------------+-----+-----------------------------------------+----------+---------------------+------+
        | blue_agent_1 |  1  |     operational_zone_a_subnet_router    |  ubuntu  |       UNKNOWN       |  9   |
        |     ...      | ... |                   ...                   |   ...    |         ...         | ...  |
        ```
    ---


## Blue Wrappers

### BlueFixedActionWrapper
This wrapper enumerates the full action space for each Blue agent in the scenario and establishes a fixed integer-to-action mapping that is consistent across runs. Since the number of hosts and the IP addresses of each host varies between episodes, this wrapper updates the list of actions available to the agent at the start of every episode. Action indices will always correspond to a specific action against a specific host, regardless of IP address. If a host is not included in a given episode, the action is replaced with a `Sleep` placeholder and the action label is marked with an `[Invalid]` prefix.

The `step` function accepts actions as `dict[str, int]` where the key is the agent name and the value is an index corresponding to
an action within the agent's action space. A few convenience functions are provided by this wrapper to help understand the
integer-to-action mapping and avoid temporarily invalid actions:

=== "action_space(agent)"

    This function returns a `gymnasium.space.Discrete` with the maximum size of the agent's action space.

    ```python
    >>> env.action_space('blue_agent_0')
    Discrete(82)
    ```

=== "action_labels(agent)"

    Returns an ordered list of human-readable action labels.
    The `[Invalid]` prefix means that this action is temporarily unavailable for the duration of the episode.
    The order of this list will always be consistent.

    ```python
    [
        'Analyse restricted_zone_a_subnet_server_host_0',
        'Analyse restricted_zone_a_subnet_server_host_1',
        'Analyse restricted_zone_a_subnet_server_host_2',
        '[Invalid] Analyse restricted_zone_a_subnet_server_host_3',
        '[Invalid] Analyse restricted_zone_a_subnet_server_host_4',
        '[Invalid] Analyse restricted_zone_a_subnet_server_host_5',
        'Analyse restricted_zone_a_subnet_user_host_0',
        'Analyse restricted_zone_a_subnet_user_host_1',
        'Analyse restricted_zone_a_subnet_user_host_2',
        'Analyse restricted_zone_a_subnet_user_host_3',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_4',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_5',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_6',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_7',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_8',
        '[Invalid] Analyse restricted_zone_a_subnet_user_host_9',
        'Monitor',
        'Remove restricted_zone_a_subnet_server_host_0',
        'Remove restricted_zone_a_subnet_server_host_1',
        'Remove restricted_zone_a_subnet_server_host_2',
        '[Invalid] Remove restricted_zone_a_subnet_server_host_3',
        '[Invalid] Remove restricted_zone_a_subnet_server_host_4',
        '[Invalid] Remove restricted_zone_a_subnet_server_host_5',
        'Remove restricted_zone_a_subnet_user_host_0',
        'Remove restricted_zone_a_subnet_user_host_1',
        'Remove restricted_zone_a_subnet_user_host_2',
        'Remove restricted_zone_a_subnet_user_host_3',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_4',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_5',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_6',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_7',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_8',
        '[Invalid] Remove restricted_zone_a_subnet_user_host_9',
        'Restore restricted_zone_a_subnet_server_host_0',
        'Restore restricted_zone_a_subnet_server_host_1',
        'Restore restricted_zone_a_subnet_server_host_2',
        '[Invalid] Restore restricted_zone_a_subnet_server_host_3',
        '[Invalid] Restore restricted_zone_a_subnet_server_host_4',
        '[Invalid] Restore restricted_zone_a_subnet_server_host_5',
        'Restore restricted_zone_a_subnet_user_host_0',
        'Restore restricted_zone_a_subnet_user_host_1',
        'Restore restricted_zone_a_subnet_user_host_2',
        'Restore restricted_zone_a_subnet_user_host_3',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_4',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_5',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_6',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_7',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_8',
        '[Invalid] Restore restricted_zone_a_subnet_user_host_9',
        'Sleep',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- admin_network_subnet (10.0.57.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- contractor_network_subnet (10.0.184.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- internet_subnet (10.0.163.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- office_network_subnet (10.0.50.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- operational_zone_a_subnet (10.0.133.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- operational_zone_b_subnet (10.0.24.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- public_access_zone_subnet (10.0.63.0/24)',
        'AllowTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- restricted_zone_b_subnet (10.0.210.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- admin_network_subnet (10.0.57.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- contractor_network_subnet (10.0.184.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- internet_subnet (10.0.163.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- office_network_subnet (10.0.50.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- operational_zone_a_subnet (10.0.133.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- operational_zone_b_subnet (10.0.24.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- public_access_zone_subnet (10.0.63.0/24)',
        'BlockTrafficZone restricted_zone_a_subnet (10.0.237.0/24) <- restricted_zone_b_subnet (10.0.210.0/24)',
        'DeployDecoy restricted_zone_a_subnet_server_host_0',
        'DeployDecoy restricted_zone_a_subnet_server_host_1',
        'DeployDecoy restricted_zone_a_subnet_server_host_2',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_server_host_3',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_server_host_4',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_server_host_5',
        'DeployDecoy restricted_zone_a_subnet_user_host_0',
        'DeployDecoy restricted_zone_a_subnet_user_host_1',
        'DeployDecoy restricted_zone_a_subnet_user_host_2',
        'DeployDecoy restricted_zone_a_subnet_user_host_3',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_4',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_5',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_6',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_7',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_8',
        '[Invalid] DeployDecoy restricted_zone_a_subnet_user_host_9'
    ]
    ```

=== "action_mask(agent)"

    Returns a list of booleans corresponding to whether an action can be executed in a given episode.
    This list is also included in the `info` dictionary returned by `reset()` and `step()`.

    ```python
    >>> env.action_mask('blue_agent_0')
    [ True, True, True, False, False, False, True, True, True, True, False, False, False, False, False, False, True, True, True, True, False, False, False, True, True, True, True, False, False, False, False, False, False, True, True, True, False, False, False, True, True, True, True, False, False, False, False, False, False, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, False, False, False, True, True, True, True, False, False, False, False, False, False ]
    ```

???+ Note "Action Space Padding"
    By default, the action space of each agent corresponds to the size of the agent's
    full action space, however, some libraries require all agents to have the same
    action space size. In this case, the `pad_spaces = True` argument can be passed
    to the wrapper to pad the action spaces of each agent with `Sleep` actions. These
    will actions will have a `[Padding]` prefix in the list of action labels and have
    a mask value of `False`.

### BlueFlatWrapper

This wrapper is an extension of the `BlueFixedActionWrapper` that flattens the CybORG
observation into a vector of fixed-size and fixed-order for training RL agents.
A full breakdown of how the observation vectors are structured is available at
[Appendix B](../../README.md#appendix-b-agent-observation).

???+ Note "Observation Space Padding"
    Setting `pad_spaces = True` will pad the observation vector of each agent to the
    largest observation space by filling the remaining space with zeros. This will
    also pad the action space as needed.

### BlueEnterpriseWrapper

`BlueEnterpriseWrapper` is an alias of `BlueFlatWrapper`.


## Library-Specific Wrappers
If you are utilising a machine learning library, such as TensorFlow, PyTorch, or Scikit-learn, you may need to create a library specific wrapper to interface between CybORG and your library of choice in order to create/train your algorithm.

**We highly encourage solutions made incorporating ML and hope that this documentation can help you with this task.**

Unfortunately we cannot create wrappers for everyone, so we have created one for RLlib - a widely used python reinforcement learning library - and hope that this example will be a sufficient basis when making your own.

### EnterpriseMAE
This wrapper is a `BlueEnterpriseWrapper` that is compatible with RLlib's `MultiAgentEnv` class to interface between CybORG and RLlib agents.

A step-by-step guide for getting started with this wrapper is available in [Tutorial 1 - Training RLlib Agents](../01_Getting_Started/3_Training_Agents.md).
