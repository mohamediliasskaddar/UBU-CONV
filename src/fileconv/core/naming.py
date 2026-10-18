"""Helpers for selecting output paths without replacing existing files."""

from __future__ import annotations

from pathlib import Path


def unique_path(path: Path) -> Path:
    """Return path if unused, otherwise append a numbered suffix before its extension."""
    if not path.exists():
        return path

    number = 1
    while True:
        candidate = path.with_name(f"{path.stem} ({number}){path.suffix}")
        if not candidate.exists():
            return candidate
        number += 1


def reserve_unique_path(path: Path) -> Path:
    """Atomically create and return an unused path, adding a number on collision."""
    number = 0
    while True:
        candidate = path if number == 0 else path.with_name(f"{path.stem} ({number}){path.suffix}")
        try:
            candidate.open("x").close()
            return candidate
        except FileExistsError:
            number += 1


def reserve_unique_directory(path: Path) -> Path:
    """Atomically create and return an unused directory, adding a number on collision."""
    number = 0
    while True:
        candidate = path if number == 0 else path.with_name(f"{path.name} ({number})")
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            number += 1
