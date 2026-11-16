"""Public-only, serial HTTP capture and shared archive helpers (Python 3.11+)."""
from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT if (ROOT / "raw/manifest.json").exists() else ROOT / "archive"
PUBLIC_HOSTS = {"calendar.tamu.edu", "support.livewhale.com", "marcomm.tamu.edu"}


def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def run_id():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def public_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in PUBLIC_HOSTS or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError(f"Not an allowed public source URL: {url}")
    return url


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Capture:
    """Save exact response body and acquisition metadata before parsing anything."""
    def __init__(self, directory, delay=1.0):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=False)
        self.delay = delay
        self.records = []
        self.opener = urllib.request.build_opener(PublicRedirect())

    def get(self, url, relative, retries=2):
        public_url(url)
        path = self.directory / relative
        if path.exists():
            raise FileExistsError(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {"url": url, "requested_at_utc": utcnow(), "attempts": [], "path": str(path.relative_to(ARCHIVE))}
        body = b""
        for attempt in range(retries + 1):
            time.sleep(self.delay if attempt == 0 else 2 ** attempt)
            started = utcnow()
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "OSCE-Public-Archive/1.0 (public preservation; serial rate-limited requests)", "Accept-Encoding": "identity"})
                with self.opener.open(request, timeout=35) as response:
                    body = response.read()
                    record.update(http_status=response.status, final_url=response.url, headers=dict(response.headers.items()))
                record["attempts"].append({"at_utc": started, "http_status": record["http_status"]})
                break
            except urllib.error.HTTPError as exc:
                body = exc.read()
                record.update(http_status=exc.code, final_url=exc.url, headers=dict(exc.headers.items()), error=str(exc))
                record["attempts"].append({"at_utc": started, "http_status": exc.code, "error": str(exc)})
                if exc.code not in (429, 500, 502, 503, 504):
                    break
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                record.update(http_status=None, error=str(exc))
                record["attempts"].append({"at_utc": started, "error": str(exc)})
        # Never parse, reformat, or sanitize these bytes.
        path.write_bytes(body)
        record.update(acquired_at_utc=utcnow(), byte_size=len(body), sha256=sha256(body))
        write_json(path.with_suffix(path.suffix + ".meta.json"), record)
        self.records.append(record)
        write_json(self.directory / "manifest.json", self.records)
        print(json.dumps({"url": url, "status": record["http_status"], "bytes": len(body), "path": record["path"]}), flush=True)
        return body, record


def monthly_url(month, version="v2", extra=""):
    import calendar
    year, number = map(int, month.split("-"))
    end = calendar.monthrange(year, number)[1]
    prefix = "live/json/v2/events" if version == "v2" else "live/json/events"
    return f"https://calendar.tamu.edu/{prefix}/group/Office%20of%20Sustainability/start_date/{month}-01/end_date/{month}-{end:02d}/response_fields/all/{extra}"


def rows_and_meta(payload):
    if isinstance(payload, list):
        return payload, {}, {}
    if isinstance(payload, dict) and "errors" not in payload:
        rows = payload.get("data", payload.get("results"))
        if isinstance(rows, list):
            return rows, payload.get("meta", {}), payload.get("links", {})
    raise ValueError("Not a recognized successful LiveWhale event response")
