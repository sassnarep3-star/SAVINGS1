# COORDINATION.md — Shared Task Board

**Repository:** sassnarep3-star/SAVINGS1
**Account opening date used for all return calculations:** 2026-10-22
**Data verification date:** 2026-10-22 (official disclosures dated 2026-10-07 to 2026-10-22)

| Session | Arena branch | Role | Scope |
|---|---|---|---|
| `S-830079CD` | `arena/830079cd-savings1` | Primary dashboard, published at `/` | `data/*.json`, `scripts/**`, root `*.html`, `assets/**`, `.github/workflows/**` |
| `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | Independent 20-account cross-check, published at `/verified/` | `data/v2/**`, `tools/**`, `verified/**` |
| `S-37CFC7F4` | `arena/37cfc7f4-savings1` | Primary-source **resolution layer**, published at `/resolved/` | `session_37cfc7f4/**`, `resolved/**`, `archive/session-9e13adff/**`, `archive/session-d752b000/**`, one footer line in `scripts/build_site.py` |
| `arena/9e13adff-savings1` | `arena/9e13adff-savings1` | Alternate dashboard; PR #4 closed by its own session to avoid overwriting main | archived read-only at `archive/session-9e13adff/` |
| `arena/d752b000-savings1` | `arena/d752b000-savings1` | Alternate 11-product dashboard; PR #12 left open and conflicting | archived read-only at `archive/session-d752b000/` |

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
| 2026-10-22 | `S-830079CD` | PRs #1, #3, #5, #6, #7 merged; primary dashboard live at the repository root |
| 2026-10-22 | `arena-c3aa0d20` | Re-merged `main` after PR #7 (clean), opened PR #8, CI green, merged, Pages rebuilt |

## Cross-session requests

- `arena-c3aa0d20` → `S-830079CD`: **PNC Standard Savings** and **TD Bank Simple/Signature Savings** are fully verified in `data/v2/accounts.json` (rates, fees, minimums, certificate numbers). They are not rows in the primary dataset. If the primary dashboard wants them, the records are ready to copy; this session did not edit `data/accounts.json` because it is outside its file scope.
- `arena-c3aa0d20` → `S-830079CD`: the primary dashboard's Axos one-year figure (4.28%, $10,703) is presented as a single number. The cross-check publishes the tier-dependent formula (4.2473% at $250,000+, 4.60% below it) and flags the difference as F26. Both are defensible; the difference is the tier boundary.

## Pull request and deployment

| Item | Value |
|---|---|
| Session branch | `arena/830079cd-savings1` (integration) · `arena/c3aa0d20-savings1` (independent cross-check) |
| PR #1 | https://github.com/sassnarep3-star/SAVINGS1/pull/1 — merged 2026-10-22T00:10:33Z as `442a5e1` |
| PR #2 | https://github.com/sassnarep3-star/SAVINGS1/pull/2 — merged 2026-10-22T00:13:48Z (15-account dashboard) |
| PR #3 | https://github.com/sassnarep3-star/SAVINGS1/pull/3 — merged as `9f50b91` (primary site moved to repo root) |
| PR #5 | https://github.com/sassnarep3-star/SAVINGS1/pull/5 — merged as `6bc6e36` (PR/deploy record, account-count label) |
| PR #6 | https://github.com/sassnarep3-star/SAVINGS1/pull/6 — merged as `4d5f7d8` (U.S. Bank added to FDIC table) |
| PR #7 | https://github.com/sassnarep3-star/SAVINGS1/pull/7 — merged as `88e95e7` (per-bank app and security review) |
| PR #8 | https://github.com/sassnarep3-star/SAVINGS1/pull/8 — merged as `9edb4d3` (cross-check published at `/verified/`) |
| PR #9 | https://github.com/sassnarep3-star/SAVINGS1/pull/9 — merged as `4f65343` (unrendered template expression fixed, CI guard added) |
| PR #10 | https://github.com/sassnarep3-star/SAVINGS1/pull/10 — merged as `c29522c` (deploy record for the reconciliation) |
| Parallel session | `arena/c3aa0d20` board preserved; its 20-account build is published at `/verified/` and is not merged into the primary tables |
| GitHub Pages | `main` branch, root (`/`), HTTPS enforced |
| Live URL | https://sassnarep3-star.github.io/SAVINGS1/ · cross-check at /verified/ |
| Deploy status | Pages builds for `9edb4d3`, `c29522c`, `88e95e7` and `4f65343` completed with status `built`; both `/` and `/verified/` serve |

---

## Task board — session `S-37CFC7F4` (primary-source resolution layer)

**Claimed and pushed before implementation** (commit `1004e96`, then `a892377`). Scope deliberately
non-overlapping: this session wrote only into `session_37cfc7f4/**`, `resolved/**` and
`archive/session-*/**`, plus a single additive footer line in `scripts/build_site.py` so the new layer is
reachable from the main dashboard. No other session's data file, page or stylesheet was edited or deleted.

| ID | Task | Status | File scope | Result |
|----|------|--------|-----------|--------|
| S37-T1 | FDIC charter + benchmark ledger from `api.fdic.gov` and `fdic.gov` | **done** | `session_37cfc7f4/fdic_charters_and_sweeps.json` | 24 charters (23 active, Discover #5649 inactive), shared-certificate map, Oct-2026 FDIC/Treasury/Fed benchmarks |
| S37-T2 | Resolve the values the two live dashboards published as unverified | **done** | `session_37cfc7f4/data/resolved_accounts.json` | 4 items closed against primary sources (R01–R04) |
| S37-T3 | Add nationally-available accounts neither dataset carried | **done** | `session_37cfc7f4/data/resolved_accounts.json` | 6 accounts added, incl. the highest flat APY in the repository |
| S37-T4 | Multi-horizon returns (1/2/3/5 yr) + FDIC safe-harbour arithmetic | **done** | `session_37cfc7f4/build_resolved_site.py`, `resolved/returns.html` | 10 projectable accounts × 7 deposit sizes × 4 horizons |
| S37-T5 | Max-FDIC-coverage routes incl. the April-2024 trust ceiling | **done** | `resolved/coverage.html` | Ownership-category stack to $2,250,000 at one bank; shared-certificate traps |
| S37-T6 | Line-by-line audit, link check, cross-session reconciliation | **done** | `resolved/flagged.html`, `resolved/sources.html` | 8 new flags (2 high), 37 pages / 1,470 link refs / 0 broken, 151 external URLs all official |
| S37-T7 | Preserve the two unmerged sibling sessions' work | **done** | `archive/session-9e13adff/**`, `archive/session-d752b000/**` | Both branches merged for true ancestry; both web trees archived byte-for-byte |

### Values RESOLVED against a primary source (previously published as unverified)

| ID | Previously reported as | Resolved value | Primary source | Date printed on the document |
|----|----------------------|----------------|----------------|------------------------------|
| R01 | "Chase APY is ZIP-gated — blank" | **Chase Savings 0.01% APY**, all four balance tiers (New York) | `chase.com/content/dam/chase-ux/ratesheets/pdfs/rdny1.pdf` | RATES IN EFFECT AS OF: Friday, October 16, 2026 |
| R01 | "Bank of America renders `$XXXX` — blank" | **Advantage Savings 0.04% APY**, all nine balance tiers (New York – Tri-State) | `media.bac-assets.com/DigitalDeposit_NY_NY_Tri_State_Area.pdf` | Effective as of: October 21, 2026 |
| R01 | "Wells Fargo 0.01% is only the CA default market" | **Platinum Savings 3.25% APY** for new savings customers on $25,000+, all states excluding Colorado | `wellsfargo.com/fetch-pdf?documentName=Account+Addenda` | Platinum Savings Rate Update, Effective October 7, 2026 |
| R02 | "BofA fee and minimum unreadable" | **$8.00/mo monthly maintenance fee, $100.00 minimum to open**, waived 6 months for new accounts | `bankofamerica.com/salesservices/deposits/resources/personal-schedule-fees/` | Effective August 7, 2026 |
| R03 | "App unverified: Ally, Marcus, Barclays, Wells Fargo" | All four confirmed on the banks' own pages | ally.com · marcus.com · banking.us.barclays · wellsfargo.com | read 2026-10-22 |
| R04 | "Security unverified: Marcus, Wells Fargo" | Both publish security pages describing account controls | marcus.com/us/en/banking-with-us/security-center · wellsfargo.com/privacy-security/fraud/security-tools-and-options/ | read 2026-10-22 |

### Accounts ADDED (absent from both published datasets)

| Account | FDIC cert | APY | Date printed by the bank | Source |
|---|---|---|---|---|
| Select Savings from Barclays (AARP Digital Banking) | 57203 | **4.25%** flat on every tier | accurate as of 10/07/2026 | banking.us.barclays/select-home/savings.html |
| U.S. Bank Elite Money Market — new-client rate | 6548 | **4.00%** on $25,000+ within 30 days | read 2026-10-20/21 | usbank.com/bank-accounts/savings-accounts/elite-money-market.html |
| CIT Bank Savings Connect | 11063 | **3.65%** flat | accurate as of July 1, 2026 | cit.com/cit-bank/bank/savings |
| Barclays Online Savings | 57203 | **3.20%** flat | read 2026-10-22, no date printed | banking.us.barclays/online-savings.html |
| Alto by BMO Online Savings | 16571 | **3.00%** | APY as of October 21, 2026 | alto.bmo.com/en-us/ |
| Truist One Savings | 9846 | **0.01%** every tier | accurate as of 9/28/2026 | truist.com/savings/truist-one-savings/disclosures-and-fees |

### Irregularities flagged by this session (published on `/resolved/flagged.html`, none blocking)

| ID | Severity | Item |
|----|----------|------|
| S01 | **high** | Axos's own rate table contradicts its 5.00% headline — no tier on the page pays 5.00% (boosted tiers are 4.21% to $249,999.99 and 3.50% above). The primary dashboard's Axos ranking rests on the headline. |
| S02 | **high** | Citi's fact sheet states the promotional rate feature for new Citi Savings accounts is discontinued effective 2026-10-23 — one day after this project's reference opening date. |
| S03 | medium | Two official PNC URLs for the same page publish different High Yield Savings APYs (3.15% vs 3.30%); APY left blank rather than resolved to either. |
| S04 | medium | Alto deposits are not separately insured from other BMO accounts, and Alto names no mobile app and has no branch/ATM/BMO-digital access. |
| S05 | medium | Five brand pairs share one FDIC certificate (Openbank/Santander #29950, CIT/First-Citizens #11063, Alto/BMO #16571, three Barclays products #57203, Capital One/Discover #4297). |
| S06 | medium | Marcus caps balances at $1M/account and $3M/depositor; Barclays at $1M/account and 3 accounts; Amex at $5M and 20 accounts — bank limits that constrain a concentration strategy. |
| S07 | low | Wells Fargo's 3.25% excludes Colorado and is lost on any day the collected balance drops below $25,000. |
| S08 | low | The FDIC trust category insures up to $1,250,000 per owner per bank (rule effective 2024-04-01) — a ceiling absent from both published coverage tables. |

### Verification performed

- **Source rule:** every value read from the bank's own domain or a `.gov` domain during this session.
  Aggregators were used only to locate which official document to open; no aggregator figure appears in any table.
- **Government anchors:** FDIC *National Rates and Rate Caps – October 2026* (savings national rate 0.38%,
  savings rate cap 4.63%, Treasury yields 4.33% / 4.54% / 5.09%, revised 2026-10-19);
  FDIC *Deposit Insurance At A Glance* (the $250,000 limit, ownership categories, the April-2024 trust rule);
  FDIC BankFind institution API (index created 2026-10-16); Federal Reserve open market operations
  (target range 3.75%–4.00% as of 2026-09-17).
- **Automated gates run on the merged tree:** `python3 scripts/build_site.py` → 9 root pages regenerated,
  no stale diff; `python3 scripts/verify_data.py` → all integrity checks passed (18 accounts, 16 promotions,
  21 flags, 9 pages); placeholder grep → none; full-tree link audit → **37 HTML pages, 1,470 link references,
  0 broken internal links, 151 unique external URLs, all on an official bank or `.gov` domain**;
  local HTTP server → **HTTP 200 on all 37 pages and every asset**.
- **Nothing inferred:** Citibank's standard savings APY and PNC's High Yield Savings APY remain blank by
  decision, because resolving them would have required choosing between conflicting or unreadable official figures.

### Cross-session reconciliation — round 3 (by `S-37CFC7F4`)

Two sibling sessions never reached `main` and their work was at risk of being lost:

| Branch | State found | Action taken |
|---|---|---|
| `arena/9e13adff-savings1` | PR #4 **closed** by its own session to avoid overwriting the completed integration; 7-page dashboard + `scripts/check_site.py` stranded on the branch | Branch merged with `-s ours` so its commits are genuine ancestors of `main`; full web tree archived byte-for-byte at `archive/session-9e13adff/` |
| `arena/d752b000-savings1` | PR #12 **open and CONFLICTING**, 11-product dataset incl. Barclays AARP Select Savings and Citi NY promo research | Branch merged with `-s ours`; full web tree archived at `archive/session-d752b000/`. Its two strongest independent findings — Barclays AARP Select Savings and the BofA New York regional rate sheet — were **independently re-verified from the official sources by this session** before being promoted into `/resolved/` |

No file belonging to another session was edited, overwritten or deleted. The only shared file touched is
`scripts/build_site.py`, and only to append one footer paragraph linking to `/resolved/`; the root pages were
then regenerated by that same script so the CI staleness gate stays green.

### Cross-session requests from `S-37CFC7F4`

- **To the primary dashboard owner (`S-830079CD`):** flags F11 (Big Four APYs unverifiable), F15 (BofA fee/minimum
  unreadable), F13 (four apps unverified) and F21 (two security pages unverified) are now **resolvable** —
  the primary sources are listed in the R01–R04 table above and linked on `/resolved/resolved.html`.
  `data/accounts.json` was not edited because it is outside this session's scope.
- **To the primary dashboard owner:** flag **S01** materially affects the published Axos ranking. The 5.00%
  figure does not appear in Axos's own rate table. Recommend re-reading
  `axosbank.com/personal/bank/axos-one` before the Axos row is presented as the top result.
- **To both dashboard owners:** the FDIC trust category ($1,250,000 per owner per bank, effective 2024-04-01)
  belongs in the coverage tables; it is the single largest omission for a stated goal of maximising FDIC insurance.

### Pull request and deployment — session `S-37CFC7F4`

| Item | Value |
|---|---|
| Session branch | `arena/37cfc7f4-savings1` |
| Pull request | [#14 — Primary-source resolution layer](https://github.com/sassnarep3-star/SAVINGS1/pull/14) |
| CI gate before merge | `Verify data and site / verify` — **SUCCESS**, mergeStateStatus `CLEAN` |
| Merge result | **MERGED** 2026-10-22T00:57:23Z as `2853dc2` (no approval waited for, per the project brief) |
| GitHub Pages | `main` branch, root (`/`), legacy build, HTTPS enforced |
| Pages build | status **`built`** for commit `2853dc2`, created 2026-10-22T00:57:24Z, duration 16.7 s, no error |
| Live URL | https://sassnarep3-star.github.io/SAVINGS1/ |
| New pages live | `/resolved/` — index · resolved · accounts · returns · coverage · flagged · sources (7 pages) |
| Archives live | `/archive/session-9e13adff/` and `/archive/session-d752b000/` |
| Discoverability | Footer link to `/resolved/` confirmed present in the deployed root `index.html` |

**Flagged items do not block the merge.** All 8 new irregularities (S01–S08) are published on the clearly
labelled Flagged for Review page at `/resolved/flagged.html` with their official source links, alongside the
19 items on `/flagged.html` and the 26 on `/verified/flagged.html`, for review after the site went live.
