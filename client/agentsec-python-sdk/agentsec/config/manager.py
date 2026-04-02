from __future__ import annotations

import threading
import time
from typing import Callable, Optional

import httpx

from agentsec.auth.token import TokenManager
from agentsec.config.defaults import DEFAULT_COLLECTOR_URL, DEFAULT_PLATFORM_URL
from agentsec.config.models import AgentSecConfig
from agentsec.utils.env import get_env_bool, get_env_float, get_env_int, get_env_str
from agentsec.utils.logger import get_logger
from agentsec.utils.registration import RegistrationManager

logger = get_logger("config")


class ConfigManager:
    """Loads local bootstrap config and refreshes remote config safely."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._token_manager = TokenManager()
        self._subscribers: list[Callable[[AgentSecConfig], None]] = []
        self._stop_event = threading.Event()
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True, name="agentsec-config")
        self._runtime_state = None
        self._config: AgentSecConfig = self._load_bootstrap_config()
        self._token: Optional[str] = self._token_manager.load_token()
        self._last_fetch_at: Optional[float] = None
        self._registration = RegistrationManager(self._config.platform_url, self._token_manager)
        self._sync_token_state()
        if not self._token:
            self._token = self._registration.register_if_needed(self._config.sdk_version)
            self._sync_token_state()
        if not self._token:
            logger.warning("AgentSec registration unavailable, SDK will run in fail-open mode")

    def _load_bootstrap_config(self) -> AgentSecConfig:
        collector_url = get_env_str("AGENTSEC_COLLECTOR_URL", DEFAULT_COLLECTOR_URL)
        platform_url = get_env_str("AGENTSEC_PLATFORM_URL", DEFAULT_PLATFORM_URL)
        config_url = get_env_str("AGENTSEC_CONFIG_URL", f"{platform_url.rstrip('/')}/internal/sdk-config")
        heartbeat_url = get_env_str("AGENTSEC_HEARTBEAT_URL", f"{platform_url.rstrip('/')}/internal/heartbeat")
        otlp_protocol = get_env_str("AGENTSEC_OTLP_PROTOCOL", None)
        if not otlp_protocol:
            otlp_protocol = "http/protobuf" if collector_url.startswith(("http://", "https://")) else "grpc"
        return AgentSecConfig(
            tenant_id=get_env_str("AGENTSEC_TENANT_ID", "unknown"),
            app_id=get_env_str("AGENTSEC_APP_ID", "unknown"),
            collector_url=collector_url,
            platform_url=platform_url,
            config_url=config_url,
            heartbeat_url=heartbeat_url,
            sampling_rate=get_env_float("AGENTSEC_SAMPLING_RATE", 1.0),
            pii_redaction_enabled=get_env_bool("AGENTSEC_PII_REDACTION_ENABLED", True),
            secret_scan_enabled=get_env_bool("AGENTSEC_SECRET_SCAN_ENABLED", True),
            injection_guard_enabled=get_env_bool("AGENTSEC_INJECTION_GUARD_ENABLED", True),
            config_poll_interval=get_env_int("AGENTSEC_CONFIG_POLL_INTERVAL", 30),
            heartbeat_interval=get_env_int("AGENTSEC_HEARTBEAT_INTERVAL", 30),
            buffer_capacity=get_env_int("AGENTSEC_BUFFER_CAPACITY", 10000),
            audit_log_path=get_env_str("AGENTSEC_AUDIT_LOG_PATH", None),
            otlp_protocol=otlp_protocol,
            local_trace_max_size=get_env_int("AGENTSEC_LOCAL_TRACE_MAX_SIZE", 1000),
        )

    @property
    def token(self) -> Optional[str]:
        return self._token

    @property
    def collector_url(self) -> str:
        return self._config.collector_url

    @property
    def config(self) -> AgentSecConfig:
        with self._lock:
            return self._config.model_copy(deep=True)

    def fetch_config(self) -> AgentSecConfig:
        if not self._token or not self._config.config_url:
            return self.config

        headers = {"Authorization": f"Bearer {self._token}"}
        params = {"version": self._config.version}
        try:
            response = httpx.get(self._config.config_url, headers=headers, params=params, timeout=10.0)
            if response.status_code == 304:
                self._record_config_fetch(success=True)
                return self.config
            if response.status_code == 401:
                self._handle_auth_failure(response)
                return self.config
            response.raise_for_status()
            payload = response.json()
            remote_config = AgentSecConfig.model_validate(payload)
            self.update_config(remote_config)
            self._record_config_fetch(success=True)
        except Exception as exc:
            logger.warning("Failed to refresh config: %s", exc)
            self._record_config_fetch(success=False)
        return self.config

    def update_config(self, new_config: AgentSecConfig) -> None:
        with self._lock:
            self._config = new_config
        for callback in list(self._subscribers):
            try:
                callback(new_config)
            except Exception as exc:
                logger.debug("Config subscriber failed: %s", exc)

    def subscribe(self, callback: Callable[[AgentSecConfig], None]) -> None:
        self._subscribers.append(callback)

    def attach_runtime_state(self, runtime_state) -> None:
        self._runtime_state = runtime_state
        self._sync_token_state()

    def refresh_token(self, force: bool = False) -> Optional[str]:
        if force:
            self._token_manager.clear_cached_token()
            self._token = None
        self._token = self._registration.register_if_needed(self._config.sdk_version)
        self._sync_token_state()
        return self._token

    def invalidate_token(self, reason: str) -> None:
        logger.warning("AgentSec token invalidated: %s", reason)
        self._token = None
        if reason in {"token_expired", "token_revoked"}:
            self._token_manager.clear_cached_token()
        self._sync_token_state(reason)

    def start(self) -> None:
        if not self._poll_thread.is_alive():
            self._poll_thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._poll_thread.join(timeout=1.0)

    def _poll_loop(self) -> None:
        while not self._stop_event.is_set():
            self.fetch_config()
            self._stop_event.wait(self._config.config_poll_interval)

    def _record_config_fetch(self, success: bool) -> None:
        self._last_fetch_at = time.time()
        if self._runtime_state is not None:
            self._runtime_state.record_config_fetch(self._config.config_poll_interval, success=success)

    def _sync_token_state(self, reason: Optional[str] = None) -> None:
        status = reason or self._token_manager.token_status(self._token)
        claims = self._token_manager.parse_claims(self._token or "")
        with self._lock:
            if claims.get("tenant_id"):
                self._config.tenant_id = str(claims["tenant_id"])
            if claims.get("app_id"):
                self._config.app_id = str(claims["app_id"])
        if self._runtime_state is not None:
            self._runtime_state.set_token_status(status)

    def _handle_auth_failure(self, response: httpx.Response) -> None:
        reason = "token_invalid"
        try:
            payload = response.json()
            reason = str(payload.get("error") or payload.get("reason") or reason)
        except Exception:
            pass
        self.invalidate_token(reason)
        if reason == "token_expired":
            self.refresh_token(force=True)
