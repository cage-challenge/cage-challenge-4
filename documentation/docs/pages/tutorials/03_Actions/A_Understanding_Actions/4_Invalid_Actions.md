
# Invalid Actions
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
???+ quote "Code Output"
    ```
    {'action': InvalidAction, 'success': <TernaryEnum.FALSE: 3>}
    ```
