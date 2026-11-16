"""Rebuild canonical JSON and occurrence-grain CSV using saved evidence only."""
from __future__ import annotations
import csv
import html
import json
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo
from common import ARCHIVE, read_json, sha256, write_json
from content import convert, csv_safe
from download_assets import raw_rows


def occurrence_key(row):
    if row.get("id") is None or not row.get("date_iso"):
        raise ValueError("Source event ID or start date missing")
    return (str(row["id"]), row["date_iso"], row.get("date2_iso"))


def local_date(value):
    if value is None:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("Source ISO timestamp has no offset")
    return parsed.astimezone(ZoneInfo("America/Chicago")).isoformat()


def normalize(rows_with_pages, assets, previous=None):
    events, occurrences = {}, {}
    previous = {e["event_id"]: e for e in previous or []}
    by_event = defaultdict(list)
    image_map = {}
    for asset in assets:
        for event_id in asset["event_ids"]:
            by_event[event_id].append(asset)
        if asset["download_status"] == "downloaded":
            for url in asset["source_urls"]:
                image_map[url] = "../" + asset["local_path"]
    for row, page in rows_with_pages:
        key = occurrence_key(row)
        event_id = key[0]
        source_ref = {"path": page["path"], "url": page["url"], "row_event_id": row["id"], "date_iso": row["date_iso"], "acquired_at_utc": page["acquired_at_utc"]}
        if event_id not in events:
            event = {"event_id": event_id, "group_id": row.get("gid"), "group_title": row.get("group_title"), "title": html.unescape(row.get("title") or ""), "original_url": row.get("url"), "source_urls": [], "first_seen_at_utc": previous.get(event_id, {}).get("first_seen_at_utc", page["acquired_at_utc"]), "last_seen_at_utc": page["acquired_at_utc"], "location": row.get("location"), "location_title": row.get("location_title"), "online_url": row.get("online_url"), "contact_info_html_original": row.get("contact_info"), "cost": row.get("cost"), "registration": {k: v for k, v in row.items() if any(s in k for s in ("registration", "rsvp", "wait_list"))}, "categories": {k: v for k, v in row.items() if k.startswith("event_types")}, "tags": {k: v for k, v in row.items() if k.startswith("tags")}, "status": row.get("status"), "last_modified_source": row.get("last_modified"), "image_asset_ids": [a["asset_id"] for a in by_event[event_id]], "thumbnail_caption": row.get("thumbnail_caption"), "thumbnail_alt": row.get("thumbnail_alt"), "raw_source_refs": [], "source_fields": [], "missing_fields": [], "warnings": []}
            for field in ("summary", "description", "contact_info"):
                rich, text = convert(row.get(field), row.get("url"), image_map)
                event[field + "_html_original"] = row.get(field)
                event[field + "_html_safe"] = rich
                event[field + "_text"] = text
                if row.get(field) is None:
                    event["missing_fields"].append(field)
            if not (event["summary_text"] or event["description_text"]):
                event["warnings"].append("No summary or description exposed by API")
            if not (row.get("location") or row.get("location_title") or row.get("online_url")):
                event["missing_fields"].append("location")
            if not event["image_asset_ids"]:
                event["missing_fields"].append("image")
            if any(a["download_status"] != "downloaded" for a in by_event[event_id]):
                event["warnings"].append("Image download failed; consult assets.json")
            events[event_id] = event
        event = events[event_id]
        event["source_urls"] = sorted(set(event["source_urls"] + [page["url"], row["url"]]))
        event["first_seen_at_utc"] = min(event["first_seen_at_utc"], page["acquired_at_utc"])
        event["last_seen_at_utc"] = max(event["last_seen_at_utc"], page["acquired_at_utc"])
        if source_ref not in event["raw_source_refs"]:
            event["raw_source_refs"].append(source_ref)
        if row not in event["source_fields"]:
            event["source_fields"].append(row)
        if key not in occurrences:
            start, end = local_date(row["date_iso"]), local_date(row.get("date2_iso"))
            if end and datetime.fromisoformat(end) < datetime.fromisoformat(start):
                raise ValueError(f"Impossible end before start: {key}")
            occurrence = {"occurrence_id": event_id + "-" + sha256(json.dumps(key).encode())[:20], "event_id": event_id, "start_iso_original": row["date_iso"], "end_iso_original": row.get("date2_iso"), "timezone": row.get("timezone"), "display_timezone": "America/Chicago", "all_day": bool(row.get("is_all_day")), "display_start_local": start, "display_end_local": end, "recurrence_source_fields": {k: v for k, v in row.items() if k.startswith(("repeats", "date", "tz"))}, "source_refs": [], "warnings": []}
            if end is None and not occurrence["all_day"]:
                occurrence["warnings"].append("End time absent at source")
            occurrences[key] = occurrence
        if source_ref not in occurrences[key]["source_refs"]:
            occurrences[key]["source_refs"].append(source_ref)
    for event in events.values():
        event["occurrence_count"] = sum(o["event_id"] == event["event_id"] for o in occurrences.values())
        for field in ("title", "summary", "description", "location", "thumbnail"):
            variants = {json.dumps(row.get(field), sort_keys=True) for row in event["source_fields"]}
            if len(variants) > 1:
                event["warnings"].append(f"Multiple source {field} variants retained in source_fields; first observed used for display")
    return sorted(events.values(), key=lambda e: e["event_id"]), sorted(occurrences.values(), key=lambda o: (o["display_start_local"], o["event_id"]))


