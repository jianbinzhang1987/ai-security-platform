from aiohttp import web


async def traces(request: web.Request) -> web.Response:
    store = request.app["trace_store"]
    limit = int(request.query.get("limit", "10"))
    offset = int(request.query.get("offset", "0"))
    span_type = request.query.get("type")
    has_security_event = request.query.get("has_security_event", "false").lower() == "true"
    risk_level = request.query.get("risk_level")
    return web.json_response(
        store.list_traces(
            limit=limit,
            offset=offset,
            span_type=span_type,
            has_security_event=has_security_event,
            risk_level=risk_level,
        )
    )


async def trace_detail(request: web.Request) -> web.Response:
    store = request.app["trace_store"]
    trace = store.get_trace(request.match_info["trace_id"])
    if trace is None:
        raise web.HTTPNotFound(text="trace not found")
    return web.json_response(trace)
