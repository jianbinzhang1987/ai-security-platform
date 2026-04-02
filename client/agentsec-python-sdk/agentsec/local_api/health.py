from aiohttp import web


async def health(request: web.Request) -> web.Response:
    config = request.app["config_manager"].config
    runtime_state = request.app["runtime_state"]
    status = "ok"
    if not runtime_state.initialized:
        status = "error"
    elif not runtime_state.collector_connected:
        status = "degraded"
    return web.json_response(
        {
            "status": status,
            "tenant_id": config.tenant_id,
            "app_id": config.app_id,
            "collector_url": config.collector_url,
            "collector_connected": runtime_state.collector_connected,
            "last_span_sent_at": None if runtime_state.last_span_sent_at is None else runtime_state.last_span_sent_at.isoformat(),
            "spans_sent_total": runtime_state.spans_sent_total,
            "spans_dropped_total": runtime_state.spans_dropped_total,
            "spans_buffered": runtime_state.spans_buffered,
            "config_version": config.version,
            "token_status": runtime_state.token_status,
            "uptime_seconds": runtime_state.uptime_seconds(),
        },
        status=200 if status in ("ok", "degraded") else 503,
    )
