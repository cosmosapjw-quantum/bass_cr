from pathlib import Path
import sys
HERE=Path(__file__).resolve().parents[1]
FND=HERE.parent
REPO=HERE.parents[2]
for p in (HERE,FND/'tp2a_derivative_aware_20260926',FND/'tp2a_perf_20260926',FND/'src',FND/'full_operator_20260926',FND/'reaudit_20260925/repair',REPO):
    if str(p) not in sys.path:
        sys.path.insert(0,str(p))
