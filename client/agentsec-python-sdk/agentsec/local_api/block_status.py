from aiohttp import web


async def block_status(request: web.Request) -> web.Response:
    watcher = request.app["block_watcher"]
    if watcher is None:
        return web.json_response(
            {"active_blocks": [], "block_count": 0, "ws_connected": False, "last_ws_message_at": None}
        )
    return web.json_response(watcher.snapshot())
