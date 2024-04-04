from typing import List
from ipaddress import IPv4Address

from CybORG.Simulator.Actions.Action import RemoteAction
from CybORG.Simulator.State import State
from CybORG.Shared import Observation
from CybORG.Simulator.HostEvents import NetworkConnection
from CybORG.Shared.Enums import ProcessName


class GreenAccessService(RemoteAction):
    """A Green Agent action for communicating with a server.

    Attributes
    ----------
    src_ip : IPv4Address 
        ip address of source host
    dest_ip : IPv4Address
        ip address of destination host
    dest_port : int
        port number of destination host to be contacted
    allowed_subnets : list[str]
        list of subnets that can be reached according to the mission phase
    fp_detection_rate : float 
        the decimal probability that a false positive is created for blue (default=0.01)

    """
    
    def __init__(self, agent: str, session_id: int, src_ip: IPv4Address, allowed_subnets: List[str], fp_detection_rate: float):
        """Initialisation of green agent access service action.

        Parameters
        ----------
        agent : str
            the name of the agent performing the access service action (source agent)
        session_id : int 
            source agent session id (default=0)
        src_ip : IPv4Address
            ip address of source host
        allowed_subnets : list[str] 
            list of subnets that can be reached according to the mission phase
        fp_detection_rate : float
            the decimal probability that a false positive is created for blue (default=0.01)
        
        """
        super().__init__(agent=agent, session=session_id)
        self.ip_address = src_ip
        self.allowed_subnets = allowed_subnets
        self.dest_ip = ""
        self.dest_port = ""
        self.fp_detection_rate = fp_detection_rate

    def _get_my_used_route(self, state: State) -> List[str]:
        """Finds the route used by the action and returns the hostnames along that route.
        
        Parameters
        ----------
        state : State 
            state of simulation at current step

        Returns
        -------
        List[str] 
            list of hostnames that occur along the path from src to dest
        """
        source = state.ip_addresses[self.ip_address]
        target = state.ip_addresses[self.dest_ip]

        return self.get_route(state=state, source=source, target=target)

    def random_reachable_ip(self, state: State) -> IPv4Address:
        """Finds an ip address that the green agent believes to be reachable.

        The green agent has additional knowledge of the subnets that can be access for each mission. 
        This should be applied to its access service choice, as it serves no purpose for someone to try to access a service they know they cannot. 
        This knowledge is found in the agent's ActionSpace variable named allowed_subnets. 
            
        - If the agent knows that it's in an 'allowed_subnet' subnet, it can try to reach out to any other allowed_subnet (including its own). 
        - If the agent knows that its subnet has been intentionally cut off due to mission plans (i.e. not in the 'allowed_subnet' list), it will only try to reach out within its own subnet.

        The green agent will only reach out to host that are not themselves (as this is covered under the GreenLocalWork Action), and hosts which are servers. 

        Parameters
        ----------
        state : State 
            state of simulation at current step

        Returns
        -------
        : IPv4Address
            ip address of target host

        """
        reachable_hosts = []
        all_allowed_subnet_cidrs = []
        src_subnet = state.hostname_subnet_map[state.ip_addresses[self.ip_address]]
        if src_subnet in self.allowed_subnets:
            # if the source host is in an allowed subnet, then list all allowed subnets
            for subnet_name in self.allowed_subnets:
                all_allowed_subnet_cidrs.append(state.subnet_name_to_cidr[subnet_name])
        else:
            # if the source host is not in an allowed subnet, then only list that subnet
            all_allowed_subnet_cidrs.append(state.subnet_name_to_cidr[src_subnet])

        # Only list the host ips of hosts in the list of subnets, that are servers and not the source host
        for host_ip in state.ip_addresses:
            if 'server' in state.ip_addresses[host_ip] and not host_ip == self.ip_address:
                for subnet in all_allowed_subnet_cidrs:
                    if host_ip in subnet:
                        reachable_hosts.append(host_ip)

        if len(reachable_hosts) < 0:
            return None
        else:
            return state.np_random.choice(reachable_hosts)

    def available_dest_service(self, state) -> bool:
        """Check if there is an active, reliable service to connect to; prioritising OT services."""
        dest_host_name = state.ip_addresses[self.dest_ip]

        if ProcessName.OTSERVICE in state.hosts[dest_host_name].services.keys():
            service = state.hosts[dest_host_name].services[ProcessName.OTSERVICE]
            if service.active and state.np_random.integers(100) < service.get_service_reliability():
                return True
            else:
                return False
        else:
            available_services = [service for service in state.hosts[dest_host_name].services.values() if session.active]
            if len(available_services) > 0:
                service = state.np_random.choice(available_services)
                if state.np_random.integers(100) < service.get_service_reliability():
                    return True
            return False



    def execute(self, state: State) -> Observation:
        """Have the green agent attempt to access a service from another server host, checking routability.

        Deciding the destination host is done by random_reachable_ip(). 
        If there are no reachable hosts, then there are no hosts that meet the green agent requirements that are available. 
        This should not be possible without red actions having taken place, therefore the action will be unsuccessful.

        The destination host is then checked against the following points:

        1. Check if the host is blocked
            - If so, add a network_connections event to the host and return an unsuccessful observation
            
        2. At the fp_detection_rate, add an erroneous network_connections event to the host

        If a (unsucessful) observation has not yet been returned, the action has been sussessful and a successful observation is returned.
 
        Notes
        -----
        function closely mimics SendData action execute()

        Parameters
        ----------
        state : State 
            state of simulation at current step
            
        Returns
        -------
        obs : Observation
            observation with true or false success

        """

        obs = Observation(False)

        self.dest_ip = self.random_reachable_ip(state)
        if self.dest_ip is None:
            self.log("No reachable hosts.")
            return obs
        
        if not self.available_dest_service:
            return obs

        
        from_host = state.ip_addresses[self.dest_ip]
        from_host_obj = state.hosts[from_host]
        self.dest_port = state.hosts[from_host].get_ephemeral_port()
        from_subnet = state.hostname_subnet_map[from_host].value

        to_host = state.ip_addresses[self.ip_address]
        to_subnet = state.hostname_subnet_map[to_host].value

        # (a) Check for firewall blocks of inbound or outbound connections to and from the to/from subnets
        connection_failure_flag = False
        if to_subnet in state.blocks.keys():
            if from_subnet in state.blocks[to_subnet]:
                connection_failure_flag = True
        if from_subnet in state.blocks.keys():
            if to_subnet in state.blocks[from_subnet]:
                connection_failure_flag = True
        
        # If they are blocked, then make an event
        if connection_failure_flag:
            event = NetworkConnection(
                local_address=state.hostname_ip_map[from_host],
                remote_address=state.hostname_ip_map[to_host],
                remote_port=8800)
            from_host_obj.events.network_connections.append(event)
            return obs

        # (b) false positive detection by Blue
        if state.np_random.random() < self.fp_detection_rate:
            
            event = NetworkConnection(
                local_address=self.ip_address,
                remote_address=self.dest_ip,
                remote_port=self.dest_port
            )
            from_host_obj.events.network_connections.append(event)

        obs.set_success(True)
        return obs
    
    def __str__(self):
        return f"{self.__class__.__name__} {self.dest_ip} {self.dest_port}"
