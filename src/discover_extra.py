from common import ARCHIVE, Capture, monthly_url, run_id, sha256
import json


def main():
    capture = Capture(ARCHIVE / "raw/samples" / run_id())
    capture.get("https://support.livewhale.com/live/profiles/319-showarchived", "archived-docs.html")
    for month in ["2025-08", "2025-10"]:
        body, _ = capture.get(monthly_url(month, "v2", "show_archived/both/"), f"{month}-include-public-archived.json")
        print(month, json.loads(body).get("meta"), flush=True)
    for basename in ["11132_AGF_Standard_Logo.rev.1695068973.png", "11195_3.rev.1695937499.png"]:
        body, record = capture.get("https://calendar.tamu.edu/live/image/gid/282/" + basename, basename)
        if record["http_status"] == 200:
            path = ARCHIVE / "assets/images" / f"{sha256(body)}.png"
            if not path.exists():
                path.write_bytes(body)


if __name__ == "__main__":
    main()
