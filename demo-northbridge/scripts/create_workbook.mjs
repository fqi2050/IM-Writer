import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.resolve(import.meta.dirname,'..'), seed=JSON.parse(await fs.readFile(path.join(root,'.build/source_seed.json'),'utf8'));
const wb=Workbook.create();
const p=wb.worksheets.add('PnL'), c=wb.worksheets.add('CustomerSales'), s=wb.worksheets.add('ServiceMix');
for(const sh of [p,c,s]){sh.showGridLines=false;sh.getRange('A1:F20').format.font.name='Arial';sh.getRange('A1:F20').format.font.size=11;sh.getRange('A1:F20').format.rowHeight=23;sh.getRange('A1:A20').format.columnWidth=33;sh.getRange('B1:F20').format.columnWidth=17;}
p.getRange('A1').values=[['Northbridge management P&L']];p.getRange('A2').values=[['FICTIONAL DATA. GBP million. Year ending 31 December.']];p.getRange('A3').values=[['Management model v2.0, 21 January 2026. Unaudited.']];
p.getRange('A5:F5').values=[['GBP million','FY2023A','FY2024A','FY2025A','FY2026F','FY2027F']];
p.getRange('A6:F11').values=seed.financials;
for(const col of ['B','C','D','E','F']){p.getRange(col+'8').formulas=[['='+col+'6+'+col+'7']];p.getRange(col+'10').formulas=[['='+col+'8+'+col+'9']];p.getRange(col+'11').formulas=[['='+col+'10/'+col+'6']];}
p.getRange('B6:F10').setNumberFormat('0.0;(0.0);"-"');p.getRange('B11:F11').setNumberFormat('0.0%');
p.getRange('B6:F11').format.font.color='#0000FF';for(const r of [8,10,11])p.getRange('B'+r+':F'+r).format.font.color='#000000';
p.getRange('A13').values=[['A = management actual. F = management base-case forecast.']];p.getRange('A14').values=[['FY2025 revenue conflicts with the earlier briefing (GBP 26.2m).']];p.getRange('A15').values=[['No audit, EBITDA normalisation bridge or cash/debt schedules supplied.']];
c.getRange('A1').values=[['FY2025 customer sales']];c.getRange('A2').values=[['FICTIONAL DATA. GBP thousand. Recognised revenue excluding VAT.']];c.getRange('A4:C4').values=[['Customer ID','Customer','Revenue (GBP 000)']];c.getRange('A5:C10').values=seed.customers;c.getRange('A11').values=[['Total']];c.getRange('C11').formulas=[['=SUM(C5:C10)']];c.getRange('C5:C11').setNumberFormat('#,##0');c.getRange('B4:B11').format.columnWidth=39;c.getRange('A13').values=[['OTHER represents multiple customers, not one customer.']];
s.getRange('A1').values=[['FY2025 revenue by service']];s.getRange('A2').values=[['FICTIONAL DATA. GBP thousand. Same perimeter as P&L.']];s.getRange('A4:C4').values=[['Service','Revenue (GBP 000)','Commercial basis']];s.getRange('A5:C7').values=seed.services;s.getRange('A8').values=[['Total']];s.getRange('B8').formulas=[['=SUM(B5:B7)']];s.getRange('B5:B8').setNumberFormat('#,##0');s.getRange('B1:B12').format.columnWidth=23;s.getRange('C1:C12').format.columnWidth=32;
for(const [sh,head,last] of [[p,5,'F'],[c,4,'C'],[s,4,'C']]){sh.getRange('A1').format.font.size=16;sh.getRange('A1').format.font.bold=true;sh.getRange(`A${head}:${last}${head}`).format.fill='#132E42';sh.getRange(`A${head}:${last}${head}`).format.font.color='#FFFFFF';sh.getRange(`A${head}:${last}${head}`).format.font.bold=true;sh.getRange(`A${head}:${last}${head}`).format.rowHeight=30;}
wb.recalculate();
console.log((await wb.inspect({kind:'region',sheetId:'PnL',range:'A5:F11',maxChars:3000,tableMaxRows:8,tableMaxCols:6})).ndjson);
for(const sh of [p,c,s]){let img=await wb.render({sheetName:sh.name,range:sh===p?'A1:F15':sh===c?'A1:C13':'A1:C9',scale:1.5,format:'png'});await fs.writeFile(path.join(root,'.build',sh.name+'.png'),new Uint8Array(await img.arrayBuffer()));}
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(root,'inputs/02_management_model.xlsx'));
