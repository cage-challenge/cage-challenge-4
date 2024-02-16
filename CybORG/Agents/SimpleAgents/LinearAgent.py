import inspect
from typing import Dict, Tuple
from pprint import pprint
from random import randint

from CybORG import CybORG
from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Shared.Enums import TernaryEnum
from CybORG.Simulator.Actions import Action, Sleep, InvalidAction


class LinearAgent(BaseAgent):
    """This agent will perform a list of actions, and either repeat them indefinately or Sleep. If no action list is given it will always Sleep.
    
    This agent is intended to help with stress testing and debugging, as it allows the tester to perform a series of specific actions that they have pre-listed.
    As actions sometimes require other action to have been performed successfully to function, this sequential execution makes it possible to test these actions.
    The agent can also be used to test that another type of agent is reacting correctly to a specif series of actions.

    Attributes
    ----------
    action_list : Dict[int : (Action, dict)]
        a list of actions, with parameters, to be executed sequentially.
    circular : bool
        if true, the list of actions will be repeated once the end is reached, otherwise the remaining actions will be Sleep
    step : int
        the agent's internal step counter (not accurate to the State)
    last_action : str
        the name of the previous action that was performed
    print_action_output : bool
        print the action and action success
    print_obs_output : bool
        print the observation from the action
    
    Example
    -------
    An action list could look like the following:

    ```python
    action_list = {
        0: PrivilegeEscalate(
            hostname='contractor_network_subnet_user_host_2', 
            session=0, 
            agent='red_agent_0'),
        1: DiscoverRemoteSystems(
            subnet=IPv4Network('10.0.0.1/24'), 
            session=0, 
            agent='red_agent_0'),
        2: AggressiveServiceDiscovery(
            session=0, 
            agent='red_agent_0', 
            ip_address=IPv4Address('10.0.0.2')
    }
    ```

    """

    def __init__(
        self, name: str, action_list: Dict[int, Tuple[Action, dict]] = None,
        circular: bool = True, print_action_output: bool = True, print_obs_output: bool = False):

        super().__init__(name)
        self.action_list = action_list
        self.circular = circular
        self.step = 0

        self.print_action_output = print_action_output
        self.print_obs_output = print_obs_output

    def get_action(self, observation, action_space):
        """Returns the next action from the action list, or Sleep."""
        if observation['success'] == TernaryEnum.IN_PROGRESS:
            return Sleep()

        if self.action_list == None:
            self.action_list = {0: Sleep()}

        if self.print_action_output:
            self.last_turn_summary(observation)
        
        if not self.step in self.action_list.keys() and self.circular:
            n = self.step % len(self.action_list.keys())
            if n in self.action_list.keys():
                action = self.action_list[n]
            else:
                action = Sleep()

        elif self.step in self.action_list.keys():
            action = self.action_list[self.step]

        else:
            action = Sleep()

        self.step += 1
        return action

    def last_turn_summary(self, observation: dict):
        """Prints action name, parameters, success and sometimes observation"""

        action_str = None
        if 'action' in observation.keys():
            action_str = str(observation['action'])
        else: 
            action_str = "Initial Observation"

        print(f'\n** Turn {self.step} for {self.name} **')
        print("Action: " + action_str)
        print("Action Success: " + str(observation['success']) )

        if self.print_obs_output:
            print("Observation:")
            pprint(observation)
        
        if isinstance(observation.get('action'), InvalidAction):
            pprint(observation['action'].error)

    def train(self, results):
        pass

    def set_initial_values(self, action_space, observation):
        pass

    def end_episode(self):
        pass

