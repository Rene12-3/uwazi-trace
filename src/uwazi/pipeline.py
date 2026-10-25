"""End-to-end analysis: clean, resolve, compute indicators, build alerts."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .alerts import build_alerts
from .cleaning import prepare
from .config import Settings
from .indicators import concentration, method_mix, price, threshold, timeline
from .resolution import resolve_suppliers
from .schema import missing_columns


@dataclass
class Result:
    awards: pd.DataFrame
    quality: dict
    merges: pd.DataFrame
    concentration: pd.DataFrame
    method: pd.DataFrame
    signals: pd.DataFrame
    alerts: pd.DataFrame
    settings: Settings


def run(raw: pd.DataFrame, settings: Settings | None = None) -> Result:
    settings = settings or Settings()
    missing = missing_columns(raw)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    awards, quality = prepare(raw)
    if awards.empty:
        raise ValueError("No usable rows after cleaning. Check award values and award dates.")
    awards, merges = resolve_suppliers(awards, settings.fuzzy_supplier_merge)
    conc_table, s1 = concentration(awards, settings)
    method_table, s2 = method_mix(awards, settings)
    signals = s1 + s2 + timeline(awards, settings) + threshold(awards, settings) + price(awards, settings)
    alerts, signals_df = build_alerts(signals, awards)
    return Result(awards, quality, merges, conc_table, method_table, signals_df, alerts, settings)
