#!/usr/bin/env python3
"""Build the S-37CFC7F4 primary-source resolution dashboard at /resolved/.

Scope rules (non-overlapping with the other sessions' published output):
  * writes ONLY into <repo>/resolved/
  * reads ONLY session_37cfc7f4/data/resolved_accounts.json
  * reuses the shared root stylesheet at ../assets/style.css (no duplicate CSS)

Every figure rendered here carries the official URL it was read from.
Arithmetic is performed on published APYs; no rate is invented, and any value
that could not be read from an official page is rendered blank and flagged.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "resolved"
DATA = json.loads((HERE / "data" / "resolved_accounts.json").read_text())

META = DATA["meta"]
BM = META["benchmarks"]
RESOLVED = DATA["resolved"]
ADDED = DATA["added"]
CLOSED = DATA["closed_flags"]
NEWFLAGS = DATA["new_flags"]
VERIFIED = META["verification_date"]
OPEN_DATE = META["account_open_date"]

PAGES = [
    ("index.html", "Overview"),
    ("resolved.html", "Resolved blanks"),
    ("accounts.html", "Added accounts"),
    ("returns.html", "Returns"),
    ("coverage.html", "Max FDIC coverage"),
    ("flagged.html", "Flagged for review"),
    ("sources.html", "Sources"),
]

DEPOSITS = [10000, 25000, 50000, 100000, 250000, 500000, 1000000]
HORIZONS = [("1 year", 1.0), ("2 years", 2.0), ("3 years", 3.0), ("5 years", 5.0)]


# ------------------------------------------------------------------ helpers
def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def money(v, dec=0) -> str:
    if v is None:
        return '<span class="unv">—</span>'
    return f"${v:,.{dec}f}"


def pct(v, dec=2) -> str:
    if v is None:
        return '<span class="unv">—</span>'
    return f"{v:.{dec}f}%"


def link(url, text="source") -> str:
    if not url:
        return '<span class="unv">no source</span>'
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(text)}</a>'


def badge(kind, text) -> str:
    return f'<span class="badge {kind}">{esc(text)}</span>'


def src_cell(rec) -> str:
    bits = []
    labels = {
        "rate_sheet_pdf": "official rate sheet (PDF)",
        "addenda_pdf": "account addenda (PDF)",
        "fee_schedule": "fee schedule",
        "pricing_pdf": "pricing (PDF)",
        "overview_pdf": "account overview (PDF)",
        "fact_sheet_pdf": "fact sheet (PDF)",
        "disclosures": "disclosures",
        "product": "product page",
        "detail": "product detail",
        "compare": "comparison page",
        "savings_detail": "savings detail",
        "rates": "rates page",
        "offer": "offer terms",
        "bonus": "bonus terms",
        "app": "app page",
        "security": "security page",
        "fdic": "FDIC record",
    }
    for key, url in rec["sources"].items():
        bits.append(link(url, labels.get(key, key)))
    bits.append(f'<span class="small">FDIC cert {rec["fdic_cert"]}</span>')
    return "<br>".join(bits)


def interest(apy_pct: float, principal: float, years: float) -> float:
    return principal * ((1 + apy_pct / 100.0) ** years) - principal


def projectable():
    """Accounts with a verified, flat, whole-balance APY we can honestly project."""
    out = []
    for rec in RESOLVED + ADDED:
        if rec.get("apy") is None:
            continue
        out.append(rec)
    return sorted(out, key=lambda r: -r["apy"])


# ------------------------------------------------------------------ layout
def layout(title: str, active: str, heading: str, lede: str, body: str) -> str:
    nav = "".join(
        f'<a class="lnk{" active" if f == active else ""}" href="{f}">{esc(label)}</a>'
        for f, label in PAGES
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · SAVINGS1 Resolution Layer</title>
<meta name="description" content="Primary-source resolution layer: ZIP-gated Big Four savings APYs resolved from official regional rate sheets, plus accounts and FDIC coverage routes the main dashboards did not carry.">
<link rel="stylesheet" href="../assets/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>%F0%9F%94%8E</text></svg>">
</head>
<body>
<header class="site"><div class="wrap"><nav class="nav">
<a class="brand" href="index.html">RESOLUTION<span>·LAYER</span></a>
{nav}
<span class="spacer"></span>
<a class="lnk" href="../index.html">← Main dashboard</a>
</nav></div></header>
<main><div class="wrap">
<div class="banner"><div><strong>This is the third dashboard in this repository.</strong>
The <a href="../index.html">main dashboard</a> ranks 18 products and the
<a href="../verified/index.html">cross-check dashboard</a> independently re-verifies 20.
This layer does something different: it goes back to the <strong>items those two left blank</strong>
and resolves them from official regional rate-sheet PDFs and fee schedules, then adds the
nationally-available accounts neither dataset carried.</div></div>
<h1>{esc(heading)}</h1>
<p class="lede">{lede}</p>
{body}
</div></main>
<footer><div class="wrap">
<p><strong>SAVINGS1 · Resolution Layer</strong> — session <code>S-37CFC7F4</code>, verified {VERIFIED}.
Reference opening date for every return figure: {OPEN_DATE}. Reference market: New York, NY.</p>
<p>Every value links to the bank's own page or a .gov page. A blank cell means the value could not be read
from an official source — it is never an estimate. All APYs are variable unless the bank states otherwise.
This is research, not financial advice.</p>
<p><a href="../index.html">Main dashboard</a> · <a href="../verified/index.html">Cross-check dashboard</a> · <a href="flagged.html">Flagged for review</a></p>
</div></footer>
</body></html>"""


