from CybORG.Shared import Observation
from CybORG.Simulator.Actions.Action import RemoteAction
from CybORG.Simulator.Actions.ConcreteActions.StopProcess import StopProcess
from CybORG.Simulator.State import State
from ipaddress import IPv4Address

class Withdraw(RemoteAction):
    """ A red action that removes all the agent's sessions from a local or remote host. 

    Attributes
    ----------
    session: int
        The source session id.
    agent: str
        The name of the red agent executing the action.
    ip_address: IPv4Address
        The ip_address of the red agent executing the action. Used within RemoteAction.
    hostname: str
        The name of the target host.
    """
    def __init__(self, session: int, agent: str, ip_address:IPv4Address, hostname: str):
        """ 
        Parameters
        ----------
        session: int
            The source session id.
        agent: int
            The name of the red agent executing the action.
        ip_address: IPv4Address
            The ip_address of the red agent executing the action. Used within RemoteAction.
        hostname: str
            The name of the target host.
        """
        super().__init__(session, agent)
        self.hostname = hostname
        self.ip_address = ip_address
    
    def execute(self, state: State) -> Observation:
        """
        Removes all the agent's sessions from the target host. 

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.
        
        Returns
        -------
        obs: Observation
            An observation containing an indication of the action's successful execution as True/False.
        """
        session = state.sessions[self.agent].get(self.session, None)
        if not session:
            self.log(f"Session '{self.session}' not found for agent '{self.agent}'.")
            return Observation(False)

        # can we connect to from the source to target host
        route = self.get_route(state, target=self.hostname, source=session.hostname)
        if route is None:
            self.log(f"No route found from '{session.hostname}' to '{self.hostname}'")
            return Observation(False)
        
        # find relevant sessions on the chosen host
        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        child_sessions = [s for s in sessions if s.parent!=None]
        parent_sessions = [s for s in sessions if s.parent==None and s.ident!=0]
        
        # reorder the sessions to have the parent session last
        all_agents_sessions = child_sessions + parent_sessions
        if state.sessions[self.agent][self.session].hostname==self.hostname:
            all_agents_sessions.append(state.sessions[self.agent][self.session])
        if not all_agents_sessions:
            self.log(f"No relevant sessions found for '{self.hostname}'.")
            return Observation(False)
        
        # iterate over child sessions first before eventually removing the parent process last
        for remove_session in all_agents_sessions:
            # remove all the agents processes and sessions on a host (user/ priviledged)
            action = StopProcess(
                session=self.session,
                agent=self.agent,
                target_session=remove_session.ident,
                pid=remove_session.pid,
                stop_all=True
            )
            obs = action.execute(state)
            # if any sub-action returns False then break
            if obs.success==False:
                self.log("Failed to stop process.")
                return obs
        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
