"""Conversion orchestration."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from fileconv.core.errors import ConversionError
from fileconv.core.formats import normalize_extension
from fileconv.core.naming import reserve_unique_directory, reserve_unique_path
from fileconv.core.registry import get


def convert(src: Path, dst_ext: str, out_dir: Path | None = None) -> Path:
    """Convert a file and return its uniquely named output path."""
    source = Path(src)
    if not source.is_file():
        raise ConversionError(f"Input file does not exist or is not a file: {source}")

    source_ext = normalize_extension(source.suffix)
    destination_ext = normalize_extension(dst_ext)
    converter = get(source_ext, destination_ext)

    output_dir = Path(out_dir) if out_dir is not None else source.parent
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        if converter.output_is_directory:
            output = reserve_unique_directory(output_dir / f"{source.stem}_pages")
        else:
            output = reserve_unique_path(output_dir / f"{source.stem}.{destination_ext}")
    except OSError as exc:
        raise ConversionError(f"Could not create an output path in {output_dir}: {exc}") from exc

    try:
        converter.fn(source, output)
        if converter.output_is_directory:
            if not output.is_dir() or not any(output.iterdir()):
                raise ConversionError(f"Converter did not produce output files in: {output}")
        elif not output.is_file() or output.stat().st_size == 0:
            raise ConversionError(f"Converter did not produce a non-empty output file: {output}")
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        if converter.output_is_directory:
            shutil.rmtree(output, ignore_errors=True)
        else:
            output.unlink(missing_ok=True)
        raise ConversionError(
            f"Could not convert {source.name} to {destination_ext}: {exc}"
        ) from exc
    except ConversionError:
        if converter.output_is_directory:
            shutil.rmtree(output, ignore_errors=True)
        else:
            output.unlink(missing_ok=True)
        raise
    return output


def merge_pdfs(sources: list[Path], out_dir: Path | None = None) -> Path:
    """Merge two or more PDF files into a uniquely named PDF."""
    from fileconv.converters.pdf_ops import merge_pdfs as merge

    inputs = [Path(source) for source in sources]
    if len(inputs) < 2:
        raise ConversionError("At least two PDF files are required for merging.")
    for source in inputs:
        if not source.is_file():
            raise ConversionError(f"Input file does not exist or is not a file: {source}")
        if normalize_extension(source.suffix) != "pdf":
            raise ConversionError(f"Input file is not a PDF: {source}")

    output_dir = Path(out_dir) if out_dir is not None else inputs[0].parent
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        output = reserve_unique_path(output_dir / "merged.pdf")
    except OSError as exc:
        raise ConversionError(f"Could not create the merged PDF in {output_dir}: {exc}") from exc

    try:
        merge(inputs, output)
    except ConversionError:
        output.unlink(missing_ok=True)
        raise
    except (OSError, ValueError, RuntimeError) as exc:
        output.unlink(missing_ok=True)
        raise ConversionError(f"Could not merge PDF files: {exc}") from exc

    if not output.is_file() or output.stat().st_size == 0:
        output.unlink(missing_ok=True)
        raise ConversionError("PDF merger did not produce a non-empty output file.")
    return output
