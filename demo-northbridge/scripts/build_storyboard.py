"""Replay the authored Northbridge fixture from extracted sources. Not a general IM author."""
import json,math,re,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ex=json.loads((root/'working/extracted.json').read_text(encoding='utf-8'));sources=ex['sources'];by={s['id']:s for s in sources}
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

gross=[cell(f'PnL!{c}8') for c in 'BCDEF'];opex=[-cell(f'PnL!{c}9') for c in 'BCDEF']
gm=[g/r for g,r in zip(gross,rev)];oc=[o/r for o,r in zip(opex,rev)]
qmargin=[float(q['ebitda_gbp_m'])/float(q['revenue_gbp_m']) for q in quarters]
calc('COST_RATIOS','Gross profit / revenue; operating expenses / revenue',['FIN23','FIN24','FIN25','FIN26','FIN27'],{'gross_margin':gm,'opex_ratio':oc},'ratio')
calc('PROFIT_BRIDGE','FY2025 minus FY2023: revenue, gross profit, operating expenses and EBITDA',['FIN23','FIN25'],{'revenue':rev[2]-rev[0],'gross_profit':gross[2]-gross[0],'opex':opex[2]-opex[0],'ebitda':eb[2]-eb[0]},'GBP million')
calc('QUARTER_MARGINS','Quarter EBITDA / quarter revenue; Q4 / full year',['QUARTERS','FIN25'],{'margins':qmargin,'q4_revenue_share':float(quarters[3]['revenue_gbp_m'])/rev[2],'q4_ebitda_share':float(quarters[3]['ebitda_gbp_m'])/eb[2]},'ratio')
calc('RENEWAL_LOSS','Due agreements minus renewed; due annual value minus retained value',['RENEWALS'],{'agreements':renewal['due_count']-renewal['renewed_count'],'annual_value':renewal['due_value']-renewal['retained_value']},'count / GBP million')
calc('EXPIRY_TOTAL_SHARE','FY2025 revenue attributed to 2026 expiries / total FY2025 revenue',['EXPIRIES','FIN25'],float(expiries[0]['fy2025_maintenance_revenue_gbp_m'])/rev[2],'ratio')
calc('ENGINEER_MIX','Total headcount minus engineers; engineers / headcount; future year-end engineer growth',['OPS','BRIDGE'],{'non_engineers':heads-engineers,'share':engineers/heads,'growth_2026':int(bridge[6]['fy2026_gbp_m'])/engineers-1,'growth_2027':int(bridge[6]['fy2027_gbp_m'])/int(bridge[6]['fy2026_gbp_m'])-1},'ratio')
growth=[rev[i]/rev[i-1]-1 for i in range(1,5)]
calc('REVENUE_GROWTH','Current revenue / prior year revenue - 1',['FIN23','FIN24','FIN25','FIN26','FIN27'],growth,'ratio')
calc('FORECAST_CONTRIBUTION','Each forecast movement / net revenue increase',['BRIDGE'],{k:[float(r[k])/(float(bridge[5][k])-float(bridge[0][k])) for r in bridge[1:5]] for k in ['fy2026_gbp_m','fy2027_gbp_m']},'ratio')

sector_combined=sum(float(r['fy2025_revenue_gbp_m']) for r in sectors if r['sector'] in ['Logistics','Manufacturing'])
calc('SECTOR_COMBINATION','Logistics revenue + manufacturing revenue',['SECTORS'],sector_combined,'GBP million')

blue='#00338D';black='#000000';grey='#595959';slides=[];claims=[]
def text(s,id,x,y,w,h,t,size=16.5,color=black,bold=False,ids=(),cs=(),align='left'):
 s['elements'].append(dict(id=id,type='text',x=x,y=y,w=w,h=h,text=t,size=size,color=color,bold=bold,align=align,fact_ids=list(ids),calc_ids=list(cs)))
def line(s,id,x,y,w,color='#B8C7DF'):s['elements'].append(dict(id=id,type='rule',x=x,y=y,w=w,h=1,color=color,fact_ids=[]))
def table(s,id,x,y,w,h,rows,widths,ids,align=None,emphasis=None,cs=(),size=16):
 s['elements'].append(dict(id=id,type='table',x=x,y=y,w=w,h=h,rows=rows,widths=widths,size=size,fact_ids=list(ids),calc_ids=list(cs),column_align=align or ['left']*len(widths),emphasis_rows=emphasis or []))
def chart(s,id,x,y,w,h,cats,vals,ids,maxv,unit='GBP million',fmt='0.0',cs=()):
 s['elements'].append(dict(id=id,type='chart',x=x,y=y,w=w,h=h,categories=cats,values=vals,series_name=unit,max=maxv,format=fmt,unit=unit,color=blue,fact_ids=list(ids),calc_ids=list(cs)))
