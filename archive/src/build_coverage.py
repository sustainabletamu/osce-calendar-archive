"""Generate a formatted, offline coverage page from the preserved archive records."""
import calendar
import html
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo
from common import ROOT


def escape(value):
    return html.escape(str(value), quote=True)


def build_coverage(events, occurrences, assets, index, capture_label, archive_dir):
    coverage = index["coverage"]
    missing = Counter(field for event in events for field in event["missing_fields"])
    timed = [row for row in occurrences if not row["all_day"]]
    missing_ends = sum(row["end_iso_original"] is None for row in timed)
    captured_month = datetime.fromisoformat(index.get("finished_at_utc", index["started_at_utc"])).astimezone(ZoneInfo("America/Chicago")).strftime("%Y-%m")
    table_rows = []
    for row in coverage:
        year, month = map(int, row["month"].split("-"))
        label = f"{calendar.month_name[month]} {year}"
        status = row["status"]
        description, style = {"ok": ("Events returned", "success"), "zero_results": ("Zero results", "empty")}.get(status, ("Retrieval failed", "failed"))
        future = '<span class="future">Future at capture</span>' if row["month"] > captured_month else ""
        cells = "".join(f'<td class="number">{escape("—" if row.get(key) in (None, "") else row[key])}</td>' for key in ("raw_rows", "unique_event_ids", "pages"))
        table_rows.append(f'<tr><th scope="row">{escape(label)}{future}</th><td><span class="badge {style}">{description}</span><span class="http">HTTP {escape(row.get("http_status") or "unavailable")}</span></td>{cells}</tr>')
    field_labels = [("description", "Separate full description"), ("summary", "Summary"), ("contact_info", "Contact information"), ("location", "Structured location or online URL"), ("image", "Event image")]
    field_rows = [f'<tr><th scope="row">{label}</th><td class="number">{missing[key]}</td><td>{len(events)} source event IDs</td></tr>' for key, label in field_labels]
    field_rows.append(f'<tr><th scope="row">End time</th><td class="number">{missing_ends}</td><td>{len(timed)} timed occurrences</td></tr>')
    no_categories = sum(not any(value for value in event["categories"].values()) for event in events)
    no_tags = sum(not any(value for value in event["tags"].values()) for event in events)
    no_copy = sum(not (event["summary_text"] or event["description_text"]) for event in events)
    copy_context = ("Every archived event contains a summary or a full description." if no_copy == 0 else f"{no_copy} event IDs lack both summary and full description.") + " A missing separate description does not mean all event copy is missing. Source fields remain separate and blank values are preserved."
    successful = sum(row["status"] in ("ok", "zero_results") for row in coverage)
    zero_months = sum(row["status"] == "zero_results" for row in coverage)
    replacements = {
        "__CAPTURE_DATE__": escape(capture_label),
        "__EVENTS__": str(len(events)), "__OCCURRENCES__": str(len(occurrences)),
        "__IMAGES__": str(sum(asset["download_status"] == "downloaded" for asset in assets)),
        "__MONTHS__": str(len(coverage)), "__SUCCESSFUL__": str(successful), "__ZERO_MONTHS__": str(zero_months),
        "__COVERAGE_ROWS__": "\n".join(table_rows), "__FIELD_ROWS__": "\n".join(field_rows),
        "__COPY_CONTEXT__": escape(copy_context), "__NO_CATEGORIES__": str(no_categories), "__NO_TAGS__": str(no_tags),
    }
    page = (ROOT / "src/coverage_template.html").read_text(encoding="utf-8")
    for key, value in replacements.items():
        page = page.replace(key, value)
    destination = archive_dir / "site/coverage.html"
    destination.write_text(page, encoding="utf-8")
    print(f"Built {destination}: {len(coverage)} months, {successful} successful responses")
