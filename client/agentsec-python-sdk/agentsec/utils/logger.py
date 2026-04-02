from __future__ import annotations

import logging
import sys

_configured = False


def configure_logging() -> None:
    global _configured
    if _configured:
        return
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    root = logging.getLogger("agentsec")
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    root.propagate = False
    _configured = True


def get_logger(name: str = "") -> logging.Logger:
    configure_logging()
    logger_name = "agentsec" if not name else f"agentsec.{name}"
    return logging.getLogger(logger_name)
