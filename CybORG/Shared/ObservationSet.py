from typing import List

from CybORG.Shared import Observation

class ObservationSet:
    """Collection of Observation objects 
    
    Attributes
    ----------
    observations: List[Observation]
        list of Observation objects
    """
    def __init__(self, observations: List[Observation]):
        """ 
        Parameters
        ----------
        observations: List[Observation]
            initial list of observations
        """
        self.observations: List[Observation] = observations
    
    def get_combined_observation(self) -> Observation:
        """Returns the observations as a single Observation or ObservationSet depending on size."""
        if len(self.observations) == 0:
            return Observation()
        combined_observation = self.observations[0]
        if len(self.observations) > 1:
            for observation in self.observations[1:]:
                combined_observation.combine_obs(observation)
        return combined_observation

    def append(self, observation):
        """Adds an observation to it's observations attribute list."""
        self.observations.append(observation)