def page(title,section,source,ids):
 s=dict(title=title,background='#FFFFFF',elements=[],notes=[]);slides.append(s);n=len(slides)
 text(s,f's{n}-section',56,20,1168,20,section.upper(),13,blue,True)
 text(s,f's{n}-title',56,47,1168,42,title,28,blue,True,ids)
 line(s,f's{n}-header-rule',56,98,1168,blue)
 text(s,f's{n}-source',56,656,1168,29,source,10.5,blue,ids=ids)
 line(s,f's{n}-footer-rule',56,691,1168)
 text(s,f's{n}-footer',56,697,1080,17,'NORTHBRIDGE     FICTIONAL TRAINING CASE     January 2026',10,grey)
 text(s,f's{n}-number',1184,697,40,17,str(n),10,blue,align='right')
 return s
def heading(s,id,x,y,w,t,ids=()):text(s,id,x,y,w,25,t,19,blue,True,ids)
def para(s,id,x,y,w,h,t,ids=(),cs=()):text(s,id,x,y,w,h,t,16.5,black,False,ids,cs)

s=dict(title='Project Northbridge',background='#FFFFFF',elements=[],notes=[]);slides.append(s)
text(s,'cover-label',56,40,1168,24,'FICTIONAL TRANSACTION CASE',14,blue,True)
text(s,'cover-title',56,137,1168,69,'Project Northbridge',46,blue,True,['BUS'])
text(s,'cover-subtitle',56,221,1168,43,'Information memorandum',28,blue)
line(s,'cover-rule',56,288,1168,blue)
text(s,'cover-company',56,319,1168,65,'Northbridge Field Services Ltd\nUK equipment maintenance and technical field support',23,black,ids=['BUS','SERVICES'])
para(s,'cover-description',56,411,720,109,f'Founded in 2012, Northbridge provides scheduled maintenance, reactive repairs and installation services from three UK hubs. FY2025 management revenue is a provisional £{rev[2]:.1f}m, including £{svc[0]/1000:.1f}m of maintenance activity. Shareholders are considering a sale of 70%–100% of the equity.', ['BUS','OPS','SERVICES','FIN25','MIX','DEAL'])
text(s,'cover-date',858,411,366,80,'January 2026\nDraft for discussion\nStandalone UK company',18,blue,ids=['DEAL'])
line(s,'cover-agenda-rule',56,548,1168)
text(s,'cover-agenda',56,571,1168,69,'02 Overview      03 Investment case      04 Services      05 Customers\n06 Operations      07 Financials      08 Forecast      09 Transaction      10 Diligence',16,grey)
text(s,'cover-fiction',56,666,1168,30,'All companies, people and figures are fictional. Management financial information is unaudited.\nFY2025 revenue remains subject to reconciliation with the earlier company brief.',11,grey,ids=['CONFLICT','FIN_UPDATE'])

s=page('Company overview and proposed transaction','Executive summary','Sources: 01 company brief; 02 model, PnL / ServiceMix / CustomerSales; 05 commercial interview; 10 CFO follow-up; 13 transaction workshop.\nA = unaudited management actuals. FY2025 revenue is provisional. Detailed source locators are in notes.', ['BUS','SERVICES','FIN25','MIX','OPS','DEAL','CONFLICT','FIN_UPDATE','PROCESS','RENEWALS'])
para(s,'s2-intro',56,113,1168,63,'Northbridge provides equipment maintenance and technical field support to UK logistics, manufacturing and facilities-management customers. The business combines planned visits under annual service arrangements with reactive repairs and separately scoped installation work.', ['BUS','COMMERCIAL','SECTORS'])
table(s,'s2-profile',56,191,650,264,[['Business profile','FY2025 / current position'],['Founded / headquarters','2012 / Birmingham'],['Revenue / EBITDA',f'£{rev[2]:.1f}m / £{eb[2]:.1f}m, before any proposed add-backs'],['Historical development',f'FY2023–25 revenue CAGR {cagr:.1%}; EBITDA margin {margin[2]:.1%}'],['Service revenue',f'Maintenance £{svc[0]/1000:.1f}m; repairs £{svc[1]/1000:.1f}m; projects £{svc[2]/1000:.1f}m'],['People and footprint',f'{heads} employees, including {engineers} field engineers; three UK hubs'],['Customer exposure',f'Largest customer {largest:.0%}; top five {top:.0%} of revenue']],[2.1,4.4],['BUS','FIN25','FIN23','MIX','OPS','CUSTOMERS'],cs=['CAGR','MARGINS','NORMALIZE','TOP5','LARGEST'])
heading(s,'s2-business-head',738,191,486,'Revenue characteristics',['COMMERCIAL','RENEWALS'])
para(s,'s2-business',738,224,486,149,f'Maintenance accounts for {mix[0]:.0%} of revenue. Agreements generally last one to three years, with renewal by agreement and price reviews subject to terms and customer acceptance.\n\nIn the FY2025 due-for-renewal cohort, {renewal["renewed_count"]} of {renewal["due_count"]} agreements renewed. Retained annual value was £{renewal["retained_value"]:.2f}m on a £{renewal["due_value"]:.2f}m starting base, before price or scope changes.', ['MIX','COMMERCIAL','RENEWALS'],['MIX_SHARE','RENEWAL_RATES'])
heading(s,'s2-sale-head',738,391,486,'Ownership and sale scope',['DEAL','PROCESS'])
para(s,'s2-sale',738,424,486,214,'Founder ownership is 70%, management 20% and the seed investor 10%. The proposed sale is 70%–100% of the standalone UK company, including its hubs, operating assets and customer contracts.\nThe process is at preparation stage. No valuation, rollover, financing structure or timetable has been agreed. Contract consents and legal title require review.\nThe FY2027 forecast depends on contract wins and hiring. Pipeline remains unsigned.', ['DEAL','PROCESS','BRIDGE','PIPELINE'])
heading(s,'s2-reporting-head',56,478,650,'Reporting basis and unresolved revenue difference',['CONFLICT','FIN_UPDATE'])
para(s,'s2-reporting',56,511,650,127,f'The CFO supports provisional use of the £{rev[2]:.1f}m management model. The earlier briefing reports £{legacy:.1f}m, a £{legacy-rev[2]:.1f}m difference. A possible £0.8m order-timing item has not been reconciled to invoices or the ledger.\n\nQuarterly figures agree to the annual model. Cash and bank debt drafts are available. No QoE or verified add-backs support normalised earnings.', ['CONFLICT','FIN_UPDATE','BALANCE','QUARTERS'],['REVENUE_GAP'])

