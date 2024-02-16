from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.RestoreFromBackup import RestoreFromBackup

class Restore(Action):
    """ Reimages a host, removing all malicious activity.

    Has flat penalty of -1, representing the downtime of the host.


    Attributes
    ----------
    session: int
        the session id of the session
    agent: str
        the name of the agent executing the action
    hostname: str
        the name of the host targeted by this action.
    """
    def __init__(self, session: int, agent: str, hostname: str):
        """ Instantiates the Restore class.

        Parameters
        ----------
        session: int
            the session id of the session
        agent: str
            the name of the agent executing the action
        hostname: str
            the name of the host targeted by this action.
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.duration = 5

    def execute(self, state) -> Observation:
        """ Executes the action.
        Parameters
        ----------
        state: State
            The current CybORG state.
        
        Returns
        -------
        obs: Observation
            The observation to be returned to the user.
        """
        # perform monitor at start of action
        #monitor = Monitor(session=self.session, agent=self.agent)
        #obs = monitor.execute(state)

        if self.session not in state.sessions[self.agent]:
            self.log(f"Session '{self.session}' not found for agent '{self.agent}'.")
            return Observation(False)
        # find relevant session on the chosen host
        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        if not sessions:
            self.log(f"No sessions could be found on chosen host '{self.hostname}'.")
            return Observation(False)
        session = state.np_random.choice(sessions)
        # restore host
        action = RestoreFromBackup(session=self.session, agent=self.agent, target_session=session.ident)
        action.execute(state)
        # remove suspicious files
        return Observation(True)

    @property
    def cost(self):
        return -1

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
