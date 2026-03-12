"""
Deterministic Seeder — per-day and per-entity seed management.
Inspired by the V2 concept: seed = (year * 1000) + dayOfYear
Extended to also support per-entity seeding for consistent customer/product selection.
"""

from __future__ import annotations

import random
from datetime import date


class DeterministicSeeder:
    """
    Provides deterministic seeds so that:
    - Same config + same date → same random sequence for that day
    - Changing one day doesn't affect any other day
    - Per-entity seeding allows consistent sub-sequences within a day
    """

    def __init__(self, master_seed: int = 42) -> None:
        self.master_seed = master_seed

    def day_seed(self, d: date) -> int:
        """
        Compute seed for a specific day.
        Formula: master_seed XOR (year * 1000 + day_of_year)
        """
        day_of_year = d.timetuple().tm_yday
        return self.master_seed ^ (d.year * 1000 + day_of_year)

    def entity_seed(self, d: date, entity: str, index: int = 0) -> int:
        """
        Compute seed for a specific entity within a day.
        Allows deterministic sub-sequences for customers, products, etc.
        """
        entity_hash = hash(entity) & 0x7FFFFFFF  # positive int
        return self.day_seed(d) ^ entity_hash ^ (index * 31337)

    def rng(self, d: date) -> random.Random:
        """Return a seeded Random instance for the given day."""
        return random.Random(self.day_seed(d))

    def entity_rng(self, d: date, entity: str, index: int = 0) -> random.Random:
        """Return a seeded Random instance for a specific entity within a day."""
        return random.Random(self.entity_seed(d, entity, index))
