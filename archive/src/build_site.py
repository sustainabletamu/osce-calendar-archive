"""Deterministically build one disk-openable HTML file from canonical JSON."""
import html
import json
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo
from common import ARCHIVE, ROOT, read_json


def main():
    events = read_json(ARCHIVE / "data/events.json")
    occurrences = read_json(ARCHIVE / "data/occurrences.json")
    assets = read_json(ARCHIVE / "data/assets.json")
    by_event = defaultdict(list)
    for occurrence in occurrences:
        by_event[occurrence["event_id"]].append(occurrence)
    for event in events:
        event["occurrences"] = by_event[event["event_id"]]
        event["thumbnail_caption_display"] = html.unescape(event["thumbnail_caption"] or "")
        event["thumbnail_alt_display"] = html.unescape(event["thumbnail_alt"] or "")
        event["topics"] = sorted(set(v for field in (event["categories"], event["tags"]) for values in field.values() if isinstance(values, list) for v in values if isinstance(v, str)))
        event["search_text"] = " ".join(str(v or "") for v in (event["title"], event["summary_text"], event["description_text"], event["location"], event["location_title"], " ".join(event["topics"])))
    data = {"events": events, "assets": assets, "counts": {"events": len(events), "occurrences": len(occurrences), "images": sum(a["download_status"] == "downloaded" for a in assets)}}
    # Avoid closing script tags, HTML parser transitions, and JS line separators.
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    template = (ROOT / "src/viewer_template.html").read_text(encoding="utf-8")
    index = read_json(ARCHIVE / "raw/manifest.json")
    captured = datetime.fromisoformat(index.get("finished_at_utc", index["started_at_utc"])).astimezone(ZoneInfo("America/Chicago"))
    capture_label = f"{captured:%B} {captured.day}, {captured.year}"
    output = template.replace("__ARCHIVE_DATA__", payload).replace("__CAPTURE_DATE__", html.escape(capture_label))
    path = ARCHIVE / "site/index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding="utf-8")
    print(f"Built {path}: {len(events)} records, {len(occurrences)} dates, {len(assets)} images")


if __name__ == "__main__":
    main()
