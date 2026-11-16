"""Extract ZIP into a fresh directory and verify every checksum and local site link."""
import argparse
import re
import tempfile
import urllib.parse
import zipfile
from pathlib import Path
from common import ROOT, read_json, sha256, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("zip", type=Path)
    parser.add_argument("--report", type=Path, default=ROOT / "dist/package-verification.json")
    args = parser.parse_args()
    directory = Path(tempfile.mkdtemp(prefix="osce-clean-"))
    with zipfile.ZipFile(args.zip) as archive:
        for info in archive.infolist():
            if not (directory / info.filename).resolve().is_relative_to(directory.resolve()):
                raise ValueError("Unsafe ZIP path")
        archive.extractall(directory)
    base = directory / "archive"
    manifest = read_json(base / "manifest.json")
    for item in manifest["files"]:
        body = (base / item["path"]).read_bytes()
        assert len(body) == item["byte_size"] and sha256(body) == item["sha256"], item["path"]
    expected = {item["path"] for item in manifest["files"]} | {"manifest.json"}
    assert expected == {str(p.relative_to(base)) for p in base.rglob("*") if p.is_file()}
    page = (base / "site/index.html").read_text(encoding="utf-8")
    local_links = []
    for url in re.findall(r'(?:href|src)="([^"<]+)"', page):
        # Ignore generic JS template strings; real file links in static markup must resolve.
        if url.startswith("../") and "${" not in url:
            target = (base / "site" / urllib.parse.unquote(url.split("#", 1)[0])).resolve()
            assert target.is_relative_to(base.resolve()) and target.exists(), url
            local_links.append(url)
    for asset in read_json(base / "data/assets.json"):
        if asset["download_status"] == "downloaded":
            assert (base / asset["local_path"]).exists()
    result = {"passed": True, "zip": str(args.zip.resolve()), "zip_sha256": sha256(args.zip.read_bytes()), "clean_archive": str(base), "inventoried_files_verified": len(manifest["files"]), "static_local_links_checked": local_links, "canonical_assets_checked": len(read_json(base / "data/assets.json"))}
    write_json(args.report, result)
    print(result)


if __name__ == "__main__":
    main()
