# Project Specification: Texas A&M OSCE LiveWhale Archive

## Purpose and users

The Office of Sustainability & Campus Enrichment needs a reusable reference library of previously published calendar events, especially for creating next year's entries from prior copy, image, and logistics. Intended users are staff and incoming student technicians who may not be technical.

**Archive interval:** 2025-08-01 through 2026-12-31 inclusive. **Source scope:** the public `Office of Sustainability` LiveWhale group at `calendar.tamu.edu`, not every university calendar. Do not add unrelated groups unless requested; a page may show shared events, so check ownership and provenance. The final extraction should include records still publicly available when run and accurately characterize inaccessible historical items.

## Source hierarchy

1. Official LiveWhale JSON API, scoped by group and monthly date range, with `response_fields/all` during discovery.
2. Individually publicly accessible event detail pages and public media endpoints, only as needed to fill gaps.
3. Public iCal/RSS/CSV feeds as comparison or fallback, not as sole canonical source unless discovery proves JSON inadequate.
4. Wayback snapshots as explicitly labelled recovery sources for missing public data, never presumed comprehensive.
5. Browser automation/TinyFish only when a tested page actually requires it.

**Starting API template (verify, do not hard-code without a test):**

`https://calendar.tamu.edu/live/json/events/group/Office%20of%20Sustainability/start_date/YYYY-MM-DD/end_date/YYYY-MM-DD/response_fields/all/`

Try version-specific paths only as needed. Read `meta.total_results`, `meta.total_pages`, `links.next`, `data`, and supported response fields. API documentation notes that event feeds default to future events without date filters; API v2 supports rich fields and pagination. LiveWhale may emit a record per day for recurring or multi-day events; examine `/hide_repeats/true/` only as a supplementary comparison, not as a substitute for preserving occurrences.

## Recommended canonical data model

### `data/events.json` (one logical event per original identifier)

- `event_id`, `group_id`, `group_title`, `title`
- `original_url`, `source_urls`, `first_seen_at_utc`, `last_seen_at_utc`
- `summary_html_original`, `description_html_original`, `summary_text`, `description_text`
- `location`, `location_title`, `online_url`, `contact_info_html_original`, `cost`, `registration` as available
- `categories`, `tags`, `status`, `last_modified_source`
- `image_asset_ids`, `thumbnail_caption`, `thumbnail_alt`
- `raw_source_refs` and a `missing_fields`/`warnings` array
- Other returned fields should survive in `source_fields` or original raw JSON rather than being silently discarded.

### `data/occurrences.json` (one time slot/date occurrence per event)

- `occurrence_id`: stable from original ID plus start timestamp/date and end timestamp/date when needed
- `event_id`, `start_iso_original`, `end_iso_original`, `timezone`, `all_day`
- `display_start_local`, `display_end_local`, `recurrence_source_fields`
- `source_refs`, `warnings`

### `data/assets.json` (one file per unique downloaded asset)

- `asset_id`, `event_ids`, `source_url`, `local_path`, `mime_type`, `byte_size`
- `width_px`, `height_px`, `sha256`, `downloaded_at_utc`
- `caption`, `alt_text`, `download_status`, `warnings`

Preserve raw fields in raw snapshots even if the normalized schema omits them. Use consistent output schemas, and supply at least one sample in docs. Never mistake a thumbnail for the original just because the link resolves.

## Required directory layout

```
archive/
  raw/                   # source response files + retrieval manifest
  data/                  # normalized JSON
  assets/images/         # physical images
  exports/events.csv     # flattened spreadsheet-friendly view
  site/index.html        # offline, self-contained search interface
  reports/coverage.csv
  reports/qa.md
  reports/progress.md
  README.md              # staff handoff
  manifest.json          # counts and SHA-256s
```

`index.html` should be portable when opened from disk with `file://` and not rely on fetching a separate JSON file, a CDN, a server, or network access. Embed a safe compact data payload at build time or generate the gallery as static markup, with local relative asset links. Keep canonical source JSON separate.

## User-facing features

- Search title, summary, description, venue, topics.
- Filter by year/month and optionally topic/category.
- Event cards with thumbnail and date; detail view with copy-ready title/summary/full description, original date/time, location, source URL, and locally archived image.
- Option to copy content to clipboard where browser permissions allow; always make the text selectable and readable without clipboard support.
- Visible indicator for missing media or incomplete fields, rather than broken placeholders.
- Display image captions and alt text when available. Basic keyboard navigation and responsive layout.
- Original external URLs should be presented as provenance, not relied upon for operation.

## CSV / Sheets export

Flatten to one row per **event occurrence** or include `occurrence_count` and a separate occurrences CSV. Explain the grain in the CSV header/documentation. Essential columns: original ID, title, date, time, location, summary plain text, full description plain text, HTML field or local reference, image path, original image URL, image caption, original event URL, topic/tags, completeness flags. Never put bare formulas from untrusted text into a spreadsheet: escape values starting `=`, `+`, `-`, `@` for CSV formula injection.

Google Sheets import is an optional downstream publishing step, *not the only copy*. If Drive is used, upload **real image files** and update Sheet links to the archived copies. Do not assume a local relative path becomes a working Google Sheet hyperlink.

## Acceptance criteria

1. All 17 calendar months requested have attempted API coverage and documented status, including zero-result months and failures.
2. Every API page is traversed or a failure is documented; totals reconcile against raw monthly counts, with recurrence semantics explained.
3. Each archived event has retained original source metadata and all publicly exposed relevant text fields (including HTML when supplied).
4. Images available through tested public endpoints are downloaded; failed/missing images are reported by ID and reason. Higher-resolution retrieval strategy and actual dimensions are documented.
5. Raw and normalized data are saved, and output can be rebuilt without LiveWhale access.
6. The offline site works with networking disabled, opens directly from `index.html`, searches, and displays local images.
7. The CSV can be opened in Sheets/Excel and is documented. No material data is silently lost or fabricated.
8. An independent spot-check compares a risk-based sample of original live pages to archive records, with discrepancies explicitly recorded.
9. Final ZIP includes documentation and a SHA-256 manifest. Any gaps are prominently disclosed.
