# Phase 3 | Staff-Friendly Offline HTML Gallery

## Goal

Create a pleasant, lightweight way for nontechnical OSCE staff to browse previous events and reuse content and images.

## Requirements

1. Produce `site/index.html` and local styles/scripts/media dependencies. It must open directly by double-clicking the HTML file with internet turned off (test via `file://`), not just on localhost or GitHub Pages.
2. Search across event title, summaries, descriptions, location, and categories/tags; filter by year/month. Make results easy to scan by date and image.
3. Provide an event detail view with full original content rendered **safely**, original start/end info, location, caption/alt, source attribution, locally downloaded high-resolution photo link, and a visible 'missing' indicator if any important source field is absent.
4. Offer copy-ready plain text for title, summary, and full description; add optional copy buttons with a graceful fallback when browser clipboard access is unavailable.
5. Ensure visible images use local relative paths. If image asset is missing, present a simple labelled placeholder rather than a broken browser image icon.
6. No public hosting, API keys, Google login, remote JS/CSS/fonts, or reliance on LiveWhale for normal browsing. Do not fetch a separate JSON file at runtime from file://; embed a safe serialized index in the built HTML or generate static searchable markup.
7. Make a responsive accessible interface with semantic markup, keyboard-focus states, sufficient contrast, and clearly differentiated archive vs original-site links.
8. Generate viewer deterministically from `data/` using a reproducible build command. Keep original raw records accessible in the archive ZIP.

## Nice-to-have (after requirements)

- Event count and calendar year totals; sort by newest/oldest; topic chips.
- Copy a whole event's description and logistics together.
- Link to each archived image file and display original image caption and alternative text.
- Small 'Source details' panel with event ID, source URL, and capture timestamp.

## Phase gate

- Test offline with all networking disabled, including search and media display.
- Test records with very long text, no image, recurrence, missing end dates, and HTML markup.
- A staff member can find, open, copy, and identify a prior event without touching code.
