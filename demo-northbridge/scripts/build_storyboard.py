"""Replay the authored Northbridge fixture from extracted sources. Not a general IM author."""
import json,math,re,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ex=json.loads((root/'working/extracted.json').read_text());sources=ex['sources'];by={s['id']:s for s in sources}
for s in sources:
 if s['status']!='extracted':raise ValueError('Unreviewed input '+s['path'])
def cell(loc):
 a=next(x for x in by['02']['items'] if x['locator']==loc)
 if not isinstance(a['value'],(float,int)):raise ValueError('Missing cached numeric value '+loc)
 return float(a['value'])
def ref(sid,needle):
 a=next(x for x in by[sid]['items'] if needle in x['text']);return {'source_id':sid,'path':by[sid]['path'],'locator':a['locator'],'excerpt':a['text']}
def xref(loc):
 a=next(x for x in by['02']['items'] if x['locator']==loc);return {'source_id':'02','path':by['02']['path'],'locator':loc,'excerpt':a['text']}
facts=[];calcs=[];issues=[]
def fact(fid,claim,value,unit,period,basis,refs,status='source_supported',limitations=''):
 facts.append(dict(id=fid,claim=claim,raw_value=value,value=value,unit=unit,period=period,basis=basis,scope='Northbridge standalone UK company',source_refs=refs,status=status,limitations=limitations,synthetic=True));return fid
rev=[cell(f'PnL!{c}6') for c in 'BCDEF'];eb=[cell(f'PnL!{c}10') for c in 'BCDEF'];margin=[e/r for e,r in zip(eb,rev)];cust=[cell('CustomerSales!C'+str(r)) for r in range(5,11)];svc=[cell('ServiceMix!B'+str(r)) for r in range(5,8)]
assert math.isclose(sum(cust)/1000,rev[2],abs_tol=1e-8),'Customer schedule fails P&L tie-out'
assert math.isclose(sum(svc)/1000,rev[2],abs_tol=1e-8),'Service schedule fails P&L tie-out'
for i,c in enumerate('BCDEF'):
 assert math.isclose(cell(f'PnL!{c}8'),cell(f'PnL!{c}6')+cell(f'PnL!{c}7'),abs_tol=1e-8)
 assert math.isclose(eb[i],cell(f'PnL!{c}8')+cell(f'PnL!{c}9'),abs_tol=1e-8)
 fact(f'FIN{i+23}',f'FY20{i+23} financial statements',{'revenue':rev[i],'cost':cell(f'PnL!{c}7'),'gross_profit':cell(f'PnL!{c}8'),'opex':cell(f'PnL!{c}9'),'ebitda':eb[i],'margin':margin[i]},'GBP million / ratio',f'FY20{i+23}', 'actual' if i<3 else 'forecast',[xref(f'PnL!{c}{r}') for r in [5,6,7,8,9,10,11]],'provisional_conflict' if i==2 else 'source_supported','Unaudited management figures; FY2025 revenue conflict remains open.')
legacyref=ref('01','preliminary FY2025 revenue estimate');legacy=float(re.search(r'GBP ([0-9.]+) million',legacyref['excerpt']).group(1))
fact('CONFLICT','FY2025 revenue difference',{'model':rev[2],'briefing':legacy},'GBP million','FY2025','actual',[xref('PnL!D6'),legacyref,ref('04','provisional basis')],'provisional_conflict','Use model provisionally under CFO instruction; do not call reconciled.')
fact('BUS','Business and founding',2012,'year','January 2026','management assertion',[ref('01','was founded in 2012')])
fact('SERVICES','Services and contract terms',None,'text','FY2025','management assertion',[ref('01','Contracts generally run')])
fact('MIX','FY2025 service revenue',svc,'GBP thousand','FY2025','actual',[xref(f'ServiceMix!{c}{r}') for r in range(5,8) for c in 'ABC'])
fact('CUSTOMERS','FY2025 customer sales',cust,'GBP thousand','FY2025','actual',[xref(f'CustomerSales!{c}{r}') for r in range(5,11) for c in 'ABC'],limitations='OTHER is an aggregate.')
opsref=ref('01','120 employees');txt=opsref['excerpt'];heads=int(re.search(r'(\d+) employees',txt).group(1));engineers=int(re.search(r'(\d+) field engineers',txt).group(1))
fact('OPS','People, hubs and management',{'employees':heads,'engineers':engineers,'hubs':['Birmingham','Manchester','Bristol']},'headcount / places','31 December 2025','management assertion',[opsref])
fact('GROWTH','Management growth plan',20,'net engineers added','by FY2027','forecast',[ref('01','20 net field engineers'),ref('03','Growth depends')])
fact('MARKET','Market size and share unavailable',None,'not available','January 2026','management assertion',[ref('01','No independent market-size')],'missing','Fragmentation is a management assertion without independent support.')
fact('RETENTION','Retention estimate lacks defined basis',.94,'ratio','FY2025','management assertion',[ref('03','94%')],'management_unverified','No definition or cohort data; excluded from quantitative investment highlights.')
fact('DEAL','Ownership and proposed sale',{'founder':.7,'management':.2,'seed':.1,'sale_min':.7,'sale_max':1},'equity fraction','January 2026','proposal',[ref('01','founder holds 70%')])
fact('QOE','Financial diligence evidence unavailable',None,'not available','January 2026','management assertion',[ref('03','normalisation bridge')],'missing','No QoE, cash, debt or working-capital evidence.')
fact('UNITS','Financial and sales schedule units',{'pnl':'GBP million','sales':'GBP thousand'},'text','FY2025','management assertion',[ref('04','P&L tab is in GBP millions')])
fact('FORECAST_BASIS','Forecast bridge unavailable',None,'not available','FY2026-FY2027','forecast',[ref('04','no customer-level forecast bridge')],'missing')
def calc(cid,formula,inputs,result,unit):
 calcs.append(dict(id=cid,formula=formula,input_ids=inputs,result=result,unit=unit,rounding='Full precision internally; one decimal for GBP million and most percentages'))
