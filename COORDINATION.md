# Coordination

| Task | Status | Owner/session | Files in scope |
|---|---|---|---|
| Official-source savings research and dashboard implementation | done on this branch; duplicate PR closed to preserve completed main integration | `arena/9e13adff-savings1` | this branch's new static dashboard and support files; not merged to main |
| Official rate refinements for the published main dashboard | needs review by integration owner; request logged on PR #3 | `arena/9e13adff-savings1` | no main-owned files edited |

## Work log
- 2026-10-22 — Read the repository before starting. It contained only `README.md`; no coordination board existed on the branch's starting commit. Created this board and claimed the task. Working on Arena-assigned branch `arena/9e13adff-savings1` (fixed by the session environment).
- 2026-10-22 — Implemented a responsive static dashboard with account comparison, returns, opening rules/offers, security/FDIC, source register and Flagged for Review page; added official-source/link validation. Local checks passed (`python scripts/check_site.py`, `git diff --check`). Initial claim and implementation commits were pushed to this branch.
- During the work, `main` advanced with another active session's final integration. Re-read the current main `COORDINATION.md` and found the full task (18 products, dataset, FDIC and promotions) already integrated. PR #1, #2 and #3 were merged; the session branch's Pages deployment passed. Confirmed the live Pages site at https://sassnarep3-star.github.io/SAVINGS1/ renders the integrated dashboard. The Pages deployment checks are successful.
- To prevent overwriting the more complete shared dataset/navigation/site, did not merge this session's duplicate dashboard PR #4. Closed PR #4 after its scope was found to overlap the already completed integration. This branch's alternate implementation remains here for traceability only.
- Per the shared-file ownership rule, did not edit the integrated main files or main-owned coordination board. Logged an official-source cross-session refinement request as a comment on merged PR #3: https://github.com/sassnarep3-star/SAVINGS1/pull/3#issuecomment-6329483418.

## Independent official-source findings shared for integration review
These rate and offer sources were fetched/reviewed on 2026-10-22. Values are not market-wide rankings; variable APYs may change.

| Bank | Official source | Finding / date | Review caveat |
|---|---|---|---|
| Wells Fargo Platinum Savings | https://www.wellsfargo.com/savings-cds/rates/ | 3.25% APY, source says accurate 2026-10-07; new savings customers, $25,000 qualifying balance within 30 days | Variable; eligibility and continued balance conditions apply |
| Capital One 360 Performance Savings | https://www.capitalone.com/bank/open-an-account/ | 3.20% APY effective 2026-10-21 | Main product page renders “NaN”; account comparison and disclosure state 3.20% |
| Bank of America Advantage Savings (NY–Tri-State) | https://media.bac-assets.com/DigitalDeposit_NY_NY_Tri_State_Area.pdf?cacheBuster=7051 | 0.04% APY; effective 2026-10-21 | New York regional sheet; variable rate |
| Citi Q3 savings offer | https://banking.citi.com/cbol/OM/checking/tiered/featured-offers/default.htm?ProspectID=null | 3.75% promotional interest rate for up to 3 months; New York APY chart 0.98%–1.05% | APY chart dated 2026-07-14; offer terms through 2026-10-22; not 3.75% APY |
| Chase Savings | https://www.chase.com/personal/savings/savings-account/interest-rates | Official page says rate depends on ZIP and may vary by market | Numeric rate did not render in the official response; left blank |

## Verification / irregularities
- `scripts/check_site.py` confirms 7 HTML pages, local links/fragments and recognized official-domain links in all table body rows for this branch's alternate site.
- Current main integration has its own more comprehensive source data and verifier; this branch is not part of the live Pages deployment.
- Independent findings to consider on main: Capital One's NaN display versus explicit 3.20% sources; current Wells qualifying APY; BofA's current NY regional rate sheet; Citi's stale APY chart and offer end date. These were published in the cross-session PR comment for the integration owner to review. No shared main data was changed from this branch.
- Also logged an FDIC-headroom refinement on merged PR #5: the published $250,000 starting-deposit return scenarios accrue interest beyond the coverage ceiling; suggested explicitly showing the variable-rate, assumption-bound maximum starting principal (for Axos's 4.28% one-year model, $239,739.16) while preserving the existing caveat. Comment: https://github.com/sassnarep3-star/SAVINGS1/pull/5#issuecomment-6329504142.
- Main deployment observed as successful after PR #3; live URL above. The live site contains the original integration's categories, full 18-account data and flagged review items.
