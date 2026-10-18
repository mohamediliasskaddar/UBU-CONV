"""LibreOffice headless conversions for office document formats."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from fileconv.core.registry import register


def _office_to_pdf(source: Path, output: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="fileconv-office-") as temporary:
        temporary_path = Path(temporary)
        profile = temporary_path / "profile"
        profile.mkdir()
        conversion_dir = temporary_path / "output"
        conversion_dir.mkdir()
        subprocess.run(
            [
                "soffice",
                f"-env:UserInstallation={profile.as_uri()}",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(conversion_dir),
                str(source),
            ],
            check=True,
            timeout=120,
        )
        generated_pdf = conversion_dir / f"{source.stem}.pdf"
        if not generated_pdf.is_file():
            raise FileNotFoundError(f"LibreOffice did not create {generated_pdf.name}")
        shutil.copy2(generated_pdf, output)


for _source_extension in ("docx", "pptx", "xlsx", "odt"):
    register(_source_extension, "pdf", tool="soffice")(_office_to_pdf)
