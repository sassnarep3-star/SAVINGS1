# SAVINGS1 — verified national savings-account comparison

Two source-linked dashboards, one repository, no third-party rate data:

> **For a deposit opened on 2026-10-22, which US national bank with a digital app and FDIC insurance pays the most — and how much of that return survives after the promotional rate ends?**

| Site | Where | Built by | Scope |
|---|---|---|---|
| **Primary dashboard** (published) | `/` → https://sassnarep3-star.github.io/SAVINGS1/ | session `S-830079CD` plus follow-up integration | 20 products, 9 pages, CI-checked on every push |
| **Independent cross-check** | `/verified/` → https://sassnarep3-star.github.io/SAVINGS1/verified/ | session `arena-c3aa0d20` | 20 accounts, 41 registered sources, 26 flagged items, tier-aware return maths |

Both dashboards read the banks' own pages and the FDIC; neither uses a rate aggregator. They exist together
because two agent sessions worked on this repository in parallel and the merge rules of the project say that
neither session's verified work may be discarded. Where the two disagree, both figures stay published and the
difference is explained on the flagged pages (see `verified/flagged.html`, item F26).

Snapshot: bank rates and fees read **2026-10-21 / 2026-10-22**. Every projection assumes the account is opened on
**2026-10-22** and the published APY does not change.

## Headline findings (agreed by both dashboards)

- **Best no-conditions rate: 4.20%** — EverBank Performance Savings, $0 to open, no monthly fee. **$10,500** of
  interest on $250,000 for one year.
- **Highest advertised rate: 5.00%** for six months (Axos ONE), conditional on an Axos ONE checking bundle with
  $1,500 in monthly direct deposits plus a $1,500 average daily balance (or $5,000 + $5,000). Miss the requirement
  and the savings rate is **1.00%**.
- **Primary-site follow-up (session `arena/d752b000-savings1`):** Barclays Select Savings for active AARP members
  lists 4.25% APY across tiers (2026-10-07) and a separate $400 bonus, with conflicting 10/31/2026 vs. 1/31/2027
  deadlines on Barclays and AARP pages. Citi's New York basic-tier promotion lists a 0.98% one-year blended APY
  only on qualifying $25,000–$999,999 balances, for new accounts opened by 2026-10-22. Wells Fargo Platinum Savings
  is added at 3.25% variable APY for qualifying new customers with at least $25,000 maintained daily; the distinct
  Way2Save row remains blank for New York.
- **Best one-year blend including a promo:** Axos ONE ≈ **4.25–4.28%** depending on the tier boundary — the two
  sessions computed $10,618 and $10,703 on $250,000; both formulas are published (F26).
- **Standard big-branch savings rates can be low.** Wells Fargo Way2Save showed 0.01% only for its default
  California market; PNC showed 0.03% for its default market; U.S. Bank showed 0.05% standard at ZIP 55402
  (relationship tiers up to 3.50% require an eligible product and $25,000+ combined balance). Separate offers
  include Wells Fargo Platinum Savings at 3.25% for qualifying new customers and Citi's expiring 0.98% blended
  New York promotion. These are not interchangeable with the base rates.
- **FDIC insurance is identical everywhere on these pages** — $250,000 per depositor, per bank, per ownership
  category; $500,000 joint; $1,250,000 through a trust/POD with five or more beneficiaries (rule effective
  2024-04-01). Splitting across ownership categories or banks — not choosing a famous brand — is what raises coverage.
  Coverage includes accrued interest: at an unchanged 4.25% APY, $250,000 principal would grow to about $260,625
  in one year, and even $240,000 would reach about $250,200. The FDIC page warns to leave headroom; Barclays Tiered
  and AARP Select Savings share the same Barclays Bank Delaware limit.
- **Verified bonuses/promotions:** up to $800 (E*TRADE SAVE800, fund by 2027-01-10), $200 (Barclays Tiered,
  $25,000 held 120 days, expires 2026-10-31), $400 (Barclays AARP Select Savings, $40,000 held 120 days; deadline
  conflict flagged), up to $400 (SoFi, eligible direct deposit), Citi's 3.75% short-term savings-rate offer, and
  Wells Fargo Platinum's conditional 3.25% variable APY. These are separate from the standard-rate comparisons.
- **Discover Bank certificate 5649 is inactive** in the FDIC register. Discover is excluded from both datasets.
- **Market context:** FDIC national savings average **0.38%** (2026-10-19); federal funds target **3.75–4.00%**
  (after the 2026-09-17 hike); 6-month Treasury **4.33%**, 12-month **4.54%**.

## Repository layout

