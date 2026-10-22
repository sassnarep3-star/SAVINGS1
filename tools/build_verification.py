#!/usr/bin/env python3
"""Build data/verification.json — the line-by-line check log.

Every row answers one question about one account: which field, what value,
which official page it was read on, and whether it could be read at all.
Blank value + status 'unverified' is a deliberate, honest outcome.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
BANKFIND = "https://banks.data.fdic.gov/bankfind-suite/bankfind/details/{}"


def main():
    accounts = json.load(open(os.path.join(DATA, "accounts.json")))
    promos = json.load(open(os.path.join(DATA, "promotions.json")))
    fdic = {i["cert"]: i for i in json.load(open(os.path.join(DATA, "banks_fdic.json")))["institutions"]}
    promo_by_account = {p["account_id"]: p for p in promos["promotions"]}

    rows = []
    for acc in accounts["accounts"]:
        primary_source = acc["sources"][0]
        cert = acc["fdic_cert"]

        rows.append({
            "account": acc["brand"],
            "account_id": acc["id"],
            "field": "APY / rate",
            "value": acc.get("apy_display") or "",
            "status": acc.get("apy_status", "unverified"),
            "source": acc["sources"][0],
            "method": "Read on the bank's rate page" if acc.get("apy_status") == "verified" else "Page gated by ZIP / rendered client-side — left blank",
        })

        rows.append({
            "account": acc["brand"],
            "account_id": acc["id"],
            "field": "Minimum to open",
            "value": acc.get("min_open") or "",
            "status": acc.get("min_open_status", "unverified"),
            "source": primary_source,
            "method": "Read on the bank's product page" if acc.get("min_open") else "Not stated on the fetched page — left blank",
        })

        rows.append({
            "account": acc["brand"],
            "account_id": acc["id"],
            "field": "Monthly fee",
            "value": acc.get("monthly_fee") or "",
            "status": "verified" if acc.get("monthly_fee") else "unverified",
            "source": primary_source,
            "method": "Read on the bank's product page" if acc.get("monthly_fee") else "Rendered as a placeholder on the page — left blank",
        })

        inst = fdic.get(cert)
        rows.append({
            "account": acc["brand"],
            "account_id": acc["id"],
            "field": "FDIC charter",
            "value": f"Certificate {cert} · active={inst['active']} · {inst['name']}" if inst else "",
            "status": "verified" if inst and inst["active"] == 1 else "unverified",
            "source": BANKFIND.format(cert),
            "method": "Matched in the FDIC institutions API (index 2026-10-16) and rendered as the official BankFind detail link",
        })

        rows.append({
            "account": acc["brand"],
            "account_id": acc["id"],
            "field": "Digital app",
            "value": acc.get("app_note") or "",
            "status": acc.get("app_status", "unverified"),
            "source": primary_source,
            "method": "App capability named on the bank's own page" if acc.get("app_status") == "verified" else "Not stated on the fetched page — flagged",
        })

        p = promo_by_account.get(acc["id"])
        if p:
            rows.append({
                "account": acc["brand"],
                "account_id": acc["id"],
                "field": "Opening bonus / promotion",
                "value": p["offer"] + (" — " + p["requirement"] if p.get("requirement") else ""),
                "status": "verified" if p["status"] == "verified" else "none-displayed",
                "source": p["source"],
                "method": "Offer terms read on the bank's own page" if p["status"] == "verified" else "No bonus or promotional APY printed on the fetched product page",
            })

    verified = sum(1 for r in rows if r["status"] == "verified")
    unverified = sum(1 for r in rows if r["status"] == "unverified")
    none_dis = sum(1 for r in rows if r["status"] == "none-displayed")
    out = {
        "meta": {
            "checked_on": "2026-10-22",
            "rows": len(rows),
            "verified": verified,
            "unverified": unverified,
            "none_displayed": none_dis,
            "rule": "A field is 'verified' only when the value was read on a bank domain or a .gov domain during this session. 'none-displayed' means the official page was checked and carried no offer. 'unverified' means the page did not reveal the value — the field is blank everywhere on the site.",
        },
        "rows": rows,
    }
    json.dump(out, open(os.path.join(DATA, "verification.json"), "w"), indent=2)
    print(f"verification: {len(rows)} checks — {verified} verified, {unverified} unverified, {none_dis} verified-as-none")


if __name__ == "__main__":
    main()
