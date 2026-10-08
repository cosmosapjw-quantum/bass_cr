import numpy as np
import pytest
from bass_foundations.radial_basis import RadialSpec,atomic_bank
from bass_foundations.two_center import Trajectory,symmetric_channels
from cr_repro.observables import projectile_speed_au
import integration_runtime as ir


def _fixture():
    bank=atomic_bank(RadialSpec(radius=64,elements=4,degree=4,lmax=1,bound_nmax=1,positive_per_l=0,positive_emax=2,quad_order=8,grading=2))
    v=projectile_speed_au(100.)
    tr=Trajectory(((0.,0.,0.),(2.,0.,0.)),((0.,0.,0.),(0.,0.,v)))
    return bank,tr,symmetric_channels(bank)


def test_candidate_reference_alias_only_when_effective_numerical_request_is_identical():
    bank,tr,_=_fixture();ctx={'basis':'x','engine':'analytic'}
    # z=0 has zero longitudinal component, so phase budget does not add edges.
    ref=ir.role_request('reference',0.,0.,56,2,tr,bank[0].edges,ctx,phase_budget=24.)
    cand=ir.role_request('candidate',0.,0.,56,2,tr,bank[0].edges,ctx,phase_budget=24.)
    assert ref['numerical_task_id']==cand['numerical_task_id']
    # away from closest approach, candidate phase-panel edges differ from reference.
    ref2=ir.role_request('reference',-2.,0.,56,2,tr,bank[0].edges,ctx,phase_budget=24.)
    cand2=ir.role_request('candidate',-2.,0.,56,2,tr,bank[0].edges,ctx,phase_budget=24.)
    assert ref2['numerical_task_id']!=cand2['numerical_task_id']


def test_numerical_identity_binds_sector_order_time_mesh_and_engine():
    bank,tr,_=_fixture();ctx={'basis':'x','engine':'analytic'}
    a=ir.role_request('reference',0.,0.,56,2,tr,bank[0].edges,ctx,phase_budget=24.,sector='full')
    variants=[
      ir.role_request('reference',0.,0.,64,2,tr,bank[0].edges,ctx,phase_budget=24.,sector='full'),
      ir.role_request('reference',0.,1e-4,56,2,tr,bank[0].edges,ctx,phase_budget=24.,sector='full'),
      ir.role_request('reference',0.,0.,56,4,tr,bank[0].edges,ctx,phase_budget=24.,sector='full'),
      ir.role_request('reference',0.,0.,56,2,tr,bank[0].edges,{**ctx,'engine':'other'},phase_budget=24.,sector='full'),
      ir.role_request('reference',0.,0.,56,2,tr,bank[0].edges,ctx,phase_budget=24.,sector='even'),
    ]
    assert all(v['numerical_task_id']!=a['numerical_task_id'] for v in variants)


def test_role_row_preserves_alias_provenance_without_calling_it_independent():
    arrays={k:np.eye(2,dtype=complex) for k in ('S','H','D')}
    arrays.update({k:np.ones((1,1),complex) for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')})
    receipt={'numerical_task_id':'abc','diagnostics':{'S_hermiticity_relative':0.,'H_hermiticity_relative':0.,'metric_ratio':1.},'metadata':{}}
    role={'family':'candidate','method':'candidate','candidate_order':56,'reference_order':None,'integration_subdivisions':2,'z_center_a0':0.,'dz_a0':0.,'numerical_task_id':'abc'}
    row=ir.role_row(role,receipt,arrays,aliased=True)
    assert row['numerical_task_id']=='abc'
    assert row['alias_reuse'] is True
    assert row['evidence_relation']=='ALIASED_SAME_NUMERICAL_TASK_NOT_INDEPENDENT_CROSSCHECK'
