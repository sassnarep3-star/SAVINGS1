# Coordination

| Task | Status | Owner/session | Files in scope |
|---|---|---|---|
| Official-source research, savings comparison, site integration and GitHub Pages publishing | in progress (site implemented; deployment pending) | `arena/9e13adff-savings1` | all repository files (no other claims present at start) |

## Work log
- 2026-10-22 — Read the repository before starting. It contained only `README.md`; no coordination board existed. Created this board and claimed the full task because no other work or claims were present. Working on the Arena-assigned branch `arena/9e13adff-savings1` (branch is fixed by the session environment).
- 2026-10-22 — Added a static, responsive GitHub Pages dashboard and category pages (`index.html`, `accounts.html`, `returns.html`, `opening.html`, `security.html`, `flagged.html`, `sources.html`), official-source register, navigation, mobile styling and a link/citation validator. Added a Pages Actions workflow and left the existing default-branch Pages configuration for the deployment integration step.
- Research snapshot and modeled opening date: 2026-10-22 (UTC/local date supplied by the session). Primary rate sources:
  - Wells Fargo rate table: https://www.wellsfargo.com/savings-cds/rates/ (3.25% APY; source states APY accurate 2026-10-07 and the $25,000 / new-customer conditions).
  - Capital One official account comparison: https://www.capitalone.com/bank/open-an-account/ (3.20% APY effective 2026-10-21); account terms https://www.capitalone.com/bank/disclosures/savings-accounts/online-performance-savings-account/.
  - Citi official savings promo and NY APY chart: https://banking.citi.com/cbol/OM/checking/tiered/featured-offers/default.htm?ProspectID=null (offer through 2026-10-22; chart says APYs accurate 2026-07-14).
  - Bank of America official New York–Tri-State rate sheet: https://media.bac-assets.com/DigitalDeposit_NY_NY_Tri_State_Area.pdf?cacheBuster=7051 (effective 2026-10-21).
  - Chase official ZIP-dependent rates: https://www.chase.com/personal/savings/savings-account/interest-rates.
  - FDIC coverage rules: https://www.fdic.gov/resources/deposit-insurance/faq and https://www.fdic.gov/resources/deposit-insurance/brochures/insured-deposits.
- Verification performed: retrieved/checked the bank rate, product, offer, opening, fee, mobile/security and FDIC pages linked in `sources.html`; all account data rows link to an official bank/FDIC domain. `python scripts/check_site.py` passes: all 7 HTML pages, internal links/fragments, and official-domain links in every table body row. `git diff --check` passes. Projection arithmetic uses APY × principal for one year and principal × ((1 + APY)^n − 1) for illustrative multi-year calculations, with constant APY explicitly disclosed.
- Irregularities published on `flagged.html`: Capital One main product rate renders “NaN” while its own rate comparison and account disclosure report 3.20%; Citi APY chart is dated July 14 despite an offer open through October 22 and no current standard APY confirmed; Chase NYC numeric APY stays blank because the official ZIP-required rate table did not render; Capital One / Discover deposits are grouped for FDIC determination under Capital One's transition notice; maximum-insurance starting principal is hypothetical under variable yield; security features are bank-published, not audited; offer search does not prove absence of targeted bonuses.
- No other session claims were found. Per the session environment, work is kept on the fixed `arena/9e13adff-savings1` branch; its initial claim commit was pushed immediately. Deployment and PR/merge recording remain to be completed before marking this task done.
