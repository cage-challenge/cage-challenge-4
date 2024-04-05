# Copyright DST Group. Licensed under the MIT license.
import gym
from gym.utils.seeding import RandomNumberGenerator

from typing import Dict, List, Tuple
from CybORG.Shared import Scenario
from CybORG.Shared import Enums
from CybORG.Shared.AgentInterface import AgentInterface
from CybORG.Shared.Enums import DecoyType, TernaryEnum
from CybORG.Shared.Logger import CybORGLogger
from CybORG.Shared.ObservationSet import ObservationSet
from CybORG.Shared.Results import Results
from CybORG.Shared.Session import RedAbstractSession
from CybORG.Simulator.Actions import BlockTraffic, DiscoverNetworkServices, DiscoverRemoteSystems, ExploitRemoteService, PrivilegeEscalate, Analyse, Remove, Restore, RemoveOtherSessions, Impact
from CybORG.Simulator.Actions.Action import Action, RemoteAction, Sleep, InvalidAction
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import AllowTraffic
from CybORG.Shared.Observation import Observation
from CybORG.Shared.RewardCalculator import RewardCalculator
from CybORG.Shared.Scenarios.ScenarioGenerator import ScenarioGenerator
from CybORG.Simulator.State import State
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator 



class SimulationController(CybORGLogger):
    """The class that controls the Simulation environment.

    Attributes
    ----------
    action : Dict[str, List[Action]]
        dictionary of agent actions for the step
    actions_in_progress : Dict[str, Dict]
        actions in progress during the step
    actions_queues : Dict[str, list]
        queue of actions to be taken during the step
    agents : dict
        unused in CC4, default None
    agent_interfaces : Dict[str, AgentInterface]
        dictionary of agents and their interfaces
    bandwidth_usage : Dict[str, int]
        dictionary of hostnames and their bandwidth usage
    blocked_actions : list
        list of blocked actions
    done: bool
        flag for when the episode is complete
    dropped_actions : list
        list of dropped actions
    end_turn_actions : Dict[str, Action]
        dictionary of default actions each agent completes after all chosen actions taken
    failed_actions : list
        list of failed actions
    hostname_ip_map : Dict[str, IPv4Address]
        map of hostnames to IP addresses
    INFO_DICT : Dict[str, _]
        mapping of individual agent knowledge of the environment
    init_state : Dict[str, _]
        initial state observation data
    max_bandwidth : int
        scenario maximum bandwidth
    message_length : int
        scenario message length
    np_random : RandomNumberGenerator
        seeded numpy random number generator
    observation: Dict[str, ObservationSet]
        observations of all agents
    reward : Dict[str, Dict[str, int]]
        current reward for each team
    routeless_actions : list
        list of routeless actions
    scenario : Scenario
        scenario object that the simulation is based off of
    scenario_generator : ScenarioGenerator
        the scenario generator that created the scenario
    state : State
        the current state of the environment
    step_count : int
        the current step count
    subnet_cidr_map : Dict[SUBNET, IPv4Network]
        map of subnets to their network ip address
    team_reward_calculators : Dict[str, Dict[str, RewardCalculator]]
        mapping of teams to their reward calculators
    team : Dict[str, List[str]]
        mapping of teams to agent names
    team_assignments : Dict[str, List[str]]
        mapping of teams to agent names (duplicate)

    """
    def __init__(self, scenario_generator: ScenarioGenerator, agents, np_random: RandomNumberGenerator):
        """
        Parameters
        ----------
        scenario_generator : ScenarioGenerator
        agents : dict
        np_random: RandomNumberGenerator
        """
        self.state = None
        self.bandwidth_usage = {}
        self.dropped_actions = []
        self.routeless_actions = []
        self.blocked_actions = []
        self.end_turn_actions = {}
        self.hostname_ip_map = None
        self.subnet_cidr_map = None
        self.scenario_generator = scenario_generator
        self.np_random = np_random
        scenario = scenario_generator.create_scenario(np_random)
        self._create_environment(scenario)
        self.max_bandwidth = scenario.max_bandwidth
        self.step_count = 0

        self.agents = agents
        self.agent_interfaces = self._create_agents(scenario, agents)
        self.team_reward_calculators = scenario.get_reward_calculators()
        self.team = scenario.team_agents
        self.team_assignments = scenario.get_team_assignments()
        self.reward = {}
        self.INFO_DICT = {}
        self.action = {}
        self.failed_actions = []
        self.observation: Dict[str, ObservationSet] = {}
        self.actions_in_progress: Dict[str, Dict] = {}
        self.INFO_DICT['True'] = {}
        for host in scenario.hosts:
            self.INFO_DICT['True'][host] = {
                'System info': 'All',
                'Sessions': 'All',
                'Interfaces': 'All',
                'User info': 'All',
                'Processes': ['All']
            }
        self.init_state = self._filter_obs(self.get_true_state(self.INFO_DICT['True'])).data
        for agent in scenario.agents:
            self.INFO_DICT[agent] = scenario.get_agent_info(agent).osint.get('Hosts', {})
            for host in self.INFO_DICT[agent].keys():
                self.INFO_DICT[agent][host]['Sessions'] = agent

        # populate initial observations with OSINT
        for agent_name, agent in self.agent_interfaces.items():
            obs = self.get_true_state(self.INFO_DICT[agent_name])
            self.observation[agent_name] = self._filter_obs(obs, agent_name)
            agent.set_init_obs(self.observation[agent_name].data, self.init_state)
        self.actions_queues = {agent_name: [] for agent_name in self.agent_interfaces.keys()}
        self.reset_observation()
        self.message_length = self.scenario_generator.MESSAGE_LENGTH
        self.done = self.determine_done()
        # calculate reward for each team
        for team_name, team_calcs in self.team_reward_calculators.items():
            self.reward[team_name] = {}
            for reward_name, r_calc in team_calcs.items():
                self.reward[team_name][reward_name] = self.calculate_reward(r_calc)
        self._log_debug(f"Finished init()")

    def reset(self, np_random=None) -> Results:
        """Resets the environment 
        
        Parameters
        ----------
        np_random: RandomNumberGenerator

        Returns
        -------
        : Results
            results object from the reset environment
        """
        self.reward = {}
        self.action = {}
        self.observation = {}
        self.step_count = 0
        self.actions_in_progress = {}
        if np_random is not None:
            self.np_random = np_random

        scenario = self.scenario_generator.create_scenario(self.np_random)
        self._create_environment(scenario)

        self.agent_interfaces = self._create_agents(scenario, self.agents)
        self.team = scenario.team_agents
        self.team_assignments = scenario.get_team_assignments()
        self.max_bandwidth = scenario.max_bandwidth

        # ## INFO_DICT Changes every env.reset() given the varying network design/nodes
        self.INFO_DICT = {}
        self.INFO_DICT['True'] = {}
        for host in scenario.hosts:
            self.INFO_DICT['True'][host] = {'System info': 'All', 'Sessions': 'All', 'Interfaces': 'All', 'User info': 'All',
                                      'Processes': ['All']}
        self.init_state = self._filter_obs(self.get_true_state(self.INFO_DICT['True'])).data
        for agent in scenario.agents:
            self.INFO_DICT[agent] = scenario.get_agent_info(agent).osint.get('Hosts', {})
            for host in self.INFO_DICT[agent].keys():
                self.INFO_DICT[agent][host]['Sessions'] = agent
        self.actions_queues = {agent_name: [] for agent_name in self.agent_interfaces.keys()}
        for agent_name, agent_object in self.agent_interfaces.items():
            self.observation[agent_name] = self._filter_obs(self.get_true_state(self.INFO_DICT[agent_name]), agent_name)
            agent_object.set_init_obs(self.observation[agent_name].data, self.init_state)
        self.reset_observation()
        self.done = self.determine_done()

        # calculate reward for each team
        for team_name, team_calcs in self.team_reward_calculators.items():
            self.reward[team_name] = {}
            for reward_name, r_calc in team_calcs.items():
                self.reward[team_name][reward_name] = self.calculate_reward(r_calc)
        # changes to step and mission phase will only effect CC4
        if isinstance(self.scenario_generator, EnterpriseScenarioGenerator):
            # update step in state and calc current mission phase to step = 0
            self.state.mission_phase = 0
            # update allowed subnets in all agent interfaces and agent spaces
            self._update_agents_allowed_subnets()
    
    def step(self, actions: dict = None, skip_valid_action_check=False):
        """Updates the simulation environment based on the joint actions of all agents

        Parameters
        ----------
        actions : Dict[str, Action]
            name of the agent and the action they perform
        skip_valid_action_check: bool
            if false then action is checked against the agents action space to determine validity of action and .
            if not valid then the action is replaced with an InvalidAction object
        
        """
        # changes to step and mission phase will only effect CC4
        if isinstance(self.scenario_generator, EnterpriseScenarioGenerator):
            # update step in state and calc current mission phase
            # if mission phase has changed (inc.) then return True else return False
            if self.state.check_next_phase_on_update_step(self.step_count):
                # update allowed subnets in all agent interfaces and agent spaces
                self._update_agents_allowed_subnets()
        
        if actions is None:
            actions = {}

        # Adds new actions to the action sets.
        # Any agent that doesn't have an action supplied has a default action added for it.
        for agent_name, agent_object in self.agent_interfaces.items():
            action = actions.get(agent_name, None)
            if action is None:
                last_obs = self.get_last_observation(agent_name)
                action = agent_object.get_action(last_obs)
            if not skip_valid_action_check:
                action = self.replace_action_if_invalid(action, agent_object)
            # Adds a new item to a particular action set. Action sets are indexed by agent_name
            # This function will create any necessary empty dicts/lists as it goes.
            # The remaining_ticks is assumed to start at the duration of the action unless specified otherwise.
            set_item = {"action": action, "remaining_ticks": action.duration}
            if self.actions_in_progress.get(agent_name, None) is None:
                self.actions_in_progress[agent_name] = set_item

        # clear old observations
        self.observation = {a: ObservationSet([]) for a in self.agent_interfaces}


        # Iterates through all of the actions in the action sets, decrementing their remaining ticks.
        # Any actions with < 1 remaining ticks are ready to execute and are moved from actions_in_progress to actions_to_execute.
        actions_to_execute: Dict[str, List[Dict]] = {}
        for agent_name, set_item in self.actions_in_progress.items():
            set_item["remaining_ticks"] -= 1
            actions_to_execute.setdefault(agent_name, [])
            if set_item["remaining_ticks"] < 1:
                self.actions_in_progress[agent_name] = None
                actions_to_execute[agent_name].append(set_item['action'])
            else:
                self.observation[agent_name].append(Observation(TernaryEnum.IN_PROGRESS))
                actions_to_execute[agent_name].append(Sleep())

        self.action = actions_to_execute
        actions_to_execute = self.sort_action_order(actions_to_execute)

        # execute actions in order of priority
        for (agent_name, action) in actions_to_execute:
            obs = self.execute_action(action)
            filtered_obs = self._filter_obs(obs, agent_name)
            filtered_obs.data['action'] = action
            self.observation[agent_name].append(filtered_obs)

        # check for sessions that need to be reassigned to a different agent, due to subnet traversal
        self.different_subnet_agent_reassignment()
        
        # execute additional default end turn actions
        for agent_name, agent_action in self.end_turn_actions.items():
            if self.agent_interfaces[agent_name].active:
                obs = self.execute_action(agent_action[0](**agent_action[1]))
                filtered_obs = self._filter_obs(obs, agent_name)
                filtered_obs.data['action'] = agent_action[0](**agent_action[1])
                self.observation[agent_name].observations.append(filtered_obs)
                # self._session_check()

        # update agent interfaces and action spaces
        for agent_name, observation_sets in self.observation.items():
            for observation in observation_sets.observations:
                session_length = len(self.get_action_space(agent_name)['session'])
                if self.scenario_generator.update_each_step or session_length == 0:
                    self.agent_interfaces[agent_name].update(observation)

        # Increment step counter
        self.step_count += 1

        # calculate done signal
        self.done = self.scenario_generator.determine_done(self)

        # reset previous reward
        self.reward = {}

        # calculate reward for each team
        for team_name, team_calcs in self.team_reward_calculators.items():
            self.reward[team_name] = {}
            for reward_name, r_calc in team_calcs.items():
                self.reward[team_name][reward_name] = self.calculate_reward(r_calc)
            action_cost = sum(actions.get(agent, Action()).cost for agent in self.team[team_name])
            self.reward[team_name]['action_cost'] = action_cost

        for host in self.state.hosts.values():
            host.update(self.state)
        self.state.update_data_links()

    def set_np_random(self, np_random):
        """Sets the random number generator"""
        self.np_random = np_random
        self.state.set_np_random(np_random)

    def execute_action(self, action: Action) -> Observation:
        """Executes the given action 
        
        Parameters
        ----------
        action : Action
            action to execute
        
        Returns
        -------
        : Observation
            the observation resulting from the performed action
        """
        return action.execute(self.state)

    def get_true_state(self, info: dict) -> Observation:
        """Gets the true state
        
        Parameters
        ----------
        info : dict

        Returns
        -------
        output : Observation
            the observation from the true state
        """
        output = self.state.get_true_state(info)
        return output

    def _create_environment(self, scenario: Scenario):
        self.state = State(scenario, self.np_random)
        self.hostname_ip_map = {h: ip for ip, h in self.state.ip_addresses.items()}
        self.subnet_cidr_map = self.state.subnet_name_to_cidr
        self.end_turn_actions = scenario.get_end_turn_actions()

    def calculate_reward(self, reward_calculator: RewardCalculator) -> float:
        """Calculates the reward using the reward calculator
        
        Parameters
        ----------
        reward_calculator : RewardCalculator
            An object to calculate the reward

        Returns
        -------
        : float
            The reward value for the associated reward calculator
        """
        return reward_calculator.calculate_simulation_reward(self)

    def get_active_agents(self) -> list:
        """Gets the currently active agents
        
        Returns
        -------
        active_agents : list
            list of active agents
        """

        active_agents = []
        for agent_name, sessions in self.state.sessions.items():
            length = len([session.ident for session in sessions.values() if session.active and session.parent is None])
            if length > 0 and not self.agent_interfaces[agent_name].internal_only:
                active_agents.append(agent_name)

        return active_agents

    def is_active(self, agent_name: str) -> bool:
        """Tests if agent has an active server session"""
        return len([session.ident for session in self.state.sessions[agent_name].values() if session.active and session.parent is None]) > 0

    def has_active_non_parent_sessions(self, agent_name: str) -> bool:
        """Tests if an agent has active sessions that aren't a parent session"""
        return len([session.ident for session in self.state.sessions[agent_name].values() if session.active and session.parent is not None]) > 0

    def sort_action_order(self, actions: Dict[str, List[Action]]) -> List[Tuple[str,Action]]:
        """Sorts the actions based on priority and sets the dropped parameter for actions based on bandwidth usage
        
        Parameters
        ----------
        actions : Dict[str, List[Action]]
            dictionary of actions to sort
        
        Returns
        -------
        : List[Tuple[str,Action]]
            sorted list of actions
        
        """
        flattened_actions = [(agent_name, agent_action) for agent_name, agent_actions in actions.items() for agent_action in agent_actions]
        actions = sorted(flattened_actions, key=lambda x: x[1].priority)
        actions = self.filter_actions(actions)

        # shuffle action order to randomise which are dropped if bandwidth exceeded
        action_index = list(range(len(actions)))
        self.np_random.shuffle(action_index)

        # use bandwidth until exceeded then drop actions
        bandwidth_usage = {}
        self.routeless_actions = []
        self.blocked_actions = []
        self.dropped_actions = []

        for i in action_index:
            (agent, action) = actions[i]
            if issubclass(type(action), RemoteAction):
                route = action.get_used_route(self.state, routing=True)
                action.route_designated = True
                if route is not None:
                    for host in route:
                        # if blocked then action consumes no further bandwidth
                        # if host in self.state.blocks and route[0] in self.state.blocks[host]:
                        if action.blocking_host(self.state, route[0], host):
                            action.blocked = host
                            self.blocked_actions.append(action)
                            break
                        # otherwise action consumes bandwidth at host
                        if host in bandwidth_usage:
                            bandwidth_usage[host] += action.bandwidth_usage
                        else:
                            bandwidth_usage[host] = action.bandwidth_usage
                        # and bandwidth from all surrounding hosts
                        for interface in self.state.hosts[host].interfaces:
                            if interface.interface_type == 'wireless':
                                for h in interface.data_links:
                                    if h in bandwidth_usage:
                                        bandwidth_usage[h] += action.bandwidth_usage
                                    else:
                                        bandwidth_usage[h] = action.bandwidth_usage
                        # if the maximum bandwidth is exceeded then the action is droppped and doesn't continue down the route
                        if bandwidth_usage[host] > self.max_bandwidth:
                            self.dropped_actions.append(action)
                            action.dropped = True
                            break
                else:
                    action.dropped = True
                    self.routeless_actions.append(action)
        self.bandwidth_usage = dict(bandwidth_usage)

        # # sort the actions based on priority
        # actions = dict(sorted(actions.items(), key=lambda item: item[1].priority))
        return actions

    def filter_actions(self, actions: List[Tuple[str,Action]]) -> List[Tuple[str,Action]]:
        """ Checks agent and session exist for each action

        Parameters
        ----------
        actions : List[Tuple[str,Action]]
            list of actions to filter
        
        Returns
        -------
        : List[Tuple[str,Action]]
            list of filtered actions
        """
        sessionless = lambda action: not hasattr(action, 'session')
        has_access = lambda action: action.session in self.state.sessions.get(action.agent, [])
        filtered_actions: List[Tuple[str,Action]] = []
        for (agent, action) in actions:
            if sessionless(action) or has_access(action):
                filtered_actions.append((agent, action))
        return filtered_actions

    def get_connected_agents(self, agent: str) -> list:
        """Gets a list of agents that are connected the the agent"""
        # get agents host
        hostname = None
        for sessions, session_obj in self.state.sessions[agent].items():
            if session_obj.parent == None:
                hostname = session_obj.hostname

        if hostname is None:
            return [agent]

        # get all connected hosts
        connected_hosts = []
        for host in self.state.hosts.keys():
            if RemoteAction.check_routable(self.state, host, hostname):
                connected_hosts.append(host)

        # get agents on connected hosts
        connected_agents = []
        for other_agent, sessions in self.state.sessions.items():
            if agent == other_agent:
                continue

            for session in sessions.values():
                if session.hostname in connected_hosts and session.parent is None:
                    connected_agents.append(other_agent)
                    break
        return connected_agents

    def get_render_data(self):
        """ Build render data for CC3 - not used for CC4 """
        pass
        # scenario_gen_type = 'Unsupport scenario'
        # if isinstance(self.scenario_generator, DroneSwarmScenarioGenerator):
        #     scenario_gen_type = DroneSwarmScenarioGenerator
        # elif isinstance(self.scenario_generator, FileReaderScenarioGenerator):
        #     scenario_gen_type = FileReaderScenarioGenerator
        # if self.scenario_generator.background_image is None:
        #     raise ValueError(f"Scenario generator {self.scenario_generator.__class__} has not background_image set")
        # background_image = self.scenario_generator.background_image
        # data = {'scenario_gen_type': scenario_gen_type,
        #         'drones': {hostname: {"hostname": hostname,
        #                               "x": host_info.position[0],
        #                               "y": host_info.position[1],
        #                               "os_type": host_info.os_type.name,
        #                               "ip": host_info.interfaces[0].ip_address,
        #                               "processes": host_info.processes,
        #                               "sessions": self.state.sessions} for hostname, host_info in
        #                    self.state.hosts.items()},
        #         'network': {hostname: [h for interface in host_info.interfaces for h in interface.data_links] for
        #                     hostname, host_info in
        #                     self.state.hosts.items()},
        #         'actions': [],
        #         "background": background_image,
        #         "step": self.step_count}

        # # get which hosts are red
        # red_hosts, red_low_hosts, red_action = self.add_red_actions(data, scenario_gen_type)

        # # get which hosts are blue
        # blue_hosts, blue_protected_hosts = self.add_blue_actions(data, red_action, scenario_gen_type)

        # # 'BlueDrone', 'BlueDroneLowProvRed', 'RedDrone', 'BlueDroneProtected'
        # self.update_symbols(data, red_hosts, red_low_hosts, blue_hosts, blue_protected_hosts)

        # # add in rewards
        # self.add_rewards(data)

        # # add number of times taken by Red & number of times retaken by Blue
        # # if self.state.scenario.get_scenario_gen_type() == FileReaderScenarioGenerator:
        # #     data['sessions_count'] = self.get_impact_restore_count()
        # # elif self.state.scenario.get_scenario_gen_type() == DroneSwarmScenarioGenerator:
        # #     data['sessions_count'] = self.state.sessions_count
        # # else:
        # #     data['sessions_count'] = {}

        # return data

    def get_impact_restore_count(self) -> Dict[str, Dict[str, int]]:
        sessions_count = {}
        for hostname, hostinfo in self.state.hosts.items():
            sessions_count[hostname] = {}
            sessions_count[hostname]["impact_count"] = hostinfo.get_impact_count()
            sessions_count[hostname]["restore_count"] = hostinfo.get_restore_count()

        return sessions_count

    def add_rewards(self, data):
        data['rewards'] = {}

        for team in ['Red', 'Blue']:
            rewards = self.reward.get(team, {})

            if len(rewards) == 0:
                data['rewards'][team] = 0
            else:
                try:
                    data['rewards'][team] = sum(rewards.values())
                except:
                    print(rewards)

    def update_symbols(self, data, red_hosts, red_low_hosts, blue_hosts, blue_protected_hosts):
        for hostname, host_info in self.state.hosts.items():
            # if red high priv
            if hostname in red_hosts:
                data['drones'][hostname]['symbol'] = 'RedDrone'
            # if red low priv
            elif hostname in red_low_hosts:
                data['drones'][hostname]['symbol'] = 'BlueDroneLowPrivRed'
            # if blue protected
            elif hostname in blue_protected_hosts:
                data['drones'][hostname]['symbol'] = 'BlueDroneProtected'
            # else blue
            elif hostname in blue_hosts:
                data['drones'][hostname]['symbol'] = 'BlueDrone'
            # else neutral host
            else:
                data['drones'][hostname]['symbol'] = 'NeutralDrone' # routers

    def add_blue_actions(self, data, red_action, scenario_gen_type):
        blue_hosts = []
        blue_protected_hosts = []
        blue_action = None
        for agent in self.team['Blue']:
            blue_hosts += [i.hostname for i in self.state.sessions[agent].values()]

            for blue_session in self.state.sessions[agent].values():
                for host_proc in self.state.hosts[blue_session.hostname].processes:
                    if host_proc.decoy_type != DecoyType.NONE:
                        blue_protected_hosts.append(blue_session.hostname)

            if agent in self.action:
                for blue_action in self.action[agent]:

                    if type(blue_action) in (Sleep, InvalidAction):
                        continue

                    blue_from = agent

                    # set action source
                    if self.state.sessions.get(blue_action.agent) and self.state.sessions[blue_action.agent].get(blue_action.session):
                        blue_source = self.state.sessions[blue_action.agent][blue_action.session].hostname
                    else:
                        continue

                    # set action target
                    blue_target = None
                    if hasattr(blue_action, 'subnet'):
                        blue_target = \
                        [name for name, cidr in self.state.subnet_name_to_cidr.items() if
                         cidr == red_action.subnet][0] + 'Subnet'
                    # if scenario_gen_type == FileReaderScenarioGenerator:
                    #     if hasattr(blue_action, 'ip_address') and hasattr(red_action, 'ip_address'):
                    #         blue_target = self.state.ip_addresses[red_action.ip_address]
                    #     elif hasattr(blue_action, 'ip_address'):
                    #         blue_target = self.state.ip_addresses[blue_action.ip_address]

                    # if scenario_gen_type == DroneSwarmScenarioGenerator:
                    #     if hasattr(blue_action, 'ip_address'):
                    #         blue_target = self.state.ip_addresses[blue_action.ip_address]

                    #     if type(blue_action) == RemoveOtherSessions:
                    #         blue_target = self.state.sessions[blue_action.agent][0].hostname

                    if hasattr(blue_action, 'hostname'):
                        blue_target = blue_action.hostname

                    # set blue action label
                    blue_action_type: str = None
                    action_type_map = {}
                    if blue_target is not None:
                        # if scenario_gen_type == FileReaderScenarioGenerator:
                        #     action_type_map = {
                        #         DiscoverNetworkServices: 'port scan',
                        #         DiscoverRemoteSystems: 'network scan',
                        #         Restore: 'restore',
                        #         Remove: 'remove',
                        #         Analyse: 'analyse'
                        #     }
                        # elif scenario_gen_type == DroneSwarmScenarioGenerator:
                        #     action_type_map = {
                        #         RetakeControl: 'restore',
                        #         RemoveOtherSessions: 'remove',
                        #         AllowTraffic: 'allow_traffic',
                        #         BlockTraffic: 'block_traffic'
                        #     }
                        blue_action_type = action_type_map.get(type(blue_action), None)

                        # set actions
                        if blue_action_type is not None:
                            data['actions'].append(
                                {"agent": blue_from, "source": blue_source, "destination": blue_target,
                                "type": blue_action_type})
                         
        return blue_hosts,blue_protected_hosts

    def add_red_actions(self, data, scenario_gen_type):
        red_hosts = []
        red_low_hosts = []
        red_action = None
        for agent in self.team['Red']:
            sessions = self.state.sessions[agent].values()
            red_hosts += [s.hostname for s in sessions if s.has_privileged_access()]
            red_low_hosts += [s.hostname for s in sessions]
            # get agent actions
            if agent in self.action:
                for red_action in self.action[agent]:

                    if type(red_action) in (Sleep, InvalidAction):
                        continue
                    red_from = agent

                    # fix ActivateTrojan bug for drone swarm scenario
                    if red_action.name == 'ActivateTrojan':
                        red_source = red_action.hostname
                    else:
                        if self.state.sessions.get(red_action.agent) and self.state.sessions[red_action.agent].get(red_action.session):
                            red_source = self.state.sessions[red_action.agent][red_action.session].hostname
                        else:
                            continue

                    # set red target
                    red_target = None
                    if hasattr(red_action, 'subnet'):
                        red_target = \
                        [name for name, cidr in self.state.subnet_name_to_cidr.items() if
                         cidr == red_action.subnet][0] + '_router'
                    if hasattr(red_action, 'ip_address'):
                        red_target = self.state.ip_addresses[red_action.ip_address]
                    if hasattr(red_action, 'hostname'):
                        red_target = red_action.hostname

                    # set red action label
                    red_action_type: str = None
                    action_type_map = {}
                    if red_target is not None:
                        if scenario_gen_type == EnterpriseScenarioGenerator: # or scenario_gen_type == FileReaderScenarioGenerator):
                            action_type_map = {
                                DiscoverNetworkServices: 'port scan',
                                DiscoverRemoteSystems: 'network scan',
                                ExploitRemoteService: 'exploit',
                                Analyse: 'analyse',
                                PrivilegeEscalate: 'escalate',
                                Impact: 'impact'
                            }
                        # elif scenario_gen_type == DroneSwarmScenarioGenerator:
                        #     action_type_map = {
                        #         ExploitDroneVulnerability: 'exploit',
                        #         FloodBandwidth: 'impact',
                        #         SeizeControl: 'escalate'
                        #     }
                        red_action_type = action_type_map.get(type(red_action), None)

                        if red_action_type is not None:
                            # set actions
                            data['actions'].append(
                                {"agent": red_from, "destination": red_target, "source": red_source, "type": red_action_type})

        return red_hosts,red_low_hosts,red_action

    def _update_agents_allowed_subnets(self):
        """This function updates the allowed_subnets of the green agents depending on the current mission phases."""
        curr_mp = self.state.mission_phase
        mphases = self.state.scenario.allowed_subnets_per_mphase[curr_mp]

        for agent_name, agent in self.agent_interfaces.items():
            if "green" in agent_name:
                green_host = self.state.sessions[agent_name][0].hostname
                green_subnet = self.state.hostname_subnet_map[green_host]
                green_mphase = [green_subnet]   # a subnet is always allowed to communicate within itself

                for idx in range(len(mphases)):
                    (s1, s2) = mphases[idx]
                    if s1 == green_subnet:
                        green_mphase.append(s2)
                    elif s2 == green_subnet:
                        green_mphase.append(s1)

                agent.update_allowed_subnets(green_mphase)

    def reset_observation(self):
        """Populate initial observations with OSINT"""
        for agent_name, agent in self.agent_interfaces.items():
            true_state = self.get_true_state(self.INFO_DICT[agent_name])
            initial_obs = self._filter_obs(true_state, agent_name)
            agent.set_init_obs(initial_obs.data, self.init_state)
            self.observation[agent_name] = ObservationSet([initial_obs])

    def _session_check(self):
        for agent in self.state.sessions:
            for host in self.state.hosts.values():
                for session in host.sessions[agent]:
                    assert session in self.state.sessions[agent]

    def send_messages(self, messages: dict = None):
        """Sends messages between agents
        
        Parameters
        ----------
        messages : dict
        """
        if messages is None:
            messages = {}

        # reset messages
        for agent, agent_interface in self.agent_interfaces.items():
            agent_interface.messages = []

        # send message to other agents
        for agent, message in sorted(messages.items()):
            assert self.get_message_space(agent).contains(message), f'{agent} attempting to send message {message} that is not in the message space {self.get_message_space(agent)}'
            for other_agent in self.get_connected_agents(agent):
                self.agent_interfaces[other_agent].messages.append(message)

        # add messages to observations
        for agent, observation in self.observation.items():
            if len(self.agent_interfaces[agent].messages) > 0:
                observation.append(Observation(msg=self.agent_interfaces[agent].messages))

    def get_message_space(self, agent) -> gym.Space:
        msg_space = gym.spaces.MultiBinary(self.message_length)
        msg_space._np_random = self.np_random
        return msg_space

    def determine_done(self) -> bool:
        """The done signal is always false
        Returns
        -------
        bool
            whether goal was reached or not
        """
        return self.scenario_generator.determine_done(self)

    def different_subnet_agent_reassignment(self):
        """ If an agent has a session outside of their subnet, change the agent to the corresponding agent for the subnet. If that agent is not active, activate them.
            
        Note, a red agent may have multiple red sessions assigned to it from the PhisingEmail action (assigned to the closest connected red agent). 
        However, only not all of these will need to be reassigned, therefore, we may need to reindex the original red agents sessions. 
        This requires making adjustments to the state.sessions, state.sessions_counts, state.hosts, and the sessions children.

        This is only required for the EnterpriseScenarioGenerator, and will cause the failure of tests that utilise older scenarios if instance not checked.
        """

        if isinstance(self.scenario_generator, EnterpriseScenarioGenerator):
            red_allowed_subnets_map = { agent_name : agent.allowed_subnets for agent_name, agent in self.agent_interfaces.items() if 'red' in agent_name}
            sessions_to_reassign = []
            
            # if a session's agent does not match its host's subnet, then add it to the list of 'sessions_to_reassign'
            for agent_name in red_allowed_subnets_map.keys():
                for session_id in self.state.sessions[agent_name]:
                    session_host_subnet = self.state.hostname_subnet_map[self.state.sessions[agent_name][session_id].hostname].value
                    if session_host_subnet not in red_allowed_subnets_map[agent_name]:
                        reassign = {
                            'orig_agent' : agent_name,
                            'orig_session_id' : session_id,
                            'host_subnet' : session_host_subnet,
                            'host_name' : self.state.sessions[agent_name][session_id].hostname,
                            'host_ip' : str(self.state.hostname_ip_map[self.state.sessions[agent_name][session_id].hostname])
                        }
                        sessions_to_reassign.append(reassign)

            # Find the agent that should own the session
            for red_owner, allowed_subnets in red_allowed_subnets_map.items():
                for reassign_dict in sessions_to_reassign:
                    if reassign_dict['host_subnet'] in allowed_subnets:
                        reassign_dict['new_agent'] = red_owner

            # For each of the sessions to reassign
            for reassignment in sessions_to_reassign:
                # Reassign sessions (remove old and add new)
                old_session = self.state.sessions[reassignment['orig_agent']].pop(reassignment['orig_session_id'])
                new_session = RedAbstractSession(
                    hostname=old_session.hostname, username=old_session.username,
                    agent=reassignment['new_agent'], parent=None, pid=old_session.pid,
                    session_type=Enums.SessionType.RED_ABSTRACT_SESSION,
                    timeout=old_session.timeout, ident = None,
                    is_escalate_sandbox=old_session.is_escalate_sandbox,
                )
                self.state.add_session(new_session)
                self.state.sessions_count[reassignment['orig_agent']]-=1

                self.state.hosts[new_session.hostname].sessions[reassignment['orig_agent']].remove(reassignment['orig_session_id'])
                reassignment['new_session_id'] = new_session.ident

                # Edit + Add Observation
                new_obs = None
                for i, obs in enumerate(self.observation[reassignment['orig_agent']].observations):
                    if reassignment['host_ip'] in obs.data.keys():
                        for obs_sess in obs.data[reassignment['host_ip']]['Sessions']:
                            if obs_sess['agent'] == reassignment['orig_agent'] and obs_sess['session_id'] == reassignment['orig_session_id']:
                                # Edit the current agent's observation
                                obs_sess['agent'] = reassignment['new_agent']
                                obs_sess['session_id'] = reassignment['new_session_id']
                                obs_sess['Type'] = Enums.SessionType.RED_ABSTRACT_SESSION

                                # Add this as a new observation to the new agent
                                new_obs = obs.copy()
                                remove_keys = [k for k in new_obs.data.keys() if not k == reassignment['host_ip'] and not k == 'action' and not k == 'success']
                                for key in remove_keys:
                                    new_obs.data.pop(key)

                                new_obs.raw = reassignment['orig_agent'] + "'s action created a new session."
                                new_obs.data.pop('action')
                                new_obs.data['success'] = TernaryEnum.UNKNOWN

                                self.observation[reassignment['new_agent']].observations.append(new_obs)
                        break

        # if agent is not active but has sessions then activate
        for agent_name, agent_int in self.agent_interfaces.items():
            if agent_int.active==False and self.is_active(agent_name)==True:
                self.agent_interfaces[agent_name].active=True
            elif agent_int.active==False and self.is_active(agent_name)==False and self.has_active_non_parent_sessions(agent_name):
                self.agent_interfaces[agent_name].active=True
            elif agent_int.active==True and self.is_active(agent_name)==False and self.has_active_non_parent_sessions(agent_name)==False and 'Trojan' not in agent_name:
                # hack to ensure DroneScenario Trojan can still spawn agents
                self.agent_interfaces[agent_name].active=False

    def start(self, steps: int = None, log_file=None, verbose=False):
        """Start the environment and run for a specified number of steps.

        Parameters
        ----------
        steps : int
            the number of steps to run for
        log_file : File, optional
            a file to write results to (default=None)

        Returns
        -------
        bool
            whether goal was reached or not
        """
        done = False
        max_steps = 0
        if steps is None:
            while not done:
                if verbose:
                    print(max_steps)
                max_steps += 1
                self.step()
            if verbose:
                print('Red Wins!')  # Junk Test Code
        else:
            for step in range(steps):
                max_steps += 1
                self.step()
                if verbose:
                    print(max_steps)
                done = self.done
                if step == 500:
                    print(step)  # Junk Test Code
                if done:
                    print(f'Red Wins at step {step}')  # Junk Test Code
                    break

            # print(f"{agent_name}'s Reward: {self.reward[agent_name]}")
        if log_file is not None:
            log_file.write(
                f"{max_steps},{self.reward['Red']},{self.reward['Blue']},"
                f"{self.agent_interfaces['Red'].agent.epsilon},"
                f"{self.agent_interfaces['Red'].agent.gamma}\n"
            )
        return done

    def get_agent_state(self, agent_name: str) -> Observation:
        """Gets agent's current state
        
        Parameters
        ----------
        agent_name : str

        Returns
        -------
        : Observations
            the agent's current state
        """
        return self.get_true_state(self.INFO_DICT[agent_name])

    def get_last_observation(self, agent: str) -> Observation:
        """Get the last observation for an agent

        Parameters
        ----------
        agent : str
            name of agent to get observation for

        Returns
        -------
        Observation
            agents last observation
        """
        if agent in self.observation:
            return self.observation[agent].get_combined_observation()
        return Observation()

    def get_action_space(self, agent: str) -> dict:
        """Gets the action space for a chosen agent

        Parameters
        ----------
        agent: str
            agent selected

        Returns
        -------
        : dict
            action space of the agent
        """
        if agent in self.agent_interfaces:
            return self.agent_interfaces[agent].action_space.get_action_space()
        raise ValueError(f'Agent {agent} not in agent list {self.agent_interfaces.keys()}')

    def get_observation_space(self, agent: str) -> dict:
        """Gets the observation space for a chosen agent

        Parameters
        ----------
        agent: str
            agent selected

        Returns
        -------
        : dict
            agent observation space
        """
        if agent in self.agent_interfaces:
            return self.agent_interfaces[agent].get_observation_space()
        raise ValueError(f'Agent {agent} not in agent list {self.agent_interfaces.values()}')

    def get_last_action(self, agent: str) -> Action:
        """Gets the observation space for a chosen agent

        Parameters
        ----------
        agent: str
            agent selected

        Returns
        -------
        : Action
            agent's last action
        """
        return self.action[agent] if agent in self.action else None

    def _create_agents(self, scenario: Scenario, agent_classes: dict = None) -> Dict[str, AgentInterface]:
        agents = {}

        for agent_name in scenario.agents:
            agent_info = scenario.get_agent_info(agent_name)
            if agent_classes is not None and agent_name in agent_classes:
                agent_obj = agent_classes[agent_name]
            else:
                agent_obj = agent_info.agent_type
            agent_obj.np_random = self.np_random
            agent_obj.end_episode()
            agents[agent_name] = AgentInterface(
                agent_obj,
                agent_name,
                agent_info.actions,
                allowed_subnets=agent_info.allowed_subnets,
                scenario=scenario,
                active = agent_info.active,
                internal_only = agent_info.internal_only
            )
        return agents

    def _filter_obs(self, obs: Observation, agent_name=None):
        """Filter obs to contain only hosts/subnets in scenario network """
        if self.scenario_generator.update_each_step:
            if agent_name is not None:
                allowed_subnets = self.agent_interfaces[agent_name].allowed_subnets
                subnets = [self.subnet_cidr_map[subnet] for subnet in allowed_subnets]
            else:
                subnets = list(self.subnet_cidr_map.values())

            obs.filter_addresses(
                ips=self.hostname_ip_map.values(), cidrs=subnets, include_localhost=False
            )
        return obs

    def replace_action_if_invalid(self, action: Action, agent: AgentInterface):
        """Returns action if the parameters in the action are in and true in the action set else return InvalidAction imbued with bug report.

        Parameters
        ----------
        action : Action
            action to test if valid
        agent : AgentInterface
            agent that is performing the action

        Returns
        -------
        action : Action
            Action parameter if valid, otherwise InvalidAction
        """
        action_space = agent.action_space.get_action_space()

        if type(action) not in action_space['action']:
            message = f'Action {action} not in action space for agent {agent.agent_name}.'
            return InvalidAction(action=action, error=message)

        if not action_space['action'][type(action)]:
            message = f'Action {action} is not valid for agent {agent.agent_name} at the moment. This usually means it is trying to access a host it has not discovered yet.'
            return InvalidAction(action=action, error=message)

        # next for each parameter in the action
        for parameter_name, parameter_value in action.get_params().items():
            if parameter_name not in action_space:
                continue
            
            if isinstance(parameter_value, list):
                for value in parameter_value:
                    if value not in action_space[parameter_name]:
                        message = f'Action {action} has parameter {parameter_name} that contains {value}. However, {value} is not in the action space for agent {agent.agent_name}.'
                        return InvalidAction(action=action, error=message)
            else:
                if parameter_value not in action_space[parameter_name]:
                    message = f'Action {action} has parameter {parameter_name} valued at {parameter_value}. However, {parameter_value} is not in the action space for agent {agent.agent_name}.'
                    return InvalidAction(action=action, error=message)

                if not action_space[parameter_name][parameter_value]:
                    message = f'Action {action} has parameter {parameter_name} valued at the invalid value of {parameter_value}. This usually means an agent is trying to utilise information it has not discovered yet such as an ip_address or port number.'
                    return InvalidAction(action=action, error=message)

        return action

    def get_reward_breakdown(self, agent:str):
        """Returns host scores from reward calculator """
        return self.agent_interfaces[agent].reward_calculator.host_scores

    def get_reward(self, agent):
        """Returns the team's reward """
        team = [team_name for team_name, agents in self.team_assignments.items() if agent in agents]
        if len(team) > 0:
            return self.reward[team[0]]
        raise ValueError(f"Agent {agent} not in any team {self.team_assignments}")
