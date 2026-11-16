# Formatted coverage page verification

## Formatted coverage and limitations page

Added site/coverage.html and updated the gallery notice link to open it instead of raw Markdown. The generated page uses the gallery design, archive totals, all17 monthly response rows, missing-field counts with event/occurrence grain, category omissions, source-history/media limits, CSV downloads and back-to-gallery navigation. Data is derived from preserved canonical JSON and the raw monthly acquisition index; no network or Markdown runtime is needed. Original QA Markdown remains preserved.

Commands: python3 src/build_site.py; .venv/bin/python -m pytest -q (19passed); browser verifier29checks passed with file:// and networking disabled. The new checks cover HTML navigation, all17months, explicit zero counts, mobile overflow,31missing ends across61timed occurrences and return navigation. An independent read-only reviewer checked counts, local links, headings/captions and zero-row semantics. An initial zero-to-em-dash display issue was corrected. Event records and media are unchanged.
