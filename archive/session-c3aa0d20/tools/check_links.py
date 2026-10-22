#!/usr/bin/env python3
"""Verify every link in the site and in the data files.

This environment can reach GitHub and package registries only, so an HTTP
status check of chase.com or fdic.gov is not possible from the sandbox. Instead
the check is stricter about provenance:

  * every external URL must be registered in data/sources_fetched.json, and
  * FDIC BankFind detail links must match the verified certificate numbers, and
  * every internal link must resolve to a file that exists.

Exit code 1 on any problem, so CI or a human can gate on it.
"""

import json
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
PAGES = ["index.html", "rates.html", "returns.html", "promotions.html", "rules.html",
         "security.html", "flagged.html", "methodology.html"]

ALLOWED_EXTRA = {
    "https://github.com/sassnarep3-star/SAVINGS1": "repository link printed in the footer",
}

HREF = re.compile(r'(?:href|src)="([^"]+)"')


def main():
    sources = json.load(open(os.path.join(DATA, "sources_fetched.json")))
    known = {s["url"].rstrip("/") for s in sources["sources"]}
    pattern = sources["patterns"][0]["pattern"]
    pat_re = re.compile("^" + re.escape(pattern).replace(r"\{cert\}", r"(\d+)") + "$")
    certs = {str(i["cert"]) for i in json.load(open(os.path.join(DATA, "banks_fdic.json")))["institutions"]}

    problems = []
    checked = 0

    # ---- 1. HTML links
    for page in PAGES:
        path = os.path.join(ROOT, page)
        if not os.path.exists(path):
            problems.append(f"missing page: {page}")
            continue
        html = open(path).read()
        for url in HREF.findall(html):
            checked += 1
            if url.startswith("#") or url.startswith("data:"):
                continue
            if url.startswith("http"):
                base = url.rstrip("/")
                if base in known or url in ALLOWED_EXTRA:
                    continue
                m = pat_re.match(url)
                if m and m.group(1) in certs:
                    continue
                problems.append(f"{page}: unregistered external link {url}")
            else:
                target = urllib.parse.urlparse(url).path
                if not target:
                    continue
                if not os.path.exists(os.path.join(ROOT, target)):
                    problems.append(f"{page}: broken internal link {url}")

    # ---- 2. data files
    for name in ["accounts.json", "promotions.json", "flagged.json", "verification.json", "projections.json"]:
        blob = open(os.path.join(DATA, name)).read()
        for url in set(re.findall(r'https?://[^"\s<>]+', blob)):
            checked += 1
            base = url.rstrip("/")
            if base in known or url in ALLOWED_EXTRA:
                continue
            m = pat_re.match(url)
            if m and m.group(1) in certs:
                continue
            if "banks.data.fdic.gov/api/institutions" in url:
                # API query URLs are logged verbatim in banks_fdic.json meta
                continue
            problems.append(f"data/{name}: unregistered URL {url}")

    # ---- 3. every account has a source and every row is in the projections
    accounts = json.load(open(os.path.join(DATA, "accounts.json")))["accounts"]
    proj = {r["account_id"] for r in json.load(open(os.path.join(DATA, "projections.json")))["rows"]}
    for a in accounts:
        if not a.get("sources"):
            problems.append(f"account {a['id']} has no source link")
        if a["id"] not in proj:
            problems.append(f"account {a['id']} is missing from projections.json")

    print(f"checked {checked} link references across {len(PAGES)} pages and 5 data files")
    if problems:
        print(f"FAIL — {len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("PASS — every external link is an official source on file; every internal link resolves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
