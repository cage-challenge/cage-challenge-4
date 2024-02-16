from ipaddress import IPv4Address

from CybORG.Shared import Observation
from CybORG.Simulator.Actions.Action import RemoteAction
from CybORG.Simulator.HostEvents import NetworkConnection
from CybORG.Simulator.State import State


class Portscan(RemoteAction):
    def __init__(self, session: int, agent: str, ip_address: IPv4Address, detection_rate: float = 1):
        super().__init__(session, agent)
        self.ip_address = ip_address
        self.detection_rate = detection_rate

    def get_used_route(self, state: State, refresh = True, routing: bool = False) -> list:
        """finds the route used by the action and returns the hostnames along that route"""
        if refresh or not self.route_designated:
            target = state.ip_addresses[self.ip_address]
            source = state.sessions[self.agent][self.session].hostname
            self.route = self.get_route(state, target, source, routing)
        return self.route

    def execute(self, state: State) -> Observation:
        self.state = state
        obs = Observation()
        if self.session not in state.sessions[self.agent]:
            self.log(f"Session '{self.session}' for agent '{self.agent}' not found.")
            obs.set_success(False)
            return obs
        from_host = state.hosts[state.sessions[self.agent][self.session].hostname]
        session = state.sessions[self.agent][self.session]

        if not session.active:
            self.log("No active session found.")
            obs.set_success(False)
            return obs

        originating_ip_address = self._get_originating_ip(state, from_host, self.ip_address)
        if originating_ip_address is None:
            self.log("Could not find originating IP address.")
            obs.set_success(False)
            return obs

        target_host = state.hosts[state.ip_addresses[self.ip_address]]

        obs.set_success(True)

        # potential 'malicious' events are added to the target host to be detected by the Monitor action.
        fixed_random_value=state.np_random.random()
        for process in target_host.processes:
            for conn in process.connections:
                if conn.local_port and not conn.remote_port:
                    obs.add_process(
                        hostid=str(self.ip_address),
                        local_port=conn.local_port,
                        local_address=self.ip_address
                    )
                    if fixed_random_value <= self.detection_rate or process.decoy_type.name == 'EXPLOIT':
                        target_host.events.network_connections.append(NetworkConnection(
                            local_address=self.ip_address,
                            local_port=conn.local_port,
                            remote_address=originating_ip_address,
                            remote_port=target_host.get_ephemeral_port()
                        ))
        return obs
