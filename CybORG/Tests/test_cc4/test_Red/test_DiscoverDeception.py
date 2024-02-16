import pytest

from CybORG import CybORG
from CybORG.Shared.Enums import ProcessName
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Simulator.Actions.AbstractActions.DiscoverDeception import DiscoverDeception
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions import DecoyHarakaSMPT, DecoyApache, DecoyTomcat, DecoyVsftpd
from CybORG.Simulator.Actions.ConcreteActions.DecoyActions import DecoySmss, DecoyFemitter, DecoySSHD, DecoySvchost

RED_AGENT='red_agent_0'
SESSION_ID=0

# @pytest.mark.skip
# def test_real_agent():
#     """
#     TBC when non sleep based agents are completed
#         given they can have Withdraw in their action_space
#         and wont require forcing the skip_valid_action_flag==True
#     """
#     pass

@pytest.mark.parametrize('decoy_fp_rate',[0,1])
def test_DiscoverDeception_on_DecoyApache(decoy_fp_rate):
    """
    Test we can discover an Apache2 decoy
    """
    esg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent,
                                        red_agent_class=SleepAgent)
    cyborg = CybORG(scenario_generator=esg, seed=0)
    env = cyborg.environment_controller
    env.reset()
    red_agent_str='red_agent_0'
    
    # get the hostname for the blue_agent session
    hostname = env.state.sessions[RED_AGENT][SESSION_ID].hostname
    
    # this action is only successful if the service doesnt already exist on the host
    while ProcessName.APACHE2 in env.state.hosts[hostname].services.keys():
        env.reset()
        hostname = env.state.sessions[RED_AGENT][SESSION_ID].hostname

    action = DecoyApache(agent=red_agent_str, session=SESSION_ID, hostname=hostname)
    obs = action.execute(env.state)
    assert obs.data['success']==True
    # confirm the decoy has been added to the host
    decoy_list = [pro.name for pro in env.state.hosts[hostname].processes if pro.decoy_type.name=='EXPLOIT']
    assert len(decoy_list)>0
    assert decoy_list[0]=='apache2'

    # identify the target host and detect the decoy with a 100% success rate (detection_rate)
    target_ip = env.hostname_ip_map[hostname]
    action = DiscoverDeception(agent=RED_AGENT, session=SESSION_ID, ip_address=target_ip)
    action.detection_rate = 1.0
    action.fp_rate = decoy_fp_rate

    obs = action.execute(env.state)
    # ensure the action was a success and that the rfi properties exist from the decoy
    assert obs.data['success']==True
    apache_process = [process for process in obs.data[hostname]['Processes'] if process['service_name']=='apache2']
    assert "decoy" in apache_process[0]['Properties']
    # check for false negatives from the detected decoys - all detected with detection_rate 100%, but non contain the 'decoy' property
    non_decoys = [process for process in obs.data[hostname]['Processes'] if process['service_name']!='apache2']
    if decoy_fp_rate==0:
        assert len(non_decoys)==0
    elif decoy_fp_rate==1:
        assert len(non_decoys)>0


@pytest.mark.parametrize('decoy_fp_rate',[0,1])
def test_DiscoverDeception_on_HarakaSMPT(decoy_fp_rate):
    """
    Test we can discover an HarakaSMPT decoy
    """
    esg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent,
                                        red_agent_class=SleepAgent)
    cyborg = CybORG(scenario_generator=esg, seed=0)
    env = cyborg.environment_controller
    env.reset()
    
    blue_agent_str='blue_agent_0'
    
    # get the hostname for the blue_agent session
    hostname = env.state.sessions[blue_agent_str][SESSION_ID].hostname
    
    # this action is only successful if the service doesnt already exist on the host
    while ProcessName.SMTP in env.state.hosts[hostname].services.keys():
        env.reset()
        hostname = env.state.sessions[blue_agent_str][SESSION_ID].hostname
    
    action = DecoyHarakaSMPT(agent=blue_agent_str, session=SESSION_ID, hostname=hostname)
    obs = action.execute(env.state)
    assert obs.data['success']==True
    # confirm the decoy has been added to the host
    decoy_list = [pro.name for pro in env.state.hosts[hostname].processes if pro.decoy_type.name=='EXPLOIT']
    assert len(decoy_list)>0
    assert decoy_list[0]=='haraka'

    # identify the target host and detect the decoy with a 100% success rate (detection_rate)
    target_ip = env.hostname_ip_map[hostname]
    action = DiscoverDeception(agent=RED_AGENT, session=SESSION_ID, ip_address=target_ip)
    action.detection_rate = 1.0
    action.fp_rate = decoy_fp_rate

    obs = action.execute(env.state)
    
    # ensure the action was a success
    assert obs.data['success']==True
    haraka_process = [process for process in obs.data[hostname]['Processes'] if process['service_name']=='haraka']
    assert "decoy" in haraka_process[0]['Properties']
    # check for false negatives from the detected decoys - all detected with detection_rate 100%, but non contain the 'decoy' property
    non_decoys = [process for process in obs.data[hostname]['Processes'] if process['service_name']!='haraka']
    non_decoy_list = ["decoy"  in process['Properties'] for process in non_decoys]
    if decoy_fp_rate==0:
        assert len(non_decoy_list)==0
    elif decoy_fp_rate==1:
        assert len(non_decoy_list)>0


