"""QueueBreaker entry point."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from datetime import datetime
import threading
from typing import Any, Dict

try:  # pragma: no cover - keyboard is Windows-only
    import keyboard
except Exception as exc:  # pragma: no cover
    keyboard = None
    _KEYBOARD_ERROR = exc
else:
    _KEYBOARD_ERROR = None

from dialer import Dialer
from scheduler import BurstScheduler

SETTINGS_PATH = Path("settings.json")
ATTEMPT_LOG = Path("attempt_log.txt")
DEFAULT_SETTINGS: Dict[str, Any] = {
    "phone_number": "1-800-480-3287",
    "start_minute": 58,
    "end_minute": 2,
    "delay_between_attempts": 7,
    "max_attempts": 40,
    "call_observation_delay": 8,
    "schedule_mode": "every_hour",
    "active_hours": [],
    "phone_link_title": "Phone Link",
    "number_field_click": None,
}


def load_settings() -> Dict[str, Any]:
    if not SETTINGS_PATH.exists():
        SETTINGS_PATH.write_text(json.dumps(DEFAULT_SETTINGS, indent=2))
        logging.info("Created default settings.json")
        return dict(DEFAULT_SETTINGS)
    user_settings = json.loads(SETTINGS_PATH.read_text())
    merged = dict(DEFAULT_SETTINGS)
    merged |= user_settings
    return merged


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def register_hotkey(stop_event: threading.Event) -> None:
    if keyboard is None:
        logging.warning("keyboard module not available: %s", _KEYBOARD_ERROR)
        return

    def _stop() -> None:
        logging.warning("Emergency stop hotkey pressed. Exiting dial loop.")
        stop_event.set()

    keyboard.add_hotkey("f12", _stop)
    logging.info("Emergency stop armed: press F12 to halt dialing")


def append_attempt_log(attempt_no: int, result) -> None:
    ATTEMPT_LOG.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    window_state = result.window_state or "n/a"
    line = (
        f"{timestamp} | Attempt {attempt_no:03d} | Duration {result.duration_seconds:.1f}s | "
        f"Termination {result.termination_reason} | Window {window_state}\n"
    )
    with ATTEMPT_LOG.open("a", encoding="utf-8") as handle:
        handle.write(line)


def main() -> None:
    setup_logging()
    settings = load_settings()
    scheduler = BurstScheduler(
        start_minute=settings["start_minute"],
        end_minute=settings["end_minute"],
        schedule_mode=settings.get("schedule_mode", "every_hour"),
        active_hours=settings.get("active_hours", []),
    )
    dialer = Dialer(settings)
    stop_event = threading.Event()
    register_hotkey(stop_event)

    phone_number = settings["phone_number"]
    max_attempts = int(settings["max_attempts"])
    delay_between_attempts = float(settings["delay_between_attempts"])
    observation_delay = float(settings["call_observation_delay"])

    logging.info("Starting QueueBreaker for %s (max attempts: %s)", phone_number, max_attempts)

    attempt = 0
    while attempt < max_attempts and not stop_event.is_set():
        scheduler.wait_for_window(stop_event)
        if stop_event.is_set():
            break

        attempt += 1
        logging.info("Attempt %s/%s", attempt, max_attempts)
        result = dialer.execute_call(phone_number, observation_delay, stop_event)
        append_attempt_log(attempt, result)
        logging.info(
            "Completed attempt %s: %.1fs (%s)",
            attempt,
            result.duration_seconds,
            result.termination_reason,
        )
        scheduler.sleep_between_attempts(delay_between_attempts, stop_event)

    logging.info("QueueBreaker finished after %s attempts", attempt)


if __name__ == "__main__":
    main()
