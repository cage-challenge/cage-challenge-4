from ipaddress import IPv4Address
import pytest

from CybORG.Shared import Observation
from CybORG.Simulator.Actions import GreenLocalWork, GreenAccessService, Sleep
from CybORG.Tests.test_cc4.cyborg_env_creation import create_cyborg_env


def test_EnterpriseGreenAgent():
    """Test that checks the EnterpriseGreenAgent class can be setup in the environment and that all its attributes are filled. """

    cyborg, agent_interface = create_cyborg_env()
    agent = agent_interface.agent
    agent_name = agent.name
    # Setup Agent
    action_space = cyborg.get_action_space(agent_name)
    assert action_space['session']

    # Check attributes are not empty
    assert agent.own_ip is not None
    assert isinstance(agent.own_ip, IPv4Address)
    assert 0.0 <= agent.fp_detection_rate <= 1.0
    assert 0.0 <= agent.fp_detection_rate <= 1.0

def test_actions_in_action_space():
    """Test that checks that an EnterpriseGreenAgent's actions (in its action_space) are the expected three actions for CC4.
    
    Expected actions are:
        - Sleep
        - GreenLocalWork
        - GreenAccessService
    """

    expected_actions = {Sleep, GreenLocalWork, GreenAccessService}

    cyborg, agent_interface = create_cyborg_env()
    agent = agent_interface.agent
    agent_name = agent.name

    action_space = cyborg.get_action_space(agent_name)
    actions = set(action_space['action'].keys())
    
    assert actions == expected_actions

def test_action_return():
    """Tests that the EnterpriseGreenAgent get_action function only returns the expected actions, over 20 iterations."""
    expected_actions = [Sleep, GreenLocalWork, GreenAccessService]

    cyborg, agent_interface = create_cyborg_env()
    agent = agent_interface.agent
    agent_name = agent.name

    for i in range(0, 20):
        return_value = agent.get_action(observation=Observation(), action_space=cyborg.get_action_space(agent_name))
        assert True in [isinstance(return_value, action_type) for action_type in expected_actions]
