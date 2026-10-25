"""Supplier entity resolution (v0): rule-based normalisation plus optional conservative fuzzy merge.

Design rules: merges are logged, originals are kept in `supplier_raw`, tokens containing
digits must match exactly, and a false merge is treated as worse than a false split.
"""
from __future__ import annotations

import difflib
import re

import pandas as pd

from .config import UNKNOWN_SUPPLIER

SUFFIXES = {"LTD", "LIMITED", "LLC", "INC", "CO", "COMPANY", "CORP", "CORPORATION", "PLC", "THE"}
VARIANTS = {"MOHAMMED": "MOHAMED", "MUHAMMAD": "MOHAMED", "MOHAMAD": "MOHAMED",
            "SUPPLIERS": "SUPPLIER", "ENTERPRISE": "ENTERPRISES"}


def norm_name(name) -> str:
    text = re.sub(r"[^A-Z0-9 ]", " ", str(name).upper().replace("&", " AND "))
    return " ".join(VARIANTS.get(w, w) for w in text.split() if w not in SUFFIXES)


def _digit_tokens(key: str) -> tuple:
    return tuple(w for w in key.split() if any(ch.isdigit() for ch in w))


def resolve_suppliers(df: pd.DataFrame, fuzzy: bool = False, threshold: float = 0.90) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df.copy()
    out["supplier_raw"] = out["supplier"]
    known = out["supplier"] != UNKNOWN_SUPPLIER
    out["_key"] = out["supplier"].map(norm_name)
    counts = out.loc[known, "_key"].value_counts()
    keys = list(counts.index)
    parent = {k: k for k in keys}
    score: dict[str, float] = {}
    if fuzzy:
        for i, a in enumerate(keys):
            for b in keys[:i]:
                if a[:1] != b[:1] or _digit_tokens(a) != _digit_tokens(b) or parent[a] != a:
                    continue
                ratio = difflib.SequenceMatcher(None, a, b).ratio()
                if ratio >= threshold:
                    parent[a], score[a] = parent[b], ratio
                    break
    if known.any():
        display = out.loc[known].groupby("_key")["supplier_raw"].agg(lambda x: x.value_counts().index[0])
        out.loc[known, "supplier"] = out.loc[known, "_key"].map(lambda k: display[parent[k]])
    merges = (out[out["supplier_raw"] != out["supplier"]].groupby(["supplier_raw", "supplier"]).size()
              .reset_index(name="awards"))
    merges["rule"] = [f"fuzzy {score[norm_name(r)]:.2f}" if norm_name(r) in score else "normalised-exact"
                      for r in merges["supplier_raw"]]
    return out.drop(columns="_key"), merges
