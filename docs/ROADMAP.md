# Roadmap

Each phase has an exit criterion. Do not start the next phase until the previous one passes.

| Phase | Goal | Exit criterion |
|---|---|---|
| **0. Prototype** *(this repository)* | Prove the evidence-first review loop on synthetic data | Tests green; design reviewed; method documented |
| **1. Feasibility on real data** | Audit sources; measure coverage against budget and expenditure totals | Written go/no-go: at least 60% of awards in pilot entities have value, date, method and supplier, and coverage against budget meets an agreed floor |
| **2. Private pilot** | One oversight or journalism partner; canonical award ledger with provenance; supplier resolution with a 1,000-pair gold sample; Postgres | Expert blind review of 50-100 alerts reports precision@k and kappa; legal and ethics review passed |
| **3. Depth** | Conformal price model with specification extraction; budget-to-payment-to-project reconciliation; identifier-weighted relationship evidence; OCR with human-verified money fields | Per-indicator validation published |
| **4. Institutional** | Case workspace, right-of-reply tracking, evidence-pack export with custody log, SSO and row-level security, data-sharing agreements | Pen test passed; governance board seated |
| **5. Public release** | Public coverage dashboard and open methodology; publication policy and fairness audits in force | Quarterly fairness audit published; correction process tested |

## Near-term engineering backlog
- Versioned, effective-dated threshold table instead of a single configurable number
- Smooth counterfactual density for bunching, and bid-rotation tests when bid-level data exists
- Change-point detection with end-of-fiscal-year seasonality removed
- Open Contracting Data Standard import and export
- Splink for supplier resolution at scale
- Accessibility audit with screen readers; Swahili interface strings
- API layer (FastAPI) over the existing library

## Deliberately out of scope
Scoring people, kinship or ethnicity inference, leaked data, "corruption probability", and any public ranking of named entities.
