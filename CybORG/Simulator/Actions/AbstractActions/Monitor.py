from copy import deepcopy

from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Shared.Session import VelociraptorServer
from CybORG.Simulator.State import State


class Monitor(Action):
    """ Collects events on hosts and informs Blue Agent.

    This action runs automatically at the end of each step. If a Blue agent calls it will have no effect. Host events are cleared from the host after this action runs.

    Attributes
    ----------
    session: int
        the session id of the session
    agent: str
        the name of the agent executing the action
    """
    def __init__(self, session: int, agent: str):
        """ Instantiates Monitor class.

        Parameters
        ----------
        session: int
            the session id of the session
        agent: str
            the name of the agent executing the action
        """
        super().__init__()
        self.agent = agent
        self.session = session

    def execute(self, state: State) -> Observation:
        """ Executes the Monitor Action
        Parameters
        ----------
        state: State
            The current state of CybORG.
        
        Returns
        -------
        obs: Observation
            The observation to be returned to the Blue Agent.
            Consists of events collected from all hosts the agent has access to.
            Events are limited to Network Connection events and Process Creation events.
        """
        obs = Observation(True)
        session: VelociraptorServer = state.sessions[self.agent][self.session]
        blue_sessions = [child for child in session.children.values()] + [session]

        for child in blue_sessions:
            host = state.hosts[child.hostname]
            network_connections = host.events.network_connections
            if len(network_connections) > 0:
                obs.add_system_info(hostid=child.hostname, **host.get_state())
            for event in network_connections:
                if event.pid:
                    session.add_sus_pids(hostname=child.hostname, pid=event.pid)
                obs.add_process(hostid=child.hostname, **vars(event))
            host.events.old_network_connections = deepcopy(network_connections)
            network_connections.clear()

            processes = host.events.process_creation
            if len(processes) > 0:
                obs.add_system_info(hostid=child.hostname, **state.hosts[child.hostname].get_state())
            for event in processes:
                if 'pid' in event:
                    session.add_sus_pids(hostname=child.hostname, pid=event['pid'])
                obs.add_process(hostid=child.hostname, **event)
            host.events.old_process_creation = deepcopy(processes)
            processes.clear()
        return obs

    def __str__(self):
        return f"{self.__class__.__name__}"
