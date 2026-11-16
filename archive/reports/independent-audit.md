# Independent read-only preservation audit

Audited 2026-11-16 using publicly accessible pages and documented individual JSON endpoints. No production files changed. Eight pages and two individual JSON responses returned HTTP 200, serial requests with one-second spacing, no authentication. Exact original bodies, response headers, UTC acquisition, URL, status, byte size and SHA-256 are saved below.

## Risk-based sample

| ID | Selection reason | Public page result |
|---|---|---|
|359400|2025 cross-month multi-day event|Title/start/summary/image match; five daily occurrences Sept29-Oct 3 retained. Page end describes entire span; API individual daily ends null.|
|363287|2025 weekly recurrence after daylight-saving change|Title, UTC instants, 13:00-15:00 America/Chicago, Pavilion, summary and image match. Distinct source ID retained.|
|379688|Longest preserved full description, 2026|Title, dates, Teaching Gardens Pavilion, summary, image match. API body 1576 plain chars. Separate individual JSON confirms exact summary327 HTML chars, description 2938 HTML chars, contact HTML.|
|362803|No-image online event, 2025|Title/start/end/summary/Zoom URL match. Public JSON-LD also lacks event image.|
|386913|2026 summary-only event with absent end|Title/start/summary/image match. API end null retained. JSON-LD synthesizes end=start; not promoted to canonical end.|
|377642|2026 media-rich event with separate summary/full description|Title/start/end/MSC Rudder Plaza/summary/image match. Individual JSON confirms exact summary252 HTML chars, description 863 HTML chars, contact HTML.|
|386908|2026 multi-day all-day event|Title/start/summary/image match; eight daily occurrences Oct 1-Oct 8 retained. Span end only in recurrence fields/page metadata.|
|374684|2026 missing summary, full description present, missing end|Title/start/full description/image match; API end null retained despite JSON-LD end=start.|

Titles8/8, start instants8/8, explicit timed ends4/4, nonempty locations4/4, event image identifiers7/7 and no-image absence1/1 match. JSON-LD description equals API summary7/8 and full description 1/8. Static page bodies use JavaScript templates; JSON-LD does not independently expose the two long full bodies, so documented public individual JSON routes were used to close that gap. Both match exact original HTML 2/2. No unexplained extraction discrepancies found. Four end-field differences are source-representation differences, not inferred corrections: two multi-day span ends and two synthetic end=start values. Image-object dimensions from JSON-LD are cropped render metadata, sometimes zero, and were not used as source-file dimensions.

## Independent offline reconciliation

- Seventeen monthly raw pages: all HTTP200, all body SHA-256/size checks pass. Each page's row count equals meta.total_results; all links.next null. Empty months report meta.total_pages=0.
- Monthly raw rows Aug 2025-Dec 2026: 0,6,18,10,2,2,7,6,19,9,5,0,0,2,18,5,0 =109.
- Raw109 rows =109 unique ID/start/end keys =109 canonical occurrences. Raw78 unique source IDs =78 canonical events. No duplicate occurrence keys, omitted raw keys, invented keys, ownership mismatch, altered first-observed original summary/description HTML or inferred null ends found.
- All 109 rows gid282. America/Chicago start conversions109/109 match. Per-event occurrence_count sums reconcile.
- Five multi-day IDs retain daily display rows:359400(5),377612(5),382069(13),384637(5),386908(8). These are display-day occurrences of spanning events, not separate independently scheduled events. Eleven weekly source IDs remain separate logical records; no invented series merging.
- Twenty-four local files,20,737,236 bytes,24 distinct SHA-256s; all MIME/width/height checked independently from PNG/JPEG bytes. Fourteen JPEG and10 PNG. Hash/size/dimension/MIME24/24 pass. All event asset references resolve. Caption/alt claims preserve event values for all 70 events with media. Eight events have no image;49 null descriptions and8 null summaries remain disclosed rather than filled.

## Evidence and commands

Capture commands: `python3 /tmp/osce-qa/audit_pages.py`; `python3 /tmp/osce-qa/audit_fulltext.py` (network access). Offline checks: `python3 /tmp/osce-qa/check_archive.py`; `python3 /tmp/osce-qa/check_dimensions.py`.

- `/tmp/osce-qa/{359400,363287,379688,362803,386913,377642,386908,374684}.html`
- Each has same-stem `.headers` and `.meta.json`.
- `/tmp/osce-qa/{379688,377642}-individual.json`; same-stem `.headers` and `.meta.json`.
- `/tmp/osce-qa/page_comparison.json`
- `/tmp/osce-qa/fulltext_comparison.json`
- `/tmp/osce-qa/archive_checks.json`
- `/tmp/osce-qa/media_checks.json`

Individual JSON routes: https://calendar.tamu.edu/live/events/379688@JSON and https://calendar.tamu.edu/live/events/377642@JSON. Original sample page URLs are in every capture metadata file and page_comparison.json.

## Limits and gate

This is a risk-based eight-event audit of the successfully returned public data, not evidence of every historical publication. Deleted, hidden, unpublished and inaccessible content remains unknown. Zero months do not establish that no events ever existed. Full-size image means preserved verified public source dimensions, not proof of an original camera file or historical revision. External linked PDFs, Zoom meetings and linked websites are not included as offline content. No remaining preservation mismatch blocks proceeding to viewer work; acceptance still requires offline rebuild tests, HTML security tests, browser file:// checks and final package verification by the coordinator.
