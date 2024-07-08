from typing import TypeVar, Callable

from pyunwebui import Tag

_ST = TypeVar('_ST')
_MT = TypeVar('_MT')


class View:
    def __init__(self,
                 render: Callable[[_ST], list[Tag | str]],
                 update: Callable[[_ST, _MT], _ST],
                 initial_state: _ST):
        self.render = render
        self.update = update
        self.state = initial_state
        self.rev = 0
        self.listeners = []

    def dispatch(self, msg):
        self.state = self.update(self.state, msg)
        self.rev += 1
        for listener in self.listeners:
            listener()

    def add_listener(self, listener):
        self.listeners.append(listener)

    def remove_listener(self, listener):
        self.listeners.remove(listener)

    def vdom(self):
        return self.render(self.state)
