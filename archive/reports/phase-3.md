# Phase 3 verification — PASS

Decision: proceed to Phase 4 refresh and handoff packaging.

Created `src/build_site.py`, `src/viewer_template.html`, `src/verify_browser.py`, `site/index.html`, browser result JSON and desktop/mobile screenshots in `reports/`. Build is deterministic from canonical JSON; it embeds escaped JSON and sanitized rich text, loads only relative local media, uses no server/CDN/fonts/API/login and fetches no separate JSON at runtime.

Commands: `python3 src/build_site.py`, `.venv/bin/python src/verify_browser.py`, `python3 -m py_compile src/*.py`, `.venv/bin/python -m pytest -q`. Regression tests 18 passed. Real Chrome verification: **20 checks passed**, **zero runtime errors**, **zero remote requests**, with `file://`, browser networking disabled and HTTP(S) request interception. Clipboard API was disabled to exercise selectable-text fallback. Evidence: `reports/browser.json`, `gallery-desktop.png`, `gallery-mobile.png`.

Verified78 event cards/109 dates/24 images; all card images load as file URLs. October 2025 filters yield16 IDs/18 dates; zero month yields labelled empty state; full-body search, long text, exact copy text, local full-size image download, no-image case, five-date multi-day record, missing-end warning, native modal Escape and390px mobile layout all pass. Outbound original links are clearly labelled as requiring internet. Images/captions/alt/source dates and provenance are visible. Source-null summary/description remain separate and visibly labelled.

Independent read-only code/output review checked234 rich fields and137 outbound links: no blocked elements/attributes, unsafe URL schemes, remote image sources or script-breaking payload characters. Fixed future-refresh capture-date display and saved-image count semantics. Initial browser launch required approved process access in this sandbox; the test harness's eval-based wait was incompatible with the deliberately restrictive CSP and was replaced with inspector polling. A real mobile filter overflow was found and fixed before the final passing run. These failures did not change source data.

Limitations: tested in installed Chromium on macOS, not every browser. Browsing/selecting text works without clipboard support. Original linked sites/PDFs/online meetings require internet; their contents are not archived. The gallery is a view of preserved public responses and does not establish missing historical coverage.
