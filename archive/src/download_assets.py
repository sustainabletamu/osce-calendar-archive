"""Preserve public event media with verified full-size route and thumbnail fallback."""
from __future__ import annotations
import html
import argparse
import re
import struct
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from common import ARCHIVE, Capture, read_json, rows_and_meta, run_id, sha256, write_json


def image_info(body):
    if body.startswith(b"\x89PNG\r\n\x1a\n") and len(body) >= 24:
        return "image/png", *struct.unpack(">II", body[16:24])
    if body[:6] in (b"GIF87a", b"GIF89a") and len(body) >= 10:
        return "image/gif", *struct.unpack("<HH", body[6:10])
    if body.startswith(b"\xff\xd8"):
        pos = 2
        while pos + 4 <= len(body):
            if body[pos] != 255:
                pos += 1
                continue
            marker = body[pos + 1]
            pos += 2
            if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
                continue
            length = int.from_bytes(body[pos:pos + 2], "big")
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                height, width = struct.unpack(">HH", body[pos + 3:pos + 7])
                return "image/jpeg", width, height
            if length < 2:
                break
            pos += length
    if body[:4] == b"RIFF" and body[8:12] == b"WEBP":
        kind = body[12:16]
        if kind == b"VP8X":
            return "image/webp", 1 + int.from_bytes(body[24:27], "little"), 1 + int.from_bytes(body[27:30], "little")
        if kind == b"VP8 " and body[23:26] == b"\x9d\x01\x2a":
            return "image/webp", int.from_bytes(body[26:28], "little") & 16383, int.from_bytes(body[28:30], "little") & 16383
        if kind == b"VP8L" and body[20] == 0x2F:
            bits = int.from_bytes(body[21:25], "little")
            return "image/webp", (bits & 16383) + 1, ((bits >> 14) & 16383) + 1
    raise ValueError("Unsupported or invalid image signature/dimensions")


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.images.append(dict(attrs))


def raw_rows(all_snapshots=False):
    index = read_json(ARCHIVE / "raw/manifest.json")
    pages = {page["path"]: page for page in index["pages"]}
    if all_snapshots:
        for snapshot in (ARCHIVE / "raw/snapshots").glob("*/extraction.json"):
            for page in read_json(snapshot)["pages"]:
                pages.setdefault(page["path"], page)
    for page in sorted(pages.values(), key=lambda p: p["acquired_at_utc"], reverse=True):
        if page["http_status"] == 200:
            rows, _, _ = rows_and_meta(read_json(ARCHIVE / page["path"]))
            for row in rows:
                yield row, page


def fullsize_url(url):
    match = re.search(r"/live/image/(?:.*?/)?gid/(\d+)/(?:.*/)?([^/]+)$", urlsplit(url).path)
    if urlsplit(url).hostname == "calendar.tamu.edu" and match:
        return f"https://calendar.tamu.edu/live/image/gid/{match[1]}/{match[2]}"
    return url


def media_candidates(rows):
    grouped = {}
    for row in rows:
        thumbnail = row.get("thumbnail")
        parser = Images()
        parser.feed(row.get("thumbnail:html") or "")
        attrs = parser.images[0] if parser.images else {}
        sources = [(attrs.get("src") or thumbnail, thumbnail, row.get("thumbnail_caption"), row.get("thumbnail_alt"), attrs)] if thumbnail else []
        for field in ("summary", "description", "contact_info"):
            inline = Images()
            inline.feed(row.get(field) or "")
            sources.extend((im.get("src"), im.get("src"), None, im.get("alt"), im) for im in inline.images)
        for src, fallback, caption, alt, attrs in sources:
            if not src:
                continue
            src = urljoin(row["url"], html.unescape(src))
            fallback = urljoin(row["url"], html.unescape(fallback or src))
            candidate_url = fullsize_url(src)
            # Same observed source ID can appear with and without a revision suffix.
            key = re.sub(r"\.rev\.\d+(?=\.)", "", candidate_url)
            item = grouped.setdefault(key, {"candidate_url": candidate_url, "source_urls": [], "claims": [], "expected_dimensions": None})
            if ".rev." in candidate_url:
                item["candidate_url"] = candidate_url
            for url in (src, fallback):
                if url not in item["source_urls"]:
                    item["source_urls"].append(url)
            claim = {"event_id": str(row["id"]), "caption": caption, "alt_text": alt, "source_url": fallback}
            if claim not in item["claims"]:
                item["claims"].append(claim)
            if attrs.get("data-max-w") and attrs.get("data-max-h"):
                item["expected_dimensions"] = [int(attrs["data-max-w"]), int(attrs["data-max-h"])]
    return list(grouped.values())


def main(offline=False):
    candidates = media_candidates([row for row, _ in raw_rows(all_snapshots=True)])
    # Cache verified captured bodies from ALL prior samples/media runs, including full-size discovery copies.
    cache = {}
    for meta_path in sorted((ARCHIVE / "raw").rglob("*.meta.json")):
        record = read_json(meta_path)
        path = ARCHIVE / record["path"]
        if record.get("http_status") == 200 and path.exists() and sha256(path.read_bytes()) == record["sha256"]:
            cache[record["url"]] = record
    capture = None
    assets = {}
    for number, candidate in enumerate(candidates, 1):
        failure_reasons, best = [], None
        for attempt, url in enumerate(dict.fromkeys([candidate["candidate_url"], *candidate["source_urls"]])):
            try:
                if url in cache:
                    record = cache[url]
                    body = (ARCHIVE / record["path"]).read_bytes()
                else:
                    if offline:
                        raise ValueError("No captured image bytes available in offline cache")
                    if capture is None:
                        capture = Capture(ARCHIVE / "raw/media" / run_id())
                    body, record = capture.get(url, f"asset-{number:03d}-try-{attempt + 1}.bin")
                    cache[url] = record
                if record["http_status"] != 200:
                    raise ValueError(f"HTTP {record['http_status']}")
                mime, width, height = image_info(body)
                supplied_mime = next((v for k, v in record.get("headers", {}).items() if k.lower() == "content-type"), "").split(";", 1)[0]
                if supplied_mime not in (mime, "application/octet-stream") or width <= 0 or height <= 0:
                    raise ValueError(f"MIME or dimension mismatch: {supplied_mime}, {mime}, {width}x{height}")
                best = (body, record, mime, width, height, url)
                break
            except (ValueError, OSError, IndexError, struct.error) as exc:
                failure_reasons.append({"url": url, "reason": str(exc)})
        if best:
            body, record, mime, width, height, url = best
            digest = sha256(body)
            ext = {"image/jpeg": "jpg", "image/png": "png", "image/gif": "gif", "image/webp": "webp"}[mime]
            basename = urlsplit(url).path.rsplit("/", 1)[-1]
            label = re.sub(r"[^a-zA-Z0-9_-]", "_", basename.rsplit(".", 1)[0])[:65]
            path = ARCHIVE / "assets/images" / f"{label}-{digest[:16]}.{ext}"
            if digest in assets:
                path = ARCHIVE / assets[digest]["local_path"]
            # Reuse discovery content-hash filenames rather than storing duplicate bytes.
            existing = [p for p in (ARCHIVE / "assets/images").glob(f"{digest}.*")]
            if existing:
                path = existing[0]
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(body)
            elif sha256(path.read_bytes()) != digest:
                raise ValueError("Existing asset checksum differs")
            item = assets.setdefault(digest, {"asset_id": digest, "event_ids": [], "source_url": url, "source_urls": [], "local_path": str(path.relative_to(ARCHIVE)), "mime_type": mime, "byte_size": len(body), "width_px": width, "height_px": height, "sha256": digest, "downloaded_at_utc": record["acquired_at_utc"], "raw_source_refs": [], "download_status": "downloaded", "quality": "full-size public copy" if url == candidate["candidate_url"] else "thumbnail fallback", "claims": [], "warnings": [], "attempt_failures": []})
            item["raw_source_refs"] = sorted(set(item["raw_source_refs"] + [record["path"]]))
            expected = candidate["expected_dimensions"]
            if expected and [width, height] != expected:
                item["warnings"].append(f"Public dimensions {width}x{height} differ from source data-max {expected}; upload originality unproven")
            item["attempt_failures"].extend(failure_reasons)
        else:
            asset_id = "failed-" + sha256(candidate["candidate_url"].encode())
            item = assets.setdefault(asset_id, {"asset_id": asset_id, "event_ids": [], "source_url": candidate["candidate_url"], "source_urls": [], "local_path": None, "mime_type": None, "byte_size": None, "width_px": None, "height_px": None, "sha256": None, "downloaded_at_utc": None, "download_status": "failed", "quality": None, "claims": [], "warnings": ["No usable public image downloaded"], "attempt_failures": failure_reasons})
        item["source_urls"] = sorted(set(item["source_urls"] + [candidate["candidate_url"], *candidate["source_urls"]]))
        item["event_ids"] = sorted(set(item["event_ids"] + [c["event_id"] for c in candidate["claims"]]))
        for claim in candidate["claims"]:
            if claim not in item["claims"]:
                item["claims"].append(claim)
        # Caption/alt can differ for shared images; preserve all claims, not only the first.
        item["caption"] = item["claims"][0]["caption"]
        item["alt_text"] = item["claims"][0]["alt_text"]
        print(f"Media {number}/{len(candidates)}: {item['download_status']} {item['local_path']}", flush=True)
        write_json(ARCHIVE / "data/assets.json", sorted(assets.values(), key=lambda a: a["asset_id"]))
    if not candidates:
        write_json(ARCHIVE / "data/assets.json", [])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Reconstruct from raw captured image bytes; never contact the source")
    main(offline=parser.parse_args().offline)
