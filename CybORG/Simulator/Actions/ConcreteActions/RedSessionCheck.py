from CybORG.Shared import Observation
from CybORG.Simulator.Actions.ConcreteActions.LocalAction import LocalAction
from CybORG.Simulator.State import State


class RedSessionCheck(LocalAction):
    """Red Agents check they have access to a primary session"""

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
        obs = Observation(True)
        if state.sessions_count[self.agent] == 0:
            return obs

        active_sessions = state.sessions[self.agent]
        assert all(s.active for s in active_sessions.values())

        if 0 not in active_sessions:
            self._choose_new_primary_session(active_sessions, state)

        obs = self._all_red_sessions_observation(state, obs)
        return obs

    def _choose_new_primary_session(self, active_sessions, state):
        """This function will create a new primary session"""
        # Randomly choose and update primary session
        old_id = state.np_random.choice(list(active_sessions.keys()))
        new_primary_session = active_sessions.pop(old_id)
        new_primary_session.active=True
        new_primary_session.parent=None
        new_primary_session.children={}
        new_primary_session.ident=0
        active_sessions[new_primary_session.ident]=new_primary_session

        # update host session information
        new_session_host = state.hosts[new_primary_session.hostname].sessions[self.agent]
        new_session_host.remove(old_id)
        new_session_host.insert(0, new_primary_session.ident)

        # update the red sessions with reference to parent or child ident
        for id, session in active_sessions.items():
            if id == 0:
                continue

            session.parent=new_primary_session.name
            new_primary_session.children[session.ident]=session

    def _all_red_sessions_observation(self, state, obs):
        for sess in state.sessions[self.agent].values():
            host_ip = str(state.hostname_ip_map[sess.hostname])
            subnet = state.subnet_name_to_cidr[state.hostname_subnet_map[sess.hostname]]
            obs.add_session_info(hostid=sess.hostname, username=sess.username, session_id=sess.ident, agent=self.agent, session_type=sess.session_type)
            obs.add_interface_info(hostid=sess.hostname, ip_address=host_ip, subnet=subnet)
            obs.add_system_info(hostid=sess.hostname, hostname=sess.hostname)
        return obs