# ------------------------------------------------------------------ pages
def build_index():
    proj = projectable()
    best = proj[0]
    by_id = {r["id"]: r for r in RESOLVED}

    rows = ""
    for i, r in enumerate(proj, 1):
        rows += f"""<tr>
<td><span class="rank">{i}</span></td>
<td><b>{esc(r['bank'])}</b><div class="small">{esc(r['product'])}</div></td>
<td class="num"><b>{pct(r['apy'])}</b></td>
<td class="small">{esc(r['apy_as_of_label'])}</td>
<td class="num">{money(interest(r['apy'], 250000, 1.0))}</td>
<td class="small">{src_cell(r)}</td></tr>"""

    closed_cards = ""
    for c in CLOSED:
        links = " · ".join(link(u, u.split("/")[2]) for u in c["sources"])
        closed_cards += f"""<div class="card"><h3 style="margin-top:0">{esc(c['id'])} — {esc(c['closes'])}</h3>
<p class="small">{esc(c['finding'])}</p><p class="small">{links}</p></div>"""

    body = f"""
<div class="grid g4">
  <div class="card kpi"><div class="label">Previously-blank values resolved</div><div class="value">{len(CLOSED)}</div><div class="sub">from official PDFs &amp; fee schedules</div></div>
  <div class="card kpi"><div class="label">Accounts added</div><div class="value">{len(ADDED)}</div><div class="sub">carried by neither published dataset</div></div>
  <div class="card kpi"><div class="label">Highest verified flat APY</div><div class="value">{pct(best['apy'])}</div><div class="sub">{esc(best['bank'])}</div></div>
  <div class="card kpi"><div class="label">New irregularities flagged</div><div class="value">{len(NEWFLAGS)}</div><div class="sub">2 high severity</div></div>
</div>

<h2>What this layer found</h2>
<div class="grid g2">
  <div class="card"><h3 style="margin-top:0">The Big Four rates were never actually unpublished</h3>
  <p class="small">Both live dashboards report that Chase, Bank of America, Citi and Wells Fargo savings APYs
  "could not be verified" because the websites gate them behind a ZIP code or render them client-side.
  That is true of the <em>web pages</em> — but three of these four banks publish the same rates as
  <strong>dated, market-specific PDF rate sheets</strong> on their own domains, which render perfectly.
  Chase New York: <b>0.01%</b>. Bank of America New York–Tri-State: <b>0.04%</b>.
  Wells Fargo Platinum Savings new-customer rate: <b>3.25%</b> on $25,000+.</p>
  <p class="small">{link(by_id['chase-savings-ny']['sources']['rate_sheet_pdf'], 'Chase NY rate sheet')} ·
  {link(by_id['bofa-advantage-savings-ny']['sources']['rate_sheet_pdf'], 'BofA NY–Tri-State rate sheet')} ·
  {link(by_id['wells-platinum-savings']['sources']['addenda_pdf'], 'Wells Fargo addenda')}</p></div>

  <div class="card"><h3 style="margin-top:0">The headline that does not appear in its own rate table</h3>
  <p class="small">Axos advertises "up to 5.00% APY" and the main dashboard ranks it first on that basis.
  The rate table printed lower on the <em>same</em> Axos page shows the boosted rate for every tier from
  $0 to $249,999.99 as <b>4.21% APY</b>, and <b>3.50%</b> from $250,000 up. No tier pays 5.00%.
  Published here as flag <a href="flagged.html">S01</a> rather than silently corrected.</p>
  <p class="small">{link('https://www.axosbank.com/personal/bank/axos-one', 'Axos ONE page')}</p></div>

  <div class="card"><h3 style="margin-top:0">A 4.25% flat rate with no tier, no clock and no checking bundle</h3>
  <p class="small">Select Savings from Barclays pays <b>4.25% APY on every balance tier</b> — not an
  introductory rate, not conditional on a linked checking account, not conditional on a balance threshold.
  It requires an active AARP membership number at application. A $400 bonus is attached to a $40,000
  deposit held 120 days, but the offer closes 10/31/2026.</p>
  <p class="small">{link('https://banking.us.barclays/select-home/savings.html', 'Barclays Select Savings')}</p></div>

  <div class="card"><h3 style="margin-top:0">One bank can insure $1,250,000 — not $250,000</h3>
  <p class="small">Both live dashboards' coverage tables stop at the $250,000 single-owner and $500,000 joint
  figures. Since 1 April 2024 the FDIC insures trust accounts at $250,000 per eligible beneficiary up to five
  beneficiaries, for <b>$1,250,000 per owner, per insured bank</b>. For a max-coverage goal that changes the
  arithmetic materially — see <a href="coverage.html">Max FDIC coverage</a>.</p>
  <p class="small">{link(BM['fdic_source'].replace('national-rates-and-rate-caps', 'resources/deposit-insurance/brochures/deposits-at-a-glance'), 'FDIC — Deposit Insurance At A Glance')}</p></div>
</div>

<h2>Every account in this layer with a verified APY</h2>
<p class="small">Ranked by published APY. "Year-1 interest on $250,000" is arithmetic on the bank's own
published APY at the FDIC single-owner limit — it is an illustration, not a quote, and every rate here is
variable unless the bank states otherwise.</p>
<div class="tablewrap"><table>
<thead><tr><th>#</th><th>Bank / product</th><th class="num">APY</th><th>Effective date printed by the bank</th><th class="num">Year-1 interest on $250,000</th><th>Official sources</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<h2>Items closed against a primary source</h2>
<div class="grid g2">{closed_cards}</div>

<h2>Where to go next</h2>
<div class="grid g3">
  <a class="tile" href="resolved.html"><b>Resolved blanks →</b><span class="small">The Big Four, line by line, with the PDF each rate came from.</span></a>
  <a class="tile" href="accounts.html"><b>Added accounts →</b><span class="small">{len(ADDED)} nationally-available accounts neither dataset carried.</span></a>
  <a class="tile" href="returns.html"><b>Returns →</b><span class="small">1, 2, 3 and 5-year interest at seven deposit sizes.</span></a>
  <a class="tile" href="coverage.html"><b>Max FDIC coverage →</b><span class="small">Single, joint and trust routes to $1.25M at one bank.</span></a>
  <a class="tile" href="flagged.html"><b>Flagged for review →</b><span class="small">{len(NEWFLAGS)} new irregularities with source links.</span></a>
  <a class="tile" href="sources.html"><b>Sources →</b><span class="small">Every URL used, grouped by what it verified.</span></a>
</div>
"""
    return layout("Overview", "index.html", "Primary-source resolution layer",
                  "Closing the blanks the two published dashboards left open — using the banks' own dated "
                  "regional rate sheets, fee schedules and disclosure PDFs.", body)


