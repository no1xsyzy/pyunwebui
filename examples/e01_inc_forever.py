import asyncio
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
    return [Tag('p', {}, [f"Counter: {state.counter}"])]


def update(state: State, msg: int) -> State:
    return State(counter=state.counter + msg)


view = View(render, update, State(counter=0))

adapter = AiohttpAdapter(view)

app = web.Application()
adapter.assign(app)


async def main():
    logging.basicConfig(level=logging.INFO)
    runner = web.AppRunner(app)
    try:
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 7627)
        try:
            await site.start()
            logging.info('server started at http://0.0.0.0:7627')
            # main loop
            while True:
                view.dispatch(1)
                await asyncio.sleep(1)
            # end main loop
        finally:
            await site.stop()
    finally:
        await runner.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
