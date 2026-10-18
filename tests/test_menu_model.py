import math

import pytest

from fileconv.gui.menu_model import (
    MORE_SENTINEL,
    build_ring,
    hit_test,
    paginate,
    slice_label_position,
)


@pytest.mark.parametrize("count", [1, 2, 4, 7, 8])
def test_slice_centers_hit_expected_index(count: int) -> None:
    layout = build_ring(
        [(f"item-{index}", index) for index in range(count)],
        inner_radius=20,
        outer_radius=100,
        center=(150, 120),
    )

    for index, ring_slice in enumerate(layout.slices):
        radius = 60
        angle = math.radians((ring_slice.start_angle + ring_slice.end_angle) / 2)
        x = layout.center_x + radius * math.cos(angle)
        y = layout.center_y + radius * math.sin(angle)
        assert hit_test(layout, x, y) == index


@pytest.mark.parametrize("count", [0, 9])
def test_build_ring_rejects_unsupported_item_count(count: int) -> None:
    with pytest.raises(ValueError, match="between 1 and 8"):
        build_ring(
            [(str(index), index) for index in range(count)],
            inner_radius=20,
            outer_radius=100,
            center=(0, 0),
        )


def test_hit_test_rejects_hole_outside_and_gap_points() -> None:
    layout = build_ring(
        [(f"item-{index}", index) for index in range(4)],
        inner_radius=20,
        outer_radius=100,
        center=(0, 0),
        gap_degrees=4,
    )

    assert hit_test(layout, 0, 0) is None
    assert hit_test(layout, 110, 0) is None

    boundary_angle = math.radians(layout.slices[0].end_angle)
    assert hit_test(
        layout,
        60 * math.cos(boundary_angle),
        60 * math.sin(boundary_angle),
    ) is None


def test_top_slice_handles_angles_across_atan2_wraparound() -> None:
    layout = build_ring(
        [(f"item-{index}", index) for index in range(4)],
        inner_radius=10,
        outer_radius=100,
        center=(0, 0),
        gap_degrees=0,
    )

    assert hit_test(layout, 0.01, -50) == 0
    assert hit_test(layout, -0.01, -50) == 0


@pytest.mark.parametrize(
    ("count", "expected_lengths", "more_pages"),
    [
        (3, [3], 0),
        (7, [7], 0),
        (8, [8, 1], 1),
        (15, [8, 8, 1], 2),
    ],
)
def test_paginate(
    count: int,
    expected_lengths: list[int],
    more_pages: int,
) -> None:
    items = [(f"item-{index}", index) for index in range(count)]

    pages = paginate(items)

    assert [len(page) for page in pages] == expected_lengths
    assert sum(payload is MORE_SENTINEL for page in pages for _, payload in page) == more_pages
    for page in pages[:-1]:
        assert page[-1] == ("More", MORE_SENTINEL)
    assert pages[-1][-1] == items[-1]


def test_paginate_requires_positive_page_size() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        paginate([("item", object())], per_page=0)


def test_slice_label_position_uses_middle_radius_and_angle() -> None:
    layout = build_ring(
        [("top", object()), ("right", object())],
        inner_radius=20,
        outer_radius=100,
        center=(30, 40),
    )

    assert slice_label_position(layout, 0) == pytest.approx((30, -20))
