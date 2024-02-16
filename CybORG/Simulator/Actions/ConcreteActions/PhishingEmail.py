from ipaddress import IPv4Address

from CybORG.Shared import Observation
from CybORG.Shared.Session import RedAbstractSession
from CybORG.Simulator.Actions.Action import RemoteAction
from CybORG.Simulator.State import State

class PhishingEmail(RemoteAction):
    """ The green agent action that represents the green agent 'opening a malicious email' from a red agent.

    The action creates a new red shell session on the Host that the green agent has a session on. This gives the red agent a foothold on that system.
    The red agent that gets the shell session should be located in the same subnet as the green agent.

    Attributes:
        ip_address (IPv4Address): IP address of the host that the green agent has a session on

    """
    def __init__(self, session: int, agent: str, ip_address: IPv4Address):
        """ Initalisation of PhishingEmail attributes

        Args:
            session (int): session id
            agent (str): agent name
            ip_address (IPv4Address): host IP address
        """
        super().__init__(session=session, agent=agent)
        self.ip_address = ip_address

    def execute(self, state: State) -> Observation:
        """ Execute PhishingEmail action

        Args:
            state (State): current simulation State
        
        Returns:
            obs (Observation): the resulting observation space due to the action performed
        """
        obs = Observation()
        self._create_new_session(obs, state)
        return obs
    
    def _create_new_session(self, obs: Observation, state: State) -> Observation:
        """ Creates a new red shell session on the green host object.

        Process:
            1) The green host name is discovered from the ip_address
            2) Check if a red shell session is already present on the green host
                - if so, finish action as host already 'infected'
            3) Find the red agent that is present in the green host's subnet and check routable
                - if not present, pick another routable subnet
                    - if none, return failed observation
            4) Create a new session on the green host, of the chosen red agent
            5) Add the session details to the successful Observation object and return

        Args:
            obs (Observation): a new Observation object
            state (State): current simulation state

        Returns:
            obs (Observation): the changed Observation object, due to the action occurrance
        """

        red_agent_src = ""
        red_agents = []

        green_hostname = state.ip_addresses[self.ip_address]

        # Check if red already on host
        for agent, sid in state.hosts[green_hostname].sessions.items():
            if not sid == [] and 'red' in agent:
                return obs.set_success(True)

        # Get red agent that 'sent' the phishing email
        for hostname, host in state.hosts.items():
            for agentname, sid in host.sessions.items():
                if not sid == [] and 'red' in agentname:
                    is_routable = self.check_routable(state, green_hostname, hostname)
                    if self.ip_address in host.interfaces[0].subnet and is_routable:
                        red_agent_src = agentname
                        break
                    red_agents.append((agentname, hostname))

        while red_agent_src == "":
            if red_agents == []:
                self.log("No red_agents are routable to green host.")
                return obs.set_success(False)

            r_agent = state.np_random.choice(red_agents, replace=False)

            if self.check_routable(state=state, target=green_hostname, source=r_agent[1]):
                red_agent_src = r_agent[0]
            

        # New red shell session created
        new_session = RedAbstractSession(
            ident=None,
            pid=None,
            hostname=green_hostname,
            username='user',
            agent=red_agent_src,
            parent=None,
            session_type='RedAbstractSession'
        )
        state.add_session(new_session)
        session_info = {
            'hostid': green_hostname,
            'session_id': new_session.ident,
            'session_type': new_session.session_type,
            'agent': new_session.agent}
        
        # Add the session details to the successful Observation object
        obs.add_session_info(**session_info)
        return obs.set_success(True)
