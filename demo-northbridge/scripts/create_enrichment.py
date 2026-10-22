"""Create additional fictional client materials. Never use these figures in client work."""
from pathlib import Path
import csv, io
root=Path(__file__).resolve().parents[1]/'inputs'
def txt(name,body):
 (root/name).write_text(body.strip()+'\n',encoding='utf-8')
def tab(name,header,rows):
 s=io.StringIO();s.write('# FICTIONAL TRAINING CASE; management submission 26 January 2026; unaudited\n')
 w=csv.writer(s,lineterminator='\n');w.writerow(header);w.writerows(rows);txt(name,s.getvalue())
txt('05_commercial_interview.txt','''FICTIONAL TRAINING CASE. All statements and figures are invented for workflow testing.
Commercial director interview, 26 January 2026. Period: FY2025 unless specified.
Scheduled maintenance covers planned inspections and preventive servicing. Most contracts specify scheduled visits and an annual fee. Reactive repairs charge call-out, labour and materials. Installation projects use a separately agreed scope and price.
Contracts generally run for one to three years. Renewal requires agreement. Annual price reviews depend on contract terms and customer acceptance. Maintenance revenue should not be described as guaranteed future revenue or ARR.
The FY2025 renewal cohort comprised 25 maintenance agreements due for renewal, with GBP 4.00 million of annual contract value immediately before expiry. 23 agreements renewed. The annual value retained on those same agreements, before price changes or additional scope, was GBP 3.72 million. These are management-prepared counts and values, not independently verified customer retention.
The earlier 94% retention estimate remains undefined. It uses no documented customer cohort and cannot be reconciled to this contract-level renewal schedule.
Pipeline at 26 January 2026 totals GBP 4.8 million of indicative annual revenue: proposals GBP 2.4 million, negotiations GBP 1.5 million and preferred supplier GBP 0.9 million. All are unsigned. Stage values are unweighted and are not forecast revenue or backlog.
Maya Reed remains the primary executive contact on the largest customer accounts. The commercial team needs to document deputy account ownership and review change-of-control provisions.
No independent market-size, market-share or competitor study has been submitted.
''')
tab('06_hub_schedule.csv',['hub','fy2025_revenue_gbp_m','employees_20251231','field_engineers_20251231'],[
 ['Birmingham',11.5,55,40],['Manchester',8.0,38,27],['Bristol',5.5,27,18]])
tab('07_service_kpis.csv',['metric','numerator','denominator','period','definition'],[
 ['Urgent response SLA',561,600,'FY2025','Eligible urgent jobs attended within four hours / all eligible urgent jobs'],
 ['First-time fix',2200,2500,'FY2025','Closed reactive jobs resolved on first visit / all closed reactive jobs'],
 ['Productive hours',126480,170000,'FY2025','Recorded productive engineer hours / recorded available engineer hours; not billing utilisation']])
tab('08_contract_expiries.csv',['expiry_year','fy2025_maintenance_revenue_gbp_m','basis'],[
 [2026,6.0,'FY2025 revenue attributed to current agreement expiry year; not backlog'],
 [2027,7.5,'FY2025 revenue attributed to current agreement expiry year; not backlog'],
 [2028,4.0,'FY2025 revenue attributed to current agreement expiry year; not backlog']])
tab('09_quarterly_accounts.csv',['quarter','revenue_gbp_m','ebitda_gbp_m','basis'],[
 ['Q1 2025',5.7,.9,'Unaudited provisional management actuals'],['Q2 2025',6.1,1.15,'Unaudited provisional management actuals'],
 ['Q3 2025',6.4,1.3,'Unaudited provisional management actuals'],['Q4 2025',6.8,1.65,'Unaudited provisional management actuals']])
txt('10_cfo_follow_up.eml','''From: daniel.cole@northbridge.example
To: deal.team@example.invalid
Date: Mon, 26 Jan 2026 09:30:00 +0000
Subject: FICTIONAL CASE - supplementary draft schedules

All figures and people in this email are fictional. Figures below are GBP million unless stated.
Please continue to use the FY2025 revenue of 25.0 in the management model provisionally. The earlier 26.2 briefing figure remains unreconciled. We have identified 0.8 of possible orders relating to services scheduled for 2026, but have not verified this against invoices and the ledger. Do not deduct this amount and describe the difference as resolved.
At 31 December 2025, our draft schedule shows cash 2.4 and bank term debt 4.8. Lease liabilities, tax balances, debt-like items and restricted cash have not been assessed. These figures alone are insufficient for an enterprise-to-equity bridge.
Draft trade receivables are 4.2, inventory 0.6 and trade payables 2.1 at 31 December 2025. Other working-capital items and monthly seasonality are missing. This limited snapshot is not normalised working capital.
Management has proposed EBITDA adjustments of 0.18 for founder remuneration and 0.12 for systems implementation. We have not substantiated either adjustment. Retain management-reported EBITDA of 5.0 with no add-backs.
The quarterly revenue and EBITDA schedule ties to the annual model. All figures remain unaudited. No quality-of-earnings report is available.
The supplemental forecast bridge explains group-level movements only. No customer-level bridge, signed pipeline, recruitment cost schedule or timing of engineer productivity is available.
''')
tab('11_forecast_bridge.csv',['component','fy2026_gbp_m','fy2027_gbp_m','basis'],[
 ['Opening revenue',25,29,'Prior year actual or forecast'],['Price',1,1.16,'Management assumption; customer acceptance required'],
 ['New contracts',2,2.4,'Management assumption; unsigned pipeline'],['Cross-sell',1.6,1.74,'Management assumption; conversion required'],
 ['Attrition',-.6,-.7,'Management assumption'],['Closing revenue',29,33.6,'Management forecast'],
 ['Year-end field engineers',95,105,'Headcount; excludes attrition/replacement hiring; net growth from 85']])
tab('12_sector_mix.csv',['sector','fy2025_revenue_gbp_m'],[['Logistics',11.25],['Manufacturing',8.75],['Facilities management',5]])
txt('13_transaction_workshop.txt','''FICTIONAL TRAINING CASE. Invented transaction workshop notes, 26 January 2026.
Shareholders are considering a sale of 70% to 100% of the equity in the standalone UK company. The current ownership remains founder 70%, management 20%, seed investor 10%.
The proposed perimeter includes all three hubs, operating assets and customer contracts of the company. No excluded business has been identified. Legal entity, asset ownership and contract transferability require legal diligence.
No valuation, management rollover, financing structure or transaction timetable has been agreed. The process remains at preparation stage. No offers or signed sale terms exist in this fictional case.
Daniel Cole (CFO) owns revenue reconciliation, QoE preparation and balance-sheet schedules. Aisha Patel (COO) owns job-level KPI evidence, engineer recruitment and capacity planning. Maya Reed (CEO) owns key-account continuity and pipeline evidence. External legal counsel, not yet appointed, would review title, consents and change-of-control clauses. The strategy team owns independent market work.
''')
print('Created 9 additional fictional source files (05-13).')
