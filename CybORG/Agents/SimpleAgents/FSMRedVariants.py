from CybORG.Agents.SimpleAgents.FiniteStateRedAgent import FiniteStateRedAgent

""" *Creating Variant Red Agents*

```python

class MyVariant(FiniteStateRedAgent):
    def __init__(self, name=None, np_random=None, agent_subnets=None):
        super().__init__(name=name, np_random=np_random, agent_subnets=agent_subnets)

        # Changable variables:
        self.print_action_output = False
        self.print_obs_output = False
        self.prioritise_servers = False

    def _set_host_state_priority_list(self):
        # percentage choice
        new_host_state_priority_list = {'K':(0->100), 'KS':?, 'KD':?, 'U':?, 'UD':?, 'R':?, 'RD':?}
        return None
    
    def _state_transitions_probability(self):
        # Create new probability mapping to use
        map = {
            'K'  : [0.5,  0.25, 0.25, None, None, None, None, None, None],
            'KD' : [None, 0.5,  0.5,  None, None, None, None, None, None],
            'S'  : [0.25, None, None, 0.25, 0.5 , None, None, None, None],
            'SD' : [None, None, None, 0.25, 0.75, None, None, None, None],
            'U'  : [0.5 , None, None, None, None, 0.5 , None, None, 0.0 ],
            'UD' : [None, None, None, None, None, 1.0 , None, None, 0.0 ],
            'R'  : [0.5,  None, None, None, None, None, 0.25, 0.25, 0.0 ],
            'RD' : [None, None, None, None, None, None, 0.5,  0.5,  0.0 ],
        }
        return map
```
"""

class VerboseFSRed(FiniteStateRedAgent):
    """A variant of the FiniteStateRedAgent that outputs success, action and internal observation knowlege to the terminal.
    
    Example:
    ```
    ** Turn 0 for red_agent_0 **
    Action: Initial Observation
    Action Success: UNKNOWN

    Observation:
    {'contractor_network_subnet_user_host_5': {
        'Interface': [{'Subnet': IPv4Network('10.0.171.0/24'),
                        'interface_name': 'eth0',
                        'ip_address': IPv4Address('10.0.171.186')}],
        'Processes': [{'PID': 8888,
                        'username': 'ubuntu'}],
        'Sessions': [{'PID': 8888,
                        'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                        'agent': 'red_agent_0',
                        'session_id': 0,
                        'timeout': 0,
                        'username': 'ubuntu'}],
        'System info': {'Architecture': <Architecture.x64: 2>,
                        'Hostname': 'contractor_network_subnet_user_host_5',
                        'OSDistribution': <OperatingSystemDistribution.UBUNTU: 8>,
                        'OSType': <OperatingSystemType.LINUX: 3>,
                        'OSVersion': <OperatingSystemVersion.UNKNOWN: 1>,
                        'position': array([0., 0.])},
        'User Info': [{'Groups': [{'GID': 0}],
                        'username': 'root'},
                        {'Groups': [{'GID': 1}],
                        'username': 'user'}]}}
    Host States:
    {'10.0.171.186': {'hostname': 'contractor_network_subnet_user_host_5',
                    'state': 'U'}}
    ```
    """
    def __init__(self, name=None, np_random=None, agent_subnets=None):
        super().__init__(name=name, np_random=np_random, agent_subnets=agent_subnets)
        self.print_action_output = True
        self.print_obs_output = True


class DiscoveryFSRed(FiniteStateRedAgent):
    """An FiniteStateRedAgent variant that aims to prioritise discovery."""
    def __init__(self, name=None, np_random=None, agent_subnets=None):
        super().__init__(name=name, np_random=np_random, agent_subnets=agent_subnets)
        self.print_action_output = False
        self.print_obs_output = False
        self.prioritise_servers = True

    def set_host_state_priority_list(self):
        """Returns a custom host priority list, optimised for discovery.
        
        Returns
        -------
        host_state_priority_list : Dict[str, num]
        """
        host_state_priority_list = {
            'K':20, 'KD':20, 
            'S':20, 'SD':20,
            'U':10, 'UD':10, 
            'R':0,  'RD':0
        }
        return host_state_priority_list
    
    def state_transitions_probability(self):
        """Returns a custom state transitions probability matrix, optimised for discovery.

        Returns
        -------
        matrix : Dict[str, List[float]]
        """

        map = {
            'K'  : [0.25, 0.75, 0.0,  None, None, None, None, None, None],
            'KD' : [None, 1.0,  0.0,  None, None, None, None, None, None],
            'S'  : [0.25, None, None, 0.0,  0.75, None, None, None, None],
            'SD' : [None, None, None, 0.0,  1.0,  None, None, None, None],
            'U'  : [0.0 , None, None, None, None, 1.0 , None, None, 0.0 ],
            'UD' : [None, None, None, None, None, 1.0 , None, None, 0.0 ],
            'R'  : [1.0,  None, None, None, None, None, 0.0,  0.0,  0.0 ],
            'RD' : [None, None, None, None, None, None, 0.5,  0.5,  0.0 ],
        }

        return map
