# Copyright DST Group. Licensed under the MIT license.
import enum


class TernaryEnum(enum.Enum):
    TRUE = enum.auto()
    UNKNOWN = enum.auto()
    FALSE = enum.auto()
    IN_PROGRESS = enum.auto()

    @classmethod
    def parse_bool(cls, state_bool):
        if isinstance(state_bool, bool):
            if state_bool:
                return cls.TRUE
            return cls.FALSE
        return cls.UNKNOWN

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, bool):
            other = TernaryEnum.parse_bool(other)
        return isinstance(other, TernaryEnum) and self.value == other.value


class OperatingSystemPatch(enum.Enum):
    UNKNOWN = enum.auto()
    FILE_1 = enum.auto()
    Q147222 = enum.auto()
    KB911164 = enum.auto()
    MS17_010 = enum.auto()
    KB4500331 = enum.auto()
    KB4499149 = enum.auto()
    KB4499180 = enum.auto()
    KB4499164 = enum.auto()
    KB4499175 = enum.auto()


    @classmethod
    def parse_string(cls, patch_string):
        patch_map = {
            "file 1": cls.FILE_1,
            "q147222": cls.Q147222,
            "kb911164": cls.KB911164,
            "ms17-010": cls.MS17_010,
            "kb4500331": cls.KB4500331,
            "kb4499149": cls.KB4499149,
            "kb4499180": cls.KB4499180,
            "kb4499164": cls.KB4499164,
            "kb4499175": cls.KB4499175,
        }
        return patch_map.get(patch_string.lower(), cls.UNKNOWN)
    
    def __str__(self):
        return str(self.value)


class Architecture(enum.Enum):
    x86 = enum.auto()
    x64 = enum.auto()
    UNKNOWN = enum.auto()

    @classmethod
    def parse_string(cls, arch_string):
        arch_map = {
            "x86": cls.x86,
            "x64": cls.x64,
            "x86_64": cls.x64,  # Map both "x64" and "x86_64" to x64
        }
        return arch_map.get(arch_string.lower(), cls.UNKNOWN)


class OperatingSystemType(enum.Enum):
    """An enum for representing the different possible Operating systems. """
    UNKNOWN = enum.auto()
    WINDOWS = enum.auto()
    LINUX = enum.auto()

    @classmethod
    def parse_string(cls, os_string):
        os = os_string.lower()
        if os == "linux":
            return cls.LINUX
        if "windows" in os:
            return cls.WINDOWS
        return cls.UNKNOWN

    def __str__(self):
        return self.name


class OperatingSystemDistribution(enum.Enum):
    """An enum for representing the different possible Operating systems. """
    UNKNOWN = enum.auto()
    WINDOWS_XP = enum.auto()
    WINDOWS_SVR_2003 = enum.auto()
    WINDOWS_SVR_2008 = enum.auto()
    WINDOWS_7 = enum.auto()
    WINDOWS_8 = enum.auto()
    WINDOWS_10 = enum.auto()
    UBUNTU = enum.auto()
    KALI = enum.auto()
    WINDOWS_SVR_2003SP2 = enum.auto()
    WINDOWS_VISTA = enum.auto()
    WINDOWS_SVR_2008SP1 = enum.auto()
    WINDOWS_SVR_2008R2 = enum.auto()
    WINDOWS_7SP1 = enum.auto()
    DRONE_LINUX = enum.auto()  # TODO find correct distro

    @classmethod
    def parse_string(cls, os_string):
        os_string = os_string.lower()
        if os_string == "windows xp":
            return cls.WINDOWS_XP
        if os_string == "windows server 2003":
            return cls.WINDOWS_SVR_2003
        if "windows server 2008" in os_string or os_string == 'windows_svr_2008':
            return cls.WINDOWS_SVR_2008
        if os_string == "windows 7":
            return cls.WINDOWS_7
        if os_string == "windows 8":
            return cls.WINDOWS_8
        if os_string == "windows 10":
            return cls.WINDOWS_10
        if "ubuntu" in os_string:
            return cls.UBUNTU
        if "kali" in os_string:
            return cls.KALI
        if "2003sp2" in os_string and "window" in os_string:
            return cls.WINDOWS_SVR_2003SP2
        if "vista" in os_string and "window" in os_string:
            return cls.WINDOWS_VISTA
        if "svr 2008sp1" in os_string and "window" in os_string:
            return cls.WINDOWS_SVR_2008SP1
        if "svr 2008r2" in os_string and "window" in os_string:
            return cls.WINDOWS_SVR_2008R2
        if "7sp1" in os_string and "window" in os_string:
            return cls.WINDOWS_7SP1
        if 'dronelinux' in os_string:
            return cls.DRONE_LINUX
        return cls.UNKNOWN

    def __str__(self):
        return self.name


