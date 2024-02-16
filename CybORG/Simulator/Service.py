# Copyright DST Group. Licensed under the MIT license.
from CybORG.Simulator.Entity import Entity

class Service(Entity):
    """Class for services used in CybORG simulations
    
    Attributes
    ----------
    process : int
    active : bool
    session : Session
    percent_reliable : int
    """
    def __init__(self, process: int, active = True, session = None):
        super().__init__()
        self.process = process
        self.active = active
        self.session = session
        self._percent_reliable = 100

    def get_state(self) -> dict:
        """Returns the contents of the class"""
        return {
            'process': self.process,
            'active': self.active,
            'session': self.session,
            'reliability (%)': self._percent_reliable
        }
    
    def get_service_reliability(self):
        return self._percent_reliable

    def degrade_service_reliability(self, value: int = 20):
        """Degrades/decreases the service's reliability percent by the value given."""
        new_reliability = self._percent_reliable - value

        if new_reliability >= 0:
            self._percent_reliable = new_reliability
        else:
            self._percent_reliable = 0
    
    @classmethod
    def load(cls, info: dict):
        """Class loader"""
        return cls(
            process=info.get('PID'),
            active=info.get('active', True),
            session=info.get('session', None)
        )
    
    def __str__(self):
        active_str = 'active' if self.active else 'inactive'
        return f'Process {self.process}: {active_str}, {self._percent_reliable}% reliable'
