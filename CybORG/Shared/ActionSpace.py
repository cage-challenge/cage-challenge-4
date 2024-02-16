# Copyright DST Group. Licensed under the MIT license.

from inspect import signature

from CybORG.Shared import CybORGLogger
from CybORG.Shared.Enums import SessionType

MAX_SUBNETS = 10
MAX_ADDRESSES = 10
MAX_SESSIONS = 8
MAX_USERNAMES = 10
MAX_PASSWORDS = 10
MAX_PROCESSES = 50
MAX_PORTS = 50
MAX_GROUPS = 15
MAX_FILES = 20
MAX_PATHS = 20
SESSION_TYPES = (
    SessionType.MSF_SERVER, SessionType.VELOCIRAPTOR_SERVER, SessionType.RED_ABSTRACT_SESSION,
    SessionType.GREY_SESSION, SessionType.BLUE_DRONE_SESSION, SessionType.RED_DRONE_SESSION
)


class ActionSpace(CybORGLogger):
    """Action Space of the agent
    
    Attributes
    ----------
    actions : Dict[Action, bool]
        mapping of agent actions to their validity in the environment
    action_params : Dict[Action, _]
        mapping of actions to params
    allowed_subnets : List[str]
        list of allowed subnets for that action
    subnet : Dict[IPv4Network, bool]
        mapping of subnet networks to the validity of their use in the action
    ip_address : Dict[IPv4Address, bool]
        mapping of IP addresses to the validity of their use in the action
    server_session : dict
    client_session : Dict[int, bool]
        mapping of client session number to validity
    username : Dict[str, bool]
        mapping of username and validity
    password : dict
    process : Dict[int, bool]
        mapping of process number to validity
    port : dict
    hostname : Dict[str, bool]
        mapping of hostname to validity
    agent : Dict[str, bool]
        mapping of agent name to validity
    """

    def __init__(self, actions, agent, allowed_subnets):
        """Loads the inital information the agent knows about.
        
        Parameters
        ----------
        actions : List[Action]
            list of actions that the agent can take
        agent : str
            agent name
        allowed_subnets : dict
            subnets the agent is allowed to access
        """
        self.actions = {i: True for i in actions}
        self.action_params = {}
        for action in self.actions:
            self.action_params[action] = signature(action).parameters
        self.allowed_subnets = allowed_subnets
        self.subnet = {}
        self.ip_address = {}
        self.server_session = {}
        self.client_session = {i: False for i in range(MAX_SESSIONS)}
        self.username = {}
        self.password = {}
        self.process = {}
        self.port = {}
        self.hostname = {}
        self.agent = {agent: True}

    def get_name(self, action: int) -> str:
        pass

    def get_max_action_space(self):
        """Gets all the max integer values for class attributes.
        
        Returns
        -------
        max_action : Dict[str, int]
            a dictionary of class attributes and maximum integers
        """
        max_action = {
            'action': len(self.actions),
            'subnet': MAX_SUBNETS,
            'ip_address': MAX_ADDRESSES,
            'session': MAX_SESSIONS,
            'username': MAX_USERNAMES,
            'password': MAX_PASSWORDS,
            'process': MAX_PROCESSES,
            'port': MAX_PORTS,
            'target_session': MAX_SESSIONS}
        return max_action

    def get_action_space(self):
        """Gets all class attributes.
        
        Returns
        -------
        max_action : Dict[str, dict]
            a dictionary of class attributes names and values
        """
        max_action = {
            'action': self.actions,
            'allowed_subnets': self.allowed_subnets,
            'subnet': self.subnet,
            'ip_address': self.ip_address,
            'session': self.server_session,
            'username': self.username,
            'password': self.password,
            'process': self.process,
            'port': self.port,
            'target_session': self.client_session,
            'agent': self.agent,
            'hostname': self.hostname
        }
        return max_action

    def reset(self, agent):
        """Resets all class attributes to state after `__init__`.
        
        Parameters
        ----------
        agent : str
            agent name
        """
        self.subnet = {}
        self.ip_address = {}
        self.server_session = {}
        self.client_session = {i: False for i in range(MAX_SESSIONS)}
        self.username = {}
        self.password = {}
        self.process = {}
        self.port = {}
        self.agent = {agent: True}

    def get_max_actions(self, action):
        params = self.action_params[action]
        size = 1
        len_dict = {
            "session": self.server_session,
            "target_session": self.client_session,
            "subnet": self.subnet,
            "ip_address": self.ip_address,
            "username": self.username,
            "password": self.password,
            "process":self.process,
            "port": self.port,
            "agent": self.agent
        }
        for param in params.keys():
            if param not in len_dict:
                raise NotImplementedError(
                    f"Param '{param}' in action '{action.__name__}' has no"
                    " code to parse its size for action space"
                )
            size *= len(len_dict[param])
        return size

    def update(self, observation: dict, known: bool = True):
        """Updates the ActionSpace class attributes depending on the observation parameter and whether the attribute info is known.
        
        Parameters
        ----------
        observation : dict
            the current observation to update the action space with.
        known : bool
        """
        if observation is None:
            return

        for key, info in observation.items():
            if (key in ("success", 'Valid', 'action')) or (not isinstance(info, dict)):
                continue
            if "System info" in info and "Hostname" in info["System info"]:
                self.hostname[info["System info"]["Hostname"]] = known
            for interface in info.get("Interface", []):
                if "Subnet" in interface:
                    self.subnet[interface["Subnet"]] = known
                if "ip_address" in interface:
                    self.ip_address[interface["ip_address"]] = known

            for process in info.get("Processes", []):
                if "PID" in process:
                    self.process[process["PID"]] = known
                for connection in process.get("Connections", []):
                    if "local_port" in connection:
                        self.port[connection["local_port"]] = known
                    if "remote_port" in connection:
                        self.port[connection["remote_port"]] = known

            for user in info.get("User Info", []):
                if "username" in user:
                    self.username[user["username"]] = known
                if "Password" in user:
                    self.password[user["Password"]] = known

            for session in info.get("Sessions", []):
                if "session_id" in session and session['agent'] in self.agent:
                    if "Type" in session and (session["Type"] in SESSION_TYPES):
                        self.server_session[session["session_id"]] = known
                    self.client_session[session["session_id"]] = known
