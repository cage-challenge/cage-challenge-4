# The Action Space

Without the use of wrappers,  CybORG actions need to be constructed by the agent before being passed in.

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

???+ quote "Code Output"
    ```shell
    dict_keys(
        ['action', 'allowed_subnets', 'subnet', 'ip_address', 
        'session', 'username', 'password', 'process', 'port', 
        'target_session', 'agent', 'hostname'])
    ```

The CybORG action space is divided into "actions" and "parameters". Actions represent the use of specific cyber tools (for example, a network scanning tool like nmap), while parameters represent the inputs the tool requires to function (to scan the interfaces of a host with nmap, you need to provide the ip address of the host).

The "actions" are located under the `action` key in the `action_space` dictionary.

```python title="explore_action_space.py" linenums="22"

pprint(example_action_space['action'])

```
???+ quote "Code Output"
    ```shell
    {<class 'CybORG.Simulator.Actions.Action.Sleep'>: True,
    <class 'CybORG.Simulator.Actions.AbstractActions.DiscoverRemoteSystems.DiscoverRemoteSystems'>: True,
    <class 'CybORG.Simulator.Actions.AbstractActions.DiscoverNetworkServices.StealthServiceDiscovery'>: True,
    <class 'CybORG.Simulator.Actions.AbstractActions.DiscoverNetworkServices.AggressiveServiceDiscovery'>: True,
    <class 'CybORG.Simulator.Actions.AbstractActions.PrivilegeEscalate.PrivilegeEscalate'>: True,
    <class 'CybORG.Simulator.Actions.AbstractActions.Impact.Impact'>: True,
    <class 'CybORG.Simulator.Actions.AbstractActions.DegradeServices.DegradeServices'>: True,
    <class 'CybORG.Simulator.Actions.AbstractActions.DiscoverDeception.DiscoverDeception'>: True,
    <class 'CybORG.Simulator.Actions.ConcreteActions.Withdraw.Withdraw'>: True,
    <class 'CybORG.Simulator.Actions.ScenarioActions.EnterpriseActions.ExploitRemoteService_cc4'>: True}

    ```

We can see that our actions are each custom classes that form the keys of the above dictionary. The values specify whether this action is currently valid. 

The remaining keys in the scenario dictionary represent different classes of parameters. For example, if we examine the `ip_address` key we will get a dictionary whose keys are the various ip addresses on the network. The values are again booleans, which represents whether Red knows about this ip address or not.

```python title="explore_action_space.py" linenums="24"

pprint(example_action_space['ip_address'])

```
???+ quote "Code Output"
    ```shell
    {IPv4Address('10.0.20.9'): False,
    IPv4Address('10.0.20.30'): False,
    IPv4Address('10.0.20.38'): False,
    ...
    IPv4Address('10.0.96.73'): True,
    ...}
    ```
