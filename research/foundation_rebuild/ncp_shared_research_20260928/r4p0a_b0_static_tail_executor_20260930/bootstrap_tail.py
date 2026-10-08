"""Reuse existing source modules without changing numerical code."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
FND=HERE.parents[1]
REPO=HERE.parents[3]
R4F=HERE.parent/'r4f_parallel_migration_20260929'
R4G=HERE.parent/'r4g_n768_to_n1536_20260929'
R4C=HERE.parent/'r4c_temporal_continuation'
for p in (REPO,FND/'src',FND/'reaudit_20260925/repair',FND/'full_operator_20260926',FND/'tp2a_perf_20260926',FND/'tp1_short_transport_20260926',FND/'tp2a_derivative_aware_20260926',FND/'tp2a_analytic_pruning_20260926/code',FND/'tp2d_runtime_self_qualified_transport_20260927',R4C,R4G,R4F,HERE.parent/'r4p0_tail_basis_preflight_20260930',HERE):
    if str(p) not in sys.path:sys.path.insert(0,str(p))
