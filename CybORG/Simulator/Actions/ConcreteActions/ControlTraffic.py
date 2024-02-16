from ipaddress import IPv4Address, IPv4Network

from CybORG.Shared import Observation
from CybORG.Simulator.Actions.ConcreteActions.LocalAction import LocalAction
from CybORG.Simulator.State import State

class ControlTraffic(LocalAction):
    """Abstract parent class of all actions that control traffic."""
    def __init__(self, session, agent):
        """ 
        Parameters
        ----------
        session : int
            session id
        agent : str
            agent name
        """
        super().__init__(session, agent)
        self.priority = 1

    def execute(self, state: State) -> Observation:
        """The function that is called when the action is performed/executed.
        
        Checks that the action to be performed is valid (agent and session details)
        
        Parameters
        ----------
        state: State
            current state of the environment
        
        Returns
        -------
        :Observation
        """
        session_is_active = False
        if self.agent in state.sessions and self.session in state.sessions[self.agent]:
            session_is_active = state.sessions[self.agent][self.session].active
        if not session_is_active:
            self.log("No active session found.")
            return Observation(False)
        return self.execute_control_traffic(state)
    
    def execute_control_traffic(self, state: State):
        """Abstract function to be implemented by child class."""
        raise NotImplementedError
    

class BlockTraffic(ControlTraffic):
    def __init__(self, session: int, agent: str, ip_address: IPv4Address):
        super().__init__(session, agent)
        self.ip_address = ip_address

    def execute_control_traffic(self, state: State) -> Observation:
        hostname = state.sessions[self.agent][self.session].hostname
        other_hostname = state.ip_addresses[self.ip_address]
        if hostname in state.blocks and other_hostname in state.blocks[hostname]:
            self.log(f"'{other_hostname}' is already blocked by '{hostname}'.")
            return Observation(False)
        state.blocks.setdefault(hostname, []).append(other_hostname)
        return Observation(True)

class BlockTrafficZone(ControlTraffic):
    """Action that enables Blue agents to block off access between two subnets in the network. This functionality mimics firewall rules.
    
    Attributes
    ----------
    from_subnet: str
        name of subnet that the traffic should be blocked from
    to_subnet: str
        name of subnet that the traffic should be blocked from going to
    """
    def __init__(self, session: int, agent: str, from_subnet: str, to_subnet: str):
        """
        Parameters
        ----------
        session: int
            session identifier
        agent: str
            name of agent performing action
        from_subnet: str
            name of subnet that the traffic should be blocked from
        to_subnet: str
            name of subnet that the traffic should be blocked from going to
        """
        super().__init__(session, agent)
        self.from_subnet = from_subnet
        self.to_subnet = to_subnet

    def execute_control_traffic(self, state: State) -> Observation:
        """Checks for pre-existing blocks, and blocks the connection between the to and from subnet.
        
        Parameters
        ----------
        state: State
            the current state of the environment


        Returns
        -------
        : Observation
            the observation space for this action, holding a true or false success value
        """
        # Check if subnets given are subnets
        if self.from_subnet not in state.subnet_name_to_cidr.keys():
            self.log(f"'{self.from_subnet}' is not a valid subnet.")
            return Observation(False)
        if self.to_subnet not in state.subnet_name_to_cidr.keys():
            self.log(f"'{self.to_subnet}' is not a valid subnet.")
            return Observation(False)
        # Check not already blocked
        if self.to_subnet in state.blocks and self.from_subnet in state.blocks[self.to_subnet]:
            self.log(f"'{self.to_subnet}' is already blocked by '{self.from_subnet}'.")
            return Observation(False)

        state.blocks.setdefault(self.to_subnet, []).append(self.from_subnet)
        return Observation(True)

class AllowTraffic(ControlTraffic):
    def __init__(self, session: int, agent: str, ip_address: IPv4Address):
        super().__init__(session, agent)
        self.ip_address = ip_address

    def execute_control_traffic(self, state: State) -> Observation:
        hostname = state.sessions[self.agent][self.session].hostname
        other_hostname = state.ip_addresses[self.ip_address]
        if hostname in state.blocks and other_hostname in state.blocks[hostname]:
            state.blocks[hostname].remove(other_hostname)
            return Observation(True)
        self.log(f"'{other_hostname}' is not blocked by '{hostname}'.")
        return Observation(False)

class AllowTrafficZone(ControlTraffic):
    """Action that enables Blue agents to unblock access between two subnets in the network. This functionality mimics reversing firewall rules.
    
    Attributes
    ----------
    from_subnet: str
        name of subnet that the traffic should be unblocked from
    to_subnet: str
        name of subnet that the traffic should be unblocked from going to
    """
    def __init__(self, session: int, agent: str, from_subnet: str, to_subnet: IPv4Network):
        """
        Parameters
        ----------
        session: int
            session identifier
        agent: str
            name of agent performing action
        from_subnet: str
            name of subnet that the traffic should be unblocked from
        to_subnet: str
            name of subnet that the traffic should be unblocked from going to
        """
        super().__init__(session, agent)
        self.from_subnet = from_subnet
        self.to_subnet = to_subnet

    def execute_control_traffic(self, state: State) -> Observation:
        """Checks for specific pre-existing block, and removes it.
        
        Parameters
        ----------
        state: State
            the current state of the environment


        Returns
        -------
        : Observation
            the observation space for this action, holding a true or false success value
        """
        # Check if subnets given are subnets
        if self.from_subnet not in state.subnet_name_to_cidr.keys():
            self.log(f"'{self.from_subnet}' is not a valid subnet.")
            return Observation(False)
        if self.to_subnet not in state.subnet_name_to_cidr.keys():
            self.log(f"'{self.to_subnet}' is not a valid subnet.")
            return Observation(False)
        # Check not already blocked
        if self.to_subnet in state.blocks and self.from_subnet in state.blocks[self.to_subnet]:
            state.blocks[self.to_subnet].remove(self.from_subnet)
            return Observation(True)
        self.log(f"'{self.to_subnet}' is not blocked by '{self.from_subnet}'.")
        return Observation(False)
