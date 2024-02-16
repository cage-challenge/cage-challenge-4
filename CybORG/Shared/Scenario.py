# Copyright DST Group. Licensed under the MIT license.
import itertools
import sys
from typing import List, Dict, Tuple

from CybORG.Agents import BaseAgent, SleepAgent
from CybORG.Shared import CybORGLogger
from CybORG.Shared.Session import Session
from CybORG.Simulator.Host import Host
from CybORG.Simulator.Subnet import Subnet

class ScenarioAgent(CybORGLogger):
    """A dataclass for handling scenario information of an agent

    Is essentially a wrapper around the definition for a single agent
    in the scenario dictionary, and provides a consistent interface to
    agent data without having to remember string keys, etc.
    """

    def __init__(self,
                 agent_name: str,
                 team: str,
                 starting_sessions: List[Session],
                 actions: list,
                 osint: dict,
                 allowed_subnets: list,
                 agent_type: BaseAgent = None,
                 active: bool = True,
                 default_actions: tuple = None,
                 internal_only: bool = False):
        """
        Parameters
        ----------
        agent_name: str
            Name of the agent
        team : str
            the name of the team the agent is a part of
        starting_sessions: list
            the list of sessions the agent starts with
        actions: list
            the list of actions an agent may perform
        osint: dict
            the information the agent begins a game with
        agent_type: BaseAgent
            the class that selects the default actions of the agent
        active: bool
            determines if the agent starts active or inactive at the start of the game
        default_actions : tuple
            the action_class, action_kwargs for actions being performed at the end of a turn by this agent
        internal_only : bool
            marks if an agent is restricted from using the external cyborg interfaces,
            useful if you want to enforce a default behaviour for that agent
        """
        self.name = agent_name
        self.team = team
        self.starting_sessions: List[Session] = []
        for session in starting_sessions:
            self.starting_sessions.append(session)
        self.actions = actions
        if agent_type is not None:
            self.agent_type = agent_type
        else:
            self.agent_type = SleepAgent()
        self.osint = osint
        self.allowed_subnets = allowed_subnets
        self.active = active
        self.default_actions = default_actions
        self.internal_only = internal_only

    @staticmethod
    def get_action_classes(actions):
        """Getter method for action classes contained in `CybORG.Simulator.Actions`"""
        action_classes = []
        action_module = sys.modules['CybORG.Simulator.Actions']
        for action in actions:
            action_classes.append(getattr(action_module, action))
        return action_classes

    @classmethod
    def load(cls, agent_name: str, agent_info: dict):
        """Class load method """
        return cls(
            agent_name=agent_name,
            team=agent_info.get('team'),
            actions=cls.get_action_classes(agent_info.get("actions", [])),
            starting_sessions=[Session.load(i) for i in agent_info.get("starting_sessions", [])],
            agent_type=getattr(sys.modules['CybORG.Agents'], agent_info.get("agent_type", SleepAgent))(),
            allowed_subnets=agent_info.get("AllowedSubnets", []),
            osint=agent_info.get("INT", {})
        )

