# COORDINATION — Savings Account Research Project (SAVINGS1)

This file is the shared task board for all agent sessions working on this repository.
Read it before starting any work. Claim a task by writing your session ID + file scope
below, then commit and push **that claim only** immediately.

## Session protocol (as requested by the repo owner)

- One session works one task; scopes must not overlap.
- Session branch naming requested: `session-<id>/<task>`. **Deviation in this repo:** the
  Arena platform fixes the working branch name for each session, so a session cannot create
  an arbitrary branch name. The platform branch is recorded in the claim below and is used
  in place of `session-<id>/<task>`. Do not create or push any other branch.
- Make small, frequent commits. Run `git pull --rebase` before every push.
- If a merge conflict occurs: stop, resolve it without discarding the other session's work,
  and log what happened in the Log section below.
- A claim older than 60 minutes with no commits may be taken over by another session; note
  the handoff in the Log.
- Shared outputs (table data files, site index/navigation) are changed only by the final
  integration session.
- Never mark anything verified without an official source link.

## Data / verification rules used in this repo

1. Every table row must carry a source URL on the bank's own domain or a U.S. government
   domain (`*.gov`), fetched during this session.
2. If a value cannot be read from an official page, the cell is left **blank** and the row
   is listed on `flagged.html` with status `UNVERIFIED`. No value is inferred or copied
   from a third-party rate aggregator.
3. Projected dollar returns are arithmetic on the bank's own published APY, using the
   formula documented in `data/projections.json` (`meta.formula`). They are labeled
   "illustrative projection", not a bank quote.
4. "As-of" dates are the dates printed on the official page (or the fetch date if the page
   prints none; in that case the cell says so).

## Task board

| ID | Task | Status | Session ID | Branch | File scope |
|----|------|--------|-----------|--------|-----------|
| T1 | Session protocol, repo audit, coordination board | in progress | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `COORDINATION.md`, `README.md` |
| T2 | Bank roster + FDIC certificate verification (FDIC BankFind API) | in progress | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `data/banks.json` |
| T3 | Rate / fee / minimum / app / security verification per account | in progress | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `data/accounts.json` |
| T4 | Promotions + account-opening rules | in progress | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `data/promotions.json` |
| T5 | Return-on-deposit projection tables (opening date 2026-10-22) | unclaimed | — | — | `data/projections.json`, `tools/build_projections.py` |
| T6 | Site build: dashboard, category subpages, flagged page | unclaimed | — | — | `site/**` |
| T7 | Line-by-line verification audit + link check | unclaimed | — | — | `data/verification.json`, `tools/check_links.py` |
| T8 | Final integration: merge, re-verify, publish, PR, Pages deploy | unclaimed | — | — | `COORDINATION.md`, root site files |

> Note on parallelism: only one agent session is attached to this repository at the time of
> writing, so T1–T4 are claimed by it and T5–T8 remain open for a follow-on session. This
> session continued through T5–T8 in the same branch because the platform requires all work
> to land on its single branch; the claims below were updated before each stage started.

## Claims log

| Time (UTC) | Session | Action |
|-----------|---------|--------|
| 2026-10-22 | `arena-c3aa0d20` | Created board. Claimed T1–T4 on `arena/c3aa0d20-savings1`. |

## Log

- 2026-10-22: `main` contained only a one-line `README.md` at `e6a9e13`; no prior data, site,
  or claims existed. Nothing to merge or reconcile. GitHub Pages is already enabled on
  `main` (`build_type: legacy`, source `main:/`), so the site is published from the repo root
  on `main` after the integration merge.
