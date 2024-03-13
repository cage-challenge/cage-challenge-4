from __future__ import annotations
from gymnasium import Space, spaces

from CybORG import CybORG
from CybORG.Agents.Wrappers import BaseWrapper
from CybORG.Simulator.Actions import Action, Sleep
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import (
    EnterpriseScenarioGenerator,
)

import functools
import numpy as np
from typing import Any

SUBNET_USER_FORMAT = "{subnet}_user_host_{host}"
SUBNET_SERVER_FORMAT = "{subnet}_server_host_{host}"
SUBNET_ROUTER_FORMAT = "{subnet}_router"

NUM_MESSAGES = 4
MESSAGE_LENGTH = 8
EMPTY_MESSAGE = np.zeros(MESSAGE_LENGTH, dtype=bool)

DISABLE_SANITY_CHECKS = True


class BlueFixedActionWrapper(BaseWrapper):
    """Maintains action spaces with fixed sizes and ordering across episodes.

    On initialization, this wrapper creates a *sorted* list of all the hosts
    and subnets each agent can interact with in the CC4 EnterpriseScenario.

    On reset, the action space is populated using these sorted lists,
    translating hostnames to IP addresses where needed, such that any
    given action index will always correspond to a specific host. If
    a host does not exist in the current episode, the action will be
    replaced with a no-op (Sleep) action. Agents can check whether an
    action corresponds to an active host by consulting action_mask().

    Note: This wrapper does not change the observation space. See the
    companion wrapper `BlueFlatWrapper` for vector observations of
    fixed length and order.
    """

    def __init__(self, env: CybORG, pad_spaces: bool = False, *args, **kwargs):
        """Initialize the BlueFixedActionWrapper for blue agents.

        Parameters
        ----------
        env : CybORG
            An instance of CybORG. Must not modify action_space.
        pad_spaces : bool 
            Ensure all observation and action spaces are the same size across all agents by padding the space with the Sleep action. 
            This is a requirement for some RL libraries.
        *args, **kwargs
            Extra arguments are ignored.
        """
        super().__init__(env)

        # Filter out non-blue da ba dee da ba di
        self.agents = self.possible_agents = [a for a in env.agents if "blue" in a]

        # Variables to track max space sizes for padding
        self._pad_spaces = pad_spaces
        self._max_act_space_size = 0

        # Maintain a **sorted** record of subnets and hosts to ensure consistency
        self._agent_metadata = {}
        self._action_space = {}

        for agent in self.agents:
            self._create_hardcoded_metadata(agent)
            self._populate_action_space(agent)
        self._host_sanity_check()
        self._apply_padding()

    def reset(self, *args, **kwargs) -> tuple[dict[str, Any], dict[str, dict]]:
        """Reset the environment and update the action space.

        Parameters: All arguments are forwarded to the env provided to __init__.

        Returns
        -------
        observation : dict[str, Any]
            The observations corresponding to each agent. Forwarded directly from the env provided to __init__.

        info : dict[str, dict]
            Information dictionaries corresponding to each agent. 
            Each dictionary contains the key "action_mask" that maps to a list[bool] where each element corresponds to whether the action
            at the element's index targets a host or subnet that exists for the duration of the episode.
        """
        self.env.reset(*args, **kwargs)
        self.agents = self.possible_agents
        for agent in self.agents:
            self._populate_action_space(agent)
        self._host_sanity_check()
        self._apply_padding()
        observations = {a: self.env.get_observation(a) for a in self.agents}
        info = {a: {"action_mask": self._action_space[a]["mask"]} for a in self.agents}
        return observations, info

    def step(
        self,
        actions: dict[str, int | Action] = None,
        messages: dict[str, Any] = None,
        **kwargs,
    ) -> tuple[
        dict[str, Any],
        dict[str, float],
        dict[str, bool],
        dict[str, bool],
        dict[str, dict],
    ]:
        """Take a step in the enviroment using action indices.

        Parameters
        ----------
        actions : dict[str, int] 
            The action index corresponding to each agent. 
            These indices will be mapped to CybORG actions using the equivalent of `actions(agent)[index]`. 
            The meaning of each action can be found using `action_labels(agent)[index]`.
        messages : dict[str, Any]
            Messages from each agent. If an agent does not specify a message, it will send an empty message.
        **kwargs : dict[str, Any]
            Extra keywords are forwarded.

        Returns
        -------
        observation : dict[str, Any]
            The observations corresponding to each agent. 
            Forwarded directly from the env provided to __init__.
        rewards : dict[str, float]
            Rewards for each agent.
        terminated : dict[str, bool]
            Flags whether the agent finished normally.
        truncated : dict[str, bool]
            Flags whether the agent was stopped by env.
        info : dict[str, dict] 
            Information dictionaries corresponding to each agent. 
            Each dictionary contains the key "action_mask" that maps to a list[bool] where each element corresponds to whether the action
            at the element's index targets a host or subnet that exists for the duration of the episode.
        """
        action_dict = {} if actions is None else actions
        action_dict = {
            agent: action
            if isinstance(action, Action)
            else self._action_space[agent]["actions"][action]
            for agent, action in action_dict.items()
        }

        messages = {} if messages is None else messages
        messages = {
            agent: messages.get(agent, EMPTY_MESSAGE).astype(bool)
            for agent in self.possible_agents
        }

        obs, rews, dones, info = self.env.parallel_step(
            action_dict, messages=messages, **kwargs
        )

        for agent_name in self.agents:
            if agent_name not in info:
                info[agent_name] = {}
            info[agent_name]["action_mask"] = self._action_space[agent_name]["mask"]

        self.agents = [
            agent for agent, done in dones.items() if "blue" in agent and not done
        ]

        observations = {agent: o for agent, o in obs.items() if "blue" in agent}

        rewards = {
            agent: sum(reward.values())
            for agent, reward in rews.items()
            if "blue" in agent
        }

        terminated = {agent: done for agent, done in dones.items() if "blue" in agent}
        truncated = {agent: done for agent, done in dones.items() if "blue" in agent}

        info = {
            a: {"action_mask": self._action_space[a]["mask"]}
            for a in self.possible_agents
        }

        return observations, rewards, terminated, truncated, info

    def _create_hardcoded_metadata(self, agent_name: str) -> None:
        """Identifies all hosts and subnets that the agent will ever encounter.

        The content and ordering of this list must be consistent across all
        runs, universally, as it is used to derive the full action space.
        """
        state = self.env.environment_controller.state
        agent = state.scenario.agents[agent_name]

        subnets = set(agent.allowed_subnets)
        hosts = set()
        foreign_hosts = set()

        for subnet in agent.allowed_subnets:
            hosts.add(SUBNET_ROUTER_FORMAT.format(subnet=subnet))

            for i in range(EnterpriseScenarioGenerator.MAX_USER_HOSTS):
                hosts.add(SUBNET_USER_FORMAT.format(subnet=subnet, host=i))

            for i in range(EnterpriseScenarioGenerator.MAX_SERVER_HOSTS):
                hosts.add(SUBNET_SERVER_FORMAT.format(subnet=subnet, host=i))

            # Remove this condition if blue agents need to act on foreign hosts.
            if "red" not in agent_name:
                continue

            for hostname in hosts:
                # Some hosts may not be currently active. However, these optional
                # hosts don't have any additional information, such as connections
                # to hosts on foreign subnets. This information is mostly for red.
                if hostname not in state.scenario.hosts:
                    continue

                for foreign_hostname in state.scenario.hosts[hostname].info.keys():
                    foreign_hosts.add(foreign_hostname)

                    # Add foreign subnets to list of known subnets. This is probably
                    # unnecessary since red cannot act on foreign subnets directly.
                    subnets.add(state.hostname_subnet_map[foreign_hostname].lower())

        hosts.update(foreign_hosts)
        self._agent_metadata[agent_name] = {
            "hosts": sorted(hosts),
            "subnets": sorted(subnets),
        }

    def _populate_action_space(self, agent_name: str) -> None:
        """Construct an agent's action space in a consistent order with labels and mask."""
        state = self.env.environment_controller.state

        # This assumes that the commands will never change.
        commands = self.env.get_action_space(agent_name)["action"]
        commands = sorted(list(commands), key=str)

        # Default parameters for all actions except Sleep.
        action_params = {"session": 0, "agent": agent_name}

        # This assumes that the existence of each subnet never changes.
        sorted_subnet_name_to_cidr = sorted(state.subnet_name_to_cidr.items())

        # Check if an agent has a session on a host. Host must exist.
        has_session = lambda h: 0 < len(state.hosts[h].sessions.get(agent_name, []))

        # Action space variables to populate. Order is important!
        actions = []
        labels = []
        mask = []

        for command in commands:
            command_name = command.__name__

            if command_name == "Sleep":
                actions.append(command())
                labels.append("Sleep")
                mask.append(True)
                continue

            if command_name == "Monitor":
                actions.append(command(**action_params))
                labels.append("Monitor")
                mask.append(True)
                continue

            if command_name in ("AllowTrafficZone", "BlockTrafficZone"):
                for dstname in self._agent_metadata[agent_name]["subnets"]:
                    dst = state.subnet_name_to_cidr[dstname]

                    for srcname, src in sorted_subnet_name_to_cidr:
                        srcname = srcname.lower()
                        if src == dst:
                            continue
                        actions.append(
                            command(from_subnet=srcname, to_subnet=dstname, **action_params)
                        )
                        labels.append(
                            f"{command_name} {dstname} ({dst}) <- {srcname} ({src})"
                        )
                        mask.append(True)
                continue

            # All other (host-based) commands.
            for hostname in self._agent_metadata[agent_name]["hosts"]:
                # Actions are disabled for router hosts.
                if "router" in hostname:
                    continue

                # If the target host does not currently exist, use a no-op action.
                if hostname not in state.hosts or not has_session(hostname):
                    actions.append(Sleep())
                    labels.append(f"[Invalid] {command_name} {hostname}")
                    mask.append(False)
                    continue

                actions.append(command(hostname=hostname, **action_params))
                labels.append(f"{command_name} {hostname}")
                mask.append(True)

        self._max_act_space_size = max(self._max_act_space_size, len(actions))
        self._action_space[agent_name] = {
            "actions": actions,
            "labels": labels,
            "mask": mask,
        }

    def _apply_padding(self) -> None:
        """Pad all agent action spaces to match the size of the largest action space"""
        if not self._pad_spaces:
            return

        def pad_actions(size, agent_name, key, value):
            self._action_space[agent_name][key].extend([value] * size)

        for agent_name in self.agents:
            space_size = len(self._action_space[agent_name]["actions"])
            pad_size = self._max_act_space_size - space_size

            if pad_size == 0:
                continue

            pad_actions(pad_size, agent_name, "actions", Sleep())
            pad_actions(pad_size, agent_name, "labels", "[Padding] Sleep")
            pad_actions(pad_size, agent_name, "mask", False)

    def _host_sanity_check(self) -> None:
        """Ensure hosts aren't missing from the wrapper's host list for each agent."""
        if DISABLE_SANITY_CHECKS:
            return

        state = self.env.environment_controller.state
        for agent_name in self.agents:
            session_hosts = {s.hostname for s in state.sessions[agent_name].values()}
            assert session_hosts.issubset(self._agent_metadata[agent_name]["hosts"])

    def get_action_space(self, agent: str) -> dict[str, list[Action | str | bool]]:
        """Returns all information about an agent's action space."""
        return self._action_space[agent]

    def hosts(self, agent_name: str) -> list[str]:
        """Returns an ordered list of names of hosts the agent can interact with."""
        return self._agent_metadata[agent_name]["hosts"]

    def subnets(self, agent_name: str) -> list[str]:
        """Returns an ordered list of names of subnets the agent can interact with."""
        return self._agent_metadata[agent_name]["subnets"]

    def action_mask(self, agent_name: str) -> list[bool]:
        """Returns an ordered list corresponding to whether an action is valid or not."""
        return self._action_space[agent_name]["mask"]

    def action_labels(self, agent_name: str) -> list[str]:
        """Returns an ordered list of human-readable actions."""
        return self._action_space[agent_name]["labels"]

    def actions(self, agent_name: str) -> list[Action]:
        """Returns an ordered list of CybORG actions."""
        return self._action_space[agent_name]["actions"]

    @property
    def is_padded(self) -> bool:
        """Returns whether the action space has been padded with no-ops."""
        return self._pad_spaces

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent_name: str) -> Space:
        """Returns the discrete space corresponding to the given agent."""
        if self._pad_spaces:
            return spaces.Discrete(self._max_act_space_size)
        return spaces.Discrete(len(self._action_space[agent_name]["actions"]))

    @functools.lru_cache(maxsize=None)
    def action_spaces(self) -> dict[str, Space]:
        """Returns discrete space with optional padding for each agent."""
        return {a: self.action_space(a) for a in self.agents}