cagr=(rev[2]/rev[0])**.5-1;fcagr=(rev[4]/rev[2])**.5-1;top=sum(cust[:5])/sum(cust);largest=max(cust[:5])/sum(cust);mix=[v/sum(svc) for v in svc]
calc('CAGR','(FY2025 revenue / FY2023 revenue)^(1/2) - 1',['FIN23','FIN25'],cagr,'ratio')
calc('FCAGR','(FY2027F revenue / FY2025A revenue)^(1/2) - 1',['FIN25','FIN27'],fcagr,'ratio')
calc('TOP5','sum(CustomerSales!C5:C9) / sum(CustomerSales!C5:C10)',['CUSTOMERS'],top,'ratio')
calc('LARGEST','max(CustomerSales!C5:C9) / sum(CustomerSales!C5:C10)',['CUSTOMERS'],largest,'ratio')
calc('MIX_SHARE','ServiceMix!B5:B7 / sum(ServiceMix!B5:B7)',['MIX'],mix,'ratio')
calc('NORMALIZE','GBP thousand / 1000',['MIX','CUSTOMERS','UNITS'],{'services_m':[v/1000 for v in svc],'customers_m':[v/1000 for v in cust]},'GBP million')
calc('MARGINS','Each period EBITDA / same period revenue',['FIN23','FIN24','FIN25','FIN26','FIN27'],margin,'ratio')
calc('REVENUE_GAP','Briefing FY2025 revenue minus model FY2025 revenue',['CONFLICT'],legacy-rev[2],'GBP million')
issues=[
 dict(id='I01',severity='high',topic='Revenue conflict',facts=['CONFLICT'],treatment=f'GBP {rev[2]:.1f}m model used provisionally, GBP {legacy:.1f}m alternative disclosed.',request='Reconcile recognised revenue to orders, invoices and general ledger.',owner_role='CFO'),
 dict(id='I02',severity='resolved_normalization',topic='Unit mismatch',facts=['UNITS'],treatment='GBP 000 divided by 1,000; service and customer totals tie to GBP 25.0m.',request='Retain source units and normalization formula.',owner_role='Deal analyst'),
 dict(id='I03',severity='open',topic='Undefined retention',facts=['RETENTION'],treatment='94% excluded from numerical investment highlights.',request='Define customer or revenue retention and provide matched cohorts.',owner_role='Commercial diligence'),
 dict(id='I04',severity='open',topic='Market evidence',facts=['MARKET'],treatment='No market size, market share or leadership claim.',request='Provide independent market study and competitor analysis.',owner_role='Strategy team'),
 dict(id='I05',severity='high',topic='Financial diligence',facts=['QOE'],treatment='EBITDA labelled management-reported and unaudited.',request='Provide QoE, normalisation, debt, cash and working capital schedules.',owner_role='Financial diligence'),
 dict(id='I06',severity='open',topic='Forecast support',facts=['FORECAST_BASIS','GROWTH'],treatment='Forecasts explicitly labelled F, subject to hiring and renewals.',request='Provide customer-level revenue bridge, signed pipeline and recruitment costs.',owner_role='CFO / COO')]
import csv
def records(sid):
 return list(csv.DictReader([i['text'] for i in by[sid]['items'] if not i['text'].startswith('#')]))
def allrefs(sid):return [ref(sid,i['text']) for i in by[sid]['items']]
def supplemental(fid,sid,claim,value,unit='text',period='FY2025',basis='management assertion',limitations='Unaudited synthetic management submission.'):
 return fact(fid,claim,value,unit,period,basis,allrefs(sid),limitations=limitations)
hubs=records('06');kpis=records('07');expiries=records('08');quarters=records('09');bridge=records('11');sectors=records('12')
assert math.isclose(sum(float(r['fy2025_revenue_gbp_m']) for r in hubs),rev[2]),'Hub revenue fails tie-out'
assert sum(int(r['employees_20251231']) for r in hubs)==heads,'Hub headcount fails tie-out'
assert sum(int(r['field_engineers_20251231']) for r in hubs)==engineers,'Engineer count fails tie-out'
assert math.isclose(sum(float(r['fy2025_revenue_gbp_m']) for r in sectors),rev[2]),'Sector revenue fails tie-out'
assert math.isclose(sum(float(r['fy2025_maintenance_revenue_gbp_m']) for r in expiries),svc[0]/1000),'Contract expiry schedule fails tie-out'
assert math.isclose(sum(float(r['revenue_gbp_m']) for r in quarters),rev[2]),'Quarterly revenue fails tie-out'
assert math.isclose(sum(float(r['ebitda_gbp_m']) for r in quarters),eb[2]),'Quarterly EBITDA fails tie-out'
for j,col in enumerate(['fy2026_gbp_m','fy2027_gbp_m']):
 assert math.isclose(float(bridge[0][col]),rev[j+2]),'Forecast opening mismatch'
 assert math.isclose(sum(float(r[col]) for r in bridge[:5]),float(bridge[5][col])),'Forecast bridge fails tie-out'
 assert math.isclose(float(bridge[5][col]),rev[j+3]),'Forecast model mismatch'
assert int(bridge[6]['fy2027_gbp_m'])-engineers==20,'Engineer plan mismatch'
supplemental('HUBS','06','Hub revenue and year-end headcount',hubs,'GBP million / headcount')
supplemental('KPIS','07','Defined service delivery measures',kpis,'counts / hours')
supplemental('EXPIRIES','08','Maintenance revenue by agreement expiry year',expiries,'GBP million',limitations='FY2025 recognised revenue assigned to expiry cohorts. Not future contracted backlog.')
supplemental('QUARTERS','09','Quarterly revenue and management EBITDA',quarters,'GBP million')
supplemental('BRIDGE','11','Group-level forecast revenue bridge and engineer plan',bridge,'GBP million / headcount','FY2026-FY2027','forecast',limitations='Group-level management assumptions. No customer bridge, signed pipeline or recruitment cost schedule.')
supplemental('SECTORS','12','Revenue by customer industry',sectors,'GBP million')
supplemental('COMMERCIAL','05','Service scope, pricing and account relationships',None)
supplemental('PROCESS','13','Proposed transaction perimeter and preparation responsibilities',None,period='26 January 2026',basis='proposal')
cohort=ref('05','renewal cohort')['excerpt']
renewal={'due_count':int(re.search(r'comprised (\d+) maintenance',cohort)[1]),'renewed_count':int(re.search(r'(\d+) agreements renewed',cohort)[1]),'due_value':float(re.search(r'GBP ([\d.]+) million of annual',cohort)[1]),'retained_value':float(re.search(r'GBP ([\d.]+) million\. These',cohort)[1])}
fact('RENEWALS','Defined maintenance agreement renewal cohort',renewal,'count / GBP million','FY2025','management assertion',[ref('05','renewal cohort'),ref('05','earlier 94%')],limitations='Contract-level management cohort. Excludes price changes and additional scope. Not customer retention and not independently verified.')
pipeline=ref('05','Pipeline at')['excerpt'];pipe=[float(v) for v in re.findall(r'GBP ([\d.]+) million',pipeline)]
assert math.isclose(pipe[0],sum(pipe[1:])),'Pipeline does not sum'
fact('PIPELINE','Unsigned unweighted opportunity pipeline',pipe,'GBP million annual revenue','26 January 2026','management assertion',[ref('05','Pipeline at')],limitations='All unsigned. Not backlog or forecast revenue.')
balance=ref('10','draft schedule shows')['excerpt'];wc=ref('10','Draft trade receivables')['excerpt']
bal={'cash':float(re.search(r'cash ([\d.]+) and',balance)[1]),'term_debt':float(re.search(r'debt ([\d.]+)\.',balance)[1]),'receivables':float(re.search(r'are ([\d.]+),',wc)[1]),'inventory':float(re.search(r'inventory ([\d.]+) and',wc)[1]),'payables':float(re.search(r'payables ([\d.]+) at',wc)[1])}
fact('BALANCE','Draft limited balance-sheet schedule',bal,'GBP million','31 December 2025','management assertion',[ref('10','draft schedule shows'),ref('10','Draft trade receivables')],limitations='Missing leases, tax, debt-like items, restricted cash and other working-capital items. No normalised working capital.')
fact('FIN_UPDATE','Updated financial diligence status',None,'text','26 January 2026','management assertion',[ref('10','provisionally'),ref('10','proposed EBITDA adjustments'),ref('10','quality-of-earnings'),ref('10','supplemental forecast')],limitations='Revenue conflict remains open. No verified EBITDA add-backs, QoE or customer-level forecast support.')
for f in facts:
 if f['id'] in ['QOE','FORECAST_BASIS']:f['limitations']+=' Historical submission. See FIN_UPDATE, BALANCE and BRIDGE for supplemental evidence dated 26 January 2026.'
rates=[float(r['numerator'])/float(r['denominator']) for r in kpis]
assert all(0<=r<=1 for r in rates),'Invalid KPI rates'
renewcount=renewal['renewed_count']/renewal['due_count'];renewvalue=renewal['retained_value']/renewal['due_value']
calc('KPI_RATES','Numerator / denominator for each defined service KPI',['KPIS'],rates,'ratio')
calc('RENEWAL_RATES','Renewed contracts / due contracts; retained pre-price value / due annual value',['RENEWALS'],[renewcount,renewvalue],'ratio')
calc('EXPIRY_SHARE','FY2025 revenue in each expiry cohort / FY2025 maintenance revenue',['EXPIRIES','MIX'],[float(r['fy2025_maintenance_revenue_gbp_m'])/(svc[0]/1000) for r in expiries],'ratio')
calc('SECTOR_SHARE','Sector revenue / FY2025 total revenue',['SECTORS','FIN25'],[float(r['fy2025_revenue_gbp_m'])/rev[2] for r in sectors],'ratio')
calc('HUB_SHARE','Hub revenue / FY2025 total revenue',['HUBS','FIN25'],[float(r['fy2025_revenue_gbp_m'])/rev[2] for r in hubs],'ratio')
calc('LIMITED_NET_DEBT','Bank term debt minus cash only',['BALANCE'],bal['term_debt']-bal['cash'],'GBP million')
calc('TRADE_WC','Trade receivables + inventory - trade payables',['BALANCE'],bal['receivables']+bal['inventory']-bal['payables'],'GBP million')
calc('FORECAST_TIE','Opening revenue + price + new contracts + cross-sell + attrition',['BRIDGE'],[sum(float(r[k]) for r in bridge[:5]) for k in ['fy2026_gbp_m','fy2027_gbp_m']],'GBP million')
issues[2].update(treatment='94% customer retention remains excluded. Separate management contract-cohort renewal rates are disclosed with definitions.',request='Verify the 25-agreement cohort and define the earlier customer retention claim.',facts=['RETENTION','RENEWALS'])
issues[4].update(facts=['FIN_UPDATE','BALANCE'],treatment='Draft cash, bank debt and trade balances received. No EBITDA add-backs applied.',request='Obtain QoE, full debt-like and cash schedules, and monthly normalised working capital.')
issues[5].update(facts=['BRIDGE','PIPELINE','GROWTH'],treatment='Group-level bridge supplied and tied to model. Pipeline remains unsigned.',request='Provide customer-level bridge, signed awards, hiring costs and engineer ramp-up timing.')
issues.append(dict(id='I07',severity='open',topic='Operational evidence and consents',facts=['KPIS','PROCESS'],treatment='Management KPIs have defined denominators. Contract consents remain unreviewed.',request='Validate job records and contract change-of-control provisions.',owner_role='COO / legal counsel'))

