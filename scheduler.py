"""Scheduling utilities for QueueBreaker.

This module keeps the autodialer idle until the configured burst window
starts.  It supports two modes:

* every_hour  - the window repeats every hour of the day.
* specific_hours - only the provided hours (24h clock) are eligible.

The functions keep sleeping in small chunks so that the emergency stop
hotkey can still interrupt the process immediately.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import Iterable, Optional

from utils import sleep_with_stop


@dataclass
class BurstWindow:
    """Simple value object used by :class:`BurstScheduler`."""

    start_minute: int
    end_minute: int

    def contains(self, minute: int) -> bool:
        """Return ``True`` if ``minute`` is inside the burst window."""

        minute %= 60
        start = self.start_minute % 60
        end = self.end_minute % 60

        if start == end:
            # Whole hour is considered active.
            return True

        if start < end:
            return start <= minute <= end
        return minute >= start or minute <= end


class BurstScheduler:
    """Coordinate the burst dialing window.

    Parameters
    ----------
    start_minute, end_minute:
        Minute marks that define the dialing burst.  If ``start`` is greater
        than ``end`` the window wraps around the top of the hour.  A typical
        EDD configuration is 58-02.
    schedule_mode:
        ``"every_hour"`` or ``"specific_hours"``.  In the latter case
        ``active_hours`` must contain at least one 24h based hour integer.
    """

    def __init__(
        self,
        start_minute: int,
        end_minute: int,
        schedule_mode: str = "every_hour",
        active_hours: Optional[Iterable[int]] = None,
    ) -> None:
        self.window = BurstWindow(start_minute, end_minute)
        self.schedule_mode = (schedule_mode or "every_hour").lower()
        self.active_hours = {int(h) for h in (active_hours or [])}

    # ------------------------------------------------------------------
    # public helpers
    # ------------------------------------------------------------------
    def wait_for_window(self, stop_event=None) -> None:
        """Block until the scheduler is inside an active burst window."""

        while True:
            if stop_event and stop_event.is_set():
                return
            now = datetime.now()
            if self._hour_is_active(now) and self.window.contains(now.minute):
                return

            sleep_for = self._seconds_until_next_window(now)
            logging.debug("Next burst window in %.1f seconds", sleep_for)
            sleep_with_stop(sleep_for, stop_event)

    def sleep_between_attempts(self, delay_seconds: float, stop_event=None) -> None:
        sleep_with_stop(max(delay_seconds, 0.1), stop_event)

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------
    def _hour_is_active(self, ts: datetime) -> bool:
        if self.schedule_mode != "specific_hours":
            return True
        return True if not self.active_hours else ts.hour in self.active_hours

    def _seconds_until_next_window(self, now: datetime) -> float:
        candidate = now.replace(second=0, microsecond=0)
        # Search up to two days ahead which covers every possible combination.
        for _ in range(1, 60 * 24 * 2):
            candidate += timedelta(minutes=1)
            if self._hour_is_active(candidate) and self.window.contains(candidate.minute):
                delta = candidate - now
                return max(delta.total_seconds(), 1.0)
        # Should never happen but keeps us safe.
        return 60.0
