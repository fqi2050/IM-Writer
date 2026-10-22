"""Observable regression tests for the synthetic input/evidence workflow."""
from pathlib import Path
import tempfile,shutil,sys,json,subprocess,zipfile,re,hashlib
from xml.etree import ElementTree as ET
root=Path(__file__).resolve().parents[1]; skill=root.parent/'skills/mna-information-memo'; reports=[]
ledger=json.loads((root/'working/evidence-ledger.json').read_text()); ex=json.loads((root/'working/extracted.json').read_text())
locators={(s['id'],i['locator']) for s in ex['sources'] for i in s['items']}
for s in ledger['sources']:assert hashlib.sha256((root/'inputs'/s['path']).read_bytes()).hexdigest()==s['sha256']
for f in ledger['facts']:
 for r in f['source_refs']:assert (r['source_id'],r['locator']) in locators
reports.append('All input hashes and fact source locators match delivered inputs.')
calc={c['id']:c for c in ledger['calculations']};assert abs(calc['TOP5']['result']-.42)<1e-10;assert abs(calc['MARGINS']['result'][2]-.2)<1e-10
reports.append('Top-five concentration excludes OTHER aggregate; margins and unit conversion reconcile.')
def mutate_zip(p,member,replace):
 with zipfile.ZipFile(p) as z:parts={n:z.read(n) for n in z.namelist()}
 parts[member]=replace(parts[member].decode()).encode()
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in parts.items():z.writestr(n,b)
def fixture():
 td=tempfile.TemporaryDirectory(); d=Path(td.name);(d/'.build').mkdir();(d/'working').mkdir();shutil.copytree(root/'inputs',d/'inputs');shutil.copy(root/'scripts/build_storyboard.py',d/'.build/build_storyboard.py');return td,d
def run(d):
 subprocess.run([sys.executable,str(skill/'scripts/extract_sources.py'),str(d/'inputs'),str(d/'working/extracted.json')],check=True,capture_output=True)
 return subprocess.run([sys.executable,str(d/'.build/build_storyboard.py')],capture_output=True,text=True)
td,d=fixture()
with td:
 p=d/'inputs/02_management_model.xlsx'
 def repl(xml):
  ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};tree=ET.fromstring(xml);v=tree.find('.//s:c[@r="C5"]/s:v',ns);assert float(v.text)==3000;v.text='3100';return ET.tostring(tree,encoding='unicode')
 mutate_zip(p,'xl/worksheets/sheet2.xml',repl);r=run(d);assert r.returncode!=0 and 'Customer schedule fails P&L tie-out' in r.stderr
 reports.append('Changing customer revenue by GBP 100k triggers a reconciliation failure before rendering.')
td,d=fixture()
with td:
 mutate_zip(d/'inputs/01_company_brief.docx','word/document.xml',lambda s:s.replace('26.2','26.6'));r=run(d);assert r.returncode==0,r.stderr
 updated=json.loads((d/'working/evidence-ledger.json').read_text());gap=next(c['result'] for c in updated['calculations'] if c['id']=='REVENUE_GAP');assert abs(gap-1.6)<1e-10
 story=(d/'working/storyboard.json').read_text();assert '26.6' in story
 reports.append('Changing the briefing to GBP 26.6m updates conflict disclosure and the GBP 1.6m gap.')
status={f['id']:f['status'] for f in ledger['facts']};assert status['RETENTION']=='management_unverified' and status['MARKET']=='missing' and status['CONFLICT']=='provisional_conflict'
reports.append('Undefined retention and missing market evidence remain unverified/missing; revenue remains provisional.')
(root/'tests/evidence-test-results.json').write_text(json.dumps({'passed':reports},indent=2));print('\n'.join(reports))
