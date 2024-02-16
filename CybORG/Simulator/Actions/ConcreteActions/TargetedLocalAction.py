from CybORG.Shared import Observation
from CybORG.Simulator.Actions.ConcreteActions.LocalAction import LocalAction
from CybORG.Simulator.Host import Host
from CybORG.Simulator.State import State


class TargetedLocalAction(LocalAction):

    def __init__(self, session: int, agent: str, target_session: int):
        super().__init__(session=session, agent=agent)
        self.target_session = target_session

    def execute(self, state: State) -> Observation:
        obs = Observation(False)
        both_sessions_exist = (
            self.session in state.sessions[self.agent] and
            self.target_session in state.sessions[self.agent]
        )
        if not both_sessions_exist:
            self.log(f"Could not find both sessions '{self.session}' and '{self.target_session}' for agent '{self.agent}'.")
            return obs
        session = state.sessions[self.agent][self.session]
        target_session = state.sessions[self.agent][self.target_session]
        target_host: Host = state.hosts[target_session.hostname]

        if not (session.active and target_session.active):
            return obs

        return self.execute_targeteted_local_action(state, target_host)

    def execute_targeteted_local_action(self, state: State, target_host: Host) -> Observation:
        raise NotImplementedError
