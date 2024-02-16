from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Actions.ConcreteActions.DensityScout import DensityScout
from CybORG.Simulator.Actions.ConcreteActions.SigCheck import SigCheck


class Analyse(Action):
    """ Checks for malware on a single host.

    Targets a single host and returns any files that have Density >0.9. Based on Density Scout.
    https://cert.at/en/downloads/software/software-densityscout

    Attributes
    ----------
    session: int
        the session id of the session
    agent: str
        the name of the agent executing the action
    hostname: str
        the name of the host action is targetting.
    """
    def __init__(self, session: int, agent: str, hostname: str):
        """ Instantiates Analyse action.

        Parameters
        ----------
        session: int
            the session id of the session
        agent: str
            the name of the agent executing the action
        hostname: str
            the name of the host action is targetting.
        """
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.duration = 2

    def execute(self, state) -> Observation:
        """ Executes the Action.
        Parameters
        ----------
        state: State
            The current CybORG state.
        
        Returns
        -------
        obs: Observation
            The observation to be returned to the agent.
        """
        # perform monitor at start of action
        #monitor = Monitor(session=self.session, agent=self.agent)
        #obs = monitor.execute(state)
        
        artefacts = [DensityScout, SigCheck]
        # find relevant session on the chosen host
        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        if len(sessions) < 1:
            self.log('Failed because relevant session could not be found!')
            return Observation(False)
        session = state.np_random.choice(sessions)
        # run the artifacts on the chosen host
        obs = Observation(True)
        for artifact in artefacts:
            sub_action = artifact(
                agent=self.agent, session=self.session, target_session=session.ident
            )
            sub_obs = sub_action.execute(state)
            obs.combine_obs(sub_obs)
        return obs
    
    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
    
