"""Check exported pilot table styling, financial values, traceability and preview visibility.
Usage: python test_advisory_style.py [preview_dir]
"""
import json,sys,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
board=json.loads((root/'style-pilot/storyboard.json').read_text())
ledger=json.loads((root/'working/evidence-ledger.json').read_text())
facts={f['id'] for f in ledger['facts']};calcs={c['id'] for c in ledger['calculations']}
with zipfile.ZipFile(root/'style-pilot/northbridge-advisory-editable.pptx') as z:
 for i,s in enumerate(board['slides'],1):
  x=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
  assert not x.findall('.//p:pic',ns),'Unexpected raster substitution'
  tables=x.findall('.//a:tbl',ns);expected=[e for e in s['elements'] if e['type']=='table']
  assert len(tables)==len(expected)==1
  for table,e in zip(tables,expected):
   rows=table.findall('a:tr',ns)
   assert len(rows)==len(e['rows'])
   for ri,row in enumerate(rows):
    for ci,cell in enumerate(row.findall('a:tc',ns)):
     texts=[''.join(t.itertext()) for t in cell.findall('.//a:t',ns)]
     assert ''.join(texts).replace('\n','')==e['rows'][ri][ci].replace('\n',''),(i,ri,ci,texts)
     fill=cell.find('a:tcPr/a:solidFill/a:srgbClr',ns)
     assert fill is not None and fill.attrib['val'].upper()==('00338D' if ri==0 else 'DBE8F8' if ri%2==0 else 'FFFFFF'),(i,ri,ci,'fill')
     expected_align={'left':'l','center':'ctr','right':'r'}[e['column_align'][ci]]
     assert all(p.attrib.get('algn','l')==expected_align for p in cell.findall('.//a:pPr',ns)),(i,ri,ci,'align')
     if ri==0 or ri in e.get('emphasis_rows',[]):
      assert all(p.attrib.get('b')=='1' for p in cell.findall('.//a:rPr',ns)),(i,ri,ci,'bold')
  notes=z.read(f'ppt/notesSlides/notesSlide{i}.xml').decode()
  assert 'FICTIONAL TRAINING CASE' in notes
  for e in s['elements']:
   assert set(e['fact_ids'])<=facts
   assert set(e.get('calc_ids',[]))<=calcs
   assert all(fid in notes for fid in e['fact_ids'])
# Financial arithmetic checks on displayed data, independently from the generator.
t=expected[0]['rows']
for col in range(1,4):
 val=lambda row:float(t[row][col].replace('(','-').replace(')',''))
 assert abs(val(1)+val(2)-val(3))<0.01
 assert abs(val(3)+val(4)-val(5))<0.01
 assert abs(val(5)/val(1)*100-float(t[6][col].rstrip('%')))<0.051
service=next(e for e in board['slides'][1]['elements'] if e['type']=='table')['rows']
assert sum(float(r[1]) for r in service[1:4])==float(service[4][1])
if len(sys.argv)>1:
 from PIL import Image,ImageChops,ImageStat
 for i in range(1,4):
  for kind in ['html','ppt']:
   img=Image.open(Path(sys.argv[1])/f'{kind}-{i:02d}.png').convert('RGB')
   assert sum(ImageStat.Stat(img).stddev)>30,(kind,i,'blank preview')
print('PASS: 3 editable tables; fills, alignment, emphasis, values, source IDs and financial arithmetic; previews nonblank when supplied')
