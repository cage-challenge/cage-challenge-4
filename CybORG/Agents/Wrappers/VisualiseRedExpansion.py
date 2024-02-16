import networkx as nx
from networkx import connected_components
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import time
import numpy as np
from copy import deepcopy

from CybORG import CybORG
from CybORG.Simulator.Scenarios.EnterpriseScenarioGenerator import SUBNET
from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
from CybORG.Agents.SimpleAgents.ConstantAgent import SleepAgent
from CybORG.Agents.SimpleAgents.FiniteStateRedAgent import FiniteStateRedAgent
from CybORG.Agents import SleepAgent, EnterpriseGreenAgent


class VisualiseRedExpansion():
    """Visualisation wrapper that displays the user and root shells acquired by red agents over time, in a series of network graph plots. 
    
    Attributes
    ----------
    fig : matplotlib.pyplot.figure.Figure
        graph figure
    ax : matplotlib.pyplot.axes.Axes
        graph axes
    slider : matplotlib.widgets.Slider
        slider to control graph in GUI
    collected_networks : networkx.Graph
        graph of the network
    play_view_flag : bool
        flag for if the graph display is iterating through steps
    env : SimulationController
        CybORG environment used
    total_steps : int
        total number of steps to iterate over
    node_label_mapping : Dict[str, str]
        dictionary mapping host names to the abbreviated labels shown of the graph
    host_nodes : Dict[str, str]
        grouping of host types to hosts
    host_interfaces : list
        list of interfaces as edges between two hosts
    pos : Dict[str, float]
        position of nodes on graph
    """
    def __init__(self, cyborg, steps):
        self.fig = None
        self.ax = None
        self.slider = None
        self.collected_networks = []
        self.play_view_flag = False
        
        self.env = cyborg.environment_controller
        self.total_steps = steps

        # Fixed graph nodelists (of host) 
        env_netmap = self.env.state.link_diagram.copy()
        self.node_label_mapping = self._get_node_label_mapping(env_netmap)
        self.host_nodes = self._get_host_nodes(env_netmap)
        self.host_interfaces = list(env_netmap.edges()).copy()

        # Create initial network nodelists
        initial_network_info = self._set_initial_agents_and_sessions()

        # Add the new edges and nodes to the graph
        env_netmap.add_nodes_from(initial_network_info['active_agents']['blue'])
        env_netmap.add_edges_from(initial_network_info['host_sessions'])

        self.pos = self._set_network_host_and_agents_positions(env_netmap)
        env_netmap.add_nodes_from(initial_network_info['active_agents']['red'])

        initial_network_info['network_map'] = env_netmap
        self.collected_networks.append(initial_network_info)

    def run(self):
        """Automating the running of the visualisation, with visualising each step then outputting the graph."""
        for step in range(self.total_steps):
            self.env.step()
            self.visualise_step()
        self.show_graph()
    
    def visualise_step(self):
        """Collecting all the information at each step and adding it to a dictionary, to be used later for the visualisation. """
        
        host_nodes_compromised, red_agents = self._get_compromised_nodes()
        all_session_agents, all_host_sessions, agent_label_mapping, red_root_nodes = self._get_compromised_edges()
        
        known_red_agents = self.collected_networks[-1]['active_agents']['red']
        if len(all_session_agents['red'])>len(known_red_agents):
            new_network = self.collected_networks[-1]['network_map'].copy()
            for new_red in all_session_agents['red']:
                if new_red not in known_red_agents:
                    new_network.add_node(new_red)


            new_network_info = {
                'network_map' : new_network,
                'active_agents' : all_session_agents,
                'agent_label_mapping' : agent_label_mapping,
                'host_sessions' : all_host_sessions,
                'compromised_hosts' : host_nodes_compromised,
                'red_root_nodes' : red_root_nodes
            }
        else:
            new_network_info = {
                'network_map' : self.collected_networks[-1]['network_map'],
                'active_agents' : all_session_agents,
                'agent_label_mapping' : agent_label_mapping,
                'host_sessions' : all_host_sessions,
                'compromised_hosts' : host_nodes_compromised,
                'red_root_nodes' : red_root_nodes
            }

        self.collected_networks.append(new_network_info)
        
    def show_graph(self):
        """Render for the visualisation graph plot."""
        self.fig, self.ax = plt.subplots(num="CC4 Visualisation")
        self.ax.format_coord = lambda x, y: ""
        self._draw_network(0, init=True)
        plt.subplots_adjust(bottom=0.25)

        axcolor = 'lightgoldenrodyellow'

        ax_pos_slider = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)
        ax_pos_btn_back = plt.axes([0.125, 0.15, 0.02, 0.03], facecolor='w')
        ax_pos_btn_play = plt.axes([0.15, 0.15, 0.02, 0.03], facecolor='w')
        ax_pos_btn_pause = plt.axes([0.175, 0.15, 0.02, 0.03], facecolor='w')
        ax_pos_btn_forward = plt.axes([0.20, 0.15, 0.02, 0.03], facecolor='w')

        btn_forward = Button(ax_pos_btn_forward, '>', color='w', hovercolor='b')
        btn_back = Button(ax_pos_btn_back, '<', color='w', hovercolor='b')
        btn_play = Button(ax_pos_btn_play, 'P', color='w', hovercolor='b')
        btn_pause = Button(ax_pos_btn_pause, '||', color='w', hovercolor='b')


        self.slider = Slider(
            ax=ax_pos_slider,
            label="",
            # label='Step Progression',
            valmin=0,
            valmax=self.total_steps,
            valinit=0,
            valstep=1
        )
        self.slider.on_changed(self._draw_network)
        btn_forward.on_clicked(self._btn_forward)
        btn_back.on_clicked(self._btn_back)
        btn_play.on_clicked(self._btn_play)
        btn_pause.on_clicked(self._btn_pause)
        
        plt.show()

    def _btn_forward(self, ev):
        pos = self.slider.val
        if pos < self.total_steps:
            self.slider.set_val(pos+1)

    def _btn_back(self, ev):
        pos = self.slider.val
        if pos > 0:
            self.slider.set_val(pos-1)
    
    def _btn_play(self, ev):
        self.play_view_flag = True

        while self.play_view_flag:
            pos = self.slider.val
            if pos < self.total_steps:
                self.slider.set_val(pos+1)
            else:
                self.play_view_flag = False
            plt.pause(0.3)

    def _btn_pause(self, ev):
        self.play_view_flag = False

    def _draw_network(self, idx, init:bool = False):

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.clear()

        nx.draw_networkx_nodes(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, nodelist=self.host_nodes['users'], node_size=200, node_color='#C0C0C0', alpha=0.9, node_shape='o')
        nx.draw_networkx_nodes(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, nodelist=self.host_nodes['servers'], node_size=200, node_color='#C0C0C0', alpha=0.9, node_shape='s')
        nx.draw_networkx_nodes(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, nodelist=self.host_nodes['other'], node_size=400, node_color='#C0C0C0', alpha=0.9, node_shape='H')
        nx.draw_networkx_nodes(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, nodelist=self.collected_networks[idx]['active_agents']['red'], node_size=200, node_color='#EE4B2B', node_shape='^')
        nx.draw_networkx_nodes(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, nodelist=self.collected_networks[idx]['active_agents']['blue'], node_size=200, node_color='#0096FF', node_shape='^')
        nx.draw_networkx_edges(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, edgelist=self.host_interfaces)
        nx.draw_networkx_edges(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, edgelist=self.collected_networks[idx]['host_sessions'], style=':')
        nx.draw_networkx_labels(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, labels=self.node_label_mapping, font_size=10)
        nx.draw_networkx_labels(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, labels=self.collected_networks[idx]['agent_label_mapping'], font_size=10)
        nx.draw_networkx_nodes(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, nodelist=self.collected_networks[idx]['compromised_hosts'], node_size=200, node_color='#FFA500', alpha=0.8)
        nx.draw_networkx_nodes(self.collected_networks[idx]['network_map'], self.pos, ax=self.ax, nodelist=self.collected_networks[idx]['red_root_nodes'], node_size=200, node_color='#EE4B2B', alpha=0.8)

        self.ax.legend([
            'user host', 'server host', 'router', 
            'red agent', 'blue agent', 
            'host link', 'session link', 
            'user compromised host', 'root compromised host'
        ])

        if not init:
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
        self.fig.canvas.draw_idle()
        pass

    # get the compromised nodes for colour coding
    def _get_compromised_nodes(self):
        host_nodes_compromised=[]
        agents_active=[]
        for red_agent_name in self.env.team['Red']:
            for sess in self.env.state.sessions[red_agent_name].values():
                host_nodes_compromised.append(sess.hostname)
                agents_active.append(red_agent_name)
        return list(set(host_nodes_compromised)), list(set(agents_active))

    def _get_compromised_edges(self):
        last_collected_network = self.collected_networks[-1]

        all_session_agents = deepcopy(last_collected_network['active_agents'])
        all_host_sessions = deepcopy(last_collected_network['host_sessions'])
        agent_label_mapping = deepcopy(last_collected_network['agent_label_mapping'])

        agent_root_nodes = self._get_agent_root_nodes()
        red_root_nodes = []

        # For each host in the state, add their agent sessions to the new edges list and the agents to the new nodes list (grouped by agent type)
        for hostname, host in self.env.state.hosts.items():
            for agent, sids in host.sessions.items():
                if not sids == []:
                    if "red" in agent:
                        if agent not in all_session_agents['red']: 
                            all_host_sessions.append((hostname, agent))
                            all_session_agents["red"].append(agent)
                            agent_label_mapping[agent] = "R" + agent.split("_")[-1]
                        for sid in sids:
                            if sid in agent_root_nodes[agent]:
                                red_root_nodes.append(hostname)
                            # agent_label_mapping[hostname] = str(sid)
        #all_session_agents["red"] = list(set(all_session_agents["red"]))
        return all_session_agents, all_host_sessions, agent_label_mapping, red_root_nodes

    def _get_agent_root_nodes(self):
        agent_root_nodes = {}

        for agent, sessions in self.env.state.sessions.items():
            if 'red' in agent:
                agent_root_nodes[agent] = []
                for i, sess in sessions.items():
                    if sess.username == "root":
                        agent_root_nodes[agent].append(i)
        
        return agent_root_nodes

    def _get_node_label_mapping(self, env_netmap):
        # Node label mapping
        node_label_mapping = {}
        for node in env_netmap._node.keys():
            if not "user_host" in node and not "server_host" in node:
                new_node_label = ""
                
                # Zone name
                if "restricted_zone" in node:
                    new_node_label = "RZ"
                elif "operational_zone" in node:
                    new_node_label = "OZ"
                elif "contractor_network" in node:
                    new_node_label = "CN"
                elif "public_access_zone" in node:
                    new_node_label = "PAZ"
                elif "admin_network" in node:
                    new_node_label = "AN"
                elif "office_network" in node:
                    new_node_label = "ON"
                else:
                    new_node_label = "Internet Root"
                    node_label_mapping[node] = new_node_label
                    continue

                # Partition
                if "_a_" in node:
                    new_node_label = new_node_label + "A"
                elif "_b_" in node:
                    new_node_label = new_node_label + "B"

                node_label_mapping[node] = new_node_label

        return node_label_mapping

    def _get_host_nodes(self, env_netmap):
        host_nodes = {}

        all_host_nodes = list(env_netmap.nodes()).copy()
        host_nodes['servers'] = [host for host in all_host_nodes if 'server' in host]
        host_nodes['users'] = [host for host in all_host_nodes if 'user' in host]
        host_nodes['other'] = [host for host in all_host_nodes if 'user' not in host and 'server' not in host]

        return host_nodes

    def _set_initial_agents_and_sessions(self):
        all_session_agents = {"blue": [], "red": []}
        agent_label_mapping = {}
        all_host_sessions = []
        compromised_hosts = []

        agent_root_nodes = self._get_agent_root_nodes()
        red_root_nodes = []

        # For each host in the state, add their agent sessions to the new edges list and the agents to the new nodes list (grouped by agent type)
        for hostname, host in self.env.state.hosts.items():
            for agent, sids in host.sessions.items():
                if not sids == []:
                    if "blue" in agent:
                        all_session_agents["blue"].append(agent)
                        agent_label_mapping[agent] = "B" + agent.split("_")[-1]
                        all_host_sessions.append((hostname, agent))
                    elif "red" in agent:
                        all_session_agents["red"].append(agent)
                        agent_label_mapping[agent] = "R" + agent.split("_")[-1]
                        all_host_sessions.append((hostname, agent))
                        compromised_hosts.append(hostname)

                        for sid in sids:
                            if sid in agent_root_nodes[agent]:
                                red_root_nodes.append(hostname)

        # Duplicates are removed from lists
        all_session_agents["blue"] = list(set(all_session_agents["blue"]))
        all_session_agents["red"] = list(set(all_session_agents["red"]))

        info = {
            'active_agents' : all_session_agents,
            'agent_label_mapping' : agent_label_mapping,
            'host_sessions' : all_host_sessions,
            'compromised_hosts' : compromised_hosts,
            'red_root_nodes' : red_root_nodes
        }
        return info

    def _set_network_host_and_agents_positions(self, env_netmap):
        all_red_agents = ['red_agent_0', 'red_agent_1', 'red_agent_2', 'red_agent_3', 'red_agent_4', 'red_agent_5', ]

        red_agent_allowed_subnets = [
            [SUBNET.CONTRACTOR_NETWORK.value],
            [SUBNET.RESTRICTED_ZONE_A.value],
            [SUBNET.OPERATIONAL_ZONE_A.value],
            [SUBNET.RESTRICTED_ZONE_B.value],
            [SUBNET.OPERATIONAL_ZONE_B.value],
            [SUBNET.PUBLIC_ACCESS_ZONE.value, SUBNET.ADMIN_NETWORK.value, SUBNET.OFFICE_NETWORK.value]
        ]

        positions = nx.spring_layout(env_netmap, seed=2, iterations=300)

        # get the position of hosts in each subnet - used for new red agent positions
        subnet_host_positions = {}
        for subnet in self.env.state.subnets.values():
            subnet_name = subnet.name
            subnet_host_positions[subnet_name] = []
            for host_name in self.env.state.hosts.keys():
                if subnet_name in host_name:
                    subnet_host_positions[subnet_name].append(list(positions[host_name]))
                    
        for r in range(6):
            red_agent_name = 'red_agent_' + str(r)

            if len(red_agent_allowed_subnets[r]) == 1:
                positions[red_agent_name] = np.array(subnet_host_positions[red_agent_allowed_subnets[r][0]]).mean(axis=0)*1.15

            else:
                combined_subnet_hosts = []
                for s in red_agent_allowed_subnets[r]:
                    combined_subnet_hosts.extend(subnet_host_positions[s])
                positions[red_agent_name] = np.array(combined_subnet_hosts).mean(axis=0)*1.15

        return positions
        