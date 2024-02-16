## Understanding Actions
### The Action Space

Without the use of wrappers,  CybORG actions need to be constructed by the agent before being passed in. If you are not interested this, we suggest you skip to the [Wrapper tutorial](06_Wrappers.md).

The action space is updated every step and can returned from the environment using the `get_action_space` function. 
Because this dictionary is quite large, we will only print the keys below.

```python title="explore_action_space.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Agents import SleepAgent

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()

example_agent_name = 'red_agent_0'
example_action_space = cyborg.get_action_space(example_agent_name)

pprint(example_action_space.keys())

```

>Response:
>```
>dict_keys(
    ['action', 'allowed_subnets', 'subnet', 'ip_address', 
    'session', 'username', 'password', 'process', 'port', 
    'target_session', 'agent', 'hostname'])
>```

The CybORG action space is divided into "actions" and "parameters". Actions represent the use of specific cyber tools (for example, a network scanning tool like nmap), while parameters represent the inputs the tool requires to function (to scan the interfaces of a host with nmap, you need to provide the ip address of the host).

The "actions" are located under the `action` key in the `action_space` dictionary.

```python title="explore_action_space.py" linenums="22"

pprint(example_action_space['action'])

```
___
>Response:
>```
>{<class 'CybORG.Simulator.Actions.Action.Sleep'>: True,
 <class 'CybORG.Simulator.Actions.AbstractActions.DiscoverRemoteSystems.DiscoverRemoteSystems'>: True,
 <class 'CybORG.Simulator.Actions.AbstractActions.DiscoverNetworkServices.StealthServiceDiscovery'>: True,
 <class 'CybORG.Simulator.Actions.AbstractActions.DiscoverNetworkServices.AggressiveServiceDiscovery'>: True,
 <class 'CybORG.Simulator.Actions.AbstractActions.PrivilegeEscalate.PrivilegeEscalate'>: True,
 <class 'CybORG.Simulator.Actions.AbstractActions.Impact.Impact'>: True,
 <class 'CybORG.Simulator.Actions.AbstractActions.DegradeServices.DegradeServices'>: True,
 <class 'CybORG.Simulator.Actions.AbstractActions.DiscoverDeception.DiscoverDeception'>: True,
 <class 'CybORG.Simulator.Actions.ConcreteActions.Withdraw.Withdraw'>: True,
 <class 'CybORG.Simulator.Actions.ScenarioActions.EnterpriseActions.ExploitRemoteService_cc4'>: True}

>```

We can see that our actions are each custom classes that form the keys of the above dictionary. The values specify whether this action is currently valid. In Scenario 1b, this value will always be True.

The remaining keys in the scenario dictionary represent different classes of parameters. For example, if we examine the `ip_address` key we will get a dictionary whose keys are the various ip addresses on the network. The values are again booleans, which represents whether Red knows about this ip address or not.

```python title="explore_action_space.py" linenums="24"

pprint(example_action_space['ip_address'])

```
___
>Response:
>```
>{IPv4Address('10.0.20.9'): False,
 IPv4Address('10.0.20.30'): False,
 IPv4Address('10.0.20.38'): False,
 ...
 IPv4Address('10.0.96.73'): True,
 ...}
>```

### Taking an Action

To construct an action, we choose (or import) an action class, then instantiate it by passing in the necessary parameters.

```python title="example_sleep_action.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Simulator.Actions.Action import Sleep

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()

example_agent_name = 'blue_agent_0'
example_action_space = cyborg.get_action_space(example_agent_name)

example_action = Sleep()

results = cyborg.step(agent=example_agent_name, action=example_action)
pprint(results.observation)
```
___
>Response:
>```
>{
    'action': Sleep, 
    'success': <TernaryEnum.UNKNOWN: 2> 
}
>```
>
???+ tip
    `'success'` can come in four forms:

    1. TRUE - the action was successful
    2. UNKNOWN - it is not possible to know the success of the action / the action does not support 'success' types
    3. FALSE - the action was unsuccessful
    4. IN_PROGRESS - the action takes multiple steps and has not been completed yet.

### Sleep - The Universal Action

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

### Invalid Actions
If you create an action that doesn't make any sense within the current scenario, CybORG will accept it, but automatically convert it to an Invalid Action. These actions automatically give a reward of -0.1.

