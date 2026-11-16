# Phase 4 | Final Deliverables and Staff Handoff

## Goal

Package and explain the archive for long-term access by the OSCE team after LiveWhale goes away.

## Tasks

1. Run final time-bounded extraction or incremental refresh while public endpoints remain available; version snapshots rather than destroying earlier evidence. Re-run normalization, media validation, CSV export, and site build.
2. Produce a `README.md` written for student technicians: how to open offline HTML; search/filter; copy old summaries/descriptions; find or download a locally archived photo; open CSV in Excel or import to Google Sheets; and interpret missing-field flags.
3. Make sure Google Sheets directions distinguish local image paths from usable Drive links. If a connected Drive publishing workflow is explicitly authorized, upload image files and link Sheet rows to those uploaded copies. Avoid silent public sharing or changing permissions.
4. Include technical reproduction steps, exact commands, Python dependencies, source API template, archive scope, UTC retrieval dates, and limits of public-only access.
5. Package the `archive/` directory as a ZIP. Include `manifest.json` listing all included files, hashes, event/occurrence/image counts, extraction window, and incomplete items.
6. Independently open the ZIP from a clean directory and confirm all site links are relative and work offline; all files referenced in the manifest exist.
7. Prepare a one-page final summary: original objective, what is preserved, counts, missing/uncertain content, how to use, and how to refresh or extend for other date ranges.

## Final checklist

- [ ] All 17 months attempted and represented in coverage report.
- [ ] Raw JSON copies saved with provenance.
- [ ] Logical events and occurrences counted independently.
- [ ] Full rich text + plain text exported where available.
- [ ] Local image files preserved, with captions and quality flags.
- [ ] CSV usable in Sheets, with row-grain documented.
- [ ] Offline HTML site opens from ZIP extraction without network.
- [ ] Tests and sample accuracy audits pass or failures are disclosed.
- [ ] Handoff README and archive manifest included.
- [ ] Only public data gathered; no invented/admin-only events.