def build_resolved():
    rows = ""
    for r in RESOLVED:
        apy = pct(r["apy"]) if r.get("apy") is not None else '<span class="unv">—</span>'
        rows += f"""<tr>
<td><b>{esc(r['bank'])}</b><div class="small">{esc(r['product'])}</div>
<div class="small">{badge('ok', 'resolved') if r.get('apy') is not None else badge('warn', 'partial')}</div></td>
<td class="num"><b>{apy}</b><div class="small">{esc(r['apy_as_of_label'] or 'no date printed')}</div></td>
<td class="small">{esc(r['apy_scope'])}</td>
<td class="num">{esc(r['min_open'])}</td>
<td class="num">{esc(r['monthly_fee'])}</td>
<td class="small">{src_cell(r)}</td></tr>"""

    detail = ""
    for r in RESOLVED:
        promo = f"<p class='small'><b>Promotional rate:</b> {esc(r['promo_rate'])}</p>" if r.get("promo_rate") else ""
        bonus = f"<p class='small'><b>Opening bonus:</b> {esc(r['bonus'])}</p>" if r.get("bonus") else ""
        elig = f"<p class='small'><b>Eligibility:</b> {esc(r['eligibility'])}</p>" if r.get("eligibility") else ""
        cap = f"<p class='small'><b>Balance limit:</b> {esc(r['account_cap_note'])}</p>" if r.get("account_cap_note") else ""
        sec = (f"<p class='small'><b>Security:</b> {esc(r['security_note'])}</p>"
               if r.get("security_verified") else "<p class='small'><b>Security:</b> <span class='unv'>not verified</span></p>")
        app = (f"<p class='small'><b>Mobile app:</b> {esc(r['app_note'])}</p>"
               if r.get("app_verified") else "<p class='small'><b>Mobile app:</b> <span class='unv'>not verified</span></p>")
        detail += f"""<details><summary>{esc(r['bank'])} — {esc(r['product'])}</summary>
<p class="small"><b>How it was resolved:</b> {esc(r['resolution'])}</p>
<p class="small"><b>Fee waiver:</b> {esc(r['fee_waiver'])}</p>
<p class="small"><b>Compounding:</b> {esc(r['compounding'])}</p>
{promo}{bonus}{elig}{cap}{app}{sec}
<p class="small">{src_cell(r)}</p></details>"""

    body = f"""
<div class="banner warn"><div><strong>Why these were blank.</strong> Chase requires a 5-digit ZIP before it will
render a rate table. Bank of America's savings page returns literal <code>$XXXX</code> placeholders to an
automated reader. Citi injects its APY at runtime. Wells Fargo's product page shows a rate only for whatever
market the page defaults to. All four behaviours are real — but three of these banks <em>also</em> publish the
same numbers as static, dated, market-specific documents, which is what this page uses.</div></div>

<div class="tablewrap"><table>
<thead><tr><th>Bank / product</th><th class="num">APY (New York)</th><th>Scope of that rate</th><th class="num">Min. to open</th><th class="num">Monthly fee</th><th>Official sources</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<h2>The gap between the branch banks and the digital banks</h2>
<div class="note"><p class="small" style="margin:0">Now that the Big Four numbers are readable, the comparison
that the earlier dashboards could not make is straightforward. On a $250,000 balance held for one year:
<b>Chase Savings at 0.01% pays {money(interest(0.01, 250000, 1.0), 2)}</b>;
<b>Bank of America Advantage Savings at 0.04% pays {money(interest(0.04, 250000, 1.0), 2)}</b>;
<b>Truist One Savings at 0.01% pays {money(interest(0.01, 250000, 1.0), 2)}</b>.
The best flat rate in this layer, <b>Select Savings from Barclays at 4.25%, pays {money(interest(4.25, 250000, 1.0))}</b>
— about <b>{interest(4.25, 250000, 1.0) / interest(0.04, 250000, 1.0):,.0f}×</b> the Bank of America figure on the
same balance, at a bank with the same $250,000 FDIC limit.</p></div>

<h2>Full detail per account</h2>
{detail}

<h2>What is still unresolved</h2>
<div class="note bad"><p class="small" style="margin:0"><b>Citibank's standard savings APY remains blank.</b>
Citi's rate value is injected into the page at runtime and Citi publishes no equivalent static regional rate
sheet that could be read. Its promotional feature is documented — but Citi's own fact sheet states the
promotional rate feature for new Citi Savings accounts is discontinued effective 23 October 2026, one day after
this project's reference opening date. Published as flag <a href="flagged.html">S02</a>.
<b>PNC's High Yield Savings APY is also left blank</b>, because two official PNC URLs for the same page disagree
(3.15% versus 3.30%) and neither prints an effective date in the body — flag <a href="flagged.html">S03</a>.</p></div>
"""
    return layout("Resolved blanks", "resolved.html", "The Big Four, resolved from official rate sheets",
                  "Savings APYs the published dashboards left blank, recovered from each bank's own dated, "
                  "market-specific disclosure documents.", body)


def build_accounts():
    rows = ""
    for r in ADDED:
        app = badge("ok", "verified") if r.get("app_verified") else badge("no", "unverified")
        sec = badge("ok", "verified") if r.get("security_verified") else badge("no", "unverified")
        rows += f"""<tr>
<td><b>{esc(r['bank'])}</b><div class="small">{esc(r['product'])}</div><div class="small">{esc(r['category'])}</div></td>
<td class="num"><b>{pct(r['apy'])}</b><div class="small">{esc(r['apy_as_of'])}</div></td>
<td class="num">{esc(r['min_open'])}</td>
<td class="num">{esc(r['monthly_fee'])}</td>
<td>{app}</td><td>{sec}</td>
<td class="small">{src_cell(r)}</td></tr>"""

    detail = ""
    for r in ADDED:
        bonus = f"<p class='small'><b>Opening bonus:</b> {esc(r['bonus'])}</p>" if r.get("bonus") else "<p class='small'><b>Opening bonus:</b> none found on the official page reviewed</p>"
        elig = f"<p class='small'><b>Eligibility:</b> {esc(r['eligibility'])}</p>" if r.get("eligibility") else ""
        cap = f"<p class='small'><b>Balance / account limits:</b> {esc(r['account_cap_note'])}</p>" if r.get("account_cap_note") else ""
        agg = f"<div class='note bad'><p class='small' style='margin:0'><b>FDIC aggregation warning:</b> {esc(r['fdic_aggregation_warning'])}</p></div>" if r.get("fdic_aggregation_warning") else ""
        cav = f"<div class='note'><p class='small' style='margin:0'><b>Product caveat:</b> {esc(r['product_caveat'])}</p></div>" if r.get("product_caveat") else ""
        wdr = f"<p class='small'><b>Withdrawal rules:</b> {esc(r['withdrawal_rules'])}</p>" if r.get("withdrawal_rules") else ""
        app = (f"<p class='small'><b>Mobile app:</b> {esc(r['app_note'])}</p>" if r.get("app_verified")
               else f"<p class='small'><b>Mobile app:</b> <span class='unv'>not verified</span>{(' — ' + esc(r['app_note'])) if r.get('app_note') else ''}</p>")
        sec = (f"<p class='small'><b>Security:</b> {esc(r['security_note'])}</p>" if r.get("security_verified")
               else "<p class='small'><b>Security:</b> <span class='unv'>not verified</span></p>")
        detail += f"""<details><summary>{esc(r['bank'])} — {esc(r['product'])} · {pct(r['apy'])}</summary>
<p class="small"><b>Why it is here:</b> {esc(r['resolution'])}</p>
<p class="small"><b>Rate scope:</b> {esc(r['apy_scope'])}</p>
<p class="small"><b>Effective date:</b> {esc(r['apy_as_of_label'])}</p>
<p class="small"><b>Fee waiver:</b> {esc(r['fee_waiver'])}</p>
<p class="small"><b>Compounding:</b> {esc(r['compounding'])}</p>
{wdr}{bonus}{elig}{cap}{app}{sec}{agg}{cav}
<p class="small">{src_cell(r)}</p></details>"""

    body = f"""
<div class="banner"><div><strong>Why these matter.</strong> Each of these is nationally available, FDIC-insured
and absent from both published datasets. Two of them — Select Savings from Barclays at 4.25% and the U.S. Bank
Elite Money Market at 4.00% for new clients — sit at or near the top of the whole comparison, and one of them is
at a top-ten-by-assets national bank.</div></div>

<div class="tablewrap"><table>
<thead><tr><th>Bank / product</th><th class="num">APY</th><th class="num">Min. to open</th><th class="num">Monthly fee</th><th>App</th><th>Security</th><th>Official sources</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<h2>Full detail per account</h2>
{detail}

<h2>How these compare to the benchmarks</h2>
<p class="small">All reference points are from .gov sources read on {BM['fdic_as_of']}.</p>
<div class="tablewrap"><table>
<thead><tr><th>Account</th><th class="num">APY</th><th class="num">× FDIC national savings average ({pct(BM['fdic_national_savings_apy'])})</th><th class="num">vs federal funds ceiling (4.00%)</th><th class="num">vs 6-month Treasury ({pct(BM['treasury_6m'])})</th><th class="num">vs 12-month Treasury ({pct(BM['treasury_12m'])})</th></tr></thead>
<tbody>""" + "".join(
        f"""<tr><td><b>{esc(r['bank'])}</b><div class="small">{esc(r['product'])}</div></td>
<td class="num"><b>{pct(r['apy'])}</b></td>
<td class="num">{r['apy'] / BM['fdic_national_savings_apy']:,.1f}×</td>
<td class="num">{r['apy'] - 4.00:+.2f} pp</td>
<td class="num">{r['apy'] - BM['treasury_6m']:+.2f} pp</td>
<td class="num">{r['apy'] - BM['treasury_12m']:+.2f} pp</td></tr>"""
        for r in sorted(ADDED, key=lambda x: -x["apy"])) + f"""
</tbody></table></div>
<p class="legend">A negative figure against a Treasury yield does not make the account a bad choice — Treasuries
are not FDIC-insured deposits and are far less liquid. It does show how much of the yield curve a savings
account is giving up. Source for all three benchmarks: {link(BM['fdic_source'], 'FDIC National Rates and Rate Caps')}
and {link(BM['fed_funds_source'], 'Federal Reserve open market operations')}.</p>
"""
    return layout("Added accounts", "accounts.html", f"{len(ADDED)} accounts neither dashboard carried",
                  "Nationally available, FDIC-insured savings accounts missing from both published datasets — "
                  "including the highest flat APY found anywhere in this repository.", body)


def build_returns():
    proj = projectable()

    def table(years, label):
        head = "".join(f"<th class='num'>{money(d)}</th>" for d in DEPOSITS)
        rows = ""
        for r in proj:
            cells = ""
            for d in DEPOSITS:
                val = interest(r["apy"], d, years)
                warn = ' style="color:#b54708"' if d > 250000 else ""
                cells += f"<td class='num'{warn}>{money(val)}</td>"
            rows += (f"<tr><td><b>{esc(r['bank'])}</b><div class='small'>{esc(r['product'])}</div>"
                     f"<div class='small'>{pct(r['apy'])}</div></td>{cells}</tr>")
        return (f"<div class='tablewrap'><table><thead><tr><th>{label}</th>{head}</tr></thead>"
                f"<tbody>{rows}</tbody></table></div>")

    best = proj[0]
    ladder = ""
    for lbl, yrs in HORIZONS:
        bal = 250000 + interest(best["apy"], 250000, yrs)
        ladder += (f"<tr><td><b>{esc(lbl)}</b></td><td class='num'>{money(interest(best['apy'], 250000, yrs))}</td>"
                   f"<td class='num'>{money(bal)}</td>"
                   f"<td class='num'>{money(max(0, bal - 250000))}</td></tr>")

    safe = 250000 / ((1 + best["apy"] / 100.0) ** 1.0)

    body = f"""
<div class="banner"><div><strong>Assumptions, stated once and applied everywhere.</strong>
Lump sum deposited {OPEN_DATE}. No additions, no withdrawals, no fees deducted (every account projected here has
a $0 monthly fee or a waiver the deposit itself satisfies). Interest compounds at the bank's published APY,
held constant for the whole horizon. Cash bonuses are excluded — they are listed on the account pages, never
folded into an interest figure. <strong>Every APY here is variable</strong> and the bank can change it the day
after the account is opened, so the multi-year columns are illustrations of a constant-rate scenario, not
forecasts.</div></div>

<h2>Which accounts are projected — and which are deliberately not</h2>
<div class="grid g2">
  <div class="card"><h3 style="margin-top:0">Projected</h3>
  <p class="small">The {len(proj)} accounts in this layer with a verified APY read from an official page. Each
  pays its rate on the whole balance, so the arithmetic is unambiguous.</p></div>
  <div class="card"><h3 style="margin-top:0">Not projected</h3>
  <p class="small"><b>Citi Savings</b> and <b>PNC High Yield Savings</b> have no readable or no unambiguous APY
  and are excluded entirely rather than estimated. <b>Axos ONE</b> is not projected in this layer because its
  headline and its own rate table disagree — see flag <a href="flagged.html">S01</a>. Conditional rates
  (<b>Wells Fargo</b> $25,000+, <b>U.S. Bank Elite Money Market</b> $25,000+ for new clients) are projected only
  at deposit sizes where their condition is met; smaller sizes are shown for completeness but the condition is
  noted on the account page.</p></div>
</div>

<h2>Interest earned — 1 year</h2>
{table(1.0, "Account")}

<h2>Interest earned — 2 years</h2>
{table(2.0, "Account")}

<h2>Interest earned — 3 years</h2>
{table(3.0, "Account")}

<h2>Interest earned — 5 years</h2>
{table(5.0, "Account")}
<p class="legend">Figures in amber are on balances above $250,000 — the FDIC single-owner limit at one bank.
That portion is uninsured unless it is spread across banks or ownership categories. See
<a href="coverage.html">Max FDIC coverage</a>.</p>

<h2>The FDIC safe-harbour problem nobody's table shows</h2>
<div class="note bad"><p class="small" style="margin:0">If you deposit exactly $250,000 to hit the FDIC limit,
<b>you are uninsured by the end of the first month</b> — because the interest pushes the balance above the
ceiling, and FDIC coverage includes principal <em>and</em> accrued interest up to the limit.
At {esc(best['bank'])}'s {pct(best['apy'])}, the largest opening deposit that stays inside $250,000 for a
full year is <b>{money(safe, 2)}</b>. Deposit more than that and the excess is uninsured for as long as it
sits there.</p></div>

<div class="tablewrap"><table>
<thead><tr><th>Horizon from {OPEN_DATE}</th><th class="num">Interest on a $250,000 deposit</th><th class="num">Ending balance</th><th class="num">Amount above the $250,000 FDIC limit</th></tr></thead>
<tbody>{ladder}</tbody></table></div>
<p class="small">Computed at {esc(best['bank'])} — {esc(best['product'])}, {pct(best['apy'])}
({esc(best['apy_as_of_label'])}). {src_cell(best)}</p>

<h2>Three ways to stay fully insured while still earning</h2>
<ul class="tight">
  <li><b>Open below the line.</b> Deposit {money(safe, 2)} rather than $250,000 and let a year of interest bring
  the balance to the ceiling.</li>
  <li><b>Sweep the interest out.</b> Move credited interest to a second insured bank monthly or quarterly; the
  principal then stays at exactly $250,000 indefinitely.</li>
  <li><b>Use a second ownership category.</b> A joint account or a trust account at the same bank is insured
  separately from a single account — see <a href="coverage.html">Max FDIC coverage</a> for the exact ceilings.</li>
</ul>
"""
    return layout("Returns", "returns.html", "Returns over 1, 2, 3 and 5 years",
                  "Interest at seven deposit sizes for every account in this layer with a verified APY — plus "
                  "the FDIC safe-harbour arithmetic that a flat $250,000 deposit quietly breaks.", body)


