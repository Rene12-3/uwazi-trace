"""Central configuration. Every threshold is an explicit, documented assumption."""
from __future__ import annotations

from dataclasses import dataclass

UNKNOWN_SUPPLIER = "(unknown supplier)"
NONCOMPETITIVE = frozenset({"direct", "restricted", "emergency"})
STANDARD_CATEGORIES = ("Motor vehicles", "Laptops")


@dataclass(frozen=True)
class Settings:
    """Analysis settings. Values here are assumptions, not verified legal facts.

    approval_threshold_kes and min_bid_window_days must be checked against the
    Public Procurement and Asset Disposal Act, its Regulations and entity-type
    rules in force on the award date before any result is relied upon.
    """

    approval_threshold_kes: float = 5_000_000
    min_bid_window_days: int = 14
    materiality_floor_kes: float = 1_000_000
    price_alpha: float = 0.02          # conformal miscoverage rate (lower = fewer flags)
    annual_inflation: float = 0.0      # used to deflate unit prices to the latest award date
    min_cohort_awards: int = 5         # awards needed in an entity-category-year cohort
    min_peer_cohorts: int = 8          # peer cohorts needed to form a baseline
    fuzzy_supplier_merge: bool = False # conservative fuzzy matching, off by default
    standard_categories: tuple = STANDARD_CATEGORIES
