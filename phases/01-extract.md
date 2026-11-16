# Phase 1 | Complete Preservation Pass (Highest Priority)

## Goal

Capture all publicly retrievable event evidence and locally downloaded media **before** building the viewer.

## Tasks

1. Implement `src/fetch_events.py` and a minimal config for inclusive dates 2025-08-01..2026-12-31 and group `Office of Sustainability`. Query month-by-month, use explicit date parameters and follow every pagination link; record zero-result months distinctly from request failures.
2. Write **untouched source JSON** to `raw/YYYY-MM/page-XXX.json` and `raw/manifest.json`, recording URL, fetch time UTC, status, content length and checksum. Avoid overwriting prior snapshots without retaining history.
3. Verify and store each public event ID and event occurrence; avoid duplicate canonical events. Preserve all raw fields and HTML rich text, including embedded links. Retain original timezone/date formats.
4. Implement `src/download_assets.py` to capture each exposed event image; try documented higher-res source variants only after testing. Verify bytes and MIME, infer dimensions from files, compute SHA-256, and store descriptive filenames that are stable across runs. Avoid fetching the same asset repeatedly.
5. Store image caption/alt/credit fields and original URL alongside the local asset. Preserve remote URL for provenance but never treat it as the only backup.
6. For absent full descriptions or image data, compare public event detail pages when genuinely useful. Record where data was absent at source vs extraction failure.
7. Retry transient failures with timeouts/backoff and a low request rate. Make reruns incremental and idempotent.
8. Produce initial `data/events.json`, `data/occurrences.json`, `data/assets.json` along with a first draft `reports/coverage.csv`.

## Phase gate

- Every month in the requested interval attempted and listed in coverage report; monthly API result counts recorded.
- All pages retrieved or precisely identified as failed.
- Raw JSON saved for each successful page, plus local media downloads and checksums.
- Document unique logical events vs occurrences separately. No silent dedupe of repeat dates.
- Main preservation artifacts exist even if viewer is not built.
