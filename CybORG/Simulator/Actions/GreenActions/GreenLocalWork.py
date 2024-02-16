from CybORG.Simulator.Actions.ConcreteActions.LocalAction import LocalAction
from CybORG.Simulator.Actions.ConcreteActions.PhishingEmail import PhishingEmail
from CybORG.Simulator.State import State, Session, Host
from CybORG.Shared import Observation
from ipaddress import IPv4Address

class GreenLocalWork(LocalAction):
    """An action for Green agents to do 'local work' on the host.
    
    Consists of 3 parts: 

    1. Create a new process to represent user activity.

    2. A low probability the work creates a false positive for Blue - fp_detection_rate

    3. A low probability the work is from a phishing email, creating a red session - phishing_error_rate

    Attributes
    ----------
    ip_address : IPv4Address
        the ip address of the host which the local work is happening on
    fp_detection_rate : float 
        the decimal probability that a false positive is created for blue (0.0 <= value <= 1.0)
    phishing_error_rate : float
        the decimal probability that a PhishingEmail action is performed as a subaction (0.0 <= value <= 1.0)
    """
    def __init__(self, agent: str, session_id: int, ip_address: IPv4Address, fp_detection_rate = 0.01, phishing_error_rate = 0.01):
        """Initialisation of GreenLocalWork by setting class attributes.

        Parameters
        ----------
        agent : str 
            name of agent performing action
        session_id : int
            State session id on the host
        ip_address : IPv4Address
            ip address of the host
        fp_detection_rate : float, optional
            decimal probability that a false positive is created for blue (0.0 <= value <= 1.0, default = 0.01)
        phishing_error_rate : float, optional
            decimal probability that a PhishingEmail action is performed as a subaction (0.0 <= value <= 1.0, default = 0.01)

        Raises
        ------
        ValueError
            decimal probability value is not between 0.0 and 1.0 (inclusive)
        """
        
        super().__init__(agent=agent, session=session_id)
        self.ip_address = ip_address

        # Input validation check
        if not (0.0 <= fp_detection_rate <= 1.0):
            raise ValueError("GreenLocalWork: fp_detection_rate must be a value equal or between 0 and 1")
        self.fp_detection_rate = fp_detection_rate
        if not (0.0 <= phishing_error_rate <= 1.0):
            raise ValueError("GreenLocalWork: phishing_error_rate must be a value equal or between 0 and 1")
        self.phishing_error_rate = phishing_error_rate

    def execute(self, state: State) -> Observation:
        """ Executes the functionality of the action on the state and produces a resulting observation.

        The action execution consists of 3 parts:

        1. User trys to access local service
            - User attempts to access a service local to the host, that may have had its reliability degraded by red.
            - If no services exist on host, action also fails

        2. False alert
            - There is a small chance (1% by default) that the process will create a false positive alert for a Velociraptor Client from Blues agents action.
        
        3. User error
            - low probability the local work is malicious by accident, causing a sub action PhishingEmail.
            - if <1% by default, then this will add a session for the red agent

        Parameters
        ----------
        state : State 
            state of simulation at current step
        
        Returns
        -------
        obs : Observation
            the observation produced by the action, with the success or failure of the action set within the object.
        """
        obs = Observation()

        if self.session not in state.sessions[self.agent]:
            self.log("Session does not exist in the state.")
            obs.set_success(False)
            return obs
             
        obs.set_success(True)
        session = state.sessions[self.agent][self.session]
        hostname = session.hostname
        host = state.hosts[hostname]

        # 1. User trys to access local service
        available_host_services = [service for service in host.services.values() if service.active]
        if len(available_host_services) > 0:
            service_to_use = state.np_random.choice(available_host_services)
            if state.np_random.integers(100) >= service_to_use.get_service_reliability():
                # service is too unreliable, so local work fails
                obs.set_success(False)
                return obs
        else:
            # no services available, so local work fails
            obs.set_success(False)
            return obs

        # 2.FALSE ALERT
        if state.np_random.random() < self.fp_detection_rate:
            host_port = host.get_ephemeral_port()
            pc = {'local_address': self.ip_address, 'local_port': host_port}
            host.events.process_creation.append(pc)

        # 3.USER ERROR
        if state.np_random.random() < self.phishing_error_rate:
            sub_action = PhishingEmail(
                agent=self.agent, session=self.session, ip_address=self.ip_address
            )
            sub_obs = sub_action.execute(state)
            obs.combine_obs(sub_obs)

        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.ip_address}"
