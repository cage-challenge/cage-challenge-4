from CybORG.Shared.Enums import DecoyType, OperatingSystemType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Host import Host
from CybORG.Simulator.Actions.AbstractActions.Misinform import DecoyFactory

class SMSSDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as smss
    """
    PORT = 139
    SERVICE_NAME = "smss"
    NAME = "Smss.exe"
    PROCESS_TYPE = "smb"

    def is_host_compatible(self, host: Host) -> bool:
        has_port = super().is_host_compatible(host)
        is_windows = host.os_type == OperatingSystemType.WINDOWS
        return all((has_port, is_windows))

class DecoySmss(DecoyAction):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.
    """
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = {SMSSDecoyFactory()}