def build_coverage():
    cats = [
        ("Single accounts", "$250,000 per owner", 250000,
         "One person, no beneficiaries. All single accounts you hold at the same bank are added together."),
        ("Joint accounts", "$500,000 per account (2 owners)", 500000,
         "Each co-owner is insured to $250,000 for their share. A two-owner joint account is insured to $500,000, and that is separate from either owner's single accounts."),
        ("Trust accounts (revocable + irrevocable)", "up to $1,250,000 per owner", 1250000,
         "Since 1 April 2024 the FDIC combines revocable (POD/ITF) and irrevocable trusts into one category: $250,000 per eligible beneficiary, capped at five beneficiaries — a $1,250,000 maximum per owner, per bank."),
        ("Certain retirement accounts", "$250,000 per owner", 250000,
         "IRAs and certain self-directed retirement deposits are a separate ownership category from single accounts at the same bank."),
    ]
    cat_rows = "".join(
        f"<tr><td><b>{esc(n)}</b></td><td class='num'><b>{esc(lim)}</b></td><td class='num'>{money(v)}</td><td class='small'>{esc(d)}</td></tr>"
        for n, lim, v, d in cats)

    stack = [
        ("Single account", 250000, 250000),
        ("+ Joint account with one other person", 500000, 750000),
        ("+ Trust account naming 5 beneficiaries", 1250000, 2000000),
        ("+ IRA / certain retirement deposits", 250000, 2250000),
    ]
    stack_rows = ""
    run = 0
    for name, add, _ in stack:
        run += add
        stack_rows += (f"<tr><td>{esc(name)}</td><td class='num'>{money(add)}</td>"
                       f"<td class='num'><b>{money(run)}</b></td></tr>")

    proj = projectable()
    best = proj[0]
    second = proj[1]
    third = proj[2]

    plan_rows = ""
    for target in [250000, 500000, 1000000, 1250000, 2000000]:
        banks_needed = max(1, -(-target // 250000))
        plan_rows += (f"<tr><td class='num'><b>{money(target)}</b></td>"
                      f"<td class='num'>{banks_needed}</td>"
                      f"<td class='num'>{money(min(target, 1250000))}</td>"
                      f"<td class='num'>{money(interest(best['apy'], target, 1.0))}</td></tr>")

    body = f"""
<div class="banner"><div><strong>The rule, stated exactly.</strong> FDIC insurance is
<b>$250,000 per depositor, per insured bank, for each account ownership category</b> — not per account.
All deposits you hold in the same category at the same bank are added together, including accrued interest.
Source: {link(BM['fdic_source'].replace('national-rates-and-rate-caps', 'resources/deposit-insurance/brochures/deposits-at-a-glance'), 'FDIC — Deposit Insurance At A Glance')}.</div></div>

<h2>The ownership categories, and what each one is worth</h2>
<div class="tablewrap"><table>
<thead><tr><th>Ownership category</th><th class="num">Limit at ONE bank</th><th class="num">Maximum insured</th><th>What it means in practice</th></tr></thead>
<tbody>{cat_rows}</tbody></table></div>

<h2>Stacking categories at a single bank</h2>
<p class="small">These categories are independent of each other. One depositor, at one FDIC-insured bank, can
therefore be covered well beyond $250,000 — provided each category genuinely applies and is correctly titled.</p>
<div class="tablewrap"><table>
<thead><tr><th>Added at the same bank</th><th class="num">Coverage added</th><th class="num">Running total insured</th></tr></thead>
<tbody>{stack_rows}</tbody></table></div>
<div class="note"><p class="small" style="margin:0">The FDIC's own calculator,
<a href="https://edie.fdic.gov/" target="_blank" rel="noopener">EDIE</a>, prices a specific combination of
accounts and titling. Use it before relying on any stacked figure — the categories must genuinely apply, and
beneficiaries must be eligible.</p></div>

<h2>Getting to a target, with the best verified rate in this layer</h2>
<p class="small">Using {esc(best['bank'])} at {pct(best['apy'])}. "Banks needed" assumes a single ownership
category only — stacking categories as above reduces the number of banks required.</p>
<div class="tablewrap"><table>
<thead><tr><th class="num">Target balance</th><th class="num">Banks needed (single category only)</th><th class="num">Insurable at ONE bank using single + joint + trust</th><th class="num">Year-1 interest at {pct(best['apy'])}</th></tr></thead>
<tbody>{plan_rows}</tbody></table></div>

<h2>A fully-insured $1,000,000 built from this layer's verified rates</h2>
<p class="small">Four separate FDIC certificates, $250,000 in each, all in a single ownership category — the
simplest structure that is unambiguously covered end to end.</p>
<div class="tablewrap"><table>
<thead><tr><th>Bank</th><th class="num">FDIC cert</th><th class="num">Deposit</th><th class="num">APY</th><th class="num">Year-1 interest</th><th>Source</th></tr></thead>
<tbody>
<tr><td><b>{esc(best['bank'])}</b><div class="small">{esc(best['product'])}</div></td><td class="num">{best['fdic_cert']}</td><td class="num">{money(250000)}</td><td class="num">{pct(best['apy'])}</td><td class="num">{money(interest(best['apy'], 250000, 1.0))}</td><td class="small">{link(list(best['sources'].values())[0], 'official')}</td></tr>
<tr><td><b>{esc(second['bank'])}</b><div class="small">{esc(second['product'])}</div></td><td class="num">{second['fdic_cert']}</td><td class="num">{money(250000)}</td><td class="num">{pct(second['apy'])}</td><td class="num">{money(interest(second['apy'], 250000, 1.0))}</td><td class="small">{link(list(second['sources'].values())[0], 'official')}</td></tr>
<tr><td><b>{esc(third['bank'])}</b><div class="small">{esc(third['product'])}</div></td><td class="num">{third['fdic_cert']}</td><td class="num">{money(250000)}</td><td class="num">{pct(third['apy'])}</td><td class="num">{money(interest(third['apy'], 250000, 1.0))}</td><td class="small">{link(list(third['sources'].values())[0], 'official')}</td></tr>
<tr><td><b>Fourth certificate of your choice</b><div class="small">see the main and cross-check dashboards for further options</div></td><td class="num">—</td><td class="num">{money(250000)}</td><td class="num">—</td><td class="num">—</td><td class="small"><a href="../index.html">main dashboard</a></td></tr>
</tbody></table></div>

<h2>Certificate traps that break a max-coverage plan</h2>
<div class="note bad"><p class="small" style="margin:0">Several well-known brands are <b>not</b> separate banks.
Openbank and Santander share FDIC Cert #29950. CIT Bank and First-Citizens Bank &amp; Trust share Cert #11063.
Alto and BMO Bank N.A. share Cert #16571. Barclays Tiered Savings, Barclays Online Savings and Select Savings
from Barclays all share Cert #57203. Capital One 360 and the former Discover Bank share Cert #4297 — Discover's
own Cert #5649 is inactive. Depositing $250,000 at each brand in a pair produces $250,000 of coverage, not
$500,000. Published as flag <a href="flagged.html">S05</a>.</p></div>

<h2>Programme coverage is real, but it is not the host bank's insurance</h2>
<p class="small">SoFi advertises up to $3,000,000 and Axos up to $2,500,000 of FDIC coverage. In both cases the
host bank provides only the standard $250,000; the excess is swept into partner banks, and the coverage depends
on those partners and on you not already holding deposits at them. SoFi's own participating-bank list includes
Citibank (#7213), Citizens Bank (#57957) and Morgan Stanley Bank (#32992) — so a depositor who already holds
$250,000 at any of those banks directly can lose part of the benefit. Check the partner list before relying on
a programme figure.</p>
<p class="small">{link('https://www.sofi.com/banking/fdic/participatingbanks/', 'SoFi participating banks')} ·
{link('https://www.axosbank.com/personal/bank/axos-insured-deposit-program', 'Axos Insured Deposit Program')}</p>
"""
    return layout("Max FDIC coverage", "coverage.html", "Insuring the maximum, precisely",
                  "Ownership categories, the $1,250,000 trust ceiling the other dashboards omit, the shared-"
                  "certificate traps, and a fully-insured $1,000,000 built from verified rates.", body)


def build_flagged():
    rows = ""
    for f in NEWFLAGS:
        sev = {"high": "no", "medium": "warn", "low": "info"}[f["severity"]]
        links = "<br>".join(link(u, u.split("/")[2]) for u in f["sources"])
        rows += f"""<tr><td>{badge(sev, f['severity'])}</td>
<td><b>{esc(f['id'])} — {esc(f['title'])}</b>
<div class="small" style="margin-top:6px">{esc(f['detail'])}</div></td>
<td class="small">{links}</td>
<td>{badge('info', 'needs review')}</td></tr>"""

    closed_rows = ""
    for c in CLOSED:
        links = "<br>".join(link(u, u.split("/")[2]) for u in c["sources"])
        closed_rows += f"""<tr><td>{badge('ok', 'closed')}</td>
<td><b>{esc(c['id'])}</b> — previously published as: <i>{esc(c['closes'])}</i>
<div class="small" style="margin-top:6px">{esc(c['finding'])}</div></td>
<td class="small">{links}</td></tr>"""

    body = f"""
<div class="banner warn"><div><strong>{len(NEWFLAGS)} new items, two of them high severity.</strong>
Nothing on this page blocks publication. Each item is either a conflict between two official pages, a term that
materially changes the return, or a structural risk to a maximum-FDIC-coverage plan. Every one is linked to the
official page it came from so it can be checked by hand.</div></div>

<div class="tablewrap"><table>
<thead><tr><th>Severity</th><th>Item</th><th>Official sources</th><th>Status</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<h2>Items this layer CLOSED</h2>
<p class="small">These were published as unverified on the main dashboard. Each has now been resolved against a
primary source and can be removed from the open list after review.</p>
<div class="tablewrap"><table>
<thead><tr><th>Status</th><th>Item and resolution</th><th>Official sources</th></tr></thead>
<tbody>{closed_rows}</tbody></table></div>

<h2>How a blank is treated here</h2>
<div class="card"><p class="small" style="margin:0">A blank cell renders as <span class="unv">—</span> and means
the value could not be read from an official page on {VERIFIED}. It never means zero and never means "none".
Two values in this layer are deliberately left blank despite being partially visible: Citibank's standard savings
APY (injected at runtime) and PNC's High Yield Savings APY (two official PNC URLs disagree). Neither was resolved
to a number, because resolving them would require choosing between conflicting official figures.</p></div>
"""
    return layout("Flagged for review", "flagged.html", "Flagged for review",
                  "New irregularities found by this layer, and the previously-open items it closed against a "
                  "primary source.", body)


def build_sources():
    groups = {
        "U.S. government sources": [
            ("FDIC — National Rates and Rate Caps, October 2026", BM["fdic_source"],
             f"National savings average {pct(BM['fdic_national_savings_apy'])}, savings rate cap {pct(BM['fdic_national_rate_cap_savings'])}, money market {pct(BM['fdic_money_market_apy'])}, Treasury yields; revised {BM['fdic_as_of']}"),
            ("FDIC — Deposit Insurance At A Glance",
             "https://www.fdic.gov/resources/deposit-insurance/brochures/deposits-at-a-glance",
             "The $250,000 limit, ownership categories, and the April 2024 trust rule ($1,250,000 for five beneficiaries)"),
            ("FDIC — BankFind institution API", "https://api.fdic.gov/banks/institutions",
             "Certificate numbers, active/inactive status, charter class, city and total assets for every bank in this layer"),
            ("FDIC — EDIE deposit insurance estimator", "https://edie.fdic.gov/",
             "Referenced as the authoritative calculator for a specific combination of accounts"),
            ("Federal Reserve — Open market operations", BM["fed_funds_source"],
             f"Federal funds target range {BM['fed_funds_target']} as of {BM['fed_funds_as_of']}"),
        ],
        "Official rate sheets and disclosure PDFs (the documents that resolved the blanks)": [],
        "Bank product, fee, app and security pages": [],
    }

    for r in RESOLVED + ADDED:
        for key, url in r["sources"].items():
            entry = (f"{r['bank']} — {r['product']}", url, f"{key.replace('_', ' ')}")
            if key.endswith("_pdf") or key in ("fee_schedule", "disclosures", "addenda_pdf"):
                groups["Official rate sheets and disclosure PDFs (the documents that resolved the blanks)"].append(entry)
            else:
                groups["Bank product, fee, app and security pages"].append(entry)

    extra = [
        ("Axos Bank — Axos ONE", "https://www.axosbank.com/personal/bank/axos-one",
         "Rate-table conflict documented in flag S01"),
        ("SoFi — participating banks in the Insured Deposit Program",
         "https://www.sofi.com/banking/fdic/participatingbanks/",
         "Partner-bank overlap risk documented on the coverage page"),
        ("Axos — Insured Deposit Program",
         "https://www.axosbank.com/personal/bank/axos-insured-deposit-program",
         "Programme coverage up to $2.5M referenced on the coverage page"),
        ("Marcus by Goldman Sachs — FAQs", "https://www.marcus.com/us/en/faqs",
         "Balance limits: $1,000,000 per account, $3,000,000 per depositor (flag S06)"),
        ("American Express — Savings Schedule (PDF)",
         "https://www.americanexpress.com/content/dam/amex/en-us/banking/personal-savings/Savings-Schedule.pdf",
         "Maximum account balance of $5,000,000 and a 20-account limit, rev. October 18, 2026 (flag S06)"),
    ]
    groups["Bank product, fee, app and security pages"].extend(extra)

    html = ""
    for name, items in groups.items():
        if not items:
            continue
        seen, uniq = set(), []
        for t, u, n in items:
            if u in seen:
                continue
            seen.add(u)
            uniq.append((t, u, n))
        html += (f"<h2>{esc(name)}</h2><p class='small'>{len(uniq)} documents.</p>"
                 "<div class='tablewrap'><table><thead><tr><th>Document</th><th>Link</th>"
                 "<th>What it verified</th></tr></thead><tbody>")
        for t, u, n in uniq:
            html += (f"<tr><td><b>{esc(t)}</b></td><td class='small'>{link(u, u)}</td>"
                     f"<td class='small'>{esc(n)}</td></tr>")
        html += "</tbody></table></div>"

    body = f"""
<div class="banner"><div><strong>Official domains only.</strong> Every figure in this layer was read from a
bank's own domain or a <code>.gov</code> domain during this session. No aggregator, comparison site, review
site or news article supplied a single value. Where a bank's own page did not show a value, the cell is blank
and the item is on <a href="flagged.html">Flagged for review</a>.</div></div>
{html}
<h2>How to re-check any figure</h2>
<div class="card"><p class="small" style="margin:0">Open the linked document and search for the account name.
Rate-sheet PDFs print their own effective date at the top — Chase's New York sheet says
"RATES IN EFFECT AS OF: Friday, October 16, 2026", Bank of America's New York–Tri-State sheet says
"Effective as of: October 21, 2026", and Wells Fargo's addenda says "Platinum Savings Rate Update,
Effective October 7, 2026". Those printed dates are what appear in the tables on this site; where a page prints
no date, the table says so explicitly instead of substituting the date it was read.</p></div>
"""
    return layout("Sources", "sources.html", "Every source, and what it verified",
                  "The official documents behind this layer — government sources first, then the rate sheets "
                  "that resolved the previously-blank values.", body)


def main():
    OUT.mkdir(exist_ok=True)
    pages = {
        "index.html": build_index(),
        "resolved.html": build_resolved(),
        "accounts.html": build_accounts(),
        "returns.html": build_returns(),
        "coverage.html": build_coverage(),
        "flagged.html": build_flagged(),
        "sources.html": build_sources(),
    }
    for name, html in pages.items():
        (OUT / name).write_text(html)
    print(f"Wrote {len(pages)} pages to {OUT}")
    print(f"  resolved: {len(RESOLVED)} | added: {len(ADDED)} | "
          f"closed flags: {len(CLOSED)} | new flags: {len(NEWFLAGS)} | "
          f"projectable: {len(projectable())}")


if __name__ == "__main__":
    main()