```python title="perform_an_invalid_action.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Simulator.Actions.AbstractActions.Analyse import Analyse

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()

example_agent_name = 'blue_agent_0'
example_action_space = cyborg.get_action_space(example_agent_name)

unknown_hostnames = [hn for hn, known in example_action_space['hostname'].items() if not known]
unknown_hostname = unknown_hostnames[0]

example_action = Analyse(0, example_agent_name, unknown_hostname)

results = cyborg.step(agent=example_agent_name, action=example_action)
pprint(results.observation)
```
___
>Response:
>```
>{'action': InvalidAction, 'success': <TernaryEnum.FALSE: 3>}
>```

## Blue Actions

We will now take a look at Blue Team's actions and how they interact with those of Red Team.

```python
env = CybORG(sg, agents={'Red':B_lineAgent()})
results = env.reset('Blue')
actions = results.action_space['action']

pprint([action.__name__ for action in actions if actions[action]])
```
___
>Response:
>```
>['Sleep', 'Monitor', 'Analyse', 'Remove', 'Misinform', 'Restore']
>```

### Monitor


```python title="blue_monitor_with_red.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import Monitor

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()

blue_agent_name = 'blue_agent_0'
blue_action_space = cyborg.get_action_space(blue_agent_name)

action = Monitor(0, blue_agent_name)
results = cyborg.step(agent=blue_agent_name, action=action)

step = 1
base_obs = results.observation

print(f"Step count: {step}")
pprint(base_obs)
```
???+ quote "Code Output"
    ```
    {'action': Monitor, 'success': <TernaryEnum.TRUE: 1>}
    ```

```python title="blue_monitor_with_red.py" linenums="28"

new_obs = base_obs

while new_obs == base_obs and step < steps:
    results = cyborg.step(agent=blue_agent_name, action=action)
    step = step + 1
    new_obs = results.observation

print(f"Step count: {step}")
pprint(new_obs)

```
??? quote "Code Output"
    ```
    Step count: 184
    {
        'action': Monitor,
        'restricted_zone_a_subnet_router': 
            {
                'Interface': [{'ip_address': IPv4Address('10.0.114.254')}],
                'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                                'remote_address': IPv4Address('10.0.96.73'),
                                                'remote_port': 22}]}],
                'System info': {'Architecture': <Architecture.x64: 2>,
                                'Hostname': 'restricted_zone_a_subnet_router',
                                'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                                'OSType': <OperatingSystemType.LINUX: 3>,
                                'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                                'position': array([0., 0.])}
            },
        'restricted_zone_a_subnet_server_host_0': 
            {
                'Interface': [{'ip_address': IPv4Address('10.0.114.254')}],
                'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                                'remote_address': IPv4Address('10.0.96.73'),
                                                'remote_port': 22}]},
                            {'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.96.73'),
                                                'remote_port': 59402}]},
                            {'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.96.73'),
                                                'remote_port': 58674}]},
                            {'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.96.73'),
                                                'remote_port': 58674}]},
                            {'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.96.73'),
                                                'remote_port': 58674}]},
                            {'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.96.73'),
                                                'remote_port': 58674}]},
                            {'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.96.73'),
                                                'remote_port': 58674}]},
                            {'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.96.73'),
                                                'remote_port': 58674}]},
                            {'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.96.73'),
                                                'remote_port': 58674}]},
                            {'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.96.73'),
                                                'remote_port': 58674}]},
                            {'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.96.73'),
                                                'remote_port': 58674}]},
                            {'Connections': [{'local_address': IPv4Address('10.0.114.254'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.96.73'),
                                                'remote_port': 58674}]},
                            {'PID': 8268}],
                'System info': {'Architecture': <Architecture.x64: 2>,
                                'Hostname': 'restricted_zone_a_subnet_server_host_0',
                                'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                                'OSType': <OperatingSystemType.LINUX: 3>,
                                'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                                'position': array([0., 0.])}
        },
        'success': <TernaryEnum.TRUE: 1>
    }
    ```

