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
        
@pytest.mark.parametrize('green_subnet', 
    ['admin_network_subnet',
    'contractor_network_subnet',
    'office_network_subnet',
    'operational_zone_a_subnet',
    'operational_zone_b_subnet',
    'public_access_zone_subnet',
    'restricted_zone_a_subnet',
    'restricted_zone_b_subnet'])
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

@pytest.mark.parametrize('green_subnet', 
    ['admin_network_subnet',
    'contractor_network_subnet',
    'office_network_subnet',
    'operational_zone_a_subnet',
    'operational_zone_b_subnet',
    'public_access_zone_subnet',
    'restricted_zone_a_subnet',
    'restricted_zone_b_subnet'])
@pytest.mark.parametrize('mission_phase', [0,1,2])
def test_Score_GreenAccessService(green_subnet, mission_phase):
    # Set up CybORG with EnterpriseScenarioGenerator (cc4)
    esg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent, green_agent_class=SleepAgent, red_agent_class=SleepAgent
    )
    # seed 100 causes BlockTrafficZone not to work for blue_agent_4, due to action_space not having session 0 ???
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

    # Get a list of blue agents and their subnets
    blue_agents_to_subnet = {}
    for hostname, host in env.state.hosts.items():
        for agent, sess in host.sessions.items():
            if len(sess) > 0 and 'blue' in agent:
                if not agent in blue_agents_to_subnet.keys():
                    blue_agents_to_subnet[agent] = env.state.hostname_subnet_map[hostname]

    # Add BlockTrafficZone actions to step actions
    for agent, subnet in blue_agents_to_subnet.items():
        action = BlockTrafficZone(session=0, agent=agent, to_subnet=subnet.value, from_subnet=green_subnet)
        step_actions[agent] = action

    # Do the parallel step
    env.state.mission_phase = mission_phase
    obs, reward, dict3, dict4 = cyborg.parallel_step(actions=step_actions)

    # Check all the BlockTrafficZone actions were successful
    block_obs = {agent: obs for agent, obs in obs.items() if 'blue' in agent}
    for block_obs in block_obs.values():
        assert 'BlockTrafficZone' in str(block_obs['action']) 
        assert block_obs['success'] == True

    # Check that the GreenAccessService failed
    assert 'GreenAccessService' in str(obs[green_agent_name]['action'])
    assert obs[green_agent_name]['success'] == False

    brm = BlueRewardMachine(green_hostname)
    intended_reward = brm.get_phase_rewards(env.state.mission_phase)[green_subnet]['ASF']

    # Check the reward was correct
    assert intended_reward == reward['blue_agent_0']['BlueRewardMachine']