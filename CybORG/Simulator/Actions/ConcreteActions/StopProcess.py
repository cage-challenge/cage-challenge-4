from CybORG.Shared import Observation
from CybORG.Simulator.Actions.ConcreteActions.TargetedLocalAction import TargetedLocalAction
from CybORG.Simulator.Host import Host
from CybORG.Simulator.Process import Process
from CybORG.Simulator.State import State


class StopProcess(TargetedLocalAction):
    """ A sub-action for stopping processes on a host

        Attributes:
            session (int): the session id of the source session
            agent (str): the name of the agent executing the action
            target_session (int): the session id of the target session
            pid (int): The PID of the process we want to stop
            stop_all (bool): The default (False) is to only stop processes if they have user-level access. True stops all.
        """
    def __init__(self, session: int, agent: str, target_session: int, pid: int, stop_all: bool = False):
        super().__init__(session, agent, target_session)
        self.pid = pid
        self.stop_all = stop_all

    def execute_targeteted_local_action(self, state: State, target_host: Host) -> Observation:
        proc = target_host.get_process(self.pid)
        if proc is None:
            self.log(f"Could not find process '{self.pid}' for host '{target_host.hostname}'")
            return Observation(False)
        if not self.stop_all and proc.user in ('root', 'SYSTEM'):
            # There should be a log here, but I'm not sure how to describe the logic.
            return Observation(False)
        self.kill_process(state, target_host, proc)
        return Observation(True)

    def kill_process(self, state: State, host: Host, process: Process):
        agent, session_id = state.get_session_from_pid(host.hostname, pid=process.pid)
        host.processes.remove(process)
        service = next((s for s in host.services.values() if s.process == process.pid), None)
        if service:
            pid = host.create_pid()
            process.pid = pid
            host.processes.append(process)
            service.process = pid
        if session_id is None: return
        host.sessions[agent].remove(session_id)
        session = state.sessions[agent].pop(session_id)
        state.sessions_count[agent] -= 1
        if not service: return
        session = type(session)(
            hostname=host.hostname,
            username=session.username,
            session_type=session.session_type,
            agent=session.agent,
            parent=session.parent,
            timeout=session.timeout,
            ident=None,
            pid=None
        )
        state.add_session(session)