class Scenario(CybORGLogger):
    """A dataclass that contains the initial state information.

    Contains getter and setter functions that are used to inform the creation of environmental objects.
    
    Attributes
    ----------
    agents : Dict[str, ScenarioAgent]
    allowed_subnets_per_mphase : dict
    hosts : Dict[str, Host]
    max_bandwidth : int
    mission_phases : Tuple[int, int, int]
    operational_firewall : bool
    predeployed : bool
    scenario_gen_type : unknown
    starting_sessions : list
    subnets : Dict[str, Subnet]
    team_agents: dict
    team_calc : dict

    """

    def __init__(
        self,
        agents: Dict[str, ScenarioAgent] = None,
        team_calcs: dict = None,
        team_agents: dict = None,
        hosts: Dict[str, Host] = None,
        subnets: Dict[str, Subnet] = None,
        mission_phases: Tuple[int, int, int] = None,
        allowed_subnets_per_mphase: dict = None,
        predeployed: bool = False,
        max_bandwidth: int = 1000
    ):
        """ 
        Parameters
        ----------
        agents : Dict[str, ScenarioAgent]
        allowed_subnets_per_mphase : dict
        hosts : Dict[str, Host]
        max_bandwidth : int
            maximum bandwidth of agent communications
        mission_phases : Tuple[int, int, int]
        predeployed : bool
            by default False
        subnets : Dict[str, Subnet]
        team_agents: dict
        team_calcs : dict
        
        """
        self.agents = agents if agents is not None else {}
        agent_starting_sessions = [agent.starting_sessions for agent in self.agents.values()]
        self.starting_sessions = list(itertools.chain(agent_starting_sessions))

        self.team_calc = self._get_team_calc(team_calcs)

        self.team_agents = team_agents if team_agents is not None else {}
        self.hosts = hosts if hosts is not None else {}
        self.subnets = subnets if subnets is not None else {}
        self.predeployed = predeployed
        self.max_bandwidth = max_bandwidth
        self.operational_firewall = False

        self.mission_phases = mission_phases
        self.allowed_subnets_per_mphase = allowed_subnets_per_mphase

        self.scenario_gen_type = None

    @classmethod
    def load(cls, scenario_dict: dict, np_random):
        """Class load method"""
        agents = {}
        for name, info in scenario_dict['Agents'].items():
            agents[name] = ScenarioAgent.load(name, info)
        hosts = {}
        for hostname, host_info in scenario_dict['Hosts'].items():
            hosts[hostname] = Host.load(hostname=hostname, host_info=host_info, np_random=np_random)
        subnets = {}
        for subnet_name, subnet_info in scenario_dict['Subnets'].items():
            subnets[subnet_name] = Subnet.load(name=subnet_name, subnet_info=subnet_info)
        return cls(agents=agents,
                   team_calcs=scenario_dict['team_calcs'],
                   team_agents=scenario_dict['team_agents'],
                   hosts=hosts,
                   subnets=subnets,
                   predeployed=scenario_dict.get("predeployed", False))

    def _get_team_calc(self, team_calcs: dict):
        new_team_calcs = {}
        if team_calcs:
            for agent_name, calc_names in team_calcs.items():
                new_team_calcs[agent_name] = {}
                for name, adversary in calc_names:
                    calc = self._get_reward_calculator(agent_name, name, adversary)
                    new_team_calcs[agent_name][name] = calc
        return new_team_calcs

    def get_scenario_gen_type(self):
        return self.scenario_gen_type

    def set_scenario_gen_type(self, scenario_gen_type):
        self.scenario_gen_type = scenario_gen_type

    def _get_reward_calculator(self, team_name, reward_calculator, adversary):
        raise NotImplementedError("Not implemented for CC4")
    #     if reward_calculator == "Baseline":
    #         calc = BaselineRewardCalculator(team_name)
    #     elif reward_calculator == 'Pwn':
    #         calc = PwnRewardCalculator(team_name, self)
    #     elif reward_calculator == 'Disrupt':
    #         calc = DistruptRewardCalculator(team_name, self)
    #     elif reward_calculator == 'None' or reward_calculator is None:
    #         calc = EmptyRewardCalculator(team_name)
    #     elif reward_calculator == 'HybridAvailabilityConfidentiality':
    #         calc = HybridAvailabilityConfidentialityRewardCalculator(team_name, self, adversary)
    #     elif reward_calculator == 'HybridImpactPwn':
    #         calc = HybridImpactPwnRewardCalculator(team_name, self)
    #     else:
    #         raise ValueError(f"Invalid calculator selection: {reward_calculator} for team {team_name}")

    #     return calc

    def get_subnet_size(self, subnetname: str) -> int:
        """gets size of subnet"""
        return self.subnets[subnetname].size

    def get_subnet_hosts(self, subnetname: str) -> List[str]:
        """gets list of hosts in subnet"""
        return self.subnets[subnetname].hosts

    def get_subnet_nacls(self, subnetname: str) -> dict:
        """gets dictionary of subnet info"""
        subnet_info = self.subnets[subnetname]
        return subnet_info.nacls

    def get_host_image_name(self, hostname: str) -> str:
        return self.hosts[hostname]["image"]

    def get_host(self, hostname: str) -> Host:
        """gets host object from hostname"""
        return self.hosts[hostname]

    def get_team_info(self, team_name: str) -> dict:
        """gets dictionary of team info for team, including calculators and agents"""
        return {'calcs': self.team_calc[team_name], 'agents': self.team_agents[team_name]}

    def get_host_subnet_names(self, hostname: str) -> List[str]:
        """gets list of hosts in same subnet as hostname"""
        return [s for s in self.subnets if hostname in self.get_subnet_hosts(s)]

    def get_agent_info(self, agent_name: str) -> ScenarioAgent:
        """gets ScenarioAgent object by agent name"""
        return self.agents[agent_name]

    def get_reward_calculators(self) -> dict:
        """gets dictionary of teams and their reward calculators"""
        return {team_name: reward_calculators for team_name, reward_calculators \
                in self.team_calc.items()}

    def get_teams(self) -> list:
        """gets a list of the team names"""
        return list(self.team_calc.keys())

    def get_end_turn_actions(self) -> dict:
        """Returns the end turn action that is performed by an agent"""
        end_turn_actions = {}
        for agent_name, data in self.agents.items():
            if data.default_actions is not None:
                end_turn_actions[agent_name] = data.default_actions
        return end_turn_actions

    def get_team_assignments(self) -> dict:
        """Returns team agents dictionary """
        return self.team_agents

    def __str__(self):
        return pprint.pformat(self._scenario, depth=7)