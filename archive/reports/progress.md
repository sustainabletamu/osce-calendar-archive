# Preservation progress

## Phase 0 — PASS, proceed to Phase 1

2026-11-16 UTC. Read AGENTS.md, PROJECT_SPEC.md, START_HERE_CODEX_PROMPT.md and all five phase briefs. Coordinator owns production files. Two read-only investigations independently checked API/pagination/recurrence and media/full text.

Files: `src/common.py`, `src/discover*.py`, `raw/samples/*` with untouched bodies/metadata, `assets/images/*`, `reports/discovery.md`. Commands: `python3 src/discover.py`, `python3 src/discover_followup.py`, `python3 src/discover_extra.py`. Historical sample rows: Aug 2025 0, Oct 2025 18, Apr 2026 19, Oct 2026 18, Nov 2026 5. Two full-size public images plus two thumbnails saved. Real page-2 traversal passed; hide_repeats loses five October rows. Public archived comparison adds no rows in the two tested months. Tests/limits and exact evidence are in discovery.md. Public endpoint viable; proceed immediately to all-month raw/media preservation. Historical completeness remains unverified.

## Phase 1 — PASS, proceed to Phase 2

Commands `python3 src/fetch_events.py`, `python3 src/download_assets.py`, `python3 src/normalize.py`. Files and verification: `reports/phase-1.md`; exact monthly counts: `reports/coverage.csv`. All 17 months HTTP200, 17 response pages,109 raw rows,78 event IDs,109 display occurrences,24 canonical images (20,737,236 bytes),0 failed downloads. Four zero months distinctly reported. All raw evidence and physical media were preserved before interface work. Original HTML, nullable dates, source metadata and image claims retained. Automated regression tests and independent live-page audit underway. Historical/public-source limitations remain.

## Phase 2 — PASS, proceed to Phase 3

Commands `python3 src/normalize.py`, `.venv/bin/python -m pytest -q` (18 passed), `python3 src/validate.py` (16 checks passed). Independent audit:8 live detail pages,2 supplemental public individual JSON bodies,17 raw hashes,24 image hashes/MIME/dimensions; no unexplained discrepancies. Evidence imported untouched to `raw/qa/`; see `reports/qa.md` and comparison JSONs. Counts remain78 IDs/109 occurrences/24 images. Source omissions documented per ID;31 timed ends remain null. Offline regeneration identical with sockets denied. Refresh now preserves earlier captures even if source records disappear. Gate passed; source data and media are secured before viewer work.

## Phase 3 — PASS, proceed to Phase 4

Files/commands: `reports/phase-3.md`. Deterministic `site/index.html` built from canonical JSON. `python3 src/build_site.py`; `.venv/bin/python src/verify_browser.py`20 checks passed with file://, offline networking, no remote requests/runtime errors and forced clipboard fallback. Search, full text, year/month, local images, recurrence/null-end cases, modal keyboard behavior and mobile layout verified.18 regression tests pass. A mobile overflow and CSP-incompatible test wait were corrected. Canonical78events109dates24images unchanged. Proceed to final refresh, documentation, manifest/ZIP and clean extraction verification.

## Phase 4 — PASS; all phases complete

Final public refresh on 2026-11-16 at 21:05:52–21:06:14 UTC: all 17 months successful; unchanged 109 rows / 78 IDs. Two immutable full-range snapshots retain 218 observations. Offline media/JSON/CSV/site rebuild passed; 19 regression tests (including raw-only reconstruction) and 16 validation checks passed; refreshed viewer passed 20 offline browser checks. Staff README, schema/example, final summary, all source/tests, manifest and ZIP are included. Clean extraction passed file hashes, file-set equality, relative links and all 24 media references; its gallery passed all 20 offline browser checks. Exact final ZIP hash and read-only verification results are supplied alongside the ZIP in dist/. An independent extracted-layout offline rebuild also passed byte-identically. `reports/phase-4.md` documents files, commands, counts, results and remaining public-history limits. No work in the authorized phases remains; later public publications require a future refresh.

## Requested follow-up — GitHub Pages preparation and Drive copy

User authorized a public osce-calendar-archive repository and a Drive folder/Sheet/photos. Added outside-click dialog dismissal with interior-click/selection-drag preservation. Browser checks increased from 20 to 23 and passed offline.19 data/security tests and16 validation checks pass; pytest discovery is now explicitly scoped to tests/ so packaged test copies do not conflict. GitHub repository created under eliottelin; publication upload is in progress. Drive native Sheet populated with78 event rows,109 occurrence rows and24 photo rows; all expected values read back exactly (trailing empty cells padded). All24 uploaded image sizes/MIME/parents verified (20,737,236bytes). Formatting and real hyperlinks verified from bounded cell metadata; native Google-rendered visual layout was not inspected. No Drive sharing permissions changed. Source category absence explicitly documented; no categories inferred. Final repository upload and package checks will be recorded in reports/publication.md.

## Formatted coverage and limitations page

Added site/coverage.html and updated the gallery notice link to open it instead of raw Markdown. The generated page uses the gallery design, archive totals, all17 monthly response rows, missing-field counts with event/occurrence grain, category omissions, source-history/media limits, CSV downloads and back-to-gallery navigation. Data is derived from preserved canonical JSON and the raw monthly acquisition index; no network or Markdown runtime is needed. Original QA Markdown remains preserved.

Commands: python3 src/build_site.py; .venv/bin/python -m pytest -q (19passed); browser verifier29checks passed with file:// and networking disabled. The new checks cover HTML navigation, all17months, explicit zero counts, mobile overflow,31missing ends across61timed occurrences and return navigation. An independent read-only reviewer checked counts, local links, headings/captions and zero-row semantics. An initial zero-to-em-dash display issue was corrected. Event records and media are unchanged.
