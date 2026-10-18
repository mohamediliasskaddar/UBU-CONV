"""Typer command-line interface for fileconv."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

import fileconv.converters  # noqa: F401
from fileconv.core.errors import ConversionError
from fileconv.core.formats import normalize_extension
from fileconv.core.registry import Converter, all_converters, targets_for
from fileconv.core.runner import convert as run_conversion
from fileconv.core.runner import merge_pdfs as run_merge

app = typer.Typer(no_args_is_help=True, help="Convert files locally.")
OutputDirectory = Annotated[
    Path | None,
    typer.Option(
        "--out-dir",
        help="Directory for the converted file (defaults to the input directory).",
    ),
]
MergeSources = Annotated[
    list[Path],
    typer.Argument(help="PDF files to merge, in the desired page order."),
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


@app.command("merge")
def merge_command(
    sources: MergeSources,
    out_dir: OutputDirectory = None,
) -> None:
    """Merge two or more PDF files into one PDF."""
    try:
        output = run_merge(sources, out_dir)
    except ConversionError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(str(output))


@app.command()
def doctor() -> None:
    """Report available conversions grouped by source format."""
    converters = all_converters()
    if not converters:
        typer.echo("Converters: none registered.")
        return

    grouped: dict[str, list[Converter]] = {}
    for converter in converters:
        grouped.setdefault(converter.src, []).append(converter)

    typer.echo("Conversions grouped by source format:")
    for source_extension, source_converters in sorted(grouped.items()):
        typer.echo(f"{source_extension}:")
        for converter in sorted(source_converters, key=lambda item: item.dst):
            if converter.available():
                status = "available"
            elif converter.tool is not None:
                status = f"unavailable (missing tool: {converter.tool})"
            else:
                status = "unavailable"
            tool = f" [{converter.tool}]" if converter.tool else ""
            typer.echo(f"  {converter.dst}{tool}: {status}")


if __name__ == "__main__":
    app()
