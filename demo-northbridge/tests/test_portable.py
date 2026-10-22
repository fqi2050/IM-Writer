"""Exercise the self-contained exporter, including a native-chart corruption rejection."""
import os,sys,json,subprocess,tempfile,zipfile,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1];skill=root.parent/'skills/mna-information-memo'
with tempfile.TemporaryDirectory(prefix='IM portable ') as temp:
 out=Path(temp)/'示例 output'
 subprocess.run([sys.executable,str(skill/'scripts/build_portable.py'),str(skill/'assets/storyboard-example.json'),str(out)],check=True)
 result=json.loads((out/'outputs/validation.json').read_text(encoding='utf-8'))
 assert result['passed']['native_tables']==1 and result['passed']['native_charts']==1
 ppt=out/'outputs/im-editable.pptx'
 with zipfile.ZipFile(ppt) as z:parts={n:z.read(n) for n in z.namelist()}
 name='ppt/charts/chart1.xml';text=parts[name].decode();assert '<c:v>10</c:v>' in text
 parts[name]=text.replace('<c:v>10</c:v>','<c:v>999</c:v>',1).encode()
 broken=out/'tampered.pptx'
 with zipfile.ZipFile(broken,'w',zipfile.ZIP_DEFLATED) as z:
  for name,blob in parts.items():z.writestr(name,blob)
 r=subprocess.run([sys.executable,str(skill/'scripts/validate_native.py'),str(out/'working/storyboard.json'),str(broken),str(out/'rejected.json')],capture_output=True,text=True)
 assert r.returncode!=0 and 'chart data' in r.stderr,r.stderr
 assert not (out/'rejected.json').exists()
 result={'passed':['Standalone bundled example produces native text, table, chart, notes and embedded workbook.','Native chart cache corruption is rejected against the storyboard.','Paths with spaces and Chinese characters succeed.'],'host_platform':sys.platform,'windows_desktop_tested':False,'dependencies':'Public Python packages and local npm PptxGenJS; no artifact-tool import or private finalizer.'}
 (root/'tests/portable-test-results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps(result))
