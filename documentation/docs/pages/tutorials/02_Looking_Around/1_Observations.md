# Observations
The observation space is one of the main outputs that an agent gets from the environment, as it tells the agent all that it can sense happening in the environment. It is therefore important to understand the output - especially when making your own wrapper.

## Active Agents
Not all agents are active every step. If an agent is not active its observation space will not be accurate and it will not be able to take any actions.

You can check what agents are active in the environment by checking the variable `active_agents` in the `CybORG` class.

Here is an example:

```python title="active_agents.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)

cyborg.reset()

print(cyborg.active_agents)
```
???+ quote "Code Output"
    ```
    [
        'blue_agent_0', 'blue_agent_1', 'blue_agent_2', 'blue_agent_3', 
        'blue_agent_4', 
        
        'green_agent_0', 'green_agent_1', 'green_agent_2', 'green_agent_3',
        'green_agent_4', 'green_agent_5', 'green_agent_6', 'green_agent_7', 
        'green_agent_8', 'green_agent_9', 'green_agent_10', 'green_agent_11', 
        'green_agent_12', 'green_agent_13', 'green_agent_14', 'green_agent_15',
        'green_agent_16', 'green_agent_17', 'green_agent_18', 'green_agent_19', 
        'green_agent_20', 'green_agent_21', 'green_agent_22', 'green_agent_23', 
        'green_agent_24', 'green_agent_25', 'green_agent_26', 'green_agent_27', 
        'green_agent_28', 'green_agent_29', 'green_agent_30', 'green_agent_31', 
        'green_agent_32', 'green_agent_33', 'green_agent_34', 'green_agent_35', 
        'green_agent_36', 'green_agent_37', 'green_agent_38', 'green_agent_39', 
        'green_agent_40', 'green_agent_41', 'green_agent_42', 'green_agent_43', 
        'green_agent_44', 'green_agent_45', 'green_agent_46', 'green_agent_47', 
        
        'red_agent_0'
    ]
    ```

You can see at the initialisation of this environment, there are:

- all 5 blue agent active, 
- all 48 green agents active, and 
- only 1 of the red agents active.

There are always 6 red agents and 5 blue agents in an environment, but the number of green agents depends in the number of hosts - which is dynamic in environment and depends on the environmental seed.

The environment will always start with only 1 active red agent, `red_agent_0`, located in the contractor network.

## Red Observations
### Initial Observation

We will begin by instantiating CybORG and looking at `red_agent_0`'s initial observation.

```python title="cc4_red_observations.py" linenums="1"
from pprint import pprint
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent
from CybORG.Simulator.Actions.AbstractActions import PrivilegeEscalate

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)

reset = cyborg.reset(agent='red_agent_0')
first_session_host = list(reset.observation.keys())[1]
initial_obs = reset.observation

print("\nRed Agent 0: Initial Observation \n")
pprint(initial_obs)

```

???+ quote "Code Output"
    ```
    Red Agent 0: Initial Observation 

    {
        'contractor_network_subnet_user_host_2': {
            'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
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
        'success': <TernaryEnum.UNKNOWN: 2>
    }
    ```

The dictionary above has two keys: 

- `success` 
- `contractor_network_subnet_user_host_2` 

The `success` value indicates whether the previous action ran successfully, or whether it encountered an error. 
Since this is the start of the scenario, the success value is set to UNKNOWN.

The key `contractor_network_subnet_user_host_2` is a host identifier, indicating its corresponding value is data about that host. 
Here the host identifier is equal to the name of the host, although this can also be ip addresses depending on the previous action.

???+ Tip "Having trouble reading the outputs?"
    Due to the complex nature of computer security, CybORG's raw observations contain a lot of information presented in a standardised format which takes the form of a series of nested dictionaries and lists. It is recommended that you use `prettyprint` whenever printing a CybORG observation.

### Observable Host's Dictionary
Take a closer look at the `contractor_network_subnet_user_host_2` dictionary, shown in the code output.

```
{
    'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
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
                    'username': 'user'}]}
```

The `contractor_network_subnet_user_host_2` dictionary contains various information about the host, that the red agent knows about. 

- `Interface` gives us networking information such as the host's IP address and subnet.

- `Processes` lets us know any external facing processes running on the host that the red agent knows about.

- `Sessions` lets us know any sessions is aware of, especially shells. 

- `System info` tells us information about the general system and operating system.

- `User Info` gives the different users avaliable on the system, usually 'root' and 'user'.

You may notice that `Interface`, `Processes` and `Sessions` all have lists as values. This is because a host can and usually will have multiple of these running at the same time.

### Level of Red Control over Host
When a red agent has a session on a host, it can have either a user or root privilege level access. In order to perform actions that affect the performance of the host, root level access is needed.

Getting from user to root level access can be done in CC4 by using the PrivilegeEscalate action - which is further demonstrated in the [privilege escalate action tutorial](../03_Actions/C_Red_Actions/5_Privilege_Escalate.md). 

```python title="cc4_red_observations.py" linenums="21"
first_action = PrivilegeEscalate(hostname=first_session_host, session=0, agent='red_agent_0')
results = cyborg.step(agent='red_agent_0', action=first_action)
first_action_obs = results.observation

print("\nRed Agent 0: Observation #1 \n")
pprint(first_action_obs)
```

Let's compare the observation data before and after a successful PrivilegeEscalate action, using the code above:

=== "Initial Observation"
    ???+ quote "Code Output"
        ```
        Red Agent 0: Initial Observation 

        {
            'contractor_network_subnet_user_host_2': 
                {
                    'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
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
                                    'username': 'user'}]
                },
            'success': <TernaryEnum.UNKNOWN: 2>
        }

        ```
    ---

