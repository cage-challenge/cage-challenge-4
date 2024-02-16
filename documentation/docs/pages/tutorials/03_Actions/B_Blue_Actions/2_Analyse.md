
# Analyse 

`Analyse` checks for the occurance of malware, in the form of a file, on a single specified host.


## Executing Analyse 

The blue action `Analyse` should be executed when it is suspected that red agents have been active on the network. 

Refer to the previous action `Monitor` for more information about possible red behaviour alerts.

Below is an example of how to run the `Analyse` action:

```python title="example_analyse.py" linenums="1"
from pprint import pprint
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import Analyse

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=1000)
cyborg.reset()

blue_agent_name = 'blue_agent_0'
blue_action_space = cyborg.get_action_space(blue_agent_name)

action = Analyse(session=0, agent=blue_agent_name, hostname='restricted_zone_a_subnet_server_host_0')

results = cyborg.step(agent=blue_agent_name, action=action)
print("Step 1: ", results.observation)
results = cyborg.step(agent=blue_agent_name)
print("Step 2: ", results.observation)          
```

???+ quote "Code Output"
    ```
    Step 1:  {'success': <TernaryEnum.IN_PROGRESS: 4>}
    Step 2:  {'success': <TernaryEnum.TRUE: 1>, 'action': Analyse restricted_zone_a_subnet_server_host_0}
    ```

As you can see it takes two steps for the action to complete. This is due to action duration being added to CC4 as a way of disadvantaging high utility actions - similarly to how more valuable operations are normally harder/take more time in the real world.

However after a step, the observation space shows that the action is successful - yet there is no additional observation to return.

## Successful action after Red Agent performed Exploit Action
To catch a red agent adding malware to a host in the subnet, you can perform the analyse action repeatedly until you see activity.

Here is a basic script that iterably performs the analyse action for a certain number of steps.
```python
step = 2
while step < steps:
    results = cyborg.step(agent=blue_agent_name, action=action)
    step = step + 1
    new_obs = results.observation

pprint(new_obs)  
```

A possible output for the results of a red Exploit action is shown here:

???+ quote "Code Output Section"
    ```
    {'action': Analyse_cc4 restricted_zone_a_subnet_server_host_0,
    'restricted_zone_a_subnet_server_host_0': {'Files': [{'Density': 0.9,
                                                        'File Name': 'cmd.sh',
                                                        'Known File': <FileType.UNKNOWN: 1>,
                                                        'Known Path': <Path.TEMP: 5>,
                                                        'Path': '/tmp/'}]},
    'success': <TernaryEnum.TRUE: 1>}
    ```

The occurence of the malware `cmd.sh` indicates that an exploit was run to get a user shell on the host.

This is valuable intel that means that we may want to remove that user shell from the host before it gains root privileges, using the `Remove` action.

## Successful action after Red Agent performed PrivilegeEscalate Action
Let's also consider the successful action after the Red Agent performs `PrivilegeEscalate`.

???+ quote "Code Output"
    ```
    {'action': Analyse_cc4 restricted_zone_a_subnet_server_host_0,
    'restricted_zone_a_subnet_server_host_0': {'Files': [{'Density': 0.9,
                                                        'File Name': 'cmd.sh',
                                                        'Known File': <FileType.UNKNOWN: 1>,
                                                        'Known Path': <Path.TEMP: 5>,
                                                        'Path': '/tmp/'},
                                                        {'Density': 0.9,
                                                        'File Name': 'escalate.sh',
                                                        'Known File': <FileType.UNKNOWN: 1>,
                                                        'Known Path': <Path.TEMP: 5>,
                                                        'Path': '/tmp/'}]},
    'success': <TernaryEnum.TRUE: 1>} 
    ```

You can tell from the presence of the additional file `escalate.sh`, that the red has managed to get a root shell on the host. 
This means that the red agent has total control of that host, and the only way to get rid of red is to `Restore` the host.