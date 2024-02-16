# Copyright DST Group. Licensed under the MIT license.
import queue
from threading import Thread, Event
import warnings
from typing import Any, Tuple, Union

import gym
import numpy as np
import pygame
from gym.utils import seeding

from CybORG.Simulator.SimulationController import SimulationController
from CybORG.Shared import Observation, Results, CybORGLogger
from CybORG.Shared.Enums import DecoyType
from CybORG.Shared.Scenarios.ScenarioGenerator import ScenarioGenerator
from CybORG.Simulator.Actions import DiscoverNetworkServices, DiscoverRemoteSystems, ExploitRemoteService, \
    InvalidAction, \
    Sleep, PrivilegeEscalate, Impact, Remove, Restore, RemoveOtherSessions
from CybORG.Simulator.Actions.ConcreteActions.ActivateTrojan import ActivateTrojan
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import BlockTraffic, AllowTraffic
from CybORG.Simulator.Actions.ConcreteActions.ExploitActions.ExploitAction import ExploitAction
# from CybORG.Simulator.Scenarios import DroneSwarmScenarioGenerator, FileReaderScenarioGenerator
from CybORG.Tests.utils import CustomGenerator
# from CybORG.render.pygame_user_interface import SimulationGUI
# from CybORG.render.renderer import Renderer


