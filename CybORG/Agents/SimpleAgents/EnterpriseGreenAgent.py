from CybORG.Agents import BaseAgent
from CybORG.Shared.ActionSpace import ActionSpace
from CybORG.Simulator.Actions import Sleep, Action
from CybORG.Simulator.Actions.GreenActions import GreenAccessService, GreenLocalWork
from ipaddress import IPv4Address
from CybORG.Shared import Observation

class EnterpriseGreenAgent(BaseAgent):
    """ Green Agent to be used for the Enterprise scenario (CC4).

    Attributes
    ----------
    own_ip : IPv4Address
        ip address of the host the green agent is located on
    fp_detection_rate : float 
        the decimal rate at which a blue detection false positive occurs from the green action (0 <= value <= 1)
    phishing_error_rate : float
        the decimal rate at which a phishing email subaction occurs due to a green action (0 <= value <= 1)
    """
    def __init__(self, name: str, own_ip: IPv4Address, np_random = None, fp_detection_rate: float = 0.01, phishing_error_rate: float = 0.01):
        """ Initialisation of the EnterpriseGreenAgent class.

        Parameters
        ----------
        name : str
            name of the agent (form of unique id)
        own_ip : IPv4Address
            ip address of the host the agent is located on
        fp_detection_rate : float
            the decimal rate at which a blue detection false positive occurs from the green action (0 <= value <= 1)
        phishing_error_rate : float
            the decimal rate at which a phishing email subaction occurs due to a green action (0 <= value <= 1)
        """
        super().__init__(name=name, np_random=np_random)
        self.own_ip = own_ip
        self.fp_detection_rate = fp_detection_rate
        self.phishing_error_rate = phishing_error_rate
        
    def train(self):
        pass

    def get_action(self, observation: Observation, action_space: dict) -> Action:
        """ Returns one of the 3 possible actions of the green agent in CC4

        The 3 possible actions are: GreenLocalWork, GreenAccessService, and Sleep. The action is chosen at random from this list.

        Parameters
        ----------
        observation : Observation
            current observation of the state
        action_space : ActionSpace
            the action space of the agent at the current step

        Returns
        -------
        Action
            One of the 3 listed actions, where each inherit from base class Action
        """
        actions = list(action_space['action'].keys())
        action = self.np_random.choice(actions)

        if action == GreenAccessService:
            return GreenAccessService(
                agent=self.name,
                src_ip = self.own_ip,
                allowed_subnets=action_space['allowed_subnets'],
                session_id=0,
                fp_detection_rate = self.fp_detection_rate
            )
        if action == GreenLocalWork:
            return GreenLocalWork(
                agent=self.name,
                session_id=0,
                ip_address = self.own_ip,
                fp_detection_rate = self.fp_detection_rate,
                phishing_error_rate = self.phishing_error_rate
            )
        return Sleep()

    def end_episode(self):
        self.__init__(name=self.name, own_ip=self.own_ip, np_random=self.np_random)

    def set_initial_values(self, action_space: ActionSpace, observation: Observation):
        pass

