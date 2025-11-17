"""Utility helpers for QueueBreaker."""
from __future__ import annotations

import time
from typing import Optional


def sleep_with_stop(seconds: float, stop_event: Optional[object] = None) -> None:
    """Sleep up to ``seconds`` seconds while honoring ``stop_event``."""

    end = time.time() + max(seconds, 0)
    while time.time() < end and not (stop_event and stop_event.is_set()):
        time.sleep(min(0.5, max(0, end - time.time())))
