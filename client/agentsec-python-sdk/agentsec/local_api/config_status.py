from aiohttp import web


async def config_status(request: web.Request) -> web.Response:
    config = request.app["config_manager"].config
    runtime_state = request.app["runtime_state"]
    return web.json_response(
        {
            "config_version": config.version,
            "config_schema_version": config.config_schema_version,
            "sampling_rate": config.sampling_rate,
            "blocked_session_ids": config.blocked_session_ids,
            "last_fetched_at": None if runtime_state.last_config_fetch_at is None else runtime_state.last_config_fetch_at.isoformat(),
            "next_fetch_at": None if runtime_state.next_config_fetch_at is None else runtime_state.next_config_fetch_at.isoformat(),
            "last_fetch_ok": runtime_state.last_config_fetch_ok,
            "token_status": runtime_state.token_status,
            "in_sync": runtime_state.last_config_fetch_ok or runtime_state.last_config_fetch_at is None,
        }
    )
