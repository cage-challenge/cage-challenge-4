# Copyright DST Group. Licensed under the MIT license.

from CybORG.Shared.Enums import PasswordHashType
from CybORG.Simulator.Entity import Entity
from CybORG.Simulator.LocalGroup import LocalGroup


class User(Entity):
    """User entity
    
    Attributes
    ----------
    username : str
    password : str
    password_hash : str
    bruteforceable : bool
    password_hash_type : str
    groups: List[LocalGroup]
    logged_in : bool
    uid : int
    disabled : bool
    """
    def __init__(self, username: str, uid: int, password: str = None, password_hash: str = None,
                 password_hash_type: str = None, groups: list = None,
                 logged_in: bool = None, bruteforceable: bool = False):
        """Instantiate the User object"""
        super().__init__()
        self.username = username

        self.password = password
        self.password_hash = password_hash
        self.bruteforceable = bruteforceable
        # assert type(bruteforceable) is bool
        if password_hash_type is not None:
            self.password_hash_type = PasswordHashType.parse_string(password_hash_type)
        else:
            self.password_hash_type = None
        self.groups = []
        if groups is not None:
            for group in groups:
                self.groups.append(LocalGroup(name=group.get('Group Name'), gid=group.get('GID')))
        self.logged_in = logged_in
        self.uid = uid
        self.disabled = False

    def get_state(self):
        """Get the current internal state of the user, as an observation """
        obs = []

        if len(self.groups) > 0:
            for group in self.groups:
                observation = {"username": self.username, "password": self.password,
                               "password_hash": self.password_hash, "password_hash_type": self.password_hash_type,
                               "logged_in": self.logged_in, "group": group.name, "gid": group.ident}
                obs.append(observation)
        else:
            observation = {"username": self.username, "password": self.password, "password_hash": self.password_hash,
                           "password_hash_type": self.password_hash_type, "logged_in": self.logged_in}
            obs.append(observation)
        return obs

    def add_group(self, group: LocalGroup):
        """Add a group to the user's list of groups.
        
        Parameters
        ----------
        group : LocalGroup
            group to add
        """
        if self.groups is None:
            self.groups = [group]
        else:
            self.groups.append(group)

    def disable_user(self):
        """Set user to 'disabled'"""
        self.disabled = True
        return True

    @classmethod
    def load(cls, info: dict):
        return cls(
            username=info.get('username'),
            groups=info.get('Groups'),
            uid=info.get('uid'),
            password=info.get('Password'),
            bruteforceable=info.get('Bruteforceable', False)
        )

    def __str__(self):
        return f'{self.username}'
