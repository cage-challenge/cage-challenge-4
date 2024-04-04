import pytest

from CybORG.Simulator.Actions.Action import InvalidAction
from CybORG.Simulator.Process import Process
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator, SUBNET
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions.AbstractActions import Impact
from CybORG.Simulator.Actions.GreenActions.GreenLocalWork import GreenLocalWork
from CybORG.Simulator.Actions.GreenActions.GreenAccessService import GreenAccessService
from CybORG import CybORG
from CybORG.Simulator.Actions.ConcreteActions.ControlTraffic import BlockTrafficZone
from CybORG.Shared.BlueRewardMachine import BlueRewardMachine
from CybORG.Simulator.Service import Service

ordered_subnets = [
    [SUBNET.PUBLIC_ACCESS_ZONE, SUBNET.ADMIN_NETWORK, SUBNET.OFFICE_NETWORK], 
    [SUBNET.CONTRACTOR_NETWORK], 
    [SUBNET.RESTRICTED_ZONE_A],
    [SUBNET.OPERATIONAL_ZONE_A],
    [SUBNET.RESTRICTED_ZONE_B],
    [SUBNET.OPERATIONAL_ZONE_B],
]

policy_1 = [
    [1,1,1,0,1,0],
    [1,1,1,0,1,0],
    [1,1,1,1,1,0],
    [0,0,1,1,0,0],
    [1,1,1,0,1,1],
    [0,0,0,0,1,1]
]

policy_2 = [
    [1,1,1,0,1,0],
    [1,1,0,0,1,0],
    [1,0,1,0,0,0],
    [0,0,0,1,0,0],
    [1,1,0,0,1,1],
    [0,0,0,0,1,1]
]

policy_3 = [
    [1,1,1,0,1,0],
    [1,1,1,0,0,0],
    [1,1,1,1,0,0],
    [0,0,1,1,0,0],
    [1,0,0,0,1,0],
    [0,0,0,0,0,1]
]

@pytest.mark.parametrize('mission_phase', [0,1,2])
def test_blocks_not_interfere_with_green(mission_phase):

    # Set up CybORG with EnterpriseScenarioGenerator (cc4)
    esg = EnterpriseScenarioGenerator(
        blue_agent_class=SleepAgent, green_agent_class=EnterpriseGreenAgent, red_agent_class=SleepAgent, steps=300
    )

    cyborg = CybORG(scenario_generator=esg, seed=3)
    env = cyborg.environment_controller
    env.reset()

    # set all greens to have no false detections or phishing email effects
    for _, agent_interface in cyborg.environment_controller.agent_interfaces.items():
        agent = agent_interface.agent
        if isinstance(agent, EnterpriseGreenAgent):
            agent.fp_detection_rate = 0.0
            agent.phishing_error_rate = 0.0

    # for each entry in the policy table that is a 0 (where blocks should not impact as the greens are not expecting to be allowed communication to), add a block
    pol = mission_phase
    for row in range(len(comms_policies[pol])):
        for col in range(len(comms_policies[pol][row])):
            if comms_policies[pol][row][col] == 0:
                r_subnets = ordered_subnets[row]
                c_subnets = ordered_subnets[col]

                for r_sub in r_subnets:
                    for c_sub in c_subnets:
                        blocked_pair = (r_sub.value, c_sub.value)
                        if r_sub.value in cyborg.environment_controller.state.blocks.keys():
                            cyborg.environment_controller.state.blocks[r_sub.value].append(c_sub.value)
                        else:
                            cyborg.environment_controller.state.blocks[r_sub.value] = [c_sub.value]
                        
    
    # start the step count at the correct point for the desired mission phase
    if mission_phase == 0:
        cyborg.environment_controller.step_count = 0
    elif mission_phase == 1:
        cyborg.environment_controller.step_count = 100
    else:
        cyborg.environment_controller.step_count = 200

    # Run 100 steps and assert that each have the reward 0 - showing that green has not been impacted by the blocks
    for i in range(100):
        obs, reward, _, _ = cyborg.parallel_step()
        step_reward = reward['blue_agent_0']['BlueRewardMachine']

        if not step_reward == 0:
            for agent, entry in obs.items():
                if entry['success'] == False:
                    print(agent, entry['action'], entry['success'])
        assert step_reward == 0


comms_policies = [policy_1, policy_2, policy_3]
for pol in range(len(comms_policies)):
    print("Policy", pol)
    test_blocks_not_interfere_with_green(pol)

