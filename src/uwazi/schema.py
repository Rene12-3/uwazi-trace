"""Input data contract for award-level records."""
from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = [
    "award_id", "entity", "category", "method", "published_on", "closes_on",
    "award_date", "award_value_kes", "quantity", "supplier", "bidder_count", "source_url",
]


def missing_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in REQUIRED_COLUMNS if c not in df.columns]


def template_csv() -> str:
    return ",".join(REQUIRED_COLUMNS) + "\n"
