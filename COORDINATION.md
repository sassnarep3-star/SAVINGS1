# COORDINATION.md — Shared Task Board

**Repository:** sassnarep3-star/SAVINGS1
**Branch used by this session:** `arena/830079cd-savings1` (Arena-assigned; this session must not create or switch branches)
**Session ID:** `S-830079CD`
**Session started:** 2026-10-22 (UTC)
**Data verification date:** 2026-10-22 (rates reflect official disclosures dated 2026-10-16 to 2026-10-22)
**Account opening date used for all return calculations:** 2026-10-22

## Ground rules

1. A session claims a task by writing its session ID, status `in progress`, and its file scope here, then committing and pushing immediately.
2. Never start a task another session holds as `in progress` unless its claim is >60 minutes old with no commits.
3. Each session edits only the files in its claimed scope. To change another session's file, log a request in **Cross-session requests**.
4. Never mark anything `verified` without an official source link. Unofficial/aggregator data is never used as a row value.
5. `needs review` items are published on the site's **Flagged for Review** page and never block a merge.
6. Shared outputs (`docs/index.html`, navigation, `data/accounts.json`) are changed only by the final integration session.

## Session status

**Active sessions:** 1 (`S-830079CD`). No other session claimed work in this repository during the session window. `S-830079CD` therefore holds the research tasks and the integration task and performed them sequentially. No cross-session conflicts occurred; no rebases were required after the initial commit.

## Task board

| ID | Task | Status | Owner | File scope | Result |
|----|------|--------|-------|------------|--------|
| T1 | Verify national-bank savings products: APY, minimums, fees, opening rules | **done** | S-830079CD | `data/accounts.json`, `accounts.html` | 17 products recorded; 12 APYs verified; 4 blank + flagged (Big Four); 1 closed (Discover) |
| T2 | Verify FDIC insurance status per bank + coverage rules | **done** | S-830079CD | `data/fdic.json`, `fdic.html` | 16 active certificates confirmed via `api.fdic.gov`; Discover cert 5649 inactive |
| T3 | Verify opening bonuses / promotional APYs and terms | **done** | S-830079CD | `data/promotions.json`, `promotions.html` | 16 offers/absences recorded: 6 verified offers, 6 "none found", 4 unverified |
| T4 | Compute return tables by deposit size (FDIC-limit focus) | **done** | S-830079CD | `scripts/build_site.py`, `returns.html` | 8 deposit tiers, 1-year + 5-year, blended APY, winner per tier |
| T5 | Build static site (dashboard + category subpages) | **done** | S-830079CD | `*.html`, `assets/**` | 9 pages, shared CSS, no build step, internal link check passes |
| T6 | Final integration: re-verify, link check, publish Pages, PR + merge | **in progress** | S-830079CD | `*.html`, `assets/**`, `README.md`, `.github/workflows/**` | PR and deploy result recorded below when complete |

## Verification log

**Automated checks** — `python3 scripts/verify_data.py` (run on every build):

- every account has an https official source and an FDIC certificate number;
- every non-null APY has a `rate_as_of` date and an official source;
- every promotion and every flag has an https source;
- every row of the main accounts table contains an official link;
- 9 pages checked for internal broken links, literal `None`/`NaN`/`$XXXX`, stylesheet presence;
- result: **all integrity checks passed** (17 accounts, 16 promotions, 19 flags, 9 pages).

**Line-by-line source checks performed**

