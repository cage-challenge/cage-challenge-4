from CybORG.Shared import Observation
from CybORG.Simulator.Actions.Action import RemoteAction
from CybORG.Simulator.State import State
from ipaddress import IPv4Address

class DiscoverDeception(RemoteAction):
    """ A Red action that probes a remote host to see if it is running any decoy services. 

    Attributes
    ----------
    session : int
        The source session id.
    agent : str
        The name of the red agent executing the action.
    ip_address : IPv4Address
        The ip_address of the target host.
    target_hostname : str
        The name of the target host. 
    duration : int
        This action takes 2 steps to complete, instead of the default 1.
    detection_rate : float
        The True Positive rate of the red agent to accurately detect whether the host is running a decoy service. A True Positive Rate only includes True Positives and False Negatives.
    fp_rate : float
        The False Positive rate of the red agent to incorrectly detect a normal service as a decoy. Defaults to 10%.
    """
    def __init__(self, session: int, agent: str, ip_address: IPv4Address):
        """
        Parameters
        ----------
        session : int
            The source session id.
        agent : str
            The name of the red agent executing the action.
        ip_address : IPv4Address
            The ip_address of the target host.
        """
        super().__init__(session, agent)
        self.ip_address = ip_address
        self.duration = 2
        self.detection_rate = 0.5
        self.fp_rate = 0.1
        self.target_hostname = None
    
    def execute(self, state: State) -> Observation:
        """
        Probes the target host for decoy services.

        Action process:  
        1) Check if there are sessions for the agent on this host\n
        - if not, return unsuccessful obs\n
        2) Get the route between the source and target/remote host\n
        - if there is not a valid route (None), return unsuccessful obs\n
        3) Given that there is a valid route, connect to the remote host\n
        - iterate over all processes on the remote host\n
        - after a detection_rate attribute check (defaults to 50%), add the process to the obs if it passes\n
        - return a successful obs regardless of whether a decoy was found\n

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.
        
        Returns
        -------
        obs: Observation
            An observation containing an indication of the action's successful execution as True/False, and any detected decoy processes.
        """
        obs = Observation(False)
        # (1) check the session exists for this agent
        if self.session not in state.sessions[self.agent]:
            self.log(f"Session '{self.session}' not found for agent '{self.agent}'.")
            return obs
        
        # (2) get the route between the source and target/remote host
        source_hostname = state.sessions[self.agent][self.session].hostname
        self.target_hostname = state.ip_addresses[self.ip_address]
        # can we connect to from the source to target host
        route = self.get_route(state, target=self.target_hostname, source=source_hostname)
        if route is None:
            self.log("No route found.")
            return obs
        # (3) observation is set to true, even if no decoy is detected
        obs.set_success(True)
        # (a) obtain the list of processes running on the target host
        processes = state.hosts[self.target_hostname].processes
        for process in processes:
            # (b) we only detect decoys if detection_rate is lower than random float
            # can result in false negatives or positive as every process has the 'decoy' property added
            if state.np_random.random() <= self.detection_rate and process.decoy_type.name == 'EXPLOIT':
                obs.add_process(hostid=self.target_hostname, pid=process.pid,
                    parent_pid=process.ppid, name=process.name,
                    username=process.user, service_name=process.name,
                    properties=process.properties + ['decoy',])
                obs.add_interface_info(hostid=self.target_hostname, ip_address=self.ip_address)
            elif state.np_random.random() <= self.fp_rate and process.decoy_type.name != 'EXPLOIT':
                obs.add_process(hostid=self.target_hostname, pid=process.pid,
                    parent_pid=process.ppid, name=process.name,
                    username=process.user, service_name=process.name,
                    properties=process.properties + ['decoy',])
                obs.add_interface_info(hostid=self.target_hostname, ip_address=self.ip_address)
        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.target_hostname}"
