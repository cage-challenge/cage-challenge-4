# Copyright DST Group. Licensed under the MIT license.


class Entity:
    """An abstract base class with the empty methods `__init__` and `get_state`, to be overwritten by child classes."""
    def __init__(self):
        pass

    def get_state(self):
        pass
