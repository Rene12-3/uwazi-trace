import pandas as pd
import pytest

from uwazi.config import Settings
from uwazi.pipeline import run


def test_pipeline_produces_tiered_alerts(result):
    a = result.alerts
    assert len(a) > 0 and set(a.tier) <= {1, 2, 3}
    assert (a.tier == 1).sum() >= 1                       # the planted deep case reaches tier 1
    assert a.sort_values(["tier"]).tier.is_monotonic_increasing


def test_tier_equals_number_of_independent_families(result):
    fam = result.signals.groupby("award_id")["family"].nunique()
    merged = result.alerts.set_index("award_id").join(fam.rename("f"))
    assert ((merged.f >= 3) == (merged.tier == 1)).all()


def test_every_alert_has_a_source_and_a_baseline(result):
    assert result.alerts.source_url.notna().all()
    assert (result.signals.baseline.str.len() > 20).all()


def test_missing_columns_fail_clearly():
    with pytest.raises(ValueError, match="Missing required columns"):
        run(pd.DataFrame({"award_id": ["a"]}))


def test_higher_materiality_floor_reduces_alerts(raw):
    low = len(run(raw, Settings(materiality_floor_kes=1e6)).alerts)
    high = len(run(raw, Settings(materiality_floor_kes=2e7)).alerts)
    assert high < low


def test_fuzzy_merge_recovers_true_supplier_count(result, raw):
    assert result.awards.supplier.nunique() == 120