s=page('Investment considerations','Investment case','Sources: 02 management model; 05 commercial interview; 06 hubs; 07 KPIs; 08 expiries; 10 CFO follow-up; 11 forecast bridge.\nAnalysis uses provisional, unaudited management data. Agreement renewal is distinct from customer retention.', ['MIX','RENEWALS','FIN23','FIN25','HUBS','KPIS','EXPIRIES','BRIDGE','FIN_UPDATE'])
table(s,'s3-case',56,115,1168,381,[['Investment consideration','Evidence and commercial interpretation','Qualification'],['Maintenance-led service mix',f'£{svc[0]/1000:.1f}m of maintenance revenue ({mix[0]:.0%} of sales) provides an established base of planned service activity. One-to-three-year agreements define visit scope and annual fees.','£6.0m of FY2025 maintenance revenue relates to agreements expiring in 2026. Continued revenue depends on renewal and agreed scope.'],['Historical earnings growth',f'Revenue rose from £{rev[0]:.1f}m to £{rev[2]:.1f}m in FY2023–25. Gross profit increased by £{gross[2]-gross[0]:.1f}m, while operating expenses increased by £{opex[2]-opex[0]:.1f}m. Management EBITDA rose by £{eb[2]-eb[0]:.1f}m.','The P&L shows arithmetic improvement in gross margin and expense ratios. It does not establish the underlying operational causes. FY2025 revenue remains provisional.'],['Regional delivery capacity',f'{engineers} field engineers across three hubs support customer service. Management reports {rates[0]:.1%} urgent-response compliance and {rates[1]:.1%} first-time fix rates, with defined job denominators.','KPI records have not been independently tested. Founder-led major accounts and local engineer capacity need review alongside renewal exposure.'],['Identified expansion assumptions',f'FY2026 revenue growth of £{rev[3]-rev[2]:.1f}m comprises £1.0m pricing, £2.0m new contracts, £1.6m cross-sell and £0.6m attrition. Engineers increase to 95 at year end.','The £4.8m opportunity pipeline is unsigned and unweighted. Customer-level forecast support, recruitment costs and engineer ramp-up timing remain outstanding.']],[1.8,4.6,4.2],['MIX','COMMERCIAL','EXPIRIES','FIN23','FIN25','OPS','KPIS','BRIDGE','PIPELINE','FIN_UPDATE'],cs=['MIX_SHARE','PROFIT_BRIDGE','KPI_RATES'])
heading(s,'s3-renewal-head',56,517,568,'Renewal evidence',['RENEWALS'])
para(s,'s3-renewal',56,550,568,91,f'{renewal["renewed_count"]} of {renewal["due_count"]} agreements renewed ({renewcount:.0%}). The £{renewal["due_value"]-renewal["retained_value"]:.2f}m reduction in annual value represents {1-renewvalue:.0%} of the starting cohort. This measure excludes price changes and new scope. The earlier 94% customer-retention estimate remains undefined.', ['RENEWALS','RETENTION'],['RENEWAL_RATES','RENEWAL_LOSS'])
heading(s,'s3-concentration-head',656,517,568,'Concentration and positioning',['CUSTOMERS','SECTORS','MARKET'])
para(s,'s3-concentration',656,550,568,91,f'The top five customers account for {top:.0%} of revenue. Logistics and manufacturing account for £{sector_combined:.1f}m combined. The information supplied does not substantiate market share, a leadership position or the size of the addressable market.', ['CUSTOMERS','SECTORS','MARKET'],['TOP5','SECTOR_COMBINATION'])

