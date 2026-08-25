"""
CLI tests — verify the command-line interface behaves correctly.

Note on Windows encoding: Rich outputs ANSI sequences that may break cp1252.
We force UTF-8 via PYTHONIOENCODING and PYTHONUTF8=1, and use stderr + stdout
combined since Rich routes most output through stderr when piped.
"""

import subprocess
import sys
import os
import re
import pytest


def _cug(*args, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run cug as a subprocess with UTF-8 encoding forced."""
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-m", "cug", *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout, env=env,
    )


def _combined(result: subprocess.CompletedProcess) -> str:
    """Return stdout + stderr combined (Rich routes to stderr when piped)."""
    return (result.stdout or "") + (result.stderr or "")


def test_cli_help():
    """cug --help must exit 0 and mention generate."""
    result = _cug("--help")
    assert result.returncode == 0
    assert "generate" in _combined(result).lower()


def test_cli_help_mentions_commands():
    """cug --help should list the main commands."""
    result = _cug("--help")
    assert result.returncode == 0
    combined = _combined(result).lower()
    for cmd in ("generate", "formats", "categories"):
        assert cmd in combined, f"Command '{cmd}' not found in --help output"


def test_cli_formats():
    """cug formats must list at least 5 formats."""
    result = _cug("formats")
    assert result.returncode == 0, f"cug formats failed:\n{_combined(result)}"
    combined = _combined(result).lower()
    for fmt in ("csv", "parquet", "duckdb", "json", "excel"):
        assert fmt in combined, f"Format '{fmt}' not in output"


def test_cli_categories():
    """cug categories must succeed and produce output."""
    result = _cug("categories")
    assert result.returncode == 0, f"cug categories failed:\n{_combined(result)}"
    assert len(_combined(result).strip()) > 10


def test_cli_categories_spanish():
    """cug categories -l es must succeed."""
    result = _cug("categories", "-l", "es")
    assert result.returncode == 0, f"cug categories -l es failed:\n{_combined(result)}"


def test_cli_generate_invalid_format():
    """cug generate with an unknown format must fail (non-zero exit)."""
    result = _cug("generate", "-n", "10", "-f", "banana_format")
    assert result.returncode != 0, "Expected non-zero exit for invalid format"


def test_cli_generate_minimal(tmp_path):
    """cug generate -n 50 -f csv must complete without error."""
    result = _cug(
        "generate", "-n", "50", "-f", "csv",
        "-o", str(tmp_path / "out"), "--seed", "99",
        timeout=60,
    )
    assert result.returncode == 0, f"cug generate failed:\n{_combined(result)}"


def test_cli_info():
    """cug info must exit 0."""
    result = _cug("info")
    assert result.returncode == 0, f"cug info failed:\n{_combined(result)}"


@pytest.mark.parametrize(
    "flags, should_run",
    [
        (["--verify"],               True),   # asks for the check
        (["--strict"],               True),   # aborting implies checking
        ([],                         False),  # integrity_check defaults to false
        (["--no-verify", "--strict"], False), # explicit opt-out wins
    ],
)
def test_generate_verify_flag_controls_the_check(tmp_path, flags, should_run):
    """--verify is the documented way to run FK validation from the CLI."""
    out = tmp_path / "out"
    result = _cug(
        "generate", "-n", "300", "-f", "csv", "-o", str(out), "--seed", "42",
        *flags, timeout=120,
    )
    assert result.returncode == 0, _combined(result)
    ran = "Integrity check passed" in _combined(result)
    assert ran is should_run, f"flags={flags} -> ran={ran}"


@pytest.mark.parametrize("flags", [["--verify"], ["--strict"], []])
def test_summary_panel_agrees_with_what_runs(tmp_path, flags):
    """The panel used to print "disabled" while the check ran and passed."""
    out = tmp_path / "out"
    result = _cug(
        "generate", "-n", "300", "-f", "csv", "-o", str(out), "--seed", "42",
        *flags, timeout=120,
    )
    assert result.returncode == 0, _combined(result)
    text = _combined(result)
    announced_disabled = re.search(r"Integrity check\s*│\s*\x1b?\[?[\d;]*m?\s*disabled", text)
    actually_ran = "Integrity check passed" in text
    assert not (announced_disabled and actually_ran), (
        "panel says disabled but the check ran"
    )
