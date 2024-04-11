from enum import Enum
from ipaddress import IPv4Network
from typing import Dict, List, Type, Tuple
import inspect

from gym.utils.seeding import RandomNumberGenerator
import numpy as np

from CybORG.Agents import SleepAgent
from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
from CybORG.Agents.SimpleAgents.EnterpriseGreenAgent import EnterpriseGreenAgent
from CybORG.Agents.SimpleAgents.FiniteStateRedAgent import FiniteStateRedAgent

from CybORG.Shared import Scenario
from CybORG.Shared.RewardCalculator import EmptyRewardCalculator
from CybORG.Shared.BlueRewardMachine import BlueRewardMachine
from CybORG.Shared.Enums import Architecture, ProcessName, ProcessType, ProcessVersion
from CybORG.Shared.Scenario import ScenarioAgent
from CybORG.Shared.Scenarios.ScenarioGenerator import ScenarioGenerator
from CybORG.Simulator.Actions.AbstractActions import Monitor, DiscoverRemoteSystems, DiscoverNetworkServices, \
    ExploitRemoteService, PrivilegeEscalate, Impact, DegradeServices, AggressiveServiceDiscovery, \
    StealthServiceDiscovery, DiscoverDeception
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions import DecoyHarakaSMPT, DecoyApache, DecoyTomcat, DecoyVsftpd, DeployDecoy
from CybORG.Simulator.Actions.AbstractActions import Analyse, Remove, Restore
from CybORG.Simulator.Actions.Action import Sleep
from CybORG.Simulator.Actions.ConcreteActions import RedSessionCheck, Withdraw
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import AllowTrafficZone, BlockTrafficZone
from CybORG.Simulator.Actions.AbstractActions import Impact, DegradeServices, DiscoverDeception
from CybORG.Simulator.Actions.AbstractActions import DiscoverRemoteSystems, AggressiveServiceDiscovery, StealthServiceDiscovery, PrivilegeEscalate, Monitor
from CybORG.Shared.Session import RedAbstractSession, Session, VelociraptorServer
from CybORG.Simulator.Host import Host
from CybORG.Simulator.Interface import Interface
from CybORG.Simulator.Process import Process
from CybORG.Simulator.Service import Service
from CybORG.Simulator.Subnet import Subnet
from CybORG.Simulator.Actions.GreenActions import GreenAccessService, GreenLocalWork
from CybORG.Simulator.User import User


class SUBNET(str, Enum):
    """A class of class attributes that link subnet enums to the corresponding string subnet name. 
    """
    RESTRICTED_ZONE_A = "restricted_zone_a_subnet"
    OPERATIONAL_ZONE_A = "operational_zone_a_subnet"
    RESTRICTED_ZONE_B = "restricted_zone_b_subnet"
    OPERATIONAL_ZONE_B = "operational_zone_b_subnet"
    CONTRACTOR_NETWORK = "contractor_network_subnet"
    PUBLIC_ACCESS_ZONE = "public_access_zone_subnet"
    ADMIN_NETWORK = "admin_network_subnet"
    OFFICE_NETWORK = "office_network_subnet"
    INTERNET = "internet_subnet"


