
from CybORG.Shared.RewardCalculator import RewardCalculator
from CybORG.Simulator.State import State
from CybORG.Simulator.Actions.GreenActions import GreenAccessService, GreenLocalWork
from CybORG.Simulator.Actions.AbstractActions.Impact import Impact
from CybORG.Simulator.Actions.Action import InvalidAction

class BlueRewardMachine(RewardCalculator):
    """The reward calculator for CC4
    
    Attributes
    ----------
    phase_rewards : Dict[str, Dict[str, int]]
        the reward mapping for the current mission phase
    """

    def get_phase_rewards(self, cur_mission_phase):
        """Gets the pre-set reward mapping for the current mission phase

        Rewards Key:
        - LWF = Local Work Fails
        - ASF = Access Service Fails
        - RIA = Red Impact/Access
        
        Parameters
        ----------
        cur_mission_phase : int
            the current mission phase of the episode

        Returns
        -------
        : Dict[str, Dict[str, int]]
            the phase reward mapping for the current mission phase
        """
        phase_rewards = {
            0:{
                "public_access_zone_subnet":    {"LWF": -1, "ASF": -1, "RIA": -3}, # Part of HQ Network in ReadMe
                "admin_network_subnet":         {"LWF": -1, "ASF": -1, "RIA": -3}, # Part of HQ Network in ReadMe
                "office_network_subnet":        {"LWF": -1, "ASF": -1, "RIA": -3}, # Part of HQ Network in ReadMe
                "contractor_network_subnet":    {"LWF":  0, "ASF": -5, "RIA": -5},
                "restricted_zone_a_subnet":     {"LWF": -1, "ASF": -3, "RIA": -1},
                "operational_zone_a_subnet":    {"LWF": -1, "ASF": -1, "RIA": -1},
                "restricted_zone_b_subnet":     {"LWF": -1, "ASF": -3, "RIA": -1},
                "operational_zone_b_subnet":    {"LWF": -1, "ASF": -1, "RIA": -1},
                "internet_subnet":              {"LWF":  0, "ASF":  0, "RIA": -1}}, 
            1:{
                "public_access_zone_subnet":    {"LWF": -1, "ASF": -1, "RIA": -3},
                "admin_network_subnet":         {"LWF": -1, "ASF": -1, "RIA": -3},
                "office_network_subnet":        {"LWF": -1, "ASF": -1, "RIA": -3},
                "contractor_network_subnet":    {"LWF":  0, "ASF":  0, "RIA":  0},
                "restricted_zone_a_subnet":     {"LWF": -2, "ASF": -1, "RIA": -3},
                "operational_zone_a_subnet":    {"LWF":-10, "ASF":  0, "RIA":-10},
                "restricted_zone_b_subnet":     {"LWF": -1, "ASF": -1, "RIA": -1},
                "operational_zone_b_subnet":    {"LWF": -1, "ASF": -1, "RIA": -1},
                "internet_subnet":              {"LWF":  0, "ASF":  0, "RIA": 0}}, 
            2:{
                "public_access_zone_subnet":    {"LWF": -1, "ASF": -1, "RIA": -3},
                "admin_network_subnet":         {"LWF": -1, "ASF": -1, "RIA": -3},
                "office_network_subnet":        {"LWF": -1, "ASF": -1, "RIA": -3},
                "contractor_network_subnet":    {"LWF":  0, "ASF":  0, "RIA":  0},
                "restricted_zone_a_subnet":     {"LWF": -1, "ASF": -3, "RIA": -3},
                "operational_zone_a_subnet":    {"LWF": -1, "ASF": -1, "RIA": -1},
                "restricted_zone_b_subnet":     {"LWF": -2, "ASF": -1, "RIA": -3},
                "operational_zone_b_subnet":    {"LWF":-10, "ASF":  0, "RIA":-10},
                "internet_subnet":              {"LWF":  0, "ASF":  0, "RIA":  0}}}
        
        return phase_rewards[cur_mission_phase]


    def calculate_reward(self, current_state: dict, action_dict: dict, agent_observations: dict, done: bool, state: State):
        """Calculate the cumulative reward based on the phase mapping.

        Parameters
        ----------
        current_state : Dict[str, _]
            the current state of all the hosts in the simulation
        action_dict : dict
        agent_observations : Dict[str, ObservationSet]
            current agent observations
        done : bool
            has the episode ended
        state: State
            current State object

        Returns
        -------
        : int
            sum of the rewards collected
        """
        reward_list = []
        self.phase_rewards = self.get_phase_rewards(state.mission_phase)

        for agent_name, action in action_dict.items():
            if not action:
                continue
            
            action = action[0]            
            if isinstance(action, Impact):
                hostname = action.hostname
            elif isinstance(action, GreenAccessService) or isinstance(action, GreenLocalWork):
                hostname = state.ip_addresses[action.ip_address]
            else:
                continue

            subnet_name = state.hostname_subnet_map[hostname].value
            sessions = state.sessions[agent_name].values()

            if len([session.ident for session in sessions if session.active]) > 0:
                success = agent_observations[agent_name].observations[0].data['success']
                rewards_for_zone = self.phase_rewards[subnet_name]

                if 'green' in agent_name and success == False:
                    if isinstance(action, GreenLocalWork):
                        reward_list.append(rewards_for_zone["LWF"])
                    elif isinstance(action, GreenAccessService):
                        reward_list.append(rewards_for_zone["ASF"])

                elif 'red' in agent_name and success and isinstance(action, Impact):
                    reward_list.append(rewards_for_zone["RIA"])

        return sum(reward_list)


  
        
        
 
     
        
    