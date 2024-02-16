from CybORG.Shared.Enums import DecoyType
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyAction import DecoyAction
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyApache import ApacheDecoyFactory
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyTomcat import TomcatDecoyFactory
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyHarakaSMPT import HarakaDecoyFactory
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions.DecoyVsftpd import VsftpdDecoyFactory

class DeployDecoy(DecoyAction):
    """
    Creates a misleading process on the designated host depending on available and compatible options.
    
    The candidate decoys in this action is specifically for CC4.

    Attributes
    ----------
    session: int
        The id of the session executing the action.
    agent: str
        The agent executing the action.
    hostname: str
        The hostname of the host targeted by the action.
    duration: int
        Time steps to take the action.
    """
        
    DECOY_TYPE = DecoyType.EXPLOIT
    CANDIDATE_DECOYS = [ApacheDecoyFactory(), TomcatDecoyFactory(), HarakaDecoyFactory(), VsftpdDecoyFactory()]

    def __init__(self, *, session: int, agent: str, hostname: str):
        super().__init__(session=session, agent=agent, hostname=hostname)
        self.duration = 2