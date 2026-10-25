import pandas as pd
import pytest

from uwazi.cleaning import fiscal_year, normalise_method, parse_amount, prepare
from uwazi.config import UNKNOWN_SUPPLIER
from uwazi.schema import REQUIRED_COLUMNS


def _row(**kw):
    base = dict(award_id="a", entity="E", category="C", method="open", published_on="2024-01-01", closes_on="2024-01-20",
                award_date="2024-02-01", award_value_kes="1000", quantity=1, supplier="S", bidder_count=None, source_url="x")
    base.update(kw)
    return base


def test_amount_parsing_is_strict():
    s = parse_amount(pd.Series(["KES 1,200,000", "Ksh 5000", "750000.50", "1,2oo", "abc"]))
    assert s.iloc[0] == 1_200_000 and s.iloc[1] == 5000 and s.iloc[2] == 750000.5
    assert s.iloc[3:].isna().all()          # garbage must never become a small valid number


@pytest.mark.parametrize("raw,expected", [("Open Tender ", "open"), ("Sole source", "direct"), ("RFQ", "rfq"),
                                          ("Request for quotation", "rfq"), ("Emergency", "emergency"), ("weird", "weird")])
def test_method_normalisation(raw, expected):
    assert normalise_method(raw) == expected


def test_fiscal_year_boundaries():
    d = pd.Series(pd.to_datetime(["2024-06-30", "2024-07-01", "2025-01-15", None]))
    assert fiscal_year(d).tolist() == ["2023/2024", "2024/2025", "2024/2025", "unknown"]


def test_prepare_reports_what_it_drops_and_flags_rest():
    raw = pd.DataFrame([_row(award_id="1"), _row(award_id="2", award_value_kes="bad"), _row(award_id="3", award_date=None),
                        _row(award_id="4", supplier=None), _row(award_id="1")], columns=REQUIRED_COLUMNS)
    df, rep = prepare(raw)
    assert rep["duplicates_removed"] == 1 and rep["dropped_missing_value"] == 1 and rep["dropped_missing_award_date"] == 1
    assert set(df.award_id) == {"1", "4"}
    assert df.loc[df.award_id == "4", "supplier"].iloc[0] == UNKNOWN_SUPPLIER
    assert "missing_supplier" in df.loc[df.award_id == "4", "dq"].iloc[0]


def test_unknown_bidder_count_stays_unknown():
    df, _ = prepare(pd.DataFrame([_row()], columns=REQUIRED_COLUMNS))
    assert df["bidder_count"].isna().all()   # never coerced to 0 or 1