blue='#00338D';black='#000000';grey='#595959';slides=[];claims=[]
def text(s,id,x,y,w,h,t,size=18,color=black,bold=False,ids=(),cs=()):
 s['elements'].append(dict(id=id,type='text',x=x,y=y,w=w,h=h,text=t,size=size,color=color,bold=bold,fact_ids=list(ids),calc_ids=list(cs)))
def line(s,id,x,y,w,color='#B8C7DF'):s['elements'].append(dict(id=id,type='rule',x=x,y=y,w=w,h=1,color=color,fact_ids=[]))
def table(s,id,x,y,w,h,rows,widths,ids,align=None,emphasis=None,cs=()):
 s['elements'].append(dict(id=id,type='table',x=x,y=y,w=w,h=h,rows=rows,widths=widths,size=17,fact_ids=list(ids),calc_ids=list(cs),column_align=align or ['left']*len(widths),emphasis_rows=emphasis or []))
def chart(s,id,x,y,w,h,cats,vals,ids,maxv,unit='GBP million',fmt='0.0',cs=()):
 s['elements'].append(dict(id=id,type='chart',x=x,y=y,w=w,h=h,categories=cats,values=vals,series_name=unit,max=maxv,format=fmt,unit=unit,color=blue,fact_ids=list(ids),calc_ids=list(cs)))
def page(title,section,source,ids):
 s=dict(title=title,background='#FFFFFF',elements=[],notes=[]);slides.append(s);n=len(slides)
 text(s,f's{n}-section',72,28,1136,22,section,16,blue,True)
 text(s,f's{n}-title',72,61,1136,78,title,34,blue,True,ids)
 text(s,f's{n}-source',72,650,1136,34,source,12,blue,ids=ids)
 line(s,f's{n}-footer-rule',72,691,1136)
 text(s,f's{n}-footer',72,697,1050,18,'NORTHBRIDGE     FICTIONAL TRAINING CASE     January 2026',11,grey)
 text(s,f's{n}-number',1170,697,38,18,str(n),11,blue)
 return s
def heading(s,id,x,y,w,t,ids):text(s,id,x,y,w,29,t,21,blue,True,ids)

s=dict(title='Project Northbridge',background='#FFFFFF',elements=[],notes=[]);slides.append(s)
text(s,'cover-label',72,62,1136,28,'FICTIONAL TRANSACTION CASE',18,blue,True)
text(s,'cover-title',72,198,1136,90,'Project Northbridge',54,blue,True,['BUS'])
text(s,'cover-subtitle',72,304,1136,54,'Information memorandum',34,blue)
line(s,'cover-rule',72,389,1136,blue)
text(s,'cover-company',72,423,1000,82,'Northbridge Field Services Ltd\nEquipment maintenance and technical field support in the UK',23,black,ids=['BUS','SERVICES'])
text(s,'cover-date',72,554,900,56,'January 2026\nDraft for discussion',19,grey)
text(s,'cover-fiction',72,665,1136,35,'All companies, people and figures are fictional. Management information is unaudited.',12,grey)
s=page('Business and transaction overview','Executive summary','Sources: 01 company brief; 02 management model, PnL and ServiceMix; 10 CFO follow-up; 13 transaction workshop.\nA = management actuals. FY2025 revenue remains provisional. Full locators are in slide notes.', ['BUS','SERVICES','FIN25','MIX','OPS','DEAL','CONFLICT','FIN_UPDATE','PROCESS'])
text(s,'s2-intro',72,147,1136,64,'Northbridge provides planned equipment maintenance, reactive repairs and installation services to UK industrial and commercial sites. The company operates through three regional hubs.',20,ids=['BUS','SERVICES','OPS'])
table(s,'s2-profile',72,236,695,292,[['Company profile','Current position'],['Founded / headquarters','2012 / Birmingham'],['FY2025 revenue / EBITDA',f'£{rev[2]:.1f}m / £{eb[2]:.1f}m (management-reported)'],['Revenue mix',f'Maintenance {mix[0]:.0%}, repairs {mix[1]:.0%}, projects {mix[2]:.0%}'],['Employees / field engineers',f'{heads} / {engineers} at 31 December 2025'],['Proposed sale','70%–100% of equity in the standalone UK company']],[2.7,4.6],['BUS','FIN25','MIX','OPS','DEAL'],cs=['MIX_SHARE'])
heading(s,'s2-transaction-head',807,236,401,'Transaction preparation',['PROCESS'])
text(s,'s2-transaction',807,278,401,126,'The proposed perimeter includes the three hubs, operating assets and customer contracts. Shareholders have not agreed valuation, rollover or a timetable.',18,ids=['PROCESS'])
heading(s,'s2-status-head',807,431,401,'Financial status',['FIN_UPDATE'])
text(s,'s2-status',807,473,401,151,'Draft quarterly and balance-sheet schedules are available. No QoE report or verified EBITDA adjustments support the earnings presented. Contract and legal review remains outstanding.',18,ids=['FIN_UPDATE','BALANCE','PROCESS'])
line(s,'s2-rule',72,558,695)
text(s,'s2-reconciliation',72,578,695,62,f'The £{legacy:.1f}m earlier briefing differs from the £{rev[2]:.1f}m model. The CFO supports provisional use of the model while reconciliation remains open.',18,blue,ids=['CONFLICT'])
s=page('Investment case and supporting evidence','Investment case','Sources: 02 management model; 05 commercial interview; 06 hub schedule; 10 CFO follow-up; 11 forecast bridge.\nAll figures are synthetic management submissions. Renewal metrics refer to agreements, not customers.', ['MIX','SERVICES','FIN23','FIN25','OPS','GROWTH','RENEWALS','CONFLICT','FIN_UPDATE','BRIDGE'])
table(s,'s3-case',72,148,1136,347,[['Investment theme','Supporting evidence','Qualification / diligence focus'],['Maintenance activity',f'£{svc[0]/1000:.1f}m maintenance revenue, or {mix[0]:.0%} of FY2025 sales. Agreements typically run one to three years.','Renewal requires agreement. Validate contract scope, expiry profile and pricing clauses.'],['Historical development',f'Revenue grew from £{rev[0]:.1f}m in FY2023 to a provisional £{rev[2]:.1f}m in FY2025 ({cagr:.1%} CAGR).','The earlier briefing reports a different FY2025 revenue figure. Earnings remain unaudited.'],['Delivery footprint',f'{engineers} engineers across Birmingham, Manchester and Bristol. Total employees: {heads}.','Validate service KPIs against job records and test engineer capacity by region.'],['Management expansion plan',f'Forecast revenue of £{rev[4]:.1f}m in FY2027, supported by pricing, new contracts and cross-sell.','Pipeline remains unsigned. Hiring costs and customer-level forecast support are missing.']],[1.6,3.5,3.55],['MIX','SERVICES','FIN23','FIN25','OPS','BRIDGE','FIN27','CONFLICT','FIN_UPDATE','PIPELINE'],cs=['MIX_SHARE','CAGR'])
heading(s,'s3-renewal-head',72,525,535,'Renewal evidence',['RENEWALS'])
text(s,'s3-renewal',72,566,535,70,f'{renewal["renewed_count"]} of {renewal["due_count"]} agreements due in FY2025 renewed ({renewcount:.0%}). Retained annual value was {renewvalue:.0%}, excluding price changes and additional scope.',18,ids=['RENEWALS'],cs=['RENEWAL_RATES'])
heading(s,'s3-concentration-head',647,525,561,'Customer and earnings exposure',['CUSTOMERS','FIN_UPDATE'])
text(s,'s3-concentration',647,566,561,70,f'The five largest customers account for {top:.0%} of revenue. No unverified add-backs are included in the £{eb[2]:.1f}m management EBITDA.',18,ids=['CUSTOMERS','FIN_UPDATE','FIN25'],cs=['TOP5'])
s=page('Service portfolio and customer applications','Business overview','Sources: 02 management model, ServiceMix!A5:C7; 05 commercial interview; 12 sector mix.\nRevenue is FY2025 provisional management actuals. GBP thousand schedules are converted to GBP million.', ['MIX','SERVICES','COMMERCIAL','SECTORS','FIN25','UNITS'])
services=['Scheduled maintenance','Reactive repairs','Installation projects'];terms=['Planned visits and preventive servicing','Call-out, labour and materials','Separately agreed scope and project price']
table(s,'s4-services',72,148,1136,235,[['Service','FY2025 £m','Share','Delivery and commercial basis']]+[[services[i],f'{svc[i]/1000:.1f}',f'{mix[i]:.0%}',terms[i]] for i in range(3)]+[['Total',f'{rev[2]:.1f}','100%','Provisional management revenue']],[2.8,1.2,1,4.2],['MIX','FIN25','COMMERCIAL','UNITS'],['left','right','right','left'],[4],['MIX_SHARE','NORMALIZE'])
heading(s,'s4-sector-head',72,410,535,'Customer industry mix',['SECTORS'])
table(s,'s4-sector',72,450,535,174,[['Industry','FY2025 £m','Share']]+[[r['sector'],f'{float(r["fy2025_revenue_gbp_m"]):.2f}',f'{float(r["fy2025_revenue_gbp_m"])/rev[2]:.0%}'] for r in sectors],[3,1.25,1],['SECTORS','FIN25'],['left','right','right'],cs=['SECTOR_SHARE'])
heading(s,'s4-terms-head',647,410,561,'Commercial terms',['COMMERCIAL'])
text(s,'s4-terms',647,451,561,170,'Maintenance agreements typically run one to three years and require renewal by agreement. Annual price reviews depend on contract terms and customer acceptance.\n\nMaintenance revenue describes historical service mix. Future revenue depends on renewals and contracted scope.',18,ids=['COMMERCIAL','SERVICES'])
s=page('Customer concentration and contract renewal','Customer quality','Sources: 02 management model, CustomerSales!A5:C10; 05 commercial interview; 08 contract expiry schedule.\nExpiry cohorts allocate FY2025 maintenance revenue by current agreement expiry year. They are not backlog.', ['CUSTOMERS','RENEWALS','RETENTION','EXPIRIES','MIX'])
heading(s,'s5-chart-head',72,148,570,'Largest customers: FY2025 revenue share',['CUSTOMERS'])
chart(s,'s5-chart',72,191,570,258,['A','B','C','D','E'],[v/sum(cust) for v in cust[:5]],['CUSTOMERS'],.16,'Share of FY2025 revenue','0.0%',cs=['TOP5','LARGEST'])
text(s,'s5-exposure',72,465,570,76,f'Top five: {top:.0%}. Largest customer: {largest:.0%}. Other customers together represent {1-top:.0%}. The founder remains the executive contact for major accounts.',18,ids=['CUSTOMERS','COMMERCIAL'],cs=['TOP5','LARGEST'])
heading(s,'s5-expiry-head',682,148,526,'Maintenance agreement expiry profile',['EXPIRIES'])
table(s,'s5-expiry',682,191,526,181,[['Expiry','FY2025 £m','Share of maintenance']]+[[r['expiry_year'],f'{float(r["fy2025_maintenance_revenue_gbp_m"]):.1f}',f'{float(r["fy2025_maintenance_revenue_gbp_m"])/(svc[0]/1000):.1%}'] for r in expiries],[1,1.2,2.4],['EXPIRIES','MIX'],['left','right','right'],cs=['EXPIRY_SHARE'])
heading(s,'s5-renewal-head',682,397,526,'FY2025 renewal cohort',['RENEWALS'])
text(s,'s5-renewal',682,439,526,183,f'Agreements renewed: {renewal["renewed_count"]} / {renewal["due_count"]} ({renewcount:.0%}).\nAnnual value retained: £{renewal["retained_value"]:.2f}m / £{renewal["due_value"]:.2f}m ({renewvalue:.0%}), before price or scope changes.\n\nThe earlier 94% retention estimate lacks a defined customer cohort and remains excluded.',18,ids=['RENEWALS','RETENTION'],cs=['RENEWAL_RATES'])
text(s,'s5-review',72,566,570,59,'Commercial review should validate renewal cohorts, pricing provisions and change-of-control requirements.',18,blue,ids=['COMMERCIAL','PROCESS','RENEWALS'])
s=page('Regional delivery capacity and service performance','Operations','Sources: 01 company brief; 06 hub schedule; 07 service KPIs; 11 forecast bridge; 13 transaction workshop.\nHeadcount at 31 December 2025. Service KPIs cover FY2025 and await job-level validation.', ['OPS','HUBS','KPIS','BRIDGE','PROCESS'])
table(s,'s6-hubs',72,148,664,229,[['Hub','FY2025 £m','Employees','Engineers']]+[[r['hub'],f'{float(r["fy2025_revenue_gbp_m"]):.1f}',r['employees_20251231'],r['field_engineers_20251231']] for r in hubs]+[['Total',f'{rev[2]:.1f}',str(heads),str(engineers)]],[2.2,1.25,1.25,1.25],['HUBS','OPS','FIN25'],['left','right','right','right'],[4])
heading(s,'s6-kpi-head',776,148,432,'Service delivery measures',['KPIS'])
for i,(r,rate) in enumerate(zip(kpis,rates)):
 y=193+i*87
 text(s,f's6-kpi{i}',776,y,432,28,f'{r["metric"]}: {rate:.1%}',20,blue,True,['KPIS'],['KPI_RATES'])
 a,b=int(r['numerator']),int(r['denominator'])
 defs=[f'{a:,} of {b:,} eligible urgent jobs attended within four hours.',f'{a:,} of {b:,} closed reactive jobs resolved on the first visit.',f'{a:,} productive / {b:,} available hours. Not billing utilisation.']
 text(s,f's6-definition{i}',776,y+32,432,47,defs[i],17,ids=['KPIS'])
