"""Offline reconciliation and media integrity checks; nonzero exit on real failures."""
from __future__ import annotations
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from common import ARCHIVE, read_json, sha256, write_json
from download_assets import image_info, raw_rows
from fetch_events import months
from normalize import occurrence_key


def validate_asset(asset, base=ARCHIVE):
    if asset["download_status"] != "downloaded":
        raise ValueError(f"Media unavailable: {asset['asset_id']}")
    path = (base / asset["local_path"]).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError("Asset path escapes archive")
    body = path.read_bytes()
    if sha256(body) != asset["sha256"] or len(body) != asset["byte_size"]:
        raise ValueError("Image checksum or byte length differs")
    if image_info(body) != (asset["mime_type"], asset["width_px"], asset["height_px"]):
        raise ValueError("Image MIME or dimensions differ")
    return True


def main():
    index = read_json(ARCHIVE / "raw/manifest.json")
    events = read_json(ARCHIVE / "data/events.json")
    occurrences = read_json(ARCHIVE / "data/occurrences.json")
    assets = read_json(ARCHIVE / "data/assets.json")
    rows = list(raw_rows())
    all_rows = list(raw_rows(all_snapshots=True))
    checks, errors = [], []

    def check(name, condition):
        checks.append({"check": name, "passed": bool(condition)})
        if not condition:
            errors.append(name)

    check("All 17 month responses successful and represented", index["complete"] and [r["month"] for r in index["coverage"]] == months())
    check("Monthly totals reconcile with all saved raw rows", sum(r.get("api_total_results", 0) for r in index["coverage"]) == len(rows) == sum(r.get("raw_rows", 0) for r in index["coverage"]))
    check("Raw current page hashes and byte lengths", all(sha256((ARCHIVE / p["path"]).read_bytes()) == p["sha256"] and (ARCHIVE / p["path"]).stat().st_size == p["byte_size"] for p in index["pages"]))
    check("All acquisition bodies across samples/snapshots/media retain checksums", all(sha256((ARCHIVE / (meta := read_json(path))["path"]).read_bytes()) == meta["sha256"] for path in (ARCHIVE / "raw").rglob("*.meta.json")))
    check("Group ownership 282 only", all(str(row["gid"]) == "282" and row["group_title"] == "Office of Sustainability" for row, _ in rows))
    keys = {occurrence_key(row) for row, _ in all_rows}
    check("Event identities reconcile with all preserved snapshots", {str(r["id"]) for r, _ in all_rows} == {e["event_id"] for e in events} and len(events) == len({e["event_id"] for e in events}))
    check("Occurrence keys reconcile, with no dropped repeat dates", keys == {(o["event_id"], o["start_iso_original"], o["end_iso_original"]) for o in occurrences} and len(occurrences) == len(keys))
    check("All occurrences within inclusive requested local interval", all("2025-08-01" <= o["display_start_local"][:10] <= "2026-12-31" for o in occurrences))
    check("Original timestamps agree with supplied UTC and epoch", all(datetime.fromisoformat(row["date_iso"]).timestamp() == row["date_ts"] == datetime.strptime(row["date_utc"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp() for row, _ in rows))
    by_id = {e["event_id"]: e for e in events}
    check("Every original raw row survives in canonical source_fields", all(row in by_id[str(row["id"])]["source_fields"] for row, _ in rows))
    check("Canonical original HTML and nulls exactly match selected source row", all(all(e[field + "_html_original"] == e["source_fields"][0].get(field) for field in ("summary", "description", "contact_info")) for e in events))
    media_ids = {a["asset_id"] for a in assets}
    check("Every event image reference resolves", all(set(e["image_asset_ids"]) <= media_ids for e in events))
    for asset in assets:
        try:
            validate_asset(asset)
        except (ValueError, OSError) as exc:
            errors.append(f"Asset {asset['asset_id']}: {exc}")
    check("All canonical media bytes, dimensions, MIME and SHA-256 valid", not any(e.startswith("Asset ") for e in errors))
    check("Canonical media hashes unique", len(assets) == len({a["sha256"] for a in assets}))
    check("Caption and alt claims retained for every source image", all(any(c["event_id"] == str(row["id"]) and c["caption"] == row.get("thumbnail_caption") and c["alt_text"] == row.get("thumbnail_alt") for a in assets for c in a["claims"]) for row, _ in rows if row.get("thumbnail")))
    with (ARCHIVE / "exports/events.csv").open(encoding="utf-8-sig", newline="") as file:
        exported = list(csv.DictReader(file))
    check("CSV has one row per occurrence", len(exported) == len(occurrences) and {r["occurrence_id"] for r in exported} == {o["occurrence_id"] for o in occurrences})
    missing = Counter(k for event in events for k in event["missing_fields"])
    result = {"passed": not errors, "snapshot_id": index["snapshot_id"], "counts": {"months": len(index["coverage"]), "raw_pages": len(index["pages"]), "raw_rows": len(rows), "preserved_raw_observations": len(all_rows), "events": len(events), "occurrences": len(occurrences), "duplicate_raw_occurrence_rows_latest": len(rows) - len({occurrence_key(row) for row, _ in rows}), "images": len(assets), "image_bytes": sum(a.get("byte_size") or 0 for a in assets), "image_failures": sum(a["download_status"] != "downloaded" for a in assets), "missing_fields": dict(missing)}, "checks": checks, "errors": errors}
    write_json(ARCHIVE / "reports/validation.json", result)
    for filename, fields, records in [
        ("missing-fields.csv", ["event_id", "title", "missing_fields", "warnings"], [{"event_id": e["event_id"], "title": e["title"], "missing_fields": "; ".join(e["missing_fields"]), "warnings": "; ".join(e["warnings"])} for e in events if e["missing_fields"] or e["warnings"]]),
        ("media-inventory.csv", ["asset_id", "local_path", "width_px", "height_px", "byte_size", "mime_type", "source_url", "download_status"], assets),
    ]:
        with (ARCHIVE / "reports" / filename).open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            from content import csv_safe
            writer.writerows({k: csv_safe(r.get(k)) for k in fields} for r in records)
    print(json.dumps(result, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
