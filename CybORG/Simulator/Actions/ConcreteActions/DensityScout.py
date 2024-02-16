from CybORG.Shared import Observation
from CybORG.Simulator.Actions.ConcreteActions.TargetedLocalAction import TargetedLocalAction
from CybORG.Simulator.Host import Host
from CybORG.Simulator.State import State


class DensityScout(TargetedLocalAction):

    def execute_targeteted_local_action(self, state: State, target_host: Host) -> Observation:
        obs = Observation(True)
        for file in target_host.files:
            obs.add_file_info(
                hostid=target_host.hostname, name=file.name, path=file.path, density=file.density
            )
        return obs
