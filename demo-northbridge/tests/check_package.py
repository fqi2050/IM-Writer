from pathlib import Path
import zipfile,json,re,io,hashlib
from xml.etree import ElementTree as E
from openpyxl import load_workbook
root=Path(__file__).resolve().parents[1];p=root/'outputs/northbridge-im-editable.pptx'
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
with zipfile.ZipFile(p) as z:
 names=z.namelist();slides=sorted([n for n in names if re.fullmatch(r'ppt/slides/slide\d+.xml',n)],key=lambda n:int(re.search(r'(\d+)\.xml',n).group(1)))
 assert len(slides)==10
 tables=sum(len(E.fromstring(z.read(n)).findall('.//a:tbl',ns)) for n in slides)
 charts=[n for n in names if re.fullmatch(r'ppt/(?:slides/)?charts/chart\d+.xml',n)]
 images=sum(len(E.fromstring(z.read(n)).findall('.//p:pic',ns)) for n in slides)
 notes=[n for n in names if re.fullmatch(r'ppt/notesSlides/notesSlide\d+.xml',n)]
 workbooks=[n for n in names if n.startswith('ppt/embeddings/') and n.endswith('.xlsx')]
 story=json.loads((root/'working/storyboard.json').read_text())
 expected_tables=sum(e['type']=='table' for s in story['slides'] for e in s['elements'])
 assert tables==expected_tables and len(charts)==2 and len(notes)==10 and images==0
 assert len(workbooks)==2,workbooks
 values=[]
 for n in workbooks:
  w=load_workbook(io.BytesIO(z.read(n)),data_only=True);values.append([[list(r) for r in s.values] for s in w])
 allnotes=' '.join(' '.join(E.fromstring(z.read(n)).itertext()) for n in notes)
 assert 'PnL!D6' in allnotes and 'paragraph' in allnotes
 counts={'slides':len(slides),'native_tables':tables,'native_charts':len(charts),'embedded_chart_workbooks':len(workbooks),'source_notes':len(notes),'raster_pictures':images,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(root/'tests/package-test-results.json').write_text(json.dumps({'passed':counts,'embedded_data':values},indent=2));print(json.dumps(counts))
