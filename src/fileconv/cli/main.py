"""Typer command-line interface for fileconv."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

import fileconv.converters  # noqa: F401
from fileconv.core.errors import ConversionError
from fileconv.core.formats import normalize_extension
from fileconv.core.registry import all_converters, targets_for
from fileconv.core.runner import convert as run_conversion

app = typer.Typer(no_args_is_help=True, help="Convert files locally.")
OutputDirectory = Annotated[
    Path | None,
    typer.Option(
        "--out-dir",
        help="Directory for the converted file (defaults to the input directory).",
    ),
]


@app.command()
def targets(source: Path) -> None:
    """List available output formats for SOURCE."""
    extension = normalize_extension(source.suffix)
    available = targets_for(extension)
    if not available:
        typer.echo(f"No available conversions for .{extension}.")
        return
    for converter in available:
        typer.echo(f"{converter.dst}: {converter.label or converter.dst.upper()}")


@app.command("convert")
def convert_command(
    source: Path,
    destination: str,
    out_dir: OutputDirectory = None,
) -> None:
    """Convert SOURCE to DESTINATION format."""
    try:
        output = run_conversion(source, destination, out_dir)
    except ConversionError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(str(output))


@app.command()
def doctor() -> None:
    """Report required external tools and registered converters."""
    converters = all_converters()
    tools = sorted({converter.tool for converter in converters if converter.tool is not None})
    if not tools:
        typer.echo("External tools: none required by the registered converters.")
    else:
        for tool in tools:
            matching = [converter for converter in converters if converter.tool == tool]
            status = "available" if any(item.available() for item in matching) else "missing"
            typer.echo(f"{tool}: {status}")

    if converters:
        typer.echo("Converters:")
        for converter in converters:
            status = "available" if converter.available() else "unavailable"
            typer.echo(f"  {converter.src} -> {converter.dst}: {status}")
    else:
        typer.echo("Converters: none registered.")


if __name__ == "__main__":
    app()
