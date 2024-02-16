
# Taking an Action

To construct an action, we choose (or import) an action class, then instantiate it by passing in the necessary parameters.

A fully commented example is shown below:

```python title="example_sleep_action.py" linenums="1"
# import pprint package to allow for better readability of the observation space
from pprint import pprint

# import CybORG as a package, and all the classes needed for this script
from CybORG import CybORG
from CybORG.Agents import SleepAgent
from CybORG.Simulator.Actions import Sleep

steps = 200     

# Initialising the scenario creator for CC4
sg = EnterpriseScenarioGenerator(
    blue_agent_class=SleepAgent,    # agent class used for the blue agents
    green_agent_class=SleepAgent,   # agent class used for the green agents
    red_agent_class=SleepAgent,     # agent class used for the red agents
    steps=steps                     # the number of steps to take for this episode
)

# Initialising the CybORG environment with the CC4 scenario generator and a fixed seed 
# (seed is optional and will be generated randomly if not supplied)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()


example_agent_name = 'blue_agent_0' # name of the agent that is going to take the action

example_action = Sleep() # action that the agent is going to take

# the environment takes a step with the given agent and action, and outputs the results from that step
results = cyborg.step(agent=example_agent_name, action=example_action)

# print the observations gained for that agent from that step
pprint(results.observation)
```

The printed observation for the example agent is shown here.
???+ quote "Code Output"
    ```
    {
        'action': Sleep, 
        'success': <TernaryEnum.UNKNOWN: 2> 
    }
    ```

`'success'` can come in four forms:

1. TRUE - the action was successful
2. UNKNOWN - it is not possible to know the success of the action / the action does not support 'success' types
3. FALSE - the action was unsuccessful
4. IN_PROGRESS - the action takes multiple steps and has not been completed yet.


???+ tip 
    The CybORG function `parallel_step()` allows you to define the actions that multiple agents should take in one step, and get returned all the observations for all the agents.