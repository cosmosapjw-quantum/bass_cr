"""Create an OPTIONAL nested-grid refinement without any ODE integration.

Subtract the current 27 targets and source-audited C21L/HH/PR198 grids.
This future unit is not a prerequisite for completing the first 27-point pilot.
All generated files use create-only writes. No source or prior raw is modified.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from unittest.mock import patch

import numpy as np

import builder

HERE=Path(__file__).resolve().parent
C21L=HERE.parent/'cr_c21l_rei_pilot_20261021'
S_AXIS=(-.012,-.006,0.,.006,.012)
P_AXIS=(-.0002,-.0001,0.,.0001,.0002)
AXIS_ATOL=2e-13


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    with Path(path).open('x') as handle:
        json.dump(value,handle,indent=2,sort_keys=True,allow_nan=False)
        handle.write('\n')


def audited_known_targets():
    prior=json.loads((HERE/'GRID_DEDUP.json').read_text())
    for name,digest in prior['known_grid_source_sha256'].items():
        if sha(HERE/name)!=digest:
            raise ValueError('PREVIOUSLY_AUDITED_EXTERNAL_SOURCE_CHANGED:'+name)
    manifest_path=C21L/'runs/pilot81/MANIFEST.json'
    if sha(manifest_path)!=prior['C21L_manifest_sha256']:
        raise ValueError('C21L_GRID_MANIFEST_CHANGED')
    source=json.loads(manifest_path.read_text())['manifest']
    sqrt2=math.sqrt(2)
    half_s=[0.]+[sign*i*.004/12 for i in range(1,13) for sign in (-1,1)]
    half_p=[0.]+[sign*i*.001/12 for i in range(1,13) for sign in (-1,1)]
    half_m=[sign*i*.0004/12 for i in range(1,13) for sign in (-1,1)]
    hh_s=[0.]+[sign*s for s in (.0005,.001,.002,.004) for sign in (-1,1)]
    hh_p=[0.]+[sign*p for p in (.00025,.0005,.001) for sign in (-1,1)]
    families={
        'C21L81':list(itertools.product(source['S_grid'],[0.],source['P_grid'])),
        'HH63':list(itertools.product(hh_s,[0.],hh_p)),
        'PR198_parent625':[(sqrt2*s,0.,sqrt2*p) for s,p in itertools.product(half_s,half_p)],
        'PR198_matter600':[(sqrt2*s,sqrt2*m,0.) for s,m in itertools.product(half_s,half_m)],
        'PR198_mixed6':[(sqrt2*s,sqrt2*sign*.0004,-sqrt2*sign*.0004) for s,sign in itertools.product((0.,.004,-.004),(-1,1))]}
    if {name:len(values) for name,values in families.items()}!=prior['known_grid_sizes']:
        raise ValueError('AUDITED_GRID_SIZE_MISMATCH')
    return families


def prepare(output):
    output=Path(output).resolve()
    filenames=('grid_ncp_refinement98.json','NCP_REFINEMENT98_PREPARATION.json')
    if any((output/name).exists() for name in filenames):
        raise FileExistsError('REFINEMENT_OUTPUT_IS_CREATE_ONLY')
    output.mkdir(parents=True,exist_ok=True)
    pilot=json.loads((HERE/'grid_pilot26.json').read_text())
    reference=json.loads((HERE/'REFERENCE_REUSE.json').read_text())
    previous=[tuple(c[k] for k in ('S0','Pm0','Pr0')) for c in pilot['cases']]
    previous.append(tuple(reference['requested_display_coordinates'][k] for k in ('S0','Pm0','Pr0')))
    if len(previous)!=27 or len(set(previous))!=27:
        raise ValueError('CURRENT27_TARGETS_NOT_COMPLETE_OR_UNIQUE')
    known=audited_known_targets()
    excluded,remaining=[],[]
    for (i,s),(j,m),(k,r) in itertools.product(enumerate(S_AXIS),enumerate(P_AXIS),enumerate(P_AXIS)):
        case={'case_id':f'ref_s{i}_m{j}_r{k}','S0':s,'Pm0':m,'Pr0':r}
        point=np.array([s,m,r])
        matches={name:int(np.count_nonzero(np.max(abs(np.array(coords)-point),axis=1)<=AXIS_ATOL))
                 for name,coords in {'C21M_current27':previous,**known}.items()}
        if any(matches.values()):
            excluded.append({**case,'matching_family_counts':matches})
        else:
            remaining.append(case)
    if len(remaining)!=98 or len(excluded)!=27:
        raise ValueError('REFINEMENT_COUNT_DIFFERS_FROM_REVIEWED98:'+str((len(remaining),len(excluded))))
    grid={'schema':'C21M_GRID_V1','run_id':'c21m_ncp_refinement98_z20_z4_20261021','cases':remaining}
    template=builder.IndependentStressBuilder()
    identity=template.identity()
    checks=[]
    # Explicitly prohibit integrator calls during preparation, even if a later
    # builder implementation accidentally changes its initial-condition path.
    with patch.object(type(template.template),'integrate',side_effect=AssertionError('ODE_FORBIDDEN_DURING_GRID_PREPARATION')):
        for case in remaining:
            _,mapping=template.build(case['S0'],case['Pm0'],case['Pr0'])
            checks.append({'case_id':case['case_id'],
                           'max_axis_absolute_error':max(mapping['axis_absolute_errors'].values()),
                           'A_m':mapping['A_m'],'k_gamma':mapping['k_gamma'],'k_nu':mapping['k_nu'],
                           'actual_signed_S0':mapping['actual']['signed_Sigma_F'],
                           'actual_signed_Pm0':mapping['actual']['signed_Pi_m_F'],
                           'actual_signed_Pr0':mapping['actual']['signed_Pi_r_F'],
                           'continuum_min_W_m':mapping['continuum_min_W_m'],
                           'continuum_min_W_r':mapping['continuum_min_W_r'],
                           'minimum_massive_cell_number':mapping['minimum_massive_cell_number'],
                           'massive_initial_rho_normalized':mapping['massive_initial_rho_normalized'],
                           'Hamiltonian_relative_residual':mapping['Hamiltonian_relative_residual'],
                           'massive_distribution_rebuilt':mapping['massive_distribution_rebuilt']})
    if template.identity()!=identity:
        raise ValueError('SOURCE_CHANGED_DURING_INITIAL_CONDITION_PREPARATION')
    write(output/filenames[0],grid)
    receipt={'schema':'C21M_OPTIONAL_REFINEMENT_PREPARATION_V1','status':'PASS_SCOPED_INITIAL_CONDITIONS_ONLY',
             'EXECUTION':'NOT_RUN','PUBLICATION':'PENDING_PARENT_CONTENT_COMMIT',
             'BACKUP':'PENDING_PARENT_DELIVERY','DAG':'OPTIONAL_NEXT_UNIT_READY; NOT_REQUIRED_FOR_FIRST_PILOT27_CLOSEOUT',
             'ODE_solves':0,'integrator_calls_forbidden_by_test_guard':True,
             'input_candidates':125,'excluded_current_pilot27_targets':len(excluded),
             'additional_external_exclusions_beyond_current27':0,
             'ready_new_cases':len(remaining),'grid_sha256':sha(output/filenames[0]),
             'grid_filename':filenames[0],'run_id':grid['run_id'],
             'source_identity':identity,'generator_sha256':sha(Path(__file__)),
             'audit_inputs_sha256':{name:sha(HERE/name) for name in ('grid_pilot26.json','REFERENCE_REUSE.json','GRID_DEDUP.json')},
             'axes_signed_full_Frobenius':{'S0':list(S_AXIS),'Pm0':list(P_AXIS),'Pr0':list(P_AXIS)},
             'dedup_axis_absolute_tolerance':AXIS_ATOL,
             'dedup_scope':'Declared physical target grids in audited source metadata. PR198 half coordinates converted by sqrt(2). Current27 are excluded regardless of their live completion state.',
             'unavailable_scope':'Other unexposed conversations or execution returns and unobserved backups: UNAVAILABLE.',
             'before_future_execution':'Refresh external-result intake for newly completed matching targets. Confirm actual NCP identity and resource limits; use an independent create-only run directory. Do not replay completed pilot27.',
             'excluded_targets':excluded,
             'initial_checks':checks,
             'maximum_initial_axis_absolute_error':max(c['max_axis_absolute_error'] for c in checks),
             'maximum_initial_Hamiltonian_relative_residual':max(c['Hamiltonian_relative_residual'] for c in checks),
             'maximum_initial_energy_normalization_error':max(abs(c['massive_initial_rho_normalized']-1) for c in checks),
             'minimum_continuum_matter_weight':min(c['continuum_min_W_m'] for c in checks),
             'minimum_continuum_radiation_weight':min(c['continuum_min_W_r'] for c in checks),
             'minimum_massive_cell_number':min(c['minimum_massive_cell_number'] for c in checks),
             'state_count':40,'n_saved':101,'rtol':3e-11,'atol':3e-13,
             'global_error_bound':None}
    write(output/filenames[1],receipt)
    print(json.dumps({key:receipt[key] for key in ('status','EXECUTION','DAG','ODE_solves','input_candidates','excluded_current_pilot27_targets','additional_external_exclusions_beyond_current27','ready_new_cases','grid_sha256','maximum_initial_axis_absolute_error','maximum_initial_Hamiltonian_relative_residual','maximum_initial_energy_normalization_error','minimum_continuum_matter_weight','minimum_continuum_radiation_weight','minimum_massive_cell_number')},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    prepare(parser.parse_args().output_dir)
