"""Registry of available input/output format conversions."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from fileconv.core.errors import ConversionError
from fileconv.core.formats import normalize_extension

ConversionFunction = Callable[[Path, Path], None]


@dataclass(frozen=True)
class Converter:
    """A conversion implementation for one source and destination format."""

    src: str
    dst: str
    fn: ConversionFunction
    tool: str | None = None
    label: str | None = None

    def available(self) -> bool:
        """Return whether any required external executable is installed."""
        return self.tool is None or shutil.which(self.tool) is not None


_CONVERTERS: list[Converter] = []


def register(
    src: str,
    dst: str,
    tool: str | None = None,
    label: str | None = None,
) -> Callable[[ConversionFunction], ConversionFunction]:
    """Register a converter function and return it unchanged."""

    def decorator(fn: ConversionFunction) -> ConversionFunction:
        converter = Converter(
            src=normalize_extension(src),
            dst=normalize_extension(dst),
            fn=fn,
            tool=tool,
            label=label,
        )
        if any(
            existing.src == converter.src and existing.dst == converter.dst
            for existing in _CONVERTERS
        ):
            raise RuntimeError(f"Converter already registered: {converter.src} -> {converter.dst}")
        _CONVERTERS.append(converter)
        return fn

    return decorator


def all_converters() -> tuple[Converter, ...]:
    """Return all registered converters, including those with missing tools."""
    return tuple(_CONVERTERS)


def targets_for(ext: str) -> list[Converter]:
    """Return available converters for a source extension."""
    source = normalize_extension(ext)
    return [
        converter for converter in _CONVERTERS if converter.src == source and converter.available()
    ]


def get(src: str, dst: str) -> Converter:
    """Return the registered converter or raise a useful error."""
    source = normalize_extension(src)
    destination = normalize_extension(dst)
    for converter in _CONVERTERS:
        if converter.src == source and converter.dst == destination:
            if not converter.available():
                raise ConversionError(
                    f"Cannot convert {source} to {destination}: "
                    f"required tool '{converter.tool}' was not found."
                )
            return converter
    raise ConversionError(f"No converter is registered for {source} to {destination}.")
