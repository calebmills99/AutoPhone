# QueueBreaker (AutoPhone fork)

QueueBreaker is a Windows → Phone Link autodialer that repeatedly calls the
EDD customer support line (or any configured number) from an Android phone.
It is tailored for burst dialing during the final minutes of every hour so you
can pierce the EDD queue while it resets.

## Features

- **Burst windows** – dial between a configurable start/end minute (default
  58 → 02) with per-attempt delays between 5–8 seconds.
- **Two scheduling modes** – hit the window every hour, or only during the
  24-hour timestamps you list in the configuration file.
- **Phone Link automation** – PyAutoGUI/pywinauto scripts focus the Phone Link
  window, enter the phone number, trigger the call, wait a few seconds, and
  hang up.
- **Emergency stop** – press `F12` at any time to abort the loop.
- **Attempt logging** – `attempt_log.txt` records the attempt number,
  timestamp, call duration, termination reason, and a snapshot of the Phone
  Link window state.

## Requirements

- Windows 10/11 with [Phone Link](https://support.microsoft.com/phone-link)
  signed in and paired with your Android device.
- Python 3.9+ (64-bit is recommended).
- The ability to install the dependencies listed in `requirements.txt`
  (`pip install -r requirements.txt`).
- Optional but recommended: pywinauto-friendly accessibility settings enabled
  for the Phone Link desktop application.

## Installation

1. Clone this repository.
2. Install dependencies:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Pair your Android device with Phone Link and verify that you can place a
   manual call through the desktop UI.

## Configuration (`settings.json`)

The project ships with a ready-to-go `settings.json`.  Edit it to fit your
workflow:

```json
{
  "phone_number": "1-800-480-3287",
  "start_minute": 58,
  "end_minute": 2,
  "delay_between_attempts": 7,
  "max_attempts": 40,
  "call_observation_delay": 8,
  "schedule_mode": "every_hour",
  "active_hours": [],
  "phone_link_title": "Phone Link",
  "dial_pad_shortcut": ["ctrl", "shift", "d"],
  "call_button_shortcut": ["enter"],
  "hangup_shortcut": ["esc"]
}
```

- **start_minute / end_minute** – define the burst window in minutes.  If the
  start minute is greater than the end minute the window wraps across the top
  of the hour (58 → 02).
- **schedule_mode** – `every_hour` (default) replays the window once per hour.
  Use `specific_hours` with `active_hours` (list of 24h integers) for a
  restricted schedule.
- **delay_between_attempts** – seconds to wait between attempts during the
  window.  Use 5–8 seconds to match the EDD cadence.
- **call_observation_delay** – seconds to wait after pressing “Call” before
  hanging up.  Increase this if you want to monitor the call longer.
- ***_shortcut** – override these if you customized Phone Link’s keyboard
  shortcuts or use a different language layout.

## Running QueueBreaker

```powershell
python queuebreaker.py
```

- QueueBreaker waits until the burst window opens, then loops until the window
  closes, the emergency stop hotkey fires, or `max_attempts` is reached.
- Each attempt is written to `attempt_log.txt` alongside the console output so
  you can review when a call pierced the queue.
- Press **F12** for an immediate, safe shutdown.

## Logging and extension points

- All runtime logs are printed to the console and appended to
  `attempt_log.txt`.
- `dialer.detect_call_outcome()` is a stub where you can integrate OCR,
  waveform, or IVR prompts to automatically classify busy, voicemail, or human
  responses.
- `dialer.capture_window_state()` captures pywinauto metadata when available so
  you can inspect Phone Link’s UI state after each attempt.

## Development notes

- Source code entry point: `queuebreaker.py`.
- Scheduling utilities: `scheduler.py`.
- Phone Link automation helpers: `dialer.py`.
- Default config + attempt logs live in the repository root for easy editing.

Run the lightweight syntax check before committing changes:
```powershell
python -m compileall queuebreaker.py dialer.py scheduler.py
```

> **Security reminder:** The automation scripts can send keystrokes and mouse
> clicks.  Close unrelated apps and verify every shortcut before running the
> dialer on your daily driver.
