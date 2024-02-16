# The following code contains work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.
# Additionally, we waive copyright and related rights in the utilized code worldwide through the CC0 1.0 Universal public domain dedication.

"""
Handling of privilege escalation action selection and execution
"""
#pylint: disable=invalid-name

from typing import Tuple, Optional, List

from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.EscalateActions.EscalateAction import (
        ExploreHost, EscalateAction
        )
from CybORG.Simulator.Actions.ConcreteActions.EscalateActions.JuicyPotato import JuicyPotato
from CybORG.Simulator.Actions.ConcreteActions.EscalateActions.V4L2KernelExploit import V4L2KernelExploit
from CybORG.Shared.Enums import (
    OperatingSystemType, TernaryEnum)
from CybORG.Simulator.State import State
from CybORG.Shared.Session import RedAbstractSession, Session

# pylint: disable=too-few-public-methods
class EscalateActionSelector:
    """
    Examines the target host and returns a selected applicable escalate action
    if any, as well as processes that are required to be genuine
    """
    # pylint: disable=missing-function-docstring
    def get_escalate_action(self, *, state: State, session: int, target_session: int,
            agent: str, hostname: str) -> \
                    Optional[EscalateAction]:
        raise NotImplementedError

class DefaultEscalateActionSelector(EscalateActionSelector):
    """
    Attempts to use Juicy Potato if windows, otherwise V4l2 kernel
    """
    def get_escalate_action(self, *, state: State, session: int, target_session: int,
            agent: str, hostname: str) -> Optional[EscalateAction]:
        session_obj = state.sessions[agent].get(session)
        if session_obj is None:
            return
        if not isinstance(session_obj, RedAbstractSession):
            return
        if session_obj.operating_system.get(hostname, None) == OperatingSystemType.WINDOWS:
            return JuicyPotato(session=session, target_session=target_session, agent=agent)
        return V4L2KernelExploit(session=session, target_session=target_session, agent=agent)
_default_escalate_action_selector = DefaultEscalateActionSelector()


class PrivilegeEscalate(Action):
    """
    A Red action that attempts to conduct privilege escalation on a host that the agent has a user shell on, to gain a shell with root privileges.
    
    Attributes
    ----------
    hostname: str
        The name of the target host.
    session: int
        The source session id.
    agent: str
        The name of the red agent executing the action.
    escalate_action_selector: EscalateActionSelector
        A selector that chooses an applicable escalate action for the target host, as well as required processes.
    """
    def __init__(self, hostname: str, session: int, agent: str):
        """ Parameters
        ----------
        hostname: str
            The name of the target host.
        session: int
            The source session id.
        agent: str
            The name of the red agent executing the action.
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.escalate_action_selector = _default_escalate_action_selector
        self.duration=2
    

    def __perform_escalate(self, state:State, sessions:List[Session]) -> Tuple[Observation, int]:
        """ 
        Chooses a random session the agent has on the target host, and (if it is not in a sandbox) chooses and executes a privilege escalation action on that session.

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.
        sessions: List[Session]
            A list of the sessions the red agent has on the target host.
        
        Returns
        -------
        : Observation
            An observation containing an indication of the action's successful execution as True/False.
        : int
            The target session's ident on the target host. This is -1 for an unsuccessful execution.
        """
        target_session = state.np_random.choice(sessions)

        #print(f"""
        #Host {self.hostname} attempting escalate:
        #Session {target_session.__dict__}""")

        # test if session is in a sandbox
        if target_session.is_escalate_sandbox:
            state.remove_process(target_session.hostname, target_session.pid)
            return Observation(success=False), -1

        target_session_ident = target_session.ident

        sub_action = self.escalate_action_selector.get_escalate_action(
                state=state, session=self.session, target_session=target_session_ident,
                agent=self.agent, hostname=self.hostname)

        self.sub_action = sub_action

        if sub_action is None:
            return Observation(success=False), -1

        return sub_action.execute(state), target_session_ident

    def execute(self, state: State) -> Observation:
        """ 
        Attempts to privilege escalate a user shell on the target host to gain a root privileged shell.

        Parameters
        ----------
        state: State
            The state of the simulated network at the current step.
        
        Returns
        -------
        obs: Observation
            An observation containing an indication of the action's successful execution as True/False.
        """
        # find session on the chosen host
        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        if len(sessions) == 0:
            # no valid session could be found on chosen host
            return Observation(success=False)
        # find if any session are already SYSTEM or root
        target_session = None
        obs = Observation(False)
        for sess in sessions:
            # else find if session is Admin or sudo
            if sess.has_privileged_access():
                target_session = sess.ident
                obs = Observation(success=True)
                obs.add_session_info(hostid=self.hostname, **sess.get_state())
                break
        # else use random session
        if target_session is None:
            obs, target_session = self.__perform_escalate(state, sessions)

        if obs.data['success'] is not TernaryEnum.TRUE:
            return obs

        sub_action = ExploreHost(session=self.session, target_session=target_session,
                agent=self.agent)
        obs2 = sub_action.execute(state)
        for host in obs2.data.values():
            try:
                host_processes = host['Processes']
                for proc in host_processes:
                    if proc.get('service_name') == 'OTService':
                        state.sessions[self.agent][self.session].ot_service = 'OTService'
                        break
            except KeyError:
                pass
            except TypeError:
                pass

        obs.combine_obs(obs2)
        return obs

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return all((
            self.name == other.name, 
            self.hostname == other.hostname,
            self.agent == other.agent,
            self.session == other.session,
        ))
