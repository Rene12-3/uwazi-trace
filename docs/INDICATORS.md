# Indicator specifications

Every indicator is defined **before** it is coded: the question, cohort, baseline, trigger, materiality, innocent explanations and known failure modes.
Use the template at the end to propose a new one.

## CONC: Supplier concentration (family: Competition)
- **Question:** does one supplier take an unusually large share of an entity's spend in a category, compared with peers?
- **Unit:** entity x category x fiscal year (July to June).
- **Baseline:** median and 90th percentile of top-supplier value share across cohorts of the same category with at least 5 awards; at least 8 peer cohorts.
- **Trigger:** shrunk share above peer P90, Wilson lower bound above peer median, top-supplier value at least 5x the materiality floor.
- **Innocent explanations:** framework agreement; earlier open tender; few qualified suppliers in a remote area; proprietary goods; few awards; incomplete capture.
- **Failure modes:** small markets; unresolved supplier names (split shares understate concentration); missing awards.

## METHOD: Non-competitive method share (Competition)
- **Question:** is an unusually large share of spend awarded without open competition?
- **Trigger:** direct, restricted or emergency share by value above peer P90 and above 50%, with non-competitive value at least 5x the materiality floor.
- **Innocent explanations:** declared emergency; sole source; AGPO or preference set-aside; framework call-off; method mislabelled.
- **Failure modes:** emergency periods (treat as a separate regime); inconsistent method labels across portals.

## TIMELINE: Timeline integrity (Process)
- **Question:** do dates break basic process rules?
- **Trigger:** bid window shorter than the configured minimum, or award dated before tender close.
- **Innocent explanations:** shorter window permitted for the method; portal data-entry error; re-advertised tender; emergency.
- **Failure modes:** the minimum is an assumption. **Verify against the Regulations before relying on it.**

## THRESH: Threshold bunching or splitting (Process)
- **Question:** do awards cluster just under an approval threshold, or do repeated small awards add up to more than it?
- **Bunching:** awards in the band 90-100% of the threshold versus 80-90%, per entity, against a global expected share, with an exact binomial test (p < 0.01, at least 8 awards in the two bands).
- **Splitting:** same entity, supplier and category within 30 days, each below the threshold, summing above it.
- **Innocent explanations:** standard-priced items; estimates from a published price list; genuinely separate needs; a different threshold for the entity type.
- **Failure modes:** thresholds vary by entity type, category and year; a production version needs a versioned threshold table and a smooth counterfactual density.

## PRICE: Unit price versus comparable purchases (Price)
- **Question:** is the unit price higher than comparable purchases after allowing for quantity?
- **Scope:** standardised goods only (the demo uses vehicles and laptops). Most works and bespoke services cannot be compared without bills of quantities.
- **Trigger:** out-of-fold residual above the conformal upper bound and estimated excess above the materiality floor.
- **Innocent explanations:** special specification; remote delivery; VAT treatment; bundled warranty or training; mis-extracted quantity.
- **Failure modes:** specifications, inflation (optionally deflated by a setting), mixed cohorts. Recall on planted outliers is intentionally modest (see `VALIDATION.md`).

## Template for a new indicator
1. Question it asks, in plain language
2. Unit of analysis and peer cohort
3. Baseline and minimum comparators
4. Trigger and materiality floor
5. Innocent explanations a reviewer should check first, and the data point that would confirm each
6. Known failure modes and how coverage affects it
7. How it can be validated without prosecution labels
8. Which family it belongs to, and which existing indicators it is correlated with
