# Codex Standing Instructions: OSCE Calendar Archive

You are the engineering coordinator for a preservation-first project. Read `PROJECT_SPEC.md` and the active `phases/*.md` before changing code.

## Mission

Make a complete, independently usable archive of **publicly available Office of Sustainability calendar events** from **2025-08-01 through 2026-12-31**, including original text, rich HTML summaries/descriptions where present, images, image credits/captions/alt text, event date/time, venue, original links, and provenance. The outgoing LiveWhale platform may become inaccessible before January 2027. Prioritize preservation of original evidence over cosmetic presentation.

## Hard rules

1. **Use public resources only.** Never require a LiveWhale admin login, private export, security workaround, or hidden/unpublished event data.
2. **API first.** Use the Texas A&M public LiveWhale JSON API and published feed documentation. Use page parsing or browser automation only for verified gaps. Do not assume an API or image URL pattern works until tested.
3. **Save source first.** Write untouched raw responses and a UTC acquisition timestamp before transforming or cleaning data. Keep a source URL and request record for each batch. Avoid modifying raw files on later runs; version or timestamp snapshots.
4. **No invented data.** Do not fabricate missing text, images, dates, captions, counts, or locations. Preserve nulls and track failures. Any demonstration/sample records must be explicitly labelled and excluded from production exports.
5. **Preserve full text.** Retain the API's original rich HTML in canonical JSON (treat as untrusted when rendering); also produce cleaned plain text for search and copy. Preserve outbound links.
6. **Preserve media locally.** Save downloaded image bytes, metadata, source URL, MIME type, dimensions, and SHA-256. A remote URL by itself is not an archive. Attempt higher-resolution public versions where supported, without guessing success.
7. **Handle recurrence deliberately.** Distinguish unique event identity from event *occurrences*. Do not silently discard repeat dates or overcount repeat instances.
8. **Use America/Chicago for calendar-facing display.** Also retain source ISO timestamps/offsets and the original date fields. Never infer a missing end time.
9. **Idempotence.** Rerunning should not duplicate canonical event records or image files; document changes between snapshots.
10. **Be polite to the website.** Constrain requests to the needed group/months, use timeouts, retries with exponential backoff, sensible delays, caching, and reasonable concurrency. Respect site policies and access errors.
11. **Avoid insecure HTML.** Escape user-facing text and sanitize rich descriptions to disallow scripts, event handlers, iframes, unsafe URLs, and remote runtime dependencies. Never put unsanitized external HTML into the archive viewer.
12. **Build for handoff.** Another student technician should be able to browse and reuse events without Codex, Python, LiveWhale, or the internet. Document any tasks that still require internet (e.g., resolving original external URLs).

## Development conventions

- Prefer Python 3.11+, stdlib or a small documented requirements file, `pytest` for unit tests, and plain HTML/CSS/JS for the offline gallery.
- Maintain clear, version-controlled scripts in `src/`, tests in `tests/`, output in named folders. Ensure generated output and large images are appropriately handled in `.gitignore` or an artifact ZIP.
- Record status in `reports/progress.md`, including commands, counts, findings, and blockers.
- Where feasible, separate tasks into discovery, ingestion, validation, viewer, and documentation.
- Use subagents only for independent research or read-only QA. Each subagent must deliver a report with concrete links and evidence. Never let two agents modify the same files concurrently.
- Make the earliest successful raw extraction and media copy immediately; do not spend the initial run polishing the UI.

## Phase gates

Each phase must end with: **files created; verification commands executed; passed/failed checks; counts; known gaps; decision to proceed or stop**. If public data is inaccessible, stop making claims of completeness and report the limitation clearly.