heading(s,'s6-management-head',72,410,664,'Management and account continuity',['OPS','PROCESS'])
table(s,'s6-team',72,451,664,172,[['Executive','Responsibility'],['Maya Reed, CEO','Key accounts and commercial evidence'],['Daniel Cole, CFO','Financial reporting and transaction preparation'],['Aisha Patel, COO','Service delivery, recruitment and capacity']],[2.2,3.7],['OPS','PROCESS'])
heading(s,'s6-capacity-head',776,484,432,'Capacity plan',['BRIDGE','GROWTH'])
text(s,'s6-capacity',776,525,432,98,f'Year-end engineers: {engineers} in 2025, {bridge[6]["fy2026_gbp_m"]} in 2026F and {bridge[6]["fy2027_gbp_m"]} in 2027F. Recruitment costs and productivity ramp-up require support.',18,ids=['BRIDGE','OPS','FIN_UPDATE'])
s=page('Historical financial performance','Financial analysis','Sources: 02 management model, PnL!B5:D11; 09 quarterly accounts; 10 CFO follow-up; 01 earlier company brief.\nGBP million unless stated. Year ending 31 December. A = unaudited management actuals.', ['FIN23','FIN24','FIN25','QUARTERS','CONFLICT','FIN_UPDATE'])
rows=[['','FY2023A','FY2024A','FY2025A']]
for label,row in [('Revenue',6),('Cost of services',7),('Gross profit',8),('Operating expenses',9),('EBITDA',10),('EBITDA margin',11)]:
 vals=[cell(f'PnL!{c}{row}') for c in 'BCD'];rows.append([label]+[f'{v:.1%}' if row==11 else f'({abs(v):.1f})' if v<0 else f'{v:.1f}' for v in vals])
table(s,'s7-pnl',72,148,704,300,rows,[2.5,1.2,1.2,1.2],['FIN23','FIN24','FIN25'],['left','right','right','right'],[1,5,6],['MARGINS'])
heading(s,'s7-quarter-head',816,148,392,'FY2025 quarterly detail',['QUARTERS'])
table(s,'s7-quarter',816,191,392,213,[['£m','Revenue','EBITDA']]+[[r['quarter'].split()[0],f'{float(r["revenue_gbp_m"]):.2f}',f'{float(r["ebitda_gbp_m"]):.2f}'] for r in quarters]+[['FY2025',f'{rev[2]:.2f}',f'{eb[2]:.2f}']],[1.2,1.2,1.2],['QUARTERS','FIN25'],['left','right','right'],[5])
heading(s,'s7-trend-head',72,478,704,'Revenue and profitability',['FIN23','FIN25'])
text(s,'s7-trend',72,520,704,104,f'Revenue grew at {cagr:.1%} CAGR from FY2023 to FY2025. Management EBITDA increased from £{eb[0]:.1f}m to £{eb[2]:.1f}m. EBITDA margin rose from {margin[0]:.1%} to {margin[2]:.1%}.\n\nThe £{legacy:.1f}m earlier revenue estimate remains unreconciled to the £{rev[2]:.1f}m model.',18,ids=['FIN23','FIN25','CONFLICT'],cs=['CAGR','MARGINS'])
heading(s,'s7-quality-head',816,435,392,'Earnings quality',['FIN_UPDATE'])
text(s,'s7-quality',816,478,392,145,'Quarterly totals agree to the annual model. This arithmetic check does not resolve the earlier revenue discrepancy.\n\nNo proposed EBITDA add-backs are included. A QoE report is outstanding.',18,ids=['QUARTERS','FIN25','FIN_UPDATE','CONFLICT'])
s=page('Management forecast and growth assumptions','Management outlook','Sources: 02 management model, PnL!D6:F11; 05 commercial interview; 10 CFO follow-up; 11 forecast bridge.\nA = management actuals, F = management forecast. Pipeline is unsigned and unweighted.', ['FIN25','FIN26','FIN27','BRIDGE','PIPELINE','FIN_UPDATE'])
heading(s,'s8-chart-head',72,148,430,'Revenue (£m)',['FIN25','FIN26','FIN27'])
chart(s,'s8-chart',72,189,430,237,['2025A','2026F','2027F'],rev[2:],['FIN25','FIN26','FIN27'],40)
table(s,'s8-profit',72,444,430,113,[['£m','2025A','2026F','2027F'],['EBITDA']+[f'{v:.1f}' for v in eb[2:]],['Margin']+[f'{v:.1%}' for v in margin[2:]]],[1.5,1,1,1],['FIN25','FIN26','FIN27'],['left','right','right','right'],cs=['MARGINS'])
text(s,'s8-hiring',72,580,430,49,f'Engineer plan: {engineers} to {bridge[6]["fy2027_gbp_m"]} by 2027F. Hiring costs and ramp-up require validation.',18,ids=['OPS','BRIDGE','FIN_UPDATE'])
table(s,'s8-bridge',542,148,666,282,[['Revenue bridge (£m)','2026F','2027F']]+[[r['component']]+[f'({abs(float(r[k])):.2f})' if float(r[k])<0 else f'{float(r[k]):.2f}' for k in ['fy2026_gbp_m','fy2027_gbp_m']] for r in bridge[:6]],[3.5,1.3,1.3],['BRIDGE'],['left','right','right'],[1,6],['FORECAST_TIE'])
heading(s,'s8-pipeline-head',542,458,666,'Commercial support and dependencies',['PIPELINE','BRIDGE'])
text(s,'s8-pipeline',542,500,666,127,f'Unsigned pipeline: £{pipe[0]:.1f}m of indicative annual revenue, comprising proposals (£{pipe[1]:.1f}m), negotiations (£{pipe[2]:.1f}m) and preferred supplier positions (£{pipe[3]:.1f}m).\n\nPricing and cross-sell assumptions require customer acceptance. The group bridge has no supporting customer-level forecast.',18,ids=['PIPELINE','BRIDGE','FIN_UPDATE'])
s=page('Proposed transaction and financial position','Transaction overview','Sources: 01 company brief; 10 CFO follow-up; 13 transaction workshop.\nGBP million. Draft balances at 31 December 2025. Equity sale proposal remains subject to agreement.', ['DEAL','BALANCE','PROCESS','FIN_UPDATE'])
table(s,'s9-ownership',72,148,442,174,[['Shareholder','Ownership'],['Founder','70%'],['Management','20%'],['Seed investor','10%']],[2.8,1.5],['DEAL'],['left','right'])
heading(s,'s9-perimeter-head',72,355,442,'Proposed perimeter',['PROCESS','DEAL'])
text(s,'s9-perimeter',72,396,442,228,'Shareholders are considering a 70%–100% equity sale. The proposed perimeter includes the company’s operating assets, hubs and customer contracts.\n\nValuation, rollover, financing and timing remain unagreed. Legal review must confirm title and required consents.',18,ids=['PROCESS','DEAL'])
table(s,'s9-balances',554,148,654,281,[['Draft balance / subtotal','£m'],['Cash',f'{bal["cash"]:.1f}'],['Bank term debt',f'{bal["term_debt"]:.1f}'],['Bank debt less cash only',f'{bal["term_debt"]-bal["cash"]:.1f}'],['Trade receivables / inventory',f'{bal["receivables"]:.1f} / {bal["inventory"]:.1f}'],['Trade payables',f'{bal["payables"]:.1f}'],['Trade working capital only',f'{bal["receivables"]+bal["inventory"]-bal["payables"]:.1f}']],[4.1,1.6],['BALANCE'],['left','right'],[3,6],['LIMITED_NET_DEBT','TRADE_WC'])
heading(s,'s9-limits-head',554,460,654,'Limitations of the draft balances',['BALANCE'])
text(s,'s9-limits',554,502,654,123,'Lease liabilities, tax, debt-like items and restricted cash have not been assessed. Monthly working-capital seasonality and other balances are missing.\n\nThe limited subtotals do not establish transaction net debt, normalised working capital or an enterprise-to-equity bridge.',18,ids=['BALANCE','FIN_UPDATE'])
s=page('Outstanding diligence and preparation priorities','Diligence agenda','Sources: 05 commercial interview; 07 service KPIs; 10 CFO follow-up; 11 forecast bridge; 13 transaction workshop.\nResponsibility indicates management preparation ownership. External diligence appointments remain open.', ['CONFLICT','FIN_UPDATE','BALANCE','RENEWALS','KPIS','BRIDGE','PROCESS','MARKET'])
table(s,'s10-diligence',72,148,1136,441,[['Workstream','Evidence now available','Next evidence required','Owner'],['Revenue and QoE','Annual and quarterly figures agree. Earlier revenue discrepancy remains.','Ledger reconciliation, cut-off evidence and support for any adjustments.','CFO'],['Balance sheet','Draft cash, bank debt and trade balances.','Full cash/debt-like schedules and monthly working capital.','CFO'],['Customer quality','Defined 25-agreement renewal cohort and expiry schedule.','Contract review, cohort validation and customer retention definition.','CEO'],['Operations','Hub staffing and KPIs with stated denominators.','Job records, staffing capacity, hiring costs and productivity timing.','COO'],['Forecast','Group revenue bridge and unsigned opportunity pipeline.','Customer bridge, signed awards and evidence for pricing/cross-sell.','CFO / CEO'],['Legal and market','Proposed operating perimeter. No independent market study.','Title, consent and change-of-control review. Independent market work.','Legal / strategy']],[1.45,3.1,3.5,1.1],['CONFLICT','FIN_UPDATE','BALANCE','RENEWALS','EXPIRIES','KPIS','BRIDGE','PIPELINE','PROCESS','MARKET'])
text(s,'s10-close',72,608,1136,27,'Transaction preparation remains subject to financial, commercial and legal diligence.',18,blue,True,ids=['PROCESS','FIN_UPDATE'])

