## The following code contains work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.
## Additionally, we waive copyright and related rights in the utilized code worldwide through the CC0 1.0 Universal public domain dedication.
from ipaddress import IPv4Address
from typing import List

from CybORG.Shared.Enums import (ProcessType, ProcessVersion,
        TransportProtocol, DecoyType)
from CybORG.Simulator.Entity import Entity
from CybORG.Simulator.HostEvents import NetworkConnection


class Process(Entity):
    def __init__(self, process_name: str, pid: int, username: str, parent_pid: int = None, program_name: str = None,
                 path: str = None, open_ports: list = None, process_type: str = None, process_version: str = None,
                 decoy_type: DecoyType = DecoyType.NONE, properties: List[str] = None):
        """
        Parameters
        ----------
        process_name: str
            name of process
        pid: int
            id of process
        parent_pid: int
            id of parent of process
        program_name: str
            program the process is running
        username: str
            the user runnning the process
        path: str
            the path of the program the process is running
        open_ports: List[Dict[str, _]]
            listening ports of structure [{Port: int, Address: str, Application Protocol: str}, ...]
        process_type: str
            the type of process
        process_version: str
            the version of the process
        decoy_type: DecoyType
            which red actions are prevented despite appearing vulnerable
        properties: List[str]
            properties of the process to specify configuration details such as RFI presence
        """
        super().__init__()
        self.name = process_name
        self.pid = pid
        self.ppid = parent_pid
        self.program = program_name
        self.user = username
        self.path = path
        self.open_ports = open_ports
        self.decoy_type = decoy_type
        self.connections: List[NetworkConnection] = []  # Connections has the structure [{local_port, local_address, remote_port, Remote Address, Application Protocol}]
        self.properties = properties or []
        if open_ports is not None:
            for port_dict in open_ports:
                local_address = port_dict['local_address']
                if local_address == 'broadcast':
                    local_address = '0.0.0.0'
                elif local_address == 'local':
                    local_address = '127.0.0.1'
                transport_protocol = port_dict.get("transport_protocol", TransportProtocol.UNKNOWN)
                if not isinstance(transport_protocol, TransportProtocol):
                    transport_protocol = TransportProtocol.parse_string(transport_protocol)
                self.connections.append(NetworkConnection(
                    local_address=IPv4Address(local_address),
                    local_port=port_dict['local_port'],
                    transport_protocol=transport_protocol
                ))
        self.process_type = None
        if process_type is not None:
            if isinstance(process_type, str):
                self.process_type = ProcessType.parse_string(process_type)
            else:
                self.process_type = process_type
        elif isinstance(process_name, str):
            self.process_type = ProcessType.parse_string(process_name)

        if process_version is not None:
            self.version = ProcessVersion.parse_string(process_version)
        else:
            self.version = None

    def get_state(self):
        """
        Getter for the state of the process.
        
        Returns
        -------
        observations : List[dict]
         """
        observations = []
        base_obs = {
            "pid": self.pid,
            "parent_pid": self.ppid,
            "process_name": self.name,
            "program_name": self.program,
            "path": self.path,
            "process_type": self.process_type,
            "process_version": self.version,
        }
        for connection in self.connections:
            obs = base_obs.copy()
            obs.update(connection.get_state())
            if self.user is not None:
                obs["username"] = self.user
            observations.append(obs)
        if not observations:
            obs = base_obs.copy()
            obs['username'] = self.user
            observations.append(obs)
        return observations

    def is_using_port(self, port: int) -> bool:
        return any(conn.local_port == port for conn in self.connections)
    
    @classmethod
    def load(cls, info: dict):
        return cls(
            pid=info.get('PID'),
            parent_pid=info.get('PPID'),
            username=info.get("username"),
            process_name=info.get('process_name'),
            path=info.get('Path'),
            open_ports=info.get('Connections'),
            properties=info.get('Properties'),
            process_version=info.get('Process Version'),
            process_type=info.get('process_type')
        )
    
    def __str__(self):
        return f'{self.name}: {self.pid} <- {self.ppid}'
