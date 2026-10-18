"""Desktop notifications for conversion results."""

from __future__ import annotations

import subprocess


def notify(message: str) -> None:
    """Display a desktop notification, raising an explicit error if unavailable."""
    try:
        subprocess.run(
            ["notify-send", "fileconv", message],
            check=True,
            timeout=5,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"Could not display desktop notification: {exc}") from exc