class OperatingSystemVersion(enum.Enum):
    """An enum for representing the different possible Operating systems. """
    UNKNOWN = enum.auto()
    SP0 = enum.auto()
    SP1 = enum.auto()
    SP2 = enum.auto()
    SP3 = enum.auto()
    U18_04_3 = enum.auto()
    U18_04 = enum.auto()
    U8_04 = enum.auto()
    K2019_1 = enum.auto()
    K2019_2 = enum.auto()
    K2019_4 = enum.auto()
    W6_2_9200_16384 = enum.auto()
    W6_1_7601 = enum.auto()
    NT6_1 = enum.auto()

    @classmethod
    def parse_string(cls, os_string: str):
        os_string = os_string.lower()
        if os_string == "sp0":
            return cls.SP0
        if os_string == "sp1":
            return cls.SP1
        if os_string == "sp2":
            return cls.SP2
        if os_string == "sp3":
            return cls.SP3
        if os_string == "6.2.9200.16384":
            return cls.W6_2_9200_16384
        if "6.1.7601" in os_string or os_string == 'w6_1_7601':
            return cls.W6_1_7601
        if os_string in ('18.04.3', 'u18_04_3'):
            return cls.U18_04_3
        if os_string == "18.04":
            return cls.U18_04
        if os_string == "8.04":
            return cls.U8_04
        if os_string in ('2019.1', 'k2019_1'):
            return cls.K2019_1
        if os_string in ('2019.2', 'k2019_2'):
            return cls.K2019_2
        if "4.19.0-kali4" in os_string or os_string == "k2019_4":
            return cls.K2019_4
        if os_string == "nt6.1":
            return cls.NT6_1
        return cls.UNKNOWN

    def __str__(self):
        return self.name


class OperatingSystemKernelVersion(enum.Enum):
    """An enum for representing the different possible Operating systems. """
    UNKNOWN = enum.auto()
    L2_6_24 = enum.auto()
    L4_15_0_1057_AWS = enum.auto()
    L5_2_0 = enum.auto()
    L5_3_0 = enum.auto()

    @classmethod
    def parse_string(cls, os_string: str):
        os_map = {
            "linux 2.6.24": cls.L2_6_24,
            "4.15.0-1057-aws": cls.L4_15_0_1057_AWS,
            "linux 5.2.0": cls.L5_2_0,
            "linux 5.3.0": cls.L5_3_0,
        }
        return os_map.get(os_string.lower(), cls.UNKNOWN)

    def __str__(self):
        return self.name


