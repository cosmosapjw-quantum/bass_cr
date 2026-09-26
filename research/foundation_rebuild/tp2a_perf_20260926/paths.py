"""Repository-local imports. Does not install packages or modify upstream files."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FND = HERE.parent
for p in (REPO, FND/'src', FND/'reaudit_20260925/repair', FND/'full_operator_20260926', HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
