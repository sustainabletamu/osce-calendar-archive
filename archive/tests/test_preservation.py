import copy
import json
import socket
from pathlib import Path
import pytest
from common import ARCHIVE, read_json, sha256
from content import convert, csv_safe
from download_assets import fullsize_url, raw_rows
from fetch_events import paginate
from normalize import local_date, mark_visibility, normalize
from validate import validate_asset


@pytest.fixture
def source():
    row, page = next(raw_rows())
    return copy.deepcopy(row), page


def test_pagination_traverses_all_pages(source):
    row, _ = source
    first = "https://calendar.tamu.edu/live/json/v2/events/group/Office%20of%20Sustainability/?page=1"
    calls = []
    def get(url, number):
        calls.append(url)
        return json.dumps({"meta": {"total_results": 3, "total_pages": 3, "page": number}, "links": {"next": first[:-1] + str(number + 1) if number < 3 else None}, "data": [{**row, "id": number}]}).encode(), {"http_status": 200}
    rows, pages, count = paginate(first, get)
    assert [r["id"] for r in rows] == [1, 2, 3]
    assert len(calls) == len(pages) == count == 3


def test_pagination_detects_silent_truncation(source):
    row, _ = source
    with pytest.raises(ValueError, match="reconcile"):
        paginate("https://calendar.tamu.edu/live/json/v2/events/", lambda u, p: (json.dumps({"meta": {"total_results": 2, "total_pages": 2}, "data": [row], "links": {}}).encode(), {"http_status": 200}))


def test_recurring_and_multiday_identity_and_duplicates(source):
    row, page = source
    second = {**row, "date_iso": "2025-09-12T13:00:00-05:00", "date2_iso": None}
    other_id = {**second, "id": 999999}
    events, occurrences = normalize([(row, page), (row, page), (second, page), (other_id, page)], [])
    assert len(events) == 2
    assert len(occurrences) == 3
    assert len({o["occurrence_id"] for o in occurrences}) == 3


def test_dst_and_original_dates():
    assert local_date("2026-03-08T07:30:00+00:00") == "2026-03-08T01:30:00-06:00"
    assert local_date("2026-03-08T08:30:00+00:00") == "2026-03-08T03:30:00-05:00"
    assert local_date(None) is None


def test_no_inferred_end_or_full_description(source):
    row, page = source
    row.update(date2_iso=None, description=None, summary="<p>Real summary</p>", is_all_day=0)
    events, occurrences = normalize([(row, page)], [])
    assert events[0]["description_html_original"] is None
    assert events[0]["description_text"] is None
    assert occurrences[0]["end_iso_original"] is None
    assert occurrences[0]["display_end_local"] is None


def test_html_security_and_readable_text():
    rich, plain = convert('<p onclick="evil()">A &amp; B<br>two</p><script>alert(1)</script><iframe src="x">bad</iframe><a href="jav&#x61;script:alert(1)">link</a><a href="https://example.org/x?a=1&amp;b=2">safe</a><img src="https://tracker.org/x" onerror="evil()"><svg onload="evil()"/>')
    assert "<script" not in rich and "<iframe" not in rich and "<svg" not in rich
    assert "onclick" not in rich and "onerror" not in rich and "javascript:" not in rich
    assert "https://tracker.org" not in rich
    assert 'href="https://example.org/x?a=1&amp;b=2"' in rich
    assert "A & B\ntwo" in plain and "alert" not in plain


def test_malformed_link_preserves_text():
    rich, plain = convert('<a href="https://[bad">Bad link</a><p>Important text</p>')
    assert "Important text" in plain and "Bad link" in plain
    assert "href=" not in rich


def test_refresh_preserves_no_longer_public_records(source):
    row, page = source
    later = {**row, "id": 999999}
    events, occurrences = normalize([(row, page), (later, page)], [])
    mark_visibility(events, occurrences, [(later, page)])
    retained = next(e for e in events if e["event_id"] == str(row["id"]))
    assert retained["visibility_status"] == "preserved_from_earlier_snapshot"
    assert retained["source_fields"][0] == row
    assert len(events) == len(occurrences) == 2


@pytest.mark.parametrize("value", ["=1+1", "+SUM(A:A)", "-1+2", "@SUM(A:A)", "  =1", "\tcmd", "\n=bad"])
def test_csv_formula_injection(value):
    assert csv_safe(value).startswith("'")


def test_fullsize_transform_preserves_observed_filename():
    assert fullsize_url("https://calendar.tamu.edu/live/image/scale/2x/gid/282/width/80/height/80/crop/1/src_region/0,0,1800,1200/11195_3.rev.1695937499.png") == "https://calendar.tamu.edu/live/image/gid/282/11195_3.rev.1695937499.png"


def test_media_hash_validation_rejects_corruption(tmp_path):
    asset = read_json(ARCHIVE / "data/assets.json")[0]
    target = tmp_path / asset["local_path"]
    target.parent.mkdir(parents=True)
    target.write_bytes((ARCHIVE / asset["local_path"]).read_bytes())
    assert validate_asset(asset, tmp_path)
    target.write_bytes(target.read_bytes() + b"corruption")
    with pytest.raises(ValueError, match="checksum"):
        validate_asset(asset, tmp_path)


def test_offline_regeneration_is_identical(monkeypatch):
    import normalize as module
    outputs = [ARCHIVE / name for name in ("data/events.json", "data/occurrences.json", "data/assets.json", "exports/events.csv", "exports/occurrences.csv")]
    before = {p: sha256(p.read_bytes()) for p in outputs}
    raw_before = {p: sha256(p.read_bytes()) for p in (ARCHIVE / "raw").rglob("*") if p.is_file()}
    def denied(*args, **kwargs):
        raise AssertionError("Offline regeneration attempted a network connection")
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)
    module.main()
    assert before == {p: sha256(p.read_bytes()) for p in outputs}
    assert raw_before == {p: sha256(p.read_bytes()) for p in raw_before}


def test_reconstruct_json_images_and_site_from_raw_only(tmp_path, monkeypatch):
    import shutil
    import common
    import download_assets
    import normalize as normalization
    import build_site
    shutil.copytree(ARCHIVE / "raw", tmp_path / "raw")
    for module in (common, download_assets, normalization, build_site):
        monkeypatch.setattr(module, "ARCHIVE", tmp_path)
    def denied(*args, **kwargs):
        raise AssertionError("Raw-only rebuild attempted networking")
    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    download_assets.main(offline=True)
    normalization.main()
    build_site.main()
    assert len(read_json(tmp_path / "data/events.json")) == len(read_json(ARCHIVE / "data/events.json"))
    assert len(read_json(tmp_path / "data/occurrences.json")) == len(read_json(ARCHIVE / "data/occurrences.json"))
    rebuilt_assets = read_json(tmp_path / "data/assets.json")
    assert {a["sha256"] for a in rebuilt_assets} == {a["sha256"] for a in read_json(ARCHIVE / "data/assets.json")}
    assert (tmp_path / "site/index.html").exists()
