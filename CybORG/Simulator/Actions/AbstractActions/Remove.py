

from CybORG.Shared import Observation
from .Monitor import Monitor
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.StopProcess import StopProcess
from CybORG.Shared.Session import VelociraptorServer
from CybORG.Simulator.State import State


class Remove(Action):
    """ Removes any Red User session from the target host.
    Represents killing red's shell using 'kill' or 'Taskkill'. Will not remove privileged sessions such as 'root' or 'SYSTEM' shells. That's because we assume (not realistically) that these shells also have a persistance mechanism.

    Attributes
    ----------
    session: int
        the session id of the session
    agent: str
        the name of the agent executing the action
    hostname: str
        the hostname of the host targeted by the action.
    """
    def __init__(self, session: int, agent: str, hostname: str):
        """ Instantiates the Remove class.

        Parameters
        ----------
        session: int
            the session id of the session
        agent: str
            the name of the agent executing the action
        hostname: str
            the hostname of the host targeted by the action.
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.duration = 3

    def execute(self, state: State) -> Observation:
        """ Executes the action.
        Parameters
        ----------
        state: State
            The current CybORG state.
        
        Returns
        -------
        obs: Observation
            The observation to be returned to the agent.
        """
        # perform monitor at start of action
        #monitor = Monitor(session=self.session, agent=self.agent)
        #obs = monitor.execute(state)

        parent_session: VelociraptorServer = state.sessions[self.agent][self.session]
        # find relevant session on the chosen host
        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        if len(sessions) == 0:
            self.log(f"No sessions could be found on chosen host '{self.hostname}'.")
            return Observation(False)
        session = state.np_random.choice(sessions)
        # remove suspicious processes
        if self.hostname in parent_session.sus_pids:
            for sus_pid in parent_session.sus_pids[self.hostname]:
                action = StopProcess(session=self.session, agent=self.agent, target_session=session.ident, pid=sus_pid)
                action.execute(state)
        # remove suspicious files
        return Observation(True)

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