s=page('Service portfolio and customer sectors','Business overview','Sources: 02 model, ServiceMix!A5:C7; 05 commercial interview; 12 sector mix; 04 CFO units confirmation.\nFY2025 provisional management actuals. Service figures converted from GBP thousand to GBP million.', ['MIX','COMMERCIAL','SECTORS','UNITS','FIN25'])
table(s,'s4-services',56,115,1168,247,[['Service','£m','Share','Scope and pricing','Commercial characteristics'],['Scheduled maintenance',f'{svc[0]/1000:.1f}',f'{mix[0]:.0%}','Planned inspections and preventive servicing, with scheduled visits and an annual fee.','One-to-three-year agreements. Renewal and price reviews depend on terms and customer acceptance.'],['Reactive repairs',f'{svc[1]/1000:.1f}',f'{mix[1]:.0%}','Call-out, labour and materials charges for reactive equipment support.','Management plans to convert repair customers to maintenance agreements. Conversion is assumed.'],['Installation projects',f'{svc[2]/1000:.1f}',f'{mix[2]:.0%}','Separately agreed project scope and price.','Project-specific timing and scope. No project backlog schedule supplied.'],['Total',f'{rev[2]:.1f}','100%','Recognised revenue for the same UK company.','Excludes VAT. Agrees to the provisional model.']],[2.1,.7,.7,4.0,4.3],['MIX','COMMERCIAL','FIN25','UNITS','FORECAST_BASIS'],['left','right','right','left','left'],[4],['MIX_SHARE','NORMALIZE'])
heading(s,'s4-sector-head',56,381,480,'Industry revenue profile',['SECTORS'])
table(s,'s4-sector',56,414,480,151,[['Customer sector','£m','Share']]+[[r['sector'],f'{float(r['fy2025_revenue_gbp_m']):.2f}',f'{float(r['fy2025_revenue_gbp_m'])/rev[2]:.0%}'] for r in sectors],[3.1,1,1],['SECTORS','FIN25'],['left','right','right'],cs=['SECTOR_SHARE'])
para(s,'s4-sector-comment',56,582,480,59,'Industry totals describe the current customer base. They do not establish the size of the wider market or a market-share position.', ['SECTORS','MARKET'])
heading(s,'s4-commercial-head',568,381,656,'Revenue durability and cross-sell',['COMMERCIAL','BRIDGE'])
para(s,'s4-commercial',568,414,656,227,'Maintenance revenue is the value of services recognised during FY2025. Neither its 70% share nor the current agreement term establishes guaranteed future revenue. Contract expiry, visit scope and renewal terms determine the relevant commercial exposure.\n\nManagement’s FY2026 bridge includes £1.6m of cross-sell and £1.0m of pricing. The interview identifies repair customers as a route to additional maintenance agreements, but no customer-level conversion schedule links these assumptions to specific accounts.\n\nSector and service schedules are separate views of the same £25.0m revenue. A combined service-by-sector matrix has not been supplied, so the data cannot show which industries generate each service line.', ['COMMERCIAL','MIX','BRIDGE','FIN_UPDATE','SECTORS','FIN25'],['MIX_SHARE'])

