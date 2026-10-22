"""Build a three-page design pilot from the existing synthetic evidence ledger."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'style-pilot';out.mkdir(exist_ok=True)
ledger=json.loads((root/'working/evidence-ledger.json').read_text())
f={x['id']:x for x in ledger['facts']};c={x['id']:x for x in ledger['calculations']}
v=lambda k:f[k]['value']
profile=json.loads((root.parent/'skills/mna-information-memo/assets/advisory-dense.json').read_text())
blue=profile['primary'];black=profile['text'];slides=[]
def text(s,id,x,y,w,h,t,size=18,color=black,bold=False,ids=(),calc=()):
 s['elements'].append(dict(id=id,type='text',x=x,y=y,w=w,h=h,text=t,size=size,color=color,bold=bold,fact_ids=list(ids),calc_ids=list(calc)))
def line(s,id,x,y,w,color=blue):s['elements'].append(dict(id=id,type='rule',x=x,y=y,w=w,h=1,color=color,fact_ids=[]))
def table(s,id,x,y,w,h,rows,widths,ids,align=None,emphasis=None,calc=()):
 s['elements'].append(dict(id=id,type='table',x=x,y=y,w=w,h=h,rows=rows,widths=widths,size=17,fact_ids=list(ids),calc_ids=list(calc),column_align=align or ['left']*len(widths),emphasis_rows=emphasis or []))
def page(title,section,source,ids):
 s=dict(title=title,background='#FFFFFF',elements=[],notes=[]);slides.append(s);n=len(slides)
 text(s,f'p{n}-section',72,28,1136,22,section,16,blue,True)
 text(s,f'p{n}-title',72,61,1136,78,title,34,blue,True,ids=ids)
 text(s,f'p{n}-source',72,650,1100,34,source,12,blue,ids=ids)
 line(s,f'p{n}-footer-rule',72,691,1136,'#B8C7DF')
 text(s,f'p{n}-footer',72,697,1050,18,'NORTHBRIDGE  |  FICTIONAL TRAINING CASE  |  January 2026',11,'#595959')
 text(s,f'p{n}-number',1170,697,38,18,str(n),11,blue)
 return s
rev=v('FIN25')['revenue'];eb=v('FIN25')['ebitda'];shares=c['MIX_SHARE']['result'];cagr=c['CAGR']['result']
s=page('Investment case: maintenance revenue and historical growth','Investment case | Evidence and qualifications','Sources: company brief; management model (PnL, ServiceMix, CustomerSales); management interview; CFO email.\nFull source locators and calculations are retained in slide notes.', ['MIX','SERVICES','FIN23','FIN25','OPS','GROWTH','CONFLICT','QOE','RETENTION','FORECAST_BASIS','CUSTOMERS'])
table(s,'p1-case',72,148,1136,350,[['Investment theme','Supporting evidence','Qualification / diligence focus'],['Maintenance activity',f'Scheduled maintenance: £{v("MIX")[0]/1000:.1f}m, or {shares[0]:.0%} of FY2025 revenue. Contracts generally run for one to three years.','Renewal is by agreement. The 94% retention estimate has no defined cohort or calculation basis.'],['Historical growth',f'Revenue: £{v("FIN23")["revenue"]:.1f}m in FY2023 to £{rev:.1f}m in FY2025; {cagr:.1%} CAGR. FY2025 EBITDA: £{eb:.1f}m.','FY2025 revenue remains provisional versus £26.2m in the earlier brief. EBITDA is unaudited.'],['Delivery capacity',f'{v("OPS")["engineers"]} field engineers within {v("OPS")["employees"]} employees; hubs in Birmingham, Manchester and Bristol.','The founder leads major customer relationships. Relationship continuity requires diligence.'],['Management growth plan',f'Add {v("GROWTH")} net engineers by FY2027 and cross-sell maintenance to repair customers.','Execution depends on hiring and renewals. A customer-level forecast bridge is unavailable.']],[1.55,3.5,3.6],['MIX','SERVICES','FIN23','FIN25','OPS','GROWTH','CONFLICT','QOE','RETENTION','FORECAST_BASIS'],calc=['MIX_SHARE','NORMALIZE','CAGR'])
text(s,'p1-concentration-head',72,530,535,29,'Customer concentration',21,blue,True,ids=['CUSTOMERS'])
text(s,'p1-concentration',72,568,535,64,f'The top five customers represent {c["TOP5"]["result"]:.0%} of FY2025 revenue; the largest represents {c["LARGEST"]["result"]:.0%}. Contract-level review is required.',18,ids=['CUSTOMERS'],calc=['TOP5','LARGEST'])
text(s,'p1-earnings-head',647,530,561,29,'Earnings evidence',21,blue,True,ids=['QOE'])
text(s,'p1-earnings',647,568,561,64,'No QoE report or EBITDA normalisation bridge has been supplied. Investment conclusions remain subject to financial diligence.',18,ids=['QOE'])
s=page('Scheduled maintenance contributes 70% of FY2025 revenue','Business overview | Services and operating context','Sources: company brief; management model, ServiceMix!A5:C7; CFO email.\nService schedules are in GBP thousand; amounts below are converted to GBP million.', ['BUS','MIX','SERVICES','OPS','CONFLICT','UNITS','CUSTOMERS','RETENTION'])
text(s,'p2-intro',72,146,1136,49,'Founded in 2012, Northbridge provides scheduled maintenance, reactive repairs and installation work for industrial sites, logistics operations and facilities management.',18,ids=['BUS','SERVICES'])
services=['Scheduled maintenance','Reactive repairs','Installation projects'];terms=['Annual service contracts','Call-out and materials','Project-based work']
rows=[['Service','FY2025 £m','Share','Commercial basis']]+[[services[i],f'{v("MIX")[i]/1000:.1f}',f'{shares[i]:.0%}',terms[i]] for i in range(3)]+[['Total',f'{sum(v("MIX"))/1000:.1f}','100%','Ties to the provisional management model']]
table(s,'p2-services',72,218,1136,230,rows,[3,1.2,1,4.2],['MIX','SERVICES','UNITS','FIN25'],['left','right','right','left'],[4],['MIX_SHARE','NORMALIZE'])
text(s,'p2-delivery-head',72,480,535,29,'Delivery footprint',21,blue,True,ids=['OPS'])
text(s,'p2-delivery',72,520,535,93,'Three hubs: Birmingham, Manchester and Bristol.\n85 field engineers within 120 employees at 31 December 2025. The founder leads major customer relationships.',18,ids=['OPS'])
text(s,'p2-contract-head',647,480,561,29,'Contract quality and revenue basis',21,blue,True,ids=['SERVICES','CONFLICT'])
text(s,'p2-contract',647,520,561,112,'Contracts generally run for one to three years, with renewal by agreement. Maintenance share does not establish revenue retention. FY2025 revenue remains provisional: £25.0m in the model versus £26.2m in the earlier brief.',18,ids=['SERVICES','RETENTION','CONFLICT'])
s=page('Revenue reached a provisional £25.0m in FY2025','Financial analysis | Historical management actuals','Sources: management model, PnL!B5:D11; earlier company brief; CFO email; management interview.\nA = management actuals. Figures are unaudited; FY2025 revenue remains provisional.', ['FIN23','FIN24','FIN25','UNITS','CONFLICT','QOE'])
text(s,'p3-units',72,145,1136,24,'GBP million unless stated. Year ending 31 December.',16,'#595959',ids=['UNITS','FIN23','FIN24','FIN25'])
rows=[['','FY2023A','FY2024A','FY2025A']]
for label,key in [('Revenue','revenue'),('Cost of services','cost'),('Gross profit','gross_profit'),('Operating expenses','opex'),('EBITDA','ebitda'),('EBITDA margin','margin')]:
 vals=[v(k)[key] for k in ['FIN23','FIN24','FIN25']]
 rows.append([label]+[f'{a:.1%}' if key=='margin' else f'({abs(a):.1f})' if a<0 else f'{a:.1f}' for a in vals])
table(s,'p3-financials',72,188,704,326,rows,[2.5,1.2,1.2,1.2],['FIN23','FIN24','FIN25'],['left','right','right','right'],[1,5,6],['MARGINS'])
text(s,'p3-analysis-head',816,188,392,29,'Historical development',21,blue,True,ids=['FIN23','FIN24','FIN25'])
text(s,'p3-analysis',816,230,392,175,f'Revenue increased from £18.0m to £25.0m between FY2023 and FY2025 ({cagr:.1%} CAGR).\n\nManagement EBITDA rose from £2.7m to £5.0m. Reported margins were 15.0%, 18.1% and 20.0% across the three years.',18,ids=['FIN23','FIN24','FIN25'],calc=['CAGR','MARGINS'])
text(s,'p3-quality-head',816,426,392,29,'Diligence focus',21,blue,True,ids=['QOE','CONFLICT'])
text(s,'p3-quality',816,468,392,146,'The earnings basis is management-reported. QoE, normalisation, debt, cash and working-capital schedules are unavailable. The revenue difference requires reconciliation before relying on the growth trend.',18,ids=['QOE','CONFLICT'])
line(s,'p3-recon-rule',72,544,704)
text(s,'p3-recon',72,565,704,78,'Revenue reconciliation remains open: £25.0m management model versus £26.2m earlier company brief. The CFO supports provisional use of the model; this does not resolve the difference.',18,blue,ids=['CONFLICT'])
claims=[]
for i,s in enumerate(slides,1):
 ids=set();calcs=set()
 for e in s['elements']:
  ids.update(e['fact_ids']);calcs.update(e.get('calc_ids',[]))
  if e['fact_ids']:claims.append(dict(slide=i,element_id=e['id'],fact_ids=e['fact_ids'],calculation_ids=e.get('calc_ids',[]),source_refs=[r for fid in e['fact_ids'] for r in f[fid]['source_refs']]))
 s['notes']=['FICTIONAL TRAINING CASE. Synthetic Northbridge evidence only.']+[json.dumps(f[k],ensure_ascii=False) for k in sorted(ids)]+[json.dumps(c[k],ensure_ascii=False) for k in sorted(calcs)]
(out/'storyboard.json').write_text(json.dumps(dict(title='Northbridge — advisory design pilot',style_profile='advisory-dense',synthetic=True,slides=slides),ensure_ascii=False,indent=2))
(out/'claim-map.json').write_text(json.dumps(dict(ledger='../working/evidence-ledger.json',slide_claims=claims),ensure_ascii=False,indent=2))
print('Built 3 style pilot pages from existing evidence')
