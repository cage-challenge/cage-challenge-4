from prettytable import PrettyTable
from CybORG import CybORG
from CybORG.Agents.Wrappers import BaseWrapper


class TrueStateTableWrapper:
    """A CC4 wrapper that outputs the true state of the environment, in the form of various tables.

    The tables are created using PrettyTable package to make the output more readable.
    It is recommended that the output is piped to a text file, as the length of the output can be long.
    
    Attributes
    ----------
    hostnames : List[str]
        list of hostnames in the environment
    env : CybORG
        the cyborg environment that the wrapper is being added to (parent class attribute).
    agents : dict
        dictionary of agents (parent class attribute).
    """
    def __init__(self, env: CybORG = None):
        self.env = env
        self.hostnames = list(env.environment_controller.state.hosts.keys())
        
    def get_raw_full_true_state(self):
        """Gets all the raw true state data straight from the environment.
        
        Returns
        -------
        : dict
            the raw true state data from the env
        """
        get_all_dict = {
            'Interfaces': 'All',
            'Processes': 'All',
            'Sessions': 'All',
            'Files': 'All',
            'User info': 'All',
            'System info': 'All',
            'Services': 'All'
        }
        info = {host: get_all_dict for host in self.hostnames}
        return self.env.get_true_state(info)

    def get_host_overview_table(self):
        """Creates a table of: hostnames, IP addresses, sessions, and number of processes.
        
        Returns
        -------
        table : PrettyTable
            host overview table
        """
        table = PrettyTable(["Hostname", "IP Address", "Sessions", "No. Processes"])

        get_dict = {
            'Interfaces': 'ip_address',
            'Processes': 'All',
            'Sessions': 'All'
        }
        get_dict_per_host = {host: get_dict for host in self.hostnames}
        true_state_dict = self.env.get_true_state(info=get_dict_per_host)
        true_state_dict.pop("success")

        for hostname, host_state in true_state_dict.items():
            state_keys = host_state.keys()
            ip_address = str(host_state['Interface'][0]['ip_address'])

            if 'Sessions' in state_keys:
                sessions = [sess['agent'] for sess in host_state['Sessions']]
            else:
                sessions = "-"

            if 'Processes' in state_keys:
                num_processes = str(len(host_state['Processes']))
            else:
                num_processes = "0"

            table.add_row([hostname, ip_address, sessions, num_processes])

        return table
    
    def get_host_processes_tables(self):
        """Creates a table of: hostname, process ID, process name, process type, associated username, associated session and session ID (if any); per subnet.
        
        Returns
        -------
        tables : Dict[str, PrettyTable]
            dictionary of host processes tables per subnet
        """

        # Get true state info from environment
        get_dict = {
            'Interfaces': 'All',
            'Processes': 'All',
            'Sessions': 'All'
        }
        get_dict_per_host = {host: get_dict for host in self.hostnames}
        true_state_dict = self.env.get_true_state(info=get_dict_per_host)
        true_state_dict.pop("success")

        # Define tables storage
        subnet_cidr_map = self.env.environment_controller.subnet_cidr_map
        tables = {subnet_name.name: PrettyTable(["Hostname", "PID", "Name", "Type", "Username", "Session", "SID"]) for subnet_name in subnet_cidr_map.keys()}

        # Creates table
        for hostname, host_state in true_state_dict.items():
            state_keys = host_state.keys()
            row = 0
            if 'Processes' in state_keys:
                num_procs = len(host_state['Processes'])
                for proc in host_state['Processes']:
                    pid = proc['PID']
                    row += 1
                    
                    if "process_name" in proc.keys():
                        p_name = proc["process_name"]
                    else:
                        p_name = "-"

                    if "process_type" in proc.keys():
                        p_type = proc["process_type"]
                    else:
                        p_type = "-"

                    if "username" in proc.keys():
                        p_user = proc["username"]
                    else:
                        p_user = "-"

                    p_sess = "-"
                    p_sid = "-"
                    if 'Sessions' in state_keys:
                        
                        for sess in host_state['Sessions']:
                            if sess["PID"] == pid:
                                p_sess = sess["agent"]
                                p_sid = sess["session_id"]
                                break
                    
                    subnet_cidr = host_state['Interface'][0]["Subnet"]
                    for name, cidr in subnet_cidr_map.items(): 
                        if cidr == subnet_cidr:
                            subnet_name = name.name
                            break
                    
                    if row == num_procs and row == 1:
                        tables[subnet_name].add_row([hostname, pid, p_name, p_type, p_user, p_sess, p_sid], divider=True)
                    elif row == 1:
                        tables[subnet_name].add_row([hostname, pid, p_name, p_type, p_user, p_sess, p_sid])
                    elif row == num_procs:
                        tables[subnet_name].add_row(["\"", pid, p_name, p_type, p_user, p_sess, p_sid], divider=True)
                    else:
                        tables[subnet_name].add_row(["\"", pid, p_name, p_type, p_user, p_sess, p_sid])
        
        return tables

    def get_agent_session_tables(self):
        """Creates a table of: agent name, session ID, associated hostname, username, session type, and associated process ID; per agent team (red, blue, green). 

        Returns
        -------
        team_tables: Dict[str, PrettyTable]
        """
        
        # Get true state info from environment
        get_dict = {
            'Sessions': 'All'
        }
        get_dict_per_host = {host: get_dict for host in self.hostnames}
        true_state_dict = self.env.get_true_state(info=get_dict_per_host)
        true_state_dict.pop("success")

        table_data = {
            'red' : {},
            'blue' : {},
            'green' : {}
        }

        for hostname, host_state in true_state_dict.items():
            for sess in host_state['Sessions']:
                agent = sess['agent']
                sess_id = sess['session_id']
                sess_type = sess['Type']
                sess_user = sess['username']
                sess_pid = sess['PID']

                team_dict = None
                if 'red' in agent:
                    team_dict = table_data['red']
                elif 'blue' in agent:
                    team_dict = table_data['blue']
                else:
                    team_dict = table_data['green']

                if not agent in team_dict.keys():
                    team_dict[agent] = []
                team_dict[agent].append((sess_id, hostname, sess_user, sess_type, sess_pid))

        team_tables = {}
        for team, team_data in table_data.items():
            team_table = PrettyTable(["Agent", "SID", "Hostname", "Username", "Type", "PID"])
            
            for agent, agent_data in team_data.items():
                agent_data.sort()
                total_agent_sessions = len(agent_data)

                sess_count = 0
                for session_data in agent_data:
                    sess_count += 1
                    row_data = list(session_data)
                    
                    if sess_count == 1:
                        row_data.insert(0, agent)
                        team_table.add_row(row_data)
                    elif sess_count == total_agent_sessions:
                        row_data.insert(0, "-")
                        team_table.add_row(row_data, divider=True)
                    else:
                        row_data.insert(0, "-")
                        team_table.add_row(row_data)

            team_tables[team] = team_table

        return team_tables

    def print_host_overview_table(self):
        """Prints the table produces by get_host_overview_table to stdout."""
        print(self.get_host_overview_table())

    def print_host_processes_tables(self):
        """Prints the tables produced by get_host_process_tables to stdout."""
        tables = self.get_host_processes_tables()
        for subnet, table in tables.items():
            print(f"Host Processes Table: Subnet {subnet} \n")
            print(table)
            print("\n")

    def print_agent_session_tables(self):
        """Prints the tables produced by get_agent_session_tables to stdout."""
        team_tables = self.get_agent_session_tables()
        for team, team_table in team_tables.items():
            print(f"Agent Session Table: Team {team} \n")
            print(team_table)
            print("\n")