#!/usr/bin/env python3
"""Dependency-free integrity checks for the static research dashboard."""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "rates.html", "accounts.html", "offers.html", "coverage.html", "flagged.html"]
OFFICIAL_HOSTS = (
    "fdic.gov", "edie.fdic.gov", "marcus.com", "ally.com", "wellsfargo.com",
    "capitalone.com", "chase.com", "jpmorganchase.com", "bankofamerica.com",
    "citi.com", "citibank.com", "americanexpress.com", "barclays", "usbank.com",
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key == "href" and value:
                self.links.append(value)
            if tag == "script" and key == "src" and value:
                self.links.append(value)
            if tag == "link" and key == "href" and value:
                self.links.append(value)


def main() -> int:
    errors: list[str] = []
    data_path = ROOT / "data/accounts.json"
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except Exception as exc:  # report malformed research data cleanly in CI
        print(f"FAIL: cannot read account data: {exc}")
        return 1

    if data.get("asOf") != "2026-10-22" or data.get("openingDate") != "2026-10-22":
        errors.append("research and scenario opening dates must match 2026-10-22")
    if data.get("horizonEnd") != "2027-10-22":
        errors.append("scenario horizon end must be 2027-10-22")
    if data.get("fdic", {}).get("limit") != 250000:
        errors.append("FDIC limit should be $250,000")

    products = data.get("products", [])
    if len(products) < 5:
        errors.append("expected at least five researched bank products")
    seen = set()
    for product in products:
        name = product.get("bank", "<unnamed>")
        if product.get("id") in seen:
            errors.append(f"duplicate product id for {name}")
        seen.add(product.get("id"))
        for field in ("rateSource", "termsSource", "offerSource", "securitySource", "fdicSource", "appSource"):
            url = product.get(field)
            parsed = urlparse(url or "")
            host = parsed.hostname or ""
            if parsed.scheme != "https" or not any(host == h or host.endswith("." + h) for h in OFFICIAL_HOSTS):
                errors.append(f"{name}: {field} must point to an official HTTPS source, got {url!r}")
        apy = product.get("apy")
        if apy is None:
            if product.get("apyLabel") != "—" or product.get("rateStatus") != "unverified":
                errors.append(f"{name}: missing APY must have blank label and unverified status")
        elif not isinstance(apy, (int, float)) or not 0 <= apy <= 25:
            errors.append(f"{name}: invalid APY {apy!r}")
        if not product.get("apyDate") or not product.get("opening") or not product.get("offer") or not product.get("securityNotes"):
            errors.append(f"{name}: missing date/opening/offer/security summary")
        for field in ("rateSourceAlt",):
            url = product.get(field)
            if url:
                parsed = urlparse(url)
                host = parsed.hostname or ""
                if parsed.scheme != "https" or not any(host == h or host.endswith("." + h) for h in OFFICIAL_HOSTS):
                    errors.append(f"{name}: {field} must point to an official HTTPS source, got {url!r}")

    for page in PAGES:
        path = ROOT / page
        if not path.is_file():
            errors.append(f"missing page: {page}")
            continue
        parser = LinkParser()
        parser.feed(path.read_text(encoding="utf-8"))
        for link in parser.links:
            if link.startswith(("https://", "http://", "mailto:", "#")):
                continue
            local = link.split("#", 1)[0].split("?", 1)[0]
            if local and not (ROOT / page).parent.joinpath(local).resolve().exists():
                errors.append(f"{page}: broken local link or asset: {link}")

    for asset in (ROOT / "assets/site.js", ROOT / "assets/site.css", ROOT / "data/accounts.json"):
        if not asset.is_file():
            errors.append(f"missing site asset: {asset.relative_to(ROOT)}")

    if errors:
        print("SITE CHECK FAILED")
        for error in errors:
            print(f" - {error}")
        return 1
    print(f"SITE CHECK PASSED: {len(PAGES)} pages; {len(products)} products; all product source links use official HTTPS domains.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
