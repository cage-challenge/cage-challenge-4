# Control Traffic Between Zones

In CC4, blue agents can make block and allow firewall rules to cut off parts of the network.

This is a risky move for blue, as green will penalise blue if it cannot perform remote actions (GreenAccessService). But it may be worth it to lower the risk of red infecting the network.

???+ info
    Red can still infect the cut off network via clicking on phishing emails. However this is a rare sub-action.

## BlockTrafficZone

Blocking traffic between two subnets is as simple as picking the two subnets and running the `BlockTrafficZone` action. 
Here is an example:

```python title="control_traffic_example.py" linenums="1"
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import BlockTrafficZone, AllowTrafficZone

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=SleepAgent, 
                                red_agent_class=SleepAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()

blue_agent_name = 'blue_agent_0'
action_space = cyborg.get_action_space(blue_agent_name)

action = BlockTrafficZone(session=0, agent=blue_agent_name, from_subnet='restricted_zone_a_subnet', to_subnet='restricted_zone_b_subnet')

results = cyborg.step(agent=blue_agent_name, action=action)
obs = results.observation
pprint(obs)
```

???+ quote "Code Output"
    ```
    {'action': BlockTrafficZone, 'success': <TernaryEnum.TRUE: 1>}
    ```

From the output, we can see that the action has been executed successfully.

## AllowTrafficZone

The `AllowTrafficZone` action will then reverse the firewall rule.

```python title="control_traffic_example.py" linenums="25"
action = AllowTrafficZone(session=0, agent=blue_agent_name, from_subnet='restricted_zone_a_subnet', to_subnet='restricted_zone_b_subnet')

results = cyborg.step(agent=blue_agent_name, action=action)
obs = results.observation
pprint(obs)
```

???+ quote "Code Output"
    ```
    {'action': AllowTrafficZone, 'success': <TernaryEnum.TRUE: 1>}
    ```

From the output, we can see that the action has been executed successfully.