"""Parsing, normalisation and data-quality flagging. Never silently invents data."""
from __future__ import annotations

import pandas as pd

from .config import UNKNOWN_SUPPLIER

METHOD_RULES = (
    ("emerg", "emergency"), ("urgen", "emergency"), ("direct", "direct"), ("sole", "direct"),
    ("restrict", "restricted"), ("select", "restricted"), ("quot", "rfq"), ("rfq", "rfq"), ("open", "open"),
)


def normalise_method(value) -> str:
    text = str(value).lower().strip()
    for key, label in METHOD_RULES:
        if key in text:
            return label
    return text  # unmapped labels stay visible and are treated as competitive


def parse_amount(series: pd.Series) -> pd.Series:
    """Strict money parsing. 'KES 1,200,000' parses; '1,2oo' becomes missing, never 12."""
    cleaned = (series.astype(str).str.upper()
               .str.replace(r"^\s*(KES|KSH|KSHS|KSH\.)\s*", "", regex=True)
               .str.replace(",", "", regex=False).str.strip())
    return pd.to_numeric(cleaned, errors="coerce")


def fiscal_year(dates: pd.Series) -> pd.Series:
    """Kenyan fiscal year runs 1 July to 30 June. Returns 'YYYY/YYYY' or 'unknown'."""
    year, month = dates.dt.year, dates.dt.month
    start = year.where(month >= 7, year - 1).astype("Int64")
    label = start.astype(str) + "/" + (start + 1).astype(str)
    return label.where(dates.notna(), "unknown")


def prepare(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return (clean awards, quality report). Dropped rows are counted, not hidden."""
    df = raw.copy()
    report = {"rows_in": len(df)}
    for col in ("published_on", "closes_on", "award_date"):
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["award_value_kes"] = parse_amount(df["award_value_kes"])
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["bidder_count"] = pd.to_numeric(df["bidder_count"], errors="coerce")  # NaN = unknown, never "one bidder"
    df["method"] = df["method"].map(normalise_method)
    supplier = df["supplier"].astype("string").str.strip()
    df["supplier"] = supplier.where(supplier.notna() & ~supplier.isin(["", "nan", "None"]), UNKNOWN_SUPPLIER).astype(str)

    before = len(df)
    df = df.drop_duplicates("award_id", keep="first")
    report["duplicates_removed"] = before - len(df)
    df["fy"] = fiscal_year(df["award_date"])
    no_value = df["award_value_kes"].isna()
    no_date = df["fy"].eq("unknown")
    report["dropped_missing_value"] = int(no_value.sum())
    report["dropped_missing_award_date"] = int((no_date & ~no_value).sum())
    df = df[~no_value & ~no_date].reset_index(drop=True)

    missing_dates = df[["published_on", "closes_on", "award_date"]].isna().any(axis=1)
    unknown_supplier = df["supplier"].eq(UNKNOWN_SUPPLIER)
    df["dq"] = [",".join(f for f, bad in (("missing_dates", d), ("missing_supplier", s)) if bad)
                for d, s in zip(missing_dates, unknown_supplier, strict=True)]
    report["rows_out"] = len(df)
    return df, report


def completeness(df: pd.DataFrame) -> dict:
    """Share of usable records with each key field present."""
    n = max(len(df), 1)
    return {
        "Award dates present": float(df[["published_on", "closes_on", "award_date"]].notna().all(axis=1).sum() / n),
        "Supplier named": float((df["supplier"] != UNKNOWN_SUPPLIER).sum() / n),
        "Bidder count known": float(df["bidder_count"].notna().sum() / n),
        "Quantity recorded": float((df["quantity"] > 0).sum() / n),
    }
