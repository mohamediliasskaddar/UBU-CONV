"""Pure-Python geometry and pagination for radial menu layouts."""

from __future__ import annotations

import math
from dataclasses import dataclass

Item = tuple[str, object]
MORE_SENTINEL = object()


@dataclass(frozen=True)
class Slice:
    """One selectable angular sector in a radial menu."""

    index: int
    label: str
    start_angle: float
    end_angle: float
    payload: object


@dataclass(frozen=True)
class RingLayout:
    """Ring geometry and its selectable slices."""

    center_x: float
    center_y: float
    inner_radius: float
    outer_radius: float
    slices: tuple[Slice, ...]


def build_ring(
    items: list[Item],
    inner_radius: float,
    outer_radius: float,
    center: tuple[float, float],
    gap_degrees: float = 3.0,
    start_at_top: bool = True,
) -> RingLayout:
    """Divide a ring evenly, placing its first slice at the top by default.

    Angles are degrees measured clockwise from the positive x-axis, matching
    screen coordinates where y increases downward.
    """
    if not 1 <= len(items) <= 8:
        raise ValueError("A ring must contain between 1 and 8 items.")
    if inner_radius < 0 or outer_radius <= inner_radius:
        raise ValueError("Radii must satisfy 0 <= inner_radius < outer_radius.")
    if not 0 <= gap_degrees:
        raise ValueError("gap_degrees must be non-negative.")

    step = 360.0 / len(items)
    if gap_degrees >= step:
        raise ValueError("gap_degrees must be smaller than each slice.")

    offset = -90.0 if start_at_top else 0.0
    slice_width = step - gap_degrees
    slices = tuple(
        Slice(
            index=index,
            label=label,
            start_angle=offset + index * step - slice_width / 2,
            end_angle=offset + index * step + slice_width / 2,
            payload=payload,
        )
        for index, (label, payload) in enumerate(items)
    )
    return RingLayout(
        center_x=float(center[0]),
        center_y=float(center[1]),
        inner_radius=float(inner_radius),
        outer_radius=float(outer_radius),
        slices=slices,
    )


def hit_test(layout: RingLayout, x: float, y: float) -> int | None:
    """Return the slice containing a point, excluding the hole and angular gaps."""
    dx = x - layout.center_x
    dy = y - layout.center_y
    radius = math.hypot(dx, dy)
    if radius < layout.inner_radius or radius > layout.outer_radius:
        return None

    screen_angle = math.degrees(math.atan2(dy, dx))
    for ring_slice in layout.slices:
        center_angle = (ring_slice.start_angle + ring_slice.end_angle) / 2
        half_width = (ring_slice.end_angle - ring_slice.start_angle) / 2
        delta = (screen_angle - center_angle + 180.0) % 360.0 - 180.0
        if abs(delta) < half_width:
            return ring_slice.index
    return None


def paginate(items: list[Item], per_page: int = 7) -> list[list[Item]]:
    """Split items into pages, adding a More sentinel to each non-final page."""
    if per_page < 1:
        raise ValueError("per_page must be at least 1.")
    pages = [items[index : index + per_page] for index in range(0, len(items), per_page)]
    for page in pages[:-1]:
        page.append(("More", MORE_SENTINEL))
    return pages


def slice_label_position(layout: RingLayout, index: int) -> tuple[float, float]:
    """Return the middle-radius point at the center angle of a slice."""
    try:
        ring_slice = layout.slices[index]
    except IndexError as exc:
        raise ValueError(f"Slice index out of range: {index}") from exc
    if ring_slice.index != index:
        raise ValueError(f"Slice index out of range: {index}")

    middle_radius = (layout.inner_radius + layout.outer_radius) / 2
    middle_angle = math.radians((ring_slice.start_angle + ring_slice.end_angle) / 2)
    return (
        layout.center_x + middle_radius * math.cos(middle_angle),
        layout.center_y + middle_radius * math.sin(middle_angle),
    )
