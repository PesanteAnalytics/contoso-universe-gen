"""
CUG — Contoso Universe Generator
High-performance synthetic retail data for analytics demos.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _installed_version

try:
    # Read the version from package metadata so pyproject.toml is the only place
    # it is written. Keeping a literal here means it eventually disagrees with
    # the tag, and the release workflow only checks pyproject.
    __version__ = _installed_version("contoso-universe-gen")
except PackageNotFoundError:  # a source tree that was never installed
    __version__ = "0.0.0.dev0"

__author__ = "Pesante Analytics LLC"

from .config import AppConfig, load_config

__all__ = ["load_config", "AppConfig", "__version__"]