=== "Observation #1"
    ???+ quote "Code Output"
        ```
        Red Agent 0: Observation #1 

        {
            'action': PrivilegeEscalate contractor_network_subnet_user_host_2,
            'contractor_network_subnet_user_host_2': 
                {
                    'Interface': [{'Subnet': IPv4Network('10.0.74.0/24'),
                                    'ip_address': IPv4Address('10.0.74.39')}],
                    'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                    'agent': 'red_agent_0',
                                    'session_id': 0,
                                    'username': 'root'}],
                    'System info': {'Hostname': 'contractor_network_subnet_user_host_2'}
                },
            'success': <TernaryEnum.TRUE: 1>
        }
        ```
    ---

The way to tell the current privileges is by looking at the session username. If the username is `root` it has root level access, otherwise it has user level access.


## Blue Observations
### Initial Blue Observation
For the initial observation space of a blue agent, it sees all the hosts that it is in-charge of protecting.
This initial observation is large, so we will initially only print out the keys.

```python title="cc4_blue_observations.py" linenums="1"
from pprint import pprint
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import Sleep

steps = 1000
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)

reset = cyborg.reset(agent='blue_agent_0')
initial_obs = reset.observation

print("\nBlue Agent 0: Initial Observation")
print("\nKeys Only: \n")
pprint(initial_obs.keys())
```
???+ quote "Code Output"
    ```
    Blue Agent 0: Initial Observation

    Keys Only: 

    dict_keys([
        'success', 'restricted_zone_a_subnet_router', 'restricted_zone_a_subnet_user_host_0', 
        'restricted_zone_a_subnet_user_host_1', 'restricted_zone_a_subnet_user_host_2', 
        'restricted_zone_a_subnet_user_host_3', 'restricted_zone_a_subnet_user_host_4', 
        'restricted_zone_a_subnet_server_host_0', 'restricted_zone_a_subnet_server_host_1', 
        'restricted_zone_a_subnet_server_host_2'
    ])
    ```
From this output, we can tell that `blue_agent_0` is in-charge of protecting the restricted zone A subnet.

When printing out the observation contents of the first host, we can see it has the same keys as in the [red observation](#observable-hosts-dictionary). 
But this time with a blue agent user session.

```python linenums="20"
print("\nSingle Host: \n")
pprint(initial_obs[list(initial_obs.keys())[2]])
```
???+ quote "Code Output"
    ```
    Single Host: 

    {'Interface': [{'Subnet': IPv4Network('10.0.26.0/24'),
                    'interface_name': 'eth0',
                    'ip_address': IPv4Address('10.0.26.88')}],
    'Processes': [{'PID': 7519, 'username': 'ubuntu'}],
    'Sessions': [{'PID': 7519,
                'Type': <SessionType.UNKNOWN: 1>,
                'agent': 'blue_agent_0',
                'session_id': 2,
                'timeout': 0,
                'username': 'ubuntu'}],
    'System info': {'Architecture': <Architecture.x64: 2>,
                    'Hostname': 'restricted_zone_a_subnet_user_host_0',
                    'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                    'OSType': <OperatingSystemType.LINUX: 3>,
                    'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                    'position': array([0., 0.])},
    'User Info': [{'Groups': [{'GID': 0}], 'username': 'root'},
                {'Groups': [{'GID': 1}], 'username': 'user'}]}
    ```

### Uneventful Steps

Blue agents do the Monitor action every step as their 'end of turn' action. 
This means that they get feedback from the environment on what is happening to the hosts they have visibility of.

If no events are triggered, such as in the code below, nothing apart from the action and its success are returned in the observation space.

```python linenums="23"
obs_1 = cyborg.step(agent='blue_agent_0', action=Sleep()).observation

print("\nBlue Agent 0: Step #1 \n")
pprint(obs_1)
```
???+ quote "Code Output"
    ```
    Blue Agent 0: Step #1 

    {'action': Sleep, 'success': <TernaryEnum.UNKNOWN: 2>}
    ```
### Eventful Steps
When something does happen on a host that the blue agent has a session on, it can appear in its observation space.

In the example below, the false positive (fp) detection rate of the green agents have been set to `1.0` so that any action that could trigger a false positive security event will. This value can be set at any float but is usually set at 0.01.

This means there is now a high likelihood that something will appear in the agent's observation ...

```python linenums="28"
for agent_name, ai in cyborg.environment_controller.agent_interfaces.items():
    if 'green' in agent_name and isinstance(ai.agent, EnterpriseGreenAgent):
        ai.agent.fp_detection_rate = 1.0

obs_2 = cyborg.step(agent='blue_agent_0', action=Sleep()).observation

print("\nBlue Agent 0: Step #2 with Green False Positive \n")
pprint(obs_2)
```
???+ quote "Code Output"
    ```
    Blue Agent 0: Step #2 with Green False Positive 

    {'action': Sleep,
    'restricted_zone_a_subnet_user_host_4': {'Interface': [{'ip_address': IPv4Address('10.0.26.104')}],
                                            'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.26.104'),
                                                                            'local_port': 58063}]}],
                                            'System info': {'Architecture': <Architecture.x64: 2>,
                                                            'Hostname': 'restricted_zone_a_subnet_user_host_4',
                                                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                                                            'OSType': <OperatingSystemType.LINUX: 3>,
                                                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                                                            'position': array([0., 0.])}},
    'success': <TernaryEnum.UNKNOWN: 2>}
    ```

Just as in real-life, there may be false-positives or incorrect negatives. 
The monitor function may be triggered by green actions, as is the case in the code above, or it may miss a malicious red action.
It is the blue agents job to decide how it wants to react to these observations.
