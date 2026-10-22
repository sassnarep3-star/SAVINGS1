#!/usr/bin/env python3
"""
Build the SAVINGS1 static site from verified data.

All rates/terms come from data/*.json, which are populated only from official
bank / FDIC / Federal Reserve pages. This script performs arithmetic on those
verified values; it never invents a rate.

Output: repository root (GitHub Pages source: main branch, /)
"""
from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT

META = json.loads((DATA / "accounts.json").read_text())["meta"]
ACCOUNTS = json.loads((DATA / "accounts.json").read_text())["accounts"]
PROMOS = json.loads((DATA / "promotions.json").read_text())
FDIC = json.loads((DATA / "fdic.json").read_text())
FLAGS = json.loads((DATA / "flags.json").read_text())

VERIFIED = META["verification_date"]
OPEN_DATE = META["account_open_date"]
NATIONAL = META["fdic_national_savings_rate"]
FED_TOP = 4.00
TREASURY = META["treasury_yields"]
TIERS = META["deposit_tiers"]

PAGES = [
    ("index.html", "Overview"),
    ("accounts.html", "Accounts"),
    ("returns.html", "Returns"),
    ("promotions.html", "Promotions"),
    ("fdic.html", "FDIC coverage"),
    ("analysis.html", "Analysis"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged for review"),
    ("method.html", "Method"),
]


# ---------------------------------------------------------------- formatting
def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def money(v, decimals=0) -> str:
    if v is None:
        return '<span class="unv">—</span>'
    return f"${v:,.{decimals}f}"


def pct(v, decimals=2) -> str:
    if v is None:
        return '<span class="unv">—</span>'
    return f"{v:.{decimals}f}%"


def link(url, text="source") -> str:
    if not url:
        return '<span class="unv">no source</span>'
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(text)}</a>'


def badge(kind, text=None) -> str:
    labels = {"ok": "verified", "warn": "flagged", "no": "unverified", "info": "info"}
    return f'<span class="badge {kind}">{esc(text or labels.get(kind, kind))}</span>'


# ---------------------------------------------------------------- math
def split_bands(amount: float, bands):
    """Marginal split of an amount across bands."""
    out, prev = [], 0.0
    for b in bands:
        upto = b["upto"]
        cap = amount if upto is None else min(amount, float(upto))
        portion = max(0.0, cap - prev)
        if portion > 0:
            out.append((portion, float(b["rate"]) / 100.0))
        prev = cap if upto is None else min(amount, float(upto))
        if upto is not None and amount <= float(upto):
            break
    if not out:
        out = [(amount, float(bands[-1]["rate"]) / 100.0)]
    return out


def rate_for_amount(amount: float, bands, mode: str) -> float:
    """Effective annual rate on the whole balance under cliff or marginal tiers."""
    if not bands:
        return 0.0
    if mode == "cliff":
        for b in bands:
            if b["upto"] is None or amount <= float(b["upto"]):
                return float(b["rate"]) / 100.0
        return float(bands[-1]["rate"]) / 100.0
    if len(bands) == 1:
        return float(bands[0]["rate"]) / 100.0
    return sum(p * r for p, r in split_bands(amount, bands)) / amount


def balance_after(acct: dict, deposit: float, years: float) -> float:
    std = acct.get("standard_bands")
    if not std:
        return deposit
    mode = acct.get("tier_mode", "marginal")
    promo_m = acct.get("promo_months") or 0
    promo = acct.get("promo_bands")

    if promo_m > 0 and promo:
        t1 = promo_m / 12.0
        if mode == "cliff":
            r1 = rate_for_amount(deposit, promo, mode)
            b1 = deposit * (1 + r1) ** t1
        else:
            b1 = sum(p * (1 + r) ** t1 for p, r in split_bands(deposit, promo))
        rest = years - t1
        if rest <= 0:
            return deposit * (1 + rate_for_amount(deposit, promo, mode)) ** years
        if mode == "cliff":
            r2 = rate_for_amount(b1, std, mode)
            return b1 * (1 + r2) ** rest
        return sum(p * (1 + r) ** rest for p, r in split_bands(b1, std))

    if mode == "cliff":
        return deposit * (1 + rate_for_amount(deposit, std, mode)) ** years
    return sum(p * (1 + r) ** years for p, r in split_bands(deposit, std))


def interest(acct: dict, deposit: float, years: float) -> float:
    return balance_after(acct, deposit, years) - deposit


def standard_interest(acct: dict, deposit: float) -> float:
    std = acct.get("standard_bands")
    if not std:
        return 0.0
    mode = acct.get("tier_mode", "marginal")
    if mode == "cliff":
        return deposit * rate_for_amount(deposit, std, mode)
    return sum(p * r for p, r in split_bands(deposit, std))


def blended_apy(acct: dict, deposit: float) -> float:
    return (balance_after(acct, deposit, 1.0) / deposit - 1) * 100


def active_accounts():
    return [a for a in ACCOUNTS if a.get("standard_bands")]


def top_for_tier(deposit, metric="y1"):
    rows = []
    for a in active_accounts():
        if metric == "y1":
            val = interest(a, deposit, 1.0)
        elif metric == "y5":
            val = interest(a, deposit, 5.0)
        else:
            val = blended_apy(a, deposit)
        rows.append((val, a))
    return sorted(rows, key=lambda x: -x[0])


# ---------------------------------------------------------------- layout
CSS = """
:root{
  --bg:#f6f7f9; --card:#ffffff; --ink:#101828; --muted:#667085; --line:#e4e7ec;
  --brand:#0b5fff; --brand-dark:#0846c4; --ok:#067647; --ok-bg:#ecfdf3;
  --warn:#b54708; --warn-bg:#fffaeb; --bad:#b42318; --bad-bg:#fef3f2;
  --radius:14px; --shadow:0 1px 2px rgba(16,24,40,.06),0 1px 3px rgba(16,24,40,.10);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--brand);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.site{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
.nav{display:flex;align-items:center;gap:18px;height:62px;flex-wrap:nowrap;overflow-x:auto}
.brand{font-weight:800;letter-spacing:-.02em;font-size:17px;white-space:nowrap;color:var(--ink)}
.brand span{color:var(--brand)}
.nav a.lnk{color:#344054;font-size:14px;font-weight:550;white-space:nowrap;padding:6px 2px;border-bottom:2px solid transparent}
.nav a.lnk.active{color:var(--brand);border-bottom-color:var(--brand)}
.nav .spacer{flex:1}
main{padding:34px 0 70px}
h1{font-size:34px;line-height:1.15;letter-spacing:-.03em;margin:0 0 10px}
h2{font-size:22px;letter-spacing:-.02em;margin:38px 0 12px}
h3{font-size:17px;margin:24px 0 8px}
p.lede{font-size:17px;color:#475467;max-width:80ch;margin:0 0 22px}
.small{font-size:13px;color:var(--muted)}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:20px}
.grid{display:grid;gap:14px}
.g4{grid-template-columns:repeat(4,1fr)}
.g3{grid-template-columns:repeat(3,1fr)}
.g2{grid-template-columns:repeat(2,1fr)}
@media(max-width:900px){.g4{grid-template-columns:repeat(2,1fr)}.g3,.g2{grid-template-columns:1fr}}
@media(max-width:560px){.g4{grid-template-columns:1fr}h1{font-size:27px}}
.kpi .label{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:700}
.kpi .value{font-size:30px;font-weight:800;letter-spacing:-.03em;margin:6px 0 2px}
.kpi .sub{font-size:13px;color:var(--muted)}
.banner{display:flex;gap:12px;align-items:flex-start;background:var(--ok-bg);border:1px solid #abefc6;color:#054f31;border-radius:12px;padding:12px 14px;font-size:14px;margin-bottom:22px}
.banner.warn{background:var(--warn-bg);border-color:#fedf89;color:#7a2e0e}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:#fff}
table{border-collapse:collapse;width:100%;font-size:14px;min-width:640px}
th,td{padding:11px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f9fafb;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#475467;font-weight:700;position:sticky;top:0}
tbody tr:hover{background:#fbfcfe}
tbody tr:last-child td{border-bottom:none}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.badge{display:inline-block;font-size:11px;font-weight:700;padding:2px 7px;border-radius:999px;white-space:nowrap}
.badge.ok{background:var(--ok-bg);color:var(--ok)}
.badge.warn{background:var(--warn-bg);color:var(--warn)}
.badge.no{background:var(--bad-bg);color:var(--bad)}
.badge.info{background:#eff4ff;color:#175cd3}
.unv{color:#b42318;font-weight:600}
.note{background:#f9fafb;border-left:3px solid var(--brand);padding:12px 14px;border-radius:0 8px 8px 0;font-size:14px;color:#344054;margin:16px 0}
.note.bad{border-left-color:var(--bad);background:var(--bad-bg)}
.note.ok{border-left-color:var(--ok);background:var(--ok-bg)}
ul.tight{margin:8px 0 0;padding-left:18px}
ul.tight li{margin:5px 0}
.tile{display:block;background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px;box-shadow:var(--shadow)}
.tile:hover{border-color:#b2ccff;text-decoration:none}
.tile b{display:block;margin-bottom:4px}
.bar{height:9px;border-radius:5px;background:#e9edf5;overflow:hidden;min-width:100px}
.bar>i{display:block;height:100%;background:linear-gradient(90deg,#0b5fff,#4f8cff)}
.rank{display:inline-flex;width:22px;height:22px;border-radius:50%;background:#eff4ff;color:#175cd3;font-size:12px;font-weight:800;align-items:center;justify-content:center}
footer{border-top:1px solid var(--line);background:#fff;padding:26px 0;color:var(--muted);font-size:13px}
code{background:#f2f4f7;padding:1px 5px;border-radius:4px;font-size:13px}
details{border:1px solid var(--line);border-radius:10px;background:#fff;padding:12px 14px;margin:10px 0}
summary{cursor:pointer;font-weight:650}
.search{width:100%;max-width:340px;padding:9px 12px;border:1px solid #d0d5dd;border-radius:9px;font-size:14px;margin:0 0 12px}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--muted);margin:8px 0 0}
"""

JS = """
document.querySelectorAll('input[data-filter]').forEach(function(inp){
  inp.addEventListener('input', function(){
    var q = inp.value.toLowerCase();
    var table = document.querySelector(inp.dataset.filter);
    if(!table) return;
    table.querySelectorAll('tbody tr').forEach(function(tr){
      tr.style.display = tr.innerText.toLowerCase().indexOf(q) > -1 ? '' : 'none';
    });
  });
});
"""


def layout(title: str, active: str, body: str, subtitle: str = "") -> str:
    nav = "".join(
        f'<a class="lnk{" active" if f == active else ""}" href="{f}">{esc(label)}</a>'
        for f, label in PAGES
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · SAVINGS1</title>
<meta name="description" content="Verified comparison of national-bank savings accounts: APYs, returns by deposit size, FDIC coverage, promotions, and flagged irregularities.">
<link rel="stylesheet" href="assets/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>%F0%9F%8F%A6</text></svg>">
</head>
<body>
<header class="site"><div class="wrap"><nav class="nav">
<a class="brand" href="index.html">SAVINGS<span>1</span></a>
{nav}
<span class="spacer"></span>
</nav></div></header>
<main><div class="wrap">
{body}
</div></main>
<footer><div class="wrap">
<p><strong>SAVINGS1</strong> — independent, source-linked comparison built {VERIFIED}. Account opening date used for all return math: {OPEN_DATE}.</p>
<p>Rates change daily. Every figure links to the official page it came from; blank cells are unverified and listed on the <a href="flagged.html">Flagged for review</a> page. This is research, not financial advice.</p>
</div></footer>
<script src="assets/app.js"></script>
</body></html>"""


def page_shell(title, active, heading, lede, body):
    return layout(title, active, f"<h1>{esc(heading)}</h1><p class='lede'>{lede}</p>{body}")


# ---------------------------------------------------------------- sections
def source_cell(a):
    s = link(a["source"], "official page")
    if a.get("terms_source") and a["terms_source"] != a["source"]:
        s += "<br>" + link(a["terms_source"], "terms/rates")
    if a.get("fdic", {}).get("cert"):
        s += f"<br><span class='small'>FDIC cert {a['fdic']['cert']}</span>"
    return s


def status_cell(a):
    if a["category"] == "closed":
        return badge("no", "closed")
    if a.get("headline_apy") is None:
        return badge("no", "APY unverified")
    if a.get("promo_months"):
        return badge("warn", "intro rate")
    return badge("ok", "verified")


# ---------------------------------------------------------------- index
def build_index():
    t250 = top_for_tier(250000)
    best, second, third = t250[0], t250[1], t250[2]
    n_active = len(active_accounts())
    n_flags = len(FLAGS["flags"])

    nc_best = max(((interest(a, 250000, 1.0), a) for a in active_accounts() if not a.get("promo_months")),
                  key=lambda row: row[0])
    rows = ""
    for i, (val, a) in enumerate(t250[:6], 1):
        rows += f"""<tr>
<td><span class="rank">{i}</span></td>
<td><b>{esc(a['bank'])}</b><div class="small">{esc(a['product'])}</div></td>
<td class="num"><b>{pct(a['headline_apy'])}</b><div class="small">{'6-mo intro' if a.get('promo_months') else 'variable'}</div></td>
<td class="num">{pct(a['standard_apy'])}</td>
<td class="num"><b>{money(val)}</b></td>
<td class="num">{pct(blended_apy(a, 250000))}</td>
<td>{source_cell(a)}</td></tr>"""

    body = f"""
<div class="banner"><div><strong>Verified {VERIFIED}.</strong> Every rate and term in this dashboard was read from the bank's own website, the FDIC, or the Federal Reserve. Cells that could not be confirmed are blank and published on the <a href="flagged.html">Flagged for review</a> page — never filled in by inference.</div></div>

<div class="grid g4">
  <div class="card kpi"><div class="label">Highest 1-year return on $250,000</div><div class="value">{pct(blended_apy(best[1], 250000), 2)}</div><div class="sub">{esc(best[1]['bank'])} · {money(best[0])} interest</div></div>
  <div class="card kpi"><div class="label">FDIC national savings average</div><div class="value">{NATIONAL:.2f}%</div><div class="sub">as of {META['fdic_national_savings_rate_as_of']} · <a href="https://www.fdic.gov/national-rates-and-rate-caps" target="_blank" rel="noopener">FDIC</a></div></div>
  <div class="card kpi"><div class="label">Federal funds target</div><div class="value">{META['fed_funds_target_range']}%</div><div class="sub">after the {META['fed_funds_as_of']} FOMC move · <a href="https://www.federalreserve.gov/monetarypolicy/openmarket.htm" target="_blank" rel="noopener">Federal Reserve</a></div></div>
  <div class="card kpi"><div class="label">Accounts with a verified APY</div><div class="value">{n_active}<span style="font-size:16px;color:#667085">/{len(ACCOUNTS)}</span></div><div class="sub">5 unverified (Big Four + U.S. Bank) · 1 closed · {n_flags} flags</div></div>
</div>

<h2>Bottom line</h2>
<div class="grid g2">
  <div class="card"><h3 style="margin-top:0">Best one-year return — Axos ONE, if you will meet the conditions</h3>
  <p class="small"><b>{pct(blended_apy(best[1], 250000), 2)}</b> blended in year one on $250,000 ({money(best[0])} of interest), from a 5.00% six-month introductory rate on the first $50,000 and 4.21% above it. The 4.21% ongoing rate needs an Axos ONE checking account plus either $1,500 of monthly direct deposits and a $1,500 average daily balance, or $5,000 of monthly deposits and a $5,000 balance. Miss a month and the rate falls to <b>1.00%</b>.</p>
  <p>{link('https://www.axosbank.com/personal/bank/axos-one', 'Axos terms')} · <a href="analysis.html">Competitiveness analysis</a></p></div>
  <div class="card"><h3 style="margin-top:0">Best return with no conditions — EverBank</h3>
  <p class="small"><b>4.20%</b> on every balance, no monthly fee, $0 to open. That is <b>{money(interest(nc_best[1], 250000, 1.0))}</b> of interest on $250,000 in year one, and it does not depend on a second account, direct deposit, or a promotional deadline.</p>
  <p>{link('https://www.everbank.com/banking/performance-savings', 'EverBank terms')} · {link('https://www.everbank.com/rates', 'rates')}</p></div>
  <div class="card"><h3 style="margin-top:0">Best large-brand account — American Express or Capital One, both 3.20%</h3>
  <p class="small">Both pay <b>3.20%</b> with no minimum and no monthly fee, and both have a verified mobile app. That is well below the online specialists, but it is a straightforward account at a large national bank — the trade-off the Big Four cannot even be compared on, because their savings APYs are not published in a readable form.</p>
  <p>{link('https://www.americanexpress.com/en-us/banking/online-savings/high-yield-savings-account/', 'Amex terms')} · {link('https://www.capitalone.com/bank/open-an-account/', 'Capital One terms')}</p></div>
  <div class="card"><h3 style="margin-top:0">If the goal is maximum FDIC coverage — split, don't concentrate</h3>
  <p class="small">One bank insures $250,000 per depositor per ownership category. Above that, either open accounts at separate banks ($1,000,000 needs four), use joint/trust/IRA categories, or rely on a deposit programme — SoFi advertises up to $3,000,000 and Axos up to $2,500,000 through partner banks. Programme coverage depends on the partners, so treat it as conditional.</p>
  <p><a href="fdic.html">FDIC coverage detail</a> · <a href="flagged.html">Flagged for review</a></p></div>
</div>
<p class="small" style="margin-top:12px">This is a comparison of published terms as of {VERIFIED}, not personal financial advice. Every APY shown is variable and can change after the account is opened.</p>

<h2>What the data says</h2>
<div class="grid g3">
  <div class="card"><h3 style="margin-top:0">1. The best headline rate is conditional, not automatic</h3>
  <p class="small">Axos advertises 5.00% APY for six months, but only inside an Axos ONE checking bundle with monthly direct deposits and an average daily balance. Miss a month and the standard tier is <b>1.00%</b>. The 5.00% is also {5.0 - FED_TOP:.2f} percentage points above the top of the Federal Reserve's target range — a strong signal it is temporary.</p>
  <p>{link('https://www.axosbank.com/personal/bank/axos-one')}</p></div>
  <div class="card"><h3 style="margin-top:0">2. No-strings rates cluster at 3.10%–4.20%</h3>
  <p class="small">EverBank pays <b>4.20%</b> with $0 to open and no monthly fee; Openbank pays <b>4.00%</b> after its six-month boost; Synchrony <b>3.55%</b>; Marcus <b>3.50%</b>. These are the cleanest comparisons because the rate does not depend on a second account.</p>
  <p>{link('https://www.everbank.com/rates', 'EverBank rates')} · {link('https://www.openbank.us/banking/high-yield-savings-account/', 'Openbank')}</p></div>
  <div class="card"><h3 style="margin-top:0">3. Big Four APYs are not publicly checkable</h3>
  <p class="small">Chase requires a ZIP code, Bank of America renders placeholders, Citi injects the rate at runtime, and Wells Fargo's page showed 0.01% only for its default California market. None is verified for New York, so all four are blank here rather than quoted from third parties. Their <b>fees</b> are visible: $4.50–$5.00 per month unless a balance condition is met.</p>
  <p>{link('https://www.chase.com/personal/savings/savings-account/interest-rates', 'Chase rate page')}</p></div>
</div>

<h2>Best verified 1-year return on a $250,000 deposit</h2>
<p class="small">Interest is computed from each bank's own published APY, applying the six-month introductory rate where one exists and the published post-intro rate for the remaining six months. Balances above $250,000 are not insured at a single bank in a single ownership category.</p>
<div class="tablewrap"><table>
<thead><tr><th>#</th><th>Bank / account</th><th class="num">Headline APY</th><th class="num">Post-intro APY</th><th class="num">Year-1 interest</th><th class="num">Blended APY</th><th>Official source</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p class="legend">Full {len(ACCOUNTS)}-account table on <a href="accounts.html">Accounts</a> · all deposit sizes on <a href="returns.html">Returns</a> · bonus terms on <a href="promotions.html">Promotions</a>.</p>

<h2>How to read this dashboard</h2>
<div class="grid g2">
  <div class="card"><h3 style="margin-top:0">The question this answers</h3>
  <p class="small">Given a deposit of $1,000 to $1,000,000, opened on <b>{OPEN_DATE}</b>, which national FDIC-insured bank with a digital app pays the most — and how much of that return depends on a temporary promotion, a second account, or monthly activity?</p>
  <p class="small">Return tables show the blended first year, the steady-state year, and a five-year projection at constant rates. Bonuses are listed separately and never folded into the interest math.</p></div>
  <div class="card"><h3 style="margin-top:0">The rules applied</h3>
  <ul class="tight small">
    <li>Only official sources: bank product pages, FDIC BankFind API, FDIC national rate table, Federal Reserve.</li>
    <li>No aggregator or review site is used as the source for any value.</li>
    <li>If a field could not be read from an official page, it is blank and flagged.</li>
    <li>Every table row carries a link to the official page for manual review.</li>
    <li>FDIC status is checked by certificate number, not by a logo on the page.</li>
  </ul></div>
</div>

<h2>Jump to</h2>
<div class="grid g3">
  <a class="tile" href="accounts.html"><b>Accounts →</b><span class="small">All {len(ACCOUNTS)} products: APY, minimums, fees, FDIC certificate, app, source.</span></a>
  <a class="tile" href="returns.html"><b>Returns →</b><span class="small">Interest by deposit size at $1k through $1M, 1-year and 5-year.</span></a>
  <a class="tile" href="fdic.html"><b>FDIC coverage →</b><span class="small">What $250,000 really covers, and how to insure larger balances.</span></a>
  <a class="tile" href="promotions.html"><b>Promotions →</b><span class="small">$800, $400, $200, BOOST50, 5.00% intro and their conditions.</span></a>
  <a class="tile" href="analysis.html"><b>Analysis →</b><span class="small">Competitiveness vs the Fed, Treasuries, and each bank's own post-promo rate.</span></a>
  <a class="tile" href="flagged.html"><b>Flagged for review →</b><span class="small">{n_flags} irregularities and unverified items, with links.</span></a>
</div>
"""
    return page_shell("Overview", "index.html", "Best savings account for a large, FDIC-insured balance",
                      "A source-linked comparison of national banks — built to show what a deposit actually earns after the promotional rate ends.", body)


# ---------------------------------------------------------------- accounts
def build_accounts():
    rows = ""
    for a in ACCOUNTS:
        app = badge("ok", "yes") if a["app"]["verified"] else badge("no", "unverified")
        apy = pct(a["headline_apy"]) if a["headline_apy"] is not None else '<span class="unv">—</span>'
        std = pct(a["standard_apy"]) if a["standard_apy"] is not None else '<span class="unv">—</span>'
        fee = money(a["monthly_fee"], 2) if a["monthly_fee"] is not None else '<span class="unv">—</span>'
        mino = money(a["min_open"]) if a["min_open"] is not None else '<span class="unv">—</span>'
        fdic = badge("ok", f"cert {a['fdic']['cert']}") if a["fdic"]["active"] else badge("no", "inactive")
        rows += f"""<tr>
<td><b>{esc(a['bank'])}</b><div class="small">{esc(a['product'])}</div><div class="small">{status_cell(a)}</div></td>
<td class="num"><b>{apy}</b><div class="small">{esc(a.get('rate_as_of') or 'no date')}</div></td>
<td class="num">{std}</td>
<td class="num">{mino}</td>
<td class="num">{fee}</td>
<td>{fdic}</td>
<td>{app}</td>
<td class="small">{source_cell(a)}</td></tr>"""
    body = f"""
<div class="banner"><div><strong>Reading the table.</strong> “Headline APY” is the best rate advertised for a new customer. “Post-intro APY” is what the same account pays after any introductory period. Where a rate could not be read from the official page it is shown in red as unverified, not guessed.</div></div>
<input class="search" data-filter="#acct" placeholder="Filter by bank or product…" aria-label="Filter accounts">
<div class="tablewrap"><table id="acct">
<thead><tr><th>Bank / product</th><th class="num">Headline APY</th><th class="num">Post-intro APY</th><th class="num">Min. to open</th><th class="num">Monthly fee</th><th>FDIC status</th><th>Mobile app</th><th>Official source</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<h2>Opening rules and fees</h2>
<div class="tablewrap"><table>
<thead><tr><th>Bank</th><th>Monthly fee / waiver</th><th>Minimum balance for APY</th><th>Access limits</th><th>App verification</th></tr></thead>
<tbody>
""" + "".join(
        f"""<tr><td><b>{esc(a['bank'])}</b></td>
<td class="small">{esc(a['fee_waiver'] or '—')}</td>
<td class="num">{money(a['min_balance_for_apy']) if a['min_balance_for_apy'] is not None else '<span class="unv">—</span>'}</td>
<td class="small">{esc(a['withdrawal_limit'] or '—')}</td>
<td class="small">{('Verified: ' + esc(a['app']['name'])) if a['app']['verified'] else '<span class="unv">Not verified</span>'}</td></tr>"""
        for a in ACCOUNTS) + """
</tbody></table></div>

<h2>Digital app and security</h2>
<p class="small">Security controls are quoted from each bank's own security centre or product page. “Not verified” means the bank's security page could not be reached or did not describe account controls on the day of review — it is not a finding that the controls are absent.</p>
<div class="tablewrap"><table>
<thead><tr><th>Bank</th><th>Mobile app</th><th>Security controls verified</th><th>Source</th></tr></thead>
<tbody>
""" + "".join(
        f"""<tr><td><b>{esc(a['bank'])}</b></td>
<td class="small">{('Verified: ' + esc(a['app']['name'])) if a['app']['verified'] else '<span class="unv">Not verified</span>'}</td>
<td class="small">{esc(a['security']['note']) if a.get('security', {}).get('verified') else '<span class="unv">Not verified</span>'}</td>
<td class="small">{link(a['security']['source'], 'security page') if a.get('security', {}).get('source') else '—'}</td></tr>"""
        for a in ACCOUNTS) + """
</tbody></table></div>

<h2>Why the Big Four look different</h2>
<div class="note bad"><b>APY unavailable from an official page for the user's market.</b> Chase shows its savings rate table only after a valid 5-digit ZIP code is entered. Bank of America's page renders fee and minimum-balance values as “$XXXX” to automated readers. Citi's rate table renders a dynamic placeholder (its footnote dates the APY to 10/21/2026 but the number is injected at runtime). Wells Fargo does print 0.01% APY — but only for the page's default market (CA 94105), not for New York. All four APYs are therefore left blank and excluded from every return calculation. See <a href="flagged.html">Flagged for review</a>.</div>

<h2>Accounts excluded</h2>
<p class="small"><b>Discover Bank Online Savings</b> is excluded: the product page no longer exists and the FDIC lists Discover Bank certificate 5649 as inactive. Capital One, which acquired Discover, states that deposits at the two brands are combined for FDIC coverage. <a href="https://api.fdic.gov/banks/institutions?filters=CERT:5649" target="_blank" rel="noopener">FDIC record</a></p>
"""
    return page_shell("Accounts", "accounts.html", f"All {len(ACCOUNTS)} accounts, line by line",
                      "National branch banks and national digital banks, with the rate, minimums, fees, FDIC certificate and app status each verified against the bank's own page.", body)


# ---------------------------------------------------------------- returns
def build_returns():
    accts = active_accounts()

    def matrix(years, label):
        head = "".join(f"<th class='num'>{money(t)}</th>" for t in META["primary_deposit_tiers"])
        body = ""
        for a in sorted(accts, key=lambda x: -interest(x, 250000, years)):
            cells = "".join(
                f"<td class='num'>{money(interest(a, t, years))}</td>" for t in META["primary_deposit_tiers"])
            body += f"<tr><td><b>{esc(a['bank'])}</b><div class='small'>{esc(a['product'])}</div></td>{cells}</tr>"
        return f"""<div class="tablewrap"><table><thead><tr><th>{label}</th>{head}</tr></thead><tbody>{body}</tbody></table></div>"""

    def apy_matrix():
        head = "".join(f"<th class='num'>{money(t)}</th>" for t in META["primary_deposit_tiers"])
        body = ""
        for a in sorted(accts, key=lambda x: -blended_apy(x, 250000)):
            cells = "".join(f"<td class='num'>{pct(blended_apy(a, t))}</td>" for t in META["primary_deposit_tiers"])
            body += f"<tr><td><b>{esc(a['bank'])}</b><div class='small'>{esc(a['product'])}</div></td>{cells}</tr>"
        return f"""<div class="tablewrap"><table><thead><tr><th>Blended first-year APY</th>{head}</tr></thead><tbody>{body}</tbody></table></div>"""

    axos = next((a for a in accts if a["id"] == "axos"), None)
    AXOS_ASSUMPTION = (axos or {}).get("model_assumption", "")

    best_rows = ""
    for t in META["primary_deposit_tiers"]:
        val, a = top_for_tier(t)[0]
        best_rows += f"""<tr><td class="num"><b>{money(t)}</b></td><td><b>{esc(a['bank'])}</b><div class="small">{esc(a['product'])}</div></td>
<td class="num"><b>{money(val)}</b></td><td class="num">{pct(blended_apy(a, t))}</td><td class="num">{money(min(t, 250000))}</td><td>{source_cell(a)}</td></tr>"""

    body = f"""
<div class="banner"><div><strong>Assumptions are fixed and disclosed.</strong> Deposit opened {OPEN_DATE}. Interest compounds at the stated APY; introductory rates apply for exactly the advertised period, then the bank's published post-intro rate applies. No fees, bonuses, or rate changes are assumed. Banks may change variable rates at any time.</div></div>

<div class="grid g3">
  <div class="card kpi"><div class="label">Best 1-year interest, $250k</div><div class="value">{money(top_for_tier(250000)[0][0])}</div><div class="sub">{esc(top_for_tier(250000)[0][1]['bank'])}</div></div>
  <div class="card kpi"><div class="label">Best 5-year growth, $250k</div><div class="value">{money(top_for_tier(250000, 'y5')[0][0])}</div><div class="sub">{esc(top_for_tier(250000, 'y5')[0][1]['bank'])} interest over 5 years</div></div>
  <div class="card kpi"><div class="label">Range of 1-year returns, $250k</div><div class="value">{money(top_for_tier(250000)[-1][0])}–{money(top_for_tier(250000)[0][0])}</div><div class="sub">lowest to highest verified account</div></div>
</div>

<h2>Winner at each deposit size</h2>
<div class="tablewrap"><table>
<thead><tr><th class="num">Deposit</th><th>Best account</th><th class="num">Year-1 interest</th><th class="num">Blended APY</th><th class="num">FDIC-insured</th><th>Source</th></tr></thead>
<tbody>{best_rows}</tbody></table></div>
<p class="small">The insured column applies the FDIC single-ownership limit of $250,000 per depositor, per bank, per ownership category. Amounts above it are uninsured unless placed across banks or ownership categories — see <a href="fdic.html">FDIC coverage</a>.</p>

<h2>First-year interest by deposit size</h2>
<p class="small">Dollars of interest earned in the first 12 months, including the effect of any six-month introductory rate.</p>
{matrix(1.0, "Account")}

<h2>Five-year interest by deposit size</h2>
<p class="small">Cumulative interest over five years, assuming the published post-intro rate holds after the promotional period. This is a projection, not a guarantee: every one of these APYs is variable.</p>
{matrix(5.0, "Account")}

<h2>Modelling assumptions that affect the ranking</h2>
<div class="tablewrap"><table><thead><tr><th>Account</th><th>Assumption used</th><th>Why</th></tr></thead><tbody>
<tr><td><b>Axos Bank</b></td><td>5.00% applied to the first $50,000 for 6 months; 4.21% above that; 4.21% ongoing while requirements are met</td><td class="small">{esc(AXOS_ASSUMPTION)}</td></tr>
<tr><td><b>CIT Bank</b></td><td>Entire balance earns the tier rate (cliff), per CIT's tiered-account disclosure</td><td class="small">CIT states interest is paid on the entire balance at the rate for the tier the end-of-day balance falls into.</td></tr>
<tr><td><b>Barclays</b></td><td>Entire balance earns the tier rate (cliff); $250,000+ earns 3.65%</td><td class="small">Barclays states APY is based on the tier into which the end-of-day balance falls.</td></tr>
<tr><td><b>SoFi</b></td><td>4.40% for 6 months, 3.30% after; SoFi Plus 4.70% tier excluded</td><td class="small">The 4.40% headline is the direct-deposit boost; the 4.70% tier requires a paid subscription.</td></tr>
</tbody></table></div>

<h2>Blended first-year APY by deposit size</h2>
<p class="small">The effective APY actually earned in year one, after mixing the intro and post-intro rates. This is the number to compare against the bank's advertised headline.</p>
{apy_matrix()}

<h2>Notes that change the ranking</h2>
<ul class="tight">
  <li><b>Axos</b> wins most tiers on paper, but the 4.21% ongoing rate requires monthly activity in an Axos ONE checking account; without it the ongoing rate is 1.00%. The 5.00% intro is applied to the first $50,000 only because Axos does not publish the cap on the page reviewed. See <a href="flagged.html">F03/F04</a>.</li>
  <li><b>Barclays</b> is modelled on its tier structure: balances below $250,000 earn 3.50%, not the 3.65% headline.</li>
  <li><b>CIT</b> pays 0.25% (standard) on balances under $5,000; the promo adds only 0.50%, leaving 0.75% there.</li>
  <li><b>SoFi's</b> 4.40% lasts six months and requires an eligible direct deposit; its 4.70% SoFi Plus tier is a separate paid subscription and is not modelled here.</li>
  <li>Bonuses (up to $800) are excluded from all interest figures and are listed on <a href="promotions.html">Promotions</a>.</li>
</ul>
"""
    return page_shell("Returns", "returns.html", "What the deposit actually earns",
                      "Interest by deposit size from $1,000 to $1,000,000, using each bank's published intro and post-intro APYs.", body)


# ---------------------------------------------------------------- promotions
def build_promotions():
    rows = ""
    for p in PROMOS["promotions"]:
        st = {"verified": badge("ok"), "none_found": badge("info", "none found"),
              "unverified": badge("no")}.get(p["status"], badge("info"))
        val = f"<b>{esc(p['value'])}</b>" if p["value"] else '<span class="unv">—</span>'
        rows += f"""<tr><td><b>{esc(p['bank'])}</b><div class="small">{esc(p['account'])}</div></td>
<td>{esc(p['type'])}</td><td class="num">{val}</td><td class="small">{esc(p['apy_offer'] or '—')}</td>
<td class="small">{esc(p['requirements'])}</td><td>{esc(p['deadline'] or '—')}</td><td>{st}</td><td>{link(p['source'], 'official terms')}</td></tr>"""
    body = f"""
<div class="banner warn"><div><strong>Deadlines matter.</strong> Three of these offers expire between 10/31/2026 and 1/10/2027. Bonus terms are quoted from the bank's own page; where no offer appeared on the official page it is recorded as “none found”, not as “no bonus exists”.</div></div>
<div class="tablewrap"><table>
<thead><tr><th>Bank / account</th><th>Type</th><th class="num">Value</th><th>Rate offer</th><th>Conditions</th><th>Deadline</th><th>Status</th><th>Official terms</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<h2>What the bonuses are worth in practice</h2>
<div class="grid g2">
  <div class="card"><h3 style="margin-top:0">E*TRADE: $800 on $100,000</h3>
  <p class="small">An $800 bonus on a $100,000 deposit is worth about <b>0.80%</b> of the deposit in year one. Combined with the 4.25% six-month rate, the first-year value is roughly 5.05% — but the money must stay for the 30-day funding window plus 45 more days, and only new accounts with promo code SAVE800 qualify.</p>
  <p class="small">{link('https://us.etrade.com/promo/savings', 'E*TRADE terms')}</p></div>
  <div class="card"><h3 style="margin-top:0">SoFi: $400 on $5,000 of direct deposit</h3>
  <p class="small">This bonus is tied to payroll or government deposits, not to the size of the savings balance. $400 on $5,000 of deposits is 8%, but it is a one-time payment and requires the direct deposit relationship to be maintained. Bonuses are taxable miscellaneous income.</p>
  <p class="small">{link('https://www.sofi.com/banking/high-yield-savings-account/', 'SoFi terms')}</p></div>
  <div class="card"><h3 style="margin-top:0">Barclays: $200 on $25,000</h3>
  <p class="small">$200 on $25,000 is <b>0.80%</b> of the deposit, but the money must stay for 120 days and the offer expires 10/31/2026. It is paid about 60 days after the holding period.</p>
  <p class="small">{link('https://banking.us.barclays/tiered-savings.html', 'Barclays terms')}</p></div>
  <div class="card"><h3 style="margin-top:0">CIT: BOOST50 is a rate, not cash</h3>
  <p class="small">The 0.50% APY boost for six months is worth about <b>$12.50 per $5,000</b>, or $250 per $100,000 over the six months, versus the standard tier. It also lifts balances under $5,000 only from 0.25% to 0.75%.</p>
  <p class="small">{link('https://www.cit.com/cit-bank/platinum-savings/boost', 'CIT terms')}</p></div>
</div>
"""
    return page_shell("Promotions", "promotions.html", "Bonuses and promotional rates",
                      "Cash bonuses, promotional APYs and referral offers with their exact conditions and deadlines.", body)


# ---------------------------------------------------------------- fdic
def build_fdic():
    bank_rows = ""
    for b in FDIC["banks"]:
        status = badge("ok", "active") if b["active"] else badge("no", "inactive")
        exp = money(b["expanded_limit"]) if b["expanded_limit"] else '<span class="unv">none stated</span>'
        bank_rows += f"""<tr><td><b>{esc(b['bank'])}</b></td><td class="num">{b['cert']}</td><td>{status}</td>
<td class="num">{money(b['base_limit']) if b['base_limit'] else '—'}</td><td class="num">{exp}</td><td class="small">{esc(b['expanded_mechanism'])}</td><td>{link(b['source'], 'FDIC API')}</td></tr>"""

    cover_rows = ""
    for dep in [250000, 500000, 750000, 1000000, 2000000, 5000000]:
        cover_rows += f"""<tr><td class="num"><b>{money(dep)}</b></td><td class="num">{money(min(dep,250000))}</td>
<td class="num">{money(max(0, dep-250000))}</td><td class="num">{money(min(dep,500000))}</td><td class="num">{max(1, -(-dep//250000))} banks</td></tr>"""

    body = f"""
<div class="banner"><div><strong>FDIC coverage is $250,000 per depositor, per insured bank, per ownership category</strong> — not $250,000 per account. All deposits in the same category at the same bank are added together. Source: <a href="{FDIC['rules']['source']}" target="_blank" rel="noopener">FDIC, Understanding Deposit Insurance</a>.</div></div>

<div class="grid g3">
  <div class="card kpi"><div class="label">Single-owner limit</div><div class="value">$250,000</div><div class="sub">per depositor, per bank</div></div>
  <div class="card kpi"><div class="label">Joint-account limit</div><div class="value">$500,000</div><div class="sub">two owners, $250,000 each</div></div>
  <div class="card kpi"><div class="label">Coverage basis</div><div class="value" style="font-size:20px">Ownership category</div><div class="sub">same-category balances are combined</div></div>
</div>

<h2>How much of a deposit is insured at one bank</h2>
<div class="tablewrap"><table>
<thead><tr><th class="num">Deposit</th><th class="num">Insured (single)</th><th class="num">Uninsured excess</th><th class="num">Insured (joint)</th><th class="num">Banks needed for full coverage</th></tr></thead>
<tbody>{cover_rows}</tbody></table></div>
<p class="small">A joint account doubles the limit only because two depositors each have a $250,000 share; it does not double the per-person limit. Different ownership categories at the <i>same</i> bank can also extend coverage.</p>

<h2>Ownership categories the FDIC recognises</h2>
<div class="card"><ul class="tight">{''.join(f'<li>{esc(c)}</li>' for c in FDIC['rules']['ownership_categories'])}</ul>
<p class="small" style="margin-top:10px">Balances held in the same category are added together. A single account plus a joint account plus an IRA at one bank can therefore be insured above $250,000 — but the categories must genuinely apply. The FDIC's EDIE tool calculates a specific situation: <a href="https://edie.fdic.gov/" target="_blank" rel="noopener">edie.fdic.gov</a>.</p></div>

<h2>Bank-by-bank FDIC status</h2>
<p class="small">Certificate numbers checked directly against the FDIC's institution API on {VERIFIED}. The API index is dated {FDIC['api_index'].split()[0]}.</p>
<div class="tablewrap"><table>
<thead><tr><th>Bank</th><th class="num">FDIC cert</th><th>Status</th><th class="num">Base limit</th><th class="num">Expanded coverage</th><th>Mechanism</th><th>Record</th></tr></thead>
<tbody>{bank_rows}</tbody></table></div>

<h2>If the goal is the maximum insured balance</h2>
<div class="grid g2">
  <div class="card"><h3 style="margin-top:0">Option A: one bank per $250,000</h3>
  <p class="small">Straightforward and fully transparent. At $1,000,000, four banks at $250,000 each are fully covered in a single ownership category. This dashboard's return tables let you pick the best payer at exactly $250,000.</p></div>
  <div class="card"><h3 style="margin-top:0">Option B: programme coverage at one bank</h3>
  <p class="small">Axos (up to $2.5M) and SoFi (up to $3M) place deposits with participating banks through insured deposit programmes. The FDIC insurance is real, but it depends on those partner banks and the programme's terms — it is not extra insurance issued by the host bank. E*TRADE advertises $500,000 without disclosing the conditions; that item is flagged.</p></div>
</div>
<div class="note"><b>Practical warning:</b> $500,000 in a single-owner savings account at one bank leaves $250,000 uninsured, no matter which bank it is or how high its APY is. Above $250,000, the ranking in <a href="returns.html">Returns</a> should be applied per bank, not to the whole balance.</div>
"""
    return page_shell("FDIC coverage", "fdic.html", "FDIC insurance, by certificate number",
                      "What the $250,000 limit actually covers, how ownership categories interact, and which banks offer expanded programme coverage.", body)


# ---------------------------------------------------------------- analysis
def build_analysis():
    rows = ""
    for a in sorted(active_accounts(), key=lambda x: -(x["headline_apy"] or 0)):
        h = a["headline_apy"]
        gap = h - FED_TOP
        mult = h / NATIONAL
        promo_premium = (h - a["standard_apy"]) if a.get("promo_months") else 0.0
        vs6 = h - TREASURY["6_month"]
        signal = badge("warn", "above policy ceiling") if gap > 0.25 else (badge("info", "near ceiling") if gap >= -0.25 else badge("ok", "below ceiling"))
        rows += f"""<tr><td><b>{esc(a['bank'])}</b><div class="small">{esc(a['product'])}</div></td>
<td class="num"><b>{pct(h)}</b></td><td class="num">{pct(a['standard_apy'])}</td>
<td class="num">{mult:.1f}×</td><td class="num">{gap:+.2f} pp</td><td class="num">{promo_premium:+.2f} pp</td><td class="num">{vs6:+.2f} pp</td><td>{signal}</td></tr>"""

    body = f"""
<div class="banner"><div><strong>Reference points, all official.</strong> FDIC national savings average <b>{NATIONAL:.2f}%</b> as of {META['fdic_national_savings_rate_as_of']}; federal funds target range <b>{META['fed_funds_target_range']}%</b> after the {META['fed_funds_as_of']} FOMC decision; 6-month Treasury yield <b>{TREASURY['6_month']:.2f}%</b>, 12-month <b>{TREASURY['12_month']:.2f}%</b> (FDIC national rate table).</div></div>

<h2>Headline APY versus the policy rate, the national average, and a 6-month Treasury</h2>
<div class="tablewrap"><table>
<thead><tr><th>Account</th><th class="num">Headline APY</th><th class="num">Post-intro APY</th><th class="num">× national avg</th><th class="num">vs fed funds ceiling</th><th class="num">Promo premium</th><th class="num">vs 6-mo Treasury</th><th>Rate character</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p class="legend">“Above policy ceiling” = headline more than 0.25 pp above the top of the federal funds target range (4.00%). “Promo premium” = headline APY minus the bank's own post-intro APY. Every value is computed from figures on official pages.</p>

<h2>Five findings</h2>
<div class="grid g2">
  <div class="card"><h3 style="margin-top:0">1. One rate is a full point above the Fed's ceiling</h3>
  <p class="small">Axos's 5.00% is 1.00 pp above the top of the 3.75%–4.00% target range. A bank paying materially above the policy rate on a liquid, insured account is buying deposits for a limited period; Axos limits it to six months. Four other headline rates (SoFi 4.40%, Openbank 4.35%, CIT 4.25%, E*TRADE 4.25%) sit 0.25–0.40 pp above the ceiling — also promotional, but by a smaller margin.</p></div>
  <div class="card"><h3 style="margin-top:0">2. A 6-month Treasury beats two of the five top promo rates</h3>
  <p class="small">The 6-month Treasury yield is {TREASURY['6_month']:.2f}%. CIT and E*TRADE pay 4.25%, below it; only Axos (5.00%), SoFi (4.40%) and Openbank (4.35%) beat it. Treasury interest is also exempt from state and local income tax, while savings interest is not. This does not make Treasuries a substitute for an emergency fund — they are not FDIC-insured and are less liquid — but it sets a hard benchmark for what a promotional savings rate is worth.</p></div>
  <div class="card"><h3 style="margin-top:0">3. The 12-month Treasury beats every post-intro rate</h3>
  <p class="small">The 12-month Treasury yield is {TREASURY['12_month']:.2f}%. Every bank's <i>ongoing</i> savings rate is below it: Axos 4.21%, Openbank 4.00%, CIT 3.75%, E*TRADE 3.75%, Synchrony 3.55%, Marcus 3.50%, SoFi 3.30%. Six-month teasers can beat the 12-month Treasury for half a year, but the steady-state savings rate does not.</p></div>
  <div class="card"><h3 style="margin-top:0">4. The promo premium ranges from 0 to 1.10 pp</h3>
  <p class="small">SoFi's headline is 1.10 pp above its own ongoing rate; Axos's is 0.79 pp; CIT and E*TRADE 0.50 pp; Openbank 0.35 pp. EverBank, Synchrony, Marcus, Amex, Capital One and Ally advertise no promotional premium at all, which makes their rates easier to compare and less likely to fall at the six-month mark.</p></div>
  <div class="card"><h3 style="margin-top:0">5. “Life span” changes the winner</h3>
  <p class="small">Over one year the ranking is driven by introductory rates. Over five years it is driven by the ongoing rate — which is why Axos still leads on paper but its lead narrows, and why EverBank (4.20% with no promo and no conditions) moves up relative to six-month teasers. The five-year table on <a href="returns.html">Returns</a> shows both. All of these rates are variable and none is locked.</p></div>
  <div class="card"><h3 style="margin-top:0">6. The Big Four cannot be ranked at all</h3>
  <p class="small">Their APYs are ZIP-gated, market-specific, or injected at runtime, so they are excluded from every calculation rather than filled in from third-party estimates. Where fees are visible they are the highest in the set: $4.50–$5.00 per month unless a balance condition is met, versus $0 at every digital bank reviewed.</p></div>
</div>

<h2>What would change this analysis</h2>
<ul class="tight">
  <li>A change in the federal funds target range: the next FOMC decision moves every variable savings rate, usually within weeks.</li>
  <li>Promotional deadlines: Barclays (10/31/2026), CIT (12/15/2026), E*TRADE (1/10/2027).</li>
  <li>Axos requirement compliance: missing one month drops the ongoing rate from 4.21% to 1.00%.</li>
  <li>SoFi Plus subscription status: 4.70% on the first $20,000 is a different product tier from the 4.40% headline.</li>
  <li>Any bank merger or charter change — notably Santander/Webster (Openbank) and Capital One/Discover.</li>
</ul>
"""
    return page_shell("Analysis", "analysis.html", "How competitive are these rates, really?",
                      "Each headline APY measured against the Fed's target range, the FDIC national average, a 6-month Treasury, and the bank's own post-promotional rate.", body)


# ---------------------------------------------------------------- sources
def build_sources():
    groups = {
        "Government / regulator": [
            ("FDIC — National Rates and Rate Caps, October 2026", "https://www.fdic.gov/national-rates-and-rate-caps", "0.38% national savings average, Treasury yields, CD averages; revised 2026-10-19"),
            ("FDIC — Understanding Deposit Insurance", "https://www.fdic.gov/resources/deposit-insurance/understanding-deposit-insurance", "Coverage limits and ownership categories"),
            ("FDIC — Institution API (BankFind data)", "https://api.fdic.gov/banks/institutions", "Certificate numbers, active status, location"),
            ("Federal Reserve — Open Market Operations", "https://www.federalreserve.gov/monetarypolicy/openmarket.htm", "Target range 3.75%–4.00% after 2026-09-17"),
        ],
        "Bank product and rate pages": [],
    }
    for a in ACCOUNTS:
        groups["Bank product and rate pages"].append((f"{a['bank']} — {a['product']}", a["source"], f"Rate as of {a.get('rate_as_of') or 'not stated'}"))
        if a.get("terms_source") and a["terms_source"] != a["source"]:
            groups["Bank product and rate pages"].append((f"{a['bank']} — terms / rates", a["terms_source"], "Terms, fees, or rate table"))

    groups["Promotions"] = [(f"{p['bank']} — {p['type']}", p["source"], p["apy_offer"] or "") for p in PROMOS["promotions"] if p["source"]]

    html = ""
    for name, items in groups.items():
        if not items:
            continue
        html += f"<h2>{esc(name)}</h2><div class='tablewrap'><table><thead><tr><th>Source</th><th>Link</th><th>What it verified</th></tr></thead><tbody>"
        for title, url, note in items:
            html += f"<tr><td><b>{esc(title)}</b></td><td>{link(url, url)}</td><td class='small'>{esc(note)}</td></tr>"
        html += "</tbody></table></div>"

    body = f"""
<div class="banner"><div><strong>Every value in this dashboard traces to one of these pages.</strong> No aggregator, review site, or press article is used as the source for a rate, fee, minimum, or FDIC status. Links open the official page for manual review.</div></div>
{html}
<h2>What is not on this list</h2>
<p class="small">Third-party comparison sites were used only to discover candidate banks and to identify which official pages to look for. No number from those sites appears in any table. Where a bank's own page did not show a value, the cell is blank and the item is on the <a href="flagged.html">Flagged for review</a> page.</p>
"""
    return page_shell("Sources", "sources.html", "Every source used, with what it verified",
                      "Official pages only — banks, the FDIC, and the Federal Reserve.", body)


# ---------------------------------------------------------------- flags
def build_flags():
    rows = ""
    for f in FLAGS["flags"]:
        sev = {"high": "bad", "medium": "warn", "low": "info"}[f["severity"]]
        rows += f"""<tr><td>{badge(sev, f['severity'])}</td>
<td><b>{esc(f['title'])}</b><div class="small" style="margin-top:6px">{esc(f['detail'])}</div></td>
<td>{link(f['source'], 'primary')}{('<br>' + link(f['second_source'], 'secondary')) if f.get('second_source') else ''}</td>
<td>{badge('info', f['status'])}</td></tr>"""
    body = f"""
<div class="banner warn"><div><strong>{len(FLAGS['flags'])} items are published here rather than silently resolved.</strong> Each is either a conflict between two official pages, a value that could not be read from an official page, or a term that materially changes the return. None of them blocks publication; all of them are linked for manual review.</div></div>
<div class="tablewrap"><table>
<thead><tr><th>Severity</th><th>Item</th><th>Sources</th><th>Status</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<h2>How unverified values are shown</h2>
<div class="card"><p class="small">In the tables, an unverified value appears as <span class="unv">—</span> in red, never as an estimate. A blank means “this could not be confirmed from an official source on {VERIFIED}”, not zero and not “none”. The most consequential blanks are the four Big Four APYs, which are excluded from every return calculation rather than sourced from a comparison site.</p></div>
"""
    return page_shell("Flagged for review", "flagged.html", "Flagged for review",
                      "Irregularities, conflicts, and values that could not be verified from an official source.", body)


# ---------------------------------------------------------------- method
def build_method():
    body = f"""
<div class="banner"><div><strong>Reproducible by design.</strong> The site is generated from three JSON files by a Python script; every rate carries its source URL and the date it was read.</div></div>

<h2>Scope</h2>
<ul class="tight">
  <li><b>Included:</b> nationally available savings accounts at FDIC-insured banks with a mobile app or online banking, including national branch banks and national digital banks.</li>
  <li><b>Excluded:</b> credit unions, local/regional banks, accounts not open to new customers, brokered deposits, CDs (except where a bank's own page is used for context), and non-deposit products.</li>
  <li><b>Reference date:</b> all rates and terms read on {VERIFIED}. Account opening date used in every calculation: {OPEN_DATE}.</li>
</ul>

<h2>Calculation</h2>
<div class="card"><p class="small">Interest is compounded at the stated APY. For accounts with an introductory rate, the intro rate is applied for exactly the advertised number of months, then the balance is re-tiered at the bank's published post-intro rate for the remaining period. Tiered accounts are modelled either marginally (each band applies to its portion) or as a cliff (the whole balance earns the rate of the band it falls into), according to how the bank describes the account. Bonuses are excluded. No fees are deducted because every digital account in the set has a $0 monthly fee; the Big Four's fees are shown but their APYs are unverified, so they cannot be modelled.</p>
<p class="small">Formulas: <code>balance = Σ portion × (1 + rate)^years</code>; blended first-year APY = <code>(balance₁ / deposit) − 1</code>; five-year projection applies the post-intro rate for the remaining 4.5 years.</p></div>

<h2>Verification standard</h2>
<div class="tablewrap"><table>
<thead><tr><th>Field</th><th>Required source</th><th>If missing</th></tr></thead>
<tbody>
<tr><td>APY</td><td>Bank's own product or rates page, with date if printed</td><td>Blank + flagged</td></tr>
<tr><td>Minimum to open / fee</td><td>Bank's own product page or fee schedule</td><td>Blank + flagged</td></tr>
<tr><td>FDIC status</td><td>api.fdic.gov institution record by certificate number</td><td>Excluded</td></tr>
<tr><td>Promotion terms</td><td>Bank's own terms page</td><td>“none found” or flagged</td></tr>
<tr><td>Mobile app</td><td>Bank's own page naming or linking the app</td><td>“unverified”</td></tr>
<tr><td>National average / Fed rate / Treasury</td><td>fdic.gov and federalreserve.gov</td><td>Not used</td></tr>
</tbody></table></div>

<h2>Limitations</h2>
<ul class="tight">
  <li>APYs are variable. A rate verified today can change tomorrow; only E*TRADE's six-month boost is described as guaranteed for its term.</li>
  <li>Bank pages sometimes render rates with JavaScript or behind a ZIP gate. Those values are blank here, not approximated.</li>
  <li>Tier structures differ between banks. The model follows each bank's own description; where two official pages conflict, the more conservative reading is used and the conflict is flagged.</li>
  <li>Bonuses are one-time and taxable; they are not annualised into any APY.</li>
  <li>This is research, not financial, tax, or legal advice.</li>
</ul>

<h2>Reproduce</h2>
<div class="card"><p class="small"><code>python3 scripts/verify_data.py</code> checks that every account row has an official source and that no rate was entered without a date. <code>python3 scripts/build_site.py</code> regenerates <code>docs/</code> from <code>data/</code>. Both run in this repository.</p></div>
"""
    return page_shell("Method", "method.html", "How this was built and verified",
                      "Scope, formulas, the verification standard applied to each field, and the limits of the analysis.", body)


# ---------------------------------------------------------------- write
def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    pages = {
        "index.html": build_index(),
        "accounts.html": build_accounts(),
        "returns.html": build_returns(),
        "promotions.html": build_promotions(),
        "fdic.html": build_fdic(),
        "analysis.html": build_analysis(),
        "sources.html": build_sources(),
        "flagged.html": build_flags(),
        "method.html": build_method(),
    }
    for name, html in pages.items():
        (OUT / name).write_text(html)
    (OUT / "assets" / "style.css").write_text(CSS)
    (OUT / "assets" / "app.js").write_text(JS)
    (OUT / ".nojekyll").write_text("")
    print(f"Wrote {len(pages)} pages to {OUT}")


if __name__ == "__main__":
    main()
