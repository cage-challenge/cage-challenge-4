## The following code contains work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.
## Additionally, we waive copyright and related rights in the utilized code worldwide through the CC0 1.0 Universal public domain dedication.

import pprint
from copy import deepcopy
from datetime import datetime
from typing import Union, Optional
from ipaddress import IPv4Network, IPv4Address

import CybORG.Shared.Enums as CyEnums

BROADCAST_ADDRESS = IPv4Address('0.0.0.0')

class Observation:
    """Class that holds the observation data for the environment at a step in the episode
    
    Attributes
    ----------
    data : Dict[str, _]
        dictionary of agent observation data
    raw : str
    """

    def __init__(self, success: Union[bool, CyEnums.TernaryEnum] = CyEnums.TernaryEnum.UNKNOWN, msg:str = None):
        """
        Parameters
        ----------
        success : Union[bool, CyEnums.TernaryEnum]
            success of the action in the observation
        msg : str
            the message, if any, communicated by the agents
        """
        if not isinstance(success, CyEnums.TernaryEnum):
            success = CyEnums.TernaryEnum.parse_bool(success)
        self.data = {"success": success}
        
        if msg is not None:
            self.data['message'] = msg
        self.raw = ''

    def get_dict(self):
        """Returns the data of the observation"""
        return self.data

    def set_success(self, success: Union[bool, CyEnums.TernaryEnum]):
        """Sets the success value of the data dictionary 
        
        Parameters
        ----------
        success : Union[bool, CyEnums.TrinaryEnum]
        """
        if isinstance(success, bool):
            success = CyEnums.TernaryEnum.parse_bool(success)
        self.data["success"] = success

    def add_process(self,
                    hostid: str = None,
                    pid: int = None,
                    PID: int = None,
                    parent_pid: int = None,
                    process_name: str = None,
                    program_name: str = None,
                    service_name: str = None,
                    username: str = None,
                    path: str = None,
                    local_port: int = None,
                    remote_port: int = None,
                    local_address: Union[str, IPv4Address] = None,
                    remote_address: Union[str, IPv4Address] = None,
                    app_protocol: str = None,
                    transport_protocol: str = None,
                    status: str = None,
                    Status: str = None,
                    process_type: str = None,
                    process_version: str = None,
                    vulnerability: str = None,
                    properties: Optional[list[str]] = None,
                    **kwargs):
        """Adds a new process to a host in the observation.
        
        Parameters
        ----------
        hostid: str
        pid: int
        parent_pid: int
        process_name: str
        program_name: str
        service_name: str
        username: str
        path: str
        local_port: int
        remote_port: int
        local_address: Union[str, IPv4Address]
        remote_address: Union[str, IPv4Address]
        app_protocol: str
        transport_protocol: str
        status: str
        process_type: str
        process_version: str
        vulnerability: str
        properties: Optional[list[str]]
        """
        if hostid is None:
            hostid = str(len(self.data))
        self.data.setdefault(hostid, {})
        self.data[hostid].setdefault("Processes", [])

        new_process = {}

        pid = PID if pid is None else pid
        if pid is not None:
            pid = int(pid)
            if pid < 0:
                raise ValueError
            for old_process in self.data[hostid]["Processes"]:
                if old_process.get("PID", None) == pid:
                    new_process = old_process
                    self.data[hostid]["Processes"].remove(old_process)
                    break
            new_process["PID"] = pid

        if parent_pid is not None:
            new_process["PPID"] = int(parent_pid)

        if process_name is not None:
            new_process["process_name"] = process_name
            if isinstance(process_name, str):
                process_name = CyEnums.ProcessName.parse_string(process_name)
            new_process["Known Process"] = process_name

        if program_name is not None:
            if isinstance(program_name, str):
                program_name = CyEnums.FileType.parse_string(program_name)
            new_process["Program Name"] = program_name

        if service_name is not None:
            new_process["service_name"] = service_name

        if username is not None:
            new_process["username"] = username

        if path is not None:
            new_process["Path"] = path
            new_process["Known Path"] = CyEnums.Path.parse_string(path)

        new_connection = {}
        new_process.setdefault("Connections", [])

        if local_port is not None:
            new_connection["local_port"] = int(local_port)

        if remote_port is not None:
            new_connection["remote_port"] = int(remote_port)

        if local_address is not None:
            if isinstance(local_address, str):
                local_address = IPv4Address(local_address)
            new_connection["local_address"] = local_address
            self.add_interface_info(hostid=hostid, ip_address=local_address)

        if remote_address is not None:
            if isinstance(remote_address, str):
                remote_address = IPv4Address(remote_address)
            new_connection["remote_address"] = remote_address

        if transport_protocol is not None:
            if isinstance(transport_protocol, str):
                transport_protocol = CyEnums.TransportProtocol.parse_string(transport_protocol)
            new_connection["Transport Protocol"] = transport_protocol

        if app_protocol is not None:
            if isinstance(app_protocol, str):
                app_protocol = CyEnums.AppProtocol.parse_string(app_protocol)
            new_connection["Application Protocol"] = app_protocol

        status = status or Status
        if status is not None:
            if isinstance(status, str):
                status = CyEnums.ProcessState.parse_string(status)
            new_connection["Status"] = status

        if new_connection:
            new_process["Connections"].append(new_connection)
        elif new_process["Connections"] == []:
            new_process.pop("Connections")

        if process_type is not None:
            if isinstance(process_type, str):
                process_type = CyEnums.ProcessType.parse_string(process_type)
            new_process["process_type"] = process_type

        if process_version is not None:
            if isinstance(process_version, str):
                process_version = CyEnums.ProcessVersion.parse_string(process_version)
            new_process["Process Version"] = process_version

        if properties is not None:
            new_process["Properties"] = properties

        if vulnerability is not None:
            new_process.setdefault("Vulnerability", [])
            if isinstance(vulnerability, str):
                vulnerability = CyEnums.Vulnerability.parse_string(vulnerability)
            new_process["Vulnerability"].append(vulnerability)

        self.data[hostid]["Processes"].append(new_process)

        if self.data[hostid] == {"Processes": [{}]}:
            self.data.pop(hostid)

    def add_system_info(self,
                        hostid: str = None,
                        hostname: str = None,
                        os_type: str = None,
                        os_distribution: str = None,
                        os_version: str = None,
                        os_kernel: str = None,
                        os_patches: list = None,
                        architecture: str = None,
                        local_time: datetime = None,
                        position: tuple = None,
                        **kwargs):
        """ And new system information to a specific host in the observation.
        
        Parameters
        ----------
        hostid: str
        hostname: str
        os_type: str
        os_distribution: str
        os_version: str
        os_kernel: str
        os_patches: list
        architecture: str
        local_time: datetime
        position: tuple 
        """
        hostid = hostid or str(len(self.data))
        self.data.setdefault(hostid, {})
        self.data[hostid].setdefault("System info", {})
        sys_info: dict = self.data[hostid]["System info"]

        hostname = hostname or kwargs.get("Hostname", None)
        if hostname is not None:
            sys_info["Hostname"] = hostname

        os_type = os_type or kwargs.get("OSType", None)
        if os_type is not None:
            if isinstance(os_type, str):
                os_type = CyEnums.OperatingSystemType.parse_string(os_type)
            sys_info["OSType"] = os_type

        os_distribution = os_distribution or kwargs.get("OSDistribution", None)
        if os_distribution is not None:
            if isinstance(os_distribution, str):
                os_distribution = CyEnums.OperatingSystemDistribution.parse_string(os_distribution)
            sys_info["OSDistribution"] = os_distribution

        os_version = os_version or kwargs.get("OSVersion", None)
        if os_version is not None:
            if isinstance(os_version, str):
                os_version = CyEnums.OperatingSystemVersion.parse_string(os_version)
            sys_info["OSVersion"] = os_version

        os_kernel = os_kernel or kwargs.get("OSKernelVersion", None)
        if os_kernel is not None:
            if isinstance(os_kernel, str):
                os_kernel = CyEnums.OperatingSystemKernelVersion.parse_string(os_kernel)
            sys_info["OSKernelVersion"] = os_kernel

        os_patches = os_patches or kwargs.get("os_patches", None)
        if os_patches is not None:
            for patch in os_patches:
                if isinstance(patch, str):
                    patch = CyEnums.OperatingSystemPatch.parse_string(patch)
                sys_info.setdefault("os_patches", []).append(patch)

        architecture = architecture or kwargs.get("Architecture", None)
        if architecture is not None:
            if isinstance(architecture, str):
                architecture = CyEnums.Architecture.parse_string(architecture)
            sys_info["Architecture"] = architecture

        local_time = local_time or kwargs.get("Local Time", None)
        if local_time is not None:
            sys_info["Local Time"] = local_time

        if position is not None:
            sys_info['position'] = position

    def update_file_with_kwargs(self, kwargs):
        # TEMPORARY FOR REFACTORING. DELETE WHEN DONE.
        filename = "./keys.txt"
        if kwargs:
            existing_keys = set()
            try:
                with open(filename, 'r') as file:
                    for line in file:
                        existing_keys.add(line.strip())
            except FileNotFoundError:
                pass
            with open(filename, 'a') as file:
                for key in kwargs:
                    if key not in existing_keys:
                        file.write(key + '\n')

    def add_interface_info(self,
                           hostid: str = None,
                           interface_name: str = None,
                           ip_address: Union[str, IPv4Address] = None,
                           subnet: Union[str, IPv4Network] = None,
                           Subnet = None,
                           blocked_ips: list = None,
                           network_connections: list = None,
                           **kwargs):
        """Add new interface information to a specifc host in the observation.
        
        Parameters
        ----------
        hostid: str
        interface_name: str
        ip_address: Union[str, IPv4Address]
        subnet: Union[str, IPv4Network]
        blocked_ips: list
        """
        hostid = hostid or str(len(self.data))
        self.data.setdefault(hostid, {})
        self.data[hostid].setdefault("Interface", [])

        new_interface = {}

        if interface_name is not None:
            for interface in self.data[hostid]["Interface"]:
                if interface.get("interface_name", None) == interface_name:
                    new_interface = interface
                    self.data[hostid]["Interface"].remove(interface)
            new_interface["interface_name"] = interface_name

        if ip_address is not None:
            if isinstance(ip_address, str):
                ip_address = IPv4Address(ip_address)
            if ip_address == BROADCAST_ADDRESS:
                if self.data[hostid]["Interface"] == []:
                    self.data[hostid].pop("Interface")
                return
            for interface in self.data[hostid]["Interface"]:
                if interface.get("ip_address", None) != ip_address:
                    continue
                if len(interface) > len(new_interface):
                    new_interface = interface
                elif len(interface) == len(new_interface):
                    for k in ["interface_name", "Subnet"]:
                        if k in interface and k not in new_interface:
                            new_interface[k] = interface[k]
                self.data[hostid]["Interface"].remove(interface)
            new_interface["ip_address"] = ip_address

        subnet = subnet or Subnet
        if subnet is not None:
            if isinstance(subnet, str):
                subnet = IPv4Network(subnet)
            new_interface["Subnet"] = subnet

        if blocked_ips is not None:
            new_interface["blocked_ips"] = blocked_ips

        if network_connections is not None:
            new_interface['network_connections'] = network_connections

        self.data[hostid]["Interface"].append(new_interface)

        if self.data[hostid]["Interface"] == [{}]:
            self.data[hostid].pop("Interface")

    def add_file_info(self,
                      hostid: str = None,
                      path: str = None,
                      name: str = None,
                      vendor: str = None,
                      version: str = None,
                      file_type: str = None,
                      user: str = None,
                      user_permissions: int = None,
                      group: str = None,
                      group_permissions: int = None,
                      default_permissions: int = None,
                      last_modified_time: datetime = None,
                      signed: bool = None,
                      density: float = None,
                      **kwargs):
        """Add new file information to a specific host in the observation.
        
        Parameters
        ----------
        hostid: str
        path: str
        name: str
        vendor: str
        version: str
        file_type: str
        user: str
        user_permissions: int
        group: str
        group_permissions: int
        default_permissions: int
        last_modified_time: datetime
        signed: bool
        density: float
        """

        hostid = hostid or str(len(self.data))
        self.data.setdefault(hostid, {})
        self.data[hostid].setdefault("Files", [])

        new_file = {}
        path = path or kwargs.get("Path", None)
        if path is not None:
            new_file["Path"] = path
            new_file["Known Path"] = CyEnums.Path.parse_string(path)

        name = name or kwargs.get("File Name", None)
        if name is not None:
            new_file["File Name"] = name
            new_file["Known File"] = CyEnums.FileType.parse_string(name)

        if name is not None and path is not None:
            for file in self.data[hostid]["Files"]:
                if file.get("File Name", None) == name and file.get("Path", None) == path:
                    self.data[hostid]["Files"].remove(file)
                    new_file = file
                    break

        vendor = vendor or kwargs.get("Vendor", None)
        if vendor is not None:
            new_file["Vendor"] = CyEnums.Vendor.parse_string(vendor)

        version = version or kwargs.get("Version", None)
        if version is not None:
            new_file["Version"] = version

        file_type = file_type or kwargs.get("Type", None)
        if file_type is not None:
            if isinstance(file_type, str):
                file_type = CyEnums.FileType.parse_string(file_type)
            new_file["Type"] = file_type

        user = user or kwargs.get("username", None)
        if user is not None:
            new_file["username"] = user

        user_permissions = user_permissions or kwargs.get("User Permissions", None)
        if user_permissions is not None:
            new_file["User Permissions"] = user_permissions

        group = group or kwargs.get("Group Name", None)
        if group is not None:
            new_file["Group Name"] = group

        group_permissions = group_permissions or kwargs.get("Group Permissions", None)
        if group_permissions is not None:
            new_file["Group Permissions"] = group_permissions

        default_permissions = default_permissions or kwargs.get("Default Permissions", None)
        if default_permissions is not None:
            new_file["Default Permissions"] = default_permissions

        last_modified_time = last_modified_time or kwargs.get("Last Modified Time", None)
        if last_modified_time is not None:
            new_file["Last Modified Time"] = last_modified_time

        signed = signed or kwargs.get('Signed', None)
        if signed is not None:
            new_file['Signed'] = signed

        density = density or kwargs.get('Density', None)
        if density is not None:
            new_file['Density'] = density

        self.data[hostid]["Files"].append(new_file)

    def add_user_info(self,
                      hostid: str = None,
                      group_name: str = None,
                      gid: int = None,
                      username: str = None,
                      uid: int = None,
                      password: str = None,
                      password_hash: str = None,
                      password_hash_type: str = None,
                      logged_in: bool = None,
                      key_path: str = None,
                      Groups: list = None,
                      **kwargs):
        """Add user information to a host in the observation.
        
        Parameters
        ----------
        hostid: str
        group_name: str
        gid: int
        username: str
        uid: int
        password: str
        password_hash: str
        password_hash_type: str
        logged_in: bool
        key_path: str
        """
        hostid = hostid or str(len(self.data))

        # only add user to dict if username or uid is known
        if username is not None or uid is not None:
            self.data.setdefault(hostid, {})
            self.data[hostid].setdefault("User Info", [])

            new_user = {}

            if username is not None:
                new_user["username"] = username
                for user in self.data[hostid]["User Info"]:
                    if user.get("username", None) == username:
                        new_user = user
                        self.data[hostid]["User Info"].remove(user)

            if uid is not None:
                new_user["uid"] = uid

            password = password or kwargs.get("Password", None)
            if password is not None:
                new_user["Password"] = password

            if password_hash is not None:
                new_user["password_hash"] = password_hash

            if password_hash_type is not None:
                if isinstance(password_hash_type, str):
                    password_hash_type = CyEnums.PasswordHashType.parse_string(password_hash_type)
                new_user["password_hash_type"] = password_hash_type

            if logged_in is not None:
                new_user["logged_in"] = logged_in

            if key_path is not None:
                new_user["key_path"] = key_path

            new_group = {}
            new_user.setdefault("Groups", [])
            for groups in new_user["Groups"]:
                group_name_match = group_name is not None and groups.get("Group Name", None) == group_name
                gid_match = gid is not None and groups.get("GID", None) == gid
                if group_name_match or gid_match:
                    new_group = groups
                    new_user["Groups"].remove(groups)
                    break

            if Groups is not None:
                new_user["Groups"] = Groups
            elif group_name is not None:
                new_group["Group Name"] = group_name
                builtin_name = CyEnums.BuiltInGroups.parse_string(group_name)
                if builtin_name is not CyEnums.BuiltInGroups.UNKNOWN:
                    new_group["Builtin Group"] = builtin_name
            if gid is not None:
                new_group["GID"] = gid

            if new_group != {}:
                new_user["Groups"].append(new_group)

            if new_user["Groups"] == []:
                new_user.pop("Groups")

            self.data[hostid]["User Info"].append(new_user)

        if gid is not None and group_name is not None:
            for user in self.data.get(hostid, {}).get("User Info", []):
                for group in user.get("Groups", []):
                    gid_match = group.get("GID", None) == gid
                    group_name_match = group.get("Group Name", None) == group_name
                    if gid_match or group_name_match:
                        group["GID"] = gid
                        group["Group Name"] = group_name
                        builtin_name = CyEnums.BuiltInGroups.parse_string(group_name)
                        if builtin_name is not CyEnums.BuiltInGroups.UNKNOWN:
                            group["Builtin Group"] = builtin_name

    def add_session_info(self,
                         hostid: str = None,
                         username: str = None,
                         session_id: int = None,
                         agent: str = None,
                         timeout: int = None,
                         pid: int = None,
                         session_type: str = None,
                         **kwargs):
        """Add new session information to specific host in observation.

        Parameters
        ----------
        hostid: str
        username: str
        session_id: int
        agent: str
        timeout: int
        pid: int
        session_type: str
        """
        hostid = hostid or str(len(self.data))
        self.data.setdefault(hostid, {})
        self.data[hostid].setdefault("Sessions", [])

        new_session = {}
        if session_id is not None:
            sessions = self.data[hostid]["Sessions"]
            is_same = lambda s: s.get("agent", None) == agent and s.get("session_id", None) == session_id
            new_session = next((s for s in sessions if is_same(s)), {"session_id": session_id})

        if username is not None:
            new_session["username"] = username

        session_id = kwargs.get("session_id", None) if session_id is None else session_id
        if session_id is not None:
            new_session["session_id"] = session_id

        if timeout is not None:
            new_session["timeout"] = timeout

        pid = kwargs.get("PID", None) if pid is None else pid
        if pid is not None:
            new_session["PID"] = pid
            self.add_process(hostid=hostid, pid=pid, username=username)

        session_type = session_type or kwargs.get("Type", None)
        if session_type is not None:
            if isinstance(session_type, str):
                session_type = CyEnums.SessionType.parse_string(session_type)
            new_session["Type"] = session_type

        if agent is None:
            raise ValueError('Agent must be specified when a session is added to an observation')
        new_session["agent"] = agent

        if new_session not in self.data[hostid]["Sessions"]:
            # check we aren't adding duplicate
            self.data[hostid]["Sessions"].append(new_session)

    def combine_obs(self, obs):
        """Combines this Observation with another Observation

        Parameters
        ----------
        obs : Observation
            the other observation
        """
        if not isinstance(obs, dict):
            obs = obs.data
        for key, info in obs.items():
            if key in ["success", "action"]:
                # self.set_success(info)
                continue
            if not isinstance(info, dict):
                self.add_key_value(key, info)
                continue
            for session_info in info.get("Sessions", []):
                self.add_session_info(hostid=key, **session_info)
            for process in info.get("Processes", []):
                if 'Connections' in process:
                    for conn in process['Connections']:
                        self.add_process(hostid=key, **process, **conn)
                else:
                    self.add_process(hostid=key, **process)
            for user in info.get("User Info", []):
                self.add_user_info(hostid=key, **user)
            for file_info in info.get("Files", []):
                self.add_file_info(hostid=key, **file_info)
            for interface in info.get("Interface", []):
                self.add_interface_info(hostid=key, **interface)
            if "System info" in info:
                self.add_system_info(hostid=key, **info["System info"])
        return self

    def add_raw_obs(self, raw_obs):
        """Replaces the current raw observation with a new raw observation.
        
        Parameters
        ----------
        raw_obs
        """
        self.raw = raw_obs

    def add_key_value(self, key, val):
        self.data[key] = val

    def add_action_obs_pair(self, action, obs):
        """Adds an Action-Observation pair to this observation.

        This can be used to send back observations of multiple
        actions, in a single observation.

        Parameters
        ----------
        action : Action
            the action
        obs : Observation
            the observation
        """
        self.data.setdefault("action_obs", []).append((action, obs))

    def has_multiple_obs(self) -> bool:
        """Returns whether Observation contains multiple nested observation

        Returns
        -------
        bool
            True if Observation has nested observations
        """
        return "action_obs" in self.data

    def get_nested_obs(self):
        """Returns any nested action, observation pairs

        Returns
        -------
        list((Action, Observation))
            any nested observations
        """
        return self.data.get("action_obs", [])

    def get_sessions(self) -> list:
        """Get list of info for each session in observation

        Returns
        -------
        list(dict)
            list of session info
        """
        sessions = []
        for k, v in self.data.items():
            if not isinstance(v, dict):
                continue
            if "Sessions" not in v:
                self._log_warning(f"Observation is missing 'Sessions': {v}")
                continue
            sessions += v["Sessions"]
        return sessions

    def get_agent_sessions(self, agent: str) -> list:
        """Get list of info for each agent session in observation

        Parameters
        ----------
        agent : str
            the agent to get session info for

        Returns
        -------
        list(dict)
            list of session info
        """
        sessions = []
        for session_info in self.get_sessions():
            if session_info.get("agent", False) == agent:
                sessions.append(session_info)
        return sessions

    def filter_addresses(self,
                         ips: Union[list[str], list[IPv4Address]] = None,
                         cidrs: Union[list[str], list[IPv4Network]] = None,
                         include_localhost: bool = True):
        """Filter observation, in place, to include only certain addresses

        This function will remove any observation information for addresses
        not in the list, and will remove all observations of Hosts which have
        had atleast one address observed but where none of the observed
        addresses are in the list.

        Parameters
        ----------
        ips : list[str] or list[IPv4Address], optional
            the ip addresses to keep, if None does not filter IP addresses
            (default=None)
        cidrs : list[str] or list[IPv4Network], optional
            the cidr addresses to keep, if None does not filter Cidr addresses
            (default=None)
        include_localhost : bool, optional
            If True and ips is not None, will include localhost address
            ('127.0.0.1') in IP addresses to keep (default=True)
        """
        # convert lists to set of str for fast lookup and consistent typing
        if ips is None:
            ip_set = set()
        else:
            ip_set = set(ips)
            if include_localhost:
                ip_set.add(IPv4Address('127.0.0.1'))
            ip_set.add(IPv4Address('0.0.0.0'))

        if cidrs is None:
            cidr_set = set()
        else:
            cidr_set = set(cidrs)
            if include_localhost:
                cidr_set.add(IPv4Network('127.0.0.0/8'))

        filter_hosts = []
        for obs_k, obs_v in self.data.items():
            if isinstance(obs_v, Observation):
                obs_v.filter_addresses(ips, cidrs, include_localhost)
            elif not isinstance(obs_v, dict):
                continue

            filter_procs = []
            for i, proc in enumerate(obs_v.get("Processes", [])):
                for conn in proc.get("Connections", []):
                    for proc_k in ["local_address", "remote_address"]:
                        if proc_k in conn and conn[proc_k] not in ip_set and i not in filter_procs:
                            filter_procs.append(i)

            # Must remove indices in reverse order, else risk incorrect proc
            # being removed
            for p_idx in sorted(filter_procs, reverse=True):
                del obs_v["Processes"][p_idx]

            if "Processes" in obs_v and len(obs_v["Processes"]) == 0:
                del obs_v["Processes"]

            filter_interfaces = []
            for i, interface in enumerate(obs_v.get("Interface", [])):
                check_ip = "IP Address" in interface and interface["IP Address"] not in ip_set
                check_subnet = "Subnet" in interface and interface["Subnet"] not in cidr_set and i not in filter_interfaces
                if check_ip or check_subnet:
                    filter_interfaces.append(i)

            for i_idx in sorted(filter_interfaces, reverse=True):
                del obs_v["Interface"][i_idx]

            if "Interface" in obs_v and len(obs_v["Interface"]) == 0:
                del obs_v["Interface"]

            if len(list(obs_v.values())) == 0:
                filter_hosts.append(obs_k)

        for host_k in filter_hosts:
            del self.data[host_k]

    @property
    def success(self):
        """Success of the action that the observation 'observes'"""
        return self.data["success"]

    @property
    def action_succeeded(self) -> bool:
        """Check the success of the action that the observation 'observes'"""
        return self.data["success"] == CyEnums.TernaryEnum.TRUE

    def copy(self):
        """Creates a copy of the observation.
        
        Returns
        -------
        obs_copy : Observation
            copy of the current observation
        """
        obs_copy = Observation()
        for k, v in self.data.items():
            if isinstance(v, Observation):
                obs_copy.data[k] = v.copy()
            else:
                obs_copy.data[k] = deepcopy(v)
        return obs_copy

    def __str__(self):
        obs_str = pprint.pformat(self.data)
        return f"{self.__class__.__name__}:\n{obs_str}"

    def __eq__(self, other):
        if type(other) is not Observation:
            return False
        for k, v in self.data.items():
            if k not in other.data:
                return False
            other_v = other.data[k]
            if other_v != v:
                return False
        return True
