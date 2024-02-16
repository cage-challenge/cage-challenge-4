from CybORG.Shared.Enums import DecoyType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Actions.AbstractActions.Misinform import DecoyFactory

class ApacheDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as an apache server
    """
    PORT = 80
    SERVICE_NAME = "apache2"
    NAME = "apache2"
    PROCESS_TYPE = "webserver"
    PROPERTIES = ["rfi"]
    PROCESS_PATH="/usr/sbin"


class DecoyApache(DecoyAction):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.
    """
        
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = {ApacheDecoyFactory()}
