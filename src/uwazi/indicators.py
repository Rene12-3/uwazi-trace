"""Indicator library. Each indicator compares like with like, requires a minimum number of
comparators and a materiality floor, and returns evidence, never a verdict."""
from __future__ import annotations

from dataclasses import dataclass, field
from math import comb

import numpy as np
import pandas as pd

from .config import NONCOMPETITIVE, UNKNOWN_SUPPLIER, Settings


@dataclass(frozen=True)
class Indicator:
    code: str
    name: str
    family: str
    question: str
    legitimate: tuple = field(default_factory=tuple)


@dataclass(frozen=True)
class Signal:
    award_id: str
    indicator: str
    value: float
    detail: str
    baseline: str
    n: int
    materiality: float


INDICATORS = {
    "CONC": Indicator("CONC", "Supplier concentration", "Competition",
        "Does one supplier take an unusually large share of an entity's spend in a category, compared with peers?",
        ("Framework agreement or earlier open tender won by this supplier", "Few qualified suppliers in a remote area",
         "Proprietary or specialised goods", "Few awards in the cohort", "Incomplete data capture for this entity")),
    "METHOD": Indicator("METHOD", "Non-competitive method share", "Competition",
        "Is an unusually large share of spend awarded without open competition, compared with peers?",
        ("Declared emergency", "Sole source for proprietary goods", "AGPO or preference set-aside",
         "Framework call-off", "Method mislabelled in the source")),
    "TIMELINE": Indicator("TIMELINE", "Timeline integrity", "Process",
        "Do the dates break basic process rules, such as a very short bid window or an award before close?",
        ("Shorter statutory window for this method (verify current Regulations)", "Date entry error on the portal",
         "Re-advertised tender", "Emergency procurement")),
    "THRESH": Indicator("THRESH", "Threshold bunching or splitting", "Process",
        "Do awards cluster just under an approval threshold, or do repeated small awards add up to more than it?",
        ("Natural clustering of standard-priced items", "Estimate taken from a published price list",
         "Genuinely separate needs", "A different threshold applies to this entity type")),
    "PRICE": Indicator("PRICE", "Unit price vs comparable purchases", "Price",
        "Is the unit price higher than comparable purchases, after allowing for quantity?",
        ("Special specification (for example mobile clinic fit-out)", "Remote delivery cost", "Different VAT treatment",
         "Bundled warranty or training", "Quantity or unit mis-extracted from the title")),
}


def _wilson_lower(k: int, n: int, z: float = 1.64) -> float:
    p = k / n
    return (p + z * z / (2 * n) - z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / (1 + z * z / n)


def _binom_tail(n: int, k: int, p: float) -> float:
    return sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1))


def concentration(df: pd.DataFrame, s: Settings, shrink: float = 5.0) -> tuple[pd.DataFrame, list[Signal]]:
    d = df[df["supplier"] != UNKNOWN_SUPPLIER]
    rows = []
    for (e, c, f), g in d.groupby(["entity", "category", "fy"]):
        by = g.groupby("supplier")["award_value_kes"].sum().sort_values(ascending=False)
        top = by.index[0]
        rows.append(dict(entity=e, category=c, fy=f, top_supplier=top, share=by.iloc[0] / by.sum(), n=len(g),
                         k=int((g["supplier"] == top).sum()), top_value=by.iloc[0]))
    t = pd.DataFrame(rows)
    if t.empty:
        return t, []
    peers = t[t["n"] >= s.min_cohort_awards].groupby("category")["share"]
    t["peer_median"] = t["category"].map(peers.median())
    t["peer_p90"] = t["category"].map(peers.quantile(0.9))
    t["peer_n"] = t["category"].map(peers.count()).fillna(0).astype(int)
    t["shrunk_share"] = (t["share"] * t["n"] + shrink * t["peer_median"]) / (t["n"] + shrink)
    t["lower90"] = [_wilson_lower(k, n) for k, n in zip(t["k"], t["n"], strict=True)]
    t["flag"] = ((t["n"] >= s.min_cohort_awards) & (t["peer_n"] >= s.min_peer_cohorts) & (t["shrunk_share"] > t["peer_p90"])
                 & (t["lower90"] > t["peer_median"]) & (t["top_value"] >= 5 * s.materiality_floor_kes))
    out: list[Signal] = []
    for x in t[t["flag"]].itertuples():
        hit = d[(d.entity == x.entity) & (d.category == x.category) & (d.fy == x.fy) & (d.supplier == x.top_supplier)]
        for a in hit.itertuples():
            out.append(Signal(a.award_id, "CONC", x.share,
                f"{x.top_supplier} received {x.share:.0%} of value ({x.k} of {x.n} awards) at {x.entity} for {x.category} in FY{x.fy}.",
                f"Peer cohort: same category, {x.peer_n} entity-years. Median {x.peer_median:.0%}, P90 {x.peer_p90:.0%}. "
                f"Share after small-sample shrinkage {x.shrunk_share:.0%}. Lower 90% bound on award-count share {x.lower90:.0%}.",
                x.peer_n, float(a.award_value_kes)))
    return t, out


