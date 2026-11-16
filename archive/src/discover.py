"""Capture a bounded Phase 0 evidence sample; never scrape private resources."""
import json
from common import ARCHIVE, Capture, monthly_url, rows_and_meta, run_id


def main():
    capture = Capture(ARCHIVE / "raw" / "samples" / run_id())
    for name, url in [
        ("robots.txt", "https://calendar.tamu.edu/robots.txt"),
        ("feeds.html", "https://calendar.tamu.edu/feeds/"),
        ("api-docs.html", "https://support.livewhale.com/live/blurbs/json-api"),
        ("api-basics.html", "https://support.livewhale.com/live/blurbs/api"),
        ("policies.html", "https://marcomm.tamu.edu/calendar/policies/"),
    ]:
        capture.get(url, name)
    for month in ["2025-08", "2025-10", "2026-04", "2026-10", "2026-11"]:
        body, record = capture.get(monthly_url(month, "v1"), f"{month}.json")
        if record["http_status"] == 200:
            try:
                rows, meta, links = rows_and_meta(json.loads(body))
                print(json.dumps({"month": month, "rows": len(rows), "meta": meta, "links": links, "first_record": rows[:1]}, ensure_ascii=False), flush=True)
            except (ValueError, TypeError) as exc:
                print(f"Response parse failed: {exc}", flush=True)
    body, _ = capture.get(monthly_url("2025-10", "v2", "paginate/1/"), "v2-paginate-1.json")
    print(body.decode("utf-8", errors="replace")[:24000], flush=True)


if __name__ == "__main__":
    main()
