from inspect import signature
from typing import Union, List, Dict
from pprint import pprint
from ipaddress import IPv4Address
from numpy import invert

from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Simulator.Actions.AbstractActions import DiscoverRemoteSystems, PrivilegeEscalate, Impact, DegradeServices, AggressiveServiceDiscovery, StealthServiceDiscovery, DiscoverDeception
from CybORG.Simulator.Actions.AbstractActions.ExploitRemoteService import PIDSelectiveExploitActionSelector, ExploitRemoteService
from CybORG.Simulator.Actions.ConcreteActions.RedSessionCheck import RedSessionCheck
from CybORG.Simulator.Actions.ConcreteActions.Withdraw import Withdraw
from CybORG.Simulator.Actions import Sleep, Action, InvalidAction


class FiniteStateRedAgent(BaseAgent):
    """
    A red agent that performs as a finite state automata, transitioning the hosts it is aware of between different states of knowledge.
    
    Throughout the episode, the hosts will transition between the 8 different states. 
    This will mainly occur via the state transition matrices, depending on action success or failure.
    However, other external factors may affect the state, such as Blue removing a session from a host or the host being outside the agent's area of influence (their assigned subnets).

    """

    def __init__(self, name=None, np_random=None, agent_subnets=None):
        """Initialises the FSM red agent.
        
        Creates the variables to store internal knowledge for the agent.
        Sets the state transitions (basic) and host priorities (none), for the agent.
        
        Parameters
        ----------
        name : str
            agent name
        np_random : Tuple[np.random.Generator, Any]
            numpy random number generator
        agent_subnets : List[IPv4Subnet]
            list of subnet cidr bounds that this red agent can reach
        """
        super().__init__(name, np_random)
        self.step = 0
        self.action_params = None
        self.last_action = None
        self.host_states = {}
        self.host_service_decoy_status = {}
        self.agent_subnets = agent_subnets
        self.action_list = self.action_list()

        self.print_action_output = False
        self.print_obs_output = False
        self.prioritise_servers = False

        self.host_states_priority_list = self.set_host_state_priority_list()
        self.state_transitions_success = self.state_transitions_success()
        self.state_transitions_failure = self.state_transitions_failure()
        self.state_transitions_probability = self.state_transitions_probability()    

    def get_action(self, observation: dict, action_space):
        """The choosing and returning of the action to be used for the current step.
        

        In order to make an appropriate choice, the observations from the previous action must be processed. 
        This is carried out through private functions, in the order listed below:
        
        1. `_host_state_transition(action, success)`
            - The host that was last acted on has its state changed based on the action success.
        2. `_process_new_observations(observation)` 
            - The details of the observation is then processed for newly discovered hosts and decoy discoveries.
        3. `_session_removal_state_change(observation)` 
            - The sessions are then checked to make sure none were lost in the last step, and changing their host states accordingly.

        An textual output is available if the print attributes are set to True (function `last_turn_summary`).


        The next action for the current step is then selected:

        4. If the previous action is still 'in progress' then Sleep is returned, as this action will not be used.
        5. `_choose_host_and_action(action_space, known_hosts)` 
            - A host is chosen; either randomly or based on host state priority.
            - An action on that host is then selected according to the `state_transition_probabilities` matrix.
        6. If the action chosen is `ExploitRemoteService_cc4`, then the selector that takes into account the detected decoys is chosen.
        7. The action is stored for reference and returned.


        Parameters
        ----------
        observation : dict
            The dictionary holding the observations made by the agent from the previous action
        action_space : dict
            The restricted space that the agent knows about and can act on, given by the environment.

         """
     
        action = None
        success = None

        if 'success' in observation.keys():
            success = observation.pop('success')

        if 'action' in observation.keys():
            action = observation.pop('action')

        self._host_state_transition(action, success)
        self._process_new_observations(observation)
        self._session_removal_state_change(observation)

        if self.print_action_output:
            self.last_turn_summary(observation, action, success)

        if success.name == 'IN_PROGRESS':
            self.step += 1
            return Sleep()
        else:
            known_hosts = [h for h in self.host_states.keys() if not self.host_states[h]['state'] == 'F']
            chosen_host, action = self._choose_host_and_action(action_space, known_hosts)

            if isinstance(action, ExploitRemoteService) and chosen_host in list(self.host_service_decoy_status.keys()):
                action.exploit_action_selector = PIDSelectiveExploitActionSelector(excluded_pids=self.host_service_decoy_status[chosen_host])

            self.step += 1
            self.last_action = action
            return action

    def _host_state_transition(self, action: Action, success):
        """State transition depending on the last action and its success."""
        if not action == None and not success.name == 'IN_PROGRESS':
            action_index = None
            action_type = [A for A in self.action_list if isinstance(action, A)]

            if len(action_type) == 1:
                action_index = self.action_list.index(action_type[0])
                action_params = signature(action_type[0]).parameters
                
                host_ips = []
                if 'ip_address' in action_params:
                    host_ips.append(str(action.ip_address))
                elif 'hostname' in action_params:
                    for ip, host_dict in self.host_states.items():
                        if host_dict['hostname'] == action.hostname:
                            host_ips.append(ip)
                            break
                elif 'subnet' in action_params:
                    for ip in self.host_states.keys():
                        if IPv4Address(ip) in action.subnet:
                            host_ips.append(ip)
            
                for host_ip in host_ips:
                    if host_ip in self.host_states.keys():
                        curr_state = self.host_states[host_ip]['state']
                        next_state = None
                        if success.value == 1:
                            next_state = self.state_transitions_success[curr_state][action_index]
                        else:
                            next_state = self.state_transitions_failure[curr_state][action_index]

                        if next_state == 'U':
                            next_state = 'F'
                            for a_subnet in self.agent_subnets:
                                if IPv4Address(host_ip) in a_subnet:
                                    next_state = 'U'

                        if next_state == None:
                            # i.e. if something happens that causes the host to be in a state where they cannot perform that action 
                            # (e.g. session removed during action duration, or error), then just use their previous state. 
                            next_state = curr_state
                            
                        self.host_states[host_ip]['state'] = next_state

    def _session_removal_state_change(self, observation):
        """The changing of state of hosts, where its session has been removed (by Blue)."""
        removed_hosts = []

        for ip, hs in self.host_states.items():
            if 'U' in hs['state'] or 'R' in hs['state']:
                removed_hosts.append(ip)

        for host, obs in observation.items():
            if host == 'message':
                continue

            if 'Sessions' in obs.keys():
                for i, sess in enumerate(obs['Sessions']):
                    host_ip = str(obs['Interface'][0]['ip_address'])
                    if host_ip in removed_hosts:
                        removed_hosts.remove(host_ip)
        
        for ip in removed_hosts:
            self.host_states[ip]['state'] = 'KD'

    def _process_new_observations(self, observation: dict):
        """The finding of new hosts in the past observation, and the discovery of any decoys."""
        # Update knowledge of new hosts and decoys
        for host_id, host_details in observation.items():
            hostname = None
            ip = None

            if host_id == 'message':
                continue
                
            # Identify hostname in obs
            if '_' in host_id:
                hostname = host_id
            elif 'System info' in host_details:
                if 'Hostname' in host_details['System info']:
                    hostname = host_details['System info']['Hostname']
            
            # Identify ip in obs
            if '.' in host_id:
                ip = host_id
            elif 'Interface' in host_details:
                ip = str(host_details['Interface'][0]['ip_address'])
            
            # If hostname already in host_states, identify ip
            if ip == None and not hostname == None:
                for h_ip, h_details in self.host_states.items():
                    if h_details['hostname'] == hostname:
                        ip = h_ip
                        break

            # set new host starting state
            host_state = {}
            if self.step == 0:
                host_state['state'] = 'U'
                if self.agent_subnets == None:
                    for sub_dict in host_details['Interface']:
                        if 'Subnet' in sub_dict.keys():
                            self.agent_subnets = [sub_dict['Subnet']]
                            break
            else:
                host_state['state'] = 'K'

            # if new ip info
            if not ip in self.host_states.keys():
                self.host_states[ip] = host_state
                self.host_states[ip]['hostname'] = hostname

            # if new hostname info
            if not ip == None and not hostname == None:
                if self.host_states[ip]['hostname'] == None:
                    self.host_states[ip]['hostname'] = hostname
            
            # if new decoy info
            if 'Processes' in host_details.keys():
                for process in host_details['Processes']:
                    if 'Properties' in process and 'PID' in process:
                        if 'decoy' in process['Properties']:
                            if host_id in self.host_service_decoy_status:
                                self.host_service_decoy_status[host_id].append(process['PID'])
                            else:
                                self.host_service_decoy_status[host_id] = [process['PID']]
                        
    def _choose_host(self, host_options: List[str]):
        """A valid host is selected and returned"""
        if self.host_states_priority_list is None:
            state_host_options = host_options
        else:
            base = 100
            available_states = {}
            
            for h_opt in host_options:
                if not self.host_states[h_opt]['state'] in available_states.keys():
                    available_states[self.host_states[h_opt]['state']] = self.host_states_priority_list[self.host_states[h_opt]['state']] 
                if len(available_states) == len(self.host_states_priority_list):
                    break

            if sum(available_states.values()) > 0:
                p_multiplier = 1/((sum(available_states.values()) / base))
                probs = [(p/base)*p_multiplier for p in available_states.values()]
                chosen_state = self.np_random.choice(list(available_states.keys()), p=probs)
            else:
                chosen_state = self.np_random.choice(list(available_states.keys()))

            state_host_options = [h for h in host_options if self.host_states[h]['state'] == chosen_state]

        if self.prioritise_servers and len(state_host_options) > 1:
            server_state_host_options = [h for h in state_host_options if self.host_states[h]['hostname'] is not None and 'server' in self.host_states[h]['hostname']] 
            if len(server_state_host_options) > 0:
                i = self.np_random.random()
                if i <= 0.75:
                    chosen_host = self.np_random.choice(server_state_host_options)
                else:
                    #pick other host type
                    if not len(server_state_host_options) == len(state_host_options):
                        non_server_state_host_options = [h for h in state_host_options if not h in server_state_host_options]
                        chosen_host = self.np_random.choice(non_server_state_host_options)
                    else:
                        chosen_host = self.np_random.choice(server_state_host_options)
            else:
                chosen_host = self.np_random.choice(state_host_options)
        else:
            chosen_host = self.np_random.choice(state_host_options)

        return chosen_host
    
    
    def _choose_host_and_action(self, action_space: dict, host_options: List[str]):
        """The selection of a valid host and action to execute this step."""
        chosen_host = self._choose_host(host_options)
        if chosen_host == None:
            return Sleep()

        host_action_options = {self.action_list[i]: prob for i, prob in enumerate(self.state_transitions_probability[self.host_states[chosen_host]['state']]) if not prob == None}

        invalid_actions = []
        while True:
            options = [i for i, v in action_space['action'].items() if v and i not in invalid_actions and i in list(host_action_options.keys())]
            if len(options) > 0:
                probabilities = []
                for opt in options:
                    probabilities.append(host_action_options[opt])
                action_class = self.np_random.choice(options, p=probabilities)
            else:
                new_options = host_options[:]
                new_options.pop(chosen_host)
                return self._choose_action(action_space, new_options)
            # select random options
            action_params = {}
            for param_name in self.action_params[action_class]:
                options = [i for i, v in action_space[param_name].items() if v]
                if param_name == 'hostname':
                    if not self.host_states[chosen_host]['hostname'] == None:
                        action_params[param_name] = self.host_states[chosen_host]['hostname']
                    else:
                        invalid_actions.append(action_class)
                        action_params = None
                        break
                elif param_name == 'ip address' or param_name == "ip_address":
                    action_params[param_name] = IPv4Address(chosen_host)
                elif len(options) > 0:
                    action_params[param_name] = self.np_random.choice(options)
                else:
                    invalid_actions.append(action_class)
                    action_params = None
                    break
            if action_params is not None:
                return chosen_host, action_class(**action_params)
    
    def train(self, results):
        pass

    def end_episode(self): 
        pass

    def set_initial_values(self, action_space, observation):
        """The action parameter values in the action space are sanitised for internal use.
        
        Parameters
        ----------
        action_space : dict
        observation : dict
        """
        if type(action_space) is dict:
            self.action_params = {action_class: signature(action_class).parameters for action_class in action_space['action'].keys()}

    def last_turn_summary(self, observation: dict, action: str, success):
        """Prints action name, parameters, success and sometimes observation and host states.
        
        If `self.print_action_output` is True, the function will run and the observed action and its success will be outputted to the terminal.

        If `self.print_obs_output` is True, additionally the observation and internal `host_states` dictionaries will be outputted. This should only be True for debugging.

        Parameters
        ----------
        observation : dict
            the observation that the agent just received about its previous action
        action : str
            the previous action that was taken
        success : Union[bool, CyEnums.TrinaryEnum]
            the success of the previous action
        """

        action_str = None
        if not action == None:
            action_str = str(action)
        elif success.name == 'IN_PROGRESS':
            action_str = str(self.last_action)
        else: 
            action_str = "Initial Observation"

        print(f'\n** Turn {self.step} for {self.name} **')
        print(f"Action: {action_str}")
        print("Action Success: " + str(success))

        if self.print_obs_output:
            print("\nObservation:")
            pprint(observation)
            print("Host States:")
            pprint(self.host_states)
        
        if isinstance(observation.get('action'), InvalidAction):
            pprint(observation['action'].error)
    
    def action_list(self):
        """The possible actions that can be performed by the agent, in the order of the columns of the state transition matrices.
        
        Returns
        -------
        actions : List[Action]
            List of the 9 actions that a red agent can perform in CC4
        """
        actions = [
            DiscoverRemoteSystems,          #0
            AggressiveServiceDiscovery,     #1
            StealthServiceDiscovery,        #2
            DiscoverDeception,              #3
            ExploitRemoteService,       #4
            PrivilegeEscalate,              #5
            Impact,                         #6
            DegradeServices,                #7
            Withdraw                        #8
        ]
        return actions

    def state_transitions_success(self):
        """The state transition matrix for a successful action on a host.
        
        There is a row for each of the host states: K, KD, S, SD, U, UD, R, RD.
        Then there is a column for each of the actions, in the order of the `action_list`.

        All column 0 must have transition state as all hosts in subnet are transitioned

        ??? example
            ```
            map = {
                'K'  : ['KD', 'S',  'S',  None, None, None, None, None, None],
                'KD' : ['KD', 'SD', 'SD',  None, None, None, None, None, None],
                'S'  : ['SD', None, None, 'S' , 'U' , None, None, None, None],
                'SD' : ['SD', None, None, 'SD', 'UD', None, None, None, None],
                'U'  : ['UD', None, None, None, None, 'R' , None, None, 'S' ],
                'UD' : ['UD', None, None, None, None, 'RD', None, None, 'SD'],
                'R'  : ['RD', None, None, None, None, None, 'R' , 'R' , 'S' ],
                'RD' : ['RD', None, None, None, None, None, 'RD', 'RD', 'SD'],
                'F'  : ['F',  None, None, None, None, None, None, None, None],
            }
            ```

        Returns
        -------
        map : Dict[str, List[float]]
        """
        map = {
            'K'  : ['KD', 'S',  'S',  None, None, None, None, None, None],
            'KD' : ['KD', 'SD', 'SD',  None, None, None, None, None, None],
            'S'  : ['SD', None, None, 'S' , 'U' , None, None, None, None],
            'SD' : ['SD', None, None, 'SD', 'UD', None, None, None, None],
            'U'  : ['UD', None, None, None, None, 'R' , None, None, 'S' ],
            'UD' : ['UD', None, None, None, None, 'RD', None, None, 'SD'],
            'R'  : ['RD', None, None, None, None, None, 'R' , 'R' , 'S' ],
            'RD' : ['RD', None, None, None, None, None, 'RD', 'RD', 'SD'],
            'F'  : ['F',  None, None, None, None, None, None, None, None],
        }
        return map

    def state_transitions_failure(self):
        """The state transition matrix for an unsuccessful action on a host.

        There is a row for each of the host states: K, KD, S, SD, U, UD, R, RD.
        Then there is a column for each of the actions, in the order of the `action_list`.
        
        All column 0 must have transition state as all hosts in subnet are transitioned

        ??? example
            ```
            map = {
                'K'  : ['K' , 'K' , 'K' , None, None, None, None, None, None],
                'KD' : ['KD', 'KD', 'KD', None, None, None, None, None, None],
                'S'  : ['S' , None, None, 'S' , 'S' , None, None, None, None],
                'SD' : ['SD', None, None, 'SD', 'SD', None, None, None, None],
                'U'  : ['U' , None, None, None, None, 'U' , None, None, 'U' ],
                'UD' : ['UD', None, None, None, None, 'UD', None, None, 'UD'],
                'R'  : ['R' , None, None, None, None, None, 'R' , 'R' , 'R' ],
                'RD' : ['RD', None, None, None, None, None, 'RD', 'RD', 'RD'],
                'F'  : ['F',  None, None, None, None, None, None, None, None],
            }
            ```

        Returns
        -------
        map : Dict[str, List[float]]
        """
        map = {
            'K'  : ['K' , 'K' , 'K' , None, None, None, None, None, None],
            'KD' : ['KD', 'KD', 'KD', None, None, None, None, None, None],
            'S'  : ['S' , None, None, 'S' , 'S' , None, None, None, None],
            'SD' : ['SD', None, None, 'SD', 'SD', None, None, None, None],
            'U'  : ['U' , None, None, None, None, 'U' , None, None, 'U' ],
            'UD' : ['UD', None, None, None, None, 'UD', None, None, 'UD'],
            'R'  : ['R' , None, None, None, None, None, 'R' , 'R' , 'R' ],
            'RD' : ['RD', None, None, None, None, None, 'RD', 'RD', 'RD'],
            'F'  : ['F',  None, None, None, None, None, None, None, None],
        }
        return map

    def set_host_state_priority_list(self):
        """ Abstract function for child classes to overwrite with a host state priority list.
        
        Each dictionary value must be an integer or float from 0 to 100, with the total sum of values equaling 100.

        ??? example 
            ```
            host_state_priority_list = {
                'K':12.5, 'KD':12.5, 
                'S':12.5, 'SD':12.5, 
                'U':12.5, 'UD':12.5, 
                'R':12.5, 'RD':12.5}
            ```

        Returns
        -------
        host_state_priority_list : None
            when used in variant child classes, a dict would be returned.
        """
        return None

    def state_transitions_probability(self):
        """Returns a state transitions probability matrix.

        There is a row for each of the host states: K, KD, S, SD, U, UD, R, RD.
        Then there is a column for each of the actions, in the order of the `action_list`.

        ??? example
            ```
            map = {
                'K'  : [0.5,  0.25, 0.25, None, None, None, None, None, None],
                'KD' : [None, 0.5,  0.5,  None, None, None, None, None, None],
                'S'  : [0.25, None, None, 0.25, 0.5 , None, None, None, None],
                'SD' : [None, None, None, 0.25, 0.75, None, None, None, None],
                'U'  : [0.5 , None, None, None, None, 0.5 , None, None, 0.0 ],
                'UD' : [None, None, None, None, None, 1.0 , None, None, 0.0 ],
                'R'  : [0.5,  None, None, None, None, None, 0.25, 0.25, 0.0 ],
                'RD' : [None, None, None, None, None, None, 0.5,  0.5,  0.0 ],
            }
            ```

        Returns
        -------
        matrix : Dict[str, List[float]]
        """

        map = {
            'K'  : [0.5,  0.25, 0.25, None, None, None, None, None, None],
            'KD' : [None, 0.5,  0.5,  None, None, None, None, None, None],
            'S'  : [0.25, None, None, 0.25, 0.5 , None, None, None, None],
            'SD' : [None, None, None, 0.25, 0.75, None, None, None, None],
            'U'  : [0.5 , None, None, None, None, 0.5 , None, None, 0.0 ],
            'UD' : [None, None, None, None, None, 1.0 , None, None, 0.0 ],
            'R'  : [0.5,  None, None, None, None, None, 0.25, 0.25, 0.0 ],
            'RD' : [None, None, None, None, None, None, 0.5,  0.5,  0.0 ],
        }
        return map
