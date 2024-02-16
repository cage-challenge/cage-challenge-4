

from CybORG.Agents import BaseAgent
from CybORG.Shared import Scenario
from CybORG.Shared.RewardCalculator import RewardCalculator


class ScenarioGenerator:
    """The ScenarioGenerator class is an abstract class that defines the interface for other ScenarioGenerator classes.

    Attributes
    ----------
    update_each_step : bool
        default True
    background_image : str
        path for render image, default None
    """

    def __init__(self):
        self.update_each_step = True
        self.background_image = None

    def create_scenario(self, np_random) -> Scenario:
        """Creates a scenario object that can be used to initialise the state
        
        Raises
        ------
        NotImplementedError
            Abstract method that should be implemented by child classes
        """
        raise NotImplementedError

    def determine_done(self, env_controller):
        return False

    def validate_scenario(self, scenario: Scenario):
        """Takes in a scenario object and raises errors if the scenario is misconfigured or missing important information
        
        Parameters
        ----------
        scenario : Scenario
            scenario to be validated

        Raises
        ------
        ValueError
            CybORG does not currently support multiple types of interfaces on a single host
        AssertionError
            Scenario validation assertions
        """
        # check that all agents are assigned to a team
        for name, data in scenario.agents.items():
            assert data.team is not None
            assert data.team in scenario.get_teams()
            assert name in scenario.get_team_info(data.team)['agents']
            for calc in scenario.get_team_info(data.team)['calcs'].values():
                assert issubclass(type(calc), RewardCalculator)
            assert issubclass(type(data.agent_type), BaseAgent), f"agent: {name}, type {data.agent_type}"

        for host in scenario.hosts.values():
            # cannot have both wired and wireless interfaces currently because movement away from wireless will disconnect wired as well
            interface_type = None
            for interface in host.interfaces:
                if interface_type is None:
                    interface_type = interface.interface_type
                elif interface_type != interface.interface_type:
                    raise ValueError('CybORG does not currently support multiple types of interfaces on a single host')

    def __str__(self):
        return "BaseScenarioGenerator"
