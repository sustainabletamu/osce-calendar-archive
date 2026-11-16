import json
from common import ARCHIVE, Capture, monthly_url, run_id, sha256


def main():
    source = sorted((ARCHIVE / "raw/samples").glob("*/2025-10.json"))[0]
    rows = json.loads(source.read_bytes())["data"]
    capture = Capture(ARCHIVE / "raw/samples" / run_id())
    image_dir = ARCHIVE / "assets/images"
    image_dir.mkdir(parents=True, exist_ok=True)
    for event_id in [359398, 365922]:
        row = next(r for r in rows if r["id"] == event_id)
        capture.get(row["url"], f"event-{event_id}.html")
        body, record = capture.get(row["thumbnail"], f"image-{event_id}.bin")
        if record["http_status"] == 200 and record["headers"].get("Content-Type", "").startswith("image/"):
            ext = row["thumbnail"].rsplit(".", 1)[-1].lower()
            path = image_dir / f"{sha256(body)}.{ext}"
            if not path.exists():
                path.write_bytes(body)
    capture.get(monthly_url("2025-10", "v2", "paginate/1/") + "?page=2", "v2-page-2.json")
    capture.get(monthly_url("2025-10", "v2", "hide_repeats/true/"), "hide-repeats.json")
    capture.get("https://calendar.tamu.edu/live/ical/events/group/Office%20of%20Sustainability/start_date/2025-10-01/end_date/2025-10-31/", "2025-10.ics")


if __name__ == "__main__":
    main()
