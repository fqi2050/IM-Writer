import path from 'node:path';
import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'..'), skill=process.env.IM_PRESENTATIONS_SKILL;
if(!skill||!process.env.IM_PYTHON)throw Error('Set IM_PRESENTATIONS_SKILL and IM_PYTHON');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const finalPath=path.join(root,'outputs/northbridge-im-editable.pptx');
const result=await finalizePresentation({workspaceDir:root,candidatePath:path.join(root,'.build/draft.pptx'),finalPath,pythonExecutable:process.env.IM_PYTHON,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[4,6,7,8,9,10].flatMap(n=>['--require-native-table-slide',String(n)])],explicitTotalSlideCount:10,requiredNativeTableOwnerSlides:[4,6,7,8,9,10],requiredNativeChartOwnerSlides:[5,8],materializeLiteralChartWorkbooks:true,nativeChartTargetApplication:'portable',fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(root,'.build/portable-final-validation.json')});
console.log(JSON.stringify(result));
