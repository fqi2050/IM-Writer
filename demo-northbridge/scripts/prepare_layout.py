"""Measure this demo's Arial layout without launching a browser. No source content executes."""
import json,sys,os
from pathlib import Path
from PIL import ImageFont
story=Path(sys.argv[1]);theme=json.loads(Path(sys.argv[2]).read_text());data=json.loads(story.read_text())
regular=os.environ.get('IM_FONT_REGULAR','/System/Library/Fonts/Supplemental/Arial.ttf')
bold=os.environ.get('IM_FONT_BOLD','/System/Library/Fonts/Supplemental/Arial Bold.ttf')
def lines(value,size,width,strong=False):
 font=ImageFont.truetype(bold if strong else regular,round(size*4));count=0
 for paragraph in str(value).split('\n'):
  line='';count+=1
  for word in paragraph.split():
   test=(line+' '+word).strip()
   if font.getlength(test)/4>width:
    if not line:raise ValueError('Unbreakable word exceeds width: '+word)
    count+=1;line=word
   else:line=test
 return count
failures=[]
for n,s in enumerate(data['slides'],1):
 for e in s['elements']:
  if e['x']<0 or e['y']<0 or e['x']+e['w']>1280.1 or e['y']+e['h']>720.1:failures.append((n,e['id'],'outside canvas'))
  if e['type']=='text':
   required=lines(e['text'],e['size'],e['w']-2,e.get('bold',False))*e['size']*1.22
   if required>e['h']+2:failures.append((n,e['id'],round(required,1),e['h']))
  if e['type']=='table':
   widths=[e['w']*v/sum(e['widths']) for v in e['widths']]
   minimum=[max(lines(v,e['size'],widths[c]-2*theme['table_padding_x']-3,r==0 or r in e.get('emphasis_rows',[]))*e['size']*1.22+2*theme['table_padding_y']+1 for c,v in enumerate(row)) for r,row in enumerate(e['rows'])]
   if sum(minimum)>e['h']+1:failures.append((n,e['id'],round(sum(minimum),1),e['h']))
   extra=max(0,(e['h']-sum(minimum))/len(minimum));e['row_heights']=[h+extra for h in minimum]
if failures:raise SystemExit(json.dumps({'layout_fit_failures':failures},indent=2))
story.write_text(json.dumps(data,ensure_ascii=False,indent=2));print('Arial measurements passed; table row heights recorded for shared HTML/PPT layout.')
