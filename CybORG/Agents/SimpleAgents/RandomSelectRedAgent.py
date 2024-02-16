import inspect
from pprint import pprint
from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Simulator.Actions.ConcreteActions.Withdraw import Withdraw

from ipaddress import IPv4Network

class RandomSelectRedAgent(BaseAgent):
    """ Red Agent that random selects an action (with parameters) to execute.

    Attributes
    ----------
    step : int
        number of steps the agent has taken in the environment
    last_action : str or Action
        the previous action that was executed
    print_output : bool
        option as to if action info is printed to the terminal
    disable_withdraw : bool
        when true, the Withdraw action is removed from the list of possible actions, so that the agent will no longer perform Withdraw.

    Other Parameters
    ----------------
    name : str
        name of the agent
    np_random : numpy.random._generator.Generator
        numpy random generator initialised on creation of scenario. This allows for the seed to be consistent with the CybORG() seed parameter
    """

    def __init__(self, name: str, np_random):
        super().__init__(name, np_random=np_random)
        self.step = 0
        self.last_action = "Initial Observation"
        self.print_output = False
        self.disable_withdraw = False

    def get_action(self, observation, action_space):
        """Chooses a valid action randomly from the action space, along with corresponding parameters - picked randomly when given options.
        
        Parameters
        ----------
        observation : dict
            agent observation from last action
        action_space : dict
            agent action space

        Raises
        ------
        ValueError
            There are no valid actions for the agent to take. Sleep should always be a valid action, so will only occur in error.
        """
        if self.print_output:
            self.last_turn_summary(observation)
        
        action = None
        valid_commands = self._get_valid_commands(action_space)
        list_commands = list(valid_commands.keys())

        if self.disable_withdraw:
            list_commands.remove('Withdraw')

        valid_action = False
        while not valid_action:
            if len(list_commands) == 0:
                raise ValueError("No valid commands")
            else:
                valid_action = True
                command_opt_num = self.np_random.integers(0, len(list_commands))
                command_opt = list_commands.pop(command_opt_num)
                param_dict = valid_commands[command_opt]
                command = param_dict.pop('command')

                chosen_params = {}
                for param_name, param_opts in param_dict.items():
                    if len(param_opts) == 0:
                        valid_action = False
                        break
                    elif len(param_opts) == 1:
                        chosen_params[param_name] = param_opts[0]
                    else:
                        param_opt_num = self.np_random.integers(0, len(param_opts))
                        param_choice = param_opts[param_opt_num]
                        chosen_params[param_name] = param_choice
                
                action = command(**chosen_params)

        self.last_action = action
        if self.print_output and isinstance(self.last_action, Withdraw):
            print(f"\n*** {self.name} attempts to withdraw ***\n")

        self.step += 1
        return action

    def last_turn_summary(self, observation: dict):
        """Prints action name, parameters and success"""

        print(f'** Turn {self.step} for {self.name} **')
        print("Action: " + str(self.last_action))
        print("Action Success: " + str(observation['success']) )
        print()

    def _get_valid_commands(self, action_space: dict):
        """ Get a dictionary of valid commands with valid argument options.

        For each possible action, get the corresponding argument name. Ignore aguments 'self' and 'priority'. Get argument options per command from action_space and filter by validity.

        Parameter
        ---------
        action_space: dict(dict)
            Agent's current action_space

        Returns
        -------
        valid_commands : dict
            Dictionary of valid commands with argument options
        """
        
        valid_commands = {}
        for command in action_space['action'].keys():
            parameter_list = inspect.getfullargspec(command).args 
            parameter_dict = {}
            for parameter in parameter_list:
                if parameter == 'self':
                    continue
                if parameter == 'priority':
                    continue

                option_dict = action_space[parameter]
                filter_f = lambda key : option_dict[key]
                valid_options = list(filter(filter_f,option_dict.keys()))
                if not valid_options:
                    break
                parameter_dict[parameter] = valid_options

            else:
                parameter_dict['command'] = command
                valid_commands[command.__name__] = parameter_dict

        return valid_commands

    def train(self, results):
        pass

    def set_initial_values(self, action_space, observation):
        pass

    def end_episode(self):
        pass
