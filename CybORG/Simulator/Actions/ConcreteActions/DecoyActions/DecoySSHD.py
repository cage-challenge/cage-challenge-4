from CybORG.Shared.Enums import DecoyType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Actions.AbstractActions.Misinform import DecoyFactory

class SSHDDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as an ssh server
    """
    PORT = 22
    SERVICE_NAME = "sshd"
    NAME = "Sshd.exe"
    PROCESS_TYPE = "sshd"
    PROCESS_PATH = "C:\\Program Files\\OpenSSH\\usr\\sbin"


class DecoySSHD(DecoyAction):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.
    """
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = {SSHDDecoyFactory()}
