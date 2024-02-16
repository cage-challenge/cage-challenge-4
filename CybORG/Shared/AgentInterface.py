# Copyright DST Group. Licensed under the MIT license.

import sys
from typing import List

from CybORG.Shared import Scenario
from CybORG.Shared.ActionSpace import ActionSpace
from CybORG.Simulator.Actions import Action, Sleep
from CybORG.Shared.Observation import Observation
from CybORG.Shared.Results import Results
from CybORG.Shared.RewardCalculator import RewardCalculator

MAX_HOSTS = 5
MAX_PROCESSES = 100    # 50
MAX_CONNECTIONS = 10
MAX_VULNERABILITIES = 1
MAX_INTERFACES = 4
MAX_FILES = 10
# MAX_SESSIONS = 10    # 80
MAX_USERS = 10
MAX_GROUPS = 10
MAX_PATCHES = 10


class AgentInterface:
    """The agent interfaces for the BaseAgent instances.
    
    Attributes
    ----------
    actions : List[Action]
        list of possible actions
    action_space : ActionSpace
        ActionSpace instance
    active : bool
        flag of active (currently performing actions) agent
    agent : BaseAgent
        agent object instance
    agent_name : str
        name of the agent
    allowed_subnets : List[str]
        list of allowed subnets
    file : dict
    group_name : dict
    hostname : dict
    interface_name : dict
    internal_only : bool
        flag for the agent being an internal only agent
    last_action = None
    messages : list
        list of messages
    path : dict
    password : dict
    password_hash : dict
    process_name : dict
    scenario : Scenario
        current scenario instance
    username = dict
    """

    def __init__(self,
                 agent_obj,
                 agent_name,
                 actions,
                 allowed_subnets,
                 scenario,
                 active=True,
                 internal_only=False):
        """ 
        Parameters
        ----------
        agent_obj : BaseAgent
        agent_name : str
        actions : List[Action]
        allowed_subnets : List[str]
        scenario : Scenario
        active : bool
        internal_only : bool
        """
        self.hostname = {}
        self.username = {}
        self.group_name = {}
        self.process_name = {}
        self.interface_name = {}
        self.path = {}
        self.password = {}
        self.password_hash = {}
        self.file = {}
        self.actions = actions
        self.last_action = None
        self.allowed_subnets = allowed_subnets
        self.scenario = scenario
        self.active = active
        self.internal_only = internal_only

        self.agent_name = agent_name
        self.action_space = ActionSpace(self.actions, agent_name, allowed_subnets)
        self.agent = agent_obj
        self.agent.set_initial_values(
            action_space=self.action_space.get_action_space(),
            observation=Observation().data
        )
        self.messages = []

    def update(self, obs: dict, known: bool=True):
        """update the action space with the observation"""
        if isinstance(obs, Observation):
            obs = obs.data
        self.action_space.update(obs, known)

    def set_init_obs(self, init_obs, true_obs):
        """set and update the true and initial observations"""
        if isinstance(init_obs, Observation):
            init_obs = init_obs.data
        if isinstance(true_obs, Observation):
            true_obs = true_obs.data
        self.update(true_obs, False)
        self.update(init_obs, True)


    def get_action(self, observation: Observation, action_space: dict = None):
        """Gets an action from the agent to perform on the environment
        
        Parameters
        ----------
        observation : Observation
            agent observation space
        action_space : dict
            agent action space

        Returns
        -------
        last_action : Action
            last action performed
        """
        if isinstance(observation, Observation):
            observation = observation.data
        if action_space is None:
            action_space = self.action_space.get_action_space()
        if not self.active:
            self.last_action = Sleep()
        else:
            self.last_action = self.agent.get_action(observation, action_space)
        return self.last_action

    def end_episode(self):
        """perform agent end of episode functionality and reset the interface"""
        self.agent.end_episode()
        self.reset()

    def reset(self):
        """resets the interface with empty dictionaries"""
        self.hostname = {}
        self.username = {}
        self.group_name = {}
        self.process_name = {}
        self.interface_name = {}
        self.path = {}
        self.password = {}
        self.password_hash = {}
        self.file = {}
        self.action_space.reset(self.agent_name)
        self.agent.end_episode()

    def create_reward_calculator(self, reward_calculator: str, agent_name: str, scenario: Scenario) -> RewardCalculator:
        """Creates a reward calculator based on the name of the calculator to be used.
        
        Parameters
        ----------
        reward_calculator : str
            name of reward calculator
        agent_name : str
            name of agent
        scenario : Scenario
            current scenario object

        Returns
        -------
        : RewardCalculator
            created reward calculator
        """
        raise NotImplementedError("Not implemented for CC4")
        # calc = None
        # if reward_calculator == "Baseline":
        #     calc = BaselineRewardCalculator(agent_name)
        # elif reward_calculator == 'PwnRewardCalculator':
        #     calc = PwnRewardCalculator(agent_name, scenario)
        # elif reward_calculator == 'Disrupt':
        #     calc = DistruptRewardCalculator(agent_name, scenario)
        # elif reward_calculator == 'None' or reward_calculator is None:
        #     calc = EmptyRewardCalculator(agent_name)
        # elif reward_calculator == 'HybridAvailabilityConfidentiality':
        #     calc = HybridAvailabilityConfidentialityRewardCalculator(agent_name, scenario)
        # elif reward_calculator == 'HybridImpactPwn':
        #     calc = HybridImpactPwnRewardCalculator(agent_name, scenario)
        # else:
        #     raise ValueError(f"Invalid calculator selection: {reward_calculator} for agent {agent_name}")
        # return calc

    def get_observation_space(self):
        # returns the maximum observation space for the agent given its action set and the amount of parameters in the environment
        raise NotImplementedError

    def update_allowed_subnets(self, allowed_subnets):
        """ Updates allowed_subnets for agent

        Attributes
        ----------
        allowed_subnets : (List(str))
            agent's allowed_subnets for mission phase
        """
        self.allowed_subnets = allowed_subnets
        self.action_space.allowed_subnets = allowed_subnets