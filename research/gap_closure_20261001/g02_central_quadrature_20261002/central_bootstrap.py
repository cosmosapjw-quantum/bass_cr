"""Explicit additive R4Y imports; no mutation of the archived numerical code."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
R4X = HERE.parent / 'g02_continuous_basis_20261002'
sys.path.insert(0, str(R4X))
import operator_bootstrap
from operator_bootstrap import REPO, FND, HPC
sys.path.insert(0, str(FND / 'tp2d_runtime_self_qualified_transport_20260927'))
sys.path.insert(0, str(HERE))
