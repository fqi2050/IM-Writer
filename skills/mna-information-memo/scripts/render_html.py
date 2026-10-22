"""Render the documented semantic IM storyboard to standalone HTML."""
import json,sys,html
from pathlib import Path
E=html.escape

def chart_svg(e):
 w,h=e['w']*1.5,e['h']*1.5;left,top,right,bottom=65,40,20,65;pw,ph=w-left-right,h-top-bottom
 vals=e['values']; mx=e['max']; n=len(vals); gap=pw/n;bw=gap*.54
 pct=e.get('format')=='0.0%'
 fmt=lambda v:f'{v*100:.0f}%' if pct else f'{v:.1f}'
 parts=[f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{E(e["series_name"])}">']
 for j in range(5):
  y=top+ph-j*ph/4; v=mx*j/4
  parts.append(f'<line x1="{left}" y1="{y}" x2="{w-right}" y2="{y}" stroke="#DCE4E8"/><text x="{left-12}" y="{y+6}" text-anchor="end" fill="#5A6D7D" font-size="20">{fmt(v)}</text>')
 for i,(v,cat) in enumerate(zip(vals,e['categories'])):
  bh=v/mx*ph;x=left+gap*(i+.5)-bw/2;y=top+ph-bh
  parts.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="{e.get("color","#117F79")}"/><text x="{x+bw/2}" y="{y-12}" text-anchor="middle" font-size="25" fill="#132E42" font-weight="700">{fmt(v)}</text><text x="{x+bw/2}" y="{top+ph+35}" text-anchor="middle" font-size="20" fill="#5A6D7D">{E(str(cat))}</text>')
 return ''.join(parts)+'</svg>'

def render(data):
 base=(Path(__file__).resolve().parents[1]/'assets/viewport-base.css').read_text()
 css='''/* === IM TYPOGRAPHY AND LAYOUT === */
*{box-sizing:border-box} :root{--stage-bg:#081925;--slide-bg:#FFFFFF} body{font-family:Arial,sans-serif} .slide{transition:opacity .2s} [data-pptx]{position:absolute;margin:0} .text{white-space:pre-wrap;line-height:1.18;overflow:visible} table{border-collapse:collapse;table-layout:fixed;width:100%;height:100%;color:#132E42} th,td{padding:12px 18px;white-space:pre-wrap;border-bottom:1px solid #DCE4E8;text-align:left;vertical-align:middle;line-height:1.18} th{background:#132E42;color:white;font-weight:700} tr:nth-child(2n+1) td{background:#F2F6F7} .deck-controls{display:flex;flex-wrap:wrap;justify-content:center;max-width:calc(100vw - 20px);gap:10px;background:#132E42;padding:8px 12px;border-radius:6px;color:#FFF;font-size:13px;bottom:6px} button{cursor:pointer;background:transparent;border:1px solid #5A6D7D;color:white;padding:5px 9px} button:focus-visible{outline:2px solid #61D6C6} [contenteditable=true]{outline:2px dashed #117F79} #sourcePanel{position:fixed;right:16px;top:16px;max-width:480px;max-height:70vh;overflow:auto;background:#FFFFFF;color:#132E42;padding:22px;z-index:1001;white-space:pre-wrap;font-size:13px;box-shadow:0 8px 40px #0006} #sourcePanel[hidden]{display:none} @media print{#sourcePanel{display:none!important}.deck-controls{display:none!important}@page{size:16in 9in;margin:0}}
'''
 sections=[]
 for i,s in enumerate(data['slides']):
  elems=[]
  for e in s['elements']:
   pos=f'left:{e["x"]*1.5}px;top:{e["y"]*1.5}px;width:{e["w"]*1.5}px;height:{e["h"]*1.5}px;'
   attr=f'id="{E(e["id"])}" data-pptx="{e["type"]}" data-facts="{E(json.dumps(e.get("fact_ids",[])))}"'
   if e['type']=='text':
    style=pos+f'font-size:{e.get("size",24)*1.5}px;color:{e.get("color","#132E42")};font-weight:{700 if e.get("bold") else 400};text-align:{e.get("align","left")};'
    elems.append(f'<p {attr} class="text" style="{style}">{E(e["text"])}</p>')
   elif e['type']=='rule':elems.append(f'<div {attr} style="{pos}background:{e.get("color","#DCE4E8")}"></div>')
   elif e['type']=='table':
    widths=e.get('widths',[1]*len(e['rows'][0]));total=sum(widths)
    cols=''.join(f'<col style="width:{v/total*100}%">' for v in widths)
    rows=''.join('<tr>'+''.join(f'<{"th" if ri==0 else "td"}>{E(str(c))}</{"th" if ri==0 else "td"}>' for c in row)+'</tr>' for ri,row in enumerate(e['rows']))
    elems.append(f'<div {attr} style="{pos}font-size:{e.get("size",20)*1.5}px"><table><colgroup>{cols}</colgroup><tbody>{rows}</tbody></table></div>')
   elif e['type']=='chart':
    cfg={k:e[k] for k in ['categories','values','series_name','max','unit','format','color'] if k in e}
    elems.append(f'<div {attr} data-chart="{E(json.dumps(cfg))}" style="{pos}">{chart_svg(e)}</div>')
   else:raise ValueError('Unsupported element '+e['type'])
  notes=json.dumps(s.get('notes',[]),ensure_ascii=False).replace('<','\\u003c')
  sections.append(f'<section class="slide {"active visible" if i==0 else ""}" aria-label="Slide {i+1}: {E(s["title"])}" style="background:{s.get("background","#FFFFFF")}">{"".join(elems)}<script type="application/json" data-notes>{notes}</script></section>')
 js='''/* === NAVIGATION, EDITING AND SOURCE NOTES === */
class SlidePresentation{
 constructor(){this.slides=[...document.querySelectorAll('.slide')];this.index=0;this.edit=false;this.stage=document.querySelector('.deck-stage');this.scale();window.addEventListener('resize',()=>this.scale());this.show(0);
 document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='s'){e.preventDefault();this.save();return}if(e.target.isContentEditable)return;if(['ArrowRight','ArrowDown',' ','PageDown'].includes(e.key)){e.preventDefault();this.show(this.index+1)}if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();this.show(this.index-1)}if(e.key.toLowerCase()==='e')this.toggle();if(e.key==='Escape'&&this.edit)this.toggle();});
 let start=0,last=0;document.addEventListener('touchstart',e=>start=e.changedTouches[0].clientX,{passive:true});document.addEventListener('touchend',e=>{let d=e.changedTouches[0].clientX-start;if(!this.edit&&Math.abs(d)>45)this.show(this.index+(d<0?1:-1))},{passive:true});document.addEventListener('wheel',e=>{if(e.target.closest('#sourcePanel')||this.edit)return;if(Date.now()-last>500&&Math.abs(e.deltaY)>20){this.show(this.index+(e.deltaY>0?1:-1));last=Date.now()}},{passive:true});
 }
 scale(){let f=Math.min(innerWidth/1920,innerHeight/1080);this.stage.style.transform=`translate(${(innerWidth-1920*f)/2}px,${(innerHeight-1080*f)/2}px) scale(${f})`;}
 show(i){this.index=Math.max(0,Math.min(i,this.slides.length-1));this.slides.forEach((s,j)=>{s.classList.toggle('active',j===this.index);s.classList.toggle('visible',j===this.index)});document.querySelector('#count').textContent=`${this.index+1} / ${this.slides.length}`;this.sources(false);}
 toggle(){this.edit=!this.edit;document.querySelectorAll('[data-pptx=text],td,th').forEach(e=>{e.contentEditable=String(this.edit)});document.querySelector('#edit').textContent=this.edit?'Finish editing':'Edit text (E)';}
 sources(toggle=true){let p=document.querySelector('#sourcePanel');if(toggle)p.hidden=!p.hidden;p.textContent=JSON.parse(this.slides[this.index].querySelector('[data-notes]').textContent).join('\\n\\n');}
 save(){if(this.edit)this.toggle();let clone=document.documentElement.cloneNode(true);clone.querySelector('#sourcePanel').hidden=true;let blob=new Blob(['<!DOCTYPE html>\\n'+clone.outerHTML],{type:'text/html'});let a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='northbridge-im-edited.html';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),5000);}
}
window.deck=new SlidePresentation();document.querySelector('#prev').onclick=()=>deck.show(deck.index-1);document.querySelector('#next').onclick=()=>deck.show(deck.index+1);document.querySelector('#edit').onclick=()=>deck.toggle();document.querySelector('#save').onclick=()=>deck.save();document.querySelector('#sources').onclick=()=>deck.sources();
'''
 return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(data['title'])}</title><style>{base}\n{css}</style></head><body><div class="deck-viewport"><main class="deck-stage">{''.join(sections)}</main></div><nav class="deck-controls" aria-label="Presentation controls"><button id="prev" aria-label="Previous slide">←</button><span id="count"></span><button id="next" aria-label="Next slide">→</button><button id="edit">Edit text (E)</button><button id="save">Save HTML</button><button id="sources">Sources</button></nav><aside id="sourcePanel" hidden></aside><script>{js}</script></body></html>'''
if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit('Usage: render_html.py STORYBOARD_JSON OUTPUT_HTML')
 p=Path(sys.argv[2]);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(render(json.loads(Path(sys.argv[1]).read_text())));print(p)
