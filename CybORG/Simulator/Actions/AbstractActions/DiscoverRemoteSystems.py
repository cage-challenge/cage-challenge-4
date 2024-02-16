from ipaddress import IPv4Network

from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.Pingsweep import Pingsweep
from CybORG.Simulator import State


class DiscoverRemoteSystems(Action):
    """
    A high level Red action that discovers active IP addresses of the other hosts in a subnet. 
    It calls the low level action 'Pingsweep'.
    
    Attributes
    ----------
    subnet: IPv4Network
        The ip_address of the target subnet.
    session: int
        The source session id.
    agent: str
        The name of the red agent executing the action.
    """
    def __init__(self, subnet: IPv4Network, session: int, agent: str):
        """ 
        Parameters
        ----------
        subnet: IPv4Network
            The ip_address of the target subnet.
        session: int
            The source session id.
        agent: str
            The name of the red agent executing the action.
        """
        super().__init__()
        self.subnet = subnet
        self.agent = agent
        self.session = session

    def execute(self, state: State) -> Observation:
        """ 
        Pingsweeps the target subnet for active IP addresses of the other hosts. 

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.
        
        Returns
        -------
        obs: Observation
            An observation containing an indication of the action's successful execution as True/False, and any detected host IP addresses on the subnet.
        """
        # run pingsweep on the target subnet from selected session
        sub_action = Pingsweep(session=self.session, agent=self.agent, subnet=self.subnet)
        obs = sub_action.execute(state)
        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.subnet}"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return all((
            self.name == other.name,
            self.subnet == other.subnet,
            self.agent == other.agent,
            self.session == other.session,
        ))
