"""Wayland-compatible fullscreen radial file-conversion menu."""

from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import QMimeData, QPointF, Qt, QThreadPool, QTimer
from PySide6.QtGui import (
    QColor,
    QDragEnterEvent,
    QDragLeaveEvent,
    QDragMoveEvent,
    QDropEvent,
    QFont,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
    QResizeEvent,
)
from PySide6.QtWidgets import QWidget

from fileconv.core.formats import normalize_extension
from fileconv.core.registry import Converter, targets_for
from fileconv.gui.menu_model import (
    MORE_SENTINEL,
    RingLayout,
    build_ring,
    hit_test,
    paginate,
    slice_label_position,
)
from fileconv.gui.notify import notify
from fileconv.gui.worker import ConversionWorker

_COLORS = (
    QColor("#4169e1"),
    QColor("#168a76"),
    QColor("#ca7a16"),
    QColor("#a34bb8"),
    QColor("#c34d59"),
    QColor("#397aaf"),
    QColor("#658b35"),
    QColor("#8b6744"),
)
_MERGE_SENTINEL = object()


class RadialMenu(QWidget):
    """Fullscreen overlay that accepts files and presents conversion targets."""

    def __init__(self, files: list[Path] | None = None) -> None:
        super().__init__(None, Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.files: list[Path] = []
        self.pages: list[list[tuple[str, object]]] = []
        self.page_index = 0
        self.layout: RingLayout | None = None
        self.center_label = "Drop a file"
        self.center_detail = ""
        self.hovered_index: int | None = None
        self.running_index: int | None = None
        self._dismiss_only = False
        self._pulse = 0.0
        self._pulse_direction = 1

        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(30)
        self._pulse_timer.timeout.connect(self._advance_pulse)

        if files:
            self._set_files(files)

    def _local_files(self, mime_data: QMimeData) -> list[Path]:
        urls = mime_data.urls()
        return [Path(url.toLocalFile()) for url in urls if url.isLocalFile()]

    def _set_files(self, files: list[Path]) -> bool:
        self.files = files
        if not files:
            self._clear_choices()
            return False

        first = files[0]
        if not first.is_file():
            self.pages = []
            self.layout = None
            self.center_label = f"File not found: {first.name}"
            self.center_detail = ""
            self.update()
            return False

        extension = normalize_extension(first.suffix)
        if (
            all(path.is_file() and normalize_extension(path.suffix) == "pdf" for path in files)
            and len(files) >= 2
        ):
            converters = targets_for("pdf")
            choices: list[tuple[str, object]] = [
                (converter.label or converter.dst.upper(), converter) for converter in converters
            ]
            choices.append(("Merge", _MERGE_SENTINEL))
        else:
            converters = targets_for(extension)
            choices = [
                (converter.label or converter.dst.upper(), converter) for converter in converters
            ]

        if not choices:
            self.pages = []
            self.layout = None
            self.center_label = "No conversion available"
            self.center_detail = ""
            self.update()
            return False

        self.pages = paginate(choices, per_page=7)
        self.page_index = 0
        self.center_label = first.name if len(files) == 1 else f"{len(files)} files"
        self.center_detail = "Choose a format"
        self._rebuild_layout()
        return True

    def _clear_choices(self) -> None:
        self.files = []
        self.pages = []
        self.page_index = 0
        self.layout = None
        self.hovered_index = None
        self.center_label = "Drop a file"
        self.center_detail = ""
        self.update()

    def _rebuild_layout(self) -> None:
        if not self.pages:
            self.layout = None
            self.update()
            return

        width = self.width() or self.screen().geometry().width()
        height = self.height() or self.screen().geometry().height()
        outer_radius = min(250.0, min(width, height) * 0.42)
        inner_radius = min(95.0, outer_radius * 0.38)
        self.layout = build_ring(
            self.pages[self.page_index],
            inner_radius=inner_radius,
            outer_radius=outer_radius,
            center=(width / 2, height / 2),
        )
        self.hovered_index = None
        self.update()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self.pages:
            self._rebuild_layout()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 165))

        if self.layout is not None:
            self._paint_ring(painter, self.layout)

        center = QPointF(self.width() / 2, self.height() / 2)
        painter.setPen(QColor("#ffffff"))
        center_font = QFont()
        center_font.setPointSize(16)
        center_font.setBold(True)
        painter.setFont(center_font)
        center_rect = painter.fontMetrics().boundingRect(
            int(center.x() - 150),
            int(center.y() - 50),
            300,
            100,
            Qt.AlignmentFlag.AlignCenter,
            self.center_label,
        )
        painter.drawText(
            center_rect,
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            self.center_label,
        )

        if self.center_detail:
            detail_font = QFont()
            detail_font.setPointSize(10)
            painter.setFont(detail_font)
            painter.setPen(QColor("#dddddd"))
            painter.drawText(
                int(center.x() - 150),
                int(center.y() + 30),
                300,
                30,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                self.center_detail,
            )
        painter.end()

    def _paint_ring(self, painter: QPainter, layout: RingLayout) -> None:
        for ring_slice in layout.slices:
            color = _COLORS[ring_slice.index % len(_COLORS)]
            if ring_slice.index == self.hovered_index:
                color = color.lighter(135)
            if ring_slice.index == self.running_index:
                color = color.lighter(100 + int(self._pulse * 35))

            painter.setBrush(color)
            painter.setPen(QPen(QColor(255, 255, 255, 220), 2))
            painter.drawPath(self._slice_path(layout, ring_slice.start_angle, ring_slice.end_angle))

            label_x, label_y = slice_label_position(layout, ring_slice.index)
            painter.setPen(QColor("#ffffff"))
            font = QFont()
            font.setPointSize(11)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(
                int(label_x - 70),
                int(label_y - 18),
                140,
                36,
                Qt.AlignmentFlag.AlignCenter,
                ring_slice.label,
            )

    @staticmethod
    def _slice_path(layout: RingLayout, start_angle: float, end_angle: float) -> QPainterPath:
        path = QPainterPath()
        center = QPointF(layout.center_x, layout.center_y)
        segment_count = max(2, math.ceil((end_angle - start_angle) / 3))
        outer_points = [
            RadialMenu._point(center, layout.outer_radius, angle)
            for angle in (
                start_angle + (end_angle - start_angle) * step / segment_count
                for step in range(segment_count + 1)
            )
        ]
        inner_points = [
            RadialMenu._point(center, layout.inner_radius, angle)
            for angle in (
                end_angle - (end_angle - start_angle) * step / segment_count
                for step in range(segment_count + 1)
            )
        ]
        path.moveTo(outer_points[0])
        for point in (*outer_points[1:], *inner_points):
            path.lineTo(point)
        path.closeSubpath()
        return path

    @staticmethod
    def _point(center: QPointF, radius: float, angle: float) -> QPointF:
        radians = math.radians(angle)
        return QPointF(
            center.x() + radius * math.cos(radians),
            center.y() + radius * math.sin(radians),
        )

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if self.running_index is not None or self._dismiss_only:
            event.ignore()
            return
        files = self._local_files(event.mimeData())
        if self._set_files(files):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if self.layout is None or self._dismiss_only:
            event.ignore()
            return
        position = event.position()
        index = hit_test(self.layout, position.x(), position.y())
        if index != self.hovered_index:
            self.hovered_index = index
            self.update()
        event.acceptProposedAction()

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        if self.hovered_index is not None:
            self.hovered_index = None
            self.update()
        event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        if self.layout is None or self._dismiss_only:
            event.ignore()
            return
        position = event.position()
        index = hit_test(self.layout, position.x(), position.y())
        if index is None:
            event.ignore()
            return
        self._activate_slice(index)
        event.acceptProposedAction()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if (
            event.button() != Qt.MouseButton.LeftButton
            or self.running_index is not None
            or self._dismiss_only
        ):
            event.ignore()
            return
        if self.layout is None:
            self.close()
            return

        position = event.position()
        index = hit_test(self.layout, position.x(), position.y())
        if index is None:
            self.close()
        else:
            self._activate_slice(index)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            return
        super().keyPressEvent(event)

    def _activate_slice(self, index: int) -> None:
        if self.layout is None or self.running_index is not None:
            return
        ring_slice = self.layout.slices[index]
        if ring_slice.payload is MORE_SENTINEL:
            if self.page_index + 1 < len(self.pages):
                self.page_index += 1
                self.center_detail = "Choose a format"
                self._rebuild_layout()
            return
        if ring_slice.payload is _MERGE_SENTINEL:
            self._start_worker(index)
            return

        converter = ring_slice.payload
        if not isinstance(converter, Converter):
            self.center_label = "Invalid conversion target"
            self.center_detail = "Press Esc to close"
            self.update()
            return

        self._start_worker(index, destination=converter.dst)

    def _start_worker(self, index: int, destination: str | None = None) -> None:
        self.running_index = index
        self._dismiss_only = False
        self.hovered_index = None
        self.center_label = "Converting..."
        self.center_detail = ""
        self._pulse_timer.start()
        self.update()

        is_merge = destination is None
        worker = ConversionWorker(self.files, destination=destination, merge=is_merge)
        worker.signals.succeeded.connect(self._conversion_succeeded)
        worker.signals.failed.connect(self._conversion_failed)
        self._worker = worker
        QThreadPool.globalInstance().start(worker)

    def _conversion_succeeded(self, output: object) -> None:
        self._pulse_timer.stop()
        result = Path(output)
        try:
            notify(result.name)
        except RuntimeError as exc:
            self.center_label = str(exc)
            self.center_detail = "Press Esc to close"
            self.running_index = None
            self._dismiss_only = True
            self.update()
            return
        self.close()

    def _conversion_failed(self, message: str) -> None:
        self._pulse_timer.stop()
        self.running_index = None
        self._dismiss_only = True
        self.center_label = message
        self.center_detail = "Press Esc to close"
        try:
            notify(message)
        except RuntimeError as exc:
            self.center_detail = f"Notification failed: {exc}"
        self.update()

    def _advance_pulse(self) -> None:
        self._pulse += self._pulse_direction * 0.08
        if self._pulse >= 1.0:
            self._pulse = 1.0
            self._pulse_direction = -1
        elif self._pulse <= 0.0:
            self._pulse = 0.0
            self._pulse_direction = 1
        self.update()
