


from CybORG.Shared import Observation
from .LocalAction import LocalAction
from CybORG.Simulator.State import State

class RemoveOtherSessions_Parent(LocalAction):
    def __init__(self, session: int, agent: str, level: str, success_rate: float):
        super().__init__(session, agent)
        self.level = level
        self.success_rate = success_rate

    def execute(self, state: State) -> Observation:
        obs = Observation(False)
        if self.session in state.sessions[self.agent]:
            hostname = state.sessions[self.agent][self.session].hostname
            # find sessions to remove
            sus_pids = []
            for agent, sessions in state.sessions.items():
                if agent == self.agent: continue
                for session in sessions.values():
                    if hostname != session.hostname: continue
                    user_has_privileges = (
                        session.username != 'hardware' and (self.level == 'privileged') or
                        (self.level == 'user' and session.username not in ['root', 'SYSTEM', 'hardware']) or
                        (self.level == 'low' and session.username in ['NetworkService'])
                    )
                    if user_has_privileges and (1 - self.success_rate) < state.np_random.random():
                        sus_pids.append(session.pid)
                        obs.set_success(True)
            host = state.hosts[hostname]
            for sus_pid in sus_pids:
                process = [proc for proc in host.processes if proc.pid == sus_pid][0]
                agent, session = state.get_session_from_pid(hostname, pid=sus_pid)
                host.processes.remove(process)
                host.sessions[agent].remove(session)
                state.sessions[agent].pop(session)
        return obs

    def __str__(self):
        return f"{self.__class__.__name__}"


class RemoveOtherSessions(RemoveOtherSessions_Parent):
    def __init__(self, session: int, agent: str):
        super().__init__(session, agent, 'user', 0.9)
        self.priority = 5

class RemoveOtherSessions_AlwaysSuccessful(RemoveOtherSessions_Parent):
    def __init__(self, session: int, agent: str, level: str = 'user'):
        super().__init__(session, agent, level, 1.0)
