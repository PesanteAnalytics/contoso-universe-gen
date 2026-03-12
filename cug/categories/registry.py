"""
Category Registry — auto-discovers YAML plugins from builtin/ and custom paths.
"""

from __future__ import annotations

from pathlib import Path

from .base import CategoryPlugin

_BUILTIN_DIR = Path(__file__).parent / "builtin"


class CategoryRegistry:
    """
    Discovers and loads CategoryPlugin objects from YAML files.

    Priority order:
    1. Builtin YAMLs in cug/categories/builtin/
    2. Custom YAMLs specified by the user in config
    """

    def __init__(self) -> None:
        self._plugins: dict[str, CategoryPlugin] = {}

    def load_builtins(self, enabled: list[str] | None = None) -> "CategoryRegistry":
        """Load builtin category plugins by their ID.
        If *enabled* is None, loads all available builtin categories.
        """
        if enabled is None:
            enabled = [p.stem for p in _BUILTIN_DIR.glob("*.yaml")]
        for plugin_id in enabled:
            yaml_path = _BUILTIN_DIR / f"{plugin_id}.yaml"
            if not yaml_path.exists():
                available = [p.stem for p in _BUILTIN_DIR.glob("*.yaml")]
                raise FileNotFoundError(
                    f"Builtin category '{plugin_id}' not found. "
                    f"Available: {sorted(available)}"
                )
            plugin = CategoryPlugin.from_yaml(yaml_path)
            self._plugins[plugin.plugin_id] = plugin
        return self

    def load_custom(self, paths: list[Path]) -> "CategoryRegistry":
        """Load custom YAML plugins from user-defined paths."""
        for path in paths:
            path = Path(path)
            if not path.exists():
                raise FileNotFoundError(f"Custom category YAML not found: {path}")
            plugin = CategoryPlugin.from_yaml(path)
            self._plugins[plugin.plugin_id] = plugin
        return self

    def get(self, plugin_id: str) -> CategoryPlugin:
        if plugin_id not in self._plugins:
            raise KeyError(f"Category plugin '{plugin_id}' not loaded.")
        return self._plugins[plugin_id]

    def all(self) -> list[CategoryPlugin]:
        return list(self._plugins.values())

    def list_ids(self) -> list[str]:
        return sorted(self._plugins.keys())

    def list_available_builtins(self) -> list[str]:
        """Return all available builtin plugin IDs (regardless of what's loaded)."""
        return sorted(p.stem for p in _BUILTIN_DIR.glob("*.yaml"))

    @classmethod
    def from_config(cls, enabled: list[str], custom: list[Path]) -> "CategoryRegistry":
        """Convenience constructor that loads all plugins in one call."""
        reg = cls()
        reg.load_builtins(enabled)
        if custom:
            reg.load_custom(custom)
        return reg

    def __len__(self) -> int:
        return len(self._plugins)

    def __repr__(self) -> str:
        return f"CategoryRegistry(plugins={self.list_ids()})"
