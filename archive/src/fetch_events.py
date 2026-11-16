"""Versioned monthly preservation; follows every actual next-page link."""
from __future__ import annotations
import argparse
import csv
import json
from urllib.parse import urljoin, urlsplit
from common import ARCHIVE, Capture, monthly_url, read_json, rows_and_meta, run_id, utcnow, write_json


def months():
    return [f"{year}-{month:02d}" for year, start, end in [(2025, 8, 12), (2026, 1, 12)] for month in range(start, end + 1)]


def paginate(first_url, get_page):
    """Injectable retrieval makes pagination checks testable without networking."""
    url, seen, pages, rows, total, expected_pages = first_url, set(), [], [], None, None
    while url:
        if url in seen or len(seen) >= 100:
            raise ValueError("Pagination loop or safety limit")
        if urlsplit(url).hostname != "calendar.tamu.edu" or "/live/json/" not in urlsplit(url).path:
            raise ValueError("Unexpected pagination source")
        seen.add(url)
        body, record = get_page(url, len(pages) + 1)
        if record["http_status"] != 200:
            raise ValueError(f"HTTP failure {record['http_status']} at {url}")
        batch, meta, links = rows_and_meta(json.loads(body))
        page_number = len(pages) + 1
        if meta.get("page", page_number) != page_number:
            raise ValueError("Unexpected page number")
        if total is None:
            total, expected_pages = meta.get("total_results"), meta.get("total_pages")
        elif meta.get("total_results") != total:
            raise ValueError("Result count changed during pagination")
        if any(str(r.get("gid")) != "282" or r.get("group_title") != "Office of Sustainability" for r in batch):
            raise ValueError("Source ownership differs from requested group")
        pages.append(record)
        rows.extend(batch)
        next_url = links.get("next")
        url = urljoin(url, next_url) if next_url else None
    if total is None or len(rows) != total:
        raise ValueError(f"Rows {len(rows)} do not reconcile with API total {total}")
    if expected_pages is not None and len(pages) != max(1, expected_pages):
        raise ValueError("Missing API pages")
    if total >= 1000:
        raise ValueError("API result cap reached; subdivide interval before claiming coverage")
    return rows, pages, total


def coverage_csv(coverage):
    path = ARCHIVE / "reports/coverage.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        fields = ["month", "status", "http_status", "api_total_results", "raw_rows", "pages", "unique_event_ids", "error", "request_url"]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in fields} for row in coverage)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Acquire a new immutable snapshot; otherwise reuse latest completed extraction")
    args = parser.parse_args()
    index_path = ARCHIVE / "raw/manifest.json"
    if index_path.exists() and not args.refresh:
        index = read_json(index_path)
        if index["complete"]:
            print("Using saved complete snapshot", index["snapshot_id"])
            return
    snapshot_id = run_id()
    capture = Capture(ARCHIVE / "raw/snapshots" / snapshot_id)
    index = {"snapshot_id": snapshot_id, "started_at_utc": utcnow(), "group_id": 282, "group_title": "Office of Sustainability", "interval": ["2025-08-01", "2026-12-31"], "show_archived": "both", "complete": False, "coverage": [], "pages": []}
    for month in months():
        url = monthly_url(month, "v2", "show_archived/both/paginate/100/")
        coverage = {"month": month, "request_url": url}
        before = len(capture.records)
        try:
            rows, pages, total = paginate(url, lambda url, page: capture.get(url, f"{month}/page-{page:03d}.json"))
            coverage.update(status="ok" if rows else "zero_results", http_status=200, api_total_results=total, raw_rows=len(rows), pages=len(pages), unique_event_ids=len({r["id"] for r in rows}), error="")
            index["pages"].extend(pages)
        except (ValueError, TypeError, KeyError) as exc:
            captured = capture.records[before:]
            coverage.update(status="failed", http_status=captured[-1].get("http_status") if captured else None, error=str(exc), pages=len(captured))
            index["pages"].extend(captured)
        index["coverage"].append(coverage)
        write_json(capture.directory / "extraction.json", index)
        write_json(index_path, index)
        coverage_csv(index["coverage"])
        print(json.dumps(coverage), flush=True)
    index.update(complete=all(r["status"] != "failed" for r in index["coverage"]), finished_at_utc=utcnow())
    write_json(capture.directory / "extraction.json", index)
    write_json(index_path, index)
    if not index["complete"]:
        raise SystemExit("Incomplete extraction: inspect coverage.csv; raw evidence is retained")


if __name__ == "__main__":
    main()
