"""Real Chromium file:// QA with networking disabled; also used after ZIP extraction."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from common import ARCHIVE, read_json, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, default=ARCHIVE)
    parser.add_argument("--report", type=Path, default=ARCHIVE / "reports/browser.json")
    parser.add_argument("--browser-executable", type=str, default=None)
    args = parser.parse_args()
    base = args.archive.resolve()
    events = read_json(base / "data/events.json")
    by_id = {e["event_id"]: e for e in events}
    checks, requests, errors = [], [], []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append({"check": name, "passed": True})

    with sync_playwright() as playwright:
        mac_chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        executable = args.browser_executable or (str(mac_chrome) if mac_chrome.exists() else None)
        browser = playwright.chromium.launch(executable_path=executable, headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 1000}, offline=True)
        context.route("https://**/*", lambda route: route.abort())
        context.route("http://**/*", lambda route: route.abort())
        context.add_init_script("Object.defineProperty(navigator, 'clipboard', {get: () => undefined});")
        page = context.new_page()
        page.on("request", lambda request: requests.append(request.url))
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto((base / "site/index.html").as_uri(), wait_until="load")
        check("Disk-opened file:// gallery renders all records while offline", page.locator(".card").count() == len(events))
        page.locator(".card img").evaluate_all("images => images.forEach(image => image.loading='eager')")
        # Poll through the inspector; wait_for_function injects eval, correctly blocked by our CSP.
        for _ in range(100):
            if page.locator(".card img").evaluate_all("images => images.every(image => image.complete && image.naturalWidth > 0)"):
                break
            page.wait_for_timeout(100)
        check("All card image references load from local files", page.locator(".card img").evaluate_all("images => images.every(image => image.src.startsWith('file:') && image.naturalWidth > 0)"))
        page.screenshot(path=str(args.report.parent / "gallery-desktop.png"))
        page.locator("#year").select_option("2025")
        page.locator("#month").select_option("10")
        check("October2025 filter:16 IDs,18 dates", page.locator(".card").count() == 16 and "18 matching" in page.locator("#results").inner_text())
        page.locator("#month").select_option("08")
        check("Zero-result month shows labelled empty state", page.locator(".card").count() == 0 and page.locator(".empty").count() == 1)
        page.locator("#reset").click()
        page.locator("#search").fill("Hullabloom")
        check("Search finds historical full text record", page.locator(".card").count() == 1)
        page.locator(".card").click()
        check("Full description plain text is exact and selectable", page.locator("#text-description").input_value() == by_id["379688"]["description_text"])
        page.locator('[data-copy="description"]').click()
        check("Clipboard-unavailable fallback reveals and selects text", page.locator("#plain-description").get_attribute("open") is not None and "Text selected" in page.locator("#copy-status").inner_text())
        check("Full-size image download points to a local file", page.locator("#detail a[download]").get_attribute("href").startswith("../assets/images/"))
        page.locator("#detail-title").click()
        check("Clicks inside event frame keep the detail open", page.locator("#event-dialog").is_visible())
        title_box = page.locator("#detail-title").bounding_box()
        page.mouse.move(title_box["x"] + 12, title_box["y"] + 12)
        page.mouse.down()
        page.mouse.move(5, 5, steps=8)
        page.mouse.up()
        check("Text drag beginning inside frame does not dismiss detail", page.locator("#event-dialog").is_visible())
        page.mouse.click(5, 5)
        check("Click outside event frame returns to gallery", not page.locator("#event-dialog").is_visible())
        page.locator(".card").click()
        page.keyboard.press("Escape")
        check("Keyboard Escape closes modal", not page.locator("#event-dialog").is_visible())
        page.locator("#reset").click()
        for event_id in ("362803", "359400", "374684", "377642"):
            page.locator(f'[data-event="{event_id}"]').click()
            check(f"Risk-case detail {event_id} opens with source attribution", page.locator("#detail-title").inner_text() == by_id[event_id]["title"] and "Original public event page" in page.locator("#detail").inner_text())
            if event_id == "362803":
                check("No-image event has labelled placeholder", page.locator("#detail figure img").count() == 0 and "No image provided" in page.locator("#detail").inner_text())
            if event_id == "359400":
                check("Multi-day event displays all five captured dates", page.locator(".date-list li").count() == 5)
            if event_id == "374684":
                check("Null timed end is explicitly labelled", "End time not provided" in page.locator(".date-list").inner_text())
            page.locator("#close-dialog").click()
        # A phrase unique to the full body, absent from title/summary, proves description indexing.
        target = next(e for e in events if e["event_id"] == "379688")
        import re
        words = re.findall(r"[A-Za-z]{6,}", target["description_text"])
        term = next(w for w in words if w.lower() not in (target["title"] + (target["summary_text"] or "")).lower())
        page.locator("#search").fill(term)
        check("Search indexes full description body", page.locator('[data-event="379688"]').count() == 1)
        page.locator("#reset").click()
        page.set_viewport_size({"width": 390, "height": 844})
        check("Mobile layout has no horizontal overflow", page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
        page.screenshot(path=str(args.report.parent / "gallery-mobile.png"))
        remote_requests = [url for url in requests if url.startswith(("https:", "http:"))]
        check("No remote requests made during browsing/search/details", not remote_requests)
        check("No JavaScript runtime errors", not errors)
        browser.close()
    result = {"passed": True, "mode": "file://; browser offline=True; HTTP(S) routes aborted; clipboard disabled for fallback", "archive": str(base), "checks": checks, "remote_requests": [], "runtime_errors": errors}
    write_json(args.report, result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
