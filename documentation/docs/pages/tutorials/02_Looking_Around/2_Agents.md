# Agents
There are a number of agent types available in CC4, with competitors getting to create even more!
In this tutorial, you will be introduced to some of them.

## Green Agent
### EnterpriseGreenAgent
CC4 only has one type of green agent, the EnterpriseGreenAgent, which is present on every host in the network. 
It represents a normal computer user and the majority of the rewards are derived from how the action or inaction of blue affects green, when red agents are also present.

The following example runs through all the actions that are taken by the green agents in the first step, and groups together according to action.

```python title="" linenums="1"
from pprint import pprint
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent

# Initialise the environment
steps = 1000
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)

# Perform one generic step of the episode
cyborg.step()

# Get the dictionary of actions performed during that step
action_list = cyborg.environment_controller.action

# Separate the actions out into their three groups for easy viewing
green_actions = {'Sleep': {}, 'GreenLocalWork': {}, 'GreenAccessService': {}}
for agent, action in action_list.items():
    if 'green' in agent:
        action_str = str(action[0]) 
        if 'Sleep' in action_str:
            green_actions['Sleep'][agent] = action
        if 'GreenLocalWork' in action_str:
            green_actions['GreenLocalWork'][agent] = action
        if 'GreenAccessService' in action_str:
            green_actions['GreenAccessService'][agent] = action

# Print the dictionary
pprint(green_actions)
```
??? quote "Code Output"
    ```
    {'GreenAccessService': {
        'green_agent_1': [GreenAccessService 10.0.74.254 8071],
        'green_agent_11': [GreenAccessService 10.0.90.252 2469],
        'green_agent_13': [GreenAccessService 10.0.183.252 3890],
        'green_agent_15': [GreenAccessService 10.0.86.253 5190],
        'green_agent_17': [GreenAccessService 10.0.183.254 1220],
        'green_agent_18': [GreenAccessService 10.0.183.252 3799],
        'green_agent_21': [GreenAccessService 10.0.177.254 5456],
        'green_agent_25': [GreenAccessService 10.0.86.253 9220],
        'green_agent_3': [GreenAccessService 10.0.177.253 5055],
        'green_agent_36': [GreenAccessService 10.0.74.252 8282],
        'green_agent_38': [GreenAccessService 10.0.183.251 5638],
        'green_agent_39': [GreenAccessService 10.0.86.253 5796],
        'green_agent_4': [GreenAccessService 10.0.183.253 5740],
        'green_agent_44': [GreenAccessService 10.0.74.254 8071],
        'green_agent_45': [GreenAccessService 10.0.177.253 5055]
    },
    'GreenLocalWork': {
        'green_agent_0': [GreenLocalWork 10.0.26.88],
        'green_agent_2': [GreenLocalWork 10.0.26.173],
        'green_agent_22': [GreenLocalWork 10.0.183.36],
        'green_agent_24': [GreenLocalWork 10.0.183.53],
        'green_agent_26': [GreenLocalWork 10.0.183.153],
        'green_agent_29': [GreenLocalWork 10.0.74.39],
        'green_agent_40': [GreenLocalWork 10.0.90.77],
        'green_agent_42': [GreenLocalWork 10.0.90.221],
        'green_agent_43': [GreenLocalWork 10.0.90.137],
        'green_agent_47': [GreenLocalWork 10.0.32.201],
        'green_agent_6': [GreenLocalWork 10.0.27.73],
        'green_agent_7': [GreenLocalWork 10.0.27.109],
        'green_agent_8': [GreenLocalWork 10.0.27.53],
        'green_agent_9': [GreenLocalWork 10.0.27.189]
    },
    'Sleep': {
        'green_agent_10': [Sleep],
        'green_agent_12': [Sleep],
        'green_agent_14': [Sleep],
        'green_agent_16': [Sleep],
        'green_agent_19': [Sleep],
        'green_agent_20': [Sleep],
        'green_agent_23': [Sleep],
        'green_agent_27': [Sleep],
        'green_agent_28': [Sleep],
        'green_agent_30': [Sleep],
        'green_agent_31': [Sleep],
        'green_agent_32': [Sleep],
        'green_agent_33': [Sleep],
        'green_agent_34': [Sleep],
        'green_agent_35': [Sleep],
        'green_agent_37': [Sleep],
        'green_agent_41': [Sleep],
        'green_agent_46': [Sleep],
        'green_agent_5': [Sleep]
        }
    }
    ```
There are 3 actions that an EnterpriseGreenAgent can take:

