"""Phone Link UI automation helpers for QueueBreaker."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging
import time
from typing import Optional

try:  # pragma: no cover - optional dependency in CI
    import pyautogui as pag
    pag.FAILSAFE = False
except Exception as exc:  # pragma: no cover - pyautogui not available on linux CI
    pag = None
    _PYAUTOGUI_ERROR = exc
else:
    _PYAUTOGUI_ERROR = None

try:  # pragma: no cover - optional dependency in CI
    from pywinauto import Application
except Exception as exc:  # pragma: no cover
    Application = None
    _PYWINAUTO_ERROR = exc
else:
    _PYWINAUTO_ERROR = None


@dataclass
class DialResult:
    duration_seconds: float
    termination_reason: str
    window_state: Optional[str]


class Dialer:
    """Wrap Windows Phone Link automation routines."""

    def __init__(self, settings: dict) -> None:
        self.phone_link_title = settings.get("phone_link_title", "Phone Link")
        self.dial_pad_shortcut = settings.get(
            "dial_pad_shortcut", ["ctrl", "shift", "d"]
        )
        self.call_button_shortcut = settings.get(
            "call_button_shortcut", ["enter"]
        )
        self.hangup_shortcut = settings.get("hangup_shortcut", ["esc"])
        self._app: Optional[Application] = None
        self._warn_if_missing_dependencies()

    # ------------------------------------------------------------------
    def execute_call(self, phone_number: str, observation_delay: float, stop_event=None) -> DialResult:
        """Dial ``phone_number`` and return meta information."""

        start_time = datetime.now()
        self.focus_phone_link()
        self.open_dial_pad()
        self.enter_phone_number(phone_number)
        self.trigger_call()
        self._sleep_with_stop(observation_delay, stop_event)
        termination_reason = "unknown"
        try:
            termination_reason = self.detect_call_outcome()
        finally:
            self.hang_up()
        duration = (datetime.now() - start_time).total_seconds()
        window_state = self.capture_window_state()
        return DialResult(duration, termination_reason, window_state)

    # ------------------------------------------------------------------
    def focus_phone_link(self) -> None:
        """Bring the Phone Link window to the foreground."""

        if Application is not None:
            try:
                if self._app is None:
                    self._app = Application(backend="uia").connect(
                        title_re=self.phone_link_title
                    )
                window = self._app.top_window()
                window.set_focus()
                logging.debug("Focused Phone Link window via pywinauto")
                return
            except Exception as exc:  # pragma: no cover - UI automation is Windows-only
                logging.debug("pywinauto focus failed: %s", exc)

        if pag is None:
            raise RuntimeError(
                "PyAutoGUI is required to focus Phone Link. Original import error: %s"
                % _PYAUTOGUI_ERROR
            )

        # Fallback: Windows Search -> Phone Link.
        pag.hotkey("win")
        time.sleep(0.4)
        pag.write(self.phone_link_title)
        pag.press("enter")
        logging.debug("Focused Phone Link using Windows Search")

    def open_dial_pad(self) -> None:
        if pag is None:
            return
        time.sleep(0.3)
        self._send_shortcut(self.dial_pad_shortcut)
        time.sleep(0.3)

    def enter_phone_number(self, phone_number: str) -> None:
        if pag is None:
            return
        pag.hotkey("ctrl", "a")
        pag.press("backspace")
        pag.write(phone_number, interval=0.05)
        logging.debug("Entered phone number %s", phone_number)

    def trigger_call(self) -> None:
        if Application is not None and self._app is not None:
            try:
                window = self._app.top_window()
                call_button = window.child_window(title_re=".*call.*", control_type="Button")
                call_button.click_input()
                logging.debug("Clicked Call button via pywinauto")
                return
            except Exception as exc:  # pragma: no cover - Windows only
                logging.debug("pywinauto call button fallback: %s", exc)

        if pag is None:
            raise RuntimeError(
                "PyAutoGUI is required for keyboard automation. Import error: %s"
                % _PYAUTOGUI_ERROR
            )
        self._send_shortcut(self.call_button_shortcut)
        logging.debug("Triggered call via keyboard shortcut")

    def hang_up(self) -> None:
        if Application is not None and self._app is not None:
            try:
                window = self._app.top_window()
                hangup_button = window.child_window(title_re=".*hang.*|.*end.*", control_type="Button")
                hangup_button.click_input()
                logging.debug("Clicked Hang Up button via pywinauto")
                return
            except Exception as exc:  # pragma: no cover - Windows only
                logging.debug("pywinauto hang-up fallback: %s", exc)

        if pag is None:
            return
        self._send_shortcut(self.hangup_shortcut)
        logging.debug("Sent hang-up shortcut")

    def detect_call_outcome(self) -> str:
        """Placeholder for future OCR/IVR detection."""

        # Real call-state analysis is highly device specific.  Returning
        # "unknown" keeps the logging consistent while still giving users a
        # clear spot to plug in custom detection logic.
        return "unknown"

    def capture_window_state(self) -> Optional[str]:
        if Application is None or self._app is None:
            return None
        try:
            window = self._app.top_window()
            element = window.element_info
            return f"{element.name} | {element.control_type} | Visible={window.is_visible()}"
        except Exception:  # pragma: no cover - depends on Windows UIA
            return None

    def _warn_if_missing_dependencies(self) -> None:
        if pag is None:
            logging.warning(
                "PyAutoGUI is not available. Keyboard/mouse automation will fail: %s",
                _PYAUTOGUI_ERROR,
            )
        if Application is None:
            logging.debug("pywinauto not available: %s", _PYWINAUTO_ERROR)

    @staticmethod
    def _sleep_with_stop(seconds: float, stop_event=None) -> None:
        seconds = max(seconds, 0)
        end_time = time.time() + seconds
        while time.time() < end_time:
            if stop_event and stop_event.is_set():
                break
            time.sleep(min(0.5, max(0, end_time - time.time())))

    @staticmethod
    def _send_shortcut(keys) -> None:
        if pag is None:
            return
        keys = list(keys or [])
        if not keys:
            return
        for key in keys:
            pag.keyDown(key)
        for key in reversed(keys):
            pag.keyUp(key)
