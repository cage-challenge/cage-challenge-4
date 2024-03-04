---
hide:
  - toc
---

# Welcome to the CC4 Reference Documentation

## Environment

<div class="grid cards" markdown>

-   :material-wall:{ .lg .middle } __Scenario Creation__

    ---

    In order to spin up the CC4 CybORG environment, a number of creation classes are needed. These classes hold details about the different entity and agent objects that will be needed in the simulation.
    
    The class [EnterpriseScenarioGenerator](environment/scenario_creation/enterprise_scenario_generator.md) is specific to CC4 and holds all the details regarding how to create this challenge.


-   :material-door-open:{ .lg .middle } __Internal Objects__

    ---

    Once the simulation is up and running, there are a number of internal class objects that hold the majority of the simulation data and control the series of events that happen on each 'step' of the simulated episode.


-   :material-star-circle:{ .lg .middle } __Rewards__

    ---

    For the Blue agents to learn, they are given negative rewards according to what has taken place in the environment. For CC4, the [BlueRewardMachine](environment/outputs_and_rewards/blue_reward_machine.md) is in charge of calculating these rewards. 

    For more information about the specific rewards given, look through the CC4 [Challenge Details](../README.md#rewards).

-   :material-texture-box:{ .lg .middle } __Entities__

    ---

    Within the environment, there are lots of smaller classes that are used to give the scenario more depth. 
    
    These classes all inherit from the parent class [Entity](hosts_and_networking/entity.md).

</div>

## Outputs and Wrappers

<div class="grid cards" markdown>

-   :material-export:{ .lg .middle } __Environmental Outputs__

    ---

    After each step is taken, the CybORG environment outputs information about that step; including the observation space. This is used to train the blue agents.

-   :material-gift-outline:{ .lg .middle } __Wrappers__

    ---

    To facilitate the usage of the outputted data, wrappers can be used to augment the data. These can be written as an interface between CybORG and a machine learning library, or as an aid to make the environmental output more comprehendable to people. 
    
    While a few wrappers have been provided here, there are no restrictions around participants creating their own with development of additional wrappers being actively encouraged.

</div>

## Agents and Actions

<div class="grid cards" markdown>

-   :material-account-wrench-outline:{ .lg .middle } __Base Classes__

    ---

    These classes are parents of all the agents and actions in this simulation.


-   :material-incognito:{ .lg .middle } __Red Agents__

    ---

    Red agents are the attackers that are trying to take complete control of the network.
    They have 10 possible actions and there are a few different red agents available, with [FiniteRedAgent](agents/FiniteStateRedAgent.md) being the primary agent.

    This implementation is quite complex, therefore a [red overview](agents/red_overview.md) has been provided for more information.


-   :material-laptop-account:{ .lg .middle } __Green Agents__

    ---

    Green agents are the common users of the network, who are just trying to get work done while the invisible red and blue wars rage on. Blue agents need to avoid any impacts to the green agents' work, otherwise they will receive negative rewards.

    CC4 uses [EnterpriseGreenAgents](agents/green_agents.md), who do one of three things: work locally, access a remote service, or sleep (hopefully not on the clock!).

-   :material-shield-account:{ .lg .middle } __Blue Agents__

    ---

    Blue agents are the defender of the network, and the agents that competitors are trying to build. They have 8 actions (including Sleep) that they can use to identify and take back control of the network from Red.

</div>