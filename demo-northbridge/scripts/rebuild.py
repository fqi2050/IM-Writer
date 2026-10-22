"""Rebuild the synthetic example into a new run directory. Keep original inputs intact."""
import os,sys,shutil,subprocess,argparse
from pathlib import Path
from datetime import datetime
p=argparse.ArgumentParser();p.add_argument('--output-dir');p.add_argument('--backend',choices=['auto','portable','codex'],default='auto');p.add_argument('--native-from-storyboard',action='store_true',help='Browser-free fallback: author HTML and native PPT from the same measured storyboard');a=p.parse_args()
root=Path(__file__).resolve().parents[1];skill=root.parent/'skills/mna-information-memo'
node=os.environ.get('IM_NODE') or shutil.which('node');modules=os.environ.get('RUNTIME_NODE_MODULES');pskill=os.environ.get('IM_PRESENTATIONS_SKILL')
backend=a.backend
if backend=='auto':backend='codex' if all([node,modules,pskill]) else 'portable'
if a.native_from_storyboard and backend!='codex':raise SystemExit('--native-from-storyboard is the Codex exporter. For Copilot use --backend portable.')
if backend=='codex' and not all([node,modules,pskill]):raise SystemExit('Codex backend requires IM_NODE, RUNTIME_NODE_MODULES and IM_PRESENTATIONS_SKILL. In Copilot use --backend portable; do not install the private runtime.')
if backend=='portable':
 subprocess.run([sys.executable,skill/'scripts/build_portable.py',skill/'assets/storyboard-example.json',root/'runs/preflight-unused','--check'],check=True)
 import importlib.util
 if importlib.util.find_spec('docx') is None:raise SystemExit('Install the skill requirements.txt with this Python interpreter.')
out=Path(a.output_dir).resolve() if a.output_dir else root/'runs'/datetime.now().strftime('%Y%m%d-%H%M%S')
if out.exists():raise SystemExit('Output directory already exists. Choose a new directory.')
for folder in ['.build','working','outputs']:(out/folder).mkdir(parents=True,exist_ok=True)
shutil.copytree(root/'inputs',out/'inputs')
for name in ['build_storyboard.py','finalize.mjs','build_review.py','render_native.mjs']:shutil.copy(root/'scripts'/name,out/'.build'/name)
shutil.copy(skill/'scripts/prepare_layout.py',out/'.build/prepare_layout.py')
shutil.copy(skill/'scripts/html_to_pptx.mjs',out/'.build/html_to_pptx.mjs')
if backend=='codex':(out/'.build/node_modules').symlink_to(Path(modules),target_is_directory=True)
env=dict(os.environ,IM_PYTHON=sys.executable)
def run(args):subprocess.run([str(x) for x in args],check=True,env=env)
run([sys.executable,skill/'scripts/extract_sources.py',out/'inputs',out/'working/extracted.json'])
run([sys.executable,out/'.build/build_storyboard.py'])
run([sys.executable,out/'.build/prepare_layout.py',out/'working/storyboard.json',skill/'assets/advisory-dense.json'])
run([sys.executable,skill/'scripts/render_html.py',out/'working/storyboard.json',out/'outputs/northbridge-im.html'])
if backend=='portable':
 run([node,skill/'scripts/storyboard_to_pptx.cjs',out/'working/storyboard.json',out/'outputs/northbridge-im-editable.pptx'])
 run([sys.executable,skill/'scripts/validate_native.py',out/'working/storyboard.json',out/'outputs/northbridge-im-editable.pptx',out/'outputs/validation.json'])
elif a.native_from_storyboard:
 run([node,out/'.build/render_native.mjs',out/'working/storyboard.json',out/'.build/draft.pptx',out/'.build/previews',skill/'assets/advisory-dense.json'])
else:
 run([node,out/'.build/html_to_pptx.mjs',out/'outputs/northbridge-im.html',out/'.build/draft.pptx',out/'.build/previews'])
if backend=='codex':run([node,out/'.build/finalize.mjs'])
(out/'working/build-info.json').write_text(__import__('json').dumps({'backend':backend,'html_dom_converted':backend=='codex' and not a.native_from_storyboard,'desktop_powerpoint_tested':False}),encoding='utf-8')
run([sys.executable,out/'.build/build_review.py'])
print('Rebuilt example:',out/'outputs')
