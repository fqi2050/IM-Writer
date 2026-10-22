/** Explicit browser-free fallback: render this demo from the same measured storyboard as HTML. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const [source,draft,preview,profile]=process.argv.slice(2);
if(!profile)throw Error('Usage: render_native.mjs STORYBOARD DRAFT_PPTX PREVIEW_DIR PROFILE_JSON');
const data=JSON.parse(await fs.readFile(source,'utf8')),theme=JSON.parse(await fs.readFile(profile,'utf8'));
if(data.style_profile!=='advisory-dense')throw Error('Required report profile missing');
await fs.mkdir(path.dirname(draft),{recursive:true});await fs.mkdir(preview,{recursive:true});
const presentation=Presentation.create({slideSize:{width:1280,height:720}});
for(const s of data.slides){
 const slide=presentation.slides.add();slide.background.fill=s.background;
 for(const e of s.elements){
  const position={left:e.x,top:e.y,width:e.w,height:e.h};
  if(e.type==='text'){
   const sh=slide.shapes.add({geometry:'textbox',name:e.id,position,fill:'none',line:{fill:'none',width:0}});
   sh.text=e.text;sh.text.style={fontSize:e.size,typeface:'Arial',bold:e.bold,color:e.color,alignment:e.align||'left',verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0};
  }else if(e.type==='rule')slide.shapes.add({geometry:'rect',name:e.id,position,fill:e.color,line:{fill:'none',width:0}});
  else if(e.type==='table'){
   if(!e.row_heights)throw Error('Run prepare_layout.py before native export');
   const sum=e.widths.reduce((a,b)=>a+b,0);
   const tb=slide.tables.add({rows:e.rows.length,columns:e.rows[0].length,left:e.x,top:e.y,width:e.w,height:e.h,values:e.rows,columnWidths:e.widths.map(v=>e.w*v/sum)});
   tb.borders.assign({fill:theme.table_border,width:0.6,style:'solid'});
   for(let r=0;r<e.rows.length;r++){
    tb.rows[r].height=e.row_heights[r];
    for(let c=0;c<e.rows[r].length;c++){
     const cell=tb.getCell(r,c);cell.fill=r===0?theme.table_header:r%2===0?theme.table_band:'#FFFFFF';
     cell.text.style={fontSize:e.size,typeface:'Arial',color:r===0?theme.table_header_text:theme.text,bold:r===0||e.emphasis_rows?.includes(r),alignment:e.column_align[c],verticalAlignment:'middle',insets:{left:theme.table_padding_x,right:theme.table_padding_x,top:theme.table_padding_y,bottom:theme.table_padding_y},autoFit:'none'};
    }
   }
  }else if(e.type==='chart'){
   const chart=slide.charts.add('bar',{position,categories:e.categories,series:[{name:e.series_name,values:e.values,fill:e.color,valuesFormatCode:e.format}],hasLegend:false,titlePlacement:'none',barOptions:{direction:'column',grouping:'clustered',gapWidth:80},xAxis:{visible:true,textStyle:{fontSize:13,fill:theme.muted},line:{fill:theme.table_border,width:.6}},yAxis:{visible:true,min:0,max:e.max,majorUnit:e.max/4,numberFormatCode:e.format,textStyle:{fontSize:13,fill:theme.muted},majorGridlines:{fill:theme.table_border,width:.6}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:e.format,textStyle:{fontSize:16,bold:true,fill:theme.primary}},chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF'});
   if(!process.env.IM_PRESENTATIONS_SKILL)throw Error('Set IM_PRESENTATIONS_SKILL');
   const {applyPresentationChartFont}=await import(pathToFileURL(path.join(process.env.IM_PRESENTATIONS_SKILL,'container_tools/artifact_tool_utils.mjs')).href);applyPresentationChartFont(chart,{fontFamily:'Arial'});
  }else throw Error('Unsupported semantic element: '+e.type);
 }
 slide.speakerNotes.text=s.notes.join('\n\n');
}
await(await PresentationFile.exportPptx(presentation)).save(draft);
for(let i=0;i<presentation.slides.items.length;i++){
 const blob=await presentation.export({slide:presentation.slides.items[i],format:'png',scale:1.5});
 await fs.writeFile(path.join(preview,`ppt-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
}
console.log('Rendered '+data.slides.length+' native slides from the shared measured storyboard (no browser).');