>```python title="blue_monitor_with_green.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import Monitor

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()

blue_agent_name = 'blue_agent_0'
blue_action_space = cyborg.get_action_space(blue_agent_name)

action = Monitor(0, blue_agent_name)
results = cyborg.step(agent=blue_agent_name, action=action)

step = 1
base_obs = results.observation
new_obs = base_obs

while new_obs == base_obs and step < steps:
    results = cyborg.step(agent=blue_agent_name, action=action)
    step = step + 1
    new_obs = results.observation

print(f"Step count: {step}")
pprint(new_obs)
```
>??? quote "Code Output"
    ```shell
    Step count: 10
    {'action': Monitor,
    'restricted_zone_a_subnet_user_host_9': {'Interface': [{'ip_address': IPv4Address('10.0.114.165')}],
                                            'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.114.165'),
                                                                            'local_port': 56476}]}],
                                            'System info': {'Architecture': <Architecture.x64: 2>,
                                                            'Hostname': 'restricted_zone_a_subnet_user_host_9',
                                                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                                                            'OSType': <OperatingSystemType.LINUX: 3>,
                                                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                                                            'position': array([0., 0.])}},
    'success': <TernaryEnum.TRUE: 1>}
    ```

### Analyse

As explained by the [Observation tutorial](02_Observations.ipynb), the `Analyse` action can detect malware files on a single host. This mimics the use of a malware-detection tool such as DensityScout. Like all of Blue's actions, it requires a hostname parameter.

We can see below that the action discovers malware on `User1` as well as the passive monitoring picking up an exploit used on `Enterprise1`.

```python
action = Analyse(hostname='User1',session=0,agent='Blue')

for i in range(2):
    results = env.step(action=action,agent='Blue')
    obs = results.observation
    if i == 1:
        pprint(obs)
```
___
>Response:
<details>
<summary>Expand long response</summary>
```
{'Enterprise1': {'Interface': [{'IP Address': IPv4Address('10.0.154.215')}],
                 'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.154.215'),
                                                 'remote_address': IPv4Address('10.0.229.195'),
                                                 'remote_port': 80}]},
                               {'Connections': [{'local_address': IPv4Address('10.0.154.215'),
                                                 'local_port': 80,
                                                 'remote_address': IPv4Address('10.0.229.195'),
                                                 'remote_port': 49750}]},
                               {'Connections': [{'local_address': IPv4Address('10.0.154.215'),
                                                 'local_port': 57134,
                                                 'remote_address': IPv4Address('10.0.229.195'),
                                                 'remote_port': 4444}],
                                'PID': 4409}],
                 'System info': {'Architecture': <Architecture.x64: 2>,
                                 'Hostname': 'Enterprise1',
                                 'OSDistribution': <OperatingSystemDistribution.WINDOWS_SVR_2008: 4>,
                                 'OSType': <OperatingSystemType.WINDOWS: 2>,
                                 'OSVersion': <OperatingSystemVersion.W6_1_7601: 13>,
                                 'position': (30, 45)}},
 'User0': {'Interface': [{'IP Address': IPv4Address('10.0.154.215')}],
           'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.154.215'),
                                           'remote_address': IPv4Address('10.0.229.195'),
                                           'remote_port': 80}]}],
           'System info': {'Architecture': <Architecture.x64: 2>,
                           'Hostname': 'User0',
                           'OSDistribution': <OperatingSystemDistribution.WINDOWS_SVR_2008: 4>,
                           'OSType': <OperatingSystemType.WINDOWS: 2>,
                           'OSVersion': <OperatingSystemVersion.W6_1_7601: 13>,
                           'position': (28, 30)}},
 'User1': {'Files': [{'Density': 0.9,
                      'File Name': 'cmd.exe',
                      'Known File': <FileType.UNKNOWN: 1>,
                      'Known Path': <Path.TEMP: 5>,
                      'Path': 'C:\\temp\\',
                      'Signed': False},
                     {'Density': 0.9,
                      'File Name': 'escalate.exe',
                      'Known File': <FileType.UNKNOWN: 1>,
                      'Known Path': <Path.TEMP: 5>,
                      'Path': 'C:\\temp\\',
                      'Signed': False}]},
 'success': <TrinaryEnum.TRUE: 1>}
```
</details>

### Remove

The `Remove` action allows Blue Team to remove any of Red's user-level shells, simulating the act of killing it as a process. It will not remove a privileged shell. This is because privileged shells in Scenario1b are assumed to be persistent, meaning that if you remove them they will immediately come back.

We can see below that the Red agent attempts to `PrivilegeEscalate`, but this fails as its shell has been killed. The next turn it has to re-exploit the machine. Notice the use of the `get_last_action` method to work out what Red's last move was.

