"""Prepare four explicit off-lattice inputs and initial-state certificates.

This is initial-condition construction only. The ODE integrator is disabled.
The production runner has no default grid; this optional future run is NOT_RUN.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
os.environ.setdefault('MPLCONFIGDIR', '/tmp/c21n_mplconfig')

import numpy as np
import builder
from mass_shell_derivatives import initial_cancellation_jet
from shared_runner import load_grid

HERE = Path(__file__).resolve().parent
M = HERE.parent / 'cr_c21m_independent_stress_20261021'


def write_new(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def prepare(output):
    if output.exists():
        raise FileExistsError('CREATE_ONLY_PREPARATION')
    grid = {'schema':'C21N_GRID_V1',
            'run_id':'c21n_offgrid4_opposing_z20_z4_20261021',
            'purpose':'Optional off-lattice opposing-stress science follow-up; not a performance benchmark',
            'cases':[{'case_id':name,'S0':0.,'Pm0':p,'Pr0':-p}
                     for name,p in [('opp_mn175_rp175',-1.75e-4),('opp_mn075_rp075',-7.5e-5),
                                    ('opp_mp075_rn075',7.5e-5),('opp_mp175_rn175',1.75e-4)]]}
    spec = importlib.util.spec_from_file_location('c21m_original_offgrid_preparation', M/'builder.py')
    original = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = original
    spec.loader.exec_module(original)
    def forbidden(*args, **kwargs):
        raise AssertionError('ODE_FORBIDDEN_DURING_INPUT_PREPARATION')
    saved = builder.parent.CanonicalFVSpecies.integrate
    builder.parent.CanonicalFVSpecies.integrate = forbidden
    try:
        prepared = builder.IndependentStressBuilder()
        baseline = original.IndependentStressBuilder(optimized=False)
        cases = []
        for case in grid['cases']:
            target = [case[k] for k in ('S0','Pm0','Pr0')]
            a,ra = prepared.build(*target)
            b,rb = baseline.build(*target)
            if ra != rb or a.initial_state().tobytes() != b.initial_state().tobytes():
                raise AssertionError('OFFGRID_INITIAL_SOURCE_PARITY')
            y = a.initial_state()
            if a.rhs(0.,y).tobytes() != b.rhs(0.,y).tobytes():
                raise AssertionError('OFFGRID_INITIAL_RHS_PARITY')
            cases.append({'case':case,'mapping':ra,
                          'initial_state_sha256':hashlib.sha256(y.tobytes()).hexdigest(),
                          'mapping_values_match_original':True,
                          'initial_state_and_RHS_bytes_match_original':True,
                          'local_jet':initial_cancellation_jet(a,y)})
        output.mkdir(parents=True, exist_ok=False)
        grid_path = output/'grid_offgrid4.json'
        write_new(grid_path,grid)
        accepted,grid_hash = load_grid(grid_path)
        write_new(output/'INITIAL_CONDITION_CERTIFICATES.json', {
            'schema':'C21N_OFFGRID4_PREPARATION_V1','status':'PREPARED_VALIDATED_NOT_RUN',
            'science_execution':'NOT_RUN','new_ODE_integrations':0,
            'run_id':accepted['run_id'],'grid_sha256':grid_hash,'case_count':len(cases),
            'source':prepared.identity(), 'cases':cases,
            'deduplication':'No coordinate match to accepted125 within per-axis 2e-13',
            'other_conversations_or_inaccessible_raw':'UNAVAILABLE; fresh external intake required before execution',
            'maximum_useful_science_workers':4,
            'performance_benchmark':False,'global_error_bound':None,
            'preparation_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'diagnostic_source_sha256':hashlib.sha256((HERE/'mass_shell_derivatives.py').read_bytes()).hexdigest()})
    finally:
        builder.parent.CanonicalFVSpecies.integrate = saved
    print(json.dumps({'status':'PREPARED_VALIDATED_NOT_RUN','cases':4,'new_ODE_integrations':0,
                      'grid_sha256':grid_hash,'output':str(output)}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--output',required=True,type=Path)
    prepare(p.parse_args().output.resolve())