class ProcessName(enum.Enum):
    UNKNOWN = enum.auto()
    SVCHOST = enum.auto()
    INIT = enum.auto()
    CRON = enum.auto()
    UDEVD = enum.auto()
    JSVC = enum.auto()
    SSHD = enum.auto()
    MYSQLD_SAFE = enum.auto()
    MYSQLD = enum.auto()
    SMBD = enum.auto()
    SMTP = enum.auto()
    FEMITTER = enum.auto()
    APACHE2 = enum.auto()
    EXPLORER = enum.auto()
    LSASS = enum.auto()
    WINLOGON = enum.auto()
    SMSS = enum.auto()
    SYSTEM = enum.auto()
    SYSTEM_IDLE_PROCESS = enum.auto()
    SERVICES = enum.auto()
    SHELL = enum.auto()
    TELNET = enum.auto()
    SLEEP = enum.auto()
    JAVA = enum.auto()
    PS = enum.auto()
    VELOCLIENT = enum.auto()
    POWERSHELL = enum.auto()
    CMD = enum.auto()
    OTSERVICE = enum.auto()

    @classmethod
    def parse_string(cls, name: str):
        name_map = {
            'svchost': cls.SVCHOST,
            'svchost.exe': cls.SVCHOST,
            'init': cls.INIT,
            'cron': cls.CRON,
            'udevd': cls.UDEVD,
            'jsvc': cls.JSVC,
            'sshd': cls.SSHD,
            'sshd.exe': cls.SSHD,
            'mysqld_safe': cls.MYSQLD_SAFE,
            'mysqld': cls.MYSQLD,
            'smbd': cls.SMBD,
            'smtp': cls.SMTP,
            'femitter.exe': cls.FEMITTER,
            'apache2': cls.APACHE2,
            'explorer': cls.EXPLORER,
            'explorer.exe': cls.EXPLORER,
            'lsass': cls.LSASS,
            'lsass.exe': cls.LSASS,
            'winlogon': cls.WINLOGON,
            'winlogon.exe': cls.WINLOGON,
            'smss': cls.SMSS,
            'smss.exe': cls.SMSS,
            'system': cls.SYSTEM,
            'system idle process': cls.SYSTEM_IDLE_PROCESS,
            'system process': cls.SYSTEM_IDLE_PROCESS,
            'services': cls.SERVICES,
            'services.exe': cls.SERVICES,
            'bash': cls.SHELL,
            'sh': cls.SHELL,
            'sh.exe': cls.SHELL,
            'telnet': cls.TELNET,
            'sleep': cls.SLEEP,
            'java': cls.JAVA,
            'ps': cls.PS,
            'velociraptorclient': cls.VELOCLIENT,
            'powershell.exe': cls.POWERSHELL,
            'powershell': cls.POWERSHELL,
            'cmd.exe': cls.CMD,
            'cmd': cls.CMD,
            'otservice': cls.OTSERVICE
        }
        return name_map.get(name.lower(), cls.UNKNOWN)


class ProcessType(enum.Enum):
    """An enum for representing the different types of services. """
    UNKNOWN = enum.auto()
    SSH = enum.auto()
    SVCHOST = enum.auto()
    SMB = enum.auto()
    SMTP = enum.auto()
    FEMITTER = enum.auto()
    WEBSERVER = enum.auto()
    NETCAT = enum.auto()
    RDP = enum.auto()
    REVERSE_SESSION_HANDLER = enum.auto()
    REVERSE_SESSION = enum.auto()
    MYSQL = enum.auto()

    @classmethod
    def parse_string(cls, service_string):
        service_string = service_string.lower()
        if service_string in ('ssh', 'sshd', 'sshd.exe'):
            return cls.SSH
        if service_string == "svchost":
            return cls.SVCHOST
        if service_string == "smtp":
            return cls.SMTP
        if service_string == "femitter":
            return cls.FEMITTER
        if service_string == "mysql":
            return cls.MYSQL
        if service_string == "smb":
            return cls.SMB
        if service_string.replace(" ", "") == "webserver":
            return cls.WEBSERVER
        if service_string == "netcat":
            return cls.NETCAT
        if service_string == "rdp":
            return cls.RDP
        if service_string == "reverse_session_handler":
            return cls.REVERSE_SESSION_HANDLER
        if service_string == "reverse_session":
            return cls.REVERSE_SESSION
        if service_string == "http":
            return cls.WEBSERVER
        if service_string == "https":
            return cls.WEBSERVER
        return cls.UNKNOWN

    def __str__(self):
        return self.name


