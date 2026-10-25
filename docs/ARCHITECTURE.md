# Architecture

## Today (prototype)
    CSV / portal export
       -> cleaning.prepare        parse money and dates, map methods, flag quality, count what is dropped
       -> resolution              normalise supplier names, optional conservative fuzzy merge, keep originals
       -> indicators              CONC, METHOD, TIMELINE, THRESH, PRICE -> Signal objects with baseline text
       -> alerts.build_alerts     group by award, count independent families, assign tier and evidence grade
       -> pipeline.Result         one object holding awards, merges, tables, signals, alerts
       -> streamlit_app           Today, Review, Insights, Activity, About
       -> audit.AuditLog          reviewer decisions with a SHA-256 hash chain (SQLite, private per session)

| Module | Responsibility |
|---|---|
| `config.py` | `Settings` (frozen dataclass) and constants. Every threshold is explicit |
| `schema.py` | Input contract |
| `cleaning.py` | Parsing, normalisation, quality flags. Never silently invents data |
| `resolution.py` | Supplier entity resolution v0 |
| `indicators.py` | Indicator catalogue (`INDICATORS`) and detectors returning `Signal` |
| `alerts.py` | Tiering and evidence grade |
| `audit.py` | Reviews and tamper-evident log |
| `synthetic.py` | Benchmark data with planted ground truth |
| `pipeline.py` | Orchestration |
| `ui/` | Theme and HTML components. No analysis logic |

## Decisions (short ADRs)
1. **Statistics before machine learning.** No valid labels exist. See `METHODOLOGY.md`.
2. **Library separate from UI.** The analysis package has no Streamlit dependency, so a FastAPI service, a notebook or a batch job can reuse it.
3. **Signals carry their own explanation.** Each `Signal` holds the detail and the baseline text, so an alert can always show *compared with what*.
4. **Settings are data, not code.** A frozen `Settings` object makes runs reproducible and cacheable.
5. **SQLite audit log, hash-chained.** Simple and testable now. In production the same interface moves to Postgres with append-only permissions and an immutable evidence store.
6. **One private log per visitor.** A public demo must never share reviewers' notes between visitors.
7. **Synthetic data with planted truth.** Detectors are tested against known patterns on every commit.
8. **Fonts bundled.** The design must not depend on external CDNs or fail offline.

## Target production architecture
    Ingestion workers (queue) -> object store with object lock (immutable raw: HTML, PDF, WARC, SHA-256)
       -> Dagster asset graph + dbt -> Postgres (PostGIS, pg_trgm, pgvector)  [bronze / silver / gold]
       -> Splink entity-resolution service with a reviewer UI
       -> OCR / layout service (born-digital first, human-verified money fields)
       -> indicator service (versioned definitions, effective-dated threshold table)
       -> graph analysis (identifier-IDF weighted, temporally valid, at most three hops)
       -> FastAPI + web front end, OCDS-compatible export
       -> Keycloak SSO + MFA, row-level security, Vault / KMS, Prometheus / Grafana, Terraform, CI

Principles: immutability of raw data; bitemporal facts (valid time and record time); field-level provenance (document, page, method); merges as reversible links, never overwrites; reproducibility from a dated snapshot plus a code version.
Volume is modest (hundreds of thousands to low millions of rows), so scale people and process before hardware. Data quality, entity resolution, legal risk and trust are the bottlenecks, not compute.
Align with the Open Contracting Data Standard so partners can reuse outputs.

## Security (production)
Threats include political or legal pressure, data poisoning to implicate a competitor, insider leaks, prompt injection through documents, and harassment of staff.
Controls: SSO with MFA; role and case-level access; field-level protection of identifiers (store an HMAC, never the number); append-only audit; pinned dependencies and SBOM; sandboxed document parsers; document text treated as untrusted; tested encrypted backups; a penetration test before any public launch.
