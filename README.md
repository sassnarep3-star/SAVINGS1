# SAVINGS1

A source-linked comparison of nationally available, FDIC-insured savings accounts at large US banks — built to answer one question:

> **For a deposit opened on 2026-10-22, which national bank with a digital app pays the most — and how much of that return survives after the promotional rate ends?**

**Live dashboard:** https://sassnarep3-star.github.io/SAVINGS1/

---

## What is in the site

| Page | What it shows |
|---|---|
| **Overview** | Key findings, best 1-year return at $250,000, verification status |
| **Accounts** | All 18 products: headline APY, post-intro APY, minimums, fees, FDIC certificate, app status, official source |
| **Returns** | Interest by deposit size ($1k–$1M), 1-year and 5-year, blended APY, winner at each tier |
| **Promotions** | Cash bonuses, promo APYs, referral offers, deadlines, exact conditions |
| **FDIC coverage** | $250k rule, ownership categories, insured vs uninsured amounts, programme coverage |
| **Analysis** | Each rate vs the Fed target range, the FDIC national average, a 6-month Treasury, and the bank's own post-promo rate |
| **Sources** | Every official page used, with what it verified |
| **Flagged for review** | 19 irregularities, conflicts, and unverified values |
| **Method** | Scope, formulas, verification standard, limitations |

## Headline results (verified 2026-10-22)

| | |
|---|---|
| Highest verified 1-year return on $250,000 | **Axos Bank — 4.28% blended, $10,703** (requires an Axos ONE checking bundle and monthly activity) |
| Best no-conditions rate | **EverBank — 4.20% flat, $0 to open, $0 monthly fee** |
| Best 6-month boost with no ongoing conditions | **Openbank — 4.35% then 4.00%** |
| FDIC national savings average | **0.38%** (2026-10-19) |
| Federal funds target range | **3.75%–4.00%** (after 2026-09-17) |
| 6-month / 12-month Treasury | **4.33% / 4.54%** |

All 12 APYs are variable. Only E*TRADE's 4.25% six-month boost is described as guaranteed for its term.

## Data provenance

Every number in `data/` was read from an official page, and every table row links to it:

- **Bank product/rate pages** — APY, minimums, fees, app, promo terms
- **`api.fdic.gov`** — certificate number and active status for every bank
- **`fdic.gov/national-rates-and-rate-caps`** — national average, Treasury yields, CD averages
- **`federalreserve.gov`** — target range and 2026 FOMC change

No aggregator, review site, or press article is the source for any value.

### Rules applied

1. If a value could not be read from an official page, it is **blank** — never estimated or copied from a third party.
2. Blank values are published on **Flagged for review**, with the URL that was attempted.
3. Conflicting official pages are both cited; the more conservative reading is used and the conflict is flagged.
4. FDIC status is checked by **certificate number**, not by a logo on a marketing page.
5. Bonuses are never folded into an APY; they are listed separately.

## Repository layout

```
data/
  accounts.json      verified account records (rates, terms, sources, FDIC certs)
  promotions.json    bonus and promo terms
  fdic.json          coverage rules + per-bank certificate records
  flags.json         irregularities and unverified items
scripts/
  build_site.py      generates docs/ from data/ (all return math lives here)
  verify_data.py     integrity checks: sources, dates, links, no literal "None"/"NaN"
*.html, assets/      the published site (GitHub Pages: main branch, root)
COORDINATION.md      shared task board and verification log
```

## Rebuild

```bash
python3 scripts/build_site.py    # data/*.json -> *.html at repo root
python3 scripts/verify_data.py   # fails on missing sources or broken links
```

CI (`.github/workflows/verify.yml`) runs both on every push and fails if the published pages are out of date with `data/`.

## Method summary

Interest is compounded at the stated APY. Introductory rates apply for exactly the advertised period, then the balance is re-tiered at the bank's published post-intro rate. Tiered accounts are modelled as marginal or cliff according to how the bank describes them (CIT and Barclays are cliffs). Five-year figures hold the published post-intro rate constant and are projections, not guarantees. Bonus cash is excluded.

Deposit tiers: $1,000 · $10,000 · $25,000 · $50,000 · $100,000 · $250,000 · $500,000 · $1,000,000.

## Known limitations

- APYs change daily; verification is a point-in-time snapshot dated 2026-10-22.
- Four Big Four APYs (Chase, Bank of America, Citi, Wells Fargo) are unverified for the New York market and are excluded from every calculation.
- Mobile app existence was not confirmed for Ally, Marcus, Barclays, or Wells Fargo.
- Axos does not publish the balance cap on its 5.00% intro; the model conservatively assumes the first $50,000.
- This is research, not financial, tax, or legal advice.

## Coordination

`COORDINATION.md` is the shared task board. This repository was built by session `S-830079CD` on branch `arena/830079cd-savings1`; the board records the claim, the verification log, and the integration result.
