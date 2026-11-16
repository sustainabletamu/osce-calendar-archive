# OSCE public event archive

This archive preserves the public **Texas A&M Office of Sustainability** calendar for **August 1, 2025–December 31, 2026**, captured November 16, 2026. It contains **78 source event IDs, 109 dated display occurrences and 24 downloaded event images**. All 17 monthly API requests succeeded; four months returned zero rows. This is a verified public snapshot, **not a proven complete historical database**.

Deleted, hidden, unpublished and otherwise inaccessible records may be absent. December 2026 is still future relative to capture and may receive more events. Empty months do not prove that no historical events existed. Some text/media may have changed since original publication. No administrator credentials, private exports or fabricated records/media were used.

## Open and reuse an event — no internet or software setup

1. Extract the entire ZIP. Keep its `archive` folder together.
2. Open `archive/site/index.html` by double-clicking it. A current browser is sufficient; you do not need Codex, Python, Google login, a server or LiveWhale.
3. Search for a title, phrase, topic or venue. Try **Campus Earth Day** or **Hullabloom**. Year, month and topic filters work together; **Clear filters** restores all 78 records. Dates use **America/Chicago**.
4. Select a card to open its full record. Read separate **Summary** and **Full description** sections, all captured dates, location, captions/alt text and source details.
5. Use **Copy title**, **Copy summary** or **Copy full description**. If your browser blocks clipboard access, the gallery reveals and selects the plain text; press **Command+C** on Mac or **Ctrl+C** on Windows. You can always open **Selectable plain text**, select and copy manually.
6. Use **Save archived image** below the photo. It opens/downloads a real local full-size public copy. The same files live in `assets/images/`; `data/assets.json` and `reports/media-inventory.csv` map filenames to source URLs, resolutions, captions/alt claims and event IDs. They are not just remote links. No separate credit value was supplied by the monthly feed; supplied captions and image metadata are preserved without inventing credits.
7. Press **Escape** or **Close** to return to results. Original event/online links require internet and are for provenance; the archive itself works offline.

The record count uses original source IDs. Some weekly instances have different IDs and remain separate cards. Multi-day events can have several calendar dates under one ID; those dates are display rows of the same spanning event, not necessarily separate sessions. No missing end time has been inferred. Missing media and empty summary/full-description/location fields are labelled explicitly.

## Spreadsheet use

`exports/events.csv` has **one row per occurrence (109 data rows)**. A multi-day event's full copy repeats on each daily row. `exports/occurrences.csv` is a smaller date/identity table. Both are UTF-8 with a BOM for Excel; quoted multiline fields retain complete text. Formula-like source values are prefixed with an apostrophe for spreadsheet safety; exact originals remain in JSON/raw evidence.

Open the CSV in Excel, or in Google Sheets choose **File → Import → Upload** and select `events.csv`. Choose comma separation and disable conversion of text to numbers/dates/formulas if the import dialog offers it, to retain IDs and source strings. Date/time columns already use the stated timezone. The CSV includes copy text, original HTML, local image paths, original image/event URLs, topics and missing-field flags.

Local paths such as `assets/images/photo.jpg` **do not become usable Google Sheets image hyperlinks**. To share photos through Drive, manually upload the actual image files, choose the intended access permissions, then replace/add Sheet links with those Drive file URLs. The requested downstream Drive copy now contains a native Sheet and 24 actual image files; existing sharing permissions were not changed. Drive links are delivered separately and excluded from this public copy. A Sheet is a downstream working view; **JSON and downloaded images remain the source of truth**.

## What is included

| Path | Purpose |
|---|---|
| `raw/snapshots/` | Two immutable 17-month source acquisitions,34 response pages total |
| `raw/samples/` | Discovery JSON, docs, feeds, robots, HTML, ICS and sample media |
| `raw/media/` | Untouched image response bodies and provenance |
| `raw/qa/` | Eight independent public page checks and two individual JSON checks |
| `raw/manifest.json` | Index of the latest extraction; per-snapshot history remains intact |
| `data/events.json` |78 original IDs, original HTML, derived text, all returned fields and provenance |
| `data/occurrences.json` |109 stable date/time keys and original nullable date fields |
| `data/assets.json` |24 unique image hashes/files with per-event caption/alt claims |
| `assets/images/` |24 event images plus 2 retained discovery thumbnails |
| `site/index.html` | Embedded searchable gallery; only local relative image dependencies |
| `exports/` | Spreadsheet-friendly occurrence-grain CSV files |
| `reports/` | Per-phase gates, actual counts, coverage, omissions, QA and screenshots |
| `docs/` | Schema notes and a labelled real-record example |
| `src/`, `tests/` | Rebuild, preservation, integrity and browser-verification code |
| `manifest.json` | File sizes/SHA-256, counts, acquisition scope and limitations |

