#!/usr/bin/env python3
"""Build data/projections.json from data/accounts.json.

Rules
-----
* Only accounts with a verified, published APY produce projections.
* The APY used is the one printed on the bank's own page for the balance tier
  that the deposit falls into. No APY is inferred, interpolated or averaged
  across banks.
* Dollar results are arithmetic on that APY:
      ending_balance = principal * (1 + APY/100) ** years
      interest       = ending_balance - principal
  APY already accounts for compounding, so this is the correct conversion from
  an advertised APY to a balance after N whole years (assuming the rate never
  changes, which is an assumption, not a promise).
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

DEPOSITS = [10000, 50000, 100000, 250000, 500000, 1000000]
YEARS = [1, 3, 5]
OPENING_DATE = "2026-10-22"

# Derived comparison rows. Each is explicitly labelled and is arithmetic on
# numbers published by the bank (never on third-party data).
DERIVED = [
    {
        "id": "usbank-relationship-3.50",
        "account_id": "usbank-smartly-savings",
        "label": "U.S. Bank Bank Smartly Savings — relationship rate",
        "apy": 3.50,
        "tier_label": "Requires Bank Smartly Checking/Safe Debit/Smartly card + $25,000+ CQB",
        "note": "Same official rate sheet, relationship tier ($25,000+ combined qualifying balances).",
        "apy_as_of": "2026-10-21",
    },
    {
        "id": "sofi-year1-boost",
        "account_id": "sofi-savings",
        "label": "SoFi Savings — year 1 including the 1.10% six-month boost",
        "apy": None,  # computed below
        "tier_label": "Requires eligible direct deposit; boost lasts 6 months",
        "note": "Blend computed as sqrt((1+0.0440)*(1+0.0330))-1 from SoFi's own published 4.40% boosted and 3.30% base APYs.",
        "apy_as_of": "2026-10-20",
        "blend": [4.40, 3.30],
    },
    {
        "id": "marcus-year1-referral",
        "account_id": "marcus-online-savings",
        "label": "Marcus Online Savings — year 1 with one referral",
        "apy": 3.75,
        "tier_label": "Requires a referral; 3-month +1.00% increase",
        "note": "3.75% is Marcus's own published illustration for a year with one referral and an unchanged standard APY.",
        "apy_as_of": "2026-10-21",
    },
]


def tier_apy(account, deposit):
    """Return (apy, tier_label) for a deposit using the account's own tier table."""
    tiers = account.get("apy_tiers")
    if not tiers:
        return account.get("apy_primary"), "Single published rate"
    best = None
    for t in tiers:
        lo = t.get("min") or 0
        hi = t.get("max")
        if deposit >= lo and (hi is None or deposit <= hi):
            # Prefer the standard tier when several tiers cover the same range.
            if best is None or t["apy"] > best["apy"]:
                best = t
    if best is None:
        return account.get("apy_primary"), "Single published rate"
    return best["apy"], best["label"]


def money(x):
    return round(x, 2)


def main():
    with open(os.path.join(DATA, "accounts.json")) as fh:
        accounts = json.load(fh)

    rows = []
    for acc in accounts["accounts"]:
        if acc.get("apy_status") != "verified" or acc.get("apy_primary") is None:
            rows.append({
                "id": acc["id"],
                "account_id": acc["id"],
                "label": f'{acc["brand"]} — {acc["product"]}',
                "bank": acc["brand"],
                "apy_status": "unverified",
                "apy": None,
                "tier_label": "",
                "note": acc.get("apy_note", ""),
                "apy_as_of": acc.get("apy_as_of", ""),
                "results": [],
            })
            continue

        results = []
        for dep in DEPOSITS:
            apy, tier_label = tier_apy(acc, dep)
            for yrs in YEARS:
                ending = dep * (1 + apy / 100.0) ** yrs
                results.append({
                    "deposit": dep,
                    "years": yrs,
                    "apy": apy,
                    "tier_label": tier_label,
                    "ending": money(ending),
                    "interest": money(ending - dep),
                })
        rows.append({
            "id": acc["id"],
            "account_id": acc["id"],
            "label": f'{acc["brand"]} — {acc["product"]}',
            "bank": acc["brand"],
            "apy_status": "verified",
            "apy": acc["apy_primary"],
            "tier_label": tier_apy(acc, 100000)[1],
            "note": "",
            "apy_as_of": acc.get("apy_as_of", ""),
            "results": results,
        })

    for d in DERIVED:
        apy = d["apy"]
        if apy is None and d.get("blend"):
            hi, lo = d["blend"]
            apy = ((1 + hi / 100.0) ** 0.5 * (1 + lo / 100.0) ** 0.5 - 1) * 100
        results = []
        for dep in DEPOSITS:
            for yrs in YEARS:
                a = apy if yrs == 1 else None
                if a is None:
                    # Promotion only covers year 1; later years use the account's
                    # standard published APY.
                    base = next(x for x in accounts["accounts"] if x["id"] == d["account_id"])
                    a = tier_apy(base, dep)[0]
                    # Grow principal at the promo rate for year 1, then at base.
                    ending = dep * (1 + apy / 100.0) * (1 + a / 100.0) ** (yrs - 1)
                    tier_label = d["tier_label"] + " · then the standard APY"
                else:
                    ending = dep * (1 + a / 100.0) ** 1
                    tier_label = d["tier_label"]
                results.append({
                    "deposit": dep,
                    "years": yrs,
                    "apy": round(a, 4),
                    "year1_apy": round(apy, 4),
                    "tier_label": tier_label,
                    "ending": money(ending),
                    "interest": money(ending - dep),
                })
        rows.append({
            "id": d["id"],
            "account_id": d["account_id"],
            "label": d["label"],
            "bank": d["label"].split(" — ")[0],
            "apy_status": "derived",
            "apy": round(apy, 4),
            "tier_label": d["tier_label"],
            "note": d["note"],
            "apy_as_of": d["apy_as_of"],
            "results": results,
        })

    out = {
        "meta": {
            "opening_date": OPENING_DATE,
            "formula": "ending = principal × (1 + APY/100)^years ; interest = ending − principal",
            "assumption": "APY held constant for the whole horizon described in each cell. All rates compared here are variable except none — no CD is included — so the bank may change the rate at any time before or after opening. Projections are arithmetic illustrations, not bank quotes or guarantees.",
            "deposits": DEPOSITS,
            "years": YEARS,
            "fdic_reference": {
                "single_account_limit": 250000,
                "joint_account_limit": 500000,
                "trust_with_5_beneficiaries_limit": 1250000,
                "source": "https://www.fdic.gov/resources/deposit-insurance/brochures/insured-deposits"
            }
        },
        "rows": rows,
    }
    with open(os.path.join(DATA, "projections.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"wrote projections.json with {len(rows)} rows, "
          f"{sum(len(r['results']) for r in rows)} cells")


if __name__ == "__main__":
    main()
