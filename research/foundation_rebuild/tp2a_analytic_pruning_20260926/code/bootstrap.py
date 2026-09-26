"""Repository-local dependency imports, without installation or upstream edits."""
from pathlib import Path
import os,sys
HERE=Path(__file__).resolve().parent
DEFAULT=HERE.parents[2] if HERE.parent.name=='foundation_rebuild' else HERE.parent/'inputs/z0/repo'
REPO=Path(os.environ.get('BASS_ANALYTIC_SOURCE_ROOT',DEFAULT)).resolve()
FND=REPO/'research/foundation_rebuild'
for path in (FND/'src',FND/'reaudit_20260925/repair',FND/'full_operator_20260926',FND/'tp2a_perf_20260926',FND/'tp2a_derivative_aware_20260926',FND/'tp2a_reference_qualified_20260926',REPO):
    if str(path) not in sys.path:sys.path.append(str(path))
