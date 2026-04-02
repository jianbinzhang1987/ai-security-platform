from __future__ import annotations

import os
import tempfile
from pathlib import Path


def local_token_path(pid: int | None = None) -> Path:
    current_pid = pid if pid is not None else os.getpid()
    return Path(tempfile.gettempdir()) / f"agentsec-{current_pid}.token"
