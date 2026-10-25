# Data dictionary

One row per contract award. Use `data/sample_awards.csv` as a reference.

| Column | Type | Notes |
|---|---|---|
| `award_id` | text | Unique. Duplicates are removed (first kept) and counted |
| `entity` | text | Procuring entity. In production, resolved to a curated, effective-dated crosswalk |
| `category` | text | Goods/works/services category. Peer cohorts are formed within a category |
| `method` | text | open, rfq, restricted, direct, emergency. Free text is mapped (for example "sole source" becomes direct); unmapped labels are treated as competitive and stay visible |
| `published_on` | date | Tender publication date |
| `closes_on` | date | Bid closing date |
| `award_date` | date | Award date. Rows without it are dropped and counted; it defines the fiscal year |
| `award_value_kes` | number | Strictly parsed. "KES 1,200,000" parses; "1,2oo" becomes missing and the row is dropped and counted |
| `quantity` | number | Needed for unit-price analysis. Missing is allowed for non-standard categories |
| `supplier` | text | Missing becomes "(unknown supplier)", flagged `missing_supplier`, and excluded from supplier-based indicators |
| `bidder_count` | number | **Blank means unknown, never one bidder** |
| `source_url` | text | Link to the source record. Production stores an archived copy with a SHA-256 |

## Derived fields
- `fy`: Kenyan fiscal year, 1 July to 30 June (for example `2023/2024`)
- `dq`: comma-separated data-quality flags (`missing_dates`, `missing_supplier`). Awards with flags receive evidence grade C, otherwise A
- `supplier_raw`: the supplier name as supplied, kept when names are merged

## What is never collected
Personal national ID numbers, tax data, non-public asset declarations, and anything leaked or confidential.
