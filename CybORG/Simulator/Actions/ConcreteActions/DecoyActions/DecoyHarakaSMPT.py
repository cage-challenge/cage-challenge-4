from CybORG.Shared.Enums import DecoyType, OperatingSystemType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Host import Host
from CybORG.Simulator.Actions.AbstractActions.Misinform import DecoyFactory

class HarakaDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as an apache server
    """
    PORT = 25
    SERVICE_NAME = "haraka"
    NAME = "haraka"
    PROCESS_TYPE = "smtp"
    PROCESS_PATH = "/usr/sbin"
    VERSION = "haraka 2.7.0"

    def is_host_compatible(self, host: Host) -> bool:
        has_port = super().is_host_compatible(host)
        is_linux = host.os_type == OperatingSystemType.LINUX
        return all((has_port, is_linux))

class DecoyHarakaSMPT(DecoyAction):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.
    """
        
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = {HarakaDecoyFactory()}
