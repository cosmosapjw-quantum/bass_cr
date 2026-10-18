"""Load the immutable sibling C21E source, never a synthetic native stand-in."""
from pathlib import Path
import sys
PARENT=Path(__file__).resolve().parents[2]/"cr_c21e_event_native_20261018"
SOURCE=PARENT/"src"
if not (SOURCE/"event_coupler.py").is_file():
    raise RuntimeError("C21E sibling missing: checkout the stated parent commit")
if str(SOURCE) not in sys.path:sys.path.insert(0,str(SOURCE))