```python
action = Remove(hostname='Enterprise1', session=0, agent='Blue')

for i in range(2):
    results = env.step(action=action,agent='Blue')
    obs = results.observation
    pprint(obs)
    print(73*'-')
    print(env.get_last_action('Red'))
    print(73*'*')
```
___
>Response:
<details>
<summary>Expand long response</summary>
```
{'success': <TrinaryEnum.TRUE: 1>}
 -------------------------------------------------------------------------
 PrivilegeEscalate Enterprise0
 *************************************************************************
  {'Enterprise1': {'Interface': [{'IP Address': IPv4Address('10.0.154.215')}],
                 'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.154.215'),
                                                 'remote_address': IPv4Address('10.0.229.195'),
                                                 'remote_port': 3389}]},
                               {'Connections': [{'local_address': IPv4Address('10.0.154.215'),
                                                 'local_port': 3389,
                                                 'remote_address': IPv4Address('10.0.229.195'),
                                                 'remote_port': 49857}]},
                               {'Connections': [{'local_address': IPv4Address('10.0.154.215'),
                                                 'local_port': 51530,
                                                 'remote_address': IPv4Address('10.0.229.195'),
                                                 'remote_port': 4444}],
                                'PID': 4407}],
                 'System info': {'Architecture': <Architecture.x64: 2>,
                                 'Hostname': 'Enterprise1',
                                 'OSDistribution': <OperatingSystemDistribution.WINDOWS_SVR_2008: 4>,
                                 'OSType': <OperatingSystemType.WINDOWS: 2>,
                                 'OSVersion': <OperatingSystemVersion.W6_1_7601: 13>,
                                 'position': (30, 45)}},
 'User0': {'Interface': [{'IP Address': IPv4Address('10.0.154.215')}],
           'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.154.215'),
                                           'remote_address': IPv4Address('10.0.229.195'),
                                           'remote_port': 3389}]}],
           'System info': {'Architecture': <Architecture.x64: 2>,
                           'Hostname': 'User0',
                           'OSDistribution': <OperatingSystemDistribution.WINDOWS_SVR_2008: 4>,
                           'OSType': <OperatingSystemType.WINDOWS: 2>,
                           'OSVersion': <OperatingSystemVersion.W6_1_7601: 13>,
                           'position': (28, 30)}},
 'success': <TrinaryEnum.TRUE: 1>}
 -------------------------------------------------------------------------
 ExploitRemoteService 10.0.154.215
 *************************************************************************
```
</details>

### Restore

The `Restore` action represents reverting the system to a known baseline. This will restore a host to the state it was at the beginning of the game. This will wipe all of Red's shells away, with the notable exception of Red's starting host `User0`, which has been baselined into the system. Although `Restore` is more powerful than `Remove`, it necessarily causes some disruption on the network, so has a large negative penalty associated by using it.

Below we can see that the `Analyse` action detects malware on `User1`, but this disappears after restore has been used.

```python
for i in range(10):
    env.step() # So Red's actions don't interfere

action = Analyse(hostname='User1', session=0, agent='Blue')
results = env.step(action=action,agent='Blue')
obs = results.observation
pprint(obs)
    
action = Restore(hostname='User1', session=0, agent='Blue')
results = env.step(action=action,agent='Blue')
obs = results.observation
pprint(obs)

action = Analyse(hostname='User1', session=0, agent='Blue')
obs = results.observation
pprint(obs)
```
___
>Response:
<details>
<summary>Expand long response</summary>
```
{'Op_Server0': {'Interface': [{'IP Address': IPv4Address('10.0.104.21')}],
                'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 56752}]}],
                'System info': {'Architecture': <Architecture.x64: 2>,
                                'Hostname': 'Op_Server0',
                                'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                                'OSType': <OperatingSystemType.LINUX: 3>,
                                'OSVersion': <OperatingSystemVersion.U18_04_3: 6>,
                                'position': (63, 75)}},
 'User1': {'Files': [{'Density': 0.9,
                      'File Name': 'cmd.exe',
                      'Known File': <FileType.UNKNOWN: 1>,
                      'Known Path': <Path.TEMP: 5>,
                      'Path': 'C:\\temp\\',
                      'Signed': False},
                     {'Density': 0.9,
                      'File Name': 'escalate.exe',
                      'Known File': <FileType.UNKNOWN: 1>,
                      'Known Path': <Path.TEMP: 5>,
                      'Path': 'C:\\temp\\',
                      'Signed': False}]},
 'success': <TrinaryEnum.TRUE: 1>}
 {'Op_Server0': {'Interface': [{'IP Address': IPv4Address('10.0.104.21')}],
                'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 55950}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 49555,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 4444}],
                               'PID': 1102}],
                'System info': {'Architecture': <Architecture.x64: 2>,
                                'Hostname': 'Op_Server0',
                                'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                                'OSType': <OperatingSystemType.LINUX: 3>,
                                'OSVersion': <OperatingSystemVersion.U18_04_3: 6>,
                                'position': (63, 75)}},
 'success': <TrinaryEnum.TRUE: 1>}
 {'Op_Server0': {'Interface': [{'IP Address': IPv4Address('10.0.104.21')}],
                'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 55950}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 22,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 49555}]},
                              {'Connections': [{'local_address': IPv4Address('10.0.104.21'),
                                                'local_port': 49555,
                                                'remote_address': IPv4Address('10.0.229.195'),
                                                'remote_port': 4444}],
                               'PID': 1102}],
                'System info': {'Architecture': <Architecture.x64: 2>,
                                'Hostname': 'Op_Server0',
                                'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                                'OSType': <OperatingSystemType.LINUX: 3>,
                                'OSVersion': <OperatingSystemVersion.U18_04_3: 6>,
                                'position': (63, 75)}},
 'success': <TrinaryEnum.TRUE: 1>}
```
</details>




## Red Actions

We will now take a detailed look at Red Team's actions and understand what they do. Red's actions are listed below:

```python
pprint([action.__name__ for action in actions if actions[action]])
```
___
>Response:
>```
>['Sleep',
 'DiscoverRemoteSystems',
 'DiscoverNetworkServices',
 'ExploitRemoteService',
 'BlueKeep',
 'EternalBlue',
 'FTPDirectoryTraversal',
 'HarakaRCE',
 'HTTPRFI',
 'HTTPSRFI',
 'SQLInjection',
 'RemoteCodeExecutionOnSMTP',
 'PrivilegeEscalate',
 'Impact',
 'SSHBruteForce']
>```

### Sleep

The `Sleep` action does nothing and requires no parameters.

```python
from CybORG.Simulator.Actions import *

action = Sleep()
results = env.step(action=action,agent='Red')
print(results.observation)
```
___
>Response:
>```
>{'success': <TrinaryEnum.UNKNOWN: 2>}
>```

### DiscoverRemoteSystems

The `DiscoverRemoteSystems` action represents a ping sweep and takes in a subnet parameter to return all ips active on that subnet. Note how we pull the 

```python
subnets = action_space['subnet']
known_subnets = [subnet for subnet in subnets if subnets[subnet]]
subnet = known_subnets[0]

action = DiscoverRemoteSystems(subnet = subnet, session=0,agent='Red')
results = env.step(action=action,agent='Red')
pprint(results.observation)
```
___
>Response:
>```
>{'10.0.150.161': {'Interface': [{'IP Address': IPv4Address('10.0.150.161'),
                                 'Subnet': IPv4Network('10.0.150.160/28')}]},
 '10.0.150.163': {'Interface': [{'IP Address': IPv4Address('10.0.150.163'),
                                 'Subnet': IPv4Network('10.0.150.160/28')}]},
 '10.0.150.168': {'Interface': [{'IP Address': IPv4Address('10.0.150.168'),
                                 'Subnet': IPv4Network('10.0.150.160/28')}]},
 '10.0.150.170': {'Interface': [{'IP Address': IPv4Address('10.0.150.170'),
                                 'Subnet': IPv4Network('10.0.150.160/28')}]},
 '10.0.150.172': {'Interface': [{'IP Address': IPv4Address('10.0.150.172'),
                                 'Subnet': IPv4Network('10.0.150.160/28')}]},
 'success': <TrinaryEnum.TRUE: 1>}
>```

### DiscoverNetworkServices

The `DiscoverNetworkServices` action represents a port scan and takes in an ip address parameter to return a list of open ports and their respective services. These will be represented in the observation as new connections. The Red team must have discovered the ip address using the `DiscoverRemoteSystems` action in order for this action to succeed.

```python
known_ips = [ip for ip in ips if ips[ip]]
ip = random.choice(known_ips)
action = DiscoverNetworkServices(ip_address=ip,session=0,agent='Red')

results = env.step(action=action,agent='Red')
pprint(results.observation)
```
___
>Response:
>```
>{'10.0.150.172': {'Interface': [{'IP Address': IPv4Address('10.0.150.172')}],
                  'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.150.172'),
                                                  'local_port': 445}]},
                                {'Connections': [{'local_address': IPv4Address('10.0.150.172'),
                                                  'local_port': 139}]},
                                {'Connections': [{'local_address': IPv4Address('10.0.150.172'),
                                                  'local_port': 135}]},
                                {'Connections': [{'local_address': IPv4Address('10.0.150.172'),
                                                  'local_port': 3389}]}]},
 'success': <TrinaryEnum.TRUE: 1>}
>```

