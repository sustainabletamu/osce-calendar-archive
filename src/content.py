"""Conservative HTML allowlist and plain text conversion for untrusted source text."""
import html
import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

ALLOWED = {"p", "br", "strong", "b", "em", "i", "u", "s", "ul", "ol", "li", "h2", "h3", "h4", "h5", "h6", "blockquote", "a", "div", "span", "table", "thead", "tbody", "tr", "th", "td", "hr"}
BLOCKED = {"script", "style", "iframe", "object", "embed", "svg", "math", "form", "template"}
BREAKS = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "blockquote"}


def safe_url(value, base="https://calendar.tamu.edu/"):
    value = html.unescape(value or "").strip()
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        return None
    try:
        url = urljoin(base, value)
        parsed = urlsplit(url)
    except ValueError:
        return None
    if parsed.scheme.lower() in ("https", "http", "mailto", "tel") and not parsed.username and not parsed.password:
        return url
    return None


class Content(HTMLParser):
    def __init__(self, base, images=None):
        super().__init__(convert_charrefs=True)
        self.base, self.images = base, images or {}
        self.rich, self.plain, self.skip = [], [], []

    def handle_starttag(self, tag, attrs):
        if tag in BLOCKED:
            self.skip.append(tag)
            return
        if self.skip:
            return
        attrs = dict(attrs)
        if tag in BREAKS:
            self.plain.append("\n")
        if tag == "li":
            self.plain.append("• ")
        if tag == "img":
            url = urljoin(self.base, attrs.get("src", ""))
            path = self.images.get(url)
            if path and re.fullmatch(r"\.\./assets/images/[a-zA-Z0-9_.-]+", path):
                self.rich.append(f'<img src="{html.escape(path, quote=True)}" alt="{html.escape(attrs.get("alt") or "", quote=True)}" loading="lazy">')
            else:
                self.rich.append("<span>[Inline image unavailable locally]</span>")
            return
        if tag in ALLOWED:
            attributes = ""
            if tag == "a":
                url = safe_url(attrs.get("href"), self.base)
                if url:
                    attributes = f' href="{html.escape(url, quote=True)}" rel="noopener noreferrer"'
            self.rich.append(f"<{tag}{attributes}>")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in {"br", "hr", "img"}:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.skip:
            if tag == self.skip[-1]:
                self.skip.pop()
            return
        if tag in BREAKS:
            self.plain.append("\n")
        if tag in ALLOWED and tag not in {"br", "hr"}:
            self.rich.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.skip:
            self.rich.append(html.escape(data))
            self.plain.append(data)


def convert(value, base="https://calendar.tamu.edu/", images=None):
    if value is None:
        return None, None
    parser = Content(base, images)
    parser.feed(str(value))
    parser.close()
    plain = "".join(parser.plain).replace("\xa0", " ")
    plain = re.sub(r"[ \t\r\f\v]+", " ", plain)
    plain = re.sub(r" *\n *", "\n", plain)
    plain = re.sub(r"\n{3,}", "\n\n", plain).strip()
    return "".join(parser.rich), plain


def csv_safe(value):
    text = "" if value is None else str(value)
    if text.lstrip().startswith(("=", "+", "-", "@")) or text.startswith(("\t", "\r", "\n")):
        return "'" + text
    return text
