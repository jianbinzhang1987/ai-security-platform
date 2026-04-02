from aiohttp import web


async def metrics(request: web.Request) -> web.Response:
    config = request.app["config_manager"].config
    runtime_state = request.app["runtime_state"]
    payload = "\n".join(
        [
            "# HELP agentsec_sampling_rate Current sampling rate.",
            "# TYPE agentsec_sampling_rate gauge",
            f"agentsec_sampling_rate {config.sampling_rate}",
            "# HELP agentsec_collector_connected Collector connectivity state.",
            "# TYPE agentsec_collector_connected gauge",
            f"agentsec_collector_connected {1 if runtime_state.collector_connected else 0}",
            "# HELP agentsec_spans_buffered Number of buffered spans.",
            "# TYPE agentsec_spans_buffered gauge",
            f"agentsec_spans_buffered {runtime_state.spans_buffered}",
            "# HELP agentsec_spans_sent_total Number of exported spans.",
            "# TYPE agentsec_spans_sent_total counter",
            f"agentsec_spans_sent_total {runtime_state.spans_sent_total}",
            "# HELP agentsec_spans_dropped_total Number of dropped spans.",
            "# TYPE agentsec_spans_dropped_total counter",
            f"agentsec_spans_dropped_total {runtime_state.spans_dropped_total}",
            "# HELP agentsec_token_status Token validity state.",
            "# TYPE agentsec_token_status gauge",
            f"agentsec_token_status{{status=\"{runtime_state.token_status}\"}} 1",
            "# HELP agentsec_config_last_fetch_ok Last config fetch success state.",
            "# TYPE agentsec_config_last_fetch_ok gauge",
            f"agentsec_config_last_fetch_ok {1 if runtime_state.last_config_fetch_ok else 0}",
        ]
    )
    return web.Response(text=payload, content_type="text/plain")