# Potentially split this into separate Enums for each ProcessType at later date
class ProcessVersion(enum.Enum):
    OPENSSH_1_3 = enum.auto()
    SVC10_0_17763_1 = enum.auto()
    SAMBA_3_0_20_DEB = enum.auto()
    SMBv1 = enum.auto()
    APACHE_TOMCAT = enum.auto()
    PYTHON_SERVER = enum.auto()
    HARAKA_2_7_0 = enum.auto()
    HARAKA_2_8_9 = enum.auto()
    UNKNOWN = enum.auto()

    @classmethod
    def parse_string(cls, version_string):
        version_map = {
            "openssh 1.3": cls.OPENSSH_1_3,
            "10.0.17763.1": cls.SVC10_0_17763_1,
            "samba 3.0.20-debian": cls.SAMBA_3_0_20_DEB,
            "apache tomcat": cls.APACHE_TOMCAT,
            "python simplehttpserver": cls.PYTHON_SERVER,
            "smbv1": cls.SMBv1,
            "haraka 2.7.0": cls.HARAKA_2_7_0,
        }
        if version_string is not None and isinstance(version_string, str):
            version_string = version_string.lower()
        if version_string is not None:
            return version_map.get(version_string, version_string)
        return cls.UNKNOWN


class TransportProtocol(enum.Enum):
    """An enum for representing the different types of services. """
    UNKNOWN = enum.auto()
    TCP = enum.auto()
    UDP = enum.auto()

    @classmethod
    def parse_string(cls, service_string: str):
        service_map = {
            "tcp": cls.TCP,
            "udp": cls.UDP,
        }
        return service_map.get(service_string.lower(), cls.UNKNOWN)

    def __str__(self):
        return self.name


class BuiltInGroups(enum.Enum):
    UNKNOWN = enum.auto()
    USERS = enum.auto()
    WEBSERVER = enum.auto()
    ROOT = enum.auto()
    SHADOW = enum.auto()
    ADMINISTRATORS = enum.auto()

    @classmethod
    def parse_string(cls, group_string: str):
        group_map = {
            "users": cls.USERS,
            "web server users": cls.WEBSERVER,
            "root": cls.ROOT,
            "shadow": cls.SHADOW,
            "administrators": cls.ADMINISTRATORS,
        }
        return group_map.get(group_string.lower(), cls.UNKNOWN)


class SessionType(enum.Enum):
    """An enum for representing the different types of sessions. """
    UNKNOWN = enum.auto()
    SSH = enum.auto()
    SHELL = enum.auto()
    METERPRETER = enum.auto()
    MSF_SHELL = enum.auto()
    MSF_SERVER = enum.auto()
    VELOCIRAPTOR_CLIENT = enum.auto()
    VELOCIRAPTOR_SERVER = enum.auto()
    LOCAL_SHELL = enum.auto()
    RED_ABSTRACT_SESSION = enum.auto()
    RED_REVERSE_SHELL = enum.auto()
    GREY_SESSION = enum.auto()
    BLUE_DRONE_SESSION = enum.auto()
    RED_DRONE_SESSION = enum.auto()

    @classmethod
    def parse_string(cls, service_string):
        service_string = service_string.lower()
        if service_string == "ssh":
            return cls.SSH
        if service_string == "shell":
            return cls.SHELL
        if service_string == "meterpreter":
            return cls.METERPRETER
        if service_string in ('msf shell', 'msf_shell'):
            return cls.MSF_SHELL
        if service_string == "metasploitserver":
            return cls.MSF_SERVER
        if service_string == "velociraptorclient":
            return cls.VELOCIRAPTOR_CLIENT
        if service_string == "velociraptorserver":
            return cls.VELOCIRAPTOR_SERVER
        if service_string == "redabstractsession":
            return cls.RED_ABSTRACT_SESSION
        if service_string == "red_reverse_shell":
            return cls.RED_REVERSE_SHELL
        if service_string.replace(" ", "").replace("_", "") == "localshell":
            return cls.LOCAL_SHELL
        if service_string == "green_session":
            return cls.GREY_SESSION
        if service_string == "blue_drone_session":
            return cls.BLUE_DRONE_SESSION
        if service_string == "red_drone_session":
            return cls.RED_DRONE_SESSION
        return cls.UNKNOWN

    def __str__(self):
        return self.name