s=page('Customer exposure, expiry profile and renewals','Customer quality','Sources: 02 model, CustomerSales!A5:C10; 05 commercial interview; 08 contract expiries.\nExpiry cohorts allocate FY2025 maintenance revenue, not future backlog. Renewal measures cover agreements due in FY2025.', ['CUSTOMERS','EXPIRIES','RENEWALS','RETENTION','COMMERCIAL'])
heading(s,'s5-chart-head',56,115,548,'Largest customers: FY2025 revenue share',['CUSTOMERS'])
chart(s,'s5-chart',56,151,548,212,['A','B','C','D','E'],[v/sum(cust) for v in cust[:5]],['CUSTOMERS'],.16,'Share of FY2025 revenue','0.0%',cs=['TOP5','LARGEST'])
para(s,'s5-exposure',56,376,548,105,f'The largest customer contributes £{cust[0]/1000:.2f}m ({largest:.0%} of revenue). The five largest together contribute £{sum(cust[:5])/1000:.2f}m ({top:.0%}). The remaining £{cust[5]/1000:.2f}m is an aggregate across other customers.\nMaya Reed remains the primary executive contact on major accounts. Deputy account ownership has not been documented.', ['CUSTOMERS','COMMERCIAL'],['TOP5','LARGEST','NORMALIZE'])
heading(s,'s5-renewal-head',56,502,548,'What the renewal cohort measures',['RENEWALS'])
para(s,'s5-renewal',56,535,548,106,f'{renewal['renewed_count']} of {renewal['due_count']} agreements renewed ({renewcount:.0%}). Retained annual value was £{renewal['retained_value']:.2f}m / £{renewal['due_value']:.2f}m ({renewvalue:.0%}), excluding price and scope changes. The difference is £{renewal['due_value']-renewal['retained_value']:.2f}m.\nAn agreement cohort may contain multiple contracts per customer. It cannot validate the earlier undefined 94% customer-retention estimate.', ['RENEWALS','RETENTION'],['RENEWAL_RATES','RENEWAL_LOSS'])
heading(s,'s5-expiry-head',636,115,588,'Maintenance agreements by expiry year',['EXPIRIES'])
table(s,'s5-expiry',636,151,588,159,[['Expiry year','FY2025 £m','Maintenance share']]+[[r['expiry_year'],f'{float(r['fy2025_maintenance_revenue_gbp_m']):.1f}',f'{float(r['fy2025_maintenance_revenue_gbp_m'])/(svc[0]/1000):.1%}'] for r in expiries],[1.7,1.3,2.7],['EXPIRIES','MIX'],['left','right','right'],cs=['EXPIRY_SHARE'])
para(s,'s5-expiry-comment',636,327,588,105,f'Agreements expiring in 2026 account for £{float(expiries[0]['fy2025_maintenance_revenue_gbp_m']):.1f}m of FY2025 revenue, equivalent to {float(expiries[0]['fy2025_maintenance_revenue_gbp_m'])/rev[2]:.0%} of total company revenue. This is the amount associated with the expiry cohort, rather than an estimate of revenue loss.\nThe schedule does not establish signed future revenue, renewal timing or the amount already renegotiated.', ['EXPIRIES','MIX','FIN25'],['EXPIRY_TOTAL_SHARE'])
heading(s,'s5-review-head',636,454,588,'Contract review priorities',['COMMERCIAL','PROCESS'])
para(s,'s5-review',636,487,588,154,'Commercial review needs to link each expiry to its customer, service scope and renewal status, then test pricing clauses and termination rights against the signed agreement.\nReview of change-of-control provisions is also required for the proposed sale. No conclusion on transferability or consent requirements is available. The supplied concentration schedule and expiry schedule do not identify which major accounts sit in the 2026 expiry cohort.', ['COMMERCIAL','PROCESS','CUSTOMERS','EXPIRIES'])

s=page('Operating footprint and delivery capacity','Operations','Sources: 01 company brief; 06 hub schedule; 07 service KPIs; 11 forecast bridge; 13 transaction workshop.\nHeadcount at 31 December 2025. KPIs are management-reported FY2025 measures with defined denominators.', ['OPS','HUBS','KPIS','BRIDGE','PROCESS'])
table(s,'s6-hubs',56,115,664,195,[['Hub','Revenue £m','Revenue share','Employees','Engineers']]+[[r['hub'],f'{float(r['fy2025_revenue_gbp_m']):.1f}',f'{float(r['fy2025_revenue_gbp_m'])/rev[2]:.0%}',r['employees_20251231'],r['field_engineers_20251231']] for r in hubs]+[['Total',f'{rev[2]:.1f}','100%',str(heads),str(engineers)]],[2,1.25,1.5,1.2,1.2],['HUBS','OPS','FIN25'],['left','right','right','right','right'],[4],['HUB_SHARE'])
heading(s,'s6-kpi-head',752,115,472,'Service KPIs and definitions',['KPIS'])
for i,(r,rate) in enumerate(zip(kpis,rates)):
 y=151+i*86;a,b=int(r['numerator']),int(r['denominator'])
 text(s,f's6-kpi{i}',752,y,472,24,f'{r['metric']}: {rate:.1%}',18,blue,True,['KPIS'],['KPI_RATES'])
 defs=[f'{a:,} of {b:,} eligible urgent jobs attended within four hours.',f'{a:,} of {b:,} closed reactive jobs resolved on the first visit.',f'{a:,} productive / {b:,} available engineer hours. Recorded hours are not billing utilisation.']
 para(s,f's6-definition{i}',752,y+29,472,52,defs[i],['KPIS'])
heading(s,'s6-footprint-head',56,330,664,'Staffing and regional mix',['OPS','HUBS'])
para(s,'s6-footprint',56,363,664,86,f'Birmingham is the largest hub by revenue and engineers. Engineers account for {engineers/heads:.1%} of employees. The remaining {heads-engineers} roles lack a functional breakdown.\nYear-end headcount does not establish average deployed capacity or utilisation by hub.', ['HUBS','OPS'],['ENGINEER_MIX'])
heading(s,'s6-management-head',56,470,664,'Management responsibilities',['PROCESS'])
table(s,'s6-team',56,503,664,138,[['Executive','Current responsibility'],['Maya Reed, CEO','Key accounts and pipeline evidence'],['Daniel Cole, CFO','Financial reporting and QoE preparation'],['Aisha Patel, COO','Service delivery and engineer recruitment']],[2.3,4.3],['OPS','PROCESS'])
heading(s,'s6-plan-head',752,422,472,'Engineer plan and execution requirements',['BRIDGE'])
para(s,'s6-plan',752,455,472,186,f'The forecast increases year-end engineers from {engineers} to {bridge[6]['fy2026_gbp_m']} in 2026F and {bridge[6]['fy2027_gbp_m']} in 2027F. The first-year increase is {int(bridge[6]['fy2026_gbp_m'])/engineers-1:.1%}, compared with revenue growth of {growth[2]:.1%}.\n\nA hiring schedule is needed to explain start dates, replacement hires and time to productive deployment. KPI source records also require testing for job eligibility and incomplete records. Current data does not support a quantified productivity uplift.', ['OPS','BRIDGE','FIN25','FIN26','FIN_UPDATE','KPIS'],['ENGINEER_MIX','REVENUE_GROWTH'])

s=page('Historical earnings and quarterly trading','Financial analysis','Sources: 02 model, PnL!B5:D11; 09 quarterly accounts; 10 CFO follow-up; 01 company brief.\nGBP million unless stated. Year ending 31 December. A = unaudited management actuals. FY2025 revenue is provisional.', ['FIN23','FIN24','FIN25','QUARTERS','CONFLICT','FIN_UPDATE'])
rows=[['','FY2023A','FY2024A','FY2025A']]
for label,row in [('Revenue',6),('Cost of services',7),('Gross profit',8),('Operating expenses',9),('EBITDA',10),('EBITDA margin',11)]:
 vals=[cell(f'PnL!{c}{row}') for c in 'BCD'];rows.append([label]+[f'{v:.1%}' if row==11 else f'({abs(v):.1f})' if v<0 else f'{v:.1f}' for v in vals])
rows += [['Gross margin']+[f'{v:.1%}' for v in gm[:3]],['Operating expenses / revenue']+[f'{v:.1%}' for v in oc[:3]]]
table(s,'s7-pnl',56,115,684,305,rows,[3.1,1.25,1.25,1.25],['FIN23','FIN24','FIN25'],['left','right','right','right'],[1,3,5],['MARGINS','COST_RATIOS'])
heading(s,'s7-quarter-head',772,115,452,'FY2025 quarterly detail',['QUARTERS'])
table(s,'s7-quarter',772,151,452,207,[['£m','Revenue','EBITDA','Margin']]+[[r['quarter'].split()[0],f'{float(r['revenue_gbp_m']):.2f}',f'{float(r['ebitda_gbp_m']):.2f}',f'{qmargin[i]:.1%}'] for i,r in enumerate(quarters)]+[['FY2025',f'{rev[2]:.2f}',f'{eb[2]:.2f}',f'{margin[2]:.1%}']],[1.2,1.2,1.2,1.2],['QUARTERS','FIN25'],['left','right','right','right'],[5],['QUARTER_MARGINS','MARGINS'])
para(s,'s7-quarter-comment',772,375,452,112,f'Q4 accounts for {float(quarters[3]['revenue_gbp_m'])/rev[2]:.1%} of annual revenue and {float(quarters[3]['ebitda_gbp_m'])/eb[2]:.1%} of EBITDA. Its {qmargin[3]:.1%} margin exceeds the {margin[2]:.1%} full-year result.\nOne year of quarterly data does not establish a recurring seasonal pattern.', ['QUARTERS','FIN25'],['QUARTER_MARGINS','MARGINS'])
heading(s,'s7-bridge-head',56,440,684,'Arithmetic explanation of EBITDA growth',['FIN23','FIN25'])
para(s,'s7-bridge',56,473,684,168,f'FY2023–25 revenue increased by £{rev[2]-rev[0]:.1f}m ({cagr:.1%} CAGR). Gross profit increased by £{gross[2]-gross[0]:.1f}m, against £{opex[2]-opex[0]:.1f}m of additional operating expenses, resulting in £{eb[2]-eb[0]:.1f}m of EBITDA growth.\n\nGross margin increased from {gm[0]:.1%} to {gm[2]:.1%}. Operating expenses fell from {oc[0]:.1%} to {oc[2]:.1%} of revenue. These ratios explain the P&L movement but do not identify the effects of pricing, labour rates or service mix.\n\nThe £{legacy:.1f}m earlier revenue estimate remains unreconciled to the £{rev[2]:.1f}m model.', ['FIN23','FIN25','CONFLICT'],['CAGR','PROFIT_BRIDGE','COST_RATIOS'])
heading(s,'s7-earnings-head',772,510,452,'Reported earnings basis',['FIN_UPDATE'])
para(s,'s7-earnings',772,543,452,98,'Management proposed £0.18m of founder-remuneration and £0.12m of systems adjustments. Neither is substantiated. The £5.0m EBITDA shown includes no add-backs. QoE and revenue cut-off work remain outstanding.', ['FIN_UPDATE','FIN25'])

