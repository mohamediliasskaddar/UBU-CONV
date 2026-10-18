"""Application entry point for the fullscreen radial menu."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

import fileconv.converters  # noqa: F401
from fileconv.gui.radial_menu import RadialMenu


def main() -> int:
    """Launch the menu, optionally preloading one or more file paths."""
    files = [Path(argument).expanduser() for argument in sys.argv[1:]]
    application = QApplication(sys.argv[:1])
    menu = RadialMenu(files or None)
    menu.showFullScreen()
    menu.activateWindow()
    menu.setFocus()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
