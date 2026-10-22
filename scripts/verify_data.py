#!/usr/bin/env python3
"""Line-by-line integrity checks for SAVINGS1.

Fails loudly if:
  * a rate exists without an official source or a date it was read;
  * a promotion or flag has no source;
  * an account has no FDIC certificate record;
  * the generated site contains an internal broken link, a literal 'None',
    a 'NaN', or an account row without an official source link.
"""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
accounts = json.loads((ROOT / "data/accounts.json").read_text())["accounts"]
promos = json.loads((ROOT / "data/promotions.json").read_text())["promotions"]
flags = json.loads((ROOT / "data/flags.json").read_text())["flags"]

errors: list[str] = []
warnings: list[str] = []


def is_https(u) -> bool:
    if not isinstance(u, str):
        return False
    p = urlparse(u)
    return p.scheme == "https" and bool(p.netloc)


# ---------------------------------------------------------------- data checks
for a in accounts:
    tag = a["id"]
    if not is_https(a.get("source")):
        errors.append(f"{tag}: missing or non-https product source")
    if a.get("headline_apy") is not None:
        if not a.get("rate_as_of"):
            errors.append(f"{tag}: rate present but no rate_as_of date")
        if not is_https(a.get("source")):
            errors.append(f"{tag}: rate present but no official source")
        if not (0 < a["headline_apy"] < 15):
            errors.append(f"{tag}: implausible APY {a['headline_apy']}")
        if a.get("standard_apy") is None:
            errors.append(f"{tag}: headline APY without a post-intro APY")
    for band in (a.get("standard_bands") or []) + (a.get("promo_bands") or []):
        if not (0 <= band["rate"] < 20):
            errors.append(f"{tag}: implausible band rate {band['rate']}")
    if not a.get("fdic", {}).get("cert"):
        errors.append(f"{tag}: no FDIC certificate number")
    if a["app"]["verified"] and not is_https(a["app"].get("source")):
        errors.append(f"{tag}: app marked verified without a source")
    if a["security"]["verified"] and not is_https(a["security"].get("source")):
        errors.append(f"{tag}: security marked verified without a source")

for p in promos:
    if not is_https(p.get("source")):
        errors.append(f"promo {p['bank']}: no official source")
    if p["status"] == "verified" and not p.get("requirements"):
        errors.append(f"promo {p['bank']}: verified offer without conditions")

for f in flags:
    if not is_https(f.get("source")):
        errors.append(f"flag {f['id']}: no source")

# unverified counts
no_apy = [a["bank"] for a in accounts if a.get("headline_apy") is None and a["category"] != "closed"]
no_app = [a["bank"] for a in accounts if not a["app"]["verified"] and a["category"] not in ("closed",)]
print(f"Accounts: {len(accounts)}  |  with verified APY: {len(accounts)-len(no_apy)-1}  |  APY unverified: {len(no_apy)}")
print(f"App unverified: {len(no_app)} -> {', '.join(no_app)}")
print(f"Promotions: {len(promos)}  |  Flags: {len(flags)}")

# ---------------------------------------------------------------- html checks
class Checker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.rows, self.header_rows = [], 0, 0
        self.in_tbody = False
        self.row_links: list[int] = []
        self._cur_links = 0
        self._in_row = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and d.get("href"):
            self.links.append(d["href"])
        if tag == "tr":
            self.rows += 1
            self._in_row = True
            self._cur_links = 0
        if tag == "a" and d.get("href", "").startswith("http") and self._in_row:
            self._cur_links += 1

    def handle_endtag(self, tag):
        if tag == "tr" and self._in_row:
            self.row_links.append(self._cur_links)
            self._in_row = False


pages = sorted((ROOT / "docs").glob("*.html"))
if len(pages) != 9:
    errors.append(f"expected 9 pages, found {len(pages)}")

for page in pages:
    html = page.read_text()
    c = Checker()
    c.feed(html)
    for href in c.links:
        if href.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = (page.parent / href.split("#")[0]).resolve()
        if not target.exists():
            errors.append(f"{page.name}: broken internal link -> {href}")
    for bad in ("None", "NaN", "undefined", "$XXXX"):
        if re.search(rf">\s*{re.escape(bad)}\s*<", html):
            errors.append(f"{page.name}: renders literal '{bad}'")
    if "assets/style.css" not in html:
        errors.append(f"{page.name}: missing stylesheet")

# Every row of the main accounts table must carry an official link
acc_html = (ROOT / "docs/accounts.html").read_text()
m = re.search(r'<table id="acct">(.*?)</table>', acc_html, re.S)
if not m:
    errors.append("accounts.html: main accounts table not found")
else:
    rows = re.findall(r"<tr>(.*?)</tr>", m.group(1), re.S)[1:]
    for i, row in enumerate(rows):
        if "https://" not in row:
            errors.append(f"accounts.html: table row {i+1} has no official source link")
    if len(rows) != len(accounts):
        errors.append(f"accounts.html: {len(rows)} rows for {len(accounts)} accounts")

# Each account's product source must be present in the rendered accounts page
for a in accounts:
    if a["source"] not in acc_html:
        errors.append(f"accounts.html: source for {a['id']} not rendered")

print(f"Pages checked: {len(pages)}")
if warnings:
    print("\nWARNINGS")
    for w in warnings:
        print(" -", w)
if errors:
    print("\nFAILED CHECKS")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)
print("\nAll integrity checks passed.")
