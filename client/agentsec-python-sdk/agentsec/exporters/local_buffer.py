from __future__ import annotations

from collections import deque
from threading import Lock
from typing import Iterable, List


class LocalBuffer:
    def __init__(self, capacity: int = 10000):
        self.capacity = capacity
        self._buffer = deque(maxlen=capacity)
        self._lock = Lock()

    def append(self, item: object) -> None:
        with self._lock:
            self._buffer.append(item)

    def extend(self, items: Iterable[object]) -> None:
        with self._lock:
            for item in items:
                self._buffer.append(item)

    def drain(self) -> List[object]:
        with self._lock:
            items = list(self._buffer)
            self._buffer.clear()
            return items

    def snapshot(self) -> List[object]:
        with self._lock:
            return list(self._buffer)
