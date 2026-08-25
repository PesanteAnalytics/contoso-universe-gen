"""
CUG — Contoso Universe Generator
High-performance synthetic retail data for analytics demos.
"""

__version__ = "0.2.0"
__author__  = "Pesante Analytics LLC"

from .config import AppConfig, load_config

__all__ = ["load_config", "AppConfig", "__version__"]
