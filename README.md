# SAVINGS1 — verified national savings-account comparison

A static dashboard that answers one question with primary sources only:

> Where do I put savings so that it earns the most, while every dollar stays inside FDIC insurance?

**Live site:** https://sassnarep3-star.github.io/SAVINGS1/

Snapshot: bank rates and fees read on **2026-10-21 / 2026-10-22**. Every projection assumes the account is opened on
**2026-10-22** and the published APY does not change.

This repository was built by two agent sessions in parallel and then reconciled:

| Session | Branch | What it contributed | Result |
|---|---|---|---|
| `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | This dashboard: 20-account dataset, projection engine, verification log, link checker | **The published site** (repo root) |
| `S-830079CD` | `arena/830079cd-savings1` | 17-product dataset in `data/`, a separate site in `docs/`, CI integrity checks | Preserved; `docs/` is kept as an archived snapshot |

The two datasets were merged by re-verifying every one of the other session's high-rate finds (Axos, E*TRADE,
Openbank, CIT, EverBank, Barclays, Synchrony, Marcus, Amex, Capital One, Ally, SoFi) against the banks' own pages.
The merged dataset holds **20 accounts, 19 FDIC charters, 41 official sources, 26 flagged items**.

## What is in here

| Path | What it is |
|---|---|
| `index.html` | Dashboard: best verified rates, the $250,000 comparison, decision shortcuts |
| `rates.html` | All 20 accounts: APY, as-of date, rate scope, minimums, fees, app, source |
| `returns.html` | Interest earned at $10k → $1M over 1, 3 and 5 years; maximum-FDIC placement table |
| `promotions.html` | Cash bonuses and promotional APYs with exact conditions and deadlines |
| `rules.html` | Opening requirements, funding windows, balance ceilings, withdrawal rules |
| `security.html` | FDIC certificate numbers, active status, assets, published security statements |
| `flagged.html` | Every unverified value and irregular finding, with the official page to check |
| `methodology.html` | Formula, snapshot dates, all sources, 120-row verification log, repo audit |
| `data/v2/` | **Our dataset** — the one this site is generated from (JSON) |
| `data/` | The other session's dataset and its FDIC/flags files; consumed by `scripts/` |
| `tools/` | Our build and verification scripts (stdlib Python only) |
| `scripts/`, `docs/` | The other session's builder, CI checks and archived 17-product site |
| `COORDINATION.md` | The shared task board, including the merge reconciliation record |

### Why there are two data directories

`data/` holds the earlier session's `accounts.json` (17 products), `promotions.json`, `fdic.json` and `flags.json`
in their schema; `scripts/build_site.py` and the CI workflow read them. Our dataset lives in `data/v2/` with a
different, larger schema (tier tables, per-field verification status, source lists per account). Both are committed
so neither session's work is thrown away. The published site is generated **only** from `data/v2/`.

`docs/` still holds the 17-product site that the other session's builder produces. Every page in it now carries a
banner saying it is an archived snapshot and linking to the reconciled dashboard, so the two never read as
competing answers to the same question.

## Verification rules this dataset follows

1. **Official sources only.** A value is used only if it was read on the bank's own domain or a `.gov` domain.
   Rate aggregators and news articles are rejected; other banks' comparison tables are rejected too.
2. **Blank beats guessed.** If an official page gates a value behind a ZIP code or renders it client-side, the cell
   stays empty and the item is listed on `flagged.html`. Seventeen fields ended that way.
3. **Dates are copied.** Each APY carries the as-of date printed on the page; when no date is printed the cell is
   blank and the row is flagged.
4. **Arithmetic, not estimates.** Dollar projections are `principal × (1 + APY/100)^years` on the bank's own APY.
   Introductory rates are blended over their stated six months, and the blend formula is printed on the page.
5. **Every row links to its source.** `tools/check_links.py` fails if any external link is not a registered official
   source, or if any internal link is broken.

## Headline findings (2026-10-21/22)

- Best standard APY, no conditions: **4.20%** (EverBank Performance Savings) — **$10,500** on $250,000 for one year.
- Best APY including a six-month promo: **5.00%** (Axos ONE, first six months, needs the Axos ONE checking bundle);
  blended year one **4.25% → $10,618** on $250,000.
- Highest verified tier APY at $250,000: **4.21%** (Axos below the $250,000 step-down), **4.00%** Openbank,
  **3.75%** E*TRADE / CIT.
- Big-branch savings published rates: **0.01%** (Wells Fargo), **0.03%** (PNC standard), **0.05%** (U.S. Bank
  standard), **3.50%** (U.S. Bank relationship tier, $25,000+ combined balances and a checking bundle). The same
  $250,000 earns **$25–$10,500** a year depending only on which bank and which tier.
- **FDIC insurance is identical** at every bank listed — $250,000 per depositor, per bank, per ownership category.
  The difference is entirely rate and rule, not safety.
- Max coverage at one bank: **$250,000** single, **$500,000** joint (two owners), **$1,250,000** for a revocable
  trust/POD with five or more beneficiaries (rule effective 2024-04-01).
- Verified bonuses: **up to $800** (E*TRADE SAVE800, fund by 2027-01-10), **$200** (Barclays, $25,000 for 120 days,
  expires 2026-10-31), **up to $400** (SoFi, eligible direct deposit), plus rate boosts at Axos, E*TRADE, Openbank,
  CIT and SoFi.
- **Discover Bank's certificate 5649 is inactive** in the FDIC register. Discover is excluded; the other session
  caught this first and it stays published on `flagged.html`.

## Rebuilding

```bash
python3 tools/build_projections.py    # recompute every dollar figure -> data/v2/projections.json
python3 tools/build_verification.py   # regenerate the line-by-line log -> data/v2/verification.json
python3 tools/build_site.py           # regenerate the HTML pages from data/v2/
python3 tools/check_links.py          # provenance + internal-link check (exit 1 on failure)
```

The other session's pipeline still works and is what CI runs:

```bash
python3 scripts/build_site.py         # data/*.json -> docs/*.html
python3 scripts/verify_data.py        # integrity checks on docs/
```

Requires only Python 3 (standard library). No CDN, no tracking, no JavaScript needed to read any number.

## Data schema (short version)

`data/v2/accounts.json` — one object per account: `apy_primary`, `apy_tiers[]`, `apy_display`, `apy_as_of`,
`apy_scope`, `apy_status` (`verified` / `unverified`), `min_open`, `monthly_fee`, `fee_waiver`, `max_balance`,
`withdrawal_rules`, `app_status`, `security_note`, `fdic_statement`, `rules_note`, `sources[]`.

`data/v2/banks_fdic.json` — FDIC institutions API snapshot: certificate, legal name, active flag, assets, deposits.
`data/v2/projections.json` — every computed cell plus the formula and assumptions in `meta`.
`data/v2/flagged.json` — 26 items: unverified, irregular, scoped and risk.
`data/v2/sources_fetched.json` — every URL used, how it was obtained, and what was taken from it.

## Known limitations

- APYs change daily; this is a point-in-time snapshot dated 2026-10-21/22.
- Four APYs (Chase, Bank of America, Citibank, TD Bank) are unverified: their official rate tables are ZIP-gated or
  render client-side. They are excluded from every calculation and listed on `flagged.html`.
- Three branch-bank rate sheets are pinned to the page's default location rather than New York: U.S. Bank at ZIP
  55402, PNC at ZIP 15222, Wells Fargo at CA 94105.
- Mobile-app security features (MFA, biometrics, device binding) were **not** verified bank by bank; the site states
  only what each bank publishes and marks the rest unverified.
- Axos's year-one blend depends on the tier boundary at $250,000; the formula and both possible results are published.
- This is research, not financial, tax, or legal advice.

## Coordination

`COORDINATION.md` is the shared task board: claims, the cross-session merge record, the conflict resolution, and the
PR/deploy status. Both sessions' claims are listed there; nothing was discarded from either side.
