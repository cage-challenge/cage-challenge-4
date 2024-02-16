
from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.StopService import StopService
from CybORG.Simulator.State import State


class DegradeServices(Action):
    """ A Red action that attempts to degrade a service used by green in the mission.  
    This is achieved by stopping a random service currently running on a host that red has root priviliges on. 

    Attributes
    ----------
    hostname : str
        The name of the host the red agent is intefering with.
    session : int
        The source session id.
    agent : str
        The name of the red agent executing the action.
    """
    def __init__(self, hostname: str, session: int, agent: str):
        """
        Parameters
        ----------
        hostname : str
            The name of the host the red agent is intefering with.
        session : int
            The source session id.
        agent : str
            The name of the red agent executing the action.
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.duration=2

    def execute(self, state: State) -> Observation:
        """Executes the DegradeServices action.
        Action process:
            1) Check if there are sessions for the agent on this host
                - if not, return unsuccessful obs
            2) Check one of those sessions has root or sudo priviledges.
                - if not, return unsuccessful obs
            3) Check if host has services
            4) Degrade all services on host

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.
        
        Returns
        -------
        obs: Observation
            An observation indicating the action's success as True/False, and the service stopped, if any.
        """
        # (1) find session on the chosen host
        sessions_on_host = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        if len(sessions_on_host) == 0:
            return Observation(success=False)
        
        # (2) find if any session are already SYSTEM or root
        session = next((s.ident for s in sessions_on_host if s.has_privileged_access()), None)
        if session is None:
            return Observation(success=False)
        
        # (3) find if host has services
        services = [service for s_name, service in state.hosts[self.hostname].services.items() if service.active]

        if len(services) == 0:
            return Observation(success=False)

        # (4) degrade all services
        obs = Observation(success=True)

        for service in services:
            service.degrade_service_reliability()
            process_state = state.hosts[self.hostname].get_process(service.process).get_state()
            obs.add_process(hostid=self.hostname, **process_state[0])

        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return all((
            self.name == other.name,
            self.hostname == other.hostname,
            self.agent == other.agent,
            self.session == other.session,
        ))
