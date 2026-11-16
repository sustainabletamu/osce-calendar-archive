"""Copy the preserved archive into an existing, clean Pages repository checkout."""
import argparse
import shutil
from pathlib import Path
from common import ARCHIVE, ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    destination = args.destination.resolve()
    if destination == ROOT or not (destination / ".git").exists():
        raise ValueError("Use a separate existing repository checkout")
    for folder in ("src", "tests", "phases"):
        shutil.copytree(ROOT / folder, destination / folder, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    for name in ("AGENTS.md", "PROJECT_SPEC.md", "START_HERE_CODEX_PROMPT.md", "WORK_REVIEW_PROMPT.md", "requirements-dev.txt", "pytest.ini"):
        shutil.copyfile(ROOT / name, destination / name)
    shutil.copytree(ARCHIVE, destination / "archive", dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".venv", "drive-publication.json", "google-sheet-data.json", "drive-verification.json"))
    (destination / ".gitignore").write_text("__pycache__/\n.pytest_cache/\n.venv/\nnode_modules/\ndist/\n*.zip\n.DS_Store\n", encoding="utf-8")
    (destination / ".nojekyll").write_text("", encoding="utf-8")
    (destination / "index.html").write_text('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0; url=./archive/site/index.html"><title>OSCE Calendar Archive</title></head><body><p><a href="./archive/site/index.html">Open the OSCE event archive</a></p></body></html>\n', encoding="utf-8")
    (destination / "README.md").write_text(f'''# OSCE Calendar Archive

Public Texas A&M Office of Sustainability events, August 2025–December 2026. Preserved November 16, 2026: **78 event IDs, 109 calendar occurrences, 24 locally downloaded event images**.

Open [the gallery](archive/site/index.html), or enable GitHub Pages from **Settings → Pages → Deploy from a branch → main → /(root) → Save**. The root index redirects to the gallery; `.nojekyll` serves the static archive unchanged. No build, API key or external runtime is required. The entire archive also opens offline from disk. Click outside an event detail frame, use Close, or press Escape to return to the gallery.

The requested Drive folder, native Sheet and uploaded images were delivered privately. Their URLs/IDs are excluded from this public repository.

The Sheet includes one row per event, a separate occurrence table, source event categories/audience/campus/tags and links to the 24 real Drive image files. Drive access permissions were not changed. JSON and physical images remain the source of truth; the Sheet and HTML are downstream views.

## Historical limits

This is a verified public-response archive, not a proven complete historical database. Deleted, hidden, unpublished or inaccessible records may be missing. Four months returned zero rows (August 2025; July, August and December 2026), which does not prove no events occurred. December 2026 is future relative to capture. Missing source fields remain labelled: 49 full descriptions, 8 summaries, 31 contacts, 28 structured locations/online URLs, 8 images and 31 timed ends. Twenty-seven events lack all category fields; all 78 lack tags. Multi-day display dates are not necessarily independent sessions. Full-size public images are not proven original camera/upload bytes. External links/PDFs/meetings are not captured beyond their URLs.

See [staff instructions](archive/README.md), [QA](archive/reports/qa.md), [publication report](archive/reports/publication.md), [canonical JSON](archive/data/) and [raw source evidence](archive/raw/). Rebuild commands and optional development dependencies are documented in the staff instructions. `src/` and `tests/` contain the reproducible preservation tools.
''', encoding="utf-8")
    # Public repository excludes private downstream Drive artifacts and identifiers.
    import json
    for relative in ("exports/drive-publication.json", "exports/google-sheet-data.json", "reports/drive-verification.json"):
        (destination / "archive" / relative).unlink(missing_ok=True)
    staff = destination / "archive/README.md"
    text = staff.read_text()
    marker = "## Published copies and gallery update"
    if marker in text:
        text = text[:text.index(marker)] + "## Published copies and gallery update\n\nGitHub repository: https://github.com/eliottelin/osce-calendar-archive. Enable Pages from main / (root). The Drive Sheet and 24 real image files were delivered privately; Drive URLs and file IDs are excluded from this public repository. Canonical JSON and local images remain the source of truth. Clicking outside an event detail closes it; interior clicks and text-selection drags keep it open.\n"
    text = text.replace("See the Published copies section below.", "Drive links are delivered separately and excluded from this public copy.")
    staff.write_text(text)
    report = destination / "archive/reports/publication.md"
    report.write_text("# Follow-up verification\n\nUser requested GitHub Pages preparation, outside-click detail dismissal and a private Drive Sheet/photo copy. Public repository keeps the archive tree intact with a root entry and .nojekyll. Enable Pages from main / (root). No alternate hosting was registered.\n\n23 offline browser checks passed, including outside clicks, inside clicks and text-selection drags.19 data/security tests and16 validation checks passed. Canonical counts remain78 IDs,109 occurrences,24 images. Independent local-link, raw-reference, manifest and image-hash QA passed.\n\nThe private downstream Sheet has78 event rows,109 occurrence rows,24 photo rows and a Read me tab. Uploaded images match expected size/MIME and folder placement; hyperlinks and source-category values were read back. Native Google visual layout was not inspected; formatting was checked through cell metadata. Sharing permissions were unchanged. Private Drive URLs, IDs and publication maps are intentionally excluded from this public repository.\n\nCategory fields are source-derived and separate: event categories40 IDs, audience51, campus47, tags0. Twenty-seven IDs have no category fields. No category was inferred. Public-history limitations remain in the staff README and original phase QA reports.\n")
    # Diagnostic page captures can contain third-party client API keys; keep them private.
    for diagnostic_html in (destination / "archive/raw").rglob("*.html"):
        diagnostic_html.with_suffix(diagnostic_html.suffix + ".meta.json").unlink(missing_ok=True)
        diagnostic_html.unlink()
    # Keep original evidence private; expose only necessary public acquisition metadata.
    for headers_file in (destination / "archive/raw").rglob("*.headers"):
        headers_file.unlink()
    def public_metadata(value):
        if isinstance(value, list):
            return [public_metadata(item) for item in value if not (isinstance(item, dict) and str(item.get("path", "")).startswith("raw/") and not (destination / "archive" / item["path"]).exists())]
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                if key == "headers" and isinstance(item, dict):
                    result[key] = {name: data for name, data in item.items() if name.lower() in {"content-type", "content-length"}}
                    result["public_metadata_note"] = "HTTP headers minimized for public delivery; original response metadata remains in the local preservation package."
                elif key == "headers_path":
                    result[key] = None
                else:
                    result[key] = public_metadata(item)
            return result
        return value
    for metadata_file in (destination / "archive/raw").rglob("*.json"):
        if metadata_file.name.endswith(".meta.json") or metadata_file.name in {"manifest.json", "extraction.json"}:
            metadata_file.write_text(json.dumps(public_metadata(json.loads(metadata_file.read_text())), ensure_ascii=False, indent=2)+"\n")
    with staff.open("a") as output:
        output.write("\nThe public repository omits response-header dump files and minimizes HTTP metadata to content type/length, status, acquisition time, source URL and body checksum. Cookies, diagnostic HTML page captures with third-party client API keys, and private Drive publication artifacts are excluded. Untouched original responses and metadata remain in the local preservation ZIP. Event/API response bodies and downloaded image bytes are unchanged.\n")
    manifest_path = destination / "archive/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    base = destination / "archive"
    manifest["files"] = [{"path":str(path.relative_to(base)),"byte_size":path.stat().st_size,"sha256":__import__("hashlib").sha256(path.read_bytes()).hexdigest()} for path in sorted(base.rglob("*")) if path.is_file() and path != manifest_path and not ({"__pycache__", ".pytest_cache", ".venv", "dist"} & set(path.relative_to(base).parts))]
    manifest["counts"]["original_private_saved_acquisition_bodies"] = manifest["counts"]["saved_acquisition_bodies"]
    manifest["counts"]["saved_acquisition_bodies"] = len(list((base / "raw").rglob("*.meta.json")))
    manifest["publication_policy"] = "Public event/API bodies and images are unchanged. Private Drive artifact URLs/IDs, cookies, header dumps and diagnostic HTML captures are excluded; untouched originals remain in the local preservation ZIP."
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(f"Prepared public Pages repository at {destination}")


if __name__ == "__main__":
    main()
