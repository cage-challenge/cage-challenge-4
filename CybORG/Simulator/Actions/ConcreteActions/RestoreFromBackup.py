from CybORG.Shared import Observation
from CybORG.Simulator.Actions.ConcreteActions.TargetedLocalAction import TargetedLocalAction
from CybORG.Simulator.Host import Host
from CybORG.Simulator.State import State


class RestoreFromBackup(TargetedLocalAction):

    def execute_targeteted_local_action(self, state: State, target_host: Host) -> Observation:
        old_sessions = {}
        for agent, sessions in target_host.sessions.items():
            old_sessions[agent] = {}
            for session in sessions:
                old_sessions[agent][session] = state.sessions[agent].pop(session)
        target_host.restore()
        for agent, sessions in target_host.sessions.items():
            for session in sessions:
                state.sessions[agent][session] = old_sessions[agent][session]
        return Observation()
