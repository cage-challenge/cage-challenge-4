---
hide:
  - toc
---

# Visualisation
CC4 does not have a supported rendered, however it does have a visualisation module. This allows the user to produce an interactive diagram of what is happening to nodes on the network, regarding red shell sessions.


First the environment needs to be set up:

```python title="visualise_cc4.py" linenums="1"
from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, DiscoveryFSRed
from CybORG.render.visualisation.VisualiseRedExpansion import VisualiseRedExpansion

steps = 200
sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=DiscoveryFSRed,
                                steps=steps)
cyborg = CybORG(scenario_generator=sg, seed=7629)
```

You can then run the visualisation internally, where the steps are handled for you, or record the visualisations for each step and display it at the end.

=== "Run internally"
    ```python title="visualise_cc4.py" linenums="13"
    visualise = VisualiseRedExpansion(cyborg, steps)
    visualise.run()
    ```

=== "Visualise step-by-step"
    ```python title="visualise_cc4.py" linenums="13"

    cyborg.reset()
    visualise = VisualiseRedExpansion(cyborg, steps)

    for i in range(steps):
        # Whatever you want to do before each step
        cyborg.step()
        # Whatever you want to do after each step

        # Make a record of the environment state for the visualisation
        visualise.visualise_step()

    # Whatever you want to do once the episode is finished ...

    # Visualise the episode
    visualise.show_graph()
    ```

## Visualisation Output
  The visualisation consists of a network graph with a key, and a step scroll bar along the bottom to change the step displayed.
  
  There are 4 control buttons:

  - '<' is step back
  - '>' is step forwards
  - 'P' is step through episode (play)
  - '||' is pause the play

=== "Step 0"
    Looking at the environment, there are 8 subnets divided between 4 'zones'. 
    There are also 5 blue agents spread between 3 of the zones, and no blue agent in the contractor network (CN).
    
    Initially there is only one red agent located in the contractor network, which has compromised a single user-level host.
    The rest of the network is compromise free ... but not for long!

    <figure markdown>
      <img src="/assets/CC4_Visualisation_0.png" alt="CC4 Visualisation at step 0" width="1000">
    </figure>


=== "Step 20"
    <figure markdown>
      <img src="/assets/CC4_Visualisation_20.png" alt="CC4 Visualisation at step 0" width="1000">
      <figcaption>Figure 1 - CC4 Visualisation at step 20</figcaption>
    </figure>

=== "Step 100"
    <figure markdown>
      <img src="/assets/CC4_Visualisation_100.png" alt="CC4 Visualisation at step 0" width="1000">
      <figcaption>Figure 1 - CC4 Visualisation at step 100</figcaption>
    </figure>