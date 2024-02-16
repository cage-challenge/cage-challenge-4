from ipaddress import IPv4Address

from CybORG.Shared import Observation
from CybORG.Shared.Session import RedAbstractSession
from CybORG.Simulator.Actions import RemoteAction
from CybORG.Simulator.Actions.ConcreteActions.Portscan import Portscan


class DiscoverNetworkServices(RemoteAction):
    """
    A high level Red action that discovers services on a known host as a prerequisite for running an exploit.

    This calls the low level action 'PortScan', then modifies the observation. This must be used on a host in order to then
    successfully run the high level action ExploitRemoteServices.

    Attributes
    ----------
    session: int
        The source session id.
    agent: str
        The name of the red agent executing the action.
    ip_address: IPv4Address
        The ip_address of the target host.
    detection_rate: float
        The liklihood of blue detecting red's actions.
    """
    def __init__(self, session: int, agent: str, ip_address: IPv4Address):
        """ 
        Parameters
        ----------
        session: int
            The source session id.
        agent: str
            The name of the red agent executing the action.
        ip_address: IPv4Address
            The ip_address of the target host.
        """
        super().__init__(session=session, agent=agent)
        self.ip_address = ip_address
        self.agent = agent
        self.session = session
        self.detection_rate = 1

    def execute(self, state) -> Observation:
        """ 
        Discovers the services on the target host.

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.
        
        Returns
        -------
        obs: Observation
            An observation containing an indication of the action's successful execution as True/False, and a list of the target host's detected services.
        """

        # find if agent session exists 
        session = state.sessions.get(self.agent, {}).get(self.session, None)
        if session is None:
            self.log(f"Session '{self.session}' for agent '{self.agent}' not found.")
            return Observation(success=False)
        src_hostname = session.hostname

        # check if session is of type RedAbstractSession
        if not isinstance(session, RedAbstractSession):
            self.log(f"Session type is '{type(session)}' not 'RedAbstractSession'.")
            return Observation(success=False)

        # Check that there is no traffic blocks between subnets
        if self.blocking_host(state=state, src_hostname=src_hostname, other_hostname=state.ip_addresses[self.ip_address]):
            self.log(f"'{self.ip_address}' not found in session ports.")
            return Observation(success=False)

        # run portscan on the target ip address from the selected session
        sub_action = Portscan(session=self.session, agent=self.agent, ip_address=self.ip_address, detection_rate=self.detection_rate)
        obs = sub_action.execute(state)
        if str(self.ip_address) in obs.data:
            # session = state.sessions[self.agent][self.session]
            #if isinstance(session, RedAbstractSession):
            session.clearports(self.ip_address)
            for proc in obs.data[str(self.ip_address)]["Processes"]:
                for conn in proc['Connections']:
                    session.addport(self.ip_address, conn["local_port"])
        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.ip_address}"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return all((
            self.name == other.name,
            self.ip_address == other.ip_address,
            self.agent == other.agent,
            self.session == other.session,
        ))



class StealthServiceDiscovery(DiscoverNetworkServices):
    """
    The same high level red action as DiscoverNetworkServices, except with:

      - higher duration than AggressiveServiceDiscovery, with 3 ticks
      - lower detection rate of 25%

    Attributes
    ----------
    session: int
        The source session id.
    agent: str
        The name of the red agent executing the action.
    ip_address: IPv4Address
        The ip_address of the target host.
    duration: int
        The number of ticks the action takes to complete.
    detection_rate: float
        The liklihood of blue detecting red's actions.
    """
    
    def __init__(self, session: int, agent: str, ip_address: IPv4Address):
        """ 
        Parameters
        ----------
        session: int
            The source session id.
        agent: str
            The name of the red agent executing the action.
        ip_address: IPv4Address
            The ip_address of the target host.
        """
        super().__init__(session, agent, ip_address)
        self.duration = 3
        self.detection_rate = 0.25


class AggressiveServiceDiscovery(DiscoverNetworkServices):
    """
    The same high level red action as DiscoverNetworkServices, except with:

     - lower duration than StealthServiceDiscovery, the default of 1 tick
     - higher detection rate of 75%, compared to StealthServiceDiscovery

    Attributes
    ----------
    session: int
        The source session id.
    agent: str
        The name of the red agent executing the action.
    ip_address: IPv4Address
        The ip_address of the target host.
    detection_rate: float
        The liklihood of blue detecting red's actions.
    """
    def __init__(self, session: int, agent: str, ip_address: IPv4Address):
        """ 
        Parameters
        ----------
        session: int
            The source session id.
        agent: str
            The name of the red agent executing the action.
        ip_address: IPv4Address
            The ip_address of the target host.
        """
        super().__init__(session, agent, ip_address)
        self.detection_rate = 0.75

