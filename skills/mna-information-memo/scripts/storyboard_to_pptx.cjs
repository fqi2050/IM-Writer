/** Portable native PPT export. No Codex runtime, browser, or private package required. */
const fs = require('node:fs');
const path = require('node:path');
let PptxGenJS;
try { PptxGenJS = require('pptxgenjs'); }
catch { console.error('Missing pptxgenjs. Run npm ci in the mna-information-memo skill folder. Do not install @oai/artifact-tool for this mode.'); process.exit(2); }
if (process.argv[2] === '--check') { console.log('Portable PPT dependency available: pptxgenjs'); process.exit(0); }
const [input, output] = process.argv.slice(2);
if (!output) throw Error('Usage: node storyboard_to_pptx.cjs STORYBOARD_JSON OUTPUT_PPTX');
const data = JSON.parse(fs.readFileSync(input, 'utf8'));
const theme = JSON.parse(fs.readFileSync(path.join(__dirname, '../assets/advisory-dense.json'), 'utf8'));
if ((data.style_profile ?? 'advisory-dense') !== 'advisory-dense' || data.style_profile === null) throw Error('Required style: advisory-dense');
const color = v => (v || theme.text).replace(/^#/, '');
const inch = n => n / 96, pt = n => n * .75;
const pptx = new PptxGenJS();
pptx.defineLayout({name:'IM',width:1280/96,height:720/96}); pptx.layout='IM';
pptx.author='IM Writer'; pptx.subject='Information memorandum'; pptx.title=data.title;
pptx.lang='en-GB'; pptx.theme={headFontFace:'Arial',bodyFontFace:'Arial',lang:'en-GB'};
for (const page of data.slides) {
 const slide = pptx.addSlide(); slide.background={color:color(page.background || theme.background)};
 for (const e of page.elements) {
  if (![e.x,e.y,e.w,e.h].every(Number.isFinite) || e.x<0 || e.y<0 || e.w<=0 || e.h<=0 || e.x+e.w>1280.1 || e.y+e.h>720.1) throw Error('Invalid geometry: '+e.id);
  const pos={x:inch(e.x),y:inch(e.y),w:inch(e.w),h:inch(e.h)};
  if(e.type==='text') slide.addText(e.text,{...pos,fontFace:'Arial',fontSize:pt(e.size || 20),color:color(e.color),bold:!!e.bold,align:e.align || 'left',valign:'top',margin:0,breakLine:false,lineSpacing:pt(e.size || 20)*1.18,paraSpaceAfter:0,paraSpaceBefore:0,transparency:0});
  else if(e.type==='rule') slide.addShape(pptx.ShapeType.rect,{...pos,line:{color:color(e.color),transparency:100},fill:{color:color(e.color)}});
  else if(e.type==='table') {
   if(!e.row_heights || e.row_heights.length!==e.rows.length || e.row_heights.some(h=>!Number.isFinite(h)||h<=0) || Math.abs(e.row_heights.reduce((a,b)=>a+b,0)-e.h)>.1) throw Error('Run prepare_layout.py first: '+e.id);
   const total=e.widths.reduce((a,b)=>a+b,0);
   const rows=e.rows.map((row,r)=>row.map((value,c)=>({text:String(value),options:{align:e.column_align?.[c] || 'left',bold:r===0 || e.emphasis_rows?.includes(r),color:color(r===0?theme.table_header_text:theme.text),fill:color(r===0?theme.table_header:r%2===0?theme.table_band:theme.background)}})));
   slide.addTable(rows,{...pos,colW:e.widths.map(w=>inch(e.w*w/total)),rowH:e.row_heights.map(inch),autoPage:false,fontFace:'Arial',fontSize:pt(e.size || theme.sizes.table),margin:[pt(theme.table_padding_y),pt(theme.table_padding_x),pt(theme.table_padding_y),pt(theme.table_padding_x)],border:{type:'solid',color:color(theme.table_border),pt:.45},valign:'middle',paraSpaceAfter:0,paraSpaceBefore:0,lineSpacingMultiple:1.18});
  } else if(e.type==='chart') {
   if(!e.values.length || e.values.length!==e.categories.length || !e.values.every(v=>Number.isFinite(v)&&v>=0) || !Number.isFinite(e.max) || e.max<=0 || Math.max(...e.values)>e.max) throw Error('Invalid bar chart: '+e.id);
   slide.addChart(pptx.ChartType.bar,[{name:e.series_name,labels:e.categories.map(String),values:e.values}],{...pos,barDir:'col',catAxisLabelFontFace:'Arial',catAxisLabelFontSize:pt(13),catAxisLabelColor:color(theme.muted),valAxisLabelFontFace:'Arial',valAxisLabelFontSize:pt(13),valAxisLabelColor:color(theme.muted),chartColors:[color(e.color || theme.primary)],showLegend:false,showTitle:false,showValue:true,showCatName:false,showSerName:false,showBorder:false,valAxisMinVal:0,valAxisMaxVal:e.max,valAxisMajorUnit:e.max/4,valAxisLabelFormatCode:e.format || '0.0',dataLabelFormatCode:e.format || '0.0',dataLabelPosition:'outEnd',dataLabelColor:color(theme.primary),dataLabelFontFace:'Arial',dataLabelFontSize:pt(16),dataLabelFontBold:true,valGridLine:{color:color(theme.table_border),width:.45},catAxisLineColor:color(theme.table_border),catAxisLineSize:.45,showCatName:false,showMarker:false,showLine:false,gapSize:80});
  } else throw Error('Unsupported semantic element: '+e.type);
 }
 slide.addNotes((page.notes || []).join('\n\n'));
}
fs.mkdirSync(path.dirname(path.resolve(output)),{recursive:true});
pptx.writeFile({fileName:output}).then(()=>console.log('Exported '+data.slides.length+' editable slides: '+output)).catch(e=>{console.error(e);process.exitCode=1;});
