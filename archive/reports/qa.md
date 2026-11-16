# Phase 2 verification — PASS

Decision: proceed to Phase 3 offline gallery. Public historical completeness remains unproven.

## Reconciliation and automated tests

Executed `python3 src/normalize.py`, `.venv/bin/python -m pytest -q` (**18 passed**), and `python3 src/validate.py` (**16 validation checks passed, zero errors**). `reports/validation.json` is machine-readable; `reports/coverage.csv` gives all 17 months. Rebuild tests deny socket connections and verify byte-identical canonical/CSV outputs and unchanged raw hashes. Tests cover actual next-page traversal, missing-page detection, recurrence and duplicate grain, DST conversion, missing ends, unsafe/malformed HTML, CSV formulas, asset corruption and preservation across refreshes.

Observed latest snapshot: **109 raw rows = 109 unique occurrence keys**, **78 source IDs**, **24 canonical images /20,737,236 bytes**, **zero request/media failures**. Largest monthly response19; no hidden pagination/cap truncation. Event identity is original ID; occurrence identity is `(ID,date_iso,date2_iso)` with a stable digest. Daily multi-day rows are display occurrences; separate weekly IDs stay separate. All source fields and original HTML survive; canonical text is derived separately. Display uses America/Chicago while source offsets, UTC/epoch dates and recurrence spans remain verbatim. Thirty-one timed occurrences have no end time and retain null plus a warning. No missing end time is inferred from page JSON-LD.

All snapshots are accumulated on rebuild. Records removed upstream remain with `preserved_from_earlier_snapshot` visibility status. All conflicting field variants survive in `source_fields`; current data has no content variants requiring resolution. First/last acquisition times and raw row references remain explicit. `raw/manifest.json` points to the latest extraction; immutable per-snapshot `extraction.json` files retain history.

## Independent audit

A read-only investigator independently checked all 17 raw hashes and all 24 image hashes, sizes, signatures and dimensions. A second investigator independently used system `file` and `sips`: MIME/dimensions matched24/24. Physical image files total26:24 canonical event assets and2 discovery thumbnails. All 24 canonical images are verified full-size public copies; exposed source maximum dimensions agree where present. Original-upload byte identity is not established.

Eight public detail pages were checked: **359400** (2025 multi-day), **363287** (weekly), **379688** (long rich description), **362803** (no image/online), **386913** (2026 long summary), **377642** (media and both text fields), **386908** (2026 multi-day), **374684** (null summary/full description).

All 8 HTTP200; titles8/8 and start instants8/8 agree. Four explicit timed ends4/4 agree. Four API-null ends are not comparable to page ends: JSON-LD supplies the series span or repeats start as end. These are documented representation differences, not inferred canonical end times. All exposed page locations/online URLs agree. Seven page JSON-LD descriptions equal API summary; one equals full description because summary is null. Static JSON-LD omits the separate full body for379688 and377642, so the investigator additionally fetched the documented public individual JSON resources `https://calendar.tamu.edu/live/events/379688@JSON` and `/377642@JSON`: summary, full description and contact HTML exactly match canonical fields2/2. No unexplained content discrepancy was found in this risk-based sample; it does not independently audit every record.

Untouched audit responses and acquisition provenance are in `raw/qa/`. Detailed results: `reports/page_comparison.json`, `reports/fulltext_comparison.json`, `reports/media_checks.json`; investigator methods are retained in `reports/qa-methods/`. These public observations supplement raw feed evidence and do not replace it.

## Missing data and limits

Source-null fields among 78 IDs: **49 descriptions,8 summaries,31 contact fields,28 structured locations/online URLs,8 images**. Every ID has at least one of summary/description. See per-ID `reports/missing-fields.csv`; `reports/media-inventory.csv` gives each actual image resolution. Missing description is not filled with summary. Nulls are neither fabricated nor labelled download failures. No inline images appeared in current rich body fields.

Four months returned zero:2025-08,2026-07,2026-08,2026-12. Deleted, hidden, unpublished or otherwise inaccessible records and prior revisions cannot be established by these public endpoints. Supported public archived-item inclusion was tested and enabled; no hidden/admin setting was requested. December 2026 remains future relative to2026-11-16 acquisition and requires a later refresh. No claim of a complete historical database is supported.

Files added in this phase: repeatable normalization/content security, validation script, regression tests, occurrence-grain CSVs, JSON QA, per-ID omissions/media inventory, saved independent audit evidence. Findings fixed before proceeding: malformed URL handling, content-hash deduplication before file writes, and retaining earlier source observations on future refresh.
