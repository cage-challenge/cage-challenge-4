from __future__ import annotations
from typing import Any

import numpy as np

from CybORG import CybORG
from CybORG.Agents.Wrappers.BlueFixedActionWrapper import (
    MESSAGE_LENGTH,
    EMPTY_MESSAGE,
    NUM_MESSAGES,
)

from gymnasium.spaces import Space

from CybORG.Agents.Wrappers import BlueFlatWrapper, BlueFixedActionWrapper


class BlueEnterpriseWrapper(BlueFlatWrapper):
    """A wrapper designed to support CAGE Challenge 4.

    Creates a vector output for a neural network by directly pulling
    information out of the state object.
    """

    def step(
        self,
        actions: dict[str, Any] | None = None,
        messages: dict[str, Any] | None = None,
    ) -> tuple[
        dict[str, np.ndarray],
        dict[str, float],
        dict[str, bool],
        dict[str, bool],
        dict[str, dict],
    ]:
        """Take a step in the enviroment using action indices.

        This wrapper supports both the CybORG and original EnterpriseMAE
        parameter conventions. For example:

            actions = { "blue_agent_0": 42 }
            messages = { "blue_agent_0": np.array([1, 0, 0, 0, 0, 0, 0, 0] }

            # CybORG Convention (preferred)
            env.step(action_dict=actions, messages=messages)

            # EnterpriseMAE Convention
            env.step({
                "actions": actions,
                "messages": messages,
            })

        Args:

            action_dict (dict[str, int]): The action index corresponding to each
                agent. These indices will be mapped to CybORG actions using the
                equivalent of `actions(agent)[index]`. The meaning of each action
                can be found using `action_labels(agent)[index]`.

            messages (dict[str, Any]): Optional messages to be passed to each agent.

            **kwargs (dict[str, Any]): Extra keywords are forwarded.

        Returns:
            observation (dict[str, np.ndarray]): Observations for each agent as vectors.

            rewards (dict[str, float]): Rewards for each agent.

            terminated (dict[str, bool]): Flags whether the agent finished normally.

            truncated (dict[str, bool]): Flags whether the agent was stopped by env.

            info (dict[str, dict]): Forwarded from BlueFixedActionWrapper.
        """
        action_dict = actions if actions is not None else {}

        # Use EnterpriseMAE parameter handling
        if "actions" in action_dict:
            # Messages keyword is ignored if action_dict specifies messages.
            messages = action_dict.get("messages", messages)
            return super().step(action_dict["actions"], messages=messages)

        # Use CybORG parameters
        return super().step(action_dict, messages=messages)

    def reset(
        self, agent=None, seed=None, *args, **kwargs
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Reset the environment and update the observation space.

        Args:
            seed (Optional[int]): Set the environment's seed.

        Returns:
            observation (dict[str, Any]): The observations corresponding to each
                agent, translated into a vector format.

            info (dict[str, dict]): Forwarded from self.env.
        """
        return super().reset(agent=agent, seed=seed)

    @property
    def long_observation_space(self) -> Space:
        """Observation space used for blue_agent_4.
        This is the largest observation space for this environment.

        Deprecated in favour of self.observation_space(agent_name).
        """
        return self._long_obs_space

    @property
    def short_observation_space(self) -> Space:
        """Observation space used for agents other than blue_agent_4.

        This is the standard observation space for this environment UNLESS the
        pad_spaces option is explicitly enabled for the wrapper. If pad_spaces
        is enabled, all agents use self.long_observation_spaces() instead.

        Deprecated in favour of self.observation_space(agent_name), which
        returns the appropriate observation for each agent.
        """
        return self._short_obs_space
