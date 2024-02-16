
import random
from typing import List
from CybORG.Agents.SimpleAgents.EnterpriseGreenAgent import EnterpriseGreenAgent
from CybORG.Shared.Session import Session
from CybORG.Simulator.Actions.ConcreteActions.StopProcess import StopProcess
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import EnterpriseScenarioGenerator
from CybORG.env import CybORG


def test_stop_process():
    sg = EnterpriseScenarioGenerator(green_agent_class=EnterpriseGreenAgent)
    cyborg = CybORG(scenario_generator=sg)
    cyborg.reset()
    sim_controller = cyborg.environment_controller

    # get green agent
    valid_sessions: List[Session] = []
    for agent, sessions in sim_controller.state.sessions.items():
        if "green" in agent:
            for session in sessions.values():
                valid_sessions.append(session)
    assert valid_sessions, "Could not find valid agent"
    session = random.choice(valid_sessions)
    agent_interface = sim_controller.agent_interfaces[session.agent]
    host = sim_controller.state.hosts[session.hostname]
    pid = random.choice(list(host.services.values())).process
    session.pid = pid # This is necessary for the sake of the test
    
    # Create action and execute
    action = StopProcess(
        session=0,
        agent=agent_interface.agent_name,
        target_session=session.ident,
        pid=pid,
        stop_all=True
    )
    action.execute(cyborg.environment_controller.state)