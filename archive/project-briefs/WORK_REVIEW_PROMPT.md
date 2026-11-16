# Optional ChatGPT Work Review Prompt

I have a ZIP and/or local folder created by Codex containing a public-only archive of Texas A&M Office of Sustainability LiveWhale events from August 2025 to December 2026. Review it as if you were an incoming student technician who needs to reuse last year's event description and photo for a new listing.

**Do not rebuild the extraction pipeline.** Instead, independently test whether the delivered files are useful and trustworthy:

1. Inspect `README.md`, reports, canonical JSON, CSV and the offline HTML viewer.
2. Pick five varied events and try to find them using the viewer; confirm that you can read title, date, description, original link, and retrieve an archived image if one exists.
3. Confirm the viewer works without LiveWhale or external network dependencies, where you can test that.
4. Check that missing images, descriptions, ambiguous recurrence and incomplete months are labelled honestly.
5. Verify Google Sheets import is understandable and that linked photos will remain accessible if LiveWhale is retired.
6. Produce a concise severity-ranked QA punch list and a one-page staff SOP. Clearly distinguish observed failures from issues you could not test.

Do not upload anything to Google Drive, change permissions, or publish externally without explicit authorization. If asked to help with Drive handoff, prefer an office-owned folder and confirm access settings with me.
