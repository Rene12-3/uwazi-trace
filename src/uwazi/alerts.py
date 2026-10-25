"""Turn signals into reviewable alerts. Tier = number of independent indicator families that fired."""
from __future__ import annotations

from dataclasses import asdict

import numpy as np
import pandas as pd

from .indicators import INDICATORS, Signal

ALERT_COLUMNS = ["award_id", "families", "indicators", "materiality", "entity", "category", "supplier",
                 "award_value_kes", "award_date", "method", "dq", "source_url", "tier", "evidence_grade"]
TIER_MEANING = {1: "Three or more independent kinds of signal", 2: "Two kinds of signal", 3: "One kind of signal"}


def build_alerts(signals: list[Signal], df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not signals:
        return pd.DataFrame(columns=ALERT_COLUMNS), pd.DataFrame(columns=[*Signal.__dataclass_fields__, "family"])
    sig = pd.DataFrame([asdict(x) for x in signals])
    sig["family"] = sig["indicator"].map(lambda k: INDICATORS[k].family)
    agg = sig.groupby("award_id").agg(families=("family", "nunique"), indicators=("indicator", lambda x: sorted(set(x))),
                                      materiality=("materiality", "max")).reset_index()
    cols = ["award_id", "entity", "category", "supplier", "award_value_kes", "award_date", "method", "dq", "source_url"]
    alerts = agg.merge(df[cols], on="award_id")
    alerts["tier"] = np.select([alerts.families >= 3, alerts.families == 2], [1, 2], 3)
    alerts["evidence_grade"] = np.where(alerts.dq == "", "A", "C")
    alerts = alerts.sort_values(["tier", "materiality"], ascending=[True, False]).reset_index(drop=True)
    return alerts[ALERT_COLUMNS], sig