def method_mix(df: pd.DataFrame, s: Settings) -> tuple[pd.DataFrame, list[Signal]]:
    rows = []
    for (e, c, f), g in df.groupby(["entity", "category", "fy"]):
        nc = g.loc[g["method"].isin(NONCOMPETITIVE), "award_value_kes"].sum()
        rows.append(dict(entity=e, category=c, fy=f, n=len(g), share=nc / g["award_value_kes"].sum(), noncomp_value=nc))
    t = pd.DataFrame(rows)
    if t.empty:
        return t, []
    peers = t[t["n"] >= s.min_cohort_awards].groupby("category")["share"]
    t["peer_median"] = t["category"].map(peers.median())
    t["peer_p90"] = t["category"].map(peers.quantile(0.9))
    t["peer_n"] = t["category"].map(peers.count()).fillna(0).astype(int)
    t["flag"] = ((t["n"] >= s.min_cohort_awards) & (t["peer_n"] >= s.min_peer_cohorts) & (t["share"] > t["peer_p90"])
                 & (t["share"] > 0.5) & (t["noncomp_value"] >= 5 * s.materiality_floor_kes))
    out: list[Signal] = []
    for x in t[t["flag"]].itertuples():
        hit = df[(df.entity == x.entity) & (df.category == x.category) & (df.fy == x.fy) & df.method.isin(NONCOMPETITIVE)]
        for a in hit.itertuples():
            out.append(Signal(a.award_id, "METHOD", x.share,
                f"{x.share:.0%} of {x.entity} spend on {x.category} in FY{x.fy} used direct or restricted methods ({x.n} awards).",
                f"Peer cohort: {x.peer_n} entity-years. Median {x.peer_median:.0%}, P90 {x.peer_p90:.0%}.",
                x.peer_n, float(a.award_value_kes)))
    return t, out


def timeline(df: pd.DataFrame, s: Settings) -> list[Signal]:
    d = df.dropna(subset=["published_on", "closes_on", "award_date"]).copy()
    d["window"] = (d["closes_on"] - d["published_on"]).dt.days
    medians = d.groupby("category")["window"].median()
    counts = d.groupby("category").size()
    out: list[Signal] = []
    for a in d.itertuples():
        problems = []
        if a.window < s.min_bid_window_days:
            problems.append(f"bid window of {a.window} days is below the configured minimum of {s.min_bid_window_days}")
        if a.award_date < a.closes_on:
            problems.append("award dated before tender close")
        if problems:
            out.append(Signal(a.award_id, "TIMELINE", float(a.window), "; ".join(problems).capitalize() + ".",
                f"Median bid window for {a.category} is {medians[a.category]:.0f} days across {counts[a.category]} awards. "
                "The minimum is a setting, not a verified legal value.", int(counts[a.category]), float(a.award_value_kes)))
    return out


def threshold(df: pd.DataFrame, s: Settings, min_n: int = 8, alpha: float = 0.01) -> list[Signal]:
    T = s.approval_threshold_kes
    upper = df[(df.award_value_kes >= 0.9 * T) & (df.award_value_kes < T)]
    lower = df[(df.award_value_kes >= 0.8 * T) & (df.award_value_kes < 0.9 * T)]
    p0 = float(np.clip(len(upper) / max(1, len(upper) + len(lower)), 0.3, 0.7))
    out: list[Signal] = []
    seen: set[str] = set()
    for e, h in upper.groupby("entity"):
        k = len(h)
        n = k + int((lower.entity == e).sum())
        if n >= min_n and k >= 5:
            p = _binom_tail(n, k, p0)
            if p < alpha:
                for a in h.itertuples():
                    seen.add(a.award_id)
                    out.append(Signal(a.award_id, "THRESH", a.award_value_kes / T,
                        f"{e} has {k} of {n} awards in the 80-100% band sitting within 10% below the threshold (KES {T:,.0f}).",
                        f"Expected share in the upper band about {p0:.0%} across all entities. Exact binomial p = {p:.4f}. The threshold is a setting.",
                        n, float(a.award_value_kes)))
    below = df[(df.award_value_kes < T) & (df.supplier != UNKNOWN_SUPPLIER)]
    for (e, sup, _), g in below.sort_values("award_date").groupby(["entity", "supplier", "category"]):
        group = [g.iloc[0]]
        for _, r in g.iloc[1:].iterrows():
            if (r.award_date - group[-1].award_date).days <= 30:
                group.append(r)
            else:
                _emit_split(group, T, e, sup, out, seen)
                group = [r]
        _emit_split(group, T, e, sup, out, seen)
    return out


def _emit_split(group, T, entity, supplier, out, seen) -> None:
    total = float(sum(x.award_value_kes for x in group))
    if len(group) < 2 or total < T:
        return
    for x in group:
        if x.award_id in seen:
            continue
        seen.add(x.award_id)
        out.append(Signal(x.award_id, "THRESH", total / T,
            f"{len(group)} awards to {supplier} from {entity} within 30 days, each under KES {T:,.0f} but totalling KES {total:,.0f}.",
            "Pattern rule with no statistical baseline: same supplier, entity and category within 30 days, sum above the threshold.",
            len(group), total))


def _robust_fit(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    b = np.polyfit(x, y, 1)
    resid = np.abs(y - np.polyval(b, x))
    keep = resid <= np.quantile(resid, 0.9)
    return np.polyfit(x[keep], y[keep], 1)


def price(df: pd.DataFrame, s: Settings, min_n: int = 30) -> list[Signal]:
    """log(unit price) ~ log(quantity), robust fit, 5-fold out-of-fold residuals, split-conformal
    one-sided upper bound at miscoverage alpha. Flag only if above the bound AND material.
    Specifications are NOT modelled."""
    d = df[df.category.isin(s.standard_categories) & (df.quantity > 0)].copy()
    if d.empty:
        return []
    d["unit"] = d.award_value_kes / d.quantity
    d["yrs"] = (d.award_date.max() - d.award_date).dt.days / 365.25
    d["real"] = d.unit * (1 + s.annual_inflation) ** d.yrs
    out: list[Signal] = []
    for cat, g in d.groupby("category"):
        if len(g) < min_n:
            continue
        x, y = np.log(g.quantity.values), np.log(g.real.values)
        fold = np.random.default_rng(0).permutation(len(g)) % 5
        pred = np.empty(len(g))
        for f in range(5):
            b = _robust_fit(x[fold != f], y[fold != f])
            pred[fold == f] = np.polyval(b, x[fold == f])
        resid = y - pred
        q = np.sort(resid)[min(int(np.ceil((len(g) + 1) * (1 - s.price_alpha))), len(g)) - 1]
        slope = _robust_fit(x, y)[0]
        for a, r, p in zip(g.itertuples(), resid, pred, strict=True):
            infl = (1 + s.annual_inflation) ** a.yrs
            expected, upper = np.exp(p) / infl, np.exp(p + q) / infl
            excess = (a.unit - expected) * a.quantity
            if r > q and excess >= s.materiality_floor_kes:
                out.append(Signal(a.award_id, "PRICE", float(a.unit),
                    f"Unit price KES {a.unit:,.0f} vs model-expected KES {expected:,.0f} for quantity {a.quantity:.0f} "
                    f"({a.unit / expected - 1:+.0%}). Estimated excess about KES {excess:,.0f}.",
                    f"{len(g)} comparable '{cat}' awards. Conformal one-sided upper bound (alpha={s.price_alpha:.0%}) = KES {upper:,.0f}; "
                    f"observed exceeds it. Quantity elasticity {slope:+.2f}; inflation assumption {s.annual_inflation:.0%}/yr. "
                    "Specifications are NOT modelled.", len(g), float(excess)))
    return out
