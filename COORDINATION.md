# COORDINATION — Savings Account Research Project (SAVINGS1)

Shared task board for all agent sessions working on this repository. Read it before starting any work.
Claim a task by writing your session ID + file scope below, commit and push **that claim only** immediately.

**Repository:** `sassnarep3-star/SAVINGS1`
**Account-opening date used for all return math:** 2026-10-22
**Data verification window:** 2026-10-21 / 2026-10-22 (UTC)

## Session protocol

- One session works one task; scopes must not overlap.
- Requested branch naming is `session-<id>/<task>`. **Deviation in this repo:** the Arena platform fixes the working
  branch name for each session, so a session cannot create an arbitrary branch name. The platform branch is recorded
  in each claim and is used in place of `session-<id>/<task>`. No other branch is created or pushed.
- Make small, frequent commits. Run `git pull --rebase` before every push.
- Merge conflict → stop, resolve without discarding the other session's work, and log it below.
- A claim older than 60 minutes with no commits may be taken over; note the handoff in the Log.
- Shared outputs (table data, site index/navigation) are changed only by the final integration session.
- Never mark anything verified without an official source link.

## Data / verification rules used in this repo

1. Every table row carries a source URL on the bank's own domain or a U.S. government domain (`*.gov`), fetched
   during the session that recorded it.
2. If a value cannot be read from an official page, the cell is left **blank** and the item is listed on
   `flagged.html` with status `unverified`. No value is inferred or copied from a third-party rate aggregator.
3. Projected dollar returns are arithmetic on the bank's own published APY, using the formula documented in
   `data/v2/projections.json` (`meta.formula`). They are labeled illustrative projections, not bank quotes.
4. As-of dates are the dates printed on the official page (or the fetch date when the page prints none; the cell
   then says so and the row is flagged).
5. `tools/check_links.py` is the merge gate for the published site; `scripts/verify_data.py` is the CI gate for the
   archived `docs/` snapshot. Both must pass before a merge.

## Active sessions