Missing source fields among 78 IDs: 49 full descriptions, 8 summaries, 31 contact fields, 28 structured locations/online URLs and 8 images. Every record has at least a summary or full description. 31 timed occurrences have no end time. These omissions are not silently filled. Full-size public copies are verified image bytes/dimensions, not proven original camera/upload files. Linked PDFs, external websites and online meetings are not preserved beyond their outbound URLs.

The zero-result months are **2025-08,2026-07,2026-08,2026-12**. See `reports/coverage.csv` for exact monthly counts. `reports/qa.md`, `reports/independent-audit.md` and `reports/phase-4.md` describe verification and limits.

## Rebuild without contacting LiveWhale

Use Python 3.11 or newer for maintenance. No third-party packages are needed for the data, media reconstruction, gallery or manifest scripts. From this extracted `archive` directory:

```bash
python3 src/download_assets.py --offline
python3 src/normalize.py
python3 src/validate.py
python3 src/build_site.py
python3 src/compare_snapshots.py
```

The first command reconstructs assets/metadata from saved image response bytes and refuses network retrieval. All canonical JSON, images, CSV and HTML can be rebuilt from `raw/`; the test suite verifies this in a clean temporary directory with sockets denied. Previously captured events remain even if absent from the latest feed, labelled `preserved_from_earlier_snapshot`. All source variants remain in `source_fields`; the most recent observation is selected for display. Do not edit `raw/` or throw it away. Keep independent copies of the entire archive in office storage and a second backup location.

Developer checks (package installation requires internet once):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python src/verify_browser.py
```

The browser check uses installed Google Chrome on macOS, or Playwright Chromium elsewhere. Install the latter with `.venv/bin/python -m playwright install chromium` if necessary, or pass `--browser-executable /path/to/chrome`. It opens `file://` with browser networking disabled. Viewing the existing gallery requires none of these tools. Test dependencies: pytest 9.0.2 and Playwright 1.58.0; production scripts use the Python standard library.

## Refresh while the public service exists

Run from the extracted archive directory with public internet access:

```bash
python3 src/fetch_events.py --refresh
python3 src/download_assets.py
python3 src/normalize.py
python3 src/validate.py
python3 src/build_site.py
python3 src/compare_snapshots.py
```

The first command creates a fresh timestamped snapshot, never overwriting source bodies. Without `--refresh`, an already complete extraction is cached. Image retrieval reuses verified saved bytes and downloads newly exposed source URLs. Check `reports/coverage.csv`, `reports/validation.json` and `reports/snapshot-changes.json` before treating a refresh as successful. Cached media is an acquisition-time public copy; the service could later change bytes behind an unversioned URL. Earlier source observations are retained across refreshes; gallery first/last seen times and visibility flags explain them. The supplied 19 tests cover data preservation, security and offline reconstruction. For a new delivery, run browser checks and update the date-specific narrative reports/README as well as generated data.

Source template, verified before extraction:

```text
https://calendar.tamu.edu/live/json/v2/events/group/Office%20of%20Sustainability/start_date/YYYY-MM-DD/end_date/YYYY-MM-DD/response_fields/all/show_archived/both/paginate/100/
```

The collector follows every actual next-page link, checks totals/pages/ownership and flags the 1000-result query cap. It uses serial one-second delays, 35-second timeouts and bounded exponential retries. No hidden/unpublished setting is used. A changed or inaccessible API is a reported limitation, not a reason to request administrator access. To extend the date interval, update `months()`/scope values in the scripts and matching documentation and tests first; the delivered interval is intentionally fixed. A new interface can consume the same JSON/images without re-scraping.

To generate and check another ZIP:

```bash
python3 src/package_archive.py --zip-path /path/to/output.zip
python3 src/verify_package.py /path/to/output.zip
```

The ZIP has a sibling `.zip.sha256` checksum. `manifest.json` inventories every included file except itself to avoid a circular self-hash; the external ZIP hash covers the manifest too. On macOS use `shasum -a 256 filename.zip`, or `sha256sum filename.zip` on Linux, and compare to the sidecar. Editing files after packaging requires regenerating the manifest/ZIP. Final clean-extraction/browser verification results are also supplied alongside the delivered ZIP.

## Published copies and gallery update

GitHub repository: https://github.com/eliottelin/osce-calendar-archive. Enable Pages from main / (root). The Drive Sheet and 24 real image files were delivered privately; Drive URLs and file IDs are excluded from this public repository. Canonical JSON and local images remain the source of truth. Clicking outside an event detail closes it; interior clicks and text-selection drags keep it open.

The public repository omits response-header dump files and minimizes HTTP metadata to content type/length, status, acquisition time, source URL and body checksum. Cookies, diagnostic HTML page captures with third-party client API keys, and private Drive publication artifacts are excluded. Untouched original responses and metadata remain in the local preservation ZIP. Event/API response bodies and downloaded image bytes are unchanged.
