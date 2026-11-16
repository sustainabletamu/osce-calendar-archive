# Phase 1 verification — PASS

Decision: source preservation gate passed; proceed to Phase 2 validation. No interface has been built.

Commands executed: `python3 src/fetch_events.py`, `python3 src/download_assets.py`, `python3 src/normalize.py`. Full extraction snapshot: `raw/snapshots/20261116T205631400633Z/`. Media evidence: `raw/media/20261116T205733047536Z/` plus the earlier verified discovery images. Per-response bodies, metadata and manifests are retained.

All **17 months attempted and successful**, **17 response pages**, **109 raw rows**, **78 unique source event IDs**, **109 distinct display occurrences**, **24 distinct downloaded event image files**, **20,737,236 canonical image bytes**, **0 media failures**. All rows' ownership is group 282 / Office of Sustainability. Four zero-result months are 2025-08, 2026-07, 2026-08, 2026-12. `reports/coverage.csv` records every exact monthly URL, HTTP status, result count and page count. Production uses the tested public `show_archived/both` setting.

Files created: `src/fetch_events.py`, `src/download_assets.py`, `src/normalize.py`, shared content helpers, immutable raw snapshots and response metadata, `raw/manifest.json` latest-snapshot index, `data/events.json`, `data/occurrences.json`, `data/assets.json`, `assets/images/`, `reports/coverage.csv`, and initial occurrence-grain CSV exports.

Checks passed: monthly totals equal saved raw rows; all next links exhausted; no monthly result cap approached (largest 19); no source-group mismatch; all 24 event assets returned HTTP 200 with matching image signature/MIME and positive dimensions; each asset has SHA-256, local bytes, source URL, UTC capture time and caption/alt claims. Full-size public copies range 573×421 to 3200×2133 (also a portrait 2400×3200); exposed maximum dimensions matched wherever supplied. Original-upload byte identity is unproven. Two additional discovery thumbnails remain as evidence and are excluded from the 24 canonical image count.

Initial field observations: 49 of 78 IDs have null description, 8 null summary, 31 null contact_info, 28 no structured location/online URL, and 8 no exposed event image. No ID lacks both summary and description. These are source-null fields, preserved separately; they are not extraction failures. Rich HTML and all original returned fields survive. End times remain null when absent. Multi-day rows remain occurrences, while weekly instances with separate IDs remain separate source identities.

No public-only crawl proves that deleted, hidden, unpublished or inaccessible records are present. December 2026 is still future at capture. Zero responses do not establish absence of historical events. Automated tests and independent live sample auditing are the next phase; the preservation pass is complete for the tested public response scope, not a complete historical database claim.
