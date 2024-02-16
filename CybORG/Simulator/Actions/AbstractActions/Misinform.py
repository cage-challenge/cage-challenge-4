## The following code contains work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.
## Additionally, we waive copyright and related rights in the utilized code worldwide through the CC0 1.0 Universal public domain dedication.

"""
Implements misinformation actions for blue agents
"""
# pylint: disable=invalid-name

from typing import List, Optional
from dataclasses import dataclass

from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Shared.Enums import DecoyType
from CybORG.Simulator.Host import Host
from CybORG.Shared.Session import Session
from CybORG.Simulator.Process import Process
from CybORG.Simulator.Service import Service
from CybORG.Simulator.State import State


@dataclass
class Decoy:
    """
    Contains information necessary to create a misinform process on a host
    """
    service_name: str
    name: str
    open_ports: List[dict]
    process_type: str
    process_path: Optional[str] = None
    version: Optional[str] = None
    properties: Optional[List[str]] = None

class DecoyFactory:
    """
    Assembles process informationt to appear as a vulnerable process
    """
    PORT: int = None
    SERVICE_NAME: str = None
    NAME: str = None
    PROCESS_TYPE: str = None
    PROCESS_PATH: str = None
    PROPERTIES: List[str] = None
    VERSION: str = None

    def make_decoy(self, host: Host) -> Decoy:
        """
        Creates a Decoy instance that contains the necessary information
        to put a decoy on a given host.

        Parameters
        ---------
        host : Host 
            a host that this decoy will be placed on
        """
        del host
        return Decoy(
            service_name=self.SERVICE_NAME,
            name=self.NAME,
            open_ports=[{'local_port': self.PORT, 'local_address': '0.0.0.0'}],
            process_type=self.PROCESS_TYPE,
            process_path=self.PROCESS_PATH,
            properties=self.PROPERTIES,
            version=self.VERSION
        )

    def is_host_compatible(self, host: Host) -> bool:
        """
        Determines whether an instance of this decoy can be placed
        successfully on the given host

        Parameters
        ---------
        host : Host 
            Host to examine for compatibility with this decoy.
        """
        return not host.is_using_port(self.PORT)

class SSHDDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as an ssh server
    """
    PORT = 22
    SERVICE_NAME = "sshd"
    NAME = "Sshd.exe"
    PROCESS_TYPE = "sshd"
    PROCESS_PATH = "C:\\Program Files\\OpenSSH\\usr\\sbin"

sshd_decoy_factory = SSHDDecoyFactory()


class ApacheDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as an apache server
    """
    PORT = 80
    SERVICE_NAME = "apache2"
    NAME = "apache2"
    PROCESS_TYPE = "webserver"
    PROPERTIES = ["rfi"]
    PROCESS_PATH = "/usr/sbin"

apache_decoy_factory = ApacheDecoyFactory()


class SMSSDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as smss
    """
    PORT = 139
    SERVICE_NAME = "smss"
    NAME = "Smss.exe"
    PROCESS_TYPE = "smss"

smss_decoy_factory = SMSSDecoyFactory()


class TomcatDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as a tomcat server
    """
    PORT = 443
    SERVICE_NAME = "tomcat"
    NAME = "Tomcat.exe"
    PROCESS_TYPE = "webserver"
    PROPERTIES = ["rfi"]

tomcat_decoy_factory = TomcatDecoyFactory()


class SvchostDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as svchost
    """
    PORT = 3389
    SERVICE_NAME = "svchost"
    NAME = "Svchost.exe"
    PROCESS_TYPE = "svchost"

svchost_decoy_factory = SvchostDecoyFactory()


class Misinform(Action):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.
    
    Attributes
    ----------
    session: int
        the session id of the session
    agent: str
        the name of the agent executing the action
    hostname: str
        PLACEHOLDER
    """
    def __init__(self, *, session: int, agent: str, hostname: str):
        """ PLACEHOLDER

        Parameters
        ----------
        session: int
            PLACEHOLDER
        agent: str
            PLACEHOLDER
        hostname: int
            PLACEHOLDER
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.decoy_type = DecoyType.EXPLOIT
        self.candidate_decoys = (
                sshd_decoy_factory,
                apache_decoy_factory,
                smss_decoy_factory,
                tomcat_decoy_factory,
                svchost_decoy_factory)

    def execute(self, state: State) -> Observation:
        """ PLACEHOLDER DESC
        Parameters
        ----------
        state: State
            PLACEHOLDER
        
        Returns
        -------
        obs: Observation
            PLACEHOLDER
        """
        obs_fail = Observation(False)
        obs_succeed = Observation(True)

        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        if len(sessions) == 0:
            self.log(f"No sessions could be found on chosen host '{self.hostname}'.")
            return obs_fail

        session = state.np_random.choice(sessions)
        host = state.hosts[self.hostname]

        try:
            decoy_factory = self.__select_one_factory(host, state)
            decoy = decoy_factory.make_decoy(host)
            self.__create_process(obs_succeed, session, host, decoy)
            #print ("Misinform Success. Result: {}".format(result))
            return obs_succeed

        except RuntimeError as err:
            self.log(str(err))
            return obs_fail

    def __select_one_factory(self, host: Host, state: State) -> DecoyFactory:
        """
        Examines all decoy factories and returns one randomly compatible one.
        Raises RuntimeError if no compatible ones are found.
        """

        compatible_factories = [factory for factory in self.candidate_decoys
                if factory.is_host_compatible(host)]

        if len(compatible_factories) == 0:
            raise RuntimeError("No compatible factory")

        return state.np_random.choice(list(compatible_factories))

    def __create_process(self, obs: Observation, sess: Session, host: Host,
            decoy: Decoy) -> None:
        """
        Creates a process & service from Decoy on current host, adds it
        to the observation.
        """
        parent_pid = 1
        pid = host.create_pid()
        host.processes.append(Process(
            pid=pid,
            parent_pid=parent_pid,
            process_name=decoy.name,
            username=sess.username,
            process_version=decoy.version,
            open_ports=decoy.open_ports,
            process_type=decoy.process_type,
            properties=decoy.properties
        ))
        host.services[decoy.service_name] = Service(process=pid, session=sess)
        obs.add_process(
            hostid=self.hostname,
            pid=pid,
            parent_pid=parent_pid,
            name=decoy.name,
            username=sess.username,
            service_name=decoy.service_name,
            properties=decoy.properties
        )

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
