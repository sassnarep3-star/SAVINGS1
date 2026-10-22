const DATA_URL = 'data/accounts.json';
const money = n => new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n);
const rateText = p => p.apy === null ? '—' : `${p.apyLabel} APY`;
const sourceLink = (url,label='Official source') => { const a=document.createElement('a'); a.href=url; a.textContent=label; a.target='_blank'; a.rel='noopener noreferrer'; a.className='source'; return a; };
const td = (row, value) => { const c=document.createElement('td'); if(value instanceof Node) c.append(value); else c.textContent=value; row.append(c); return c; };
const badge = (text, cls='') => { const b=document.createElement('span'); b.className=`badge ${cls}`; b.textContent=text; return b; };
function sourceStatus(status){ return status==='confirmed'?['Rate verified','green']:status==='conditional'?['Conditional','yellow']:status==='flagged'?['Flagged','yellow']:['Unverified','gray']; }
function productRow(p, mode){
  const tr=document.createElement('tr'); const bank=document.createElement('td'); bank.innerHTML=`<strong>${p.bank}</strong><br><span class="small">${p.product}</span>`; tr.append(bank);
  if(mode==='rates'){
    td(tr, rateText(p)); td(tr, p.apyDate); const [label,cls]=sourceStatus(p.rateStatus); td(tr,badge(label,cls)); const rateLinks=document.createElement('span');rateLinks.append(sourceLink(p.rateSource,'Rate source'));if(p.rateSourceAlt){rateLinks.append(document.createTextNode(' · '),sourceLink(p.rateSourceAlt,'Rate update'))}td(tr,rateLinks);
  } else {
    td(tr,p.group); td(tr,p.minOpen); td(tr,p.opening); td(tr,p.fees); td(tr,p.access); const controls=document.createElement('span'); controls.className='small'; controls.textContent=p.securityNotes||''; const links=document.createElement('div'); links.append(sourceLink(p.termsSource,'Terms'),document.createTextNode(' · '),sourceLink(p.appSource,'App'),document.createTextNode(' · '),sourceLink(p.securitySource,'Security'),document.createTextNode(' · '),sourceLink(p.fdicSource,'FDIC')); const c=document.createElement('td');c.append(controls,links);tr.append(c);
  }
  return tr;
}
const AMOUNTS=[10000,25000,100000,235000];
function applicableRate(p,amount){
  if(p.apy===null)return null;
  if(p.id==='citi' && amount<25000)return null;
  if(p.id==='wells' && amount<25000)return .01;
  if(p.id==='barclays-tiered')return amount>=250000?3.65:3.50;
  return p.apy;
}
function renderReturnTable(data,tableId,years){
  const body=document.querySelector(`#${tableId} tbody`);if(!body)return;
  data.products.forEach(p=>{
    const tr=document.createElement('tr'); const label=document.createElement('td'); label.innerHTML=`<strong>${p.bank}</strong><br><span class="small">${p.product}</span>`; tr.append(label);
    AMOUNTS.forEach(amount=>{
      const c=document.createElement('td');const rate=applicableRate(p,amount);
      if(rate===null){c.textContent='—';c.title=p.id==='citi'&&amount<25000?'Citi promotion requires at least $25,000 in qualifying New-to-Citibank Funds.':'Rate not confirmed; estimate omitted.'}
      else if(years>1&&!p.longTermScenario){c.textContent='—';c.title='Not projected beyond one year: offer, location-specific rate, or rate conflict makes a longer scenario unsupported.'}
      else {
        const earned=years===1?amount*rate/100:amount*((1+rate/100)**years-1);
        const ending=amount+earned;
        c.textContent=money(Math.round(earned));
        if(p.id==='wells'&&amount>=25000)c.title='One-year only; assumes new-customer eligibility and at least $25,000 maintained every day.';
        else if(p.id==='wells')c.title='Uses the current 0.01% standard APY because this amount is below the promotional minimum.';
        else if(p.id==='citi')c.title='One-year blended APY only; assumes qualifying funds, the current promo through its term, and the current standard rate thereafter.';
        else if(p.id==='barclays-tiered')c.title='Uses the 3.50% APY tier below $250,000. At $250,000 or more the currently listed tier is 3.65%, but that principal would exceed the FDIC limit before interest.';
        else if(p.id==='barclays-aarp')c.title='Assumes AARP membership eligibility and that the current variable rate remains unchanged.';
        else if(p.id==='capitalone')c.title='Uses official account comparison-page APY; current product-page discrepancy is flagged.';
        else if(years>1)c.title=`Hypothetical compound-growth scenario at an unchanged ${rate.toFixed(2)}% APY for ${years} years; not a forecast.`;
        if(ending>250000){c.classList.add('cell-warning');c.title+=` Estimated ending balance ${money(ending)} exceeds the standard $250,000 single-owner FDIC limit before considering other deposits.`;}
      }
      tr.append(c);
    });
    const rateLinks=document.createElement('span');rateLinks.append(sourceLink(p.rateSource,'Official rate source'));if(p.rateSourceAlt){rateLinks.append(document.createTextNode(' · '),sourceLink(p.rateSourceAlt,'Rate update'))}td(tr,rateLinks);body.append(tr);
  });
}
function renderRates(data){
  const body=document.querySelector('#rate-table tbody'); if(body)data.products.forEach(p=>body.append(productRow(p,'rates')));
  renderReturnTable(data,'return-table',1);renderReturnTable(data,'return-3-table',3);renderReturnTable(data,'return-5-table',5);
}
function renderAccounts(data){const body=document.querySelector('#account-table tbody'); if(body)data.products.forEach(p=>body.append(productRow(p,'accounts')));}
function renderOfferCards(data){
 const host=document.querySelector('#offer-cards'); if(!host)return;
 const entries=[
  {id:'chase',title:'Chase Savings offer',copy:'$100 after $5,000+ in qualifying new money, or $200 after $10,000+. Enroll by 2027-01-27; fund within 30 days and maintain the qualifying amount for 90 days. Offer code, new-customer and other restrictions apply.',tag:'Cash bonus'},
  {id:'ally',title:'Ally Savings referral',copy:'$100 with a personal referral link and enrollment by 2026-12-31. For Savings: establish monthly recurring external ACH transfers of any amount (or qualifying direct deposit) and complete one each month for 3 consecutive months. New-friend exclusions apply.',tag:'Cash bonus'},
  {id:'marcus',title:'Marcus referral rate boost',copy:'+1.00 percentage point APY for 3 months when a new customer opens using an existing customer’s unique referral link. Then the then-current standard variable APY applies. Not a full-year fixed rate.',tag:'Temporary APY boost'},
  {id:'wells',title:'Wells Fargo new-savings-customer rate',copy:'3.25% variable APY at balances of at least $25,000, if new-customer and timing rules are met. Must reach $25,000 within 30 days and maintain it daily. Not a cash bonus.',tag:'Conditional variable APY'},
  {id:'citi',title:'Citi Savings opening-date promotion',copy:'Open by 2026-10-22. Eligible new accounts may receive 3.75% promotional interest for up to 3 months with at least $25,000 in qualifying New-to-Citibank Funds. The New York basic-tier one-year blended APY is 0.98%; it is not a cash bonus. $10,000 maximum promotional interest.',tag:'Ends 2026-10-22'},
  {id:'barclays-tiered',title:'Barclays Tiered Savings',copy:'$200 for a new Barclays customer who opens by 2026-10-31, deposits at least $25,000 within 30 days, and keeps at least $25,000 for 120 consecutive days. Bonus is added about 60 days later. Current APY is tiered: 3.50% below $250,000 and 3.65% at $250,000+.',tag:'Cash bonus'},
  {id:'barclays-aarp',title:'Barclays Select Savings for AARP members',copy:'AARP membership required. $400 for a new Select Savings customer who opens by 2026-10-31, deposits at least $40,000 within 30 days, and maintains at least $40,000 for 120 consecutive days; paid about 60 days later and treated as taxable interest. The account advertises a variable 4.25% APY across tiers, accurate 2026-10-07.',tag:'Eligibility-restricted'},
  {id:'usbank',title:'U.S. Bank Smartly relationship rate',copy:'Advertises up to 3.50% APY with a qualifying Smartly Checking, Safe Debit, or Smartly Visa relationship and at least $25,000 combined qualifying balances. Rates vary by location; the New York rate was not confirmed, and this is not a cash bonus.',tag:'Location-specific APY'},
  {id:'amex',title:'American Express High Yield Savings',copy:'No general cash bonus or temporary savings promotion was confirmed in the reviewed official sources. Current variable 3.20% APY is separate from any targeted offer.',tag:'No public bonus verified'},
  {id:'capitalone',title:'Capital One',copy:'No generally available savings cash bonus was confirmed. Capital One says account bonuses may be targeted; check for a current code and official terms before relying on any offer.',tag:'No public bonus verified'}
 ];
 entries.forEach(o=>{const p=data.products.find(x=>x.id===o.id); const card=document.createElement('article'); card.className='card'; const h=document.createElement('h3');h.textContent=o.title;card.append(h,badge(o.tag,o.id==='citi'||o.id==='barclays-aarp'||o.id==='usbank'?'yellow':'green'));const para=document.createElement('p');para.textContent=o.copy;card.append(para,sourceLink(p.offerSource,'Official offer / promotion source'));host.append(card);});
}
function renderIndex(data){
 const best=data.products.filter(p=>p.apy!==null&&p.rateStatus!=='unverified').sort((a,b)=>b.apy-a.apy)[0];
 const bestRate=document.querySelector('#best-rate'); if(bestRate)bestRate.textContent=`${best.apyLabel} APY`;
 const bestName=document.querySelector('#best-name');if(bestName)bestName.textContent=`${best.bank} — ${best.product}`;
 const tbody=document.querySelector('#shortlist tbody'); if(tbody){data.products.filter(p=>p.apy!==null&&p.rateStatus!=='unverified').sort((a,b)=>b.apy-a.apy).slice(0,7).forEach(p=>{const tr=document.createElement('tr');td(tr,`${p.bank} — ${p.product}`);td(tr,rateText(p));const [label,cls]=sourceStatus(p.rateStatus);td(tr,badge(label,cls));td(tr,sourceLink(p.rateSource,'Official rate'));tbody.append(tr);});}
}
function renderFlags(){
 const host=document.querySelector('#flags');if(!host)return;
 const flags=[
  {title:'Capital One APY rendering conflict',text:'The official account-comparison page lists 3.20% APY as of 2026-10-21, while the separate 360 Performance Savings product page and linked disclosure rendered “NaN” on 2026-10-22. The comparison-page value is used only as a flagged provisional input; confirm with Capital One at opening.',links:[['Comparison page','https://www.capitalone.com/bank/open-an-account/?sourceApplication=PSP_WEB'],['Product page','https://www.capitalone.com/bank/savings-accounts/online-performance-savings-account/'],['Disclosure','https://www.capitalone.com/bank/disclosures/savings-accounts/online-performance-savings-account/']]},
  {title:'Chase Savings APY not confirmed for New York',text:'Chase requires a ZIP code to display the live rate table and says rates may vary by market. The rates table therefore leaves APY and projected returns blank; no national or out-of-market rate was substituted.',links:[['Chase rate page','https://www.chase.com/personal/savings/savings-account/interest-rates']]},
  {title:'Bank of America APY not confirmed for New York',text:'Bank of America’s official rate page requires ZIP/county selection and routes users to local rate PDFs. No current New York product rate was confirmed during this review, so the rate and modeled return remain blank.',links:[['BofA rate page','https://www.bankofamerica.com/deposits/bank-account-interest-rates/']]},
  {title:'U.S. Bank rate is location-specific and New York rate remains unconfirmed',text:'The current rate page continued to show its default ZIP 55402 even when opened with a 10001 query and displayed a temporary rate-service warning. Its advertised “up to 3.50%” relationship APY is therefore not used as a New York rate; APY and projections are blank until the exact ZIP-specific disclosure is confirmed.',links:[['Smartly Savings rate table','https://www.usbank.com/bank-accounts/savings-accounts/bank-smartly-savings/savings-account-interest-rates.html'],['Product and relationship terms','https://www.usbank.com/bank-accounts/savings-accounts/bank-smartly-savings.html']]},
  {title:'Barclays AARP offer end-date discrepancy',text:'The directly linked Barclays Select Savings page gives an explicit $400 offer deadline of 2026-10-31. AARP’s partner offer page search result showed a later 2027-01-31 deadline. The dashboard uses Barclays’ own current product-page terms and flags the discrepancy; reconfirm the offer deadline in the application flow.',links:[['Barclays product and offer terms','https://banking.us.barclays/select-home/savings.html'],['AARP member offer page','https://www.aarp.org/membership/benefits/finance/select-savings-from-barclays/']]},
  {title:'Citi promotion expires for new openings after the snapshot date',text:'The 0.98% New York APY is a one-year blended illustration of a 3.75% promotional rate for up to three months and the then-current standard rate. The offer is for accounts opened no later than 2026-10-22, requires at least $25,000 in New-to-Citibank Funds, and is not a recurring standard APY. Projections after one year are intentionally blank.',links:[['Citi official promotional disclosure','https://banking.citi.com/cbol/OM/checking/tiered/featured-offers/default.htm'],['Citi savings account terms','https://www.citi.com/banking/savings-account']]},
  {title:'Barclays deposit accounts share one FDIC limit',text:'Barclays Tiered Savings and AARP Select Savings are both deposits at Barclays Bank Delaware. They do not receive separate $250,000 single-owner coverage merely because they are different products. Combine their balances and accrued interest with any other Barclays deposits in the same ownership category.',links:[['Barclays Tiered Savings and FDIC information','https://banking.us.barclays/tiered-savings.html'],['AARP Select Savings and FDIC information','https://banking.us.barclays/select-home/savings.html'],['FDIC coverage rules','https://www.fdic.gov/resources/deposit-insurance/faq']]},
  {title:'An insured-cap-sized principal can become partly uninsured as interest accrues',text:'A $250,000 principal deposit leaves no room for accrued interest under the standard $250,000 single-owner limit. At an unchanged 4.25% APY, $240,000 would grow to about $250,200 after one year. The $235,000 scenario is shown as a buffer illustration, but other same-bank deposits, rate changes, or account ownership can reduce coverage headroom.',links:[['FDIC coverage FAQ','https://www.fdic.gov/resources/deposit-insurance/faq'],['FDIC EDIE estimator','https://edie.fdic.gov/']]},
  {title:'Marcus cash-bonus search result was not live',text:'A search result exposed a Marcus savings cash-bonus page with tiered bonus amounts, but direct access returned an error page. It is not treated as a current confirmed offer. The live referral rate boost is included instead.',links:[['Unavailable result URL','https://www.marcus.com/us/en/savings/osa-savingsbonus'],['Live referral terms','https://www.marcus.com/us/en/savings/referrals']]},
  {title:'Security comparison is not an independent audit',text:'The reviewed official sources confirm mobile/online access, FDIC coverage, and bank-published security controls where available. They do not support an independent comparative security score or an assurance that any app is risk-free. Enable multifactor authentication where offered and use each bank’s current security guidance.',links:[['FDIC deposit insurance','https://www.fdic.gov/resources/deposit-insurance/faq'],['Ally published security approach','https://www.ally.com/security/our-approach/'],['Capital One security','https://www.capitalone.com/bank/security-fraud-protection/']]},
  {title:'FDIC coverage may be reduced by other deposits at that bank',text:'For a single-owner account, all deposits at the same insured bank in the same ownership category are aggregated, including accrued interest. Capital One specifically notes that certain Discover Bank deposits opened on or after 2025-05-18 count with Capital One deposits. Check all holdings and account titling; $250,000 is not a per-account limit.',links:[['FDIC FAQ','https://www.fdic.gov/resources/deposit-insurance/faq'],['Capital One / Discover note','https://www.capitalone.com/updates/discover/savings/']]}
 ];
 flags.forEach(f=>{const a=document.createElement('article');a.className='card';const h=document.createElement('h3');h.textContent=f.title;a.append(h);const p=document.createElement('p');p.textContent=f.text;a.append(p);f.links.forEach(([label,url],i)=>{if(i)a.append(document.createTextNode(' · '));a.append(sourceLink(url,label));});host.append(a);});
}
fetch(DATA_URL).then(r=>{if(!r.ok)throw new Error('Could not load verified account data');return r.json()}).then(data=>{renderIndex(data);renderRates(data);renderAccounts(data);renderOfferCards(data);renderFlags();document.querySelectorAll('[data-asof]').forEach(e=>e.textContent=data.asOf);document.querySelectorAll('[data-method]').forEach(e=>e.textContent=data.method);document.querySelectorAll('[data-fdic]').forEach(e=>e.textContent=data.fdic.rule);}).catch(e=>{const m=document.querySelector('#load-error');if(m){m.hidden=false;m.textContent=e.message}});
