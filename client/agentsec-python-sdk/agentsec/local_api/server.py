from __future__ import annotations

import asyncio
import secrets
import threading
from pathlib import Path
from typing import Optional

from aiohttp import web

from agentsec.local_api.block_status import block_status
from agentsec.local_api.config_status import config_status
from agentsec.local_api.health import health
from agentsec.local_api.metrics import metrics
from agentsec.local_api.traces import trace_detail, traces
from agentsec.utils.logger import get_logger
from agentsec.utils.local_token import local_token_path

logger = get_logger("local_api")


@web.middleware
async def auth_middleware(request: web.Request, handler):
    protected_paths = {
        "/agentsec/traces",
        "/agentsec/config/status",
        "/agentsec/block/status",
    }
    if request.path.startswith("/agentsec/traces/") or request.path in protected_paths:
        auth_header = request.headers.get("Authorization", "")
        expected = request.app["runtime_state"].local_api_token
        if not auth_header.startswith("Bearer ") or not secrets.compare_digest(auth_header[7:], expected):
            raise web.HTTPUnauthorized(text="invalid local api token")
    return await handler(request)


class LocalApiServer:
    def __init__(self, config_manager, runtime_state, trace_store, block_watcher=None):
        self.config_manager = config_manager
        self.runtime_state = runtime_state
        self.trace_store = trace_store
        self.block_watcher = block_watcher
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._runner: Optional[web.AppRunner] = None
        self._token_path: Path = local_token_path()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True, name="agentsec-local-api")
        self._thread.start()

    def stop(self) -> None:
        if self._loop and self._runner:
            future = asyncio.run_coroutine_threadsafe(self._shutdown(), self._loop)
            future.result(timeout=3.0)
        if self._thread:
            self._thread.join(timeout=1.0)
        try:
            self._token_path.unlink(missing_ok=True)
        except OSError:
            logger.debug("Failed to remove local API token file")

    def _run(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._start_server())
        self._loop.run_forever()

    async def _start_server(self) -> None:
        app = web.Application(middlewares=[auth_middleware])
        app["config_manager"] = self.config_manager
        app["runtime_state"] = self.runtime_state
        app["trace_store"] = self.trace_store
        app["block_watcher"] = self.block_watcher
        app.add_routes(
            [
                web.get("/agentsec/health", health),
                web.get("/agentsec/metrics", metrics),
                web.get("/agentsec/traces", traces),
                web.get("/agentsec/traces/{trace_id}", trace_detail),
                web.get("/agentsec/config/status", config_status),
                web.get("/agentsec/block/status", block_status),
            ]
        )
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        config = self.config_manager.config.local_api
        site = web.TCPSite(self._runner, config.host, config.port)
        await site.start()
        self._token_path.write_text(self.runtime_state.local_api_token, encoding="utf-8")
        logger.info("Local API started on %s:%s", config.host, config.port)

    async def _shutdown(self) -> None:
        if self._runner:
            await self._runner.cleanup()
        if self._loop:
            self._loop.stop()