s=page('Management forecast and revenue bridge','Management outlook','Sources: 02 model, PnL!D6:F11; 05 commercial interview; 10 CFO follow-up; 11 forecast bridge.\nA = provisional management actuals. F = management forecast. Pipeline amounts are unsigned, unweighted annual revenue opportunities.', ['FIN25','FIN26','FIN27','BRIDGE','PIPELINE','FIN_UPDATE'])
heading(s,'s8-chart-head',56,115,432,'Revenue trajectory (£m)',['FIN25','FIN26','FIN27'])
chart(s,'s8-chart',56,151,432,203,['2025A','2026F','2027F'],rev[2:],['FIN25','FIN26','FIN27'],40)
table(s,'s8-profit',56,371,432,145,[['','2025A','2026F','2027F'],['EBITDA £m']+[f'{v:.1f}' for v in eb[2:]],['EBITDA margin']+[f'{v:.1%}' for v in margin[2:]],['YE engineers',str(engineers),bridge[6]['fy2026_gbp_m'],bridge[6]['fy2027_gbp_m']]],[1.9,1,1,1],['FIN25','FIN26','FIN27','OPS','BRIDGE'],['left','right','right','right'],cs=['MARGINS'])
para(s,'s8-capacity',56,535,432,106,f'Revenue increases by {growth[2]:.1%} in 2026F and {growth[3]:.1%} in 2027F. EBITDA margins reach {margin[4]:.1%} by 2027F. Hiring costs, staff start dates and productivity ramp-up have not been supplied to support delivery of these outcomes.', ['FIN25','FIN26','FIN27','FIN_UPDATE','BRIDGE'],['REVENUE_GROWTH','MARGINS'])
table(s,'s8-bridge',520,115,704,259,[['Revenue bridge (£m)','2026F','2027F']]+[[r['component']]+[f'({abs(float(r[k])):.2f})' if float(r[k])<0 else f'{float(r[k]):.2f}' for k in ['fy2026_gbp_m','fy2027_gbp_m']] for r in bridge[:6]],[4.2,1.4,1.4],['BRIDGE'],['left','right','right'],[1,6],['FORECAST_TIE'])
heading(s,'s8-assumptions-head',520,395,704,'Growth composition and commercial support',['BRIDGE','PIPELINE'])
para(s,'s8-assumptions',520,428,704,213,f'FY2026 growth of £{rev[3]-rev[2]:.1f}m comprises £1.0m pricing, £2.0m new contracts and £1.6m cross-sell, less £0.6m attrition. New contracts provide {float(bridge[2]['fy2026_gbp_m'])/(rev[3]-rev[2]):.0%} of the net increase.\n\nThe £{pipe[0]:.1f}m pipeline comprises proposals (£{pipe[1]:.1f}m), negotiations (£{pipe[2]:.1f}m) and preferred-supplier positions (£{pipe[3]:.1f}m). All opportunities are unsigned. Stage labels do not establish award probability, delivery timing or recognised revenue.\n\nPricing requires customer acceptance. Cross-sell depends on converting repair customers to maintenance agreements. The bridge reconciles at group level, but no customer-level schedule links the forecast to renewal exposure, opportunity timing or engineer capacity.', ['BRIDGE','PIPELINE','FIN25','FIN26','COMMERCIAL','FIN_UPDATE'],['FORECAST_CONTRIBUTION','FORECAST_TIE'])

s=page('Transaction perimeter and draft financial position','Transaction overview','Sources: 01 company brief; 10 CFO follow-up; 13 transaction workshop.\nGBP million. Draft balances at 31 December 2025. Sale scope and transaction terms remain proposals.', ['DEAL','PROCESS','BALANCE','FIN_UPDATE'])
table(s,'s9-ownership',56,115,424,151,[['Shareholder','Ownership'],['Founder','70%'],['Management','20%'],['Seed investor','10%']],[2.8,1.4],['DEAL'],['left','right'])
heading(s,'s9-perimeter-head',56,285,424,'Proposed equity sale',['PROCESS','DEAL'])
para(s,'s9-perimeter',56,318,424,176,'Shareholders are considering a 70%–100% sale of the standalone UK company. The proposed perimeter includes all three hubs, operating assets and customer contracts. No excluded business has been identified.\n\nLegal entity scope, asset ownership and contract transferability require confirmation. No offers or signed sale terms exist in this fictional case.', ['PROCESS','DEAL'])
heading(s,'s9-process-head',56,515,424,'Preparation status',['PROCESS'])
para(s,'s9-process',56,548,424,93,'Valuation, rollover, financing and timing remain unagreed. The CFO owns financial preparation, the COO owns capacity evidence and the CEO owns key-account continuity. Legal counsel has not been appointed.', ['PROCESS'])
table(s,'s9-balances',512,115,712,270,[['Draft balance / subtotal','£m','Interpretation'],['Cash',f'{bal['cash']:.1f}','Restricted cash has not been assessed'],['Bank term debt',f'{bal['term_debt']:.1f}','Other debt-like items have not been assessed'],['Bank debt less cash',f'{bal['term_debt']-bal['cash']:.1f}','Limited arithmetic subtotal only'],['Trade receivables',f'{bal['receivables']:.1f}','No ageing or collectability schedule supplied'],['Inventory',f'{bal['inventory']:.1f}','No inventory quality review supplied'],['Trade payables',f'{bal['payables']:.1f}','Other working-capital balances are missing'],['Trade working capital',f'{bal['receivables']+bal['inventory']-bal['payables']:.1f}','Receivables + inventory − trade payables']],[3.0,.7,4.4],['BALANCE'],['left','right','left'],[3,7],['LIMITED_NET_DEBT','TRADE_WC'])
heading(s,'s9-bridge-head',512,407,712,'Requirements for an enterprise-to-equity bridge',['BALANCE','PROCESS'])
para(s,'s9-bridge',512,440,712,201,'Bank term debt less reported cash is £2.4m. This is not a concluded transaction net-debt figure: leases, tax balances, debt-like items and restricted cash have not been assessed. No enterprise value has been agreed.\nThe £2.7m trade working-capital snapshot excludes other balances and does not describe monthly seasonality. A normalised working-capital target cannot be established from a single year-end balance.\nThe deal team needs complete balance schedules and agreed transaction definitions before preparing an enterprise-to-equity bridge. Management’s draft figures are inputs to that work, rather than an equity-value conclusion.', ['BALANCE','PROCESS'],['LIMITED_NET_DEBT','TRADE_WC'])

