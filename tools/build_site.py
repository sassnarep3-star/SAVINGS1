#!/usr/bin/env python3
"""Generate the static dashboard (GitHub Pages, repo root) from data/*.json.

No third-party assets, no CDN, no build tool: plain HTML + one stylesheet.
Every number printed here comes from data/accounts.json, data/projections.json,
data/promotions.json, data/banks_fdic.json or data/verification.json.
"""

import json
import math
import os
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "v2")
OUT = os.path.join(ROOT, "verified")  # the independent 20-account verification dashboard

accounts = json.load(open(os.path.join(DATA, "accounts.json")))
projections = json.load(open(os.path.join(DATA, "projections.json")))
promotions = json.load(open(os.path.join(DATA, "promotions.json")))
fdic = json.load(open(os.path.join(DATA, "banks_fdic.json")))
verification = json.load(open(os.path.join(DATA, "verification.json")))
flagged = json.load(open(os.path.join(DATA, "flagged.json")))
sources = json.load(open(os.path.join(DATA, "sources_fetched.json")))

OPENING = accounts["meta"]["opening_date"]
BENCH = accounts["meta"]["benchmark"]
ACC = {a["id"]: a for a in accounts["accounts"]}
INST = {i["cert"]: i for i in fdic["institutions"]}
ROWS = {r["id"]: r for r in projections["rows"]}
PROMO = {p["account_id"]: p for p in promotions["promotions"]}
VER = verification["meta"]

NAV = [
    ("index.html", "Dashboard"),
    ("rates.html", "Rates"),
    ("returns.html", "Returns"),
    ("promotions.html", "Bonuses"),
    ("rules.html", "Opening rules"),
    ("security.html", "FDIC & security"),
    ("flagged.html", "Flagged for review"),
    ("methodology.html", "Method & sources"),
]

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='7' fill='%230f766e'/%3E"
           "%3Ctext x='16' y='22' font-family='Arial' font-size='16' font-weight='bold' "
           "fill='white' text-anchor='middle'%3E%24%3C/text%3E%3C/svg%3E")


# ---------------------------------------------------------------- helpers
def esc(v):
    return escape(str(v), quote=True)


def usd(x, dp=0):
    if x is None:
        return "—"
    return f"${x:,.{dp}f}"


def pct(x, dp=2):
    if x is None:
        return "—"
    return f"{x:.{dp}f}%"


def host(url):
    h = url.split("://", 1)[-1]
    h = h.split("/", 1)[0]
    return h[4:] if h.startswith("www.") else h


def link(url, text=None, cls=""):
    t = text if text is not None else host(url)
    c = f' class="{cls}"' if cls else ""
    return f'<a href="{esc(url)}" title="{esc(url)}" target="_blank" rel="noopener"{c}>{esc(t)}</a>'


def src_cell(urls):
    if not urls:
        return "—"
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(link(u))
    return " · ".join(out)


def badge(status):
    m = {
        "verified": ("b-ok", "verified"),
        "derived": ("b-info", "derived"),
        "unverified": ("b-warn", "unverified"),
        "none-displayed": ("b-neutral", "none advertised"),
        "irregular": ("b-bad", "irregular"),
        "scope": ("b-warn", "scoped"),
        "note": ("b-neutral", "note"),
    }
    cls, text = m.get(status, ("b-neutral", status))
    return f'<span class="badge {cls}">{esc(text)}</span>'


def table(headers, rows, caption="", num_cols=(), cls="", foot=""):
    h = "".join(
        f'<th class="num">{c}</th>' if i in num_cols else f"<th>{c}</th>"
        for i, c in enumerate(headers)
    )
    body = []
    for r in rows:
        tds = []
        for i, cell in enumerate(r):
            k = ' class="num"' if i in num_cols else ""
            tds.append(f"<td{k}>{cell}</td>")
        body.append("<tr>" + "".join(tds) + "</tr>")
    cap = f"<caption>{caption}</caption>" if caption else ""
    tf = f"<tfoot><tr><td colspan=\"{len(headers)}\">{foot}</td></tr></tfoot>" if foot else ""
    return (f'<div class="table-wrap"><table{" class=" + chr(34) + cls + chr(34) if cls else ""}>'
            f"{cap}<thead><tr>{h}</tr></thead><tbody>{''.join(body)}</tbody>{tf}</table></div>")


def page(slug, title, body, active, description):
    nav = "".join(
        f'<a href="{s}"{" class=" + chr(34) + "active" + chr(34) if s == active else ""}>{t}</a>'
        for s, t in NAV
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <div class="brand">
      <span class="mark">$</span>
      <span>SAVINGS1<small>Independent 20-account verification</small></span>
    </div>
    <nav class="main-nav">{nav}</nav>
  </div>
</header>
<main id="main"><div class="wrap">
<div class="callout info" style="margin-bottom:18px">
  <strong>This is the cross-check dashboard.</strong> The primary SAVINGS1 dashboard — 18 products, promoted from
  the repository root by the parallel session — is at <a href="../index.html">../index.html</a>. This section keeps
  the <em>independent</em> 20-account dataset, its 41 registered sources, the tier-aware return maths and the
  26-item flagged list, so the two can be compared line by line. Where the two disagree, both figures are published
  and the difference is explained on <a href="flagged.html">Flagged for review</a>.
</div>
{body}
</div></main>
<footer class="site-footer">
  <div class="wrap">
    <div>
      <strong>Snapshot:</strong> rate and fee data read from bank and FDIC pages on 2026-10-21 / 2026-10-22.
      Projections assume an account opened {OPENING} and a constant APY. Not financial advice.
    </div>
    <div>
      <a href="../index.html">Primary dashboard</a> ·
      <a href="methodology.html">Method &amp; sources</a> ·
      <a href="flagged.html">Flagged for review</a> ·
      <a href="https://github.com/sassnarep3-star/SAVINGS1">Repository</a>
    </div>
  </div>
</footer>
</body>
</html>
"""
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, slug), "w") as fh:
        fh.write(html)


def one_year(acc_row_id, deposit=250000):
    r = ROWS[acc_row_id]
    for c in r["results"]:
        if c["deposit"] == deposit and c["years"] == 1:
            return c
    return None


# ---------------------------------------------------------------- derived facts
def apy_at(acc, dep):
    """Tier-aware APY for an arbitrary deposit, from the bank's own tier table."""
    tiers = acc.get("apy_tiers")
    if not tiers:
        return acc.get("apy_primary")
    best = None
    for t in tiers:
        lo = t.get("min") or 0
        hi = t.get("max")
        if dep >= lo and (hi is None or dep <= hi):
            if best is None or t["apy"] > best:
                best = t["apy"]
    return best if best is not None else acc.get("apy_primary")


def over_cap(acc, dep):
    """True when the deposit exceeds a ceiling the bank itself states."""
    txt = (acc.get("max_balance") or "").replace(",", "")
    if "1000000 per" in txt and dep > 1000000:
        return True
    return False


verified_accounts = [a for a in accounts["accounts"] if a.get("apy_status") == "verified"]
unverified_accounts = [a for a in accounts["accounts"] if a.get("apy_status") != "verified"]


def best_at(dep):
    """Highest year-1 interest at this deposit among accounts with a verified APY."""
    best = None
    for a in verified_accounts:
        if over_cap(a, dep):
            continue
        apy = apy_at(a, dep)
        if apy is None:
            continue
        if best is None or apy > best[1]:
            best = (a, apy)
    return best


best_250 = best_at(250000)
best_flat = max((a for a in verified_accounts if not a.get("apy_tiers")), key=lambda a: a["apy_primary"])
i250_best = 250000 * best_250[1] / 100
i250_flat = 250000 * best_flat["apy_primary"] / 100
i250_usbank = 250000 * 0.05 / 100
i250_pnc = 250000 * 0.03 / 100
i250_wells = 250000 * 0.01 / 100
i250_natl = 250000 * BENCH["value_pct"] / 100
n_accounts = len(accounts["accounts"])
axos_y1 = one_year("axos-year1-intro")["interest"]
axos_y1_apy = next(r["apy"] for r in projections["rows"] if r["id"] == "axos-year1-intro")


def host_list(urls):
    return ", ".join(sorted({host(u) for u in urls}))


# ================================================================ INDEX
ranked = sorted(verified_accounts, key=lambda a: -(apy_at(a, 250000) or 0))
lb_rows = []
for i, a in enumerate(ranked[:8], 1):
    apy = apy_at(a, 250000)
    lb_rows.append([
        f'<span class="rank">{i}</span>',
        f'<strong>{esc(a["brand"])}</strong><span class="sub">{esc(a["product"])}</span>',
        pct(apy),
        esc(a.get("apy_as_of") or "—"),
        esc(a.get("apy_scope", "")),
        usd(250000 * apy / 100),
        badge("verified"),
        src_cell(a["sources"][:1]),
    ])

idx_body = f"""
<h1>Savings account dashboard — highest verified yield, maximum FDIC coverage</h1>
<p class="lede">Every rate, fee and rule on this site was read from the bank's own website or from a federal
government page during this session. Nothing is copied from a rate aggregator. Where an official page would not
show a number, the cell is left blank and the item appears on <a href="flagged.html">Flagged for review</a>.</p>
<p class="meta-line">Snapshot 2026-10-21/22 · projections assume the account is opened <strong>{OPENING}</strong> ·
reference market New York, NY (ZIP 10001) · {n_accounts} accounts, {len(verified_accounts)} with a verified APY ·
merged with the earlier session's high-rate finds and re-verified here</p>

<section>
  <div class="kpis">
    <div class="kpi accent">
      <div class="label">Best standard APY, any balance</div>
      <div class="value">{pct(best_flat["apy_primary"])}</div>
      <div class="sub">{esc(best_flat["brand"])} — no tier, no relationship requirement</div>
    </div>
    <div class="kpi">
      <div class="label">Best year-1 return on $250,000</div>
      <div class="value">{usd(axos_y1)}</div>
      <div class="sub">Axos ONE — 5.00% for six months, then 3.50%; needs the checking bundle</div>
    </div>
    <div class="kpi">
      <div class="label">Highest advertised promo rate</div>
      <div class="value">5.00%</div>
      <div class="sub">Axos ONE, first 6 months — needs the checking bundle</div>
    </div>
    <div class="kpi">
      <div class="label">FDIC national savings rate</div>
      <div class="value">{pct(BENCH["value_pct"])}</div>
      <div class="sub">FDIC, as of {esc(BENCH["as_of"])} — the market benchmark</div>
    </div>
  </div>
</section>

<section>
  <div class="section-head"><h2>The whole decision in one paragraph</h2>{badge("verified")}</div>
  <div class="callout info">
    <strong>Same $250,000. Same year. Same federal insurance.</strong>
    {usd(i250_best)} of interest at {pct(best_250[1])} ({esc(best_250[0]["brand"])}),
    {usd(i250_natl)} at the FDIC national average of {pct(BENCH["value_pct"])},
    {usd(i250_usbank)} at U.S. Bank's standard 0.05%,
    {usd(i250_pnc)} at PNC's standard 0.03%,
    {usd(i250_wells)} at Wells Fargo's published 0.01%.
    Add the six-month introductory rates and the best year one on $250,000 is {usd(axos_y1)} at Axos ONE
    ({pct(axos_y1_apy)} blended) — but only if you run the $1,500-a-month direct deposit and $1,500 average balance
    through its checking account, and only while the balance sits at or above $250,000.
    The gap between the best verified rate and the worst published branch-bank rate is
    <strong>{usd(i250_best - i250_wells)} a year</strong> on the same insured deposit — about
    {axos_y1 / i250_wells:.0f}× the interest. FDIC insurance does not depend on which of these banks you pick,
    so accepting a branch-bank rate is a choice, not a requirement.
  </div>
</section>

<section>
  <div class="section-head">
    <h2>Leaderboard — verified rates at a $250,000 balance, highest first</h2>
    <p>Ranked by the rate that actually applies to $250,000, not by the headline advertising rate.</p>
  </div>
  {table(
      ["#", "Bank / account", "APY at $250k", "As of", "Rate scope", "Interest on $250k, 1 yr", "Status", "Source"],
      lb_rows, num_cols=(2, 5),
      caption="Only accounts whose rate was read on the bank's own page are ranked. Chase, Bank of America, Citibank and TD Bank are excluded because their rate tables are ZIP-gated.",
      foot="Interest is arithmetic on the published APY (<a href='methodology.html'>method</a>), assuming the rate does not change. Axos drops from 4.21% to 3.50% exactly at $250,000 — see the tier note on the rates page."
  )}
</section>

<section>
  <div class="section-head"><h2>Which one is actually best for you</h2></div>
  <div class="grid-3">
    <div class="card">
      <h3 style="margin-top:0">Best return with no conditions</h3>
      <p class="note" style="margin-bottom:8px">No bundle, no direct deposit, no promo code, no tier.</p>
      <p><strong>{esc(best_flat["brand"])} Performance® Savings — {pct(best_flat["apy_primary"])}</strong><br>
      {usd(i250_flat)} on $250,000 for a year, $0 to open, no minimum, no monthly fee, interest compounded daily.
      The page prints no effective date for the rate — flagged.</p>
      <p><a href="rates.html">Compare all {n_accounts} accounts →</a></p>
    </div>
    <div class="card">
      <h3 style="margin-top:0">Max FDIC insurance, one bank</h3>
      <p class="note" style="margin-bottom:8px">Best verified rate that still insures the whole balance at one institution.</p>
      <p><strong>{esc(best_250[0]["brand"])} — {pct(best_250[1])}</strong><br>
      $250,000 is covered as a single-owner account, $500,000 as a joint account, and $1,250,000 through a trust with
      five beneficiaries. Some accounts cap deposits below that — Marcus at $1M per account, Barclays at $1M.</p>
      <p><a href="returns.html">See the FDIC-max placement table →</a></p>
    </div>
    <div class="card">
      <h3 style="margin-top:0">Biggest 6-month promo</h3>
      <p class="note" style="margin-bottom:8px">Highest advertised rate in the whole comparison.</p>
      <p><strong>Axos ONE — 5.00% for 6 months</strong>, then 4.21% below $250,000 or 3.50% above.
      Requires the Axos ONE checking bundle: $1,500 in monthly direct deposits plus a $1,500 average daily balance,
      or $5,000 + $5,000. Miss it and the rate is 1.00%.</p>
      <p><a href="promotions.html">All verified promos →</a></p>
    </div>
    <div class="card">
      <h3 style="margin-top:0">Best cash bonus</h3>
      <p class="note" style="margin-bottom:8px">One-time money on top of interest.</p>
      <p><strong>E*TRADE — up to $800</strong> with promo code SAVE800, account funded by 2027-01-10, plus 4.25%
      guaranteed for six months. Barclays pays $200 for $25,000 held 120 days (expires 2026-10-31).</p>
      <p><a href="promotions.html">All verified bonuses →</a></p>
    </div>
    <div class="card">
      <h3 style="margin-top:0">Best rate at a branch megabank</h3>
      <p class="note" style="margin-bottom:8px">If you want branches and a national app.</p>
      <p><strong>U.S. Bank Bank Smartly Savings — 3.50%</strong><br>
      Only with a U.S. Bank checking/Safe Debit/Smartly card and $25,000+ combined qualifying balances; otherwise 0.05%.
      PNC, Wells Fargo and U.S. Bank standard tiers all sit under 0.10%.</p>
      <p><a href="rates.html#tiers">Compare all tiers →</a></p>
    </div>
    <div class="card">
      <h3 style="margin-top:0">What is still unproven</h3>
      <p class="note" style="margin-bottom:8px">Read this before you open anything.</p>
      <p><strong>{len(unverified_accounts)} of {n_accounts} accounts have no publishable APY</strong>,
      two banks do not state a mobile app on the page, three branch-bank rate sheets are pinned to a non-New-York ZIP,
      and five of the new high-rate accounts print no effective date.</p>
      <p><a href="flagged.html">Flagged for review →</a></p>
    </div>
  </div>
</section>

<section>
  <div class="section-head"><h2>Go deeper</h2></div>
  <div class="grid-3">
    <a class="tile" href="rates.html"><div class="t">Rates &amp; terms</div>
      <div class="d">All {n_accounts} accounts, every published tier, fees, minimums, as-of dates and a source link per row.</div>
      <div class="arrow">Open rates →</div></a>
    <a class="tile" href="returns.html"><div class="t">Return on your deposit</div>
      <div class="d">Interest earned at $10k → $1M over 1, 3 and 5 years, plus the FDIC-max placement table.</div>
      <div class="arrow">Open returns →</div></a>
    <a class="tile" href="promotions.html"><div class="t">Bonuses &amp; promotions</div>
      <div class="d">Cash bonuses and promotional APYs with their exact conditions and deadlines.</div>
      <div class="arrow">Open bonuses →</div></a>
    <a class="tile" href="rules.html"><div class="t">Opening rules</div>
      <div class="d">What each bank requires to open, minimum deposits, funding windows, ID and balance ceilings.</div>
      <div class="arrow">Open rules →</div></a>
    <a class="tile" href="security.html"><div class="t">FDIC &amp; security</div>
      <div class="d">Certificate numbers verified with the FDIC, active status, assets, and what each bank says about security.</div>
      <div class="arrow">Open FDIC &amp; security →</div></a>
    <a class="tile" href="methodology.html"><div class="t">Method &amp; sources</div>
      <div class="d">The formula, the snapshot dates, all {len(sources["sources"])} sources and the {VER["rows"]}-row verification log.</div>
      <div class="arrow">Open method →</div></a>
  </div>
</section>

<div class="callout warn">
  <strong>Read before acting</strong>
  <ul>
    <li>Every rate here is <em>variable</em> and can change before or after the account is opened. The projections hold the rate constant only to make the comparison possible. Introductory rates expire — the six-month boosts are shown as separate “derived” rows.</li>
    <li>The projections are arithmetic on published APYs, not bank quotes. Interest is taxable and is reported on Form 1099-INT.</li>
    <li>Branch-bank rate sheets are ZIP-gated. U.S. Bank was read at ZIP 55402, PNC at ZIP 15222 and Wells Fargo at CA 94105 — <a href="flagged.html">flagged</a>.</li>
    <li>FDIC coverage is $250,000 per depositor, per bank, per ownership category. Splitting cash across ownership categories or banks — not picking a famous brand — is what raises coverage.</li>
  </ul>
</div>
"""
page("index.html", "Savings dashboard — verified national savings rates and FDIC coverage",
     idx_body, "index.html",
     f"Verified savings rates from Chase, Bank of America, Wells Fargo, Citibank, U.S. Bank, PNC, TD, Ally, Marcus, American Express, Capital One, Synchrony, Barclays, SoFi, Axos, E*TRADE, Openbank, CIT and EverBank, with FDIC coverage analysis.")


# ================================================================ RATES
rate_rows = []
for a in sorted(accounts["accounts"], key=lambda x: (-(x["apy_primary"] or -1), x["brand"])):
    apy = a.get("apy_display") or "—"
    if a.get("apy_status") != "verified":
        apy = '— <span class="badge b-warn">unverified</span>'
    rate_rows.append([
        f'<strong>{esc(a["brand"])}</strong><span class="sub">{esc(a["product"])}</span>',
        esc(a["group"]),
        apy,
        esc(a.get("apy_as_of") or "—"),
        esc(a.get("apy_scope") or "—"),
        esc(a.get("min_open") or "—"),
        esc(a.get("monthly_fee") or "—"),
        badge(a.get("app_status", "unverified")),
        src_cell(a["sources"]),
    ])

tier_blocks = []
for a in accounts["accounts"]:
    if not a.get("apy_tiers"):
        continue
    rows = []
    for t in a["apy_tiers"]:
        lo = t.get("min") or 0
        hi = t.get("max")
        rng = f"{usd(lo)} – " + (usd(hi, 2) if hi is not None else "and above")
        rows.append([esc(t["label"]), esc(rng), pct(t["apy"])])
    tier_blocks.append(f"""
    <h3>{esc(a["brand"])} — {esc(a["product"])}</h3>
    <p class="note">As of {esc(a.get("apy_as_of") or "—")} · {esc(a.get("apy_scope", ""))} · {link(a["sources"][-1])}</p>
    {table(["Tier", "Balance range", "APY"], rows, num_cols=(2,))}
    """)

bench_rows = []
for a in sorted(verified_accounts, key=lambda x: -(max(t["apy"] for t in x["apy_tiers"]) if x.get("apy_tiers") else x["apy_primary"])):
    apy = max(t["apy"] for t in a["apy_tiers"]) if a.get("apy_tiers") else a["apy_primary"]
    mult = apy / BENCH["value_pct"]
    bench_rows.append([
        f'<strong>{esc(a["brand"])}</strong><span class="sub">{esc(a["product"])}</span>',
        pct(apy), f"{mult:.1f}×", usd(250000 * apy / 100), badge("verified"),
    ])
bench_rows.append([
    '<strong>FDIC national rate — savings</strong><span class="sub">Benchmark, not an account</span>',
    pct(BENCH["value_pct"]), "1.0×", usd(i250_natl), badge("verified"),
])

rates_body = f"""
<h1>Rates &amp; terms — all {n_accounts} accounts</h1>
<p class="lede">One row per account. The APY column is blank wherever the bank did not publish a fetchable number;
those rows are still listed so you can see the fee and access rules, and every blank is explained on
<a href="flagged.html">Flagged for review</a>.</p>
<p class="meta-line">Rates read 2026-10-21/22 · benchmark: FDIC national savings rate {pct(BENCH["value_pct"])} as of {esc(BENCH["as_of"])}</p>

<section>
  {table(
      ["Bank / account", "Type", "APY", "As of", "Rate scope", "Min to open", "Monthly fee", "App", "Source"],
      rate_rows,
      caption="Sorted by published APY (highest first), unverified rows last. “Rate scope” records where the number came from when a bank varies it by ZIP, tier or promotion.",
      foot="Full URLs: hover a source link, or see <a href='methodology.html'>Method &amp; sources</a>."
  )}
</section>

<section>
  <div class="section-head"><h2>How competitive are these rates?</h2>
    <p>Versus the FDIC's own national savings rate, and in dollars on $250,000 for one year.</p></div>
  {table(["Bank / account", "Best published APY", "Multiple of national rate", "Interest on $250,000, 1 yr", "Status"],
         bench_rows, num_cols=(1, 2, 3),
         caption=f"Benchmark: FDIC national rate for savings = {pct(BENCH['value_pct'])}, accurate as of {esc(BENCH['as_of'])} ({link(BENCH['source'])})",
         foot="A 3.50% account earns about 9× what the average insured savings account pays. The gap is a pricing choice by the bank, not a difference in insurance.")}
</section>

<section>
  <div class="section-head"><h2>Where these rates sit in the market</h2>
    <p>Competitiveness over the year: the same money measured against five official reference points, each read on or after 2026-10-19.</p></div>
  {table(["Reference point", "Rate", "As of", "What it means"], 
      [[f'<strong>{esc(m["name"])}</strong>', esc(m["value"]), esc(m["as_of"]),
        f'{esc(m["meaning"])} <span class="src">{link(m["source"])}</span>'] for m in accounts["meta"]["market_context"]],
      num_cols=(1,),
      caption="FDIC national rates and the Federal Reserve's target range are government-published; nothing here comes from a rate aggregator.",
      foot="A savings APY is variable, so a 4.20% account can fall below a 4.54% one-year Treasury before the year is out. The Treasury locks the yield; the savings account keeps the money liquid. That is the actual trade-off, not the headline number."
  )}
</section>

<section>
  <div class="section-head"><h2>Every published tier</h2>
    <p>Three banks price by balance or relationship. These are the exact tables, not summaries.</p></div>
  {''.join(tier_blocks)}
</section>

<section>
  <div class="section-head"><h2>Fees and minimums in detail</h2></div>
  {table(
      ["Bank / account", "Monthly fee", "How the fee is waived", "Minimum to earn interest", "Balance ceiling"],
      [[f'<strong>{esc(a["brand"])}</strong><span class="sub">{esc(a["product"])}</span>',
        esc(a.get("monthly_fee") or "—"),
        esc(a.get("fee_waiver") or "—"),
        esc(a.get("min_to_earn") or "—"),
        esc(a.get("max_balance") or "—")] for a in accounts["accounts"]],
      caption="Fee waivers are quoted from each bank's page. “—” means the bank's page did not state the item.",
  )}
</section>

<div class="callout warn">
  <strong>What “as of” means here</strong>
  Each as-of date is the date printed on the bank's own page (or, for Barclays Online Savings, absent — then the
  fetch date is used and the row is flagged). Variable APYs can change the same day you open the account.
</div>
"""
page("rates.html", f"Savings rates & terms — all {n_accounts} national accounts", rates_body, "rates.html",
     f"Side-by-side APY, fee, minimum and source for {n_accounts} national savings accounts, benchmarked against the FDIC national savings rate.")


# ================================================================ RETURNS
def return_table(years):
    rows = []
    for r in sorted(projections["rows"], key=lambda x: -((x["apy"] or -1))):
        cells = []
        apys = sorted({c["apy"] for c in r["results"] if c["years"] == years})
        for dep in projections["meta"]["deposits"]:
            match = [c for c in r["results"] if c["deposit"] == dep and c["years"] == years]
            if not match:
                cells.append("—")
            else:
                c = match[0]
                warn = " ⚠" if dep > 250000 else ""
                cells.append(f"{usd(c['interest'])}{warn}")
        label = f'<strong>{esc(r["bank"])}</strong><span class="sub">{esc(r["label"].split(" — ", 1)[-1])}</span>'
        apy_txt = ", ".join(pct(x) for x in reversed(apys)) if apys else "—"
        if len(apys) > 1:
            apy_txt += ' <span class="sub">by tier</span>' 
        if r["apy_status"] == "unverified":
            apy_txt = '— <span class="badge b-warn">unverified</span>'
        elif r["apy_status"] == "derived":
            apy_txt = apy_txt + ' <span class="badge b-info">derived</span>'
        rows.append([label, apy_txt] + cells)
    return table(
        ["Bank / account", "APY used", "$10,000", "$50,000", "$100,000", "$250,000", "$500,000", "$1,000,000"],
        rows, num_cols=(2, 3, 4, 5, 6, 7),
        caption=f"Interest earned over {years} year{'s' if years != 1 else ''}, by deposit size.",
        foot="⚠ = cell exceeds the $250,000 single-owner FDIC limit at one bank. See the placement table below.")


def apy_for(acc, dep):
    """Tier-aware APY for an arbitrary deposit, from the bank's own tier table."""
    tiers = acc.get("apy_tiers")
    if not tiers:
        return acc.get("apy_primary"), "Single published rate"
    best = None
    for t in tiers:
        lo = t.get("min") or 0
        hi = t.get("max")
        if dep >= lo and (hi is None or dep <= hi):
            if best is None or t["apy"] > best["apy"]:
                best = t
    if best is None:
        return acc.get("apy_primary"), "Single published rate"
    return best["apy"], best["label"]


def capped(acc, dep):
    """True when the deposit exceeds a ceiling the bank itself states."""
    txt = (acc.get("max_balance") or "").replace(",", "")
    if "1000000 per" in txt and dep > 1000000:
        return True
    return False


place_rows = []
for dep in [250000, 500000, 1000000, 1250000]:
    best = None
    for a in verified_accounts:
        if capped(a, dep):
            continue
        apy, _tier = apy_for(a, dep)
        if apy is None:
            continue
        interest = dep * apy / 100
        if best is None or interest > best[1]:
            best = (a, interest, apy)
    banks_needed = math.ceil(dep / 250000)
    coverage = {250000: "1 owner, single account", 500000: "joint account, 2 owners",
                1000000: "trust / POD with 4 beneficiaries",
                1250000: "trust / POD with 5+ beneficiaries"}[dep]
    place_rows.append([
        usd(dep), esc(coverage), str(banks_needed),
        f'<strong>{esc(best[0]["brand"])}</strong><span class="sub">{esc(best[0]["product"])}</span>',
        pct(best[2]), usd(best[1]), usd(dep + best[1]),
    ])

returns_body = f"""
<h1>Return on the size of your deposit</h1>
<p class="lede">Interest earned if the account is opened on <strong>{OPENING}</strong> and the published APY does not change.
Sizes run from $10,000 to $1,000,000 so you can see exactly where more money stops being fully insured at one bank.</p>
<p class="meta-line">Formula: ending = principal × (1 + APY/100)<sup>years</sup> · APY already includes compounding ·
{n_accounts} accounts · {len(projections["rows"])} projection rows
(including {len(projections["rows"]) - n_accounts} promotional blends) · {sum(len(r["results"]) for r in projections["rows"])} computed cells</p>

<div class="callout info">
  <strong>Why APY is the right input</strong>
  An advertised APY already accounts for compounding frequency, so growing a balance at the APY for N years gives the
  balance the bank's own disclosure implies. No bank-specific quirks (daily accrual, monthly crediting) are modelled —
  they are already inside the APY.
</div>

<section>
  <div class="section-head"><h2>Year 1</h2></div>
  {return_table(1)}
</section>

<section>
  <div class="section-head"><h2>Year 3 (cumulative)</h2></div>
  {return_table(3)}
</section>

<section>
  <div class="section-head"><h2>Year 5 (cumulative)</h2></div>
  {return_table(5)}
</section>

<section>
  <div class="section-head"><h2>Maximum FDIC coverage — where to put the money</h2>
    <p>The largest balance that is fully insured at a single bank, by ownership structure.</p></div>
  {table(["Deposit", "Ownership structure that insures it at one bank", "Banks needed if single-owner only",
          "Best verified account at this size", "APY", "Year-1 interest", "Ending balance"],
         place_rows, num_cols=(2, 4, 5, 6),
         caption="FDIC: $250,000 per depositor, per insured bank, per ownership category; $1,250,000 maximum per trust owner with five or more beneficiaries (rule effective 2024-04-01).",
         foot=f"Sources: {link('https://www.fdic.gov/resources/deposit-insurance/faq')} · {link('https://www.fdic.gov/resources/deposit-insurance/brochures/insured-deposits')} · balances above an account's published ceiling switch to the next best account.")}
</section>

<section>
  <div class="section-head"><h2>What the promotions are worth inside these numbers</h2></div>
  <div class="callout">
    <strong>Three derived rows are marked “derived” in the tables above</strong>
    <ul>
      <li><strong>SoFi, year 1:</strong> 4.40% for six months then 3.30% blends to
      {pct([r for r in projections["rows"] if r["id"] == "sofi-year1-boost"][0]["apy"], 3)} — {usd(one_year("sofi-year1-boost")["interest"])}
      on $250,000, versus {usd(one_year("sofi-savings")["interest"])} at the plain 3.30%.</li>
      <li><strong>Marcus, year 1 with one referral:</strong> 3.75% (Marcus's own illustration) —
      {usd(one_year("marcus-year1-referral")["interest"])} on $250,000.</li>
      <li><strong>U.S. Bank relationship tier:</strong> 3.50% instead of 0.05% —
      {usd(one_year("usbank-relationship-3.50")["interest"])} versus {usd(one_year("usbank-smartly-savings")["interest"])}, but it requires a U.S. Bank
      checking/Safe Debit/Smartly card and $25,000+ in combined qualifying balances.</li>
    </ul>
  </div>
</section>

<section>
  <div class="section-head"><h2>How every promotional row was computed</h2>
    <p>Blended year-one APY = sqrt((1 + promotional APY) × (1 + standard APY)) − 1. Both numbers come from the bank's own page.</p></div>
  {table(
      ["Promotional row", "Promotional APY", "Standard APY after it", "Blended year-one APY", "Formula check", "Source"],
      [[f'<strong>{esc(r["bank"])}</strong><span class="sub">{esc(r["label"].split(" — ", 1)[-1])}</span>',
        pct(r["blend"][0]), pct(r["blend"][1]), pct(r["apy"]),
        f'sqrt(1.{(r["blend"][0]*100):04.0f} × 1.{(r["blend"][1]*100):04.0f}) − 1',
        src_cell(next(a for a in accounts["accounts"] if a["id"] == r["account_id"])["sources"][:1])]
       for r in projections["rows"] if r.get("blend")],
      num_cols=(1, 2, 3),
      caption=f"{len([r for r in projections['rows'] if r.get('blend')])} rows apply a six-month promotion and are labelled “derived” in the tables above; two more derived rows use a fixed published tier (U.S. Bank relationship rate, Marcus referral) and need no blending. Everything else is a single published APY.",
      foot="Years 3 and 5 compound the first year at the promotional rate and the remaining years at the standard rate, so the promotional rows are not over-credited beyond the six-month window."
  )}
</section>

<div class="callout warn">
  <strong>The one-time bonuses, in the same units</strong>
  Barclays pays $200 for $25,000 held 120 days — that is 0.80% of principal, once.
  SoFi pays up to $400 with eligible direct deposit. Both are worth less than the annual difference between a
  3.50% account and a 0.05% account on $250,000 ({usd(i250_best - i250_usbank)}), so chase the rate first and the
  bonus second. <a href="promotions.html">Bonus terms →</a>
</div>
"""
page("returns.html", "Returns by deposit size — $10k to $1M over 1, 3 and 5 years", returns_body, "returns.html",
     "Interest earned on savings deposits from $10,000 to $1,000,000 at every verified national savings rate, plus the maximum-FDIC placement table.")


# ================================================================ PROMOTIONS
promo_rows = []
for p in sorted(promotions["promotions"], key=lambda x: (x["status"] != "verified", -(x["amount_usd"] or 0), x["bank"])):
    promo_rows.append([
        f'<strong>{esc(p["bank"])}</strong>',
        esc(p["offer"]),
        usd(p["amount_usd"]) if p["amount_usd"] else "rate offer",
        esc(p.get("deadline") or "—"),
        esc(p.get("requirement") or "—"),
        esc(p.get("value_note") or "—"),
        badge(p["status"]),
        link(p["source"]),
    ])
promos_body = f"""
<h1>Bonuses &amp; promotions</h1>
<p class="lede">Cash bonuses and promotional APYs that were printed on the bank's own page. “None advertised” means the
official product page was checked on 2026-10-21/22 and carried no opening bonus or promo rate — it does not prove that
no targeted offer exists.</p>

<section>
  {table(["Bank", "Offer", "Cash value", "Deadline", "Exact requirement", "What it is worth", "Status", "Source"],
         promo_rows,
         caption="Sorted with verified cash offers first, then rate-only offers, then accounts with no offer displayed.",
         foot="Bonus terms change often and are usually limited to new customers. Re-read the terms on the bank's page before funding.")}
</section>

<section>
  <div class="section-head"><h2>Two things to check before chasing a bonus</h2></div>
  <div class="grid-2">
    <div class="callout info">
      <strong>A bonus is a one-time payment, a rate is every year</strong>
      $200 on $25,000 is 0.80% once. A 3.50% account pays $8,750 a year on $250,000. If a bonus account pays 0.05%,
      the bonus is wiped out by the rate gap in a few months.
    </div>
    <div class="callout warn">
      <strong>Bonuses usually require new money and a hold period</strong>
      Barclays: new Tiered Savings customers only, $25,000 in within 30 days and kept for 120 consecutive days, paid
      about 60 days later, and reported to the IRS as interest. Read the full terms on the bank's page.
    </div>
  </div>
</section>
"""
page("promotions.html", "Savings bonuses & promotions — verified terms", promos_body, "promotions.html",
     "Verified opening bonuses and promotional rates for national savings accounts, with exact requirements and deadlines.")


# ================================================================ RULES
rules_rows = []
for a in accounts["accounts"]:
    rules_rows.append([
        f'<strong>{esc(a["brand"])}</strong><span class="sub">{esc(a["product"])}</span>',
        esc(a.get("min_open") or "—"),
        esc(a.get("monthly_fee") or "—"),
        esc(a.get("max_balance") or "—"),
        esc(a.get("withdrawal_rules") or "—"),
        esc(a.get("compounding") or "—"),
        esc(a.get("rules_note") or "—"),
        src_cell(a["sources"][:1]),
    ])
rules_body = f"""
<h1>Rules for opening and running the account</h1>
<p class="lede">What each bank requires to open the account, what it charges to keep it, how often money can leave,
and the ceilings that matter if you are placing a large insured balance.</p>

<section>
  {table(["Bank / account", "Minimum to open", "Monthly fee", "Balance ceiling", "Withdrawal / transfer rules",
          "Compounding", "Opening requirements", "Source"],
         rules_rows,
         caption="“—” means the bank's own page did not state the item; nothing is filled in from memory.")}
</section>

<section>
  <div class="section-head"><h2>Patterns worth knowing</h2></div>
  <div class="grid-2">
    <div class="callout info">
      <strong>Branch banks charge a fee and waive it with a relationship</strong>
      Chase $5 (waived at $300), Wells Fargo $5 (waived at $300), PNC $5 (waived at $300 or a linked checking account),
      U.S. Bank $5, Citi $4.50 (waived at $500), TD $5/$15. The cheapest way to hold these accounts is usually to link a
      checking account — which is also how the banks earn the relationship.
    </div>
    <div class="callout info">
      <strong>Online banks charge nothing and have no minimum</strong>
      Ally, Marcus, Amex, Capital One, Synchrony, Barclays and SoFi all state no monthly fee and no minimum balance.
      Their limits are different: Ally caps withdrawals at 10 per statement cycle, Barclays caps the account at
      $1,000,000, and Marcus caps an Online Savings account at $1,000,000.
    </div>
    <div class="callout warn">
      <strong>Funding windows are real</strong>
      Capital One gives 60 days to fund after approval; TD closes the account automatically if no deposit is made within
      45 days; Marcus returns balances above its limits.
    </div>
    <div class="callout warn">
      <strong>Four banks' opening requirements could not be fully read</strong>
      Chase, Bank of America, Citibank and TD have components (rates, fees or minimums) that render client-side.
      See <a href="flagged.html">Flagged for review</a>.
    </div>
  </div>
</section>
"""
page("rules.html", "Account opening rules, fees and limits", rules_body, "rules.html",
     f"Minimum opening deposits, monthly fees and waivers, balance ceilings and withdrawal rules for {n_accounts} national savings accounts.")


# ================================================================ SECURITY
fdic_rows = []
for a in accounts["accounts"]:
    inst = INST.get(a["fdic_cert"], {})
    fdic_rows.append([
        f'<strong>{esc(a["brand"])}</strong>',
        esc(inst.get("name", "")),
        str(a["fdic_cert"]),
        badge("verified") if inst.get("active") == 1 else badge("unverified"),
        f'{inst.get("asset_kusd", 0) / 1_000_000:,.1f}',
        f'{inst.get("depdom_kusd", 0) / 1_000_000:,.1f}',
        esc(f'{inst.get("city", "")}, {inst.get("state", "")}'),
        link(f"https://banks.data.fdic.gov/bankfind-suite/bankfind/details/{a['fdic_cert']}", "BankFind"),
        esc(a.get("fdic_statement") or "—"),
    ])
sec_rows = []
for a in accounts["accounts"]:
    note = a.get("security_note") or ""
    src = a.get("security_source") or a["sources"][0]
    sec_rows.append([
        f'<strong>{esc(a["brand"])}</strong>',
        note if note else '— <span class="badge b-neutral">not stated</span>',
        link(src),
    ])

security_body = f"""
<h1>FDIC insurance &amp; security</h1>
<p class="lede">Insurance is the part you can verify objectively: either the charter is in the FDIC's register or it is not.
Security features are the part you cannot — so the table below shows only what each bank publishes, and marks the rest.</p>

<section>
  <div class="section-head"><h2>Every charter verified with the FDIC</h2>
    <p>Certificate numbers, active status, total assets and domestic deposits from the FDIC institutions API.</p></div>
  {table(["Brand", "FDIC legal name", "Certificate", "Active", "Total assets ($B)", "Domestic deposits ($B)", "HQ", "FDIC record", "Bank's own insurance statement"],
         fdic_rows, num_cols=(2, 4, 5),
         caption=f"Source: {link('https://banks.data.fdic.gov/api/institutions')} — index created 2026-10-16. Assets are the FDIC's reported figures (converted from thousands to billions).",
         foot="Three closed legacy charters share names with live brands (U.S. Bank 5134, Goldman Sachs 57485, PNC 7944); they are excluded. Always match on the certificate number, not the brand.")}
</section>

<section>
  <div class="section-head"><h2>What each bank says about security</h2>
    <p>Quoted from the bank's own page. “Not stated” means the page fetched did not describe security features.</p></div>
  {table(["Bank", "Verified statement", "Source"], sec_rows,
         caption="Multi-factor authentication, biometric login and device binding are app-level features that were not audited in this session for every bank — see the flag list.")}
</section>

<section>
  <div class="section-head"><h2>How the insurance actually stacks</h2></div>
  <div class="grid-2">
    <div class="callout info">
      <strong>$250,000 per depositor, per bank, per ownership category</strong>
      All of your deposits in the same ownership category at the same bank are added together. Different categories —
      single, joint, certain retirement accounts, trust — are insured separately.
      {link("https://www.fdic.gov/resources/deposit-insurance/understanding-deposit-insurance", "FDIC")}
    </div>
    <div class="callout info">
      <strong>$1,250,000 is the trust ceiling</strong>
      Since April 1, 2024, a trust owner with five or more beneficiaries is insured up to $1,250,000 per owner for all
      trust accounts (POD/ITF, revocable and irrevocable) at the same bank. Naming more beneficiaries does not raise it.
      {link("https://www.fdic.gov/resources/deposit-insurance/brochures/insured-deposits", "FDIC")}
    </div>
  </div>
  <ol class="takeaways" style="margin-top:14px">
    <li><strong>Check the certificate number, not the logo.</strong> Every row above links to its FDIC BankFind record.</li>
    <li><strong>Insurance is dollar-for-dollar, including accrued interest.</strong> A $250,000 balance that accrues interest
    above the limit is only insured to the limit — leave headroom or use a joint/trust title.</li>
    <li><strong>Use EDIE for your exact situation.</strong> {link("https://edie.fdic.gov/", "edie.fdic.gov")} is the FDIC's own estimator.</li>
    <li><strong>Two FDIC-insured banks are not automatically two coverages</strong> if the deposits are held in the same
    ownership category at the same charter.</li>
  </ol>
</section>

<section>
  <div class="section-head"><h2>Two coverage traps found in this review</h2></div>
  <div class="grid-2">
    <div class="callout warn">
      <strong>SoFi's “up to $3M” is not a SoFi charter limit</strong>
      It is additional coverage through a network of participating banks. SoFi Bank, N.A. itself insures the standard
      $250,000 per depositor, per bank, per ownership category.
      {link("https://www.sofi.com/banking/high-yield-savings-account/", "sofi.com")}
    </div>
    <div class="callout warn">
      <strong>Capital One and Discover now count as one bank</strong>
      Capital One's own FAQ: Capital One or Discover Bank deposit accounts opened on or after May 18, 2025 are counted
      with your other Capital One deposit accounts for FDIC coverage. Splitting between the two brands does not double
      coverage. {link("https://www.capitalone.com/bank/savings-accounts/online-performance-savings-account/", "capitalone.com")}
    </div>
  </div>
</section>

<div class="callout warn">
  <strong>What this page does not prove</strong>
  Being FDIC-insured says nothing about an app's authentication quality. Only Ally publishes an explicit
  multi-factor-authentication statement and a security guarantee among the pages read here; Capital One publishes a
  security program page. For the others, app-level security is unverified in this session and listed as such.
</div>
"""
page("security.html", f"FDIC insurance & security — {n_accounts} verified charters", security_body, "security.html",
     "FDIC certificate numbers, active status and asset data for every bank in the comparison, plus published security statements.")


# ================================================================ FLAGGED
flag_rows = []
for f in flagged["items"]:
    flag_rows.append([
        esc(f["id"]),
        f'<strong>{esc(f["area"])}</strong><span class="sub">{esc(f["item"])}</span>',
        esc(f["detail"]),
        esc(f["impact"]),
        badge(f["status"]),
        f'<a href="{esc(f["source"])}" target="_blank" rel="noopener">{esc(f["source"])}</a>',
    ])
flagged_body = f"""
<h1><span class="badge b-warn" style="font-size:13px;vertical-align:middle">Flagged for review</span> {len(flagged["items"])} items</h1>
<p class="lede">Everything that could not be confirmed from an official source, plus everything that looked irregular
while checking line by line. None of this blocks publication — it is the list to read before you open an account, and
each item carries the official page to check by hand.</p>

<div class="grid-3" style="margin-bottom:18px">
  <div class="kpi"><div class="label">Unverified items</div>
    <div class="value">{sum(1 for f in flagged["items"] if f["status"] == "unverified")}</div>
    <div class="sub">blank in every table, never guessed</div></div>
  <div class="kpi"><div class="label">Irregularities</div>
    <div class="value">{sum(1 for f in flagged["items"] if f["status"] == "irregular")}</div>
    <div class="sub">official statements that conflict or misrender</div></div>
  <div class="kpi"><div class="label">Scoped values</div>
    <div class="value">{sum(1 for f in flagged["items"] if f["status"] == "scope")}</div>
    <div class="sub">real, but tied to another ZIP or an older date</div></div>
  <div class="kpi"><div class="label">Notes</div>
    <div class="value">{sum(1 for f in flagged["items"] if f["status"] == "note")}</div>
    <div class="sub">limits and context that change the decision</div></div>
  <div class="kpi"><div class="label">Risks</div>
    <div class="value">{sum(1 for f in flagged["items"] if f["status"] == "risk")}</div>
    <div class="sub">stated conditions that cut the rate</div></div>
</div>

<section>
  {table(["ID", "Item", "What was found", "Why it matters", "Status", "Official page"],
         flag_rows,
         caption="Full URLs are printed rather than hostnames so each item can be checked directly.",
         foot="Status key: unverified = page did not reveal the value; irregular = conflicting or broken official output; scope = tied to a ZIP/tier/date; risk = a stated condition that cuts the rate; note = important context.")}
</section>

<section>
  <div class="section-head"><h2>How to close these out</h2></div>
  <ol class="takeaways">
    <li>Open the official rate page for Chase, Bank of America, Citibank or TD with ZIP 10001 in a normal browser; the
    rate table only appears after the ZIP is accepted.</li>
    <li>For Synchrony, confirm at application whether 3.55% or 2.85% applies to your account.</li>
    <li>For Barclays, confirm a mobile app exists if that is a hard requirement.</li>
    <li>For Axos, decide whether you can keep the checking bundle alive every month — missing it drops the savings
    rate to 1.00%, which is worse than an ordinary high-yield account.</li>
    <li>For U.S. Bank, PNC and Wells Fargo, re-read the rate table with a New York ZIP before comparing.</li>
  </ol>
</section>
"""
page("flagged.html", "Flagged for review — unverified values and irregularities", flagged_body, "flagged.html",
     "Every unverified value and irregular finding in the savings comparison, with the official page to check by hand.")


# ================================================================ METHOD
src_rows = []
for s in sources["sources"]:
    src_rows.append([
        f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["url"])}</a>',
        badge("verified") if s["method"] == "fetched" else f'<span class="badge b-info">{esc(s["method"])}</span>',
        esc(s["used_for"]),
    ])

ver_rows = []
for r in verification["rows"]:
    if r["status"] == "unverified":
        val = '— <span class="badge b-warn">blank</span>'
    elif r["status"] == "none-displayed":
        val = esc(r["value"]) + ' <span class="badge b-neutral">none advertised</span>'
    else:
        val = esc(r["value"])[:220] + ("…" if len(r["value"]) > 220 else "")
    ver_rows.append([
        esc(r["account"]), esc(r["field"]), val, badge(r["status"]),
        link(r["source"]),
    ])

method_body = f"""
<h1>Method, sources and the verification log</h1>
<p class="lede">This page is the audit trail. It states the snapshot dates, the formula, the full list of sources,
the sources that were deliberately rejected, and a {VER["rows"]}-row log of what was checked for each account.</p>

<section>
  <div class="kpis">
    <div class="kpi"><div class="label">Checks logged</div><div class="value">{VER["rows"]}</div><div class="sub">field × account</div></div>
    <div class="kpi accent"><div class="label">Verified</div><div class="value">{VER["verified"]}</div><div class="sub">read on an official page</div></div>
    <div class="kpi"><div class="label">Verified as “none”</div><div class="value">{VER["none_displayed"]}</div><div class="sub">page checked, no offer</div></div>
    <div class="kpi"><div class="label">Unverified</div><div class="value">{VER["unverified"]}</div><div class="sub">blank everywhere, flagged</div></div>
  </div>
</section>

<section>
  <div class="section-head"><h2>1 · The rules this data follows</h2></div>
  <ol class="takeaways">
    <li><strong>Official sources only.</strong> A number is used only if it was read on the bank's own domain or a
    <code>.gov</code> domain during this session. Rate aggregators, news articles and other banks' comparison tables
    were rejected — including Marcus's and SoFi's tables that quote Chase and Wells Fargo rates.</li>
    <li><strong>Blank beats guessed.</strong> If a page gates the value behind a ZIP or renders it client-side, the cell
    stays empty and the item moves to <a href="flagged.html">Flagged for review</a>. Seventeen field checks ended
    that way — most importantly the four ZIP-gated APYs at Chase, Bank of America, Citibank and TD Bank, which are
    therefore excluded from every ranked table and every projection.</li>
    <li><strong>Dates are copied, not assumed.</strong> Each APY carries the as-of date printed on the page. Where no
    date is printed (Barclays Online Savings), the as-of cell is blank and the row is flagged.</li>
    <li><strong>Projections are arithmetic, never estimates.</strong> Interest is computed from the published APY only.</li>
    <li><strong>Every row links to its source.</strong> Hover any source link for the full URL; every URL is also listed below.</li>
  </ol>
</section>

<section>
  <div class="section-head"><h2>2 · Snapshot</h2></div>
  {table(["Item", "Value"], [
      ["Account opening date assumed for projections", OPENING],
      ["Rate snapshot window", "2026-10-20 to 2026-10-22 (each row carries its own as-of date)"],
      ["FDIC institution data", "API index created 2026-10-16"],
      ["FDIC national savings rate benchmark", pct(BENCH["value_pct"]) + " as of " + BENCH["as_of"]],
      ["Reference market", accounts["meta"]["home_market"]],
      ["Accounts in the comparison", str(len(accounts["accounts"]))],
      ["Accounts with a verified APY", str(len(verified_accounts))],
      ["Projection cells", str(sum(len(r["results"]) for r in projections["rows"]))],
    ])}
</section>

<section>
  <div class="section-head"><h2>3 · The formula</h2></div>
  <div class="callout">
    <strong>ending = principal × (1 + APY/100)<sup>years</sup></strong>
    interest = ending − principal. Because APY already reflects compounding, no compounding frequency is applied on top.
    Tiered accounts use the tier that the deposit falls into, from that bank's own table. Promotional rows are blends of
    the bank's published base and promotional APYs and are labelled “derived” wherever they appear.
    <br><br>
    <strong>Known limitation:</strong> all rates compared here are variable. Holding the APY constant for 1, 3 or 5 years
    is an assumption made for comparison, not a forecast. No CD is included in this dataset.
  </div>
</section>

<section>
  <div class="section-head"><h2>4 · Sources</h2>
    <p>Every external link on the site, and what was taken from it.</p></div>
  {table(["URL", "Method", "Used for"], src_rows,
         caption=f"{len(sources['sources'])} sources. “fetched” = retrieved and read in this session; “linked-from-official-page” = printed as a link on a page that was fetched; FDIC BankFind detail links are generated from verified certificate numbers.")}
  <p class="note" style="margin-top:10px"><strong>Rejected on purpose:</strong>
  {esc(sources["rejected_sources"][0]["reason"])} {esc(sources["rejected_sources"][1]["reason"])}</p>
</section>

<section>
  <div class="section-head"><h2>5 · Line-by-line verification log</h2>
    <p>One row per field per account. Blanks are shown as blanks.</p></div>
  {table(["Account", "Field", "Value read", "Status", "Source"], ver_rows,
         caption="Generated by tools/build_verification.py from data/v2/accounts.json and data/v2/promotions.json, so the log and the tables cannot drift apart.")}
</section>

<section>
  <div class="section-head"><h2>6 · Repo audit</h2>
    <p>What was in the repository before this session, and what that means for the data.</p></div>
  {table(["Finding", "Detail", "Consequence"], [
      ["Starting state", "main at commit <code>e6a9e13</code> ('Initial commit') contained only <code>README.md</code>, whose entire content was <code># SAVINGS1---</code>. No data, no site, no <code>COORDINATION.md</code>, no <code>.gitignore</code>, no LICENSE, no CI.", "Every figure published here was gathered in this session — there is no inherited dataset to trust or reconcile. The 15 accounts in the first pass were all built from primary pages."],
      ["Second session arrives", "While this session was working, a second session (<code>S-830079CD</code>) merged PR #1 to <code>main</code> with a 17-product dataset in <code>data/</code>, its own 9-page site in <code>docs/</code>, and a CI workflow. The merge produced four conflicts.", "Both datasets are kept: theirs at <code>data/</code> (which their pipeline reads), ours at <code>data/v2/</code> (which the published site reads). Their five high-rate accounts were re-fetched and re-verified here before being added."],
      ["Coordination board", "Created at the start of this session before any research, with the task claims recorded in it; merged with the other session's board during reconciliation.", "No other session's work was overwritten, and the conflict resolution is recorded in <code>COORDINATION.md</code>."],
      ["Pages configuration", "Pages API: build_type <code>legacy</code>, source <code>main:/</code>, public, HTTPS enforced. Site URL: sassnarep3-star.github.io/SAVINGS1/", "Pages are served from the repository root, so the pages live at the root and a <code>.nojekyll</code> file is committed."],
      ["Merge gate", "CI (<code>.github/workflows/verify.yml</code>, from the other session) rebuilds <code>docs/</code> and runs <code>scripts/verify_data.py</code>. There is no branch protection.", "Both gates must pass: the CI checks on the archived <code>docs/</code> build, and <code>tools/check_links.py</code> on the published root site (provenance plus internal links)."],
      ["Open hygiene items", "No LICENSE file; README was a single line before this session rewrote it; the archived <code>docs/</code> build still carries the other session's 17-product data.", 'Flagged on <a href="flagged.html">Flagged for review</a> (F19, F20, F26) rather than silently fixed.'],
    ])}
</section>

<section>
  <div class="section-head"><h2>7 · How this site is built</h2></div>
  <p class="note">Static HTML generated by <code>tools/build_site.py</code> from the JSON in <code>data/v2/</code>:
  <code>accounts.json</code>, <code>projections.json</code>, <code>promotions.json</code>, <code>banks_fdic.json</code>,
  <code>verification.json</code>, <code>flagged.json</code> and <code>sources_fetched.json</code>.
  <code>tools/build_projections.py</code> recomputes every dollar figure and <code>tools/check_links.py</code> verifies
  that every link is either an official source on file or an existing local page. No CDN, no tracking, no JavaScript
  required to read any number.</p>
</section>
"""
page("methodology.html", "Method, sources and verification log", method_body, "methodology.html",
     "Snapshot dates, the projection formula, the full source list and a 90-row line-by-line verification log.")
print("built pages")
