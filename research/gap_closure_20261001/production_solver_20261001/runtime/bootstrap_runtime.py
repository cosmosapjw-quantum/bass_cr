"""Read-only access to frozen project numerical dependencies; no native load."""
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
FND=REPO/'research/foundation_rebuild'
TP1=FND/'tp1_short_transport_20260926'
TP2D=FND/'tp2d_runtime_self_qualified_transport_20260927'
R4C=FND/'ncp_shared_research_20260928/r4c_temporal_continuation'
R4F=FND/'ncp_shared_research_20260928/r4f_parallel_migration_20260929'
for path in (TP1,TP2D,R4C,R4F):
    if str(path) not in sys.path:sys.path.insert(0,str(path))
