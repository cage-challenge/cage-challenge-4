## The following code contains work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.
## Additionally, we waive copyright and related rights in the utilized code worldwide through the CC0 1.0 Universal public domain dedication.
import hashlib
from typing import Dict, Optional, List

import numpy as np


from CybORG.Shared.Enums import (OperatingSystemPatch, OperatingSystemKernelVersion,
        OperatingSystemVersion, DecoyType,
        OperatingSystemDistribution, OperatingSystemType,
        )

from CybORG.Simulator.Entity import Entity
from CybORG.Simulator.File import File
from CybORG.Simulator.HostEvents import HostEvents
from CybORG.Simulator.Interface import Interface
from CybORG.Simulator.Process import Process
from CybORG.Shared.Session import Session
from CybORG.Simulator.Service import Service

from CybORG.Simulator.User import User


class Host(Entity):
    """This class simulates the internals of a host, including files, processes and interfaces. The methods are used to change the state of the host.

    The Host class contains all the relevant data for a host along with the relevant methods for modifying that data. It is instantiated by the State object when the scenario is loaded and can be found in Simulator/Host.py.

    

    The methods in the Host class are mostly about modifying data. This is where most of the low-level work of CybORG is done as the Action objects call these methods, usually through the State object. An exception to this is the get_ephemeral port method, which generates a random port, which is particularly important when a new session is created. This is usually due to red activity, where an exploit creates a new shell, which needs to listen on a new port.
    
    Attributes
    ----------
    original_services: Dict[str, Dict[str,[bool, int]]
        Services present on the host at the beginning of the scenario. Needed for the Restore action.
    os_type: OperatingSystemType
        Differentiates between Windows and Linux hosts.
    distribution: OperatingSystemDistribution
        Differentiates between Linux Distributions and Windows generations (XP,7,8,10 etc.).
    version: OperatingSystemVersion
        Differentiates between Operating System versions. e.g. Windows XP Service Pack 1, Ubuntu 18.04.
    kernel: OperatingSystemKernelVersion
        Represents the kernel of the operating system.
    patches: List[OperatingSystemPatch]
        A list of patches applied to the operating system.
    hostname: str
        The name of the host.
    architecture: dict
    respond_to_ping: bool
    host_type: str
    users: List[User]
    files: List[File]
    original_files: List[File]
    sessions: Dict[Session]
    original_sessions: Dict[Session]
    default_process_info: List[Process]
    processes: List[Process]
    original_processes: List[Process]
    interfaces: List[Interface]
    ephemeral_ports: List[int]
    services: Dict[str, Dict[str,[bool, int]]

    """

    def __init__(
        self, np_random, system_info: dict, hostname: str = None, users: List[User] = None,
        files: List[File] = None, sessions: Dict[str, List[int]] = None, processes: List[Process] = None, interfaces: List[Interface] = None,
        info: dict = None, services: dict = None, respond_to_ping: bool = True,
        starting_position=np.array([0.0, 0.0]), host_type='host',
        confidentiality_value: str = None, availability_value: str = None
    ):
        """Instantiates the class
        
        Hosts have an large `__init__` function because they contain most of the data inside specified in the image and scenario files. This includes operating system information, interfaces, users, groups, files, processes, sessions and services. Each of these is it's own custom datatype.

        Parameters
        ----------
        np_random : numpy random generator
        system_info : dict
        hostname : str
        users : Dict[str, User]
        files: List[File]
        sessions : Dict[str, Session]
            dictionary of agent names and session objects
        processes : List[Process]
        interfaces : List[Interface]
        info : dict
        services : dict
        respond_to_ping : bool
        starting_position : np.array
        host_type : str
        """
        super().__init__()
        self.original_services: Dict[str, Service] = {}
        self.os_type = OperatingSystemType.parse_string(system_info["OSType"])
        self.distribution = OperatingSystemDistribution.parse_string(system_info["OSDistribution"])
        self.version = OperatingSystemVersion.parse_string(str(system_info["OSVersion"]))
        kernel = None
        if "OSKernelVersion" in system_info:
            kernel = OperatingSystemKernelVersion.parse_string(system_info["OSKernelVersion"])
        self.kernel = kernel
        self.patches = []
        if "Patches" in system_info:
            for patch in system_info["Patches"]:
                self.patches.append(OperatingSystemPatch.parse_string(patch))
        self.hostname = hostname
        self.architecture = system_info["Architecture"]
        self.respond_to_ping = respond_to_ping
        self.host_type = host_type
        self.users = users or []
        self.files = files or []
        self.original_files = []
        self.sessions = sessions or {}
        self.original_sessions = {}
        self.processes = processes or []
        self.default_processes = self.processes.copy()
        self.original_processes = []
        self.interfaces = interfaces or []
        self.ephemeral_ports = []
        self.services: Dict[str, Service] = services or {}
        self.info = info if info is not None else {}
        self.events = HostEvents()
        self.position = starting_position
        self.np_random = np_random
        self.impact_count = 0
        self.restore_count = 0
        self.availability_value = availability_value
        self.confidentiality_value = confidentiality_value

    @classmethod
    def load(cls, hostname: str, host_info: dict, np_random):
        services = host_info.get("Services")
        if services:
            services = {name: Service.load(info) for name, info in services.items()}
        users = host_info.get("User Info")
        if users:
            users = [User.load(info) for info in users]
        processes = host_info.get("Processes")
        if processes:
            processes = [Process.load(info) for info in processes]
        return cls(
            np_random=np_random,
            hostname=hostname,
            processes=processes,
            system_info=host_info.get("System info"),
            users=users,
            info=host_info.get("info", {}),
            services=services,
            confidentiality_value=host_info.get("ConfidentialityValue", None),
            availability_value=host_info.get("AvailabilityValue", None)
        )
    
    def get_impact_count(self):
        """Getter for impact count"""
        return self.impact_count

    def get_restore_count(self):
        """Getter for restore count"""
        return self.restore_count

    def get_state(self):
        """Getter for observation dictionary.
        
        Return
        ------
        observation : Dict[str, _]
        """
        observation = {"os_type": self.os_type, "os_distribution": self.distribution, "os_version": self.version,
                       "os_patches": self.patches, "os_kernel": self.kernel, "hostname": self.hostname,
                       "architecture": self.architecture, "position": self.position}
        return observation

    def get_ephemeral_port(self):
        """Getter for the host's ephemeral port 
        
        Returns
        -------
        port : int
            a random value between 49152 and 60000 based on the environment seed
        """
        port = self.np_random.integers(49152, 60000)
        if port in self.ephemeral_ports:
            port = self.np_random.integers(49152, 60000)
        self.ephemeral_ports.append(port)
        return port

    def add_session(self, new_session: Session):
        if new_session.pid is None:
            pid = self.create_pid()
            self.processes.append(Process(
                pid=pid, process_name=new_session.session_type, username=new_session.username
            ))
            new_session.pid = pid
        self.sessions.setdefault(new_session.agent, []).append(new_session.ident)
    
    def create_pid(self) -> int:
        pids = [0] + [process.pid for process in self.processes]
        return max(pids) + self.np_random.integers(1, 10)

    def add_user(self, username: str, password: str = None, password_hash_type: str = None):
        """Creates and returns a new user object.
        
        Returns
        -------
        new_user : User
            new user object
        """
        if self.os_type == OperatingSystemType.LINUX:
            uid_list = [999]
            for user in self.users:
                uid_list.append(user.uid)
            if username in uid_list:
                return None
            uid = max(uid_list) + 1  # Algorithm Tested in Linux: useradd
        elif self.os_type == OperatingSystemType.WINDOWS:
            uid_list = []
            for user in self.users:
                uid_list.append(user.username)
            if username in uid_list:
                return None
            uid = None
        else:
            raise NotImplementedError('Only Windows or Linux OS are Implemented')

        if password_hash_type is None:
            if self.os_type == OperatingSystemType.LINUX:
                password_hash_type = 'sha512'
            elif self.os_type == OperatingSystemType.WINDOWS:
                password_hash_type = 'NTLM'

        if password_hash_type == 'sha512':
            password_hash = hashlib.sha512(bytes(password, 'utf-8')).hexdigest()
        elif password_hash_type == 'NTLM':
            password_hash = hashlib.new('md4', password.encode('utf-16le')).hexdigest()
        else:
            raise NotImplementedError('Only sha512 and NTLM hashes have been implemented')

        new_user = User(username=username, uid=uid, password=password, password_hash=password_hash,
                        password_hash_type=password_hash_type, groups=None, logged_in=False)

        self.users.append(new_user)
        return new_user

    def get_user(self, username):
        """Get user object by username """
        return next((user for user in self.users if username == user.username), None)

    def get_interface(self, name=None, cidr=None, ip_address=None, subnet_name=None):
        """Get an interface with a selected name, subnet, or ip_address"""
        for interface in self.interfaces:
            name_match = name and interface.name == name
            cidr_match = cidr and interface.subnet == cidr
            ip_address_match = ip_address and interface.ip_address == ip_address
            if name_match or cidr_match or ip_address_match:
                return interface

    def get_process(self, pid):
        """Get process by pid"""
        return next((process for process in self.processes if process.pid == pid), None)

    def get_file(self, name: str, path=None):
        """Get file by filename"""
        for file in self.files:
            if file.name == name and (not path or file.path == path):
                return file

    def disable_user(self, username):
        user = self.get_user(username)
        if user is not None:
            return user.disable_user()
        return False

    def remove_user_group(self, user, group):
        user = self.get_user(user)
        return user is not None

    def start_service(self, service_name: str):
        """Starts a stopped service, no effect if service already started"""
        if service_name in self.services:
            if self.services[service_name]['process'] not in self.processes:
                self.services[service_name]['active'] = True
                process = self.services[service_name]['process']
                process.pid = self.create_pid()
                self.processes.append(process)
                self.services[service_name]['process'] = process
                return process, self.services[service_name]['session']
            return self.services[service_name]['process'], self.services[service_name]['session']

    # Fix bug - impact count does not increment
    def increment_impact_count(self):
        self.impact_count += 1
        
    def stop_service(self, service_name: str):
        """Stops a started service, no effect if service already stopped"""
        if service_name in self.services:
            if self.services[service_name].active:
                self.services[service_name].active = False
                return self.services[service_name].process

    def add_service(self, service_name: str, service: Service) -> Service:
        """
        Adds a service to the host, and starts it
        """
        if service_name not in self.services:
            self.services[service_name] = service
        return self.services[service_name]

    def is_using_port(self, port: int) -> bool:
        """
        Convenience method for checking if a host is using a port
        """
        return any(proc.is_using_port(port) for proc in self.processes)
    
    def create_backup(self):
        """Creates a backup of the host by filling original class attributes with current class details"""
        self.original_files = []
        if self.files is not None:
            for file in self.files:
                self.original_files.append(File(**file.get_state()[0]))

        self.original_sessions = {}
        if self.sessions is not None:
            for agent_name, sessions in self.sessions.items():
                if agent_name not in self.original_sessions:
                    self.original_sessions[agent_name] = []
                self.original_sessions[agent_name] += sessions

        self.original_processes = []
        if self.processes is not None:
            for process in self.processes:
                temp = None
                for p in process.get_state():
                    if temp is None:
                        open_port = {}
                        if 'local_port' in p:
                            open_port['local_port'] = p.pop('local_port')
                        if 'remote_port' in p:
                            open_port['remote_port'] = p.pop('remote_port')
                        if 'local_address' in p:
                            open_port['local_address'] = p.pop('local_address')
                        if 'remote_address' in p:
                            open_port['remote_address'] = p.pop('remote_address')
                        if 'transport_protocol' in p:
                            open_port['transport_protocol'] = p.pop('transport_protocol')
                        if len(process.properties) > 0:
                            p['properties'] = process.properties

                        temp = p
                        temp['open_ports'] = []
                        if len(open_port) > 0:
                            temp['open_ports'].append(open_port)
                    else:
                        open_port = {}
                        if 'local_port' in p:
                            open_port['local_port'] = p['local_port']
                        if 'remote_port' in p:
                            open_port['remote_port'] = p['remote_port']
                        if 'local_address' in p:
                            open_port['local_address'] = p['local_address']
                        if 'remote_address' in p:
                            open_port['remote_address'] = p['remote_address']
                        if 'transport_protocol' in p:
                            open_port['transport_protocol'] = p['transport_protocol']
                        if len(open_port) > 0:
                            temp['open_ports'].append(open_port)
                self.original_processes.append(Process(**temp))

        self.ephemeral_ports = []
        self.original_services = self._clone_services(self.services)

    def restore(self):
        """Restores the host by filling current class details from 'original' class attributes"""
        self.events = HostEvents()
        self.files = []
        if self.original_files is not None:
            for file in self.original_files:
                self.files.append(File(**file.get_state()))

        self.sessions = {}
        if self.original_sessions is not None:
            for agent_name, sessions in self.original_sessions.items():
                if agent_name not in self.sessions:
                    self.sessions[agent_name] = []
                self.sessions[agent_name] += sessions

        self.processes = []
        if self.original_processes is not None:
            for process in self.original_processes:
                temp = None
                for p in process.get_state():
                    if temp is None:
                        open_port = {}
                        if 'local_port' in p:
                            open_port['local_port'] = p.pop('local_port')
                        if 'remote_port' in p:
                            open_port['remote_port'] = p.pop('remote_port')
                        if 'local_address' in p:
                            open_port['local_address'] = p.pop('local_address')
                        if 'remote_address' in p:
                            open_port['remote_address'] = p.pop('remote_address')
                        if 'transport_protocol' in p:
                            open_port['transport_protocol'] = p.pop('transport_protocol')
                        if len(process.properties) > 0:
                            p['properties'] = process.properties
                        temp = p
                        temp['open_ports'] = []
                        if len(open_port) > 0:
                            temp['open_ports'].append(open_port)
                    else:
                        open_port = {}
                        if 'local_port' in p:
                            open_port['local_port'] = p['local_port']
                        if 'remote_port' in p:
                            open_port['remote_port'] = p['remote_port']
                        if 'local_address' in p:
                            open_port['local_address'] = p['local_address']
                        if 'remote_address' in p:
                            open_port['remote_address'] = p['remote_address']
                        if 'transport_protocol' in p:
                            open_port['transport_protocol'] = p['transport_protocol']
                        if len(open_port) > 0:
                            temp['open_ports'].append(open_port)
                self.processes.append(Process(**temp))

        self.ephemeral_ports = []
        self.services = self._clone_services(self.original_services)
        self.restore_count += 1

    def get_availability_value(self, default):
        return self.availability_value if self.availability_value is not None else default

    def get_confidentiality_value(self, default):
        return self.confidentiality_value if self.confidentiality_value is not None else default
    
    def update(self, state):
        pass

    def _clone_services(self, services: Dict[str, Service]) -> Dict[str, Service]:
        cloned_services = {}
        for service_name, service_info in services.items():
            cloned_services[service_name] = Service(
                    process=service_info.process, active=service_info.active
                )
        return cloned_services

    def __str__(self):
        return f'{self.hostname}'
