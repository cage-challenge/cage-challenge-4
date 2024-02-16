# Copyright DST Group. Licensed under the MIT license.
from typing import Dict
from CybORG.Simulator.Entity import Entity
from ipaddress import IPv4Network


class Subnet(Entity):
    """ Class that holds the details about a subnet.
    
    Attributes
    ----------
    name : str
        name of the subnet
    size : int
        number of hosts in the subnet?
    hosts : List[str]
        a list of the hostnames in the subnet?
    nacls : Dict[str, Dict[str, str]]
        ?
    cidr : IPv4Network
        The network object for the subnet
    ip_addresses : list
        ?
    """
    def __init__(
        self,
        name: str,
        size: int = None,
        hosts: list = None,
        nacls: Dict[str, Dict[str, str]] = None,
        cidr: IPv4Network = None,
        ip_addresses: list = None
    ):
        super().__init__()
        self.name = name
        self.size = size
        self.hosts = hosts if hosts is not None else []
        self.nacls = nacls if nacls is not None else {}
        self.cidr = cidr
        self.ip_addresses = ip_addresses


    @classmethod
    def load(cls, name, subnet_info):
        size = subnet_info.get('Size')
        hosts = subnet_info.get('Hosts')
        nacls = subnet_info.get('NACLs')
        return cls(name=name, size=size,hosts=hosts,nacls=nacls)

    def get_state(self): #TODO
        pass

    def contains_ip_address(self, ip_address: str) -> bool:
        """Check if the specified ip address is in the subnet.
        
        Parameters
        ----------
        ip_address: str
            host ip address in string form

        Returns
        -------
        bool
            true if the specified ip address is in the subnet
        """
        return ip_address in self.cidr

    def __str__(self):
        output = f"ScenarioAgent: name={self.name} _info={self._info} \nsessions=\n"
        for session in self.starting_sessions:
            output += f"{session}"
        return output