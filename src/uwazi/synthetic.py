"""Synthetic benchmark data with planted patterns. Fictional entities and suppliers only.

The `planted` column is the ground truth used to test detectors. It is never used by the analysis.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .schema import REQUIRED_COLUMNS

CATEGORIES = {"Motor vehicles": (6e6, 1, 6, 0.15), "Laptops": (9e4, 10, 200, 0.2),
              "Road works": (2e7, 1, 1, 0.6), "Stationery": (3e5, 1, 1, 0.5)}


def generate(seed: int = 7, n: int = 3000) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    ents = [f"National Dept {i}" for i in range(1, 7)] + [f"County {c} Health" for c in "ABCDEFGHIJ"]
    sup = [f"Supplier {i:03d} Ltd" for i in range(1, 121)]
    rows = []
    for _ in range(n):
        e, c = rng.choice(ents), rng.choice(list(CATEGORIES))
        unit, qa, qb, sd = CATEGORIES[c]
        q = int(rng.integers(qa, qb + 1))
        pub = pd.Timestamp("2022-07-01") + pd.Timedelta(days=int(rng.integers(0, 1000)))
        close = pub + pd.Timedelta(days=int(rng.integers(14, 31)))
        rows.append(dict(entity=e, category=c, method=rng.choice(["open", "rfq", "restricted", "direct"], p=[.8, .1, .05, .05]),
                         published_on=pub, closes_on=close, award_date=close + pd.Timedelta(days=int(rng.integers(7, 40))),
                         award_value_kes=unit * q * rng.lognormal(0, sd), quantity=q, supplier=rng.choice(sup),
                         bidder_count=np.nan if rng.random() < .4 else int(rng.integers(3, 10)), planted=""))
    df = pd.DataFrame(rows)

    idx = df[(df.entity == "County A Health") & (df.category == "Motor vehicles")].index   # concentration (+ some tier-1 cases)
    hit = rng.choice(idx, size=int(len(idx) * .7), replace=False)
    df.loc[hit, ["supplier", "method", "planted"]] = ["Supplier 007 Ltd", "direct", "conc"]
    deep = hit[rng.random(len(hit)) < .3]
    df.loc[deep, "award_value_kes"] *= 1.7
    df.loc[deep, "closes_on"] = df.loc[deep, "published_on"] + pd.Timedelta(days=5)

    veh = df[(df.category == "Motor vehicles") & (df.planted == "")].sample(15, random_state=1).index   # price
    df.loc[veh, "award_value_kes"] *= rng.uniform(1.5, 1.8, len(veh))
    df.loc[veh, "planted"] = "price"
    short = df[df.planted == ""].sample(20, random_state=2).index                                      # short windows
    df.loc[short, "closes_on"] = df.loc[short, "published_on"] + pd.Timedelta(days=3)
    df.loc[short, "planted"] = "short"

    extra = []
    for k in range(12):                                                                                # splitting
        base = pd.Timestamp("2023-09-01") + pd.Timedelta(days=40 * k)
        for j in range(2):
            extra.append(dict(entity="County C Health", category="Stationery", method="rfq", published_on=base - pd.Timedelta(days=20),
                              closes_on=base - pd.Timedelta(days=5), award_date=base + pd.Timedelta(days=4 * j),
                              award_value_kes=rng.uniform(3.1e6, 3.4e6), quantity=1, supplier="Supplier 033 Ltd",
                              bidder_count=np.nan, planted="split"))
    for _ in range(25):                                                                                # bunching
        pub = pd.Timestamp("2023-01-01") + pd.Timedelta(days=int(rng.integers(0, 600)))
        extra.append(dict(entity="National Dept 3", category="Road works", method="open", published_on=pub,
                          closes_on=pub + pd.Timedelta(days=21), award_date=pub + pd.Timedelta(days=40),
                          award_value_kes=rng.uniform(4.5e6, 4.99e6), quantity=1, supplier=rng.choice(sup),
                          bidder_count=4, planted="bunch"))
    df = pd.concat([df, pd.DataFrame(extra)], ignore_index=True)

    def mangle(name: str) -> str:   # realistic supplier-name noise
        r = rng.random()
        if r < .06: return name.upper().replace("LTD", "LIMITED")
        if r < .11: return name.replace(" Ltd", ", Ltd.")
        if r < .14: return name.replace("Supplier", "Suplier")
        return name
    df["supplier"] = df["supplier"].map(mangle)
    df["award_id"] = [f"A{i:05d}" for i in range(len(df))]
    df["source_url"] = "https://example.invalid/synthetic/" + df["award_id"]
    return df[[*REQUIRED_COLUMNS, "planted"]]
