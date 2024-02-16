# Privilege Escalate

`PrivilegeEscalate` carries out an exploit on a specific host that Red has a user shell on, to gain a shell with root privileges.

Here, we will be privilege escalating the first host that Red knows.

## Identify Host with User Shell

In order to run privilege escalation, we must find the target host's name. We do this by looking at Red's initial observation.

```python title="red_privilege_escalate.py" linenums="1"
from pprint import pprint
from ipaddress import IPv4Network, IPv4Address

from CybORG import CybORG
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents import SleepAgent, FiniteStateRedAgent, EnterpriseGreenAgent
from CybORG.Simulator.Actions import PrivilegeEscalate

sg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, 
                                green_agent_class=EnterpriseGreenAgent, 
                                red_agent_class=FiniteStateRedAgent,
                                steps=200)
cyborg = CybORG(scenario_generator=sg, seed=1000)
red_agent_name = 'red_agent_0'

reset = cyborg.reset(agent=red_agent_name)
initial_obs = reset.observation
pprint(initial_obs)
```
??? quote "Code Output"
    ```
    {'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                            'interface_name': 'eth0',
                                                            'ip_address': IPv4Address('10.0.96.73')}],
                                            'Processes': [{'PID': 5753,
                                                            'username': 'ubuntu'}],
                                            'Sessions': [{'PID': 5753,
                                                            'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'timeout': 0,
                                                            'username': 'ubuntu'}],
                                            'System info': {'Architecture': <Architecture.x64: 2>,
                                                            'Hostname': 'contractor_network_subnet_user_host_4',
                                                            'OSDistribution': <OperatingSystemDistribution.KALI: 9>,
                                                            'OSType': <OperatingSystemType.LINUX: 3>,
                                                            'OSVersion': <OperatingSystemVersion.K2019_4: 11>,
                                                            'position': array([0., 0.])},
                                            'User Info': [{'Groups': [{'GID': 0}],
                                                            'username': 'root'},
                                                            {'Groups': [{'GID': 1}],
                                                            'username': 'user'}]},
    'success': <TernaryEnum.UNKNOWN: 2>}
    ```

The only host Red is currently aware of has a hostname visible in the key `contractor_network_subnet_user_host_4`. 

We already have a user shell on `contractor_network_subnet_user_host_4` - this is shown in Red's initial observations above:
```
'Sessions': [{'PID': 5753,
    'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
    'agent': 'red_agent_0',
    'session_id': 0,
    'timeout': 0,
    'username': 'ubuntu'}],
```
As such, we can immediately execute `PrivilegeEscalate` on `contractor_network_subnet_user_host_4`.

If we did not have a user shell on the host that we want to perform a privilege escalate on, we would need to do that first.

## Privilege Escalate

```python title="red_privilege_escalate.py" linenums="19"
action = PrivilegeEscalate(hostname='contractor_network_subnet_user_host_4', session=0, agent=red_agent_name)
results = cyborg.step(agent=red_agent_name, action=action)
obs = results.observation
pprint(obs)
```
???+ quote "Code Output"
    ```
    {'action': PrivilegeEscalate contractor_network_subnet_user_host_4,
    'contractor_network_subnet_user_host_4': {'Interface': [{'Subnet': IPv4Network('10.0.96.0/24'),
                                                            'ip_address': IPv4Address('10.0.96.73')}],
                                            'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
                                                            'agent': 'red_agent_0',
                                                            'session_id': 0,
                                                            'username': 'root'}],
                                            'System info': {'Hostname': 'contractor_network_subnet_user_host_4'}},
    'success': <TernaryEnum.TRUE: 1>}
    ```

Comparing the resulting observation to Red's initial observation, the `username` in Red's session on `contractor_network_subnet_user_host_4` has changed to `root`, demonstrating the success of the privilege escalation:
```
'Sessions': [{'Type': <SessionType.RED_ABSTRACT_SESSION: 10>,
    'agent': 'red_agent_0',
    'session_id': 0,
    'username': 'root'}],
```