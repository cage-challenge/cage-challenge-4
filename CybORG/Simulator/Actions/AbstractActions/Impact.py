from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.StopService import StopService
from CybORG.Simulator.State import State
from CybORG.Simulator.Host import Host
from CybORG.Shared.Session import RedAbstractSession
from CybORG.Shared.Enums import ProcessName

class Impact(Action):
    """ Impact (stop service) any OT service on the host, if red has a privileged shell on the host.

    Attributes
    ----------
    session: int
        The source session id.
    agent: str
        the name of the agent executing the action
    hostname: str
        the name of the host the action is executed on
    """
    def __init__(self, hostname: str, session: int, agent: str):
        """
        Parameters
        ----------
        session: int
            session id
        agent: str
            name of agent carrying out the action
        hostname: str
            name of the host the action is being carried out on
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.duration=2

    def execute(self, state: State) -> Observation:
        """ Execution of the Impact action that stops any OT service on the host, if red has a privileged shell on the host.

        Process:
        
        1. find session on the chosen host
        2. find if any session are already SYSTEM or root
        3. find if host has an OT service
        4. impact/stop OT service

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.
        
        Returns
        -------
        obs: Observation
            successful/unsuccessful observation
        """

        # (1) find session on the chosen host
        sessions_on_host = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        if len(sessions_on_host) == 0:
            return Observation(success=False)
        
        # (2) find if any session are already SYSTEM or root
        session = next((s.ident for s in sessions_on_host if s.has_privileged_access()), None)
        if session is None:
            return Observation(success=False)

        # (3) find if host has an OT service
        ot_services = [service for s_name, service in state.hosts[self.hostname].services.items() if s_name == ProcessName.OTSERVICE and service.active]

        if len(ot_services) == 0:
            return Observation(success=False)

        # (4) impact/stop OT service
        ot_process = [(process.pid, process.name, process) for process in state.hosts[self.hostname].processes if process.name == ProcessName.OTSERVICE]
        service_process = state.hosts[self.hostname].get_process(ot_services[0].process)
        sp_state = service_process.get_state()
        
        sub_action = StopService(
            agent=self.agent, session=self.session, service=ProcessName.OTSERVICE, target_session=session
        )
        obs = sub_action.execute(state)

        if obs.success:
            obs.add_process(self.hostname, **sp_state[0])
            state.hosts[self.hostname].increment_impact_count()
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
