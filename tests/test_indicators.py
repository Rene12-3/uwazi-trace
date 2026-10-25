import pandas as pd
import pytest

from uwazi.config import UNKNOWN_SUPPLIER, Settings
from uwazi.indicators import concentration, price, timeline

PLANTED = {"conc": "CONC", "split": "THRESH", "bunch": "THRESH", "short": "TIMELINE"}


@pytest.mark.parametrize("tag,indicator", PLANTED.items())
def test_planted_patterns_are_found(raw, result, tag, indicator):
    planted = set(raw[raw.planted == tag].award_id)
    found = set(result.signals[result.signals.indicator == indicator].award_id)
    assert len(planted & found) / len(planted) >= 0.9


def test_price_detector_is_conservative_but_useful(raw, result):
    planted = set(raw[raw.planted == "price"].award_id)
    flagged = set(result.signals[result.signals.indicator == "PRICE"].award_id)
    assert len(planted & flagged) / len(planted) >= 0.4
    assert len(planted & flagged) >= 0.25 * len(flagged)   # sanity check on precision with clean synthetic data


def test_conformal_price_bound_is_calibrated_on_clean_data(raw, result):
    clean = result.awards[~result.awards.award_id.isin(raw[raw.planted != ""].award_id)]
    s = Settings(price_alpha=0.05, materiality_floor_kes=0)
    n = clean.category.isin(s.standard_categories).sum()
    assert abs(len(price(clean, s)) / n - 0.05) < 0.02


def test_small_cohorts_do_not_trigger_concentration():
    rows = [dict(award_id=f"a{i}", entity="E", category="C", fy="2023/2024", supplier="S", award_value_kes=1e8) for i in range(3)]
    table, signals = concentration(pd.DataFrame(rows), Settings())
    assert signals == [] and not table["flag"].any()


def test_unknown_suppliers_are_not_treated_as_one_supplier(result):
    unknown_alerts = result.alerts[result.alerts.supplier == UNKNOWN_SUPPLIER]
    conc = result.signals[(result.signals.indicator == "CONC") & result.signals.award_id.isin(unknown_alerts.award_id)]
    assert conc.empty


def test_timeline_flags_award_before_close():
    df = pd.DataFrame([dict(award_id="x", category="C", entity="E", award_value_kes=10,
                            published_on=pd.Timestamp("2024-01-01"), closes_on=pd.Timestamp("2024-02-01"),
                            award_date=pd.Timestamp("2024-01-20"))])
    out = timeline(df, Settings())
    assert len(out) == 1 and "before tender close" in out[0].detail