def export_csv(events, occurrences, assets):
    by_id = {e["event_id"]: e for e in events}
    media = {a["asset_id"]: a for a in assets}
    full_fields = ["occurrence_id", "event_id", "title", "date", "time", "end_iso", "all_day", "timezone", "location", "summary_text", "description_text", "summary_html_original", "description_html_original", "contact_info_text", "image_paths", "image_source_urls", "image_caption", "image_alt", "original_event_url", "topics_tags", "completeness_flags", "canonical_json"]
    directory = ARCHIVE / "exports"
    directory.mkdir(parents=True, exist_ok=True)
    records = []
    for occurrence in occurrences:
        event = by_id[occurrence["event_id"]]
        images = [media[k] for k in event["image_asset_ids"]]
        start = occurrence["display_start_local"]
        record = {"occurrence_id": occurrence["occurrence_id"], "event_id": event["event_id"], "title": event["title"], "date": start[:10], "time": "" if occurrence["all_day"] else start[11:], "end_iso": occurrence["end_iso_original"], "all_day": occurrence["all_day"], "timezone": "America/Chicago", "location": event["location_title"] or event["location"], "summary_text": event["summary_text"], "description_text": event["description_text"], "summary_html_original": event["summary_html_original"], "description_html_original": event["description_html_original"], "contact_info_text": event["contact_info_text"], "image_paths": "; ".join(a["local_path"] for a in images if a["local_path"]), "image_source_urls": "; ".join(a["source_url"] for a in images), "image_caption": event["thumbnail_caption"], "image_alt": event["thumbnail_alt"], "original_event_url": event["original_url"], "topics_tags": json.dumps({"categories": event["categories"], "tags": event["tags"]}, ensure_ascii=False), "completeness_flags": "; ".join(event["missing_fields"] + event["warnings"] + occurrence["warnings"]), "canonical_json": "data/events.json#" + event["event_id"]}
        records.append(record)
    for filename, fields in [("events.csv", full_fields), ("occurrences.csv", full_fields[:8])]:
        with (directory / filename).open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows({k: csv_safe(row[k]) for k in fields} for row in records)


def mark_visibility(events, occurrences, current_rows):
    keys = {occurrence_key(row) for row, _ in current_rows}
    ids = {key[0] for key in keys}
    for event in events:
        event["visibility_status"] = "present_in_latest_snapshot" if event["event_id"] in ids else "preserved_from_earlier_snapshot"
        if event["event_id"] not in ids:
            event["warnings"].append("Not returned in latest public snapshot; earlier captured evidence retained")
    for occurrence in occurrences:
        key = (occurrence["event_id"], occurrence["start_iso_original"], occurrence["end_iso_original"])
        occurrence["visibility_status"] = "present_in_latest_snapshot" if key in keys else "preserved_from_earlier_snapshot"
        if key not in keys:
            occurrence["warnings"].append("Occurrence absent from latest public snapshot; earlier capture retained")


def main():
    assets = read_json(ARCHIVE / "data/assets.json")
    previous_path = ARCHIVE / "data/events.json"
    previous = read_json(previous_path) if previous_path.exists() else []
    events, occurrences = normalize(list(raw_rows(all_snapshots=True)), assets, previous)
    mark_visibility(events, occurrences, list(raw_rows()))
    write_json(ARCHIVE / "data/events.json", events)
    write_json(ARCHIVE / "data/occurrences.json", occurrences)
    export_csv(events, occurrences, assets)
    print(json.dumps({"events": len(events), "occurrences": len(occurrences), "assets": len(assets)}))


if __name__ == "__main__":
    main()