| Bank | Value verified | Official page | Date on page |
|---|---|---|---|
| Axos | 5.00% intro / 4.21% ongoing / 3.50% $250k+ / 1.00% if unmet | axosbank.com/personal/bank/axos-one | none printed |
| E*TRADE | 4.25% 6 mo / 3.75% base / $400–$800 bonus | us.etrade.com/bank/premium-savings-account, /promo/savings | 2026-10-21 |
| Openbank | 4.00% + 0.35% 6 mo = 4.35%; $500 min | openbank.us/banking/high-yield-savings-account | today (2026-10-22) |
| SoFi | 3.30% + 1.10% 6 mo = 4.40%; $50/$400 bonus; rate sheet 4.70% Plus tier | sofi.com/banking/high-yield-savings-account, /legal/banking-rate-sheet | 2026-10-20 |
| CIT | 4.25% 6 mo with BOOST50; 3.75% / 0.25% standard; $100 min | cit.com/cit-bank/platinum-savings/boost | standard 2026-07-01 |
| EverBank | 4.20% all balances; $0 min; $0 fee | everbank.com/rates, /banking/performance-savings | 2026-10-16 |
| Barclays | 3.50% <$250k; 3.65% $250k–$1M; $200 bonus | banking.us.barclays/tiered-savings.html | 2026-10-07 |
| Synchrony | 3.55% | synchrony.com/banking/products/hys-core | none printed |
| Marcus | 3.50% | marcus.com/us/en/savings/high-yield-savings | 2026-10-21 |
| Amex | 3.20% | americanexpress.com/en-us/banking/online-savings/high-yield-savings-account | 2026-10-21 |
| Capital One | 3.20% | capitalone.com/bank/open-an-account | 2026-10-22 (captured) |
| Ally | 3.10% | ally.com/bank/view-rates | 2026-10-21 |
| Chase | $5 fee / $300 waiver / $0 min; APY ZIP-gated | chase.com/personal/savings/savings-account[/interest-rates] | n/a |
| Bank of America | 6-month fee waiver; fee/min rendered as $XXXX | bankofamerica.com/deposits/savings/savings-accounts | n/a |
| Wells Fargo | $5 fee / $300 waiver / $25 min; 0.01% only for default ZIP 94105 | wellsfargo.com/savings-cds/way2save | n/a |
| Citi | $4.50 fee / $500 waiver; APY dynamic placeholder; app named | citi.com/banking/savings-account | APY footnote 2026-10-21 |
| Discover | cert 5649 inactive; page 404 | api.fdic.gov `CERT:5649` | 2026-10-16 index |

**FDIC certificates confirmed active (api.fdic.gov, index `institutions_20261016090006`, created 2026-10-16):**

Axos 35546 · Morgan Stanley Private Bank 34221 · Santander 29950 · SoFi 26881 · First-Citizens 11063 · EverBank 34775 · Barclays Bank Delaware 57203 · Synchrony 27314 · Goldman Sachs Bank USA 33124 · American Express National Bank 27471 · Capital One 4297 · Ally 57803 · JPMorgan Chase 628 · Bank of America 3510 · Wells Fargo 3511 · Citibank 7213. **Discover 5649 inactive.**

**Government reference points:** FDIC national savings average 0.38% and Treasury yields 4.33% (6 mo) / 4.54% (12 mo) as of 2026-10-19; federal funds target 3.75%–4.00% after the 2026-09-17 increase.

## Irregularities / flagged items

19 items, published on `flagged.html` with source links. Highest-severity:

1. **Discover Bank closed** — FDIC certificate 5649 inactive; excluded from all calculations.
2. **Capital One + Discover deposits are combined** for FDIC coverage (opened on/after 2025-05-18).
3. **Axos does not publish the balance cap** on its 5.00% intro; model conservatively assumes the first $50,000.
4. **Axos ongoing rate falls to 1.00%** if monthly requirements are missed.
5. **SoFi's 4.40% is a 6-month boost**; its 4.70% SoFi Plus tier requires a paid subscription.
6. **SoFi's $3M FDIC figure** comes from a partner-bank programme, not SoFi's own insurance.
7. **E*TRADE advertises $500,000 FDIC coverage** without disclosing the conditions.
8. **CIT's standard-rate footnote is dated 2026-07-01** while the boost runs to 2026-12-15.
9. **Santander + Webster** combination announced on Openbank's home page.
10. **Barclays' 3.65% applies only to $250k–$1M.**
11. **Big Four APYs unverifiable** for New York (ZIP gate, placeholders, runtime injection, market-specific display).
12. **Citi Accelerate Savings is not offered in New York** per Citi's state list.

Lower-severity items (Synchrony's undated APY, four unverified mobile apps, banks disagreeing with the FDIC on the national average, BofA's unreadable fee, three expiring promotions, absence-of-bonus caveat, variable-rate caveat) are on the same page.

## Cross-session requests

_None._

## Pull request and deployment

| Item | Value |
|---|---|
| Session branch | `arena/830079cd-savings1` |
| PR | _recorded after creation_ |
| Merge result | _recorded after merge_ |
| GitHub Pages | main branch, root (`/`) |
| Live URL | https://sassnarep3-star.github.io/SAVINGS1/ |
| Deploy status | _recorded after deploy_ |
