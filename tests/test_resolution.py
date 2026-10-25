import pandas as pd

from uwazi.config import UNKNOWN_SUPPLIER
from uwazi.resolution import norm_name, resolve_suppliers


def _df(names):
    return pd.DataFrame({"supplier": names})


def test_normalisation_removes_legal_suffixes_and_punctuation():
    assert norm_name("Acme Traders Ltd.") == norm_name("ACME TRADERS LIMITED") == norm_name("Acme  Traders, Co")


def test_digit_tokens_never_merge_even_when_fuzzy():
    df, merges = resolve_suppliers(_df(["Supplier 007 Ltd"] * 5 + ["Supplier 017 Ltd"] * 5), fuzzy=True)
    assert df.supplier.nunique() == 2 and merges.empty


def test_fuzzy_merges_typo_but_keeps_original_name():
    df, merges = resolve_suppliers(_df(["Kamau Traders Ltd"] * 4 + ["Kamua Traders Ltd"]), fuzzy=True)
    assert df.supplier.nunique() == 1
    assert (df.supplier_raw == "Kamua Traders Ltd").sum() == 1 and len(merges) == 1


def test_fuzzy_is_off_by_default():
    df, _ = resolve_suppliers(_df(["Kamau Traders Ltd"] * 4 + ["Kamua Traders Ltd"]), fuzzy=False)
    assert df.supplier.nunique() == 2


def test_unknown_supplier_is_never_merged():
    df, _ = resolve_suppliers(_df([UNKNOWN_SUPPLIER, "Unknown Supplier Co", "Unknown Supplier Co"]), fuzzy=True)
    assert (df.supplier == UNKNOWN_SUPPLIER).sum() == 1