- [Sleep](../03_Actions/A_Understanding_Actions/3_Sleep.md)
- [GreenLocalWork](../../reference/actions/green_actions/local_work.md)
- [GreenAccessService](../../reference/actions/green_actions/access_service.md)

The string output of GreenLocalWork includes the IP address of the host where the local work is taking place, and the string output of GreenAccessService includes the destination IP address and port number.

During GreenLocalWork, another subaction called [PhishingEmail](../../reference/actions/green_actions/phishing_email.md) can also occur. However as a sub action this will not appear on the action list.


## Red Agents
CC4 has two main types of heuristic red agents: [RandomSelectRedAgent](../../reference/agents/RandomSelectRedAgent.md), and [FiniteStateRedAgent](../../reference/agents/FiniteStateRedAgent.md).


### RandomSelectRedAgent
This red agent does what it says on the tin, 'randomly selects'. 

For red agents, there are a [10 possible actions](../../reference/agents/red_overview.md#red-agent-actions), and this agent picks a random valid one from the list. Below is an example action list output from a RandomSelectRedAgent.

```python title="example_random_red.py" linenums="1"
from pprint import pprint
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, RandomSelectRedAgent

# Initialise environment
steps = 1000
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=RandomSelectRedAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)

# Record actions of red_agent_0
red_agent_0_actions = []
for i in range(10):
    cyborg.step()
    step_actions = cyborg.environment_controller.action
    red_agent_0_actions.append(step_actions['red_agent_0'])

# Print red_agent_0's actions
pprint(red_agent_0_actions)
```
???+ quote "Code Output"
    ```
    [[AggressiveServiceDiscovery 10.0.43.13],
    [DiscoverRemoteSystems 10.0.43.0/24],
    [PrivilegeEscalate contractor_network_subnet_user_host_5],
    [DegradeServices contractor_network_subnet_user_host_5],
    [Withdraw contractor_network_subnet_user_host_5],
    [Sleep],
    [Sleep],
    [Sleep],
    [Sleep],
    [Sleep]]
    ```

#### Agent Options
The agent has two additional options:

```python title="RandomSelectRedAgent.py" linenums="34"
self.print_output = False
self.disable_withdraw = False
```

If `print_output` is set to `True`, the example_random_red.py (minus the final two lines) would output the following:

???+ quote "Code Output"
    ```
    ** Turn 0 for red_agent_0 **
    Action: Initial Observation
    Action Success: UNKNOWN

    ** Turn 1 for red_agent_0 **
    Action: AggressiveServiceDiscovery 10.0.43.13
    Action Success: TRUE

    ** Turn 2 for red_agent_0 **
    Action: DiscoverRemoteSystems 10.0.43.0/24
    Action Success: TRUE

    ** Turn 3 for red_agent_0 **
    Action: PrivilegeEscalate contractor_network_subnet_user_host_5
    Action Success: TRUE

    ** Turn 4 for red_agent_0 **
    Action: DegradeServices contractor_network_subnet_user_host_5
    Action Success: TRUE


    *** red_agent_0 attempts to withdraw ***
    ```
This gives you much more visibility of what is happening, as you can tell what actions were successful.

You can tell that the final attempt to withdraw was successful as there are no turns after this.
To stop the agent trying to withdraw itself, you can set `disable_withdraw` to `True`.


### FiniteStateRedAgent
This section will cover how to use the FiniteStateRedAgent. If you want more information about its [design](../../reference/agents/red_overview.md#finite-state-machine-based-red-agents) or the ability to [make variants](../../reference/agents/red_overview.md#creating-variant-fsm-red-agents) of this agent, please use the links provided.

The code to show the FiniteStateRedAgent actions is almost identical to `example_random_red.py` for the RandomSelectRedAgent, with only the agent name and number of steps being changed.

```python title="example_fsm_red.py" linenums="1"
from pprint import pprint
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, RandomSelectRedAgent

# Initialise environment
steps = 1000
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)

# Record actions of red_agent_0
red_agent_0_actions = []
for i in range(20):
    cyborg.step()
    step_actions = cyborg.environment_controller.action
    red_agent_0_actions.append(step_actions['red_agent_0'])

# Print red_agent_0's actions
pprint(red_agent_0_actions)
```
???+ quote "Code Output"
    ```
    [[DiscoverRemoteSystems 10.0.43.0/24],
    [AggressiveServiceDiscovery 10.0.43.251],
    [DiscoverRemoteSystems 10.0.43.0/24],
    [Sleep],
    [Sleep],
    [Sleep],
    [Sleep],
    [StealthServiceDiscovery 10.0.43.253],
    [AggressiveServiceDiscovery 10.0.43.143],
    [AggressiveServiceDiscovery 10.0.43.61],
    [Sleep],
    [Sleep],
    [Sleep],
    [Sleep],
    [StealthServiceDiscovery 10.0.43.224],
    [Sleep],
    [Sleep],
    [ExploitRemoteService_cc4 10.0.43.61],
    [PrivilegeEscalate contractor_network_subnet_user_host_0],
    [Impact contractor_network_subnet_user_host_0]]
    ```
The resultant actions have a more logical sequence than the RandomSelectRedAgent, with the agent first exploring the environment with discovery actions before focusing on a target to gain privileges on and impact.

While the RandomSelectRedAgent should be easy to defeat or mitigate against, the FiniteStateRedAgent and its variants shold be a more difficult challenge.

#### Agent Options
There are a large amount of possible agent modifications for this agent; so many that a [FSM variant template](../../reference/agents/red_overview.md#creating-variant-fsm-red-agents) has been created to allow for better control and to reduce complexity.

However, three options have been left in the original. Two are for verbosity and one is for basic prioritisation.
```python title="FiniteStateRedAgent.py" linenums="50"
self.print_action_output = False
self.print_obs_output = False
self.prioritise_servers = False
```

Output verbosity can be scaled to either 'low', with only actions displayed, or 'high', with the environmental observation and internal agent logic also shown. 

Explore these two output options below:

=== "Output Actions Only"
    If you want to get a grasp of what the red agent is doing, without being overwhelmed by information - this is the option for you.

    Active red agents state:

    - Who they are
    - What step they are on internally
    - What there action for that step was
    - How successful the action was

    This make it easy to tell the progress agents are making and what agents are active.

    ??? quote "Code Output: print_action_output == True"
        ```
        ** Turn 0 for red_agent_0 **
        Action: Initial Observation
        Action Success: UNKNOWN

        ** Turn 1 for red_agent_0 **
        Action: DiscoverRemoteSystems 10.0.43.0/24
        Action Success: TRUE

        ** Turn 2 for red_agent_0 **
        Action: AggressiveServiceDiscovery 10.0.43.251
        Action Success: TRUE

        ** Turn 3 for red_agent_0 **
        Action: DiscoverRemoteSystems 10.0.43.0/24
        Action Success: TRUE

        ** Turn 4 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.253
        Action Success: IN_PROGRESS

        ** Turn 5 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.253
        Action Success: IN_PROGRESS

        ** Turn 6 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.253
        Action Success: IN_PROGRESS

        ** Turn 7 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.253
        Action Success: IN_PROGRESS

        ** Turn 8 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.253
        Action Success: TRUE

        ** Turn 9 for red_agent_0 **
        Action: AggressiveServiceDiscovery 10.0.43.143
        Action Success: TRUE

        ** Turn 10 for red_agent_0 **
        Action: AggressiveServiceDiscovery 10.0.43.61
        Action Success: TRUE

        ** Turn 11 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.224
        Action Success: IN_PROGRESS

        ** Turn 12 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.224
        Action Success: IN_PROGRESS

        ** Turn 13 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.224
        Action Success: IN_PROGRESS

        ** Turn 14 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.224
        Action Success: IN_PROGRESS

        ** Turn 15 for red_agent_0 **
        Action: StealthServiceDiscovery 10.0.43.224
        Action Success: TRUE

        ** Turn 16 for red_agent_0 **
        Action: ExploitRemoteService_cc4 10.0.43.61
        Action Success: IN_PROGRESS

        ** Turn 17 for red_agent_0 **
        Action: ExploitRemoteService_cc4 10.0.43.61
        Action Success: IN_PROGRESS

        ** Turn 18 for red_agent_0 **
        Action: ExploitRemoteService_cc4 10.0.43.61
        Action Success: TRUE

        ** Turn 19 for red_agent_0 **
        Action: PrivilegeEscalate contractor_network_subnet_user_host_0
        Action Success: TRUE
        ```
    ---
=== "Output Actions and Observations"

    This option gives you all the output you would possibly need to determine why the agent is doing what it is doing.
    As well as showing you the action information and observation output (as discussed in the [previous tutorial](1_Observations.md#observable-hosts-dictionary)), the 'host states' dictionary is also displayed.

    The host states represent the agent's internal knowledge level for each host it is aware of. The host is identified via its IP address and given a state, which determines what future actions can be made on that state. For more information on this mechanism, look at the [reference agent design documentation](../../reference/agents/red_overview.md#finite-state-machine-based-red-agents).

    The output that you get for the initial observation, and first two steps are shown below:

    ??? quote "Code Output: print_obs_output && print_action_output == True"
        ```
        ** Turn 0 for red_agent_0 **
        Action: Initial Observation
        Action Success: UNKNOWN

        Observation:
        {'contractor_network_subnet_user_host_5': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                                                'interface_name': 'eth0',
                                                                'ip_address': IPv4Address('10.0.43.13')}],
                                                'Processes': [{'PID': 9298,
                                                                'username': 'ubuntu'}],
                                                'Sessions': [{'PID': 9298,
                                                                'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'timeout': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Architecture': <Architecture.x64: 2>,
                                                                'Hostname': 'contractor_network_subnet_user_host_5',
                                                                'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                                                                'OSType': <OperatingSystemType.LINUX: 3>,
                                                                'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                                                                'position': array([0., 0.])},
                                                'User Info': [{'Groups': [{'GID': 0}],
                                                                'username': 'root'},
                                                                {'Groups': [{'GID': 1}],
                                                                'username': 'user'}]}}
        Host States:
        {'10.0.43.13': {'hostname': 'contractor_network_subnet_user_host_5',
                        'state': 'U'}}

        ** Turn 1 for red_agent_0 **
        Action: DiscoverRemoteSystems 10.0.43.0/24
        Action Success: TRUE

        Observation:
        {'10.0.43.129': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.129')}]},
        '10.0.43.13': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                    'ip_address': IPv4Address('10.0.43.13')}]},
        '10.0.43.130': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.130')}]},
        '10.0.43.143': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.143')}]},
        '10.0.43.224': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.224')}]},
        '10.0.43.251': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.251')}]},
        '10.0.43.252': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.252')}]},
        '10.0.43.253': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.253')}]},
        '10.0.43.254': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                        'ip_address': IPv4Address('10.0.43.254')}]},
        '10.0.43.61': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                    'ip_address': IPv4Address('10.0.43.61')}]},
        'contractor_network_subnet_user_host_5': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                                                'ip_address': IPv4Address('10.0.43.13')}],
                                                'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_5'}}}
        Host States:
        {'10.0.43.129': {'hostname': None, 'state': 'K'},
        '10.0.43.13': {'hostname': 'contractor_network_subnet_user_host_5',
                        'state': 'UD'},
        '10.0.43.130': {'hostname': None, 'state': 'K'},
        '10.0.43.143': {'hostname': None, 'state': 'K'},
        '10.0.43.224': {'hostname': None, 'state': 'K'},
        '10.0.43.251': {'hostname': None, 'state': 'K'},
        '10.0.43.252': {'hostname': None, 'state': 'K'},
        '10.0.43.253': {'hostname': None, 'state': 'K'},
        '10.0.43.254': {'hostname': None, 'state': 'K'},
        '10.0.43.61': {'hostname': None, 'state': 'K'}}

        ** Turn 2 for red_agent_0 **
        Action: AggressiveServiceDiscovery 10.0.43.251
        Action Success: TRUE

        Observation:
        {'10.0.43.251': {'Interface': [{'ip_address': IPv4Address('10.0.43.251')}],
                        'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.43.251'),
                                                        'local_port': 22}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.43.251'),
                                                        'local_port': 3390}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.43.251'),
                                                        'local_port': 80}]},
                                    {'Connections': [{'local_address': IPv4Address('10.0.43.251'),
                                                        'local_port': 25}]}]},
        'contractor_network_subnet_user_host_5': {'Interface': [{'Subnet': IPv4Network('10.0.43.0/24'),
                                                                'ip_address': IPv4Address('10.0.43.13')}],
                                                'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                                'agent': 'red_agent_0',
                                                                'session_id': 0,
                                                                'username': 'ubuntu'}],
                                                'System info': {'Hostname': 'contractor_network_subnet_user_host_5'}}}
        Host States:
        {'10.0.43.129': {'hostname': None, 'state': 'K'},
        '10.0.43.13': {'hostname': 'contractor_network_subnet_user_host_5',
                        'state': 'UD'},
        '10.0.43.130': {'hostname': None, 'state': 'K'},
        '10.0.43.143': {'hostname': None, 'state': 'K'},
        '10.0.43.224': {'hostname': None, 'state': 'K'},
        '10.0.43.251': {'hostname': None, 'state': 'S'},
        '10.0.43.252': {'hostname': None, 'state': 'K'},
        '10.0.43.253': {'hostname': None, 'state': 'K'},
        '10.0.43.254': {'hostname': None, 'state': 'K'},
        '10.0.43.61': {'hostname': None, 'state': 'K'}}
        ```
    ---

For the basic prioritisation option, you can choose to set the agent to prefer servers.

**Why:**
Impact is only successful on servers that run a specific operational service. Therefore, if you want the agent to focus on impacting as many servers as possible, prioritising servers is necessarty.

**How:**
If a server is known by the agent, there will be a 75% chance that the next action will happen on a server.

The source code for how this is achieved is shown below:

```python title="FiniteStateRedAgent.py" linenums="265"
if self.prioritise_servers and len(state_host_options) > 1:
    server_state_host_options = [h for h in state_host_options if self.host_states[h]['hostname'] is not None and 'server' in self.host_states[h]['hostname']] 
    if len(server_state_host_options) > 0:
        i = self.np_random.random()
        if i <= 0.75:
            chosen_host = self.np_random.choice(server_state_host_options)
        else:
            #pick other host type
            if not len(server_state_host_options) == len(state_host_options):
                non_server_state_host_options = [h for h in state_host_options if not h in server_state_host_options]
                chosen_host = self.np_random.choice(non_server_state_host_options)
            else:
                chosen_host = self.np_random.choice(server_state_host_options)
    else:
        chosen_host = self.np_random.choice(state_host_options)
else:
    chosen_host = self.np_random.choice(state_host_options)
```
## Blue Agents
The objective for competitors in CC4 is to create the best Blue agent possible. As such, there are no Blue agents provided in CC4.

## Other Agents
### Keyboard Agent

The KeyboardAgent allows a person to manually choose actions, acting as the brains of the agent. This is useful for getting familiar the scenario. However, the observation space is given in its raw dictionary form, which means that it can be hard to follow what is happening when given a large observation.

Here is how you would use it:

```python title="keyboard_agent_example.py" linenums="1"
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent, KeyboardAgent

steps = 1000
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, # use a stand-in agent that you will overwrite the actions of
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1234)

# Create the keyboard agent
agent = KeyboardAgent('blue_agent_0')
# Reset the environment
results = cyborg.reset()

for i in range(3):
    # Get the action and observation space
    obs = results.observation
    action_space = cyborg.get_action_space('blue_agent_0')

    # Prompt the keyboard agent to ask yoy for the action to take
    action = agent.get_action(obs, action_space)
    # Take a step using that action
    results = cyborg.step(agent='blue_agent_0', action=action)
```

And here is a snip-it of the output:

???+ quote "Code Output"
    ```
                                ...
                            'User Info': [{'Groups': [{'GID': 0}],
                                            'username': 'root'},
                                            {'Groups': [{'GID': 1}],
                                            'username': 'user'}]},
    'success': <TernaryEnum.UNKNOWN: 2>}

    ********************************* Turn 1: Command Selection **********************************

    0 AllowTrafficZone
    1 BlockTrafficZone
    2 Restore_cc4
    3 Remove_cc4
    4 DecoyHarakaSMPT_cc4
    5 DecoyApache_cc4
    6 DecoyTomcat_cc4
    7 DecoyVsftpd_cc4
    8 Analyse_cc4
    9 Monitor
    10 Sleep
    ----------------------------------------------------------------------------------------------
    CHOOSE A COMMAND: 5
    You chose DecoyApache_cc4.


    ******************************** Turn 1: Parameter Selection *********************************


    ------------------------------------- Session Selection --------------------------------------
    Automatically choosing 0 as it is the only option.
    -------------------------------------- Agent Selection ---------------------------------------
    Automatically choosing blue_agent_0 as it is the only option.
    ------------------------------------- Hostname Selection -------------------------------------
    0 restricted_zone_a_subnet_router
    1 restricted_zone_a_subnet_user_host_0
    2 restricted_zone_a_subnet_user_host_1
    3 restricted_zone_a_subnet_user_host_2
    4 restricted_zone_a_subnet_user_host_3
    5 restricted_zone_a_subnet_user_host_4
    6 restricted_zone_a_subnet_server_host_0
    7 restricted_zone_a_subnet_server_host_1
    8 restricted_zone_a_subnet_server_host_2
    ----------------------------------------------------------------------------------------------
    CHOOSE A PARAMETER: 5
    You chose restricted_zone_a_subnet_user_host_4.
    ----------------------------------------------------------------------------------------------
    ----------------------------------------------------------------------------------------------

    ************************************ Turn 2: BLUE_AGENT_0 ************************************

    ----------------------------------------------------------------------------------------------
    ----------------------------------------------------------------------------------------------

    ************************************ Turn 2: Observation *************************************

    {'success': <TernaryEnum.IN_PROGRESS: 4>}
    ----------------------------------------------------------------------------------------------
    Action is still executing...
    **********************************************************************************************
    ```
