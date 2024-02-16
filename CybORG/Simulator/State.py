## The following code contains work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.
## Additionally, we waive copyright and related rights in the utilized code worldwide through the CC0 1.0 Universal public domain dedication.
import copy
from datetime import datetime
from gym.utils.seeding import RandomNumberGenerator
from ipaddress import IPv4Address, IPv4Network
from math import sqrt
from typing import Dict, List


import networkx as nx
from networkx import connected_components

from CybORG.Shared import Scenario, CybORGLogger
from CybORG.Shared.Enums import SessionType
from CybORG.Shared.Observation import Observation
from CybORG.Simulator.File import File
from CybORG.Simulator.Host import Host
from CybORG.Shared.Session import Session
from CybORG.Simulator.Subnet import Subnet


class State(CybORGLogger):
    """Simulates the Network State.

    This class contains all the data for the simulated network, including ips, subnets, hosts and sessions.
    The methods mostly modify the network state, but tend to delegate most of the work to the Host class.

    Attributes
    ----------
    np_random: numpy.random._generator.Generator
        Used to resolve all random events inside CybORG.
    scenario: Scenario
        Object used to create initial State from Scenario Object.
    subnet_name_to_cidr: Dict[str, IPv4Network]
        Dictionary mapping subnet name to matching cidr address.
    ip_addresses: Dict[IPv4Address, str]
        Dictionary mapping ip address to corresponding hostname.
    hostname_ip_map: Dict[str, IPv4Address]
        Dictionary mapping hostname to corresponding ip address.
    hostname_subnet_map: Dict[str, SUBNET]
        Dictionary mapping hostname to corresponding subnet Enum object.
    hosts: Dict[str, Host]
        Dictionary  mapping hostname to matching Host object.
    sessions: Dict[str, Dict[int, Session]]
        Dictionary mapping agent name to dictionary containing its corresponding sessions. Sessions objects are indexed by session ids, which are integers.
    subnets: Dict[IPv4Network, Subnet]
        Dictionary mapping ip address to corresponding subnet.
    link_diagram: networkx.classes.graph.Graph
        NetworkX graph representing which hosts can directly communicate with each other. Used for routing actions between hosts.
    connected_components: List[Set[str]]
        List of sets of hostnames representing hosts that are all connected together. Used to identify which hosts have no route between them.
    sessions_count: Dict[str, int]
        Dictionary mapping agent name to the number of sessions it controls across the network.
    mission_phase: int
        Integer representing the current mission phase.
    original_time: datetime.datetime
        Time fixed at Jan 1 2020. Unused, but intended to timestamp backup of Restored host.
    time: datetime.datetime
        Simulated current time. Unused, but intended for timestamping purposes.
    operational_firewall: bool
        Boolean represeting whether the Operational Server in Scenario 2 has a firewall protecting it. Unused in later scenarios.
    blocks: Dict[str:List[str]]
        Dictionary mapping hostames to a list of hostnames they will block actions from.
    """
    def __init__(self, scenario: Scenario, np_random: RandomNumberGenerator):
        """Instantiates State class.

        Parameters
        ----------
        scenario: Scenario
            Object used to create initial State from Scenario Object.
        np_random: numpy.random._generator.Generator
            Used to resolve all random events inside CybORG.
        """

        self.np_random: RandomNumberGenerator = np_random
        self.scenario = scenario
        self.subnet_name_to_cidr = {}  # contains mapping of subnet names to subnet cidrs
        self.ip_addresses = {}  # contains mapping of ip addresses to hostnames
        self.hostname_ip_map = {}  # contains mapping of hostnames to ip addresses
        self.hostname_subnet_map = {}  # contains mapping of hostnames to subnet name

        self.hosts: Dict[str, Host] = {}  # contains mapping of hostnames to host objects
        self.sessions: Dict[str, Dict[int, Session]] = {}  # contains mapping of agent names to mapping of session id to session objects
        self.subnets: Dict[IPv4Network, Subnet] = {}  # contains mapping of subnet cidrs to subnet objects
        self.subnets_cidr_to_name = {}  # contains mapping of subnet cidrs to subnet names

        self.link_diagram = None
        self.connected_components = None

        self.sessions_count = {}  # contains a mapping of agent name to number of sessions
        for subnet_name, subnet in scenario.subnets.items():
            self.subnet_name_to_cidr[subnet_name] = subnet.cidr
            self.subnets_cidr_to_name[subnet.cidr] = subnet_name
            self.subnets[subnet.cidr] = subnet
        
        for hostname, host_info in scenario.hosts.items():
            for interface in host_info.interfaces:
                self.ip_addresses[interface.ip_address] = hostname
                self.hostname_ip_map[hostname] = interface.ip_address
                self.hostname_subnet_map[hostname] = self.subnets_cidr_to_name[interface.subnet]
        
        self.hosts = scenario.hosts
        for hostname in self.hosts:
            for agent in scenario.agents:
                self.hosts[hostname].sessions[agent] = []

        for agent, agent_info in scenario.agents.items():
            self.sessions[agent] = {}
            self.sessions_count[agent] = 0
            # instantiate parentless sessions first
            for starting_session in agent_info.starting_sessions:
                if starting_session.parent is None:
                    starting_session.ident = self.sessions_count[agent]
                    starting_session.agent = agent
                    host = self.hosts[starting_session.hostname]
                    host.add_session(starting_session)
                    self.sessions[agent][len(self.sessions[agent])] = starting_session
                    self.sessions_count[agent] += 1
            for starting_session in agent_info.starting_sessions:
                if starting_session.parent is not None:
                    if starting_session.parent not in [i.name for i in self.sessions[agent].values()]:
                        raise ValueError(
                            f"Parent session: {starting_session.parent} of session: {starting_session} not in agent's session list")
                    id = {i.name: id for id, i in self.sessions[agent].items()}[starting_session.parent]
                    parent = self.sessions[agent][id]
                    host = self.hosts[starting_session.hostname]
                    starting_session.ident = self.sessions_count[agent]
                    starting_session.agent = agent
                    starting_session.parent = parent.ident
                    self.sessions[agent][len(self.sessions[agent])] = starting_session
                    host.add_session(starting_session)
                    parent.children[self.sessions_count[agent]] = self.sessions[agent][self.sessions_count[agent]]
                    self.sessions_count[agent] += 1

        for host in self.hosts.values():
            host.create_backup()

        self._setup_data_links()
        
        self.mission_phase = 0
        self.original_time = datetime(2020, 1, 1, 0, 0)
        self.time = copy.deepcopy(self.original_time)

        # hacky fix to enable operational firewall for Scenario1b and Scenario2
        self.operational_firewall = scenario.operational_firewall
        self.blocks: Dict[str, List[str]] = {}

    def get_true_state(self, info: dict) -> Observation:
        """Create's a dictionary containing the requested information from the state.

        Intended to be used for debugging and evaluation purposes. Agents should not have visibility of the unfiltered state.
        Info dictionary should have hostnames as keys. Each host is passed a dictionary whose keys define the subcomponents to pull out and whose values specify which attributes. For example:
            {'HostnameA': {'Interfaces':'ip_address','Services':'Femitter'},
             'HostnameB': {'Interfaces':'All', 'Files': 'All', 'Sessions':'All'},
             'HostnameC': {'User info': 'All', 'System info': 'All'}
             }

        
        Parameters
        ----------
        info: Dict(str:Dict[str:str])
            Dictionary used to filter out information.
        Returns
        -------
        true_obs: dict
            Dictionary containing the requested information from the state.
        """
        true_obs = Observation()
        if info is None:
            raise ValueError('None is not a valid argument for the get true state function in the State class')
        for hostname, host in self.hosts.items():
            if hostname not in info:
                continue
            if 'Processes' in info[hostname]:
                for process in host.processes:
                    obs = process.get_state()
                    for o in obs:
                        true_obs.add_process(hostid=hostname, **o)
            if 'Interfaces' in info[hostname]:
                if info[hostname]['Interfaces'] == 'All':
                    for interface in host.interfaces:
                        true_obs.add_interface_info(hostid=hostname, **interface.get_state())
                elif info[hostname]['Interfaces'] == 'ip_address':
                    for interface in host.interfaces:
                        if interface.name != 'lo':
                            true_obs.add_interface_info(hostid=hostname, ip_address=interface.ip_address)
                else:
                    raise NotImplementedError(f"{info[hostname]['Interfaces']} cannot be collected from state")
            if 'Sessions' in info[hostname]:
                if info[hostname]['Sessions'] == 'All':
                    for agent_name, sessions in host.sessions.items():
                        for session in sessions:
                            true_obs.add_session_info(
                                hostid=hostname, **self.sessions[agent_name][session].get_state()
                            )
                else:
                    agent_name = info[hostname]['Sessions']
                    if agent_name in host.sessions:
                        for session in host.sessions[agent_name]:
                            true_obs.add_session_info(
                                hostid=hostname, **self.sessions[agent_name][session].get_state()
                            )
            if 'Files' in info[hostname]:
                for file in host.files:
                    true_obs.add_file_info(hostid=hostname, **file.get_state())
            if 'User info' in info[hostname]:
                for user in host.users:
                    obs = user.get_state()
                    for o in obs:
                        true_obs.add_user_info(hostid=hostname, **o)
            if 'System info' in info[hostname]:
                true_obs.add_system_info(hostid=hostname, **host.get_state())

            if 'Services' in info[hostname]:
                if 'All' in info[hostname]['Services']:
                    for service, service_info in host.services.items():
                        true_obs.add_process(hostid=hostname, service_name=service, pid=service_info.process)
                else:
                    for service_name in info[hostname]['Services']:
                        if service_name in host.services:
                            true_obs.add_process(hostid=hostname, service_name=service_name, pid=host.services[service_name].process)
        return true_obs

    def _setup_data_links(self):
        """Sets up the data links object for the initial state."""
        # create the link diagram
        self.link_diagram = nx.Graph()
        # add hosts to link diagram
        for hostname in self.hosts.keys():
            self.link_diagram.add_node(hostname)
        # add datalink connections between hosts
        for hostname, host_info in self.hosts.items():
            for interface in host_info.interfaces:
                if interface.interface_type == 'wired':
                    for data_link in interface.data_links:
                        self.link_diagram.add_edge(hostname, data_link)
        self.update_data_links()

    def set_np_random(self, np_random):
        """Sets up the np_random object at the beginning of the scenario.
        
        Parameters
        ----------
        np_random: numpy.random._generator.Generator
            The random number genetator to resolve CybORG's internal events.
        """
        self.np_random = np_random
        for hostname in self.hosts:
            self.hosts[hostname].np_random = np_random

    @staticmethod
    def dist(pos_a:float, pos_b:float):
        """Computes the Eulcidian distance between two points.

        Intended for use with DroneSwarmScenarioGenerator to compute distance between drones.
        
        Parameters
        ----------
        pos_a: float
            Position of first drone.
        pos_b: float
            Position of second drone.
        Returns
        -------
        distance: int
            The distance between the two points provided.
        """
        return sqrt((pos_a[0]-pos_b[0])**2+(pos_a[1]-pos_b[1])**2)

    def update_data_links(self):
        """Updates the links between drones.

        Intended for use with DroneSwarmScenarioGenerator. Drones which are too far apart will have their data links dropped. Drones that come into range will establish datalinks.
        """
        if any([any([j.interface_type == 'wireless' for j in i.interfaces]) for i in self.hosts.values()]):
            distances = {hostname: {hostname: 0.} for hostname in self.hosts.keys()}
            for hostname, host_info in self.hosts.items():
                for hostname2, host_info2 in self.hosts.items():
                    if hostname2 not in distances[hostname]:
                        distances[hostname][hostname2] = self.dist(host_info.position, host_info2.position)
                        distances[hostname2][hostname] = distances[hostname][hostname2]

            for hostname, host_info in self.hosts.items():
                for interface in host_info.interfaces:
                    if interface.interface_type != 'wired':
                        old_data_links = interface.data_links
                        interface.data_links = [
                            other_hostname
                            for other_hostname in self.hosts
                            if distances[hostname][other_hostname] < interface.max_range
                        ]
                        for dl in old_data_links:
                            if dl not in interface.data_links:
                                self.link_diagram.remove_edge(hostname, dl)
                            for interface2 in self.hosts[dl].interfaces:
                                if hostname in interface2.data_links:
                                    interface2.data_links.remove(hostname)
                        for dl in interface.data_links:
                            if dl not in old_data_links:
                                self.link_diagram.add_edge(hostname, dl)
        self.connected_components = list(connected_components(self.link_diagram))

    def add_session(self, session: Session):
        """Adds a session to the specified host.
        
        Sessions with usernames 'root' or 'SYSTEM' are considered privileged.
        If process is none then a PID will be created randomly. 
        If the session is a sandbox, then the PrivilegeEscalate action will not work on this host. Created only when exploiting an deceptive service.
        """
        if session.ident is None:
            if len(self.sessions[session.agent]) > 0:
                session.ident = max(self.sessions[session.agent].keys()) + 1
            else:
                session.ident = 0
        elif self.sessions.get(session.agent, {}).get(session.ident, None) is not None:
            raise ValueError(f'Unable to add session {session.ident} a session with this identity already exists')
        self.sessions_count[session.agent] += 1
        self.sessions[session.agent][session.ident] = session
        host = self.hosts[session.hostname]
        host.add_session(session)
        if session.parent is not None:
            self.sessions[session.agent][session.parent].children[session.ident] = session
        
    def add_file(self, host: str, name: str, path: str, user: str = None, user_permissions: str = None,
                 group: str = None, group_permissions: int = None, default_permissions: int = None):
        """Adds a file to the specified host.

        This is based on Linux file permissions.
        
        Parameters
        ----------
        host: str
            The name of the host to add the file to.
        name: str
            The name of the file to add.
        path: str
            The path of the file on the target host.
        user: str
            The user who owns the file.
        user_permissions: str
            The file permissions of the file owner.
        group: str
            The group the file belongs to.
        group_permissions: int
            The file permissions of the file group.
        default_permissions: int
            The file permissions for default users.
        Returns
        -------
        file: File
            The file to be added to the host.
        """
        host_obj = self.hosts[host]
        new_file = File(
            name=name,
            path=path,
            user=host_obj.get_user(user),
            user_permissions=user_permissions,
            group=group,
            group_permissions=group_permissions,
            default_permissions=default_permissions
        )
        host_obj.files.append(new_file)
        return new_file

    def add_user(self, host: str = None, username: str = None, password: str = None, password_hash_type: str = None):
        """Adds a user to the specified host.

        Parameters
        ----------
        host: str
            The name of the host having the user added.
        username: str
            The name of the user to be added.
        password: str
            The password of the user to be added.
        password_hash_type: str
            The hashing algorithm to be used on the password.
        Returns
        -------
        user: User
            The user to be added to the host.
        """
        host = self.hosts[host]

        return host.add_user(username=username, password=password, password_hash_type=password_hash_type)

    def remove_process(self, hostname: str, pid: int):
        """Removes a process from the specified host.
        
        Parameters
        ----------
        hostname: str
            The name of the host having the process removed.
        pid: int
            The process id of the process to be removed.
        """
        host = self.hosts[hostname]
        process = host.get_process(pid)
        if process is None:
            return
        agent, session = self.get_session_from_pid(hostname=hostname, pid=pid)
        host.processes.remove(process)
        pids = [service.process for service in host.services.values() if service.active]
        if process.pid in pids:
            process.pid = None
            host.add_process(process)
            service = True
        else:
            service = False
        if session is None:
            return
        host.sessions[agent].remove(session)
        session = self.sessions[agent].pop(session)
        if service:
            self.add_session(session)

    def get_session_from_pid(self, hostname: str, pid: int):
        """Searches the target host for a session with the specified PID.

        Returns None, None if not found.
        
        Parameters
        ----------
        hostname: str
            The name of the host to search.
        pid: int
            The process id to search for.

        Returns
        -------
        agent: str
            Name of the agent owning the found session.
        session_index: int
            The Session id of the found session.
        """
        for agent, sessions in self.sessions.items():
            for session_index, session in sessions.items():
                if session.pid == pid and session.hostname == hostname:
                    return agent, session_index
        return None, None

    def reboot_host(self, hostname):
        """Unused. Used by deprecated action."""
        host = self.hosts[hostname]
        for agent, sessions in host.sessions.items():
            for session in sessions:
                self.sessions[agent].pop(session)
                for other_session in self.sessions[agent].values():
                    if other_session.session_type == SessionType.MSF_SERVER and session in other_session.routes:
                        other_session.routes.pop(session)
        host.sessions = {}
        host.processes = []
        for file in host.files:
            if file.path == "/tmp/":
                host.files.remove(file)

        # start back up
        host.processes = host.default_processes.copy()

        for servicename, service in host.services.items():
            if service['active']:
                self.start_service(hostname, servicename)

    def stop_service(self, hostname: str, service_name: str):
        """Stops the target service on the specified host.
        
        Parameters
        ----------
        hostname: str
            The name of the host to stop the service on.
        service_name: str
            The name of the service to stop.
        """
        # stops a service, its process, and associated sessions
        process = self.hosts[hostname].stop_service(service_name)
        self.remove_process(hostname, process)

    def start_service(self, hostname: str, service_name: str):
        """Starts the target service on the specified host.
        
        Parameters
        ----------
        hostname: str
            The name of the host to start the service on.
        service_name: str
            The name of the service to start.
        """
        # stops a service, its process, and associated sessions
        process, session = self.hosts[hostname].start_service(service_name)
        if session is not None:
            self.add_session(session)

    def get_subnet_containing_ip_address(self, ip_address: IPv4Address) -> Subnet:
        """Returns the subnet containing the specified ip address.
        
        Parameters
        ----------
        ip_address: IPv4Address
            The ip address to find the subnet for.

        Returns
        -------
        subnet: Subnet
            The subnet containing the specified ip address.
        """
        for subnet in self.subnets.values():
            if subnet.contains_ip_address(ip_address):
                return subnet
        raise ValueError(f"No Subnet contains the ip address {ip_address}")

    def check_next_phase_on_update_step(self, step: int):     
        """Updates the State step count and mission phase number.

        Parameters
        ----------
        step: int
            The current step count

        Returns
        -------
        change: bool
            True if mission phased changed otherwise False
        """

        new_mission_phase = None
        min_step = 0
        max_step = 0

        for phase_num, phase_step_size in enumerate(self.scenario.mission_phases):
            min_step = max_step
            max_step = min_step + phase_step_size
            if step >= min_step and step < max_step:
                new_mission_phase = phase_num
                break
        
        if new_mission_phase is None:
            raise ValueError(f"Step number ({step}) exceeds last mission phase step maximum ({max_step}). Use step parameter in EnterpriseScenarioGenerator.")
        if new_mission_phase > self.mission_phase:
            self.mission_phase = new_mission_phase
            return True
        return False

    def __str__(self):
        #output = f"scenario = {self.scenario}"
        #output += f"subnet_name_to_cidr = {self.subnet_name_to_cidr}\n"

        output = f"State:\n"
        output += f"Network:\n"
        for ip_address in self.subnet_name_to_cidr:
            output += f"ip_addresses = {ip_address}\n"
        output += f"Hosts:\n"
        for host in self.hosts:
            output += f"host = {host}\n"
        output += f"Sessions:\n"
        for session in self.sessions:
            output += f"session = {session}\n"
        output += f"Subnets:\n"
        for subnet in self.subnets:
            output += f"subnet = {subnet}\n"

        return output

