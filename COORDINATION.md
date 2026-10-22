# COORDINATION.md — Shared Task Board

**Repository:** sassnarep3-star/SAVINGS1
**Branch used by this session:** `arena/830079cd-savings1` (Arena-assigned; this session must not create or switch branches)
**Session ID:** `S-830079CD`
**Session started:** 2026-10-22 (UTC)
**Data verification date (all rates/terms):** 2026-10-22, reflecting official bank disclosures dated 2026-10-20 / 2026-10-21
**Account opening date used for all return calculations:** 2026-10-22

## Ground rules for this board

1. A session claims a task by writing its session ID, status `in progress`, and its file scope here, then committing and pushing immediately.
2. Never start a task another session holds as `in progress` unless its claim is >60 minutes old with no commits.
3. Each session edits only the files in its claimed scope. To change another session's file, log a request in the **Cross-session requests** section.
4. Never mark anything `verified` without an official source link. Unofficial/aggregator data is never used as a row value.
5. `needs review` items are published on the site's **Flagged for Review** page and never block a merge.
6. Shared outputs (`site/index.html`, navigation, `data/accounts.json`) are changed only by the final integration session.

## Current status

**Active sessions:** 1 (`S-830079CD`). No other session has claimed work in this repo as of the timestamp above.
Because only one session is active, `S-830079CD` holds both the research tasks and the final integration task, and performs them sequentially in the order below.

## Task board

| ID | Task | Status | Owner | File scope | Notes |
|----|------|--------|-------|------------|-------|
| T1 | Verify national-bank savings products: APY, minimums, fees, opening rules | in progress | S-830079CD | `data/accounts.json`, `research/t1_rates.md` | Official bank product pages only |
| T2 | Verify FDIC insurance status per bank (FDIC BankFind API) + coverage rules | in progress | S-830079CD | `data/fdic.json`, `research/t2_fdic.md` | api.fdic.gov + fdic.gov |
| T3 | Verify opening bonuses / promotional APYs and their terms | in progress | S-830079CD | `data/promotions.json`, `research/t3_promos.md` | Official promo terms only |
| T4 | Compute return tables by deposit size (FDIC-limit focus) | unclaimed | — | `scripts/build_site.py` | Depends on T1–T3 |
| T5 | Build static site (dashboard + category subpages) | unclaimed | — | `site/**` | Depends on T4 |
| T6 | Final integration: re-verify combined data, link check, publish GitHub Pages, PR + merge | unclaimed | — | `site/**`, `README.md`, `.github/workflows/**` | Depends on T5 |

## Cross-session requests

_None._

## Verification log

_Entries appended as tasks complete._

## Irregularities / flagged items

_Entries appended as tasks complete; published on `site/flagged.html`._
