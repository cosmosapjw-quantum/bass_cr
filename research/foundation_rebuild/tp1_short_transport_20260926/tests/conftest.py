from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
TP1=HERE.parent
REPO=TP1.parents[2]
REPAIR=TP1.parent/'reaudit_20260925'/'repair'
FND_SRC=TP1.parent/'src'
FULL=TP1.parent/'full_operator_20260926'
sys.path[:0]=[str(TP1),str(FULL),str(REPAIR),str(FND_SRC),str(REPO)]
