"""
Category Plugin Base Class
All category plugins (builtin or external) must follow this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ProductTemplate:
    name_template: str    # e.g. "{brand} {model} {spec}"
    models: list[str]
    specs: list[str]
    brands: list[str]


@dataclass
class Subcategory:
    id: str
    display_names: dict[str, str]   # {"en": "Computers", "es": "Computadoras"}
    brands: list[str]
    price_range: tuple[float, float]
    margin_range: tuple[float, float]
    trend: dict[int, float]         # {year: weight_multiplier}
    products: list[ProductTemplate]


@dataclass
class CategoryPlugin:
    plugin_id: str
    display_names: dict[str, str]  # {"en": "Electronics", "es": "Electrónica"}
    subcategories: list[Subcategory]
    source_path: Path | None = None

    def display_name(self, language: str = "en") -> str:
        """Return display name for the given language, falling back to English."""
        return self.display_names.get(language) or self.display_names.get("en", self.plugin_id)

    @classmethod
    def from_yaml(cls, path: Path) -> "CategoryPlugin":
        """Load a CategoryPlugin from a YAML file."""
        with open(path, encoding="utf-8") as f:
            data: dict[str, Any] = yaml.safe_load(f)

        subcategories = []
        for sub in data.get("subcategories", []):
            # Parse trend: YAML keys may be ints or strings
            raw_trend: dict[str, float] = sub.get("trend", {})
            trend = {int(k): float(v) for k, v in raw_trend.items()}

            # Parse product templates
            templates = []
            for pt in sub.get("products", []):
                templates.append(ProductTemplate(
                    name_template=pt.get("name_template", "{brand} {model}"),
                    models=pt.get("models", []),
                    specs=pt.get("specs", []),
                    brands=pt.get("brands", sub.get("brands", [])),
                ))

            subcategories.append(Subcategory(
                id=sub["id"],
                display_names=sub.get("display_names", {"en": sub["id"]}),
                brands=sub.get("brands", []),
                price_range=tuple(sub.get("price_range", [99, 999])),
                margin_range=tuple(sub.get("margin_range", [0.10, 0.30])),
                trend=trend,
                products=templates,
            ))

        return cls(
            plugin_id=data["plugin_id"],
            display_names=data.get("display_names", {"en": data["plugin_id"]}),
            subcategories=subcategories,
            source_path=path,
        )
