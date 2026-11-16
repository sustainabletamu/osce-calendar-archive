# Phase 2 | Normalize, Reconcile, and QA

## Goal

Turn raw snapshots into a trustworthy, reproducible archive, including rigorous error reporting.

## Tasks

1. Implement repeatable normalization from `raw/` (no live internet required) into `data/events.json`, `data/occurrences.json`, and `data/assets.json`.
2. Choose and document unique event and occurrence keys. Explain which fields of the API represent individual repeat instances or multi-day display rows. Preserve event recurrence rules if present.
3. Normalize datetime for display in America/Chicago but retain original ISO, UTC, end-time, all-day flags, and nulls. Detect impossible dates or mismatched IDs.
4. Keep original HTML strings intact; derive sanitized rich view and plain-text searchable/copyable versions. Handle HTML entities and line breaks correctly.
5. Reconcile raw monthly row counts, duplicated occurrences, unique events, and any failed pages. Report every month including zeros. Avoid claiming historical completeness beyond publicly visible data.
6. Check all media references: file existence, nonzero size, MIME, dimensions, hashes, repeated assets, caption/alt preservation, and thumbnail-vs-full-resolution decisions.
7. Build `exports/events.csv` (and `exports/occurrences.csv` if needed), escaping spreadsheet formula-like leading characters. Clearly explain whether each row is a logical event or occurrence.
8. Write automated tests for: pagination; duplicates; recurrence; timezone; missing end time; HTML sanitization; CSV formula escaping; media hash validation; offline regeneration.
9. Perform a documented independent sample audit, ideally including events from different years/months, recurring events, a long description, no-image event, and media-rich event. Compare original public pages where available; report discrepancy counts and examples.
10. Generate `reports/qa.md`, `reports/coverage.csv`, and `manifest.json` with counts, quality flags, and SHA-256s.

## Phase gate

- Tests run with documented results.
- Full outputs can be regenerated from saved raw files without internet.
- No unexplained pagination gaps, count mismatches, or broken local image references.
- Missing public source data is explicitly labelled rather than silently filled in.
