from __future__ import annotations
from typing import Any

import numpy as np

from CybORG.Agents.Wrappers import BlueEnterpriseWrapper
from ray.rllib.env.multi_agent_env import MultiAgentEnv


class EnterpriseMAE(BlueEnterpriseWrapper, MultiAgentEnv):
    """A wrapper designed to support CAGE Challenge 4 (RLlib Compatible).

    Creates a vector output for a neural network by directly pulling
    information out of the state object.
    """

    def step(
        self,
        action_dict: dict[str, Any] | None = None,
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
        obs, rew, terminated, truncated, info = super(BlueEnterpriseWrapper, self).step(
            actions=action_dict, messages=messages
        )
        terminated["__all__"] = False
        truncated["__all__"] = self.env.environment_controller.determine_done()
        return obs, rew, terminated, truncated, info
