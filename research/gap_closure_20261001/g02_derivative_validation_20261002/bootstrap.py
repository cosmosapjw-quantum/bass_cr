"""Additive R4Z imports; keep the archived analytic bootstrap module distinct."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
R4X = HERE.parent / 'g02_continuous_basis_20261002'
R4Y = HERE.parent / 'g02_central_quadrature_20261002'
sys.path.insert(0, str(R4X))
import operator_bootstrap
from operator_bootstrap import REPO, FND, HPC
# Preload the archived module before exposing this stage's same-named file.
import bootstrap as archived_analytic_bootstrap
if Path(archived_analytic_bootstrap.__file__).resolve() != FND / 'tp2a_analytic_pruning_20260926/code/bootstrap.py':
    raise ImportError('archived analytic bootstrap identity mismatch')
sys.path.insert(0, str(R4Y))
sys.path.insert(0, str(FND / 'tp2d_runtime_self_qualified_transport_20260927'))
