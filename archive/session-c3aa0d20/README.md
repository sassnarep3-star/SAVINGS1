# SAVINGS1 — verified national savings-account comparison

A static dashboard that answers one question with primary sources only:

> Where do I put savings so that it earns the most, while every dollar stays inside FDIC insurance?

**Live site:** https://sassnarep3-star.github.io/SAVINGS1/

Snapshot: bank rates and fees read on **2026-10-21 / 2026-10-22**. Projections assume the account is opened on
**2026-10-22** and the published APY does not change.

## What is in here

| Path | What it is |
|---|---|
| `index.html` | Dashboard: best verified rates, the $250,000 comparison, decision shortcuts |
| `rates.html` | All 15 accounts: APY, as-of date, rate scope, minimums, fees, app, source |
| `returns.html` | Interest earned at $10k → $1M over 1, 3 and 5 years; maximum-FDIC placement table |
| `promotions.html` | Cash bonuses and promotional APYs with exact conditions and deadlines |
| `rules.html` | Opening requirements, funding windows, balance ceilings, withdrawal rules |
| `security.html` | FDIC certificate numbers, active status, assets, published security statements |
| `flagged.html` | Every unverified value and irregular finding, with the official page to check |
| `methodology.html` | Formula, snapshot dates, all sources, 90-row verification log, repo audit |
| `data/` | The dataset the site is generated from (JSON) |
| `tools/` | Build and verification scripts (stdlib Python only) |
| `COORDINATION.md` | The shared task board used for multi-session work |

## Verification rules this dataset follows

1. **Official sources only.** A value is used only if it was read on the bank's own domain or a `.gov` domain.
   Rate aggregators and news articles are rejected; other banks' comparison tables are rejected too.
2. **Blank beats guessed.** If an official page gates a value behind a ZIP code or renders it client-side, the cell
   stays empty and the item is listed on `flagged.html`. Ten fields ended that way: the Chase, Bank of America,
   Citibank and TD Bank APYs; the Bank of America and Citibank minimum-to-open; the Bank of America fee; and the
   mobile-app claims for American Express and both Barclays products.
3. **Dates are copied.** Each APY carries the as-of date printed on the page; when no date is printed the cell is
   blank and the row is flagged.
4. **Arithmetic, not estimates.** Dollar projections are `principal × (1 + APY/100)^years` on the bank's own APY.
5. **Every row links to its source.** `tools/check_links.py` fails if any external link is not a registered official
   source, or if any internal link is broken.

## Headline findings (2026-10-21/22)

- Best verified APY: **3.65%** (Barclays Tiered Savings, $250,000–$1,000,000 tier) — **$9,125** on $250,000 for one year.
- Best flat rate with no conditions: **3.55%** (Synchrony) — **$8,875**.
- Big-branch savings published rates range from **0.01%** (Wells Fargo) to **0.06%** (PNC Platinum tier). The same
  $250,000 earns **$25–$150** a year there.
- **FDIC insurance is identical** at every bank listed. The difference is entirely rate and fee, not safety.
- Max coverage at one bank: **$250,000** single, **$500,000** joint (two owners), **$1,250,000** for a trust/POD with
  five or more beneficiaries (rule effective 2024-04-01).
- Verified bonuses: **$200** (Barclays, $25,000 for 120 days, expires 2026-10-31) and **up to $400** (SoFi, eligible
  direct deposit), plus a 1.10% six-month APY boost at SoFi.

## Rebuilding

```bash
python3 tools/build_projections.py    # recompute every dollar figure -> data/projections.json
python3 tools/build_verification.py   # regenerate the line-by-line log -> data/verification.json
python3 tools/build_site.py           # regenerate the HTML pages from data/
python3 tools/check_links.py          # provenance + internal-link check (exit 1 on failure)
```

Requires only Python 3 (standard library). No CDN, no tracking, no JavaScript needed to read any number.

## Data schema (short version)

`data/accounts.json` — one object per account: `apy_primary`, `apy_tiers[]`, `apy_as_of`, `apy_scope`,
`apy_status` (`verified` / `unverified`), `min_open`, `monthly_fee`, `fee_waiver`, `max_balance`,
`withdrawal_rules`, `app_status`, `security_note`, `fdic_statement`, `rules_note`, `sources[]`.

`data/banks_fdic.json` — FDIC institutions API snapshot: certificate, legal name, active flag, assets, deposits.
`data/projections.json` — every computed cell plus the formula and assumptions in `meta`.
`data/flagged.json` — 20 items: unverified, irregular, scoped and note.
`data/sources_fetched.json` — every URL used, how it was obtained, and what was taken from it.

## Not financial advice

Rates are variable and change without notice. Projections hold the APY constant only to make comparison possible.
Interest is taxable and reported on Form 1099-INT. Confirm every figure on the bank's own page before opening an
account, and use <https://edie.fdic.gov/> for your own coverage calculation.
