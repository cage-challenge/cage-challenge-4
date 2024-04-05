import pytest

from CybORG.Simulator.Actions.Action import InvalidAction
from CybORG.Simulator.Process import Process
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Simulator.Actions.AbstractActions import Impact
from CybORG.Simulator.Actions.GreenActions.GreenLocalWork import GreenLocalWork
from CybORG.Simulator.Actions.GreenActions.GreenAccessService import GreenAccessService
from CybORG import CybORG
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import BlockTrafficZone
from CybORG.Shared.BlueRewardMachine import BlueRewardMachine
from CybORG.Simulator.Service import Service

ALL_SUBNETS = [
    'admin_network_subnet',
    'contractor_network_subnet',
    'office_network_subnet',
    'operational_zone_a_subnet',
    'operational_zone_b_subnet',
    'public_access_zone_subnet',
    'restricted_zone_a_subnet',
    'restricted_zone_b_subnet']

def test_Score_Red_Impact():
    esg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent, green_agent_class=SleepAgent, red_agent_class=SleepAgent
    )
    cyborg = CybORG(scenario_generator=esg, seed=3)
    env = cyborg.environment_controller
    env.reset()

    red_agent_str='red_agent_0'
    
    # initialise the BRM
    brm = BlueRewardMachine(red_agent_str)
    
    hostname_red = env.state.sessions[red_agent_str][0].hostname

    host = env.state.hosts[hostname_red]
    process = Process(pid=host.create_pid(), process_name=red_agent_str, username='root')
    host.processes.append(process)
    host.add_service('OTService', Service(process=process.pid))
    env.state.sessions[red_agent_str][0].ot_service = 'OTService'
    
    expected_rewards = [-5, 0, 0]
    for mp in range(3):
        env.state.mission_phase=mp
        input_action = Impact(hostname=hostname_red, agent=red_agent_str, session=0)
        input_action.duration = 1
        results = cyborg.step(action=input_action, agent=red_agent_str)
        output_action = results.action[0]
        assert isinstance(output_action, Impact)
        assert output_action.hostname == hostname_red
        reward = brm.calculate_reward(
            env.state,
            action_dict=env.action,
            agent_observations=env.observation,
            done=env.done,
            state=env.state
        )
        assert reward == expected_rewards[mp]
        
@pytest.mark.parametrize('green_subnet', ALL_SUBNETS)
@pytest.mark.parametrize('mission_phase', [0,1,2])
def test_Score_GreenLocalWork(green_subnet, mission_phase):
    # Set up CybORG with EnterpriseScenarioGenerator (cc4)
    esg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent, green_agent_class=SleepAgent, red_agent_class=SleepAgent
    )
    cyborg = CybORG(scenario_generator=esg, seed=100)
    env = cyborg.environment_controller
    env.reset()
    env.state.mission_phase = mission_phase

    green_hostname = green_subnet + '_user_host_0'
    target_host = env.state.hosts[green_hostname]

    # Fully degrade services on host
    for service in target_host.services.values():
        service._percent_reliable = 0

    green_agent = [agent for agent, sess in env.state.hosts[green_hostname].sessions.items() if len(sess)>0 and 'green' in agent][0]
    host_ip = env.state.hostname_ip_map[green_hostname]
    env.agent_interfaces[green_agent].action_space.actions[GreenLocalWork] = True

    # Perform GreenLocalWork action
    action = GreenLocalWork(agent=green_agent, session_id=0, ip_address=host_ip, fp_detection_rate=0.0, phishing_error_rate=0.0)
    obs, reward, _, _ = cyborg.parallel_step(actions={green_agent: action})

    # Check that action fails
    assert obs[green_agent]['success'] == False

    observed_reward = reward['blue_agent_0']['BlueRewardMachine']

    brm = BlueRewardMachine(green_hostname)
    intended_reward = brm.get_phase_rewards(env.state.mission_phase)[green_subnet]['LWF']

    # check that the negative reward from local work failing is correct
    assert observed_reward == intended_reward

@pytest.mark.parametrize('green_subnet', ALL_SUBNETS)
@pytest.mark.parametrize('mission_phase', [0,1,2])
def test_Score_GreenAccessService(green_subnet, mission_phase):
    # Set up CybORG with EnterpriseScenarioGenerator (cc4)
    esg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent, green_agent_class=SleepAgent, red_agent_class=SleepAgent
    )

    cyborg = CybORG(scenario_generator=esg, seed=3)
    env = cyborg.environment_controller
    env.reset()
    env.state.mission_phase = mission_phase

    # Get info about green test agent
    green_hostname = green_subnet + '_user_host_0'
    green_agent_name = [agent for agent, sess in env.state.hosts[green_hostname].sessions.items() if (len(sess)>0 and 'green' in agent)][0]
    green_agent_interface = env.agent_interfaces[green_agent_name]

    # Add GreenAccessService as a action to SleepAgent
    green_agent_interface.action_space.actions[GreenAccessService] = True

    # Initialise GreenAccessService action
    green_action = GreenAccessService(
        agent=green_agent_name,
        session_id=0,
        src_ip=env.state.hostname_ip_map[green_hostname],
        allowed_subnets=green_agent_interface.allowed_subnets,
        fp_detection_rate=0.0
    )

    # Check that action works without the block
    results = cyborg.step(agent=green_agent_name, action=green_action)
    assert results.observation['success'] == True

    # Set up step actions 
    step_actions = {}
    step_actions[green_agent_name] = green_action

    # Get a Blue agent to block from green_subnet to all other subnets
    for sub_idx in range(len(ALL_SUBNETS)):
        action = BlockTrafficZone(session=0, agent="blue_agent_0", to_subnet=green_subnet, from_subnet=ALL_SUBNETS[sub_idx]) # to_subnet and from_subnet could be either way as call/response required
        results = cyborg.step(agent="blue_agent_0", action=action)
        assert results.observation['success'] == True

    print(cyborg.environment_controller.state.blocks)

    env.state.mission_phase = mission_phase
    obs, reward, _, _ = cyborg.parallel_step(actions={green_agent_name: green_action})

    # Check that the GreenAccessService failed
    assert 'GreenAccessService' in str(obs[green_agent_name]['action'])
    assert obs[green_agent_name]['success'] == False

    brm = BlueRewardMachine(green_hostname)
    intended_reward = brm.get_phase_rewards(env.state.mission_phase)[green_subnet]['ASF']

    # Check the reward was correct
    assert intended_reward == reward['blue_agent_0']['BlueRewardMachine']