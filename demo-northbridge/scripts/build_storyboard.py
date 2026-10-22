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
N='#132E42';T='#117F79';M='#586D7C';W='#FFFFFF';A='#99621B';slides=[];claims=[]
def text(sl,id,x,y,w,h,txt,size=24,color=N,bold=False,facts=None,calcs=None,align='left'):
 sl['elements'].append(dict(id=id,type='text',x=x,y=y,w=w,h=h,text=txt,size=size,color=color,bold=bold,align=align,fact_ids=facts or [],calc_ids=calcs or []))
def rule(sl,id,y,x=60,w=1160,color='#DCE4E8'):
 sl['elements'].append(dict(id=id,type='rule',x=x,y=y,w=w,h=1,color=color,fact_ids=[]))
def table(sl,id,x,y,w,h,rows,widths,fids,size=21,cids=None):sl['elements'].append(dict(id=id,type='table',x=x,y=y,w=w,h=h,rows=rows,widths=widths,size=size,fact_ids=fids,calc_ids=cids or []))
def chart(sl,id,x,y,w,h,cats,vals,fids,maxv,fmt='0.0',unit='GBP million',color=T,cids=None):sl['elements'].append(dict(id=id,type='chart',x=x,y=y,w=w,h=h,categories=cats,values=vals,series_name=unit,max=maxv,format=fmt,unit=unit,color=color,fact_ids=fids,calc_ids=cids or []))
def slide(title,section,bg=W):
 s=dict(title=title,background=bg,elements=[],notes=[]);slides.append(s);num=len(slides)
 text(s,f's{num}-section',60,32,1160,22,f'NORTHBRIDGE  /  {section.upper()}',14,T,True)
 text(s,f's{num}-title',60,76,1160,65,title,42,N,True)
 rule(s,f's{num}-header-rule',154)
 text(s,f's{num}-footer',60,677,1070,21,'FICTIONAL TRAINING MATERIAL   •   Management information, January 2026',13,M)
 text(s,f's{num}-page',1170,677,50,21,f'{num:02d}',14,M,align='right')
 return s
s=dict(title='Project Northbridge',background=N,elements=[],notes=[]);slides.append(s)
text(s,'cover-label',70,55,1100,30,'FICTIONAL TRANSACTION CASE',18,'#83D3C6',True)
text(s,'cover-title',70,180,1120,110,'Project Northbridge',68,W,True,facts=['BUS'])
text(s,'cover-subtitle',74,310,1050,58,'Information Memorandum',38,W)
text(s,'cover-company',74,400,1040,70,'Northbridge Field Services Ltd\nUK equipment maintenance and technical field support',25,'#BFD0D9',facts=['BUS'])
text(s,'cover-date',74,570,1050,55,'January 2026\nDraft for discussion',20,'#BFD0D9')
text(s,'cover-fiction',74,675,1100,22,'All companies, people and financial data in this case are fictional.',14,'#BFD0D9')
s=slide('Executive summary','Overview')
for j,(v,label,f,c) in enumerate([(f'£{rev[2]:.1f}m','FY2025 revenue',['FIN25'],[]),(f'£{eb[2]:.1f}m','FY2025 EBITDA',['FIN25'],[]),(f'{margin[2]:.0%}','FY2025 EBITDA margin',['FIN25'],['MARGINS']),(f'{mix[0]:.0%}','Maintenance revenue share',['MIX'],['MIX_SHARE'])]):
 text(s,f's2-kpi{j}',60+j*295,192,275,65,v,48,T,True,facts=f,calcs=c);text(s,f's2-label{j}',60+j*295,267,275,50,label,20,M,facts=f)
rule(s,'s2-midrule',338)
text(s,'s2-business',60,372,690,174,'UK provider of scheduled maintenance, reactive repairs and installation projects.\n\nFounded in 2012, the company operates from three hubs with 85 field engineers.',25,facts=['BUS','SERVICES','OPS'])
text(s,'s2-sale',820,372,400,40,'Proposed majority sale',27,N,True,facts=['DEAL'])
text(s,'s2-sale-detail',820,430,390,124,'Shareholders are considering a sale of 70% to 100%. Management rollover remains to be agreed.',24,facts=['DEAL'])
text(s,'s2-caveat',60,590,1160,62,f'Provisional revenue basis: the model shows £{rev[2]:.1f}m versus £{legacy:.1f}m in the earlier briefing.\nThe difference remains unresolved. EBITDA is management-reported and unaudited.',18,A,facts=['CONFLICT','QOE'])
s=slide('Investment highlights','Investment case')
rows=[('Contracted maintenance activity',f'Scheduled maintenance contributes {mix[0]:.0%} of FY2025 revenue. Contracts generally run for one to three years, with renewal by agreement.',['MIX','SERVICES'],['MIX_SHARE']),('Historical revenue\ngrowth',f'Revenue increased from £{rev[0]:.1f}m in FY2023 to a provisional £{rev[2]:.1f}m in FY2025, a {cagr:.1%} CAGR.',['FIN23','FIN25'],['CAGR']),('Technical delivery\ncapacity',f'{engineers} field engineers support delivery from Birmingham, Manchester and Bristol. Total year-end headcount is {heads}.',['OPS'],[]),('Identified expansion\npriorities','Management plans to add 20 net engineers by FY2027 and cross-sell maintenance to repair customers. Execution depends on hiring and renewals.',['GROWTH'],[])]
for i,(title,body,f,c) in enumerate(rows):
 y=185+i*112;text(s,f's3-num{i}',60,y,60,45,f'0{i+1}',30,T,True);text(s,f's3-head{i}',140,y,365,67,title,25,N,True,facts=f);text(s,f's3-body{i}',535,y,685,84,body,23,facts=f,calcs=c)
 if i<3:rule(s,f's3-rule{i}',y+96,x=140,w=1080)
text(s,'s3-caveat',60,638,1160,25,'Revenue remains provisional. The growth plan is a management forecast, not contracted backlog.',17,A,facts=['CONFLICT','FORECAST_BASIS'])
s=slide('Business and revenue mix','Services')
text(s,'s4-intro',60,181,1160,58,'Scheduled maintenance accounts for most revenue, supported by repairs and project work.',25,facts=['MIX','SERVICES'])
table(s,'s4-table',60,265,1160,245,[['Service','FY2025 £m','Share','Commercial basis'],['Scheduled maintenance',f'{svc[0]/1000:.1f}',f'{mix[0]:.0%}','Annual service contracts'],['Reactive repairs',f'{svc[1]/1000:.1f}',f'{mix[1]:.0%}','Call-out and materials'],['Installation projects',f'{svc[2]/1000:.1f}',f'{mix[2]:.0%}','Project-based work']],[3.4,1.5,1.1,3],['MIX','SERVICES'],22,['MIX_SHARE','NORMALIZE'])
text(s,'s4-contract',60,551,560,80,'Contract term\nTypically one to three years, with renewal by agreement.',23,facts=['SERVICES'])
text(s,'s4-customer',700,551,520,80,'Customer applications\nIndustrial sites, logistics operations and facilities management.',23,facts=['SERVICES'])
s=slide('Customer concentration','Customers')
text(s,'s5-chart-title',60,180,700,35,'FY2025 share of revenue by largest customer',23,N,True,facts=['CUSTOMERS'])
chart(s,'s5-chart',60,234,725,355,['A','B','C','D','E'],[v/sum(cust) for v in cust[:5]],['CUSTOMERS'],.16,'0.0%','Share of FY2025 revenue',cids=['TOP5','LARGEST'])
text(s,'s5-top',850,205,350,65,f'{top:.0%}',54,T,True,facts=['CUSTOMERS'],calcs=['TOP5']);text(s,'s5-top-label',850,280,340,55,'Top five customers',24,facts=['CUSTOMERS'])
text(s,'s5-largest',850,360,350,65,f'{largest:.0%}',54,T,True,facts=['CUSTOMERS'],calcs=['LARGEST']);text(s,'s5-largest-label',850,435,340,50,'Largest customer',24,facts=['CUSTOMERS'])
text(s,'s5-caveat',60,608,1160,48,f'The remaining {1-top:.0%} comprises multiple customers. The management retention estimate lacks\na defined basis and cohort data, so no verified retention metric is presented.',18,A,facts=['CUSTOMERS','RETENTION'])
s=slide('Operations and management','Operating model')
text(s,'s6-count',60,185,520,70,f'{heads} employees',44,T,True,facts=['OPS'])
text(s,'s6-engineers',60,275,520,55,f'Including {engineers} field engineers',26,facts=['OPS'])
text(s,'s6-hubs-head',60,365,520,38,'Three operating hubs',27,N,True,facts=['OPS'])
text(s,'s6-hubs',60,425,520,130,'Birmingham\nManchester\nBristol',26,facts=['OPS'])
table(s,'s6-team',650,190,570,245,[['Management','Role'],['Maya Reed','Founder and CEO'],['Daniel Cole','CFO'],['Aisha Patel','COO']],[1.1,1.3],['OPS'],22)
text(s,'s6-dependency',650,485,570,125,'The founder leads major customer relationships. Management plans 20 net engineer hires by FY2027. Recruitment and relationship continuity require diligence.',23,facts=['OPS','GROWTH'])
text(s,'s6-date',60,631,1160,25,'Headcount as at 31 December 2025. Management information.',17,M,facts=['OPS'])
s=slide('Historical financial performance','Financials')
text(s,'s7-unit',60,180,1160,30,'GBP million unless stated. Year ending 31 December. Management actuals.',20,M,facts=['FIN23','FIN24','FIN25','UNITS'])
finrows=[['','FY2023A','FY2024A','FY2025A']]
for label,row in [('Revenue',6),('Cost of services',7),('Gross profit',8),('Operating expenses',9),('EBITDA',10),('EBITDA margin',11)]:
 vals=[cell(f'PnL!{c}{row}') for c in 'BCD'];finrows.append([label]+[f'{v:.1%}' if row==11 else f'({abs(v):.1f})' if v<0 else f'{v:.1f}' for v in vals])