class Path(enum.Enum):
    UNKNOWN = enum.auto()
    WINDOWS = enum.auto()
    WINDOWS_SYSTEM = enum.auto()
    SYSTEM = enum.auto()
    TEMP = enum.auto()
    SBIN = enum.auto()
    BIN = enum.auto()
    USR_SBIN = enum.auto()
    USR_BIN = enum.auto()
    ETC = enum.auto()
    ADMINISTRATOR_DESKTOP = enum.auto()
    WEBSERVER = enum.auto()
    EXPLOIT = enum.auto()

    @classmethod
    def parse_string(cls, path_string: str):
        path_map = {
            "system": cls.SYSTEM,
            "c:/windows/system32/": cls.WINDOWS_SYSTEM,
            "c:\\windows\\system32\\": cls.WINDOWS_SYSTEM,
            "c:/windows/": cls.WINDOWS,
            "c:\\windows\\": cls.WINDOWS,
            "/tmp/": cls.TEMP,
            "c:\\temp\\": cls.TEMP,
            "/sbin/": cls.SBIN,
            "/sbin": cls.SBIN,
            "/bin/": cls.BIN,
            "/bin": cls.BIN,
            "/usr/sbin/": cls.USR_SBIN,
            "/usr/sbin": cls.USR_SBIN,
            "/usr/bin/": cls.USR_BIN,
            "/usr/bin": cls.USR_BIN,
            "/etc/": cls.ETC,
            "/etc": cls.ETC,
            "c:\\users\\administrator\\desktop\\": cls.ADMINISTRATOR_DESKTOP,
            "/tmp/webserver/": cls.WEBSERVER,
            "/usr/share/exploitdb/exploits/linux/local/": cls.EXPLOIT,
        }
        return path_map.get(path_string.lower(), cls.UNKNOWN)


class ProcessState(enum.Enum):
    """An enum for representing the different types of services. """
    UNKNOWN = enum.auto()
    OPEN = enum.auto()
    CLOSED = enum.auto()
    FILTERED = enum.auto()

    @classmethod
    def parse_string(cls, service_string: str):
        service_map = {
            "open": cls.OPEN,
            "closed": cls.CLOSED,
            "filtered": cls.FILTERED,
        }
        return service_map.get(service_string.lower(), cls.UNKNOWN)

    def __str__(self):
        return self.name


class FileType(enum.Enum):
    UNKNOWN = enum.auto()
    SVCHOST = enum.auto()
    PASSWD = enum.auto()
    SHADOW = enum.auto()
    FLAG = enum.auto()
    SMBCLIENT = enum.auto()
    NMAP = enum.auto()
    DirtyCowCode = enum.auto()
    DirtyCowExe = enum.auto()
    PYTHON = enum.auto()
    GCC = enum.auto()
    UDEV141CODE = enum.auto()
    UDEV141EXE = enum.auto()
    NC_REVERSE_SHELL = enum.auto()
    NC = enum.auto()

    @classmethod
    def parse_string(cls, name_string: str):
        name_map = {
            "svchost": cls.SVCHOST,
            "passwd": cls.PASSWD,
            "shadow": cls.SHADOW,
            "flag": cls.FLAG,
            "smbclient": cls.SMBCLIENT,
            "nmap": cls.NMAP,
            "dirty_cow_c_file": cls.DirtyCowCode,
            "python": cls.PYTHON,
            "gcc": cls.GCC,
            "udev < 1.4.1": cls.UDEV141CODE,
            "nc_reverse_shell": cls.NC_REVERSE_SHELL,
            "nc": cls.NC,
        }
        return name_map.get(name_string.lower(), cls.UNKNOWN)


