"""Rebuild the synthetic example into a new run directory. Keep original inputs intact."""
import os,sys,shutil,subprocess,argparse
from pathlib import Path
from datetime import datetime
p=argparse.ArgumentParser();p.add_argument('--output-dir');a=p.parse_args()
root=Path(__file__).resolve().parents[1];skill=root.parent/'skills/mna-information-memo'
node=os.environ.get('IM_NODE');modules=os.environ.get('RUNTIME_NODE_MODULES');pskill=os.environ.get('IM_PRESENTATIONS_SKILL')
if not all([node,modules,pskill]):raise SystemExit('Set IM_NODE, RUNTIME_NODE_MODULES and IM_PRESENTATIONS_SKILL from the Codex workspace dependency loader. Run this script with the bundled Python runtime.')
out=Path(a.output_dir).resolve() if a.output_dir else root/'runs'/datetime.now().strftime('%Y%m%d-%H%M%S')
if out.exists():raise SystemExit('Output directory already exists. Choose a new directory.')
for folder in ['.build','working','outputs']:(out/folder).mkdir(parents=True,exist_ok=True)
shutil.copytree(root/'inputs',out/'inputs')
for name in ['build_storyboard.py','finalize.mjs']:shutil.copy(root/'scripts'/name,out/'.build'/name)
shutil.copy(skill/'scripts/html_to_pptx.mjs',out/'.build/html_to_pptx.mjs')
(out/'.build/node_modules').symlink_to(Path(modules),target_is_directory=True)
env=dict(os.environ,IM_PYTHON=sys.executable)
def run(args):subprocess.run([str(x) for x in args],check=True,env=env)
run([sys.executable,skill/'scripts/extract_sources.py',out/'inputs',out/'working/extracted.json'])
run([sys.executable,out/'.build/build_storyboard.py'])
run([sys.executable,skill/'scripts/render_html.py',out/'working/storyboard.json',out/'outputs/northbridge-im.html'])
run([node,out/'.build/html_to_pptx.mjs',out/'outputs/northbridge-im.html',out/'.build/draft.pptx',out/'.build/previews'])
run([node,out/'.build/finalize.mjs'])
print('Rebuilt example:',out/'outputs')
