"""Compatibility entrypoint for the shared skill layout checker."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parents[2]/'skills/mna-information-memo/scripts/prepare_layout.py'),run_name='__main__')
