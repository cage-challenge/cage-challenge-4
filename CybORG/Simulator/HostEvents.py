from ipaddress import IPv4Address
from typing import List

from CybORG.Shared.Enums import TransportProtocol


class HostEvents():
    """Object that holds 'events'/alerts that have happened on a specific host. 
    
    Attributes
    ----------
    network_connections : List[NetworkConnection]
        current network connection alerts
    old_network_connections : List[NetworkConnection]
        past network connection alerts
    process_creation : list
        current process creation alerts
    old_process_creation : list
        past process creation alerts

    """
    def __init__(self):
        self.network_connections: List[NetworkConnection] = []
        self.old_network_connections: List[NetworkConnection] = []
        self.process_creation = []
        self.old_process_creation = []

class NetworkConnection():
    """Object that holds a network connection event/alert.
    
    Attributes
    ----------
    local_address : IPv4Address
    local_port : int
    remote_address : IPv4Address
    remote_port : int
    pid : int
    application_protocol : str
    transport_protocol : TransportProtocol
    """
    def __init__(
        self,
        local_address: IPv4Address,
        local_port: int = None,
        remote_address: IPv4Address = None,
        remote_port: int = None,
        pid: int = None,
        application_protocol: str = None,
        transport_protocol: TransportProtocol = None
    ):
        self.local_address = local_address
        self.local_port = local_port
        self.remote_address = remote_address
        self.remote_port = remote_port
        self.pid = pid
        self.application_protocol = application_protocol
        self.transport_protocol = transport_protocol

    def get_state(self) -> dict:
        obs = {
            "local_port": self.local_port,
            "local_address": self.local_address
        }
        if self.remote_port:
            obs["remote_port"] = self.remote_port
        if self.remote_address:
            obs["remote_address"] = self.remote_address
        if self.transport_protocol:
            obs["transport_protocol"] = self.transport_protocol
        return obs
