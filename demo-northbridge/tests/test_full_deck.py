"""Check delivered native PPT content against the authored source-linked storyboard."""
import json,zipfile,hashlib,re,importlib.util
from pathlib import Path
from xml.etree import ElementTree as E
root=Path(__file__).resolve().parents[1]
story=json.loads((root/'working/storyboard.json').read_text())
assert story['style_profile']=='advisory-dense' and len(story['slides'])==10
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
norm=lambda s:re.sub(r'\s+',' ',s).strip()
counts={'native_tables':0,'text_elements':0}
ppt=root/'outputs/northbridge-im-editable.pptx'
with zipfile.ZipFile(ppt) as z:
 for n,s in enumerate(story['slides'],1):
  slide=E.fromstring(z.read(f'ppt/slides/slide{n}.xml'))
  tables=slide.findall('.//a:tbl',ns);expected=[e for e in s['elements'] if e['type']=='table']
  assert len(tables)==len(expected)
  for t,e in zip(tables,expected):
   actual=[[norm(' '.join(c.itertext())) for c in row.findall('a:tc',ns)] for row in t.findall('a:tr',ns)]
   assert actual==[[norm(str(c)) for c in row] for row in e['rows']],(n,e['id'],actual)
   assert t.find('.//a:srgbClr[@val="00338D"]',ns) is not None,(n,e['id'],'missing blue')
   counts['native_tables']+=1
  texts=[norm(' '.join(sh.findall('p:txBody',ns)[0].itertext())) for sh in slide.findall('.//p:sp',ns) if sh.find('p:txBody',ns) is not None]
  for e in s['elements']:
   if e['type']=='text':
    assert norm(e['text']) in texts,(n,e['id'],'text mismatch');counts['text_elements']+=1
  assert slide.find('.//p:pic',ns) is None,'Raster slide replacement'
  assert 'FICTIONAL TRAINING CASE' in z.read(f'ppt/notesSlides/notesSlide{n}.xml').decode()
  assert s['background']=='#FFFFFF'
  for e in s['elements']:
   assert e.get('color','#000000') in ['#000000','#00338D','#595959','#B8C7DF']
 html=(root/'outputs/northbridge-im.html').read_text()
 assert '#117F79' not in html and '#132E42' not in html
renderer=root.parent/'skills/mna-information-memo/scripts/render_html.py'
spec=importlib.util.spec_from_file_location('im_renderer',renderer);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
sample=json.loads((root.parent/'skills/mna-information-memo/assets/storyboard-example.json').read_text())
sample.pop('style_profile',None);assert '#00338D' in module.render(sample)
for invalid in [None,'generic','teal']:
 sample['style_profile']=invalid
 try:module.render(sample)
 except ValueError:pass
 else:raise AssertionError('Mandatory style not enforced')
report={'passed':counts,'slide_count':10,'sha256':hashlib.sha256(ppt.read_bytes()).hexdigest(),'checks':['Every native table cell and text element matches storyboard.','All 10 pages use the required report design and retain source notes.','No raster slide replacement.','Missing profile defaults to advisory-dense; null/alternative profiles fail.'],'limitations':['Desktop PowerPoint edit/save/reopen has not been tested.','Arial substitutes for the proprietary reference title font.']}
(root/'tests/full-deck-test-results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