s=page('Diligence workplan and evidence gaps','Preparation priorities','Sources: 05 commercial interview; 07 service KPIs; 10 CFO follow-up; 11 forecast bridge; 13 transaction workshop.\nWorkplan interpretation is based on identified evidence gaps. Named owners reflect management preparation responsibilities.', ['CONFLICT','FIN_UPDATE','BALANCE','RENEWALS','KPIS','BRIDGE','PROCESS','MARKET'])
table(s,'s10-diligence',56,115,1168,450,[['Workstream','Current evidence / issue','Next deliverable and purpose','Owner'],['Revenue and earnings',f'Annual and quarterly schedules agree to £{rev[2]:.1f}m. The £{legacy:.1f}m briefing remains unreconciled. Proposed EBITDA add-backs are unsupported.','Revenue ledger-to-invoice reconciliation with cut-off testing. QoE review and item-level adjustment support to establish the earnings basis.','CFO'],['Net debt and working capital','Cash, bank debt and trade balances are preliminary. Leases, debt-like items and monthly seasonality are missing.','Full balance schedules, restricted-cash assessment and monthly working-capital history to define transaction adjustments.','CFO'],['Customers and renewals','A defined 25-agreement cohort and expiry allocation are available. The earlier customer-retention estimate remains undefined.','Matched agreement-level renewal records, expiry status and account coverage. Review pricing and termination terms to assess revenue exposure.','CEO'],['Service delivery and capacity','Hub headcount and three KPIs have stated denominators. No job-level validation or detailed hiring/ramp-up plan is available.','Job record extracts and eligibility rules. Engineer recruitment dates, replacement needs and cost assumptions to test delivery capacity.','COO'],['Forecast conversion','Group revenue bridge reconciles. All pipeline stages remain unsigned and customer-level support is absent.','Customer-by-customer revenue bridge, opportunity timing and signed awards. Link growth to renewals, cross-sell and engineer availability.','CFO / CEO'],['Legal perimeter and market','The proposal includes operating assets and contracts. Consents and title are unreviewed. Independent market evidence is absent.','Legal perimeter and consent schedule. Separate independent market work before using market-size, share or leadership claims.','Legal / strategy']],[1.55,3.8,4.5,1.0],['CONFLICT','FIN_UPDATE','BALANCE','RENEWALS','EXPIRIES','KPIS','BRIDGE','PIPELINE','PROCESS','MARKET'])
heading(s,'s10-sequence-head',56,578,1168,'Implications for transaction preparation',['PROCESS','FIN_UPDATE'])
para(s,'s10-sequence',56,610,1168,42,'The unresolved revenue basis affects historical performance, forecast opening balances and earnings analysis. Contract and capacity work must then test whether the management plan can convert into recognised revenue. Timing remains to be agreed.', ['CONFLICT','FIN_UPDATE','BRIDGE','PROCESS'])

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
(root/'working/evidence-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding="utf-8")
(root/'working/storyboard.json').write_text(json.dumps({'title':'Project Northbridge — Information Memorandum','synthetic':True,'style_profile':'advisory-dense','slides':slides},ensure_ascii=False,indent=2),encoding="utf-8")
(root/'working/issue-register.json').write_text(json.dumps(issues,indent=2),encoding="utf-8")
(root/'working/input-manifest.json').write_text(json.dumps(ledger['sources'],indent=2),encoding="utf-8")
print(f'Built {len(slides)} slides, {len(facts)} facts, {len(calcs)} calculations, {len(claims)} claim mappings')
