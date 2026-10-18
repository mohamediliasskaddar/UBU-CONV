"""Background conversion jobs for the radial menu."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal

from fileconv.core.errors import ConversionError
from fileconv.core.runner import convert, merge_pdfs


class WorkerSignals(QObject):
    """Signals emitted when a conversion job finishes."""

    succeeded = Signal(object)
    failed = Signal(str)


class ConversionWorker(QRunnable):
    """Run a conversion without blocking the GUI thread."""

    def __init__(
        self,
        sources: list[Path],
        destination: str | None = None,
        merge: bool = False,
    ) -> None:
        super().__init__()
        self.sources = sources
        self.destination = destination
        self.merge = merge
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            if self.merge:
                output = merge_pdfs(self.sources)
            elif self.destination is not None:
                output = convert(self.sources[0], self.destination)
            else:
                raise ConversionError("No conversion target was selected.")
        except ConversionError as exc:
            self.signals.failed.emit(str(exc))
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            message = str(exc) or exc.__class__.__name__
            self.signals.failed.emit(f"Conversion failed: {message}")
        else:
            self.signals.succeeded.emit(output)