table(s,'s7-table',60,230,840,338,finrows,[2.8,1.4,1.4,1.4],['FIN23','FIN24','FIN25'],22,['MARGINS'])
text(s,'s7-cagr',960,248,260,70,f'{cagr:.1%}',51,T,True,facts=['FIN23','FIN25'],calcs=['CAGR']);text(s,'s7-cagr-label',960,330,250,75,'FY2023–FY2025\nrevenue CAGR',23,facts=['FIN23','FIN25'])
text(s,'s7-margin',960,438,250,80,f'{margin[2]:.1%}\nFY2025 margin',28,T,True,facts=['FIN25'],calcs=['MARGINS'])
text(s,'s7-caveat',60,598,1160,60,f'FY2025 revenue is provisional: £{rev[2]:.1f}m model versus £{legacy:.1f}m briefing.\nManagement EBITDA is unaudited. No normalisation bridge or QoE report is available.',18,A,facts=['CONFLICT','QOE'])
s=slide('Growth plan and management outlook','Outlook')
text(s,'s8-chart-head',60,180,690,35,'Revenue (£m), management base case',23,N,True,facts=['FIN25','FIN26','FIN27'])
chart(s,'s8-chart',60,230,690,300,['FY2025A','FY2026F','FY2027F'],rev[2:],['FIN25','FIN26','FIN27'],40)
table(s,'s8-ebitda',60,550,690,95,[['','FY2025A','FY2026F','FY2027F'],['EBITDA (£m)',f'{eb[2]:.1f}',f'{eb[3]:.1f}',f'{eb[4]:.1f}']],[2.4,1,1,1],['FIN25','FIN26','FIN27'],20)
text(s,'s8-plan',820,190,400,40,'Management priorities',27,N,True,facts=['GROWTH'])
text(s,'s8-plan-body',820,250,400,165,'Add 20 net engineers by FY2027.\n\nCross-sell maintenance to repair customers and extend coverage from existing hubs.',23,facts=['GROWTH'])
text(s,'s8-caveat',820,445,400,195,'Forecasts depend on hiring and renewals. No customer-level forecast bridge or signed pipeline is available.\n\nMarket size and share remain unsubstantiated.',21,A,facts=['FORECAST_BASIS','GROWTH','MARKET'])
s=slide('Proposed transaction','Transaction overview')
table(s,'s9-ownership',60,205,550,245,[['Current shareholder','Ownership'],['Founder','70%'],['Management','20%'],['Seed investor','10%']],[2.3,1],['DEAL'],23)
text(s,'s9-sale',700,195,520,78,'70%–100%',58,T,True,facts=['DEAL'])
text(s,'s9-sale-label',700,290,520,55,'Indicative equity sale perimeter',25,facts=['DEAL'])
text(s,'s9-scope',700,380,520,118,'The proposal covers the standalone UK company. Management rollover, valuation, timetable and financing remain to be agreed.',24,facts=['DEAL','BUS'])
text(s,'s9-caveat',60,550,1160,80,'Cash, debt and normalised working capital have not been supplied.\nAn enterprise-to-equity value bridge cannot yet be prepared.',22,A,facts=['QOE','DEAL'])
s=slide('Key considerations and diligence','Review agenda')
table(s,'s10-table',60,190,1160,390,[['Topic','Current position','Evidence required'],['Revenue recognition',f'£{rev[2]:.1f}m model vs £{legacy:.1f}m briefing','Recognised revenue reconciliation'],['Earnings and\nbalance sheet','Unaudited management EBITDA','QoE, normalisation, debt,\ncash and working capital'],['Customer quality',f'Top five account for {top:.0%}\nof revenue','Contracts and defined\nretention cohorts'],['Growth execution','Hiring and renewals\nunderpin forecast','Revenue bridge, pipeline\nand hiring costs'],['Market positioning','No substantiated size or share','Independent market and competitor work']],[2,3,3.5],['CONFLICT','QOE','CUSTOMERS','RETENTION','GROWTH','FORECAST_BASIS','MARKET'],20,['TOP5'])
text(s,'s10-close',60,610,1160,44,'The investment case remains subject to financial and commercial diligence.',24,N,True,facts=['CONFLICT','QOE','MARKET','FORECAST_BASIS'])
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
(root/'working/storyboard.json').write_text(json.dumps({'title':'Project Northbridge — Information Memorandum','synthetic':True,'slides':slides},ensure_ascii=False,indent=2))
(root/'working/issue-register.json').write_text(json.dumps(issues,indent=2))
(root/'working/input-manifest.json').write_text(json.dumps(ledger['sources'],indent=2))
print(f'Built {len(slides)} slides, {len(facts)} facts, {len(calcs)} calculations, {len(claims)} claim mappings')
