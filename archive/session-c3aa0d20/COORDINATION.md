# COORDINATION — Savings Account Research Project (SAVINGS1)

Shared task board for all agent sessions working on this repository. Read it before starting any work.
Claim a task by writing your session ID + file scope below, commit and push **that claim only** immediately.

## Session protocol

- One session works one task; scopes must not overlap.
- Session branch naming requested: `session-<id>/<task>`. **Deviation in this repo:** the Arena platform fixes the
  working branch name for each session, so a session cannot create an arbitrary branch name. The platform branch is
  recorded in the claim below and is used in place of `session-<id>/<task>`. No other branch is created or pushed.
- Make small, frequent commits. Run `git pull --rebase` before every push.
- Merge conflict → stop, resolve without discarding the other session's work, and log it below.
- A claim older than 60 minutes with no commits may be taken over; note the handoff in the Log.
- Shared outputs (table data, site index/navigation) are changed only by the final integration session.
- Never mark anything verified without an official source link.

## Data / verification rules used in this repo

1. Every table row carries a source URL on the bank's own domain or a U.S. government domain (`*.gov`), fetched
   during this session.
2. If a value cannot be read from an official page, the cell is left **blank** and the item is listed on
   `flagged.html` with status `unverified`. No value is inferred or copied from a third-party rate aggregator.
3. Projected dollar returns are arithmetic on the bank's own published APY, using the formula documented in
   `data/projections.json` (`meta.formula`). They are labeled illustrative projections, not bank quotes.
4. As-of dates are the dates printed on the official page (or the fetch date when the page prints none; the cell
   then says so and the row is flagged).
5. `tools/check_links.py` is the merge gate: it fails if any external URL is not a registered official source in
   `data/sources_fetched.json`, if any internal link is broken, or if an account has no source.

## Task board

| ID | Task | Status | Session ID | Branch | File scope |
|----|------|--------|-----------|--------|-----------|
| T1 | Session protocol, repo audit, coordination board | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `COORDINATION.md`, `README.md` |
| T2 | Bank roster + FDIC certificate verification (FDIC BankFind API) | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `data/banks_fdic.json` |
| T3 | Rate / fee / minimum / app / security verification per account | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `data/accounts.json` |
| T4 | Promotions + account-opening rules | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `data/promotions.json` |
| T5 | Return-on-deposit projection tables (opening date 2026-10-22) | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `data/projections.json`, `tools/build_projections.py` |
| T6 | Site build: dashboard, category subpages, flagged page | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `site pages (root *.html)`, `assets/**`, `tools/build_site.py` |
| T7 | Line-by-line verification audit + link check | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `data/verification.json`, `data/flagged.json`, `tools/build_verification.py`, `tools/check_links.py` |
| T8 | Final integration: merge, re-verify, publish, PR, Pages deploy | done | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `COORDINATION.md` |

> Note on parallelism: only one agent session is attached to this repository, and the platform requires all work to
> land on this session's single branch. The same session therefore claimed T5–T8 after finishing T1–T4, updating this
> board before each stage. If a second session is ever attached, T5–T8 are the natural split points because their
> file scopes do not overlap with T2–T4.

## Claims log

| Time (UTC) | Session | Action |
|-----------|---------|--------|
| 2026-10-22 | `arena-c3aa0d20` | Created board. Claimed T1–T4 on `arena/c3aa0d20-savings1`. Committed `ebbdc47` and pushed. |
| 2026-10-22 | `arena-c3aa0d20` | T1–T4 done. Claimed T5–T7 (projections, site build, verification audit). |
| 2026-10-22 | `arena-c3aa0d20` | T5–T7 done. Claimed T8 (integration: re-verify, PR, merge, Pages deploy). |

## Sources used (all fetched in this session)

Bank product/rate pages: chase.com (2), bankofamerica.com, wellsfargo.com, citi.com, usbank.com (2), pnc.com (2),
td.com (2), ally.com (2, incl. security centre), marcus.com (2), americanexpress.com, capitalone.com (2 + security
program link), synchrony.com, banking.us.barclays (3), sofi.com.

Government: fdic.gov national rates and rate caps (Oct 2026, revised 2026-10-19), fdic.gov deposit-insurance pages
(3), FDIC "Your Insured Deposits" brochure page (trust rule), FDIC institutions API (5 queries), edie.fdic.gov.

Repository/platform: github.com repo, GitHub Pages API, repository API.

Full list with what was taken from each: `data/sources_fetched.json`. Rejected on purpose: NerdWallet, Forbes
Advisor, Business Insider, GOBankingRates, US News, Fortune, and banks' own competitor-comparison tables.

## Verification performed

- **90 field-level checks** across 15 accounts → 69 verified, 11 verified-as-none, 10 unverified
  (`data/verification.json`, generated by `tools/build_verification.py`).
- **FDIC charters**: 14 active certificates confirmed by API (628, 3510, 3511, 7213, 6548, 6384, 18409, 57803,
  33124, 27471, 4297, 27314, 57203, 26881); 3 closed legacy charters with matching names identified and excluded.
- **Link provenance**: `tools/check_links.py` → 470 link references, 0 problems.
- **Arithmetic**: every dollar figure recomputed by `tools/build_projections.py`; 252 cells across 18 rows.
- **Pages built**: 8 HTML pages, 1 stylesheet, 0 external assets, no JavaScript required to read a number.

## Irregularities logged (published on `flagged.html`)

F01 Chase APY ZIP-gated · F02 BoA rate/fee placeholders (rates endpoint HTTP 405) · F03 Citi APY is
region/tier/promo-driven · F04 TD rate table renders empty · F05 Synchrony 3.55% vs 2.85% on the same page ·
F06 U.S. Bank rates pinned to ZIP 55402 · F07 PNC rates pinned to ZIP 15222 · F08 Wells Fargo rate shown for CA 94105 ·
F09 Barclays tier table dated 10/07/2026 · F10 Capital One product page renders "NaN APY" · F11 Amex app not stated ·
F12 Barclays native app not stated · F13 Marcus referral terms not opened · F14 SoFi "$3M FDIC" is partner-bank
coverage · F15 Capital One and Discover count as one bank since 2025-05-18 · F16 Marcus/Barclays/PNC balance ceilings ·
F17 FDIC snapshot is 2026-10-16 · F18 four accounts unpriced · F19 repo contained only a one-line README and no
LICENSE · F20 Pages uses a legacy build from the repo root with no CI.

## Log

- 2026-10-22: `main` at `e6a9e13` contained only a one-line `README.md`. No prior data, site or claims existed —
  nothing to merge or reconcile. GitHub Pages is already enabled on `main` (`build_type: legacy`, source `main:/`,
  HTTPS enforced), so the site publishes from the repo root after the integration merge.
- 2026-10-22: No merge conflicts occurred (single session, single branch, linear history).
