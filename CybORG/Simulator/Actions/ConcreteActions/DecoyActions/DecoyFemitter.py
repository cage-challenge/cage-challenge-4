from CybORG.Shared.Enums import DecoyType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Host import Host
from CybORG.Shared.Enums import OperatingSystemType
from CybORG.Simulator.Actions.AbstractActions.Misinform import DecoyFactory

class FemitterDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as an apache server
    """
    PORT = 21
    SERVICE_NAME = "femitter"
    NAME = "femitter"
    PROCESS_TYPE = 'femitter'
    PROCESS_PATH = "/usr/sbin"

    def is_host_compatible(self, host: Host) -> bool:
        has_port = super().is_host_compatible(host)
        is_windows = host.os_type == OperatingSystemType.WINDOWS
        return has_port and is_windows

class DecoyFemitter(DecoyAction):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.
    """
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = {FemitterDecoyFactory()}
