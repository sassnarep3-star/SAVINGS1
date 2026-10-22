# National Savings Account Review

A static, source-linked dashboard comparing savings accounts from large national banks and national online banks. It summarizes official APYs, one-, three- and five-year illustrative return scenarios, account-opening rules, cash bonuses and rate promotions, app access, published security controls, fees, FDIC coverage, and unresolved verification items.

## Review snapshot

- **Research and scenario opening date:** October 22, 2026
- **One-year horizon:** October 22, 2026 through October 22, 2027
- **Additional hypothetical horizons:** three and five years, only for accounts with a current standard rate suitable for illustrative constant-rate modeling
- **Banks/products reviewed:** Marcus, Ally, Wells Fargo, Capital One, Chase, Bank of America, Citi, American Express National Bank, Barclays Tiered Savings, Barclays AARP Select Savings, and U.S. Bank Smartly Savings
- **Coverage reference:** FDIC standard limit of $250,000 per depositor, per insured bank, per account ownership category. Accounts in the same category at the same bank are aggregated, including accrued interest.
- **Primary research rule:** if a current and applicable value was not confirmed on an official source, the site leaves it blank and flags the issue. Capital One's APY is shown only provisionally due to an official-page inconsistency. Chase, Bank of America, and U.S. Bank APYs are blank where New York-specific rates were not confirmed.

## Site pages

- `index.html` — overview and shortlist
- `rates.html` — published APYs and one-, three- and five-year scenario estimates
- `accounts.html` — opening requirements, minimums, fees, app access, security, and FDIC source links
- `offers.html` — current official cash offers and promotional APY rules
- `coverage.html` — FDIC coverage and calculation methodology
- `flagged.html` — unresolved and irregular source findings

## Method and limits

The one-year return scenario uses opening principal × applicable current APY, rounded to the nearest dollar, assuming one lump-sum deposit on October 22, 2026, no additions or withdrawals, and an unchanged rate for one full year. The three- and five-year tables use compound growth at the current APY only where standard-rate modeling is supported. All are illustrations, not predictions or guarantees. Variable rates can change at any time. Fees, taxes, and cash bonuses are excluded. Promotional, location-unconfirmed, and officially conflicting rates are not extrapolated beyond one year. Wells Fargo's 3.25% new-customer rate is conditional on its balance and eligibility requirements. Citi's 0.98% New York blended APY is available only for qualifying $25,000+ New-to-Citibank funds and an account opened by October 22, 2026.

The AARP Select Savings rate from Barclays requires active AARP membership. Barclays Tiered Savings and the AARP product are both accounts at Barclays Bank Delaware and share FDIC limits for the same depositor and ownership category. The $235,000 comparison scenario leaves a buffer at current rates but cannot guarantee coverage if other deposits, rates, or balances change.

FDIC insurance is not a per-account limit. Existing deposits at the same bank and ownership category count toward the limit. Confirm coverage with the FDIC's official [deposit insurance FAQ](https://www.fdic.gov/resources/deposit-insurance/faq) and [EDIE estimator](https://edie.fdic.gov/).

The site reports official bank disclosures; it does not independently rate the banks' cybersecurity or guarantee any account's suitability. Offer terms and APYs can change. Re-check official linked disclosures on the date you apply.

## Local checks

No build dependencies are required. Run:

```sh
python3 scripts/check_site.py
```

The script checks local links, required account-source links, official source domains, JSON validity, and core data fields. GitHub Pages deployment is configured to verify pull requests and deploy on pushes to `main` or manual dispatch.
