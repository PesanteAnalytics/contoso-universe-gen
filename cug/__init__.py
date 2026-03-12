"""
CUG — Contoso Universe Generator
High-performance synthetic retail data for analytics demos.
"""

__version__ = "0.2.0"
__author__  = "CSalcedoDataBI"

from .config import load_config, AppConfig

__all__ = ["load_config", "AppConfig", "__version__"]
