import path from 'node:path';
import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'..'), skill=process.env.IM_PRESENTATIONS_SKILL;
if(!skill||!process.env.IM_PYTHON)throw Error('Set IM_PRESENTATIONS_SKILL and IM_PYTHON');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const storyboard=JSON.parse(await fs.readFile(path.join(root,'working/storyboard.json'),'utf8'));
const owners=type=>storyboard.slides.flatMap((s,i)=>s.elements.some(e=>e.type===type)?[i+1]:[]);
const finalPath=path.join(root,'outputs/northbridge-im-editable.pptx');
const result=await finalizePresentation({workspaceDir:root,candidatePath:path.join(root,'.build/draft.pptx'),finalPath,pythonExecutable:process.env.IM_PYTHON,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...owners('table').flatMap(n=>['--require-native-table-slide',String(n)])],explicitTotalSlideCount:10,tableArithmeticContracts:[
 {slide:4,table:1,label_column:0,total_row:4,value_columns:[1],component_rows:[1,2,3]},
 {slide:6,table:1,label_column:0,total_row:4,value_columns:[1,3,4],component_rows:[1,2,3]},
 {slide:7,table:1,label_column:0,total_row:3,value_columns:[1,2,3],component_rows:[1,2]},
 {slide:7,table:1,label_column:0,total_row:5,value_columns:[1,2,3],component_rows:[3,4]},
 {slide:7,table:2,label_column:0,total_row:5,value_columns:[1,2],component_rows:[1,2,3,4]},
 {slide:8,table:2,label_column:0,total_row:6,value_columns:[1,2],component_rows:[1,2,3,4,5]},
 ],requiredNativeTableOwnerSlides:owners('table'),requiredNativeChartOwnerSlides:owners('chart'),materializeLiteralChartWorkbooks:true,nativeChartTargetApplication:'portable',fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(root,'.build/portable-final-validation.json')});
console.log(JSON.stringify(result));
