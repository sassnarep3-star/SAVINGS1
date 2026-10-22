#!/usr/bin/env python3
"""Validate local navigation/fragment links and source links in published tables."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted(ROOT.glob("*.html"))

class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.in_tbody = False
        self.in_row = False
        self.row_links = []
        self.table_rows = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
            if self.in_tbody and self.in_row:
                self.row_links.append(attrs["href"])
        if tag == "tbody":
            self.in_tbody = True
        elif tag == "tr" and self.in_tbody:
            self.in_row = True
            self.row_links = []
    def handle_endtag(self, tag):
        if tag == "tr" and self.in_row:
            self.table_rows.append(self.row_links[:])
            self.in_row = False
        elif tag == "tbody":
            self.in_tbody = False

scans = {p.name: Scan() for p in PAGES}
for name, scan in scans.items():
    scan.feed((ROOT / name).read_text(encoding="utf-8"))

OFFICIAL_DOMAINS = (
    "fdic.gov", "wellsfargo.com", "capitalone.com", "citi.com", "citibank.com",
    "chase.com", "bankofamerica.com", "bac-assets.com",
)

def is_official_source(href):
    host = (urlsplit(href).hostname or "").lower()
    return any(host == domain or host.endswith("." + domain) for domain in OFFICIAL_DOMAINS)

errors = []
for name, scan in scans.items():
    for href in scan.links:
        u = urlsplit(href)
        if u.scheme or u.netloc or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        target = (ROOT / unquote(u.path)).resolve() if u.path else (ROOT / name).resolve()
        if ROOT.resolve() not in target.parents and target != ROOT.resolve():
            errors.append(f"{name}: link escapes site root: {href}")
            continue
        if not target.is_file():
            errors.append(f"{name}: missing local file for {href}")
            continue
        if u.fragment:
            target_name = target.name
            target_scan = scans.get(target_name)
            if target_scan is None:
                target_scan = Scan()
                target_scan.feed(target.read_text(encoding="utf-8"))
            if unquote(u.fragment) not in target_scan.ids:
                errors.append(f"{name}: missing fragment #{u.fragment} in {target_name}")
    for index, links in enumerate(scan.table_rows, start=1):
        if not any(urlsplit(link).scheme in {"http", "https"} and is_official_source(link) for link in links):
            errors.append(f"{name}: table body row {index} has no recognized official source link")

if errors:
    print("Site validation failed:")
    print("\n".join(f" - {e}" for e in errors))
    raise SystemExit(1)
print(f"Validated {len(PAGES)} HTML pages, local links/fragments, and official source links in every table row.")
