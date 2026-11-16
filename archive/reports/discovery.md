# Phase 0 verification — 2026-11-16 UTC

Decision: **PASS; proceed immediately to Phase 1 preservation.** Public historical JSON and physical image bytes are available. This verifies access, not historical completeness.

## Saved evidence and commands

Executed `python3 src/discover.py`, `python3 src/discover_followup.py`, and `python3 src/discover_extra.py` with approved public network access. Default sandbox DNS failed; approved network execution succeeded. Immutable bodies and per-request metadata (exact request/final URLs, UTC times, status, headers, length, SHA-256) are in `raw/samples/20261116T205417793634Z/`, `raw/samples/20261116T205451265575Z/`, and `raw/samples/20261116T205530296566Z/`. Two historical detail HTML bodies, an ICS comparison, API documentation, feeds and robots are saved. Four physical sample images (two thumbnails and two full-size public copies) are in `assets/images/`.

## Endpoint tests

The official [feeds directory](https://calendar.tamu.edu/feeds/) publishes the exact Office of Sustainability group and [calendar](https://calendar.tamu.edu/sustainability/). Returned records confirm `gid=282`, `group_title=Office of Sustainability`.

All five monthly requests used `https://calendar.tamu.edu/live/json/events/group/Office%20of%20Sustainability/start_date/YYYY-MM-01/end_date/YYYY-MM-DD/response_fields/all/`; exact URLs are in each `.meta.json`.

| Month | HTTP | Actual API rows | Pages |
|---|---:|---:|---:|
| 2025-08 | 200 | 0 | 0 (one empty response saved) |
| 2025-10 | 200 | 18 | 1 |
| 2026-04 | 200 | 19 | 1 |
| 2026-10 | 200 | 18 | 1 |
| 2026-11 (current month) | 200 | 5 | 1 |

The unversioned route already returns v2 `meta`, `links`, `data`. Explicit `/live/json/v2/events/.../paginate/1/` returns October total 18, 18 pages; following the returned next link returns page 2, different ID 359402 versus 359398. Both saved responses passed inspection. Production will use explicit v2, `/paginate/100/`, traverse actual `links.next`, reconcile all rows/pages with metadata, reject pagination loops, and flag the documented 1000-result query cap. [Official API documentation](https://support.livewhale.com/live/blurbs/json-api) is saved locally.

Documented [`show_archived/both`](https://support.livewhale.com/live/profiles/319-showarchived) was tested publicly without credentials: August remains 0 and October remains 18 (HTTP 200). Production will include this supported public archived-item setting. Hidden/unpublished settings are never requested.

Returned fields include source dates/UTC/offsets/timestamps/timezone, all-day, recurrence bounds, title, URL, summary, description, contact_info, location, online data, registration, cost, status, tags/event_types, editor/last_modified, thumbnail, caption, alt, and sometimes `thumbnail:html`. All raw fields survive. Many events use summary for the main copy and null description; these fields must stay separate and nulls must not become invented descriptions.

## Recurrence and counts

October `hide_repeats/true` returns 13 rather than 18 rows. It removes five relevant dates/instances and is comparison-only. Multi-day ID 359400 has October 1/2/3 rows sharing a September 29–October 3 source span. Weekly Office Hours instances have distinct IDs (363282, 363283, 363284, 363286); do not merge by title. Logical identity = source ID; occurrence identity = ID + original `date_iso` + original nullable `date2_iso`. Occurrence rows are calendar display dates, not necessarily independently scheduled sessions. Preserve recurrence fields without manufacturing dates or end times.

## Images and full text

The supplied 80×80 thumbnails for IDs 359398 and 365922 were saved first. A read-only media investigation verified that retaining the observed `gid` and filename and removing rendering transformations retrieves larger public copies. Coordinator independently saved:

| Tested source | HTTP/MIME | Actual dimensions | Bytes | SHA-256 |
|---|---|---|---:|---|
| `/live/image/gid/282/11132_AGF_Standard_Logo.rev.1695068973.png` | 200 image/png | 1042×1042 | 33882 | c4fd6302924cad987291017c274e8a3bacd6d0722875ccc5828d6563a2de4cae |
| `/live/image/gid/282/11195_3.rev.1695937499.png` | 200 image/png | 1800×1200 | 572406 | 01243bbc88037b914ae793b80b0b451ad4dac26915ddcbb8eba5a0d4b6793d64 |

Dimensions match exposed `data-max` dimensions. Production must verify each response's MIME, signature, dimensions and hash, falling back to the observed thumbnail when necessary. Label these full-size public copies; original-upload byte identity is unproven. [Official responsive-image documentation](https://support.livewhale.com/live/blurbs/image-markup) explains derivatives and format conversion. Preserve image caption/alt and HTML verbatim in canonical data. Null `thumbnail:html` does not imply no image.

Public historical detail pages 359398 and 365922 were saved. The independent investigator also checked 359398 and 363282: JSON-LD plain description matches API summary, so null API description did not imply recoverable longer text on those two pages. Details are runtime calendar shells with JSON-LD; their unrelated university featured content must not enter this group's archive. ICS is comparison-only and is not used to replace richer JSON.

## Policies, failures and limits

Saved robots.txt HTTP 200 disallows only `*?replytocom`; these scoped feed/media requests do not match it. Use sequential requests, one-second delays, 35-second timeouts and bounded exponential retries; respect 403/404 and do not bypass them. One investigation response reported a server throttle wait of three seconds.

The university [calendar policy](https://marcomm.tamu.edu/calendar/policies/) describes the transition before spring 2027 and permits editorial deletion. Public requests cannot establish that deleted, hidden, unpublished, or otherwise inaccessible events are included. August's zero is an observed response, not proof no events happened. December 2026 is future relative to capture and can change. Current source text may differ from what was originally published. No credentials or private endpoints were used; no records or media were invented.

Verification results: historical JSON **PASS**, v2 and next-page traversal **PASS**, scope **PASS**, recurrence comparison **PASS**, two larger physical images **PASS**, robots check **PASS**. Historical completeness **not established**. Production extraction has not yet run at this gate.
