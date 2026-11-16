# Phase 0 | Public API & Media Discovery

## Goal

Determine the lowest-risk, reproducible way to retrieve public historical OSCE events, including rich descriptions, original dates, repeats, images, captions, and alt text. Time-box investigation; prioritize quickly saving a verified sample.

## Tasks

1. Inspect official https://calendar.tamu.edu/feeds/ and LiveWhale API docs. Verify the exact Office of Sustainability group slug/name and source calendar URL.
2. Test August 2025, October 2025, April 2026, October 2026 and a current month using scoped start/end dates; record HTTP status and exact request URL. Use API `response_fields/all` initially, and inspect `meta`, `links`, and `data`.
3. Test whether `live/json/events` already returns JSON v2; if necessary compare `/live/json/v2/events`. Check a monthly response with more than one page or pagination test route. Never silently truncate at 100 results.
4. Study `summary`, `description`, contact fields, `thumbnail`, `thumbnail_caption`, `thumbnail_alt`, image HTML and image URLs. Check the public detail page for two sample event IDs and record differences.
5. Test how repeating/multi-day events are represented; determine event identity vs occurrence key, and whether `hide_repeats/true` loses relevant occurrence dates.
6. Inspect at least two public event images and determine a documented/reliable method to retrieve the highest available resolution. Confirm actual bytes, MIME and dimensions; note if only thumbnails are accessible.
7. Check whether any site robots/terms restrictions are relevant, and implement bounded, rate-limited retrieval.
8. Optionally compare a public CSV/ICS feed for parity and decide if it offers useful fallback content.

## Evidence to save

- `reports/discovery.md`: endpoint table, successful/failed tests, actual response fields, pagination plan, dedupe strategy, image strategy, limitations and recommendations.
- `raw/samples/`: untouched JSON responses and metadata for at least two months, one individual event if available, and one sample image in `assets/images/`.
- `reports/progress.md`: actions and next steps.

## Phase gate

- At least one past month yields real data and at least one image is locally saved if the events contain media, OR blockers clearly documented.
- A dependable plan exists for traversing every month/page and handling recurrences.
- No need to investigate hidden/admin data. Proceed immediately to preservation if viable.
