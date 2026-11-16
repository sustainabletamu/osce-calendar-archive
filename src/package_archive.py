"""Include reproducible tooling, inventory all files, and build an integrity-checkable ZIP."""
import argparse
import shutil
import zipfile
from pathlib import Path
from common import ARCHIVE, ROOT, read_json, sha256, write_json


def sync_tooling():
    for folder in ("src", "tests"):
        destination = ARCHIVE / folder
        destination.mkdir(exist_ok=True)
        for source in (ROOT / folder).glob("*"):
            if source.is_file() and source.suffix in (".py", ".html") and source.resolve() != (destination / source.name).resolve():
                shutil.copyfile(source, destination / source.name)
    if (ROOT / "requirements-dev.txt").resolve() != (ARCHIVE / "requirements-dev.txt").resolve():
        shutil.copyfile(ROOT / "requirements-dev.txt", ARCHIVE / "requirements-dev.txt")
    if (ROOT / "pytest.ini").exists() and (ROOT / "pytest.ini").resolve() != (ARCHIVE / "pytest.ini").resolve():
        shutil.copyfile(ROOT / "pytest.ini", ARCHIVE / "pytest.ini")
    if (ROOT / "phases").exists():
        brief = ARCHIVE / "project-briefs"
        brief.mkdir(exist_ok=True)
        for name in ("AGENTS.md", "PROJECT_SPEC.md", "START_HERE_CODEX_PROMPT.md", "WORK_REVIEW_PROMPT.md"):
            shutil.copyfile(ROOT / name, brief / name)
        shutil.copytree(ROOT / "phases", brief / "phases", dirs_exist_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip-path", type=Path, default=ARCHIVE.parent / "dist/osce-calendar-archive-2026-11-16.zip")
    args = parser.parse_args()
    if args.zip_path.resolve().is_relative_to(ARCHIVE.resolve()):
        raise ValueError("Write the ZIP outside archive/ to avoid including a prior output inside itself")
    for required in ("README.md", "raw/manifest.json", "data/events.json", "data/occurrences.json", "data/assets.json", "exports/events.csv", "site/index.html", "reports/coverage.csv", "reports/qa.md", "reports/progress.md", "reports/phase-4.md"):
        if not (ARCHIVE / required).is_file():
            raise FileNotFoundError(f"Required deliverable missing: {required}")
    sync_tooling()
    index = read_json(ARCHIVE / "raw/manifest.json")
    validation = read_json(ARCHIVE / "reports/validation.json")
    captures = [read_json(path) for path in (ARCHIVE / "raw").rglob("*.meta.json")]
    files = [{"path": str(p.relative_to(ARCHIVE)), "byte_size": p.stat().st_size, "sha256": sha256(p.read_bytes())} for p in sorted(ARCHIVE.rglob("*")) if p.is_file() and p != ARCHIVE / "manifest.json" and not ({"__pycache__", ".pytest_cache", "dist", ".venv"} & set(p.relative_to(ARCHIVE).parts))]
    manifest = {"schema_version": 1, "scope": {"group_id": 282, "group_title": "Office of Sustainability", "start_date": "2025-08-01", "end_date": "2026-12-31", "display_timezone": "America/Chicago", "source_template": "https://calendar.tamu.edu/live/json/v2/events/group/Office%20of%20Sustainability/start_date/YYYY-MM-DD/end_date/YYYY-MM-DD/response_fields/all/show_archived/both/paginate/100/"}, "latest_snapshot": index["snapshot_id"], "acquisition_window_utc": [min(c["acquired_at_utc"] for c in captures), max(c["acquired_at_utc"] for c in captures)], "counts": {**validation["counts"], "physical_image_files_including_discovery": len(list((ARCHIVE / "assets/images").glob("*"))), "extraction_snapshots": len(list((ARCHIVE / "raw/snapshots").glob("*/extraction.json"))), "saved_acquisition_bodies": len(captures)}, "public_range_requests_successful": index["complete"], "historical_completeness": "not established", "limitations": ["Deleted, hidden, unpublished and otherwise inaccessible records cannot be established by public requests", "Zero-result months do not prove no historical events existed", "December2026 is future relative to capture; later publications require refresh", "Source text/media may have changed since original publication", "Full-size public image copies are not proven original-upload or camera bytes", "External linked websites/PDFs/online meeting contents are not archived", "Source-null fields and missing timed ends remain null; see reports/missing-fields.csv"], "file_inventory_note": "Every ZIP file except manifest.json is listed below. Manifest self-hash is excluded to avoid circularity; the external ZIP SHA-256 covers manifest.json too.", "files": files}
    write_json(ARCHIVE / "manifest.json", manifest)
    args.zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in [*(ARCHIVE / item["path"] for item in files), ARCHIVE / "manifest.json"]:
            archive.write(path, "archive/" + str(path.relative_to(ARCHIVE)))
    digest = sha256(args.zip_path.read_bytes())
    args.zip_path.with_suffix(".zip.sha256").write_text(f"{digest}  {args.zip_path.name}\n", encoding="ascii")
    print({"zip": str(args.zip_path), "bytes": args.zip_path.stat().st_size, "sha256": digest, "inventoried_files": len(files), "zip_files": len(files) + 1})


if __name__ == "__main__":
    main()