fmap={f['id']:f for f in facts};cmap={c['id']:c for c in calcs}
for n,s in enumerate(slides,1):
 used=set();cu=set()
 for e in s['elements']:
  for f in e['fact_ids']:assert f in fmap
  for c in e.get('calc_ids',[]):assert c in cmap
  if e['fact_ids']:
   refs=[r for f in e['fact_ids'] for r in fmap[f]['source_refs']]
   claims.append({'slide':n,'element_id':e['id'],'fact_ids':e['fact_ids'],'calculation_ids':e.get('calc_ids',[]),'source_refs':refs})
   used.update(e['fact_ids']);cu.update(e.get('calc_ids',[]))
 notes=['FICTIONAL TRAINING CASE. All company and financial data are synthetic.']
 for fid in sorted(used):
  f=fmap[fid];notes.append(fid+': '+f['claim']+' ['+f['status']+']\n'+'\n'.join(r['path']+' / '+r['locator']+' — '+r['excerpt'] for r in f['source_refs'])+('\nLimitations: '+f['limitations'] if f['limitations'] else ''))
 for cid in sorted(cu):notes.append(cid+': '+json.dumps(cmap[cid],ensure_ascii=False))
 s['notes']=notes
ledger={'synthetic':True,'sources':[{k:v for k,v in s.items() if k!='items'} for s in sources],'facts':facts,'calculations':calcs,'issues':issues,'slide_claims':claims}
(root/'working/evidence-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2))
(root/'working/storyboard.json').write_text(json.dumps({'title':'Project Northbridge — Information Memorandum','synthetic':True,'style_profile':'advisory-dense','slides':slides},ensure_ascii=False,indent=2))
(root/'working/issue-register.json').write_text(json.dumps(issues,indent=2))
(root/'working/input-manifest.json').write_text(json.dumps(ledger['sources'],indent=2))
print(f'Built {len(slides)} slides, {len(facts)} facts, {len(calcs)} calculations, {len(claims)} claim mappings')