class FileVersion(enum.Enum):
    UNKNOWN = enum.auto()
    U4_2_4_1 = enum.auto()
    D9_2_1_21 = enum.auto()
    OPENBSD = enum.auto()

    @classmethod
    def parse_string(cls, name_string: str):
        name_map = {
            "ubuntu 4.2.4-1": cls.U4_2_4_1,
            "debian 9.2.1-21": cls.D9_2_1_21,
            "openbsd": cls.OPENBSD,
        }
        return name_map.get(name_string.lower(), cls.UNKNOWN)



class FileExt(enum.Enum):
    ELF = enum.auto()
    UNKNOWN = enum.auto()

    @classmethod
    def parse_string(cls, name_string: str):
        if name_string.lower() == "elf":
            return cls.ELF
        return cls.UNKNOWN


class Vulnerability(enum.Enum):
    UNKNOWN = enum.auto()

    @classmethod
    def parse_string(cls, vuln_string):
        return cls.UNKNOWN


class Vendor(enum.Enum):
    UNKNOWN = enum.auto()

    @classmethod
    def parse_string(cls, vendor_string):
        return cls.UNKNOWN


class PasswordHashType(enum.Enum):
    UNKNOWN = enum.auto()
    MD5 = enum.auto()
    SHA512 = enum.auto()
    NTLM = enum.auto()

    @classmethod
    def parse_string(cls, hash_string: str):
        hash_map = {
            "md5": cls.MD5,
            "sha512": cls.SHA512,
            "ntlm": cls.NTLM
        }
        return hash_map.get(hash_string.lower(), cls.UNKNOWN)


class InterfaceType(enum.Enum):
    UNKNOWN = enum.auto()
    BROADCAST = enum.auto()
    LOCAL = enum.auto()

    @classmethod
    def parse_string(cls, interface_string: str):
        interface_map = {
            "broadcast": cls.BROADCAST,
            "local": cls.LOCAL,
        }
        return interface_map.get(interface_string.lower(), cls.UNKNOWN)


class AppProtocol(enum.Enum):
    UNKNOWN = enum.auto()
    HTTP = enum.auto()
    HTTPS = enum.auto()
    SSH = enum.auto()
    JPV13 = enum.auto()
    TCP = enum.auto()
    MYSQL = enum.auto()
    NETBIOS_SSN = enum.auto()
    MICROSOFT_DS = enum.auto()
    RPC = enum.auto()

    @classmethod
    def parse_string(cls, protocol_string: str):
        protocol_map = {
            "http": cls.HTTP,
            "https": cls.HTTPS,
            "ssh": cls.SSH,
            "jpv13": cls.JPV13,
            "tcp": cls.TCP,
            "mysql": cls.MYSQL,
            "netbios-ssn": cls.NETBIOS_SSN,
            "microsoft-ds": cls.MICROSOFT_DS,
            "rpc": cls.RPC,
        }
        return protocol_map.get(protocol_string.lower(), cls.UNKNOWN)


class QueryType(enum.Enum):
    SYNC = enum.auto()
    ASYNC = enum.auto()

    @classmethod
    def parse_string(cls, query_string: str):
        if query_string.lower() == "sync":
            return cls.SYNC
        if query_string.lower() == "async":
            return cls.ASYNC

## The following code contains work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105.
## Additionally, we waive copyright and related rights in the utilized code worldwide through the CC0 1.0 Universal public domain dedication.

class DecoyType(enum.Flag):
    NONE = 0
    ESCALATE = enum.auto()
    EXPLOIT = enum.auto()
    SANDBOXING_EXPLOIT = enum.auto()
