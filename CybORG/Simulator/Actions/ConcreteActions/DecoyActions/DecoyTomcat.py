from CybORG.Shared.Enums import DecoyType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Actions.AbstractActions.Misinform import DecoyFactory

class TomcatDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as a tomcat server
    """
    PORT = 443
    SERVICE_NAME = "tomcat"
    NAME = "Tomcat.exe"
    PROCESS_TYPE = "webserver"
    PROPERTIES = ["rfi"]


class DecoyTomcat(DecoyAction):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.
    """
        
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = {TomcatDecoyFactory()}
