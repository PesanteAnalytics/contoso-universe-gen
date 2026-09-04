"""
The core install must stay installable.

`deltalake`, `xlsxwriter` and `pyodbc` are extras. `pyodbc` in particular needs
an ODBC stack and, on some platforms, a compiler — as a hard requirement it
turns `pip install` into a failure for everyone who only ever wanted Parquet.

Keeping them optional costs nothing at runtime and one rule at import time: no
module on the core path may import them. That rule is invisible, easy to break
with a tidy-up that hoists an import to the top of a writer, and breaks only for
people who do not have the extra — which is nobody on the machine that made the
change. Hence this file.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

OPTIONAL = ("deltalake", "xlsxwriter", "pyodbc")
ROOT = Path(__file__).resolve().parent.parent


def test_optional_deps_are_not_core_requirements():
    """They belong to extras, and dev carries them so the suite can run."""
    meta = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = meta["project"]

    core = " ".join(project["dependencies"])
    for pkg in OPTIONAL:
        assert pkg not in core, f"{pkg} is back in the core dependencies"

    extras = project["optional-dependencies"]
    for extra in ("delta", "excel", "sqlserver", "all", "dev"):
        assert extra in extras, f"the '{extra}' extra is gone"

    assert "deltalake" in " ".join(extras["delta"])
    assert "xlsxwriter" in " ".join(extras["excel"])
    assert "pyodbc" in " ".join(extras["sqlserver"])

    everything = " ".join(extras["all"])
    for pkg in OPTIONAL:
        assert pkg in everything, f"the 'all' extra forgot {pkg}"
        assert pkg in " ".join(extras["dev"]), f"dev cannot test {pkg}"


@pytest.mark.parametrize("module", ["cug.cli", "cug.orchestrator", "cug.writers"])
def test_core_imports_pull_no_optional_dependency(module: str):
    """Importing the core path must not load an optional package.

    Run in a subprocess: the test session has all three installed, so an import
    leak is invisible from inside it. A clean interpreter is the only place the
    question can actually be asked.
    """
    probe = (
        f"import {module}, sys; "
        f"leaked = [m for m in {OPTIONAL!r} if m in sys.modules]; "
        "print(','.join(leaked))"
    )
    out = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True, text=True, cwd=ROOT, timeout=120,
    )
    assert out.returncode == 0, f"importing {module} failed:\n{out.stderr}"
    leaked = out.stdout.strip()
    assert not leaked, (
        f"importing {module} pulled in {leaked} — that package is an extra, so "
        "a core-only install would now fail on import"
    )


def test_project_urls_are_declared():
    """Without these the PyPI page has no link back to the repository."""
    meta = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    urls = meta["project"].get("urls", {})
    assert {"Homepage", "Repository", "Issues"} <= set(urls)
    for name, url in urls.items():
        assert url.startswith("https://"), f"{name} is not https"
