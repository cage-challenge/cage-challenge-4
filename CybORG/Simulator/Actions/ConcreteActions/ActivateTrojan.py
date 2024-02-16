from CybORG.Shared import Observation
from CybORG.Shared.Session import Session
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.RemoveOtherSessions import RemoveOtherSessions_AlwaysSuccessful
from CybORG.Simulator.State import State


class ActivateTrojan(Action):
    def __init__(self, agent, hostname: str):
        super().__init__()
        self.hostname = hostname
        self.agent = agent

    def execute(self, state: State) -> Observation:
        if self.hostname not in state.hosts:
            return Observation(False)
        # create new root session
        agent = 'red_agent_' + self.hostname.split('_')[-1]
        if agent in state.sessions and 0 in state.sessions[agent]:
            self.log(f"Agent '{agent}' already has a session '0'")
            return Observation(False)
        session = Session(
            ident=0,
            hostname=self.hostname,
            username='root',
            agent=agent,
            pid=None,
            session_type="red_drone_session",
        )
        state.add_session(session)
        # remove other sessions
        sub_action = RemoveOtherSessions_AlwaysSuccessful(session.ident, agent, level='privileged')
        return sub_action.execute(state)
