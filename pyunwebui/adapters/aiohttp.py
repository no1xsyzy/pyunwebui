import asyncio
import importlib.resources
import logging
import weakref
from contextlib import suppress
from typing import Literal, TypeAlias

from aiohttp import web, WSMessage

from pyunwebui import vdom
from pyunwebui.view import View

logger = logging.getLogger('pyunwebui.adapters.aiohttp')

Instruction: TypeAlias = tuple[Literal['i', 'd'], vdom.TagList]

ASSETS = importlib.resources.files('pyunwebui.adapters')


class AiohttpAdapter:
    def __init__(self, view: View, style='*{margin: 0}', title="Application", script=None, template=None):
        self.view: View = view
        view.add_listener(self.listener)
        self.qs = weakref.WeakSet[asyncio.Queue[Instruction]]()
        self.title = title
        self.style = style
        self.script = script if script is not None else (ASSETS / "unwebui.js").read_text()
        self.template = template if template is not None else (ASSETS / "index.html").read_text()

    def listener(self):
        vd: vdom.TagList = self.view.vdom()
        for q in self.qs:
            q.put_nowait(('d', vd))

    def assign(self, app: web.Application, root='/'):
        app.add_routes([web.get(root, self.page),
                        web.get(root + 'ws', self.ws)])

    async def page(self, request: web.Request) -> web.StreamResponse:
        body = vdom.to_html_str(self.view.vdom())
        text = self.template.format(title=self.title, script=self.script, style=self.style, body=body)

        return web.Response(text=text, content_type='text/html')

    async def ws(self, request: web.Request) -> web.StreamResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        vnl = self.view.vdom()
        q = asyncio.Queue[Instruction]()
        self.qs.add(q)
        t = asyncio.create_task(self.ws_sends(ws, q, vnl))

        async for msg in ws:
            msg: WSMessage
            if msg.type == web.WSMsgType.TEXT:
                if msg.data == 'sync':
                    vnl: vdom.TagList = self.view.vdom()
                    await q.put(('i', vnl))
                elif msg.data.startswith("msg"):
                    d = msg.data[3:]
                    logger.debug(f"received msg data {d!r}")
                    self.view.dispatch(d)
            elif msg.type == web.WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                      ws.exception())

        t.cancel()
        with suppress(asyncio.CancelledError):
            await t
        return ws

    async def ws_sends(self, ws: web.WebSocketResponse, q, vnl: list[vdom.Tag | str]):
        logger.info(f"started ws connection")
        try:
            while True:
                op, new_vnl = await q.get()
                if op == 'd':
                    await ws.send_str('p' + vdom.serialize_diff(vdom.diff_tags(vnl, new_vnl)))
                elif op == 'i':
                    await ws.send_str('i' + vdom.serialize(new_vnl))
                vnl = new_vnl
        except ConnectionResetError:
            await ws.close()
