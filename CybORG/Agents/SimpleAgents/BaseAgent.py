from gym.utils import seeding
from CybORG.Shared import Results

class BaseAgent:
    """The base inherited class for any agent used in CybORG.

    This class acts as an abstract class that enforces the implementation of the agent choosing an actions. 
    It also provides placeholder functions for use when/if the agent: learns a policy, set initial values, or update its internal state.

    Attributes
    ----------
    name : str
        agent name
    np_random : Tuple[np.random.Generator, Any], optional
        contains a RNG and the seed
    """
    def __init__(self, name: str, np_random=None):
        """Initialises the instance with a given name and rnadom number generator (RNG)

        Parameters
        ----------
        name : str
            agent name
        np_random : Tuple[np.random.Generator, Any], optional
            contains a RNG and the seed, usually omitted
        """

        self.name = name
        if np_random is None:
            np_random, seed = seeding.np_random()
        self.np_random = np_random

    def train(self, results: Results):
        """Allows an agent to learn a policy
        
        Function is left empty to be overwritten by the class that inherits BaseAgent. 
        If the agent is deterministic (e.g. a heuristic agent), then this function will usually be passed.

        Parameters
        ----------
        results : Results
            class object that holds the consequences or 'results' of the agent's action

        Raises
        ------
        NotImplementedError 
            The class inheriting BaseAgent has not implemented this function
        """
        raise NotImplementedError

    def get_action(self, observation, action_space):
        """ Gets the agent's action for that step.

        The function gets an action from the agent that should be performed based on the agent's internal state and provided observation and action space. The contents is left empty to be overwritten by the class that inherits BaseAgent. 

        Parameters
        ----------
        observation : dict
            the 'data' dictionary contained within the Observation object
        action_space : dict
            a dictionary representation of the Action_Space object

        Raises
        ------
        NotImplementedError
            The class inheriting BaseAgent has not implemented this function
        """
        raise NotImplementedError

    def end_episode(self):
        """Allows an agent to update its internal state.
        
        Raises:
            NotImplementedError: The class inheriting BaseAgent has not implemented this function
        """
        raise NotImplementedError

    def set_initial_values(self, action_space, observation):
        """Allows the agent to set initial values when the AgentInterface object is first defined.

        This function is very rarely used and commonly passed in agent implementation.

        Raises
        ------
        NotImplementedError
            The class inheriting BaseAgent has not implemented this function
        """
        raise NotImplementedError

    # By default special members (e.g. __special__) and private members (e.g. _private) are not included in docstrings

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return f"{self.__class__.__name__}"
