from __future__ import annotations
from gymnasium import Space, spaces

from CybORG import CybORG
from CybORG.Simulator import State
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import (
    EnterpriseScenarioGenerator,
)

from typing import Any

import numpy as np
import networkx as nx

import functools
import itertools

from CybORG.Agents.Wrappers.BlueFixedActionWrapper import (
    BlueFixedActionWrapper,
    MESSAGE_LENGTH,
    EMPTY_MESSAGE,
    NUM_MESSAGES,
)

NUM_SUBNETS = 9
NUM_HQ_SUBNETS = 3

MAX_USER_HOSTS = EnterpriseScenarioGenerator.MAX_USER_HOSTS
MAX_SERVER_HOSTS = EnterpriseScenarioGenerator.MAX_SERVER_HOSTS
MAX_HOSTS = MAX_USER_HOSTS + MAX_SERVER_HOSTS


class BlueFlatWrapper(BlueFixedActionWrapper):
    """Converts observation spaces to vectors of fixed size and ordering across episodes.

    This is a companion wrapper to the BlueFixedActionWrapper and inherits the fixed
    action space and int-to-action mappings as a result.

    Using the *sorted* host and subnet lists from FixedAction wrapper, this wrapper
    establishes the maximum observation space for each agent. On each step, the
    observation vectors are populated such that each element within a vector will
    have a consistent meaning across runs. This is critical for RL-based agents.
    """

    def __init__(self, env: CybORG, *args, **kwargs):
        """Initialize the BlueFlatWrapper for blue agents.

        Note: The padding setting is inherited from BlueFixedActionWrapper.

        Args:
            env (CybORG): The environment to wrap.

            *args, **kwargs: Extra arguments are ignored.
        """
        super().__init__(env, *args, **kwargs)
        self._short_obs_space, self._long_obs_space = self._get_init_obs_spaces()
        self.comms_policies = self._build_comms_policy()
        self.policy = {}

    def reset(self, *args, **kwargs) -> tuple[dict[str, Any], dict[str, Any]]:
        """Reset the environment and update the observation space.

        Args: All arguments are forwarded to the env provided to __init__.

        Returns
        -------
        observation : dict[str, Any]
            The observations corresponding to each agent, translated into a vector format.
        info : dict[str, dict]
            Forwarded from self.env.
        """
        observations, info = super().reset(*args, **kwargs)
        self.comms_policies = self._build_comms_policy()
        observations = {
            a: self.observation_change(a, observations[a]) for a in self.agents
        }
        return observations, info

    def step(
        self,
        actions: dict[str, int | Action] = None,
        messages: dict[str, Any] = None,
        **kwargs,
    ) -> tuple[
        dict[str, np.ndarray],
        dict[str, float],
        dict[str, bool],
        dict[str, bool],
        dict[str, dict],
    ]:
        """Take a step in the enviroment.

        Parameters:
            action_dict : dict[str, int | Action]
                The action or action index corresponding to each agent. 
                Indices will be mapped to CybORG actions using the equivalent of `actions(k)[v]`. 
                The meaning of each action can be found using `action_labels(k)[v]`.
            messages : dict[str, Any]
                Messages from each agent. If an agent does not specify a message, it will send an empty message.
            **kwargs : dict[str, Any]
                Extra keywords are forwarded.

        Returns
        -------
        observation : dict[str, np.ndarray] 
            Observations for each agent as vectors.
        rewards : dict[str, float] 
            Rewards for each agent.
        terminated : dict[str, bool]
            Flags whether the agent finished normally.
        truncated : dict[str, bool]
            Flags whether the agent was stopped by env.
        info : dict[str, dict]
            Forwarded from BlueFixedActionWrapper.
        """
        observations, rewards, terminated, truncated, info = super().step(
            actions=actions, messages=messages, **kwargs
        )

        observations = {
            agent: self.observation_change(agent, obs)
            for agent, obs in sorted(observations.items())
            if "blue" in agent
        }
        return observations, rewards, terminated, truncated, info

    def _get_init_obs_spaces(self):
        """Calculates the size of the largest observation space for each agent."""
        observation_space_components = {
            "mission": [3],
            "blocked_subnets": NUM_SUBNETS * [2],
            "comms_policy": NUM_SUBNETS * [2],
            "malicious_processes": MAX_HOSTS * [2],
            "network_connections": MAX_HOSTS * [2],
            "subnet": NUM_SUBNETS * [2],
            "messages": (NUM_MESSAGES * MESSAGE_LENGTH) * [2],
        }

        observation_head = observation_space_components["mission"]
        observation_tail = observation_space_components["messages"]
        observation_middle = list(
            itertools.chain(
                *[
                    v
                    for k, v in observation_space_components.items()
                    if k not in ("mission", "messages")
                ]
            )
        )

        short_observation_components = (
            observation_head + observation_middle + observation_tail
        )

        long_observation_components = (
            observation_head + (NUM_HQ_SUBNETS * observation_middle) + observation_tail
        )

        short_observation_space = spaces.MultiDiscrete(short_observation_components)
        long_observation_space = spaces.MultiDiscrete(long_observation_components)

        self._observation_space = {
            agent: long_observation_space
            if self.is_padded or agent == "blue_agent_4"
            else short_observation_space
            for agent in self.agents
        }

        return short_observation_space, long_observation_space

    def observation_change(self, agent_name: str, observation: dict) -> np.ndarray:
        """Converts an observation dictionary to a vector of fixed size and ordering.

        Parameters
        ----------
        agent_name : str
            Agent corresponding to the observation.
        observation : dict 
            Observation to convert to a fixed vector.

        Returns
        -------
        output : np.ndarray
        """
        state = self.env.environment_controller.state

        proto_observation = []

        # Mission Phase
        mission_phase = state.mission_phase
        proto_observation.append(mission_phase)

        # Useful (sorted) information
        sorted_subnet_name_to_cidr = sorted(state.subnet_name_to_cidr.items())
        subnet_names, subnet_cidrs = zip(*sorted_subnet_name_to_cidr)
        subnet_names = [name.lower() for name in subnet_names]
        hosts = self.hosts(agent_name)

        for subnet in self.subnets(agent_name):
            # One-hot encoded subnet vector
            subnet_subvector = [subnet == name for name in subnet_names]

            # Get blocklist
            blocked_subnets = state.blocks.get(subnet, [])
            blocked_subvector = [s in blocked_subnets for s in subnet_names]

            # Comms
            comms_policy = self.comms_policies[state.mission_phase]
            comms_matrix = nx.to_numpy_array(comms_policy, nodelist=subnet_names)
            comms_policy_subvector = comms_matrix[subnet_names.index(subnet)]
            comms_policy_subvector = np.logical_not(comms_policy_subvector)
            self.policy[agent_name] = comms_policy

            # Process malware events for users, then servers
            subnet_hosts = [h for h in hosts if subnet in h and "router" not in h]

            process_subvector = [
                h in state.hosts and 0 < len(self._get_procesess(state, h))
                for h in subnet_hosts
            ]

            connection_subvector = [
                h in state.hosts and 0 < len(self._get_connections(state, h))
                for h in subnet_hosts
            ]

            proto_observation.extend(
                itertools.chain(
                    subnet_subvector,
                    blocked_subvector,
                    comms_policy_subvector,
                    process_subvector,
                    connection_subvector,
                )
            )

        output = np.array(proto_observation, dtype=np.int64)

        # Messages from other agents
        # This assumes CybORG provides a consistent ordering.
        messages = observation.get("message", [EMPTY_MESSAGE] * NUM_MESSAGES)
        assert len(messages) == NUM_MESSAGES

        message_subvector = np.concatenate(messages)
        assert len(message_subvector) == NUM_MESSAGES * MESSAGE_LENGTH

        output = np.concatenate([output, message_subvector])

        # Apply padding as required
        if self.is_padded:
            output = np.pad(
                output, (0, self._long_obs_space.shape[0] - output.shape[0])
            )

        return output

    def _build_comms_policy(self):
        policy_dict = {}
        mission_phases = ["Preplanning", "MissionA", "MissionB"]
        for mission in mission_phases:
            network = self._build_comms_policy_network(mission)
            index = mission_phases.index(mission)
            policy_dict[index] = network
        return policy_dict

    def _build_comms_policy_network(self, mission: str):
        hosts = (
            "internet_subnet",
            "admin_network_subnet",
            "office_network_subnet",
            "public_access_zone_subnet",
            "contractor_network_subnet",
            "restricted_zone_a_subnet",
            "restricted_zone_b_subnet",
        )

        network = nx.complete_graph(len(hosts))
        node_mapping = dict(enumerate(hosts))
        network = nx.relabel_nodes(network, node_mapping)

        network.add_edges_from((
            ("restricted_zone_a_subnet", "operational_zone_a_subnet"),
            ("restricted_zone_b_subnet", "operational_zone_b_subnet"),
        ))

        if mission == "MissionA":
            network.remove_edges_from((
                ("restricted_zone_a_subnet", "operational_zone_a_subnet"),
                ("restricted_zone_a_subnet", "contractor_network_subnet"),
                ("restricted_zone_a_subnet", "restricted_zone_b_subnet"),
                ("restricted_zone_a_subnet", "internet_subnet"),
            ))
        elif mission == "MissionB":
            network.remove_edges_from((
                ("restricted_zone_b_subnet", "operational_zone_b_subnet"),
                ("restricted_zone_b_subnet", "contractor_network_subnet"),
                ("restricted_zone_b_subnet", "restricted_zone_a_subnet"),
                ("restricted_zone_b_subnet", "internet_subnet"),
            ))

        return network

    def _get_procesess(self, state: State, hostname: str):
        observed_proc_events = state.hosts[hostname].events.old_process_creation
        unobserved_proc_events = state.hosts[hostname].events.process_creation
        return observed_proc_events + unobserved_proc_events

    def _get_connections(self, state: State, hostname: str):
        observed_conn_events = state.hosts[hostname].events.old_network_connections
        unobserved_conn_events = state.hosts[hostname].events.network_connections
        return observed_conn_events + unobserved_conn_events

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent_name: str) -> Space:
        """Returns the multi-discrete space corresponding to the given agent."""
        return self._observation_space[agent_name]

    @functools.lru_cache(maxsize=None)
    def observation_spaces(self) -> dict[str, Space]:
        """Returns multi-discrete spaces corresponding to each agent."""
        return {a: self.observation_space(a) for a in self.possible_agents}
