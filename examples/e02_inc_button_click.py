import logging

from aiohttp import web
from attrs import define

from pyunwebui.adapters.aiohttp import AiohttpAdapter
from pyunwebui.vdom import Tag
from pyunwebui.view import View


@define
class State:
    counter: int


def render(state: State):
    return [
        Tag('p', {}, [f"Counter: {state.counter}"]),
        Tag('button', {'e:click': '1'}, [f"increment"])
    ]


def update(state: State, msg: str) -> State:
    return State(counter=state.counter + int(msg))


view = View(render, update, State(counter=0))

adapter = AiohttpAdapter(view)

app = web.Application()
adapter.assign(app)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    web.run_app(app, port=7627)