| Session | Branch | Status | Owns |
|---|---|---|---|
| `arena-c3aa0d20` (integration) | `arena/c3aa0d20-savings1` | **active** — finished the reconciliation | Root site, `data/v2/**`, `tools/**`, `README.md`, `COORDINATION.md` |
| `S-830079CD` | `arena/830079cd-savings1` | merged into `main` (PR #1) | `data/accounts.json`, `data/promotions.json`, `data/fdic.json`, `data/flags.json`, `scripts/**`, `docs/**`, `.github/workflows/**` |

## Task board — session `arena-c3aa0d20`

| ID | Task | Status | Session ID | Branch | File scope |
|----|------|--------|-----------|--------|-----------|
| T1 | Session protocol, repo audit, coordination board | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `COORDINATION.md`, `README.md` |
| T2 | Bank roster + FDIC certificate verification (FDIC BankFind API) | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `data/v2/banks_fdic.json` |
| T3 | Rate / fee / minimum / app / security verification per account | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `data/v2/accounts.json` |
| T4 | Promotions + account-opening rules | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `data/v2/promotions.json` |
| T5 | Return-on-deposit projection tables (opening date 2026-10-22) | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `data/v2/projections.json`, `tools/build_projections.py` |
| T6 | Site build: dashboard, category subpages, flagged page | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `site pages (root *.html)`, `assets/**`, `tools/build_site.py` |
| T7 | Line-by-line verification audit + link check | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `data/v2/verification.json`, `data/v2/flagged.json`, `tools/build_verification.py`, `tools/check_links.py` |
| T8 | Integration: merge `origin/main`, re-verify, publish, PR, Pages deploy | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `COORDINATION.md`, all shared outputs |
| T9 | Reconcile the two datasets (20 accounts) and keep both pipelines green | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `data/v2/**`, `data/**` (theirs untouched), `docs/**` (banner only) |

## Task board — session `S-830079CD`

| ID | Task | Status | Owner | File scope | Result |
|----|------|--------|-------|------------|--------|
| T1 | Verify national-bank savings products: APY, minimums, fees, opening rules | done | S-830079CD | `data/accounts.json`, `docs/accounts.html` | 17 products recorded; 12 APYs verified; 4 blank + flagged; 1 closed (Discover) |
| T2 | Verify FDIC insurance status per bank + coverage rules | done | S-830079CD | `data/fdic.json`, `docs/fdic.html` | 16 active certificates confirmed via `api.fdic.gov`; Discover cert 5649 inactive |
| T3 | Verify opening bonuses / promotional APYs and terms | done | S-830079CD | `data/promotions.json`, `docs/promotions.html` | 16 offers/absences recorded |
| T4 | Compute return tables by deposit size (FDIC-limit focus) | done | S-830079CD | `scripts/build_site.py`, `docs/returns.html` | 8 deposit tiers, 1-year + 5-year, blended APY |
| T5 | Build static site (dashboard + category subpages) | done | S-830079CD | `docs/**` | 9 pages, shared CSS, internal link check passes |
| T6 | Final integration: re-verify, link check, publish Pages, PR + merge | done | S-830079CD | `docs/**`, `README.md`, `.github/workflows/**` | Merged to `main` as PR #1 (`442a5e1`) |

## Claims log

| Time (UTC) | Session | Action |
|-----------|---------|--------|
| 2026-10-22 | `arena-c3aa0d20` | Created board. Claimed T1–T4 on `arena/c3aa0d20-savings1`. Committed `ebbdc47` and pushed. |
| 2026-10-22 | `arena-c3aa0d20` | T1–T4 done. Claimed T5–T7 (projections, site build, verification audit). |
| 2026-10-22 | `arena-c3aa0d20` | T5–T7 done. Claimed T8 (integration: re-verify, PR, merge, Pages deploy). Commit `8736995`, PR #2 opened. |
| 2026-10-22 | `arena-c3aa0d20` | `gh pr merge 2` failed: `main` had moved (PR #1 from session `S-830079CD`). Claimed T9, the cross-session reconciliation. |

## Cross-session reconciliation (T9)

`main` gained session `S-830079CD`'s dataset, site and CI while this session was building. `git merge origin/main`
produced four conflicts and one structural overlap. Nothing from either side was dropped.

**Conflicts and how each was resolved**

| File | Conflict | Resolution |
|---|---|---|
| `data/accounts.json` | add/add — 15 accounts (ours) vs 17 (theirs) | Theirs kept at the canonical path, because `scripts/build_site.py` and CI read it. Ours moved to `data/v2/accounts.json`, then extended with their five high-rate finds. |
| `data/promotions.json` | add/add — 15 vs 16 offers | Theirs kept at the canonical path; ours moved to `data/v2/promotions.json`, then extended with six new offers/absences. |
| `COORDINATION.md` | both sessions wrote a board | Both boards preserved above; this section records the reconciliation. |
| `README.md` | both sessions rewrote it | Rewritten once, documenting both datasets, both pipelines and the final result. |
| `data/{banks_fdic,flagged,projections,sources_fetched,verification}.json` | same path, different schema | Ours now live only in `data/v2/`; the toolchain points there (`DATA = data/v2` in all four `tools/*.py`). |

**Duplicate data removed on purpose:** our copies of `banks_fdic.json`, `flagged.json`, `projections.json`,
`sources_fetched.json` and `verification.json` were deleted from `data/` after being copied to `data/v2/`, because
two files with the same name and different schemas in one directory is how a future session gets silently wrong
numbers. Their `data/fdic.json` and `data/flags.json` are untouched.

**Site location decision:** the root pages are the published site (Pages is configured for `main:/`, `legacy` build,
HTTPS enforced). `docs/` keeps the other session's 9-page build and passes CI, but every page now carries a banner
identifying it as an archived snapshot and linking to the reconciled dashboard. `scripts/build_site.py` was changed
only to inject that banner; no data or markup from their pages was altered.

**Re-verification, not trust.** All five of their high-rate accounts were re-fetched and re-read in this session
before being added to `data/v2/accounts.json`:

| Account | Value re-read on the bank's page | Result |
|---|---|---|
| Axos ONE | 4.21% < $250k, 3.50% ≥ $250k, 1.00% if requirements missed, 5.00% first six months | added |
| E*TRADE Premium | 3.75% base as of 2026-10-21, 4.25% six months, $10M cap, SAVE800 up to $800 | added |
| Openbank HYS | 4.00% + 0.35% six months, $500 minimum, Santander cert 29950 | added |
| CIT Platinum | 3.75% / 0.25% as of 2026-07-01, BOOST50 → 4.25%, $100 minimum | added |
| EverBank Performance | 4.20% new accounts, $0 minimum, no fee, daily compounding | added |

FDIC charters for all five were re-confirmed through the BankFind API (Axos 35546, Morgan Stanley Private Bank 34221,
Santander 29950, First-Citizens 11063, EverBank 34775) and appended to `data/v2/banks_fdic.json`.

**One number changed after re-verification.** Their Axos year-one blend was 4.28% → $10,703 on $250,000. This
session computes sqrt((1.05)(1.035)) − 1 = **4.2473% → $10,618**, because $250,000 sits in Axos's $250,000+ tier,
which pays 3.50% after the intro. Their number is preserved in flagged item F26 with both formulas; the published
figure is the one whose formula is printed on the page.

## Sources used

Bank product/rate pages (all fetched, never quoted from an aggregator): chase.com (2), bankofamerica.com,
wellsfargo.com, citi.com, usbank.com (2), pnc.com (2), td.com (2), ally.com (2, incl. security centre), marcus.com (2),
americanexpress.com, capitalone.com (2), synchrony.com, banking.us.barclays (3), sofi.com, axosbank.com,
us.etrade.com, openbank.us, cit.com, everbank.com.

Government: fdic.gov national rates and rate caps (revised 2026-10-19), fdic.gov deposit-insurance pages (3),
FDIC "Your Insured Deposits" brochure page (trust rule), FDIC institutions API (`banks.data.fdic.gov`, 8 queries),
edie.fdic.gov, federalreserve.gov open-market operations (2026-09-17 +25 bp → 3.75–4.00%), congress.gov (S.2155
income from transaction accounts, used only in a footnote).

Rejected on purpose: NerdWallet, Forbes Advisor, Business Insider, GOBankingRates, US News, Fortune, and banks' own
competitor-comparison tables.

## Verification performed

- **120 field-level checks** across 20 accounts → 91 verified, 12 verified-as-none, 17 unverified
  (`data/v2/verification.json`, generated by `tools/build_verification.py`).
- **FDIC charters**: 19 active certificates confirmed by API (628, 3510, 3511, 7213, 6548, 6384, 18409, 57803, 33124,
  27471, 4297, 27314, 57203, 26881, 35546, 34221, 29950, 11063, 34775). Discover 5649 is inactive and excluded.
- **Link provenance**: `tools/check_links.py` → 563 link references, 0 problems (8 pages + 5 data files).
- **Arithmetic**: every dollar figure recomputed by `tools/build_projections.py`; 414 cells across 27 rows.
- **CI pipeline kept green**: `python3 scripts/build_site.py` + `python3 scripts/verify_data.py` → all integrity checks
  passed (17 accounts, 16 promotions, 19 flags, 9 pages).
- **Pages built**: 8 HTML pages, 1 stylesheet, 0 external assets, no JavaScript required to read a number.

## Irregularities logged (published on `flagged.html`)

F01 Chase APY ZIP-gated · F02 BoA rate/fee placeholders (rates endpoint HTTP 405) · F03 Citi APY is region/tier/promo
driven · F04 TD rate table renders empty · F05 Synchrony 3.55% vs 2.85% on the same page · F06 U.S. Bank rates pinned
to ZIP 55402 · F07 PNC rates pinned to ZIP 15222 · F08 Wells Fargo rate shown for CA 94105 · F09 Barclays tier table
dated 10/07/2026 · F10 Capital One product page renders "NaN APY" · F11 Amex app not stated · F12 Barclays native app
not stated · F13 Marcus referral terms not opened · F14 SoFi "$3M FDIC" is partner-bank coverage · F15 Capital One and
Discover count as one bank since 2025-05-18 · F16 Marcus/Barclays/PNC balance ceilings · F17 FDIC snapshot is
2026-10-16 · F18 four of twenty accounts unpriced · F19 repo contained only a one-line README and no LICENSE ·
F20 Pages uses a legacy build from the repo root · F21 Axos bundle requirement drops the rate to 1.00% ·
F22 Axos publishes no balance cap · F23 E*TRADE $10M cap applies to the whole balance · F24 four new accounts print no
rate effective date · F25 promotional windows expire · F26 the two sessions' Axos blends differ (both formulas shown).

## Pull request and deployment

| Item | Value |
|---|---|
| Session branch | `arena/c3aa0d20-savings1` |
| PR | #2 — `https://github.com/sassnarep3-star/SAVINGS1/pull/2` |
| Merge result | _recorded after merge_ |
| GitHub Pages | `main` branch, `/` (legacy build, HTTPS enforced) |
| Live URL | https://sassnarep3-star.github.io/SAVINGS1/ |
| Deploy status | _recorded after deploy_ |

## Log

- 2026-10-22: `main` at `e6a9e13` contained only a one-line `README.md`. No prior data, site or claims existed.
  GitHub Pages is already enabled on `main` (`build_type: legacy`, source `main:/`, HTTPS enforced), so the site
  publishes from the repo root after the integration merge.
- 2026-10-22: Session `arena-c3aa0d20` committed the 15-account dataset, the projection engine and the 8-page site,
  ran the link check (470 references, PASS), opened PR #2.
- 2026-10-22: **Merge conflict occurred** — `main` had advanced to `442a5e1` with PR #1 (`S-830079CD`).
  `gh pr merge 2` was rejected ("merge commit cannot be cleanly created"). Resolved as recorded above; both sessions'
  work is preserved and both pipelines pass.
