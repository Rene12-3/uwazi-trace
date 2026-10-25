# Methodology

Uwazi Trace answers one question: **where should scarce review capacity go first, and what is the evidence?**
It does not estimate who is corrupt. Corruption has no reliable labels (see `VALIDATION.md`), so a supervised "corruption model"
would learn what investigators chose to pursue, not what happened. Instead the system uses transparent statistics against visible baselines.

## 1. Compare like with like
Every indicator compares an award or pattern with a **peer cohort**: the same category, across entities, over comparable periods.
A cohort needs a minimum number of comparators (default 8 peer entity-years, 5 awards in the focal cohort). Below that, the indicator stays silent.
Silence means "not enough evidence to compare", never "fine".

## 2. Shrink small samples
An entity with three awards will look extreme by chance. For concentration, the observed share is pulled toward the peer median in proportion to sample size:

    shrunk = (share * n + m * peer_median) / (n + m)        with m = 5

A flag also requires a Wilson lower bound on the award-count share to exceed the peer median, so a lucky small cohort cannot trigger it.

## 3. Calibrated price intervals
Prices use `log(unit price) ~ log(quantity)` with a robust (trimmed) fit. Out-of-fold residuals (5 folds) give a split-conformal one-sided upper bound at miscoverage `alpha`.
An award is flagged only when it is above the bound **and** the estimated excess exceeds a materiality floor. On clean data the exceedance rate matches alpha (tested in `tests/test_indicators.py`).
By construction about `alpha` of perfectly normal awards will exceed the bound, which is why materiality and human review follow.

## 4. Materiality
A tiny anomaly in a small award is not worth a reviewer's afternoon. Every signal carries a KES materiality, and indicators require a floor.

## 5. Independent evidence, not summed evidence
Indicators in the same family are correlated: direct procurement, a short window and a single bidder often travel together. Counting them separately would triple-count one story.
Signals are grouped into **families** (Competition, Process, Price). The **tier** counts independent families that fired:

| Tier | Meaning |
|---|---|
| 1 | Three independent kinds of signal |
| 2 | Two kinds of signal |
| 3 | One kind of signal |

No composite "risk score" is shown, and nothing is ever scored for a person. The production design adds expert-elicited weights and rank-stability intervals (see `ROADMAP.md`).

## 6. Missing is not zero
Unknown bidder counts stay unknown. They are never coerced to one bidder. Unknown suppliers are excluded from supplier-based indicators, so "(unknown supplier)" can never become the biggest supplier in town.
Money parsing is strict: `"1,2oo"` becomes missing, never 12.

## 7. Entity resolution (v0)
Supplier names are normalised (legal suffixes, punctuation, spelling variants). An optional conservative fuzzy merge handles typos, with two guards:
tokens containing digits must match exactly, and every merge is listed with its rule and score. Originals are kept in `supplier_raw`. A false merge is treated as worse than a false split.
People are **not** resolved in this version, by design (see `ETHICS_AND_LEGAL.md`).

## 8. Why not a neural network?
On modest tabular data with scarce, biased labels, robust statistics and gradient boosting match or beat deep models and explain far better. Autoencoders do not beat simple methods here and are harder to defend to an auditor or a court.
GNNs need labels that do not exist. Pretrained neural parts (OCR, multilingual text embeddings) are welcome as *tools*, never as judges. Revisit only after thousands of reviewer-validated outcomes exist, and even then as one input.

## 9. Known limits
- Published awards are a non-random subset. Indicators are conditional on what was published, and coverage is displayed.
- Entities that publish more produce more flags. Never compare raw alert counts between entities.
- Prices do not model specifications. A mobile-clinic fit-out looks inflated, which is why it is the first listed innocent explanation.
- Thresholds and bid-window minimums are assumptions you set. Verify them against the Regulations in force on the award date.
