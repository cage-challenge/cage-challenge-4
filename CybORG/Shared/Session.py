## The following code contains work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.
## Additionally, we waive copyright and related rights in the utilized code worldwide through the CC0 1.0 Universal public domain dedication.
from ipaddress import IPv4Address
from typing import Dict, List

from CybORG.Shared.Enums import SessionType, OperatingSystemType
from CybORG.Simulator.Entity import Entity

class Session(Entity):
    """Details of the session created between an agent and a host. 
    
    Attributes
    ----------
    ident : int
        session id
    hostname : str
        name of host with session
    username : str
        username of session on host
    agent : str
        name of agent on host
    timeout : int
    pid : int
        process id linked to the session
    parent : int
        parent session id (if exists)
    session_type : str
        type of session
    active : bool
        is the session active/live
    children : {}
        session id of child sessions
    name : str
        name of session
    is_escalate_sandbox : bool
        is the session a decoy sandbox
    num_children : int
        the number of child sessions
    action_queue : list
        queuing actions of multiple time step duration
    """
    def __init__(self, ident: int, hostname: str, username: str, agent: str,
                 pid: int, timeout: int = 0, session_type: str = 'shell',
                 active: bool = True, parent=None, name=None,
                 is_escalate_sandbox: bool = False, num_children=None):
        super().__init__()
        self.ident = ident
        self.hostname = hostname
        self.username = username
        self.agent = agent
        self.timeout = timeout
        self.pid = pid
        self.parent = parent
        if isinstance(session_type, str):
            self.session_type = SessionType.parse_string(session_type)
        else:
            self.session_type = session_type
        self.active = active
        self.children = {}
        self.name = name
        self.is_escalate_sandbox = is_escalate_sandbox
        self.action_queue = []
        self.num_children = num_children

    def get_state(self):
        """Returns a dictionary representing the state of the session."""
        return {
            "username": self.username,
            "session_id": self.ident,
            "timeout": self.timeout,
            "pid": self.pid,
            "session_type": self.session_type,
            "agent": self.agent
        }

    def set_orphan(self):
        """Make the session an orphan session."""
        self.active = False
        self.parent = None

    def dead_child(self, child_id: int):
        """Remove a specific child session."""
        self.children.pop(child_id)

    def append_action(self, action: list):
        backlog_time = self.action_queue[-1][1] if len(self.action_queue) != 0 else 0 
        time_remaining = action.duration + backlog_time
        action_tuple = (action, time_remaining)
        self.action_queue.append(action_tuple)

    def has_privileged_access(self) -> bool:
        """Does the session have privileged access, based on the username."""
        return self.username in ('root', "SYSTEM")

    @classmethod
    def load(cls, session_info: dict):
        username = session_info.get("username")
        session_type = session_info.get("type")
        hostname = session_info.get("hostname")
        parent = session_info.get("parent", None)
        num_children = session_info.get("num_children_sessions", 0)
        name = session_info.get('name', None)
        session_types = {
            'VelociraptorServer': VelociraptorServer,
            SessionType.VELOCIRAPTOR_SERVER: VelociraptorServer,
            'RedAbstractSession': RedAbstractSession,
            SessionType.RED_ABSTRACT_SESSION: RedAbstractSession,
            'MetasploitServer': MSFServerSession,
            SessionType.MSF_SHELL: MSFServerSession
        }
        session_class = session_types.get(session_type, cls)
        session = session_class(
            username=username, ident=None, session_type=session_type, hostname=hostname, parent=parent,
            num_children=num_children, name=name, pid=None, agent=None
        )
        # This line is a band-aid fix due to inconsistency in how this class is used. Sometimes
        # the value is expected as an enum, sometimes as a string. Should be addressed in future
        return session

class RedAbstractSession(Session):
    """A red session that remembers previously seen information that can be used by actions."""
    def __init__(self, ident: int, hostname: str, username: str, agent: str,
                 pid: int, timeout: int = 0, session_type: str = 'shell', active: bool = True, parent=None, name=None, num_children=None, is_escalate_sandbox: bool = False):
        super().__init__(ident, hostname, username, agent, pid, timeout, session_type, active, parent, name, num_children=num_children, is_escalate_sandbox=is_escalate_sandbox)
        self.ports: Dict[IPv4Address, List[int]] = {} # a mapping of ip_addresses to previously seen open ports
        self.operating_system = {} # a mapping of hostnames to os types
        self.ot_service = None

    def addport(self, ip_address: IPv4Address, port: int):
        self.ports.setdefault(ip_address, []).append(port)

    def clearports(self, ip_address: IPv4Address):
        self.ports[ip_address] = []

    def addos(self, hostname: str, os: OperatingSystemType):
        self.operating_system[hostname] = os

class GreenAbstractSession(Session):
    # Currently a clone of RedAbstractSession
    # a session that remembers previously seen information that can be used by actions
    def __init__(self, ident: int, hostname: str, username: str, agent: str,
                 pid: int, timeout: int = 0, session_type: str = 'shell', active: bool = True, parent=None, name=None):
        super().__init__(ident, hostname, username, agent, pid, timeout, session_type, active, parent, name)
        self.ports: Dict[IPv4Address, List[int]] = {} # a mapping of ip_addresses to previously seen open ports
        self.operating_system = {} # a mapping of hostnames to os types
        self.ot_service = None

    def addport(self, ip_address: IPv4Address, port: int):
        self.ports.setdefault(ip_address, []).append(port)

    def addos(self, hostname: str, os: OperatingSystemType):
        self.operating_system[hostname] = os

class VelociraptorServer(Session):
    # a session that remembers previously seen information that can be used by actions
    def __init__(self, ident: int, hostname: str, username: str, agent: str,
                 pid: int, timeout: int = 0, session_type: str = 'shell', active: bool = True, parent=None, name=None,
                 artifacts=None, num_children=None):
        super().__init__(ident, hostname, username, agent, pid, timeout, session_type, active, parent, name, num_children=num_children)
        self.artifacts = [] if artifacts is None else artifacts  # a list of artifacts that the velociraptor collects
        self.sus_pids: Dict[str, List[int]] = {}
        self.sus_files = {}

    def add_sus_pids(self, hostname: str, pid: int):
        self.sus_pids.setdefault(hostname, []).append(pid)

class MSFServerSession(Session):

    def __init__(
        self, ident: str, hostname: str, username: str, agent: str, pid: int,
        timeout: int = 0, session_type: str = SessionType.MSF_SERVER, parent=None, name=None,
        num_children=None
    ):
        super().__init__(
            ident, hostname, username, agent, pid, timeout, session_type, parent=parent,
            name=name, num_children=num_children
        )
        self.routes = {}  # routes have the structure sessionid: subnet

    def dead_child(self, child_id: int):
        super().dead_child(child_id)
        if child_id in self.routes:
            self.routes.pop(child_id)