@pytest.mark.parametrize('decoy_fp_rate',[0,1])
def test_DiscoverDeception_on_DecoyTomcat(decoy_fp_rate):
    """
    Test we can discover an Tomcat decoy
    """
    esg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent,
                                        red_agent_class=SleepAgent)
    cyborg = CybORG(scenario_generator=esg, seed=0)
    env = cyborg.environment_controller
    env.reset()
    blue_agent_str='blue_agent_0'

    # get the hostname for the blue_agent session
    hostname = env.state.sessions[blue_agent_str][SESSION_ID].hostname
    
    # this action is only successful if the service doesnt already exist on the host \
    # which is true for the current seed set in the environment (1)
    action = DecoyTomcat(agent=blue_agent_str, session=SESSION_ID, hostname=hostname)
    obs = action.execute(env.state)
    assert obs.data['success']==True
    # confirm the decoy has been added to the host
    decoy_list = [pro.name for pro in env.state.hosts[hostname].processes if pro.decoy_type.name=='EXPLOIT']
    assert len(decoy_list)>0
    assert decoy_list[0]=='Tomcat.exe'

    # identify the target host and detect the decoy with a 100% success rate (detection_rate)
    target_ip = env.hostname_ip_map[hostname]
    action = DiscoverDeception(agent=RED_AGENT, session=SESSION_ID, ip_address=target_ip)
    action.detection_rate = 1.0
    action.fp_rate = decoy_fp_rate

    obs = action.execute(env.state)
    
    # ensure the action was a success
    assert obs.data['success']==True
    tomcat_process = [process for process in obs.data[hostname]['Processes'] if process['service_name']=='Tomcat.exe']
    assert "decoy" in tomcat_process[0]['Properties']
    # check for false negatives from the detected decoys - all detected with detection_rate 100%, but non contain the 'decoy' property
    non_decoys = [process for process in obs.data[hostname]['Processes'] if process['service_name']!='Tomcat.exe']
    non_decoy_list = ["decoy" in process['Properties'] for process in non_decoys]
    if decoy_fp_rate==0:
        assert len(non_decoy_list)==0
    elif decoy_fp_rate==1:
        assert len(non_decoy_list)>0


@pytest.mark.parametrize('decoy_fp_rate',[0,1])
def test_DiscoverDeception_on_DecoyVsftpd(decoy_fp_rate):
    """
    Test we can discover an Vsftpd decoy
    """
    esg = EnterpriseScenarioGenerator(blue_agent_class=SleepAgent, green_agent_class=SleepAgent,
                                        red_agent_class=SleepAgent)
    cyborg = CybORG(scenario_generator=esg, seed=0)
    env = cyborg.environment_controller
    env.reset()
    blue_agent_str='blue_agent_0'

    # get the hostname for the blue_agent session
    hostname = env.state.sessions[blue_agent_str][SESSION_ID].hostname
    
    # this action is only successful if the service doesnt already exist on the host \
    # which is true for the current seed set in the environment (1)
    action = DecoyVsftpd(agent=blue_agent_str, session=SESSION_ID, hostname=hostname)
    obs = action.execute(env.state)
    assert obs.data['success']==True
    # confirm the decoy has been added to the host
    decoy_list = [pro.name for pro in env.state.hosts[hostname].processes if pro.decoy_type.name=='EXPLOIT']
    assert len(decoy_list)>0
    assert decoy_list[0]=='vsftpd'
    print(decoy_list)
    # identify the target host and detect the decoy with a 100% success rate (detection_rate)
    target_ip = env.hostname_ip_map[hostname]
    action = DiscoverDeception(agent=RED_AGENT, session=SESSION_ID, ip_address=target_ip)
    action.detection_rate = 1.0
    action.fp_rate = decoy_fp_rate

    obs = action.execute(env.state)
    # ensure the action was a success
    assert obs.data['success']==True
    vsftpd_process = [process for process in obs.data[hostname]['Processes'] if process['service_name']=='vsftpd']
    assert "decoy" in vsftpd_process[0]['Properties']
    # check for false negatives from the detected decoys - all detected with detection_rate 100%, but non contain the 'decoy' property
    non_decoys = [process for process in obs.data[hostname]['Processes'] if process['service_name']!='vsftpd']
    non_decoy_list = ["decoy" in process['Properties'] for process in non_decoys]
    if decoy_fp_rate==0:
        assert len(non_decoy_list)==0
    elif decoy_fp_rate==1:
        assert len(non_decoy_list)>0
