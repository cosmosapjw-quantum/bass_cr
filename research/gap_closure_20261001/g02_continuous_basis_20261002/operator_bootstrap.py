"""Explicit repository imports for the additive R4X diagnostic operator."""
from pathlib import Path
import os
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FND = REPO / 'research/foundation_rebuild'
HPC = HERE.parent / 'hpc_optimization_20261001'
PATHS = (HERE, HPC, REPO, FND / 'src', FND / 'reaudit_20260925/repair',
         FND / 'full_operator_20260926', FND / 'tp2a_perf_20260926',
         FND / 'tp2a_derivative_aware_20260926', FND / 'tp2a_reference_qualified_20260926',
         FND / 'tp2a_analytic_pruning_20260926/code')
for path in reversed(PATHS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
if os.environ.get('BASS_ANALYTIC_SOURCE_ROOT', str(REPO)) != str(REPO):
    raise ValueError('external analytic source override forbidden')
os.environ['BASS_ANALYTIC_SOURCE_ROOT'] = str(REPO)
