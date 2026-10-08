import sys
from pathlib import Path
r=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(r))
sys.path.insert(0,str(r/"vendor"))
sys.path.insert(0,str(r/"source"))
