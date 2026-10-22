/** Convert the supported semantic HTML slide format into native PowerPoint objects. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const [htmlPath,pptxPath,previewDir]=process.argv.slice(2);
if(!previewDir)throw Error('Usage: html_to_pptx.mjs INPUT_HTML DRAFT_PPTX PREVIEW_DIR');
await fs.mkdir(previewDir,{recursive:true});await fs.mkdir(path.dirname(pptxPath),{recursive:true});
// Disable scripts in source HTML and block all outbound network requests.
const browser=await chromium.launch({headless:true, ...(process.env.IM_BROWSER_PATH ? {executablePath:process.env.IM_BROWSER_PATH} : {channel:"chrome"})});
let context;
try{
 context=await browser.newContext({viewport:{width:1920,height:1080},javaScriptEnabled:false});
 await context.route('**/*',route=>{const u=route.request().url();return /^(file:|data:|about:)/.test(u)?route.continue():route.abort();});
 const page=await context.newPage();await page.goto(pathToFileURL(path.resolve(htmlPath)).href);
 // Disable transitions before measuring/capturing; otherwise later slides can be captured at opacity 0.
 await page.evaluate(()=>document.querySelectorAll('.slide').forEach(s=>s.style.transition='none'));
 const data=await page.evaluate(()=>{
  const hex=c=>{const m=c.match(/\d+/g);if(!m)throw Error('Unsupported color '+c);return '#'+m.slice(0,3).map(v=>Number(v).toString(16).padStart(2,'0')).join('');};
  const slides=[...document.querySelectorAll('.slide')];
  if(!slides.length)throw Error('No semantic slides found');
  document.querySelector('.deck-stage').style.transform='none';
  const results=[];
  for(const [si,s] of slides.entries()){
   s.style.visibility='visible';s.style.opacity='1';
   const sr=s.getBoundingClientRect();if(sr.width!==1920||sr.height!==1080)throw Error('Slides must be 1920 x 1080');
   const elements=[];
   for(const el of s.querySelectorAll('[data-pptx]')){
    const t=el.dataset.pptx,st=getComputedStyle(el),r=el.getBoundingClientRect();
    if(!['text','table','chart','rule'].includes(t))throw Error('Unsupported semantic element '+t);
    if(st.transform!=='none'||st.backgroundImage!=='none'||(t==='text'&&el.children.length))throw Error('Unsupported styling in '+el.id);
    if(r.left<-.5||r.top<-.5||r.right>1920.5||r.bottom>1080.5)throw Error('Element outside slide: '+el.id);
    let e={id:el.id,type:t,x:r.left/1.5,y:r.top/1.5,w:r.width/1.5,h:r.height/1.5};
    if(t==='text'){
     if(el.scrollHeight>el.clientHeight+2||el.scrollWidth>el.clientWidth+2)throw Error('Text overflow: '+el.id+' '+el.scrollHeight+'/'+el.clientHeight);
     e={...e,text:el.innerText,font:st.fontFamily.split(',')[0].replaceAll('"',''),size:parseFloat(st.fontSize)/1.5,bold:parseInt(st.fontWeight)>=600,color:hex(st.color),align:st.textAlign};
    }else if(t==='rule')e.color=hex(st.backgroundColor);
    else if(t==='table'){
     const table=el.querySelector('table');if(!table)throw Error('No table in '+el.id);
     const rows=[...table.rows];e.rows=rows.map(r=>[...r.cells].map(c=>c.innerText));e.widths=[...rows[0].cells].map(c=>c.getBoundingClientRect().width/1.5);e.rowHeights=rows.map(r=>r.getBoundingClientRect().height/1.5);e.size=parseFloat(st.fontSize)/1.5;
     e.cellStyles=rows.map(row=>[...row.cells].map(cell=>{
      const cs=getComputedStyle(cell);
      if(cell.scrollWidth>cell.clientWidth+2||cell.scrollHeight>cell.clientHeight+2)throw Error('Table cell overflow: '+el.id);
      return {fill:cs.backgroundColor==='rgba(0, 0, 0, 0)'?'#FFFFFF':hex(cs.backgroundColor),color:hex(cs.color),bold:parseInt(cs.fontWeight)>=600,align:cs.textAlign,border:hex(cs.borderBottomColor),size:parseFloat(cs.fontSize)/1.5,insets:{left:parseFloat(cs.paddingLeft)/1.5,right:parseFloat(cs.paddingRight)/1.5,top:parseFloat(cs.paddingTop)/1.5,bottom:parseFloat(cs.paddingBottom)/1.5}};
     }));
     if(e.rows.some(r=>r.length!==e.rows[0].length))throw Error('Ragged table');
     if(table.getBoundingClientRect().height>r.height+2)throw Error('Table overflow: '+el.id);
    }else{
     e.chart=JSON.parse(el.dataset.chart);let c=e.chart;
     if(!Array.isArray(c.values)||c.values.length!==c.categories.length||c.values.some(v=>typeof v!=='number'||!Number.isFinite(v)||v<0||v>c.max))throw Error('Invalid chart data: '+el.id);
    }
    elements.push(e);
   }
   results.push({background:hex(getComputedStyle(s).backgroundColor),elements,notes:JSON.parse(s.querySelector('[data-notes]')?.textContent||'[]')});
   s.style.visibility='hidden';s.style.opacity='0';
  }
  return results;
 });
 await fs.writeFile(path.join(previewDir,'dom-model.json'),JSON.stringify(data,null,2));
 // Render HTML using source scripts disabled; the converter owns slide selection.
 for(let i=0;i<data.length;i++){
  await page.evaluate(i=>{document.querySelectorAll('.slide').forEach((s,j)=>{s.style.visibility=i===j?'visible':'hidden';s.style.opacity=i===j?'1':'0'});document.querySelector('.deck-controls')?.remove();},i);
  await page.screenshot({path:path.join(previewDir,`html-${String(i+1).padStart(2,'0')}.png`)});
 }
 const presentation=Presentation.create({slideSize:{width:1280,height:720}});
 for(const s of data){
  const slide=presentation.slides.add();slide.background.fill=s.background;
  for(const e of s.elements){
   const position={left:e.x,top:e.y,width:e.w,height:e.h};
   if(e.type==='text'){
    const sh=slide.shapes.add({geometry:'textbox',name:e.id,position,fill:'none',line:{fill:'none',width:0}});sh.text=e.text;sh.text.style={fontSize:e.size,typeface:'Arial',bold:e.bold,color:e.color,alignment:e.align,verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0};
   }else if(e.type==='rule'){
    slide.shapes.add({geometry:'rect',name:e.id,position,fill:e.color,line:{fill:'none',width:0}});
   }else if(e.type==='table'){
    const tb=slide.tables.add({rows:e.rows.length,columns:e.rows[0].length,left:e.x,top:e.y,width:e.w,height:e.h,values:e.rows,columnWidths:e.widths});
    tb.borders.assign({fill:e.cellStyles[0][0].border,width:1,style:'solid'});
    for(let r=0;r<e.rows.length;r++){
     tb.rows[r].height=e.rowHeights[r];
     for(let c=0;c<e.rows[r].length;c++){
      const cell=tb.getCell(r,c),cs=e.cellStyles[r][c];cell.fill=cs.fill;cell.text.style={fontSize:cs.size,typeface:'Arial',color:cs.color,bold:cs.bold,alignment:cs.align,verticalAlignment:'middle',insets:cs.insets,autoFit:'none'};
     }
    }
   }else if(e.type==='chart'){
    const c=e.chart;
    const chart=slide.charts.add('bar',{position,categories:c.categories,series:[{name:c.series_name,values:c.values,fill:c.color||'#117F79',valuesFormatCode:c.format||'0.0'}],hasLegend:false,titlePlacement:'none',barOptions:{direction:'column',grouping:'clustered',gapWidth:80},xAxis:{visible:true,textStyle:{fontSize:16,fill:'#586D7C'},line:{fill:'#DCE4E8',width:1}},yAxis:{visible:true,min:0,max:c.max,majorUnit:c.max/4,numberFormatCode:c.format||'0.0',textStyle:{fontSize:15,fill:'#586D7C'},majorGridlines:{fill:'#DCE4E8',width:1}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:c.format||'0.0',textStyle:{fontSize:19,bold:true,fill:'#132E42'}},chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF'});
    // Chart-specific font properties are set by the shared skill helper when available.
    if(process.env.IM_PRESENTATIONS_SKILL){const {applyPresentationChartFont}=await import(pathToFileURL(path.join(process.env.IM_PRESENTATIONS_SKILL,'container_tools/artifact_tool_utils.mjs')).href);applyPresentationChartFont(chart,{fontFamily:'Arial'});}
   }
  }
  slide.speakerNotes.text=s.notes.join('\n\n');
 }
 await(await PresentationFile.exportPptx(presentation)).save(pptxPath);
 for(let i=0;i<presentation.slides.items.length;i++){
  const png=await presentation.export({slide:presentation.slides.items[i],format:'png',scale:1.5});await fs.writeFile(path.join(previewDir,`ppt-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
 }
 console.log(JSON.stringify({slides:data.length,pptx:pptxPath,nativeTables:data.flatMap(s=>s.elements).filter(e=>e.type==='table').length,nativeCharts:data.flatMap(s=>s.elements).filter(e=>e.type==='chart').length}));
}finally{await browser.close();}
