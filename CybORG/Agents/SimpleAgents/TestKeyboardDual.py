import inspect
from pprint import pprint

from CybORG import CybORG
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Agents.SimpleAgents.KeyboardAgent import KeyboardAgent
import argparse

def print_subnet_host_agents_info(env):
    for ipv4_net, subnet in env.state.subnets.items():
                    for hostname, hosts in env.state.hosts.items():
                        printer=False
                        ip_address = env.hostname_ip_map[hostname]
                        for agent_name, sess in hosts.sessions.items():
                            
                            if len(sess)>0:
                                printer=True
                                if ip_address in ipv4_net:
                                    print(subnet.name.name, '-', hostname, '-', ip_address, '-', agent_name)
                        if 'contractor_network_subnet_server_host_' in hostname and 'CONTRACT' in subnet.name.name and ip_address in ipv4_net and printer==False:
                                print(subnet.name.name, '-', hostname, '-', ip_address, '-', 'NA')
                                    
                    print()
                
    for agent_name, agent in env.agent_interfaces.items():
        if 'red' in agent_name:
            for id, session in env.state.sessions[agent_name].items():
                print(agent_name, id, session)
    
    # printing to check movement 
    for agent, session in env.state.hosts['contractor_network_subnet_server_host_0'].sessions.items():
        if len(session)>0:
            print(agent, session)

def main(args):
    sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent, red_agent_class=SleepAgent)
    cyborg = CybORG(scenario_generator=sg, seed=2023)
    cyborg.reset()

    agent_name_red = 'red_agent_0'
    agent_name_blue = 'blue_agent_0'

    observation_red = cyborg.get_observation(agent_name_red)
    action_space_red = cyborg.get_action_space(agent_name_red)
    observation_blue = cyborg.get_observation(agent_name_blue)
    action_space_blue = cyborg.get_action_space(agent_name_blue)

    agent_red = KeyboardAgent(agent_name_red)
    agent_blue = KeyboardAgent(agent_name_blue)

    reward = 0
    done = False

    while True:
        env = cyborg.environment_controller
        action_red = agent_red.get_action(observation_red, action_space_red)
        action_blue = agent_blue.get_action(observation_blue, action_space_blue)
        results = cyborg.parallel_step(actions={agent_name_blue:action_blue,
                                                agent_name_red:action_red,})
        
        if args.debug_mode:
            print_subnet_host_agents_info(env)

        observation_blue = results[0][agent_name_blue]
        observation_red = results[0][agent_name_red]

        reward += results[1][agent_name_red]['action_cost']
        #action_space = results.action_space
        if done:
            print(f"Game Over. Total reward: {reward}")
            break
if __name__ == "__main__":
    print("Setup")
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug_mode', type=bool, default=False)
    args = parser.parse_args()
    main(args)

