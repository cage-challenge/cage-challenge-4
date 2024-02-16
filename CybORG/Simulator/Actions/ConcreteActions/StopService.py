from CybORG.Shared import Observation
from CybORG.Simulator.Actions.ConcreteActions.TargetedLocalAction import TargetedLocalAction
from CybORG.Simulator.Host import Host
from CybORG.Simulator.State import State


class StopService(TargetedLocalAction):
    def __init__(self, agent: str, session: int, target_session: int, service: str):
        super().__init__(session, agent, target_session)
        self.service = service

    def execute_targeteted_local_action(self, state: State, target_host: Host) -> Observation:
        # find chosen service on host
        if self.service not in target_host.services:
            self.log(f"Could not find service '{self.service}' on host '{target_host.hostname}'.")
            return Observation(False)
        state.stop_service(target_host.hostname, self.service)
        return Observation(True)