class EnterpriseScenarioGenerator(ScenarioGenerator):
    """ 
    This class is used to generate scenarios designed for the Cage Challenge 4 (CC4)

    Attributes
    ----------
    background_image : str
        path to a background render image
    used_pids: List[int]
    blue_agent_class : BaseAgent
        class instance that inherits from BaseAgent to be used in scenario for blue agents
    red_agent_class : BaseAgent
        class instance that inherits from BaseAgent to be used in scenario for red agents
    green_agent_class : BaseAgent
        class instance that inherits from BaseAgent to be used in scenario for green agents
    steps : int
        number of steps that make up the episode
    MIN_USER_HOSTS : int
        minimum number of user hosts generated in the dynamic scenario, set at 3
    MAX_USER_HOSTS : int
        maximum number of user hosts generated in the dynamic scenario, set at 10
    MIN_SERVER_HOSTS : int
        minimum number of server hosts generated in the dynamic scenario, set at 1
    MAX_SERVER_HOSTS : int
        maximum number of server hosts generated in the dynamic scenario, set at 6
    MAX_ADDON_SERVICES : int
        maximum number of add-on services generated in the dynamic scenario, set at 10
    MAX_BANDWIDTH : int
        maximum bandwidth of communications, set at 100
    MESSAGE_LENGTH : int
        message length of agent communications, set at 8
    """

    MIN_USER_HOSTS = 3
    MAX_USER_HOSTS = 10
    MIN_SERVER_HOSTS = 1
    MAX_SERVER_HOSTS = 6
    MAX_ADDON_SERVICES = 10
    MAX_BANDWIDTH = 100
    MESSAGE_LENGTH = 8

    def __init__(
            self,
            blue_agent_class: Type[BaseAgent] = None,
            red_agent_class: Type[BaseAgent] = None,
            green_agent_class: Type[BaseAgent] = None,
            steps: int = 100
    ):
        """
        Parameters
        ----------
        blue_agent_class : BaseAgent, optional
            The type of agent for blue agents, by default None
        red_agent_class : BaseAgent, optional
            The type of agent for red agents, by default None
        green_agent_class : BaseAgent, optional
            The type of agent for green agents, by default None
        steps : int, optional
            The number of steps, by default 100
        """

        super().__init__()
        self.background_image = "img/blank.png"
        self.used_pids: List[int] = []
        self.blue_agent_class = blue_agent_class
        self.red_agent_class = red_agent_class
        self.green_agent_class = green_agent_class
        self.steps = steps

    def create_scenario(self, np_random: RandomNumberGenerator) -> Scenario:
        """
        This public function initiates the generation of a new Enterprise Scenario.

        This function calls a multitude of private functions to generate:
        
        - subnets
        - hosts
        - agents (red, green, blue)
        - mission phases
        - reward machines

        Finally, the outputs from all the private functions in this class are used to create an instance of the Scenario object - which is returned.

        Parameters
        ----------
        np_random : RandomNumberGenerator
            The RNG that will be used to make "random" decisions when creating scenarios.

        Returns
        -------
        scenario : Scenario
            The new enterprise scenario object
        """
        self.used_pids.clear()
        self.np_random = np_random
        subnets = self._generate_subnets()
        hosts = self._generate_hosts(subnets)
        agents: Dict[str, ScenarioAgent] = {}
        self._generate_blue_agents(subnets, agents)
        self._generate_green_agents(hosts, subnets, agents)
        self._generate_red_agents(subnets, agents)
        team_agents = self._generate_team_agents(agents)
        scenario = Scenario(
            agents=agents,
            team_calcs=None,
            team_agents=team_agents,
            hosts=hosts,
            subnets=subnets,
            mission_phases=self._generate_mission_phases(self.steps),
            allowed_subnets_per_mphase=self._set_allowed_subnets_per_mission_phase(),
            predeployed=False,
            max_bandwidth=self.MAX_BANDWIDTH
        )
        scenario.team_calc = self._generate_team_calcs()

        return scenario

    def _generate_subnets(self) -> Dict[str, Subnet]:
        """
        This function generates the specific subnets required by CC4 for the scenario.

        Returns
        -------
        scenario_subnets : Dict[str, Subnet]
            A dictionary where the keys are the subnet names, and the values are the subnets
            themselves.
        """
        subnet_prefix = 24
        network = IPv4Network("10.0.0.0/16")
        network_subnets = list(network.subnets(new_prefix=subnet_prefix))

        # declare subnet NACLs
        subnet_nacls = {
            SUBNET.RESTRICTED_ZONE_A: {
                SUBNET.OPERATIONAL_ZONE_A: {"in": "None", "out": "all"},
                SUBNET.CONTRACTOR_NETWORK: {"in": "all", "out": "all"},
                SUBNET.PUBLIC_ACCESS_ZONE: {"in": "all", "out": "all"},
            },
            SUBNET.OPERATIONAL_ZONE_A: {
                SUBNET.RESTRICTED_ZONE_A: {"in": "all", "out": "None"}
            },
            SUBNET.RESTRICTED_ZONE_B: {
                SUBNET.OPERATIONAL_ZONE_B: {"in": "None", "out": "all"},
                SUBNET.CONTRACTOR_NETWORK: {"in": "all", "out": "all"},
                SUBNET.PUBLIC_ACCESS_ZONE: {"in": "all", "out": "all"},
            },
            SUBNET.OPERATIONAL_ZONE_B: {
                SUBNET.RESTRICTED_ZONE_B: {"in": "all", "out": "None"}
            },
            SUBNET.CONTRACTOR_NETWORK: {
                SUBNET.RESTRICTED_ZONE_A: {"in": "all", "out": "all"},
                SUBNET.RESTRICTED_ZONE_B: {"in": "all", "out": "all"},
                SUBNET.PUBLIC_ACCESS_ZONE: {"in": "all", "out": "all"},
            },
            SUBNET.PUBLIC_ACCESS_ZONE: {
                SUBNET.RESTRICTED_ZONE_A: {"in": "all", "out": "all"},
                SUBNET.RESTRICTED_ZONE_B: {"in": "all", "out": "all"},
                SUBNET.CONTRACTOR_NETWORK: {"in": "all", "out": "all"},
                SUBNET.ADMIN_NETWORK: {"in": "all", "out": "all"},
                SUBNET.OFFICE_NETWORK: {"in": "all", "out": "all"},
            },
            SUBNET.ADMIN_NETWORK: {
                SUBNET.PUBLIC_ACCESS_ZONE: {"in": "all", "out": "all"},
                SUBNET.OFFICE_NETWORK: {"in": "all", "out": "all"}
            },
            SUBNET.OFFICE_NETWORK: {
                SUBNET.PUBLIC_ACCESS_ZONE: {"in": "all", "out": "all"},
                SUBNET.ADMIN_NETWORK: {"in": "all", "out": "all"}
            },
            SUBNET.INTERNET: {
                SUBNET.RESTRICTED_ZONE_A: {"in": "all", "out": "all"},
                SUBNET.OPERATIONAL_ZONE_A: {"in": "all", "out": "all"},
                SUBNET.RESTRICTED_ZONE_B: {"in": "all", "out": "all"},
                SUBNET.OPERATIONAL_ZONE_B: {"in": "all", "out": "all"},
                SUBNET.CONTRACTOR_NETWORK: {"in": "all", "out": "all"},
                SUBNET.PUBLIC_ACCESS_ZONE: {"in": "all", "out": "all"},
                SUBNET.ADMIN_NETWORK: {"in": "all", "out": "all"},
                SUBNET.OFFICE_NETWORK: {"in": "all", "out": "all"}
            }
        }
        # Create subnets in a list that can be iterated over
        scenario_subnets = {}
        for subnet_name in SUBNET:
            nacl = subnet_nacls[subnet_name]
            subnet = self._generate_subnet(subnet_name.value, nacl, network_subnets)
            scenario_subnets[subnet_name] = subnet
        return scenario_subnets

    def _generate_subnet(self, subnet_name: str, nacls: Dict[str, Dict[str, str]],
                         ipv4_subnets: List[IPv4Network]) -> Subnet:
        """
        This function generates a new Scenario subnet. It has placeholder values for 'size' and
        'hosts' as we haven't generated the hosts yet.

        Parameters
        ----------
        subnet_name : str
            the label of the subnet
        nacls : Dict[str, Dict[str, str]]
            A dictionary where the keys are the other subnets the subnet being generated interacts
            with, and the values are another dictionary that specifies how information can flow.
        ipv4_subnets : List[IPv4Network]
            A list containing the remaining available IPv4 subnets.

        Returns
        -------
        Subnet
            A new Subnet object
        """
        selected_subnet_index = self.np_random.choice(len(ipv4_subnets))
        cidr = ipv4_subnets.pop(selected_subnet_index)
        size = len(list(cidr.hosts()))
        return Subnet(subnet_name, size, [], nacls, cidr, [])

    def _set_allowed_subnets_per_mission_phase(self) -> Dict[SUBNET, tuple]:
        """This static function returns the allowed_subnets according to readme for CC4.

        # (0) Pre-planning phase
        # (1) Mission A
        # (2) Mission B

        Returns
        -------
        comms_policy : Array[Array[Tuple(Subnet, Subnet)]]
            A list of pairs of subnets that are allowed to communicate with each other during the policy iteration
        """

        policy_1 = [
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.CONTRACTOR_NETWORK), (SUBNET.ADMIN_NETWORK, SUBNET.CONTRACTOR_NETWORK), (SUBNET.OFFICE_NETWORK, SUBNET.CONTRACTOR_NETWORK),
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.RESTRICTED_ZONE_A), (SUBNET.ADMIN_NETWORK, SUBNET.RESTRICTED_ZONE_A), (SUBNET.OFFICE_NETWORK, SUBNET.RESTRICTED_ZONE_A),
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.RESTRICTED_ZONE_B), (SUBNET.ADMIN_NETWORK, SUBNET.RESTRICTED_ZONE_B), (SUBNET.OFFICE_NETWORK, SUBNET.RESTRICTED_ZONE_B),
            (SUBNET.RESTRICTED_ZONE_A, SUBNET.CONTRACTOR_NETWORK),
            (SUBNET.OPERATIONAL_ZONE_A, SUBNET.RESTRICTED_ZONE_A),
            (SUBNET.RESTRICTED_ZONE_B, SUBNET.CONTRACTOR_NETWORK),
            (SUBNET.RESTRICTED_ZONE_B, SUBNET.RESTRICTED_ZONE_A),
            (SUBNET.OPERATIONAL_ZONE_B, SUBNET.RESTRICTED_ZONE_B)
        ]

        policy_2 = [
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.CONTRACTOR_NETWORK), (SUBNET.ADMIN_NETWORK, SUBNET.CONTRACTOR_NETWORK), (SUBNET.OFFICE_NETWORK, SUBNET.CONTRACTOR_NETWORK),
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.RESTRICTED_ZONE_A), (SUBNET.ADMIN_NETWORK, SUBNET.RESTRICTED_ZONE_A), (SUBNET.OFFICE_NETWORK, SUBNET.RESTRICTED_ZONE_A),
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.RESTRICTED_ZONE_B), (SUBNET.ADMIN_NETWORK, SUBNET.RESTRICTED_ZONE_B), (SUBNET.OFFICE_NETWORK, SUBNET.RESTRICTED_ZONE_B),
            (SUBNET.RESTRICTED_ZONE_B, SUBNET.CONTRACTOR_NETWORK),
            (SUBNET.OPERATIONAL_ZONE_B, SUBNET.RESTRICTED_ZONE_B)
        ]

        policy_3 = [
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.CONTRACTOR_NETWORK), (SUBNET.ADMIN_NETWORK, SUBNET.CONTRACTOR_NETWORK), (SUBNET.OFFICE_NETWORK, SUBNET.CONTRACTOR_NETWORK),
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.RESTRICTED_ZONE_A), (SUBNET.ADMIN_NETWORK, SUBNET.RESTRICTED_ZONE_A), (SUBNET.OFFICE_NETWORK, SUBNET.RESTRICTED_ZONE_A),
            (SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.RESTRICTED_ZONE_B), (SUBNET.ADMIN_NETWORK, SUBNET.RESTRICTED_ZONE_B), (SUBNET.OFFICE_NETWORK, SUBNET.RESTRICTED_ZONE_B),
            (SUBNET.RESTRICTED_ZONE_A, SUBNET.CONTRACTOR_NETWORK),
            (SUBNET.OPERATIONAL_ZONE_A, SUBNET.RESTRICTED_ZONE_A)
        ]

        comms_policy = [policy_1, policy_2, policy_3]

        return comms_policy

    def _generate_hosts(self, subnets: Dict[str, Subnet]) -> Dict[str, Host]:
        """
        This function initiates the creation of all the hosts in the scenario. Since the hosts
        are tried to the subnets, the scenario's subnets are required as a parameter.

        Parameters
        ----------
        subnets : Dict[str, Subnet]
            A dictionary where the keys are the names of the subnets, and the values are the
            subnets themselves.

        Returns
        -------
        Dict[str, Host]
            A dictionary where the keys are the hostname, and the values are the hosts themselves.
        """
        host_list = []
        for subnet in subnets.values():
            ip_addresses = list(subnet.cidr.hosts())

            if subnet.name == "internet_subnet":
                hostname = "root_internet_host_0"
                subnet.hosts.append(hostname)
                selected_ip_address_index = self.np_random.choice(len(ip_addresses))
                ip_address = ip_addresses.pop(selected_ip_address_index)
                subnet.ip_addresses.append(ip_address)
                host_list.append(self._generate_linux_host(hostname, ip_address, subnet))
                subnet.size = 1
                continue

            hostname = f'{subnet.name}_router'
            subnet.hosts.append(hostname)
            selected_ip_address_index = self.np_random.choice(len(ip_addresses))
            ip_address = ip_addresses.pop(selected_ip_address_index)
            subnet.ip_addresses.append(ip_address)
            host_list.append(self._generate_linux_host(hostname, ip_address, subnet))

            # generate user hosts
            num_user_hosts = self.np_random.integers(self.MIN_USER_HOSTS, self.MAX_USER_HOSTS, endpoint=True)
            for i in range(num_user_hosts):
                hostname = f"{subnet.name}_user_host_{i}"
                subnet.hosts.append(hostname)
                selected_ip_address_index = self.np_random.choice(len(ip_addresses))
                ip_address = ip_addresses.pop(selected_ip_address_index)
                subnet.ip_addresses.append(ip_address)
                host_list.append(self._generate_linux_host(hostname, ip_address, subnet))

            # generate servers
            num_server_hosts = self.np_random.integers(self.MIN_SERVER_HOSTS, self.MAX_SERVER_HOSTS, endpoint=True)
            for i in range(num_server_hosts):
                hostname = f"{subnet.name}_server_host_{i}"
                ip_address = ip_addresses.pop()
                subnet.ip_addresses.append(ip_address)
                host_list.append(self._generate_linux_host(hostname, ip_address, subnet))
                subnet.hosts.append(hostname)

            subnet.size = num_user_hosts + num_server_hosts + 1

        # Convert list into a dictionary and return it
        return {host.hostname: host for host in host_list}

    def _generate_data_links(self, hostname: str, subnet):
        """_summary_

                Parameters
                ----------
                hostname : str
                    The name of the host whose parent is to be defined.
                subnet : _type_
                    The subnet that host belongs to.

                Returns
                -------
                List[str]
                    The parent data link
                """
        if hostname == "root_internet_host_0":
            data_links = ['restricted_zone_a_subnet_router',
                          'restricted_zone_b_subnet_router',
                          'contractor_network_subnet_router',
                          'public_access_zone_subnet_router']
        elif "_router" in hostname:
            if 'restricted_zone_a' in hostname:
                data_links = ["root_internet_host_0", "operational_zone_a_subnet_router"]
            elif 'restricted_zone_b' in hostname:
                data_links = ["root_internet_host_0", "operational_zone_b_subnet_router"]
            elif 'contractor' in hostname:
                data_links = ["root_internet_host_0"]
            elif 'public_access' in hostname:
                data_links = ["root_internet_host_0",
                              "admin_network_subnet_router",
                              "office_network_subnet_router"]
            elif 'operational_zone_a' in hostname:
                data_links = ["restricted_zone_a_subnet_router"]
            elif 'operational_zone_b' in hostname:
                data_links = ["restricted_zone_b_subnet_router"]
            elif 'admin_network' in hostname:
                data_links = ["public_access_zone_subnet_router"]
            elif 'office_network' in hostname:
                data_links = ["public_access_zone_subnet_router"]
            else:
                raise ValueError(f"Unexpected router {hostname} in subnet {subnet}")
        else:
            data_links = [f"{subnet.name}_router"]
        return data_links

    def _between_subnet_links(self, hostname: str):
        """Additional info about other hosts that red gains when it get root controll of the host.

        Parameters
        ----------
        hostname : str
            the name of the host.

        Returns
        -------
        links : Dict[str, List[str]]
            hosts that have (directional) links to eachother
        """
        links = {
            "contractor_network_subnet_server_host_0": [
                "restricted_zone_a_subnet_server_host_0",
                "restricted_zone_b_subnet_server_host_0",
                "public_access_zone_subnet_server_host_0",
                ],
            "restricted_zone_a_subnet_server_host_0": [
                "operational_zone_a_subnet_server_host_0",
                "contractor_network_subnet_server_host_0"
            ],
            "operational_zone_a_subnet_server_host_0": [
                "restricted_zone_a_subnet_server_host_0"
            ],
            "restricted_zone_b_subnet_server_host_0": [
                "operational_zone_b_subnet_server_host_0",
                "contractor_network_subnet_server_host_0"
            ],
            "operational_zone_b_subnet_server_host_0": [
                "restricted_zone_b_subnet_server_host_0"
            ],
            "public_access_zone_subnet_server_host_0": [
                "admin_network_subnet_server_host_0",
                "office_network_subnet_server_host_0",
                "contractor_network_subnet_server_host_0"
            ],
            "admin_network_subnet_server_host_0": [
                "public_access_zone_subnet_server_host_0"
            ],
            "office_network_subnet_server_host_0": [
                "public_access_zone_subnet_server_host_0"
            ]
        }
        if not hostname in links:
            return None
        info = {}
        for host in links[hostname]:
            info[host] = {'Interfaces': 'ip_address'}
        return info

    def _generate_linux_host(self, hostname: str, ip_address: IPv4Network, subnet: Subnet) -> Host:
        """
        Generates a host for the scenario with linux specifications.

        Parameters
        ----------
        hostname : str
            The label to be given to the new host.
        ip_address : IPv4Network
            The IP address to be assigned to the new host.
        subnet : Subnet
            The subnet the new host will belong to.

        Returns
        -------
        Host
            The new (linux) Host.
        """
        linux_distro_options = [
            { "OSDistribution": "UBUNTU", "OSVersion": "22.04.2 LTS" },
            { "OSDistribution": "KALI", "OSVersion": "K2019_4" }
        ]
        system_info = { 'OSType': "LINUX", "Architecture": Architecture.x64 }

        OSDistribution = self.np_random.choice(linux_distro_options)
        system_info.update(OSDistribution)
        interfaces = [Interface(
            name='eth0',
            ip_address=ip_address,
            subnet=subnet.cidr,
            interface_type='wired',
            data_links=self._generate_data_links(hostname, subnet),
            swarm=False
        )]
        root_user = User(groups=[{'GID': 0, 'Group Name': 'root'}], uid=0, username='root')
        user_group = {'GID': 1, 'Group Name': 'user'}
        user = User(groups=[user_group], uid=1000, username='user', bruteforceable=True)
    
        if hostname == "root_internet_host_0" or 'router' in hostname:
            services = None
            processes = None
            respond_to_ping = False
        else:
            services = self._generate_linux_host_services(hostname)
            processes = self._generate_linux_host_processes(services)
            respond_to_ping = True

        return Host(
            hostname=hostname,
            host_type="",
            processes=processes,
            system_info=system_info,
            interfaces=interfaces,
            info=self._between_subnet_links(hostname),
            users=[root_user, user],
            services=services,
            respond_to_ping=respond_to_ping,
            np_random=self.np_random,
        )

    def _generate_linux_host_services(self, hostname: str) -> Dict[str, Service]:
        """
        This function generates a dict of random services for a linux host.

        Parameters
        ----------
        hostname : str
            The name of the host to have services generated.

        Returns
        -------
        Dict[str, dict]
            A dictionary where the keys are the service names, and the values are the dictionaries
            containing the services themselves.
        """
        # Set up the mandatory services.
        services = { ProcessName.SSHD: Service(process=self._generate_pid()) }
        if "operational" in hostname:
            services[ProcessName.OTSERVICE] = Service(process=self._generate_pid())
        
        # Define what the options are for additional services
        addon_services_options = {
            ProcessName.APACHE2: Service(process=self._generate_pid()),
            ProcessName.MYSQLD: Service(process=self._generate_pid()),
            ProcessName.SMTP: Service(process=self._generate_pid()),
        }
        # Choose a random number of the optional services
        max_addon_services = min(len(addon_services_options), self.MAX_ADDON_SERVICES)
        num_addon_services = self.np_random.integers(0, max_addon_services, endpoint=True)
        for _ in range(num_addon_services):
            choice = self.np_random.choice(list(addon_services_options.keys()))
            services[choice] = addon_services_options.pop(choice)
        return services

    def _generate_pid(self) -> int:
        """
        Generates a dummy process ID number that is not already contained within the list of used
        process IDs.

        Returns
        -------
        int
            The new process ID.
        """
        while True:
            pid = self.np_random.integers(1000, 10000)  # generate a random 4-digit number
            if pid not in self.used_pids:  # check if the generated PID is not in the used_pids list
                self.used_pids.append(pid)
                return pid  # if not, return the generated PID

    def _generate_linux_host_processes(self, services: Dict[str, Service]) -> List[dict]:
        """
        Creates a set of randomised processes for a linux host based on its services.

        Parameters
        ----------
        services : dict
            A dict containing the services that were made for the host.

        Returns
        -------
        List[dict]
            A list containing dicts that represent the processes for the linux host.
        """
        processes = []
        prob_vuln_proc_occurs = 1.0

        local_processes = {
            ProcessName.SSHD: {'port': 22, 'type': ProcessType.SSH},
            ProcessName.APACHE2: {'port': 80, 'type': ProcessType.WEBSERVER},
            ProcessName.MYSQLD: {'port': 3390, 'type': ProcessType.MYSQL},
            ProcessName.SMTP: {'port': 25, 'type': ProcessType.SMTP},
            ProcessName.OTSERVICE: {'port': 1, 'type': ProcessType.UNKNOWN},
            "FTP": {'port': 21, 'type': ProcessType.FEMITTER}
        }

        for key, service in services.items():
            process = Process(
                process_name=key,
                pid=service.process,
                path='/ usr / sbin',
                username="user",
                open_ports=[{
                    "local_address": "0.0.0.0",
                    "local_port": local_processes[key]['port'],
                }],
                process_type=local_processes[key]['type']
            )

            if local_processes[key]['type'] == ProcessType.SMTP:
                process.version = ProcessVersion.HARAKA_2_8_9

            if prob_vuln_proc_occurs < self.np_random.random():
                if local_processes[key]['type'] == ProcessType.WEBSERVER:
                    process.properties = ['rfi']
                if local_processes[key]['type'] == ProcessType.SMTP:
                    process.version = ProcessVersion.HARAKA_2_7_0

            processes.append(process)
        return processes

    def _generate_blue_agents(self, subnets: Dict[str, Subnet], agents: Dict[str, ScenarioAgent]):
        """
        Populates the agents dict with blue agents. These blue agents are distributed between the
        five security zones.
        Parameters
        ----------
        subnets : Dict[str, Subnet]
            A dict containing the subnets of the scenario.
        agents : Dict[str, ScenarioAgent]
            a dict containing the agents of the scenario.
        """
        blue_actions = [AllowTrafficZone, BlockTrafficZone, Monitor, Analyse, Restore, Remove, DeployDecoy, Sleep]
        blue_agent_allowed_subnets = [
            [SUBNET.RESTRICTED_ZONE_A.value],
            [SUBNET.OPERATIONAL_ZONE_A.value],
            [SUBNET.RESTRICTED_ZONE_B.value],
            [SUBNET.OPERATIONAL_ZONE_B.value],
            [SUBNET.PUBLIC_ACCESS_ZONE.value, SUBNET.ADMIN_NETWORK.value, SUBNET.OFFICE_NETWORK.value]
        ]
        for allowed_subnets in blue_agent_allowed_subnets:
            i = blue_agent_allowed_subnets.index(allowed_subnets)
            agent_name = f"blue_agent_{i}"
            # Determine which subnet the agent is starting on
            starting_subnet = subnets[self.np_random.choice(allowed_subnets)]
            # Set-up session objects for all the hosts in the possible subnets
            sessions: List[Session] = []
            allowed_hosts = []
            for subnet_name in allowed_subnets:
                subnet = subnets[subnet_name]
                allowed_hosts += subnet.hosts
            # Set-up OSINT based on the subnet the starting host is in.
            osint = {"Hosts": {}}
            for host in allowed_hosts:
                osint["Hosts"][host] = {
                    'Interfaces': 'All', 'System info': 'All', 'User info': 'All'
                }
            # Make one of the sessions the parent session
            parent_host = self.np_random.choice(allowed_hosts)
            for host in allowed_hosts:
                j = allowed_hosts.index(host)
                session_class = Session
                session_type = 'blue_session'
                if host == parent_host:
                    session_class = VelociraptorServer
                    session_type = "VelociraptorServer"
                session = session_class(
                    name=f"blue_session_{i}_{j}",
                    username="ubuntu",
                    session_type=session_type,
                    hostname=host,
                    pid=None,
                    ident=None,
                    agent=None
                )
                sessions.append(session)
            parent_session = next(s for s in sessions if s.hostname == parent_host)
            parent_session.num_children = len(sessions) - 1
            for session in sessions:
                if session.name == parent_session.name: continue
                session.parent = parent_session.name
            # Determine agent type
            agent_type = None
            if self.blue_agent_class:
                agent_type = self.blue_agent_class(agent_name)
            default_actions = (Monitor, {'session': 0, 'agent': agent_name})
            agents[agent_name] = ScenarioAgent(
                agent_name, "Blue", sessions, blue_actions, osint, allowed_subnets, agent_type, True, default_actions
            )

    def _generate_green_agents(self, hosts: Dict[str, Host], subnets: Dict[str, Subnet], agents: Dict[str, ScenarioAgent]):
        """
        Populates the agents dict with green agents. There is a green agents for every host in the
        scenario.

        Parameters
        ----------
        hosts : Dict[str, Host]
            A dict containing all of the hosts of the scenario.
        subnets : Dict[str, Subnet]
            A dict containing all the subnets of the scenario.
        agents : Dict[str, ScenarioAgent]
            A dict containing all of the agents of the scenario (so far.)
        """
        green_actions = [GreenAccessService, GreenLocalWork, Sleep]
        green_agent_count = 0
        for subnet in subnets.values():
            for hostname in subnet.hosts:
                if "user" not in hostname: continue
                # Set-up OSINT based on the subnet the starting host is in.
                osint = {"Hosts": {}}
                for host in subnet.hosts:
                    osint["Hosts"][host] = {
                        'Interfaces': 'All', 'System info': 'All', 'User info': 'All'
                    }
                agent_name = f"green_agent_{green_agent_count}"
                green_agent_count += 1
                session = Session(
                    name=f"green_session_{green_agent_count}",
                    username="ubuntu",
                    session_type="green_session",
                    hostname=hostname,
                    pid=None,
                    ident=None,
                    agent=None
                )
                agent_type = None
                default_actions = (Sleep, {})
                if self.green_agent_class:
                    if self.green_agent_class == EnterpriseGreenAgent:
                        host_ip = hosts[hostname].interfaces[0].ip_address
                        agent_type = self.green_agent_class(name=agent_name, np_random=self.np_random, own_ip=host_ip)
                    elif self.green_agent_class == SleepAgent:
                        green_actions = [Sleep]
                    else:
                        agent_type = self.green_agent_class(agent_name)
                agents[agent_name] = ScenarioAgent(
                    agent_name, "Green", [session], green_actions, osint, [subnet.name], agent_type, True,
                    default_actions
                )

    def _generate_red_agents(self, subnets: Dict[str, Subnet], agents):
        """
        Populates the agents dict with red agents. These red agents are distributed between the
        five security zones. Only one of them starts as active.

        Parameters
        ----------
        subnets : Dict[str, Subnet]
            A dict containing the subnets of the scenario.
        agents : _type_
            A dict containing all of the agents of the scenario (so far.)
        """

        red_actions = [
            DiscoverRemoteSystems, AggressiveServiceDiscovery, StealthServiceDiscovery,
            ExploitRemoteService, PrivilegeEscalate, DegradeServices, DiscoverDeception,
            Impact, Withdraw, Sleep
        ]
        red_agent_allowed_subnets = [
            [SUBNET.CONTRACTOR_NETWORK.value],
            [SUBNET.RESTRICTED_ZONE_A.value],
            [SUBNET.OPERATIONAL_ZONE_A.value],
            [SUBNET.RESTRICTED_ZONE_B.value],
            [SUBNET.OPERATIONAL_ZONE_B.value],
            [SUBNET.PUBLIC_ACCESS_ZONE.value, SUBNET.ADMIN_NETWORK.value, SUBNET.OFFICE_NETWORK.value]
        ]
        red_agent_types: List[Type[BaseAgent]] = [SleepAgent, ]
        for allowed_subnets in red_agent_allowed_subnets:
            i = red_agent_allowed_subnets.index(allowed_subnets)
            agent_name = f"red_agent_{i}"
            starting_subnet = subnets[self.np_random.choice(allowed_subnets)]
            allowed_starting_hosts = [h for h in starting_subnet.hosts if 'router' not in h]
            starting_host = self.np_random.choice(allowed_starting_hosts)
            osint = { "Hosts": {}}
            osint["Hosts"][starting_host] = {'Interfaces': 'All', 'System info': 'All', 'User info': 'All'}

            sess_list = []
            active = False

            # Agent is active if it's the one that is in the contractor network.
            if starting_subnet.name == SUBNET.CONTRACTOR_NETWORK.value:
                sess_list.append(RedAbstractSession(
                    name=f"red_session_{i}",
                    username="ubuntu",
                    session_type="RedAbstractSession",
                    hostname=starting_host,
                    pid=None,
                    ident=None,
                    agent=None
                ))
                active = True

            # Determine agent type
            agent_type = self.np_random.choice(red_agent_types)(agent_name)
            default_actions = (RedSessionCheck, {'session': 0, 'agent': agent_name})
            if self.red_agent_class:
                parameter_list = inspect.getfullargspec(self.red_agent_class).args
                if 'np_random' in parameter_list:
                    if isinstance(self.red_agent_class, FiniteStateRedAgent) or issubclass(self.red_agent_class, FiniteStateRedAgent):
                        agent_subnets = [subnets[sn].cidr for sn in allowed_subnets]
                        agent_type = self.red_agent_class(agent_name, np_random=self.np_random, agent_subnets=agent_subnets)
                    else:
                        agent_type = self.red_agent_class(agent_name, np_random=self.np_random)
                else:
                    agent_type = self.red_agent_class(agent_name)
            agents[agent_name] = ScenarioAgent(agent_name, "Red", sess_list, red_actions, osint, allowed_subnets,
                                               agent_type, active, default_actions)

    def _generate_team_calcs(self) -> dict:
        """
        Returns
        -------
        team_calcs : Dict[str, Dict[str, BlueRewardMachine]]
            A dictionary of reward calculator instances for each agent type
        """
        team_calcs = {
            "Blue": { 'BlueRewardMachine': BlueRewardMachine("Blue") },
            "Red": { 'None': EmptyRewardCalculator("Red") },
            "Green": { 'None': EmptyRewardCalculator("Green") }
        }
        return team_calcs

    def _generate_team_agents(self, agents: Dict[str, ScenarioAgent]) -> Dict[str, List[str]]:
        """
        Creates a dict where the keys are the different teams, and the values are lists of the
        names of agents that belong to those teams.

        Parameters
        ----------
        agents : Dict[str, ScenarioAgent]
            A dict that contains all the agents of the scenario.

        Returns
        -------
        Dict[str, List[str]]
            _description_
        """
        team_agents = {}
        for team in ["Blue", "Red", "Green"]:
            team_agents[team] = [agent for agent in agents.keys() if team.lower() in agent]
        return team_agents


    def _generate_mission_phases(self, steps) -> Tuple[int, int, int]:
        quotient, remainder = divmod(steps, 3)
        if remainder == 2:
           return (quotient+1, quotient+1, quotient)
        if remainder == 1:
            return (quotient+1, quotient, quotient)
        return (quotient, quotient, quotient)

    def determine_done(self, env_controller) -> bool:
        """ Determines when the episode ends 
        
        Returns
        -------
        Boolean
            T/F value for if episode is to end
        """
        return env_controller.step_count >= (self.steps-1)