| Path | What it is |
|---|---|
| `index.html`, `accounts.html`, `returns.html`, `promotions.html`, `fdic.html`, `analysis.html`, `sources.html`, `flagged.html`, `method.html` | **Primary site** (session `S-830079CD`), generated from `data/` by `scripts/build_site.py` |
| `verified/` | **Independent cross-check site** (session `arena-c3aa0d20`), generated from `data/v2/` by `tools/build_site.py` |
| `data/` | Primary dataset: `accounts.json` (20 products), `promotions.json`, `fdic.json`, `flags.json` |
| `data/v2/` | Cross-check dataset: `accounts.json` (20 accounts), `promotions.json`, `flagged.json`, `verification.json`, `projections.json`, `banks_fdic.json`, `sources_fetched.json` |
| `scripts/` | `build_site.py` (renders the primary site) and `verify_data.py` (integrity gate) |
| `tools/` | `build_projections.py`, `build_verification.py`, `build_site.py`, `check_links.py` (stdlib Python only) |
| `.github/workflows/verify.yml` | CI: rebuilds the primary site, fails if it is stale, runs the integrity checks, rejects placeholders |
| `COORDINATION.md` | Shared task board: both sessions' claims, the two merge reconciliations, PR and deploy records |

### Why there are two data directories and two sites

`data/` and `scripts/` are session `S-830079CD`'s schema; `data/v2/` and `tools/` are session `arena-c3aa0d20`'s.
The schemas differ (the cross-check records per-field verification status, tier tables and a source registry), so
they cannot share one file name without silently corrupting one of them. Both are committed and both builds are
reproducible. The root site is what GitHub Pages publishes; `/verified/` is published from the same branch and is
linked from every page's footer.

## Verification rules both datasets follow

1. **Official sources only.** A value is used only if it was read on the bank's own domain or a `.gov` domain.
   Rate aggregators, news articles and other banks' comparison tables are rejected.
2. **Blank beats guessed.** If a page gates a value behind a ZIP code or renders it client-side, the cell stays
   empty and the item is listed on the flagged page. Chase and Bank of America remain blank in both datasets.
   The primary site separately records Citi's expiring New York promotional blended APY and leaves the generic
   ongoing/other-market rate unprojected; the independent cross-check dataset remains unchanged.
3. **Dates are copied.** Each APY carries the as-of date printed on the page; when none is printed the cell is blank
   and the row is flagged.
4. **Arithmetic, not estimates.** Dollar figures are `principal × (1 + APY/100)^years` on the bank's own APY.
   Introductory rates are blended over their stated six months and the blend formula is printed on the page.
5. **Every row links to its source.** `scripts/verify_data.py` and `tools/check_links.py` both fail the build if a
   row loses its official link or an internal link breaks.

## Rebuilding

```bash
# primary site (session S-830079CD)
python3 scripts/build_site.py       # data/*.json  -> root *.html
python3 scripts/verify_data.py      # integrity gate

# independent cross-check (session arena-c3aa0d20)
python3 tools/build_projections.py  # data/v2/projections.json
python3 tools/build_verification.py # data/v2/verification.json
python3 tools/build_site.py         # data/v2/*.json -> verified/*.html
python3 tools/check_links.py        # provenance + internal links
```

Only Python 3 standard library. No CDN, no tracking, no JavaScript required to read any number.

## Known limitations

- APYs change daily; this is a point-in-time snapshot dated 2026-10-21/22.
- Chase and Bank of America New York APYs remain unverified in the primary site. Citi's 0.98% blended rate is
  promotional and limited to qualifying New York balances/accounts opened by 2026-10-22; the separate cross-check
  dataset remains unchanged and leaves Citi blank. TD Bank is still unverified in the cross-check.
- Location-pinned rate sheets remain flagged: U.S. Bank at ZIP 55402, PNC at ZIP 15222, and Wells Fargo Way2Save
  at CA 94105. Wells Fargo Platinum Savings is a separate new-customer offer with explicit $25,000 daily-balance
  conditions and a Colorado exclusion.
- The primary site now links bank-published app/security summaries for the active products; these summaries are
  not an independent technical security audit, score, or guarantee.
- The two sessions compute the Axos one-year blend from different tier assumptions (F26).
- This is research, not financial, tax, or legal advice.

## How the two sessions were reconciled

`COORDINATION.md` records both claims logs and both conflict resolutions. In short:

1. PR #1 added the `S-830079CD` dataset, site and CI. PR #2 added the `arena-c3aa0d20` dataset and site.
2. The second merge (this one) hit conflicts on `index.html`, `returns.html`, `promotions.html`, `flagged.html`,
   `assets/style.css`, `README.md`, `COORDINATION.md` and on my data files that had been archived under
   `archive/session-c3aa0d20/`.
3. Resolution: the primary site keeps the root (it is what Pages serves and what CI rebuilds); the cross-check site
   moved to `verified/` with its own stylesheet; the stale `archive/` copy was deleted because its numbers were out
   of date and duplicated a dataset that is now merged; every figure from both sides is either published or
   explicitly superseded in `COORDINATION.md`.