### ExploitRemoteService

The `ExploitRemoteService` action represents the use of a service exploit to obtain a reverse shell on the host. It requires an ip address as an input parameter and creates a new shell on the target host. 

CybORG actually models several different types of real-world exploits and this action chooses between them depending on the services available and the operating system of the host. This action will only ever succeed if the host's ip address has been discovered by Red team.

Usually the shell created by this action will be a shell with user privileges, but some exploits, such as EternalBlue, give SYSTEM access to a Windows machine. In this case, performing the Privilege Escalation action afterwards is unnecessary, although our rules-based agents always will.

```python
action = ExploitRemoteService(ip_address=ip,session=0,agent='Red')

results = env.step(action=action,agent='Red')
pprint(results.observation)
```
___
>Response:
>```
>{'10.0.150.161': {'Interface': [{'IP Address': IPv4Address('10.0.150.161')}],
                  'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.150.161'),
                                                  'local_port': 4444,
                                                  'remote_address': IPv4Address('10.0.150.172'),
                                                  'remote_port': 58218}],
                                 'Process Type': <ProcessType.REVERSE_SESSION_HANDLER: 10>}]},
 '10.0.150.172': {'Interface': [{'IP Address': IPv4Address('10.0.150.172')}],
                  'Processes': [{'Connections': [{'Status': <ProcessState.OPEN: 2>,
                                                  'local_address': IPv4Address('10.0.150.172'),
                                                  'local_port': 3389}],
                                 'Process Type': <ProcessType.RDP: 9>},
                                {'Connections': [{'local_address': IPv4Address('10.0.150.172'),
                                                  'local_port': 58218,
                                                  'remote_address': IPv4Address('10.0.150.161'),
                                                  'remote_port': 4444}],
                                 'Process Type': <ProcessType.REVERSE_SESSION: 11>}],
                  'Sessions': [{'Agent': 'Red',
                                'session_id': 1,
                                'Type': <SessionType.RED_REVERSE_SHELL: 11>}],
                  'System info': {'Hostname': 'User2',
                                  'OSType': <OperatingSystemType.WINDOWS: 2>}},
 'success': <TrinaryEnum.TRUE: 1>}
>```

### PrivilegeEscalate

The `PrivilegeEscalate` represents the use of malware to establish a privileged shell with root (Linux) or SYSTEM (Windows) privileges. This action requires a user shell to be on the target host.

This action has the potential to reveal information about hosts on other subnets, which can then be scanned and exploited.

```python
hostname = results.observation[str(ip)]['System info']['Hostname']
action = PrivilegeEscalate(hostname=hostname,session=0,agent='Red')

results = env.step(action=action,agent='Red')
pprint(results.observation)
```
___
>Response:
>```
>{'Enterprise1': {'Interface': [{'IP Address': IPv4Address('10.0.199.185')}]},
 'User2': {'Interface': [{'IP Address': IPv4Address('10.0.150.172'),
                          'Interface Name': 'eth0',
                          'Subnet': IPv4Network('10.0.150.160/28')}],
           'Sessions': [{'Agent': 'Red',
                         'session_id': 1,
                         'Type': <SessionType.RED_REVERSE_SHELL: 11>,
                         'Username': 'SYSTEM'}]},
 'success': <TrinaryEnum.TRUE: 1>}
>```

### Impact

The `Impact` action represents the degredation of services. It requires a hostname input parameter, but will only work on the `OpServer0` host on the Operational subnet and needs to be continually run in order to have an ongoing effect.

```python
from CybORG.Agents import B_lineAgent

results = env.reset(agent='Red')
obs = results.observation
action_space = results.action_space
agent = B_lineAgent()

while True:
    action = agent.get_action(obs,action_space)
    results = env.step(action=action,agent='Red')
    obs = results.observation
    
    if action.__class__.__name__ == 'Impact':
        print(action)
        print(obs)
        break
```
___
>Response:
>```
>Impact Op_Server0
 {'success': <TrinaryEnum.TRUE: 1>}
>```

## Green Actions