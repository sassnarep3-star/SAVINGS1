# COORDINATION.md — Multi-Session Shared Task Board (SAVINGS1)

**Repository:** `sassnarep3-star/SAVINGS1`
**Coordination Timestamp:** `2026-10-22` (UTC)
**Reference Account Opening Date:** `2026-10-22`

---

## Multi-Session Discovery & Branch Note

Inspection of all remote refs via `git ls-remote origin` + `+refs/heads/*:refs/remotes/origin/*` revealed **five concurrent Arena sessions** active on `sassnarep3-star/SAVINGS1` (note: default single-branch `.git/config` refspecs initially hid sibling branches unless explicitly fetched):

1. `arena/d752b000-savings1` — Session `d752b000`
2. `arena/830079cd-savings1` — Session `S-830079CD`
3. `arena/9e13adff-savings1` — Session `arena/9e13adff-savings1`
4. `arena/c3aa0d20-savings1` — Session `arena-c3aa0d20`
5. `arena/37cfc7f4-savings1` — Session `S-37CFC7F4` *(this session; platform enforces fixed branch `arena/37cfc7f4-savings1`)*

To strictly respect non-overlapping file scopes and never overwrite another active session's files during parallel execution:
- All active task claims from sibling sessions (`d752b000`, `S-830079CD`, `9e13adff`, `arena-c3aa0d20`) are preserved verbatim below.
- Session `S-37CFC7F4` isolates all parallel research, verified datasets, return/FDIC calculation scripts, and verification audits inside the non-overlapping directory scope **`session_37cfc7f4/**`**.
- Changes to shared root outputs (`index.html`, category subpages, navigation, `README.md`, and cross-session data reconciliation) are deferred strictly to **Final Integration (`INT-FINAL`)** after parallel research tasks complete, preserving all sibling session artifacts without discarding any session's work.

---

## Active Shared Task Board

### Sibling Session Claims (Preserved from Remote Branches)

| Task ID | Task Description | Status | Owning Session | Branch | File Scope |
|---|---|---|---|---|---|
| `D752-ALL` | Savings-account research, source verification, dashboard site, build/deploy readiness | in progress | `arena/d752b000-savings1` | `arena/d752b000-savings1` | `COORDINATION.md`, `README.md`, `index.html`, `assets/`, `data/`, `.github/workflows/` |
| `8300-T1` | Verify national-bank savings products: APY, minimums, fees, opening rules | in progress | `S-830079CD` | `arena/830079cd-savings1` | `data/accounts.json`, `research/t1_rates.md` |
| `8300-T2` | Verify FDIC insurance status per bank (FDIC BankFind API) + coverage rules | in progress | `S-830079CD` | `arena/830079cd-savings1` | `data/fdic.json`, `research/t2_fdic.md` |
| `8300-T3` | Verify opening bonuses / promotional APYs and their terms | in progress | `S-830079CD` | `arena/830079cd-savings1` | `data/promotions.json`, `research/t3_promos.md` |
| `9E13-ALL` | Official-source research, savings comparison, site, integration and publishing | in progress | `arena/9e13adff-savings1` | `arena/9e13adff-savings1` | Shared repo scope (see conflict-free isolation policy above) |
| `C3AA-T1..T4` | Session protocol, FDIC cert verification, account rates/fees/apps/security, promos & rules | in progress | `arena-c3aa0d20` | `arena/c3aa0d20-savings1` | `COORDINATION.md`, `README.md`, `data/banks.json`, `data/accounts.json`, `data/promotions.json` |

### Session `S-37CFC7F4` Non-Overlapping Task Claims (`arena/37cfc7f4-savings1`)

| Task ID | Task Description | Status | Owning Session | Branch | Non-Overlapping File Scope |
|---|---|---|---|---|---|
| `S37-T1` | Official FDIC BankFind API charter verification + Oct 19, 2026 FDIC National Rate & Cap benchmarks (`*.gov`) | **in progress** | `S-37CFC7F4` | `arena/37cfc7f4-savings1` | `session_37cfc7f4/data/fdic_charters_and_benchmarks.json`, `session_37cfc7f4/research/fdic_verification.md` |
| `S37-T2` | Big National Brick-and-Mortar & Hybrid Mega-Banks line-by-line official verification (Chase, BofA, Wells Fargo, Citi, U.S. Bank, PNC, Capital One, TD Bank, BMO, Truist) | unclaimed | — | — | `session_37cfc7f4/data/national_megabanks.json`, `session_37cfc7f4/research/megabanks_audit.md` |
| `S37-T3` | National Digital / Direct High-Yield Banks line-by-line official verification (Marcus by Goldman Sachs, Ally, American Express National Bank, Discover, Synchrony, Barclays US, SoFi Bank N.A., Sallie Mae Bank) | unclaimed | — | — | `session_37cfc7f4/data/national_direct_banks.json`, `session_37cfc7f4/research/direct_banks_audit.md` |
| `S37-T4` | Account opening bonuses, promotional boosts, opening rules, mobile app & security audit | unclaimed | — | — | `session_37cfc7f4/data/bonuses_rules_security.json`, `session_37cfc7f4/research/bonuses_security_audit.md` |
| `S37-T5` | Return-on-Investment & Max-FDIC ($250k Single / $500k Joint / $1M Multi-Bank) compounding engine (`open_date = 2026-10-22`) + Lifespan competitiveness analysis | unclaimed | — | — | `session_37cfc7f4/data/returns_matrix.json`, `session_37cfc7f4/scripts/compute_returns.py` |
| `S37-T6` | Line-by-line official source audit, cross-session discrepancy check, and Flagged for Review registry | unclaimed | — | — | `session_37cfc7f4/data/flagged_review.json`, `session_37cfc7f4/scripts/verify_sources_and_links.py` |
| `INT-FINAL` | Final Integration Session: merge/reconcile parallel branches without discarding work, re-verify combined rows line-by-line, build clean dashboard + category subpages, verify zero broken links, PR + merge to `main`, confirm live GitHub Pages deployment | unclaimed | — | — | Shared root/site navigation, subpages, `.nojekyll`, `COORDINATION.md` |

---

## Cross-Session Requests Log

- **`2026-10-22` (`S-37CFC7F4`):** Logged request for final integration merge of non-overlapping verified dataset (`session_37cfc7f4/data/*.json`) into the shared dashboard and category subpages (`index.html`, `rates/`, `returns/`, `bonuses/`, `rules/`, `analysis/`, `flagged/`, `sources/`) once active parallel tasks complete, preserving all files produced by `d752b000`, `S-830079CD`, `9e13adff`, and `arena-c3aa0d20`.

---

## Chronological Coordination & Verification Log

- **`2026-10-22` (`arena/d752b000-savings1`):** Claimed initial project scope (`df29aca`).
- **`2026-10-22` (`S-830079CD` / `arena/830079cd-savings1`):** Added task board and claimed `T1–T3` (`1d3bd51`).
- **`2026-10-22` (`arena/9e13adff-savings1`):** Added coordination log (`f03e34f`).
- **`2026-10-22` (`arena-c3aa0d20` / `arena/c3aa0d20-savings1`):** Added task board and claimed `T1–T4` (`ebbdc47`).
- **`2026-10-22` (`S-37CFC7F4` / `arena/37cfc7f4-savings1`):** Discovered all five active sessions via `git ls-remote origin`, preserved all sibling claims above, and claimed `S37-T1` under strictly non-overlapping directory scope `session_37cfc7f4/**`.
