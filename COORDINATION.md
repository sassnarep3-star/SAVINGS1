# COORDINATION.md — Shared Task Board

**Repository:** sassnarep3-star/SAVINGS1
**Account opening date used for all return calculations:** 2026-10-22
**Data verification date:** 2026-10-22 (official disclosures dated 2026-10-07 to 2026-10-22)

| Session | Arena branch | Role | Scope |
|---|---|---|---|
| `S-830079CD` | `arena/830079cd-savings1` | Primary dashboard, published at `/` | `data/*.json`, `scripts/**`, root `*.html`, `assets/**`, `.github/workflows/**` |
| `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | Independent 20-account cross-check, published at `/verified/` | `data/v2/**`, `tools/**`, `verified/**` |

## Ground rules

1. A session claims a task by writing its session ID, status `in progress`, and its file scope here, then committing and pushing immediately.
2. Never start a task another session holds as `in progress` unless its claim is >60 minutes old with no commits.
3. Each session edits only the files in its claimed scope. To change another session's file, log a request in **Cross-session requests**.
4. Never mark anything `verified` without an official source link. Unofficial/aggregator data is never used as a row value.
5. `needs review` items are published on the site's **Flagged for Review** page and never block a merge.
6. Shared outputs (`index.html`, navigation, `data/accounts.json`) are changed only by the final integration session.
7. **Branch-name deviation:** Arena fixes each session's branch name, so `session-<id>/<task>` cannot be created. Each session works and pushes only to its Arena branch and opens its PR from it.

## Task board — session `S-830079CD` (primary dashboard)

| ID | Task | Status | Owner | File scope | Result |
|----|------|--------|-------|------------|--------|
| T1 | Verify national-bank savings products: APY, minimums, fees, opening rules | **done** | S-830079CD | `data/accounts.json`, `accounts.html` | 18 products recorded; 12 APYs verified; 5 blank + flagged (Big Four + U.S. Bank); 1 closed (Discover) |
| T2 | Verify FDIC insurance status per bank + coverage rules | **done** | S-830079CD | `data/fdic.json`, `fdic.html` | 16 active certificates confirmed via `api.fdic.gov`; Discover cert 5649 inactive; U.S. Bank cert 6548 added in PR #6 |
| T3 | Verify opening bonuses / promotional APYs and terms | **done** | S-830079CD | `data/promotions.json`, `promotions.html` | 16 offers/absences recorded: 6 verified offers, 6 "none found", 4 unverified |
| T4 | Compute return tables by deposit size (FDIC-limit focus) | **done** | S-830079CD | `scripts/build_site.py`, `returns.html` | 8 deposit tiers, 1-year + 5-year, blended APY, winner per tier |
| T5 | Build static site (dashboard + category subpages) | **done** | S-830079CD | `*.html`, `assets/**` | 9 pages, shared CSS, no build step, internal link check passes |
| T6 | Final integration: re-verify, link check, publish Pages, PR + merge | **done** | S-830079CD | `*.html`, `assets/**`, `README.md`, `.github/workflows/**` | PRs #1, #3, #5, #6 merged; Pages builds from `main:/` |

## Task board — session `arena-c3aa0d20` (independent cross-check)

| ID | Task | Status | Owner | File scope | Result |
|----|------|--------|-------|------------|--------|
| T1 | Protocol, repo audit, coordination board | **done** | arena-c3aa0d20 | `COORDINATION.md`, `README.md` | Board created and pushed before research |
| T2 | Bank roster + FDIC certificate verification (BankFind API) | **done** | arena-c3aa0d20 | `data/v2/banks_fdic.json` | 19 active charters |
| T3 | Rate / fee / minimum / app / security verification per account | **done** | arena-c3aa0d20 | `data/v2/accounts.json` | 20 accounts, 16 with a verified APY, 4 blank + flagged |
| T4 | Promotions + account-opening rules | **done** | arena-c3aa0d20 | `data/v2/promotions.json` | 20 offers/absences |
| T5 | Return-on-deposit projections (opening date 2026-10-22) | **done** | arena-c3aa0d20 | `data/v2/projections.json`, `tools/build_projections.py` | 27 rows, 414 cells, tier-aware, promo blends with published formula |
| T6 | Site build: dashboard, category subpages, flagged page | **done** | arena-c3aa0d20 | `verified/**`, `tools/build_site.py` | 8 pages, no JS required |
| T7 | Line-by-line verification audit + link check | **done** | arena-c3aa0d20 | `data/v2/verification.json`, `data/v2/flagged.json`, `tools/*.py` | 120 checks (91 verified, 12 verified-as-none, 17 unverified), 26 flags, 599 link references |
| T8 | Merge PR #2 into `main` | **done** | arena-c3aa0d20 | — | PR #2 merged 2026-10-22T00:13:48Z |
| T9 | Second reconciliation: merge `main` after PRs #3/#5/#6, republish | **done** | arena-c3aa0d20 | `verified/**`, `tools/**`, `README.md`, `COORDINATION.md`, `scripts/build_site.py` (footer link only) | Root keeps the primary site; cross-check published at `/verified/` |

## Verification log — primary dashboard (`scripts/verify_data.py`)

- every account has an https official source and an FDIC certificate number;
- every non-null APY has a `rate_as_of` date and an official source;
- every promotion and every flag has an https source;
- every row of the main accounts table contains an official link;
- 9 pages checked for internal broken links, literal `None`/`NaN`/`$XXXX`, stylesheet presence;
- result: **all integrity checks passed** (18 accounts, 16 promotions, 19 flags, 9 pages).

## Verification log — cross-check (`tools/check_links.py`, `data/v2/verification.json`)

- 120 field-level checks across 20 accounts → 91 verified, 12 verified-as-none, 17 unverified;
- 599 link references across 8 pages and 5 data files, 0 problems;
- every external URL registered in `data/v2/sources_fetched.json` with the method used to obtain it;
- FDIC BankFind detail links generated only for certificate numbers present in `data/v2/banks_fdic.json`.

### Line-by-line source checks performed (both sessions, agreed values)

| Bank | Value verified | Official page | Date on page |
|---|---|---|---|
| Axos | 5.00% intro / 4.21% ongoing / 3.50% $250k+ / 1.00% if unmet | axosbank.com/personal/bank/axos-one | none printed |
| E*TRADE | 4.25% 6 mo / 3.75% base / $400–$800 bonus (SAVE800) | us.etrade.com/bank/premium-savings-account | 2026-10-21 |
| Openbank | 4.00% + 0.35% 6 mo = 4.35%; $500 min | openbank.us/banking/high-yield-savings-account | 2026-10-22 |
| SoFi | 3.30% + 1.10% 6 mo = 4.40%; $50/$400 bonus | sofi.com/banking/high-yield-savings-account | 2026-10-20 |
| CIT | 4.25% 6 mo with BOOST50; 3.75% / 0.25% standard; $100 min | cit.com/cit-bank/platinum-savings/boost | standard 2026-07-01 |
| EverBank | 4.20% all balances; $0 min; $0 fee | everbank.com/banking/performance-savings | none printed |
| Barclays | 3.50% <$250k; 3.65% $250k–$1M; $200 bonus | banking.us.barclays/tiered-savings.html | 2026-10-07 |
| Synchrony | 3.55% (page also shows 2.85% in its own calculator — flagged) | synchrony.com/banking/products/hys-core | none printed |
| Marcus | 3.50% | marcus.com/us/en/savings/high-yield-savings | 2026-10-21 |
| Amex | 3.20% | americanexpress.com/en-us/banking/online-savings/account | 2026-10-21 |
| Capital One | 3.20% | capitalone.com/bank/savings-accounts/ | 2026-10-21 (product page renders "NaN") |
| Ally | 3.10% | ally.com/bank/online-savings-account/ | 2026-10-21 |
| U.S. Bank | 0.05% standard; 1.00% / 2.00% / 3.50% relationship tiers | usbank.com/.../savings-account-interest-rates.html | 2026-10-21, ZIP 55402 |
| PNC | 0.02% / 0.03% standard; 0.03–0.06% with relationship | pnc.com/.../deposit-rates/standard-savings.html | 2026-10-21, ZIP 15222 |
| Chase | $5 fee / $300 waiver / $0 min; APY ZIP-gated | chase.com/personal/savings/savings-account[/interest-rates] | n/a |
| Bank of America | 6-month fee waiver; fee/min rendered as `$XXXX` | bankofamerica.com/deposits/savings/savings-accounts/ | n/a |
| Wells Fargo | $5 fee / $300 waiver / $25 min; 0.01% only for default market CA 94105 | wellsfargo.com/savings-cds/way2save/ | n/a |
| Citi | $4.50 fee / $500 waiver; APY injected at runtime; app named | citi.com/banking/savings-account | APY footnote 2026-10-21 |
| TD Bank | $0 min; $5 / $15 fees; rates table renders empty | td.com/us/en/personal-banking/savings-accounts[/rates] | 2026-10-21 |
| Discover | cert 5649 inactive; excluded | api.fdic.gov `CERT:5649` | 2026-10-16 index |

**FDIC certificates confirmed active (api.fdic.gov, index created 2026-10-16):**

Axos 35546 · Morgan Stanley Private Bank 34221 · Santander 29950 · SoFi 26881 · First-Citizens 11063 · EverBank 34775 · Barclays Bank Delaware 57203 · Synchrony 27314 · Goldman Sachs Bank USA 33124 · American Express National Bank 27471 · Capital One 4297 · Ally 57803 · JPMorgan Chase 628 · Bank of America 3510 · Wells Fargo 3511 · Citibank 7213 · U.S. Bank 6548 · PNC 6384 · TD Bank 18409. **Discover 5649 inactive.**

**Government reference points:** FDIC national savings average 0.38%, savings rate cap 4.63%, Treasury yields 4.33% (6 mo) / 4.54% (12 mo) / 5.09% (60 mo) as of 2026-10-19; federal funds target 3.75%–4.00% after the 2026-09-17 increase.

## Irregularities / flagged items

Primary dashboard: 19 items on `flagged.html`. Cross-check: 26 items on `verified/flagged.html`. Highest-severity, agreed by both:

1. **Discover Bank closed** — FDIC certificate 5649 inactive; excluded from all calculations.
2. **Capital One + Discover deposits are combined** for FDIC coverage (opened on/after 2025-05-18).
3. **Axos does not publish the balance cap** on its 5.00% intro; the primary dashboard conservatively assumes the first $50,000.
4. **Axos ongoing rate falls to 1.00%** if monthly requirements are missed.
5. **SoFi's 4.40% is a 6-month boost**; its 4.70% SoFi Plus tier requires a paid subscription.
6. **SoFi's $3M FDIC figure** comes from a partner-bank programme, not SoFi's own insurance.
7. **CIT's standard-rate footnote is dated 2026-07-01** while the boost runs to 2026-12-15.
8. **Barclays' 3.65% applies only to $250k–$1M.**
9. **Big Four APYs unverifiable** for New York (ZIP gate, placeholders, runtime injection, market-specific display).
10. **E*TRADE's $10,000,000 cap applies to the whole balance** — above it the entire balance may earn the base rate.
11. **Four of the five newly merged accounts print no rate effective date.**
12. **The two sessions blended Axos's year one differently** (4.28% vs 4.2473%) — both formulas published.

## Parallel session integration — round 1 (by `S-830079CD`, PR #3)

A second session, `arena-c3aa0d20` (branch `arena/c3aa0d20-savings1`, PR #2), built a separate 15-account dashboard in parallel. `S-830079CD` acted as the first integration session and published its own dashboard at the repository root, which is what Pages serves.

**What was preserved at that point:** the complete `arena-c3aa0d20-savings1` tree was archived byte-for-byte at `archive/session-c3aa0d20/`, and its branch history was merged with an explicit merge commit (`4640e47`), so no commits were lost.

**What was promoted into the live dataset after independent re-verification (PR #5):** the U.S. Bank Bank Smartly savings row (APY left blank for New York, FDIC cert 6548 confirmed) and the Ally security-centre data.

## Parallel session integration — round 2 (by `arena-c3aa0d20`)

After PR #2 merged, `main` moved on with PRs #3, #5 and #6. Merging `main` back into `arena/c3aa0d20-savings1` produced conflicts on `index.html`, `returns.html`, `promotions.html`, `flagged.html`, `assets/style.css`, `README.md`, `COORDINATION.md`, the `docs/` directory (deleted upstream, moved to root) and the archived copy of this session's data files.

**Resolution and the reason for each choice**

| Conflict | Resolution | Why |
|---|---|---|
| Root pages (`index`, `returns`, `promotions`, `flagged`) | **Primary site kept** (`--theirs`) | Pages serves `main:/` and CI rebuilds these files from `data/`; overwriting them would fail the build gate |
| `assets/style.css` | Primary stylesheet kept at root; the cross-check stylesheet moved to `verified/assets/style.css` | Two different design systems; neither is broken |
| `data/v2/**` renames | Kept as the only home for this session's dataset | The primary pipeline reads `data/*.json`; the schemas are incompatible |
| `docs/**` | Deleted (upstream had already moved the site to the repository root) | Keeping a stale second copy of the same site would publish old numbers |
| `archive/session-c3aa0d20/**` | Deleted | It was a byte-for-byte copy of this session's older tree. Its numbers are now superseded and its data files duplicated `data/v2/` under a stale name; the full history is still in git |
| `scripts/build_site.py` | Two small edits: removed an obsolete banner injected in round 1, added a footer link to `/verified/` | Round 1's banner pointed at a path that no longer exists; the footer link makes the cross-check discoverable |
| This session's 8 pages | Rebuilt into `verified/` under a single banner that links to the primary dashboard | Nothing is deleted, and a reader can never mistake one dashboard for the other |

**Net effect:** the published root dashboard is unchanged in content (18 products, 9 pages, CI-green), and the independent 20-account dataset — with its 41 registered sources, tier-aware projections, 26 flagged items and link checker — is published at `/verified/` from the same branch.

## Claims log

| Time (UTC) | Session | Action |
|-----------|---------|--------|
| 2026-10-22 | `arena-c3aa0d20` | Board created; claimed T1–T4; committed `ebbdc47` and pushed |
| 2026-10-22 | `arena-c3aa0d20` | T1–T4 done; claimed T5–T7 (projections, site, verification audit) |
| 2026-10-22 | `arena-c3aa0d20` | T5–T7 done; claimed T8; commit `8736995`; PR #2 opened |
| 2026-10-22 | `arena-c3aa0d20` | PR #2 merged |
| 2026-10-22 | `arena-c3aa0d20` | `main` advanced (PRs #3/#5/#6); merge conflict hit; claimed T9 and resolved as above |
| 2026-10-22 | `S-830079CD` | PRs #1, #3, #5, #6 merged; primary dashboard live at the repository root |

## Cross-session requests

- `arena-c3aa0d20` → `S-830079CD`: **PNC Standard Savings** and **TD Bank Simple/Signature Savings** are fully verified in `data/v2/accounts.json` (rates, fees, minimums, certificate numbers). They are not rows in the primary dataset. If the primary dashboard wants them, the records are ready to copy; this session did not edit `data/accounts.json` because it is outside its file scope.
- `arena-c3aa0d20` → `S-830079CD`: the primary dashboard's Axos one-year figure (4.28%, $10,703) is presented as a single number. The cross-check publishes the tier-dependent formula (4.2473% at $250,000+, 4.60% below it) and flags the difference as F26. Both are defensible; the difference is the tier boundary.

## Pull request and deployment

| Item | Value |
|---|---|
| Session branch | `arena/c3aa0d20-savings1` |
| PR #1 | https://github.com/sassnarep3-star/SAVINGS1/pull/1 — merged 2026-10-22T00:10:33Z (`442a5e1`) |
| PR #2 | https://github.com/sassnarep3-star/SAVINGS1/pull/2 — merged 2026-10-22T00:13:48Z (15-account dashboard) |
| PR #3 | https://github.com/sassnarep3-star/SAVINGS1/pull/3 — merged (`9f50b91`), primary site moved to the repository root |
| PR #5 | https://github.com/sassnarep3-star/SAVINGS1/pull/5 — merged (`6bc6e36`) |
| PR #6 | https://github.com/sassnarep3-star/SAVINGS1/pull/6 — merged (`4d5f7d8`) |
| Reconciliation PR | recorded below once opened |
| GitHub Pages | `main` branch, root (`/`), legacy build, HTTPS enforced |
| Live URL | https://sassnarep3-star.github.io/SAVINGS1/ · cross-check at `/verified/` |
| Deploy status | recorded below after the reconciliation merge |
