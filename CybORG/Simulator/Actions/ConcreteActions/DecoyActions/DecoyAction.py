from typing import Set
from CybORG.Shared.Enums import DecoyType
from CybORG.Shared.Observation import Observation
from CybORG.Shared.Session import Session
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.AbstractActions.Misinform import Decoy, DecoyFactory
from CybORG.Simulator.Host import Host
from CybORG.Simulator.Process import Process
from CybORG.Simulator.Service import Service
from CybORG.Simulator.State import State


class DecoyAction(Action):
    """ Creates a Decoy Service on the specified host.

    An exploit targetting an decoy service will automatically fail.

    Parameters
    ----------
    session: int
        The id of the session executing the action.
    agent: str
        The agent executing the action.
    hostname: str
        The hostname of the host targeted by the action.
    """
    DECOY_TYPE: DecoyType = None
    CANDIDATE_DECOYS: Set[DecoyFactory] = set()

    def __init__(self, *, session: int, agent: str, hostname: str):
        """ Instantiates DecoyAction class.

        Parameters
        ----------
        session: int
            The id of the session executing the action.
        agent: str
            The agent executing the action.
        hostname: str
            The hostname of the host targeted by the action.
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
    
    def execute(self, state: State) -> Observation:
        """ Executes the action to create a decoy.
        Parameters
        ----------
        state: State
            The current state of CybORG.
        
        Returns
        -------
        obs: Observation
            The observation to be returned to the agent.
        """
        obs_fail = Observation(False)
        obs_succeed = Observation(True)
        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        if len(sessions) == 0:
            return obs_fail
        session = state.np_random.choice(sessions)
        host = state.hosts[self.hostname]
        try:
            decoy_factory = self.__select_one_factory(host, state)
            decoy = decoy_factory.make_decoy(host)
            self.__create_process(obs_succeed, session, host, decoy)
            return obs_succeed
        except RuntimeError:
            return obs_fail
        
    def __select_one_factory(self, host: Host, state: State) -> DecoyFactory:
        """
        Examines all decoy factories and returns one randomly compatible one.
        Raises RuntimeError if no compatible ones are found.
        """
        compatible_factories = [
            factory for factory in self.CANDIDATE_DECOYS if factory.is_host_compatible(host)
        ]
        if not compatible_factories:
            raise RuntimeError("No compatible factory")
        return state.np_random.choice(list(compatible_factories))
    
    def __create_process(self, obs: Observation, sess: Session, host: Host, decoy: Decoy) -> None:
        """
        Creates a process & service from Decoy on current host, adds it
        to the observation.
        """
        parent_pid = 1
        pid = host.create_pid()
        host.processes.append(Process(
            pid=pid,
            process_name=decoy.name,
            parent_pid=parent_pid,
            username=sess.username,
            process_version=decoy.version,
            process_type=decoy.process_type,
            open_ports=decoy.open_ports,
            decoy_type=self.DECOY_TYPE,
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