class CybORG(CybORGLogger):
    """The main interface for the Cyber Operations Research Gym.

    The primary purpose of this class is to provide a unified interface for the CybORG simulation and emulation
    environments. The user chooses which of these modes to run when instantiating the class and CybORG initialises
    the appropriate environment controller.

    This class also provides the external facing API for reinforcement learning agents, before passing these commands
    to the environment controller. The API is intended to closely resemble that of OpenAI Gym, but is also inspired by PettingZoo for MultiAgent aspects.

    Attributes
    ----------
    scenario_generator: ScenarioGenerator
        ScenarioGenerator object that creates scenarios.
    environment: str
        The environment to use. CybORG currently only supports 'sim' (default='sim').
    env_config: dict
        Configuration keyword arguments for environment controller
        (See relevant Controller class for details), (default=None).
    agents: dict
        Defines the agent that selects the default action to be performed if the external agent does not pick an action
        If None agents will be loaded from description in scenario file (default=None).
    """
    supported_envs = ['sim']

    def __init__(self,
                 scenario_generator: ScenarioGenerator,
                 agents: dict = None,
                 seed: Union[int, CustomGenerator] = None):
        """Instantiates the CybORG class.

        Parameters
        ----------
        scenario_generator: ScenarioGenerator
            ScenarioGenerator object that creates scenarios.
        agents: dict, optional
            Defines the agent that selects the default action to be performed if the external agent does not pick an action
            If None agents will be loaded from description in scenario file (default=None).
        seed : Union[int, CustomGenerator]
            optional seed for random number generator
        """
        assert issubclass(type(scenario_generator),
                          ScenarioGenerator), f'Scenario generator object of type {type(scenario_generator)} must be a subclass of ScenarioGenerator'
        self.scenario_generator = scenario_generator
        self._log_info(f"Using scenario generator {str(scenario_generator)}")
        if seed is None or isinstance(seed, int):
            self.np_random, seed = seeding.np_random(seed)
        else:
            self.np_random = seed
        self.environment_controller = SimulationController(self.scenario_generator, agents, self.np_random)

        # # CC4: GUI not implemented for CC4, disable by default
        # self._disable_gui = True

        # self.renderer: Renderer = None
        # self.gui: Thread = None
        # self.gui_actions_queue: queue.Queue = None

        # # used to signal termination to the threads
        # self.stop_event: Event = None if self._disable_gui else Event()

    # def _gui(f):
    #     def _impl(self, *args, **kwargs):
    #         if not self._disable_gui:
    #             f(self, *args, **kwargs)
    #     return _impl

    def parallel_step(self, actions: dict = None, messages: dict = None, skip_valid_action_check: bool = False) -> Tuple[dict, dict, dict, dict]:
        """Performs a step in CybORG accepting multiple external agent inputs.
            
            Used by multiagent scenarios such as CAGE Challenge 3 and CAGE Challenge 4. Actions conceptually occur simultaneously, but in reality occur sequentially according to priority order.

                Parameters
                ----------
                actions: dict
                    the actions to perform
                skip_valid_action_check: bool
                    a flag to diable the valid action check
                Returns
                -------
                tuple
                    the result of agent performing the action
                """
        if actions is not None and len(actions) > 0:
            agents = list(actions.keys())
        else:
            agents = []
        if actions is self.environment_controller.action:
            warnings.warn("Reuse of the actions input. This variable is altered inside the simulation "
                          "and may contain actions from previous steps")
        self.environment_controller.step(actions, skip_valid_action_check)
        self.environment_controller.send_messages(messages)
        agents = set(agents + self.active_agents)
        return {agent: self.get_observation(agent) for agent in agents}, \
               {agent: self.environment_controller.get_reward(agent) for agent in agents}, \
               {agent: self.environment_controller.done for agent in agents}, {}

    def step(self, agent: str = None, action=None, messages: dict = None,
         skip_valid_action_check: bool = False) -> Results:
        """Performs a step in CybORG for the given agent.
        Enables compatibility with older versions of CybORG including CAGE Challenge 1 and CAGE Challenge 2

        Parameters
        ----------
        agent: str, optional
            the agent to perform step for (default=None)
        action: Action
            the action to perform
        skip_valid_action_check: bool
            a flag to diable the valid action check
        Returns
        -------
        Results
            the result of agent performing the action
        """
        if action is None or agent is None:
            action = {}
        else:
            action = {agent: action}
        self.environment_controller.step(action, skip_valid_action_check)
        self.environment_controller.send_messages(messages)
        if agent is None:
            result = Results(observation=Observation().data)
        else:
            reward = round(sum(self.environment_controller.get_reward(agent).values()), 1)
            action_space = self.environment_controller.agent_interfaces[agent].action_space.get_action_space()
            result = Results(
                observation=self.get_observation(agent),
                done=self.environment_controller.done,
                reward=reward,
                action_space=action_space,
                action=self.environment_controller.action[agent]
            )
        return result

    def start(self, steps: int, log_file=None, verbose=False) -> bool:
        """Start CybORG and run for a specified number of steps.

        Parameters
        ----------
        steps: int
            the number of steps to run for
        log_file: File, optional
            a file to write results to (default=None)

        Returns
        -------
        bool
            whether goal was reached or not
        """
        return self.environment_controller.start(steps, log_file, verbose)

    def get_true_state(self, info: dict) -> dict:
        """Create's a dictionary containing the requested information from the state.

        Intended to be used for debugging and evaluation purposes. Agents should not have visibility of the unfiltered state.
        Info dictionary should have hostnames as keys. Each host is passed a dictionary whose keys define the subcomponents to pull out and whose values specify which attributes. For example:
            {'HostnameA': {'Interfaces':'ip_address','Services':'Femitter'},
             'HostnameB': {'Interfaces':'All', 'Files': 'All', 'Sessions':'All'},
             'HostnameC': {'User info': 'All', 'System info': 'All'}
             }

        Parameters
        ----------
        info: dict


        Returns
        -------
        Results
            The information requested.
        """
        return self.environment_controller.get_true_state(info).data

    def get_agent_state(self, agent_name) -> dict:
        """Get the initial observation of the specified agent.

        Parameters
        ----------
        agent_name : str
            The agent to get the initial observation for.
            Set as 'True' to get the true-state.

        Returns
        -------
        : dict
            The initial observation of the specified agent.
        """
        return self.environment_controller.get_agent_state(agent_name).data

    def reset(self, agent: str = None, seed: int = None) -> Results:
        """Resets CybORG and gets initial observation and action-space for the specified agent.

        Note
        ----
        This method is a critical part of the OpenAI Gym API.

        Parameters
        ----------
        agent: str, optional
            The agent to get the initial observation for.
            If None will return the initial true-state (default=None).

        Returns
        -------
        Results
            The initial observation and actions of an agent.
        """
        if seed is not None:
            self.np_random, seed = seeding.np_random(seed)
        self.environment_controller.reset(np_random=self.np_random)
        if agent is None:
            return Results(observation=self.environment_controller.init_state)
        obs = self.environment_controller.observation[agent].get_combined_observation().data
        action_space = self.environment_controller.agent_interfaces[agent].action_space.get_action_space()
        return Results(observation=obs, action_space=action_space)

    def get_observation(self, agent: str) -> dict:
        """Get the last observation for an agent.

        Parameters
        ----------
        agent: str
            Name of the agent to get observation for.

        Returns
        -------
        Observation
            The agent's last observation.
        """
        return self.environment_controller.get_last_observation(agent).data  # Temp for stability

        # observation = self.environment_controller.get_last_observation(agent) # Required for time
        # for name, obs in observation.items():
        #    observation[name] = obs.data

        # return observation

    def get_action_space(self, agent: str):
        """Returns the most recent action space for the specified agent.

        Action spaces may change dynamically as the scenario progresses.

        Parameters
        ----------
        agent: str
            Name of the agent to get action space for.

        Returns
        -------
        dict
            The action space of the specified agent.

        """
        return self.environment_controller.get_action_space(agent)

    def get_observation_space(self, agent: str):
        """Returns the most recent observation for the specified agent.

        Parameters
        ----------
        agent: str
            Name of the agent to get observation space for.

        Returns
        -------
        dict
            The observation of the specified agent.

        """
        return self.environment_controller.get_observation_space(agent)

    def get_last_action(self, agent: str):
        """Returns the last executed action for the specified agent.

        Parameters
        ----------
        agent: str
            Name of the agent to get last action for.

        Returns
        -------
        Action
            The last action of the specified agent.

        """
        return self.environment_controller.get_last_action(agent)

    def set_seed(self, seed: int):
        """Creates an np_random object to seed all internal CybORG randomisations.

        Parameters
        ----------
        seed: int
            The seed to pass to the np_random object
        """
        self.np_random, seed = seeding.np_random(seed)
        self.environment_controller.set_np_random(self.np_random)

    def get_ip_map(self):
        """Returns a mapping of hostnames to ip addresses for the current scenario.

        Returns
        -------
        ip_map
            The ip_map indexed by hostname.

        """
        return self.environment_controller.hostname_ip_map

    def get_cidr_map(self):
        '''Returns a mapping of hostnames to subnet cidrs for the current scenario.

        Returns
        -------
        cidr_map
            The ip_map indexed by hostname.
        '''
        return self.environment_controller.subnet_cidr_map

    def get_rewards(self):
        """Returns the rewards for each agent at the last executed step.

        Returns
        -------
        rewards: dict
            The rewards indexed by team name.

        """
        return self.environment_controller.reward

    def get_reward_breakdown(self, agent: str):
        '''Returns a dictionary mapping hosts to the rewards they contribute to the overall total.

        Parameters
        ----------
        agent: str
            The agent to see the reward breakdown for.
            
        Returns
        -------
        rewards: dict
            The rewards indexed by hostname.
        '''
        return self.environment_controller.get_reward_breakdown(agent)

    def get_attr(self, attribute: str) -> Any:
        """Returns the specified attribute if present.

        Intended to give wrappers access to the base CybORG class.

        Parameters
        ----------
        attribute: str
            Name of the requested attribute.

        Returns
        -------
        Any
            The requested attribute.
        """
        if hasattr(self, attribute):
            return self.__getattribute__(attribute)
        return None

    @property
    def agents(self) -> list:
        """Returns all external-facing agents.
        
        Returns
        -------
        Agents: List[str]
            List of names of all external-facing agents.
        """
        return [agent_name for agent_name, agent_info in self.environment_controller.agent_interfaces.items() if not agent_info.internal_only]

    @property
    def active_agents(self) -> list:
        '''Returns all active agents.

        An active agent must have an active shell.

        Returns
        -------
        agents: List[str]
            List of names of all active agents.
        '''
        return self.environment_controller.get_active_agents()

    def get_agent_ids(self):
        '''Returns the ids for the agents.
        Returns
        -------
        agent_ids: List[str]
            List of agent ids.
        '''
        return list(self.environment_controller.agent_interfaces.keys())

    def close(self, **kwargs):
        '''Shuts down CybORG.

        Designed for the emulator.

        Parameters
        ----------
        **kwargs
            Keyword Arguments to pass to the environment_controller.
        '''
        if not self._disable_gui:
            self.gui_actions_queue.put('shutdown')

    @property
    def unwrapped(self):
        '''Returns CybORG without any wrappers.
        Returns
        -------
        cyborg: CybORG
            The CybORG main class.
        '''
        return self

    def get_message_space(self, agent: str) -> gym.Space:
        '''Returns an OpenAI Gym Space that contains possible values for messages.

        Parameters
        ----------
        agent: str
            The agent whose message space is being returned.

        Returns
        -------
        message_space: gym.Space
            The message space being returned.
        '''
        return self.environment_controller.get_message_space(agent)

    # --- GUI functions removed in CC4 trim as not supported ---

    def get_renderer(self):
        pass

    def gui_thread(self):
        pass

    def stop_gui(self):
        pass

    def render(self, mode='human'):
        pass

    def add_red_actions(self, data):
        pass

    def add_blue_actions(self, data, red_action):
        pass

    def get_render_data(self):
        pass

    def add_rewards(self, data):
        pass

    def update_symbols(self, data, red_hosts, red_low_hosts, blue_hosts, blue_protected_hosts):
        pass