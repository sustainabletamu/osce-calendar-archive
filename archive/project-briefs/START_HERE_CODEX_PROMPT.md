# Paste this into Codex

You are the coordinator for the OSCE Calendar Archive project in this repository. Read `AGENTS.md`, `PROJECT_SPEC.md`, and the phase briefs in `phases/` before implementing.

**Goal:** Preserve the publicly available Texas A&M Office of Sustainability LiveWhale calendar for August 2025 through December 2026 as a durable, independently usable archive. Our office **does not have LiveWhale admin access**. The source platform will be replaced before the start of spring 2027. We need original event titles, dates, locations, summaries, full descriptions, links, photos, captions/alt text, and other public metadata so staff can reuse previous event copy and media.

**Priorities in order:** (1) capture original raw evidence, (2) download original or highest-quality publicly accessible images, (3) normalize and validate data with full recurrence handling, (4) export spreadsheet-friendly files, (5) build an attractive offline searchable HTML archive, (6) document staff handoff. Do not spend time on UI before the source is secured.

**Method:** Start with the public LiveWhale JSON API; test a known historical month such as October 2025, examine pagination/fields and image URLs, then extract the full range month by month. Respect rate limits and use only publicly accessible resources. Use browser automation/TinyFish or Wayback only for demonstrated gaps. Do not invent missing data or claim that public records include hidden/admin-only events.

**Agents:** You may delegate two *read-only, independent* discovery subagents: (A) API/pagination/recurrence and (B) image/full-text recovery. Each must report evidence and recommendations. The coordinator owns all production code/files. Later, a QA subagent may independently review output in read-only mode. Do not let agents simultaneously edit the same files.

**Execution:** Execute `phases/00-discovery.md` first and create its report. If discovery confirms a viable public endpoint, immediately build a minimal raw-data-and-image preservation pass from `phases/01-extract.md` before polishing documentation. Continue through phases in order. At each phase record file paths, commands, observed counts, QA outcomes, and known gaps in `reports/progress.md`. If a phase fails, attempt reasonable fixes and report the blocker, not a false success.

**Definition of done:** Full public-range retrieval attempts recorded; canonical JSON, local image files, CSV, offline `site/index.html`, test suite, QA report, staff README, and a final ZIP with manifest. Show exactly how someone can open the HTML, search for old events, find full descriptions, and reuse archived photos. Final status must clearly distinguish complete, partially complete, and unavailable information.

Begin with Phase 0. Do not ask for LiveWhale credentials.
