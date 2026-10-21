#!/usr/bin/env python3
"""Independent static theory/source verification of C21M; no integration."""
import os
os.environ['PYTHONDONTWRITEBYTECODE']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import sys,json,math,hashlib
from unittest.mock import patch
import numpy as np
ROOT=Path('/workspace/scratch/10765dc22dcf')
TARGET=ROOT/'bass_cr/research/cr_c21m_independent_stress_20261021'
sys.path.insert(0,str(TARGET))
import builder as b
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];rejections=[]
with patch.object(b.parent.CanonicalFVSpecies,'integrate',side_effect=AssertionError('ODE prohibited')):
    builder=b.IndependentStressBuilder()
    for label,targets in [('opposing',(0.,.0004,-.0004)),('matter',(-.031,-.0004,0.)),('radiation',(.023,0.,.0006)),('mixed',(.017,.0005,.0003)),('isotropic',(0.,0.,0.))]:
        obj,r=builder.build(*targets);y=obj.initial_state();d=obj.fields(0.,y);rhs=obj.rhs(0.,y)
        assert obj.rhs.__func__ is b.parent.CanonicalFVSpecies.rhs
        # Class method identity checked statically below because integrate is mocked here.
        p=d['Pi_matter_J_m3']+d['Pi_gamma_J_m3']+d['Pi_nu_J_m3']
        expected_sdot=-3*d['H']*d['s']+(8*math.pi*b.parent.G_SI/b.parent.C_SI**2)*p
        actual_sdot=obj.source.href*d['H']*rhs[2]
        np.testing.assert_allclose(actual_sdot,expected_sdot,rtol=2e-14,atol=1e-48)
        m=obj.momentum
        E=np.hypot(m.mass,m._q)
        den=np.sum(m._numbers*E)
        p2=(3*m._mu2-1)/2
        e2=float(np.sum(m._numbers*E*p2)/den)
        e2err=abs(e2-r['A_m']/5)
        assert e2err<5e-16
        direct_pa=float(np.sum(m._numbers*(m._q**2*m._mu2/E))/den)
        direct_pp=float(np.sum(m._numbers*(m._q**2*(1-m._mu2)/(2*E)))/den)
        pref=obj.source.rhocrit_j_m3*obj.source.omega_m*.1/obj.source.aref**3
        delta_pressure=pref*(direct_pa-direct_pp)
        field_delta=3*d['Pi_matter_J_m3']
        np.testing.assert_allclose(field_delta,delta_pressure,rtol=3e-14,atol=1e-24)
        actual_sigma=np.linalg.norm(np.diag([-d['s'],-d['s'],2*d['s']]))/d['H']
        signed_sigma=np.sign(d['s'])*actual_sigma
        tensor_m=np.diag([-field_delta/3,-field_delta/3,2*field_delta/3])
        sgn=np.sign(field_delta)
        signed_pm=sgn*(8*math.pi*b.parent.G_SI/b.parent.C_SI**4)*np.linalg.norm(tensor_m)/(d['H']/b.parent.C_SI)**2
        rad=d['Pi_gamma_J_m3']+d['Pi_nu_J_m3']
        signed_pr=np.sign(rad)*(8*math.pi*b.parent.G_SI/b.parent.C_SI**4)*np.linalg.norm(np.diag([-rad,-rad,2*rad]))/(d['H']/b.parent.C_SI)**2
        errors=abs(np.array((signed_sigma,signed_pm,signed_pr))-targets)
        assert errors.max()<2e-13
        assert np.all(m._numbers>=0) and np.all(m._cell_numbers>=0)
        assert not m._numbers.flags.writeable
        assert min(1+r['A_m'],1-r['A_m']/2)>=0
        assert abs(r['k_gamma'])<=.5 and r['k_gamma']==r['k_nu']
        rows.append({'label':label,'targets':targets,'A_m':r['A_m'],'k':r['k_gamma'],
            'independent_tensor_axis_errors':errors.tolist(),'source_angular_E2_error':e2err,
            'massive_pressure_difference_error_J_m3':float(field_delta-delta_pressure),
            'signed_shear_equation_error_s_inverse_squared':float(actual_sdot-expected_sdot),
            'original_rhs_method_identity':True,'state_components':len(y)})
    _,zero=builder.build(.031,0.,0.)
    for tag,index in [('lower',0),('upper',1)]:
        obj,r=builder.build(.031,zero['attainable_matter_signed_full'][index],0.)
        assert r['A_m']==(-1.,2.)[index]
    for tag,index in [('lower',0),('upper',1)]:
        obj,r=builder.build(.031,0.,zero['attainable_radiation_signed_full'][index])
        assert r['k_gamma']==(-.5,.5)[index]
    for targets in [(0.,.01,0.),(0.,0.,.01),(math.sqrt(6),0.,0.),(0.,float('inf'),0.)]:
        try:builder.build(*targets)
        except (ValueError,ArithmeticError) as e:rejections.append({'target_repr':repr(targets),'type':type(e).__name__,'message':str(e)})
        else:raise AssertionError('expected domain refusal')

assert builder.template.integrate.__func__ is b.parent.CanonicalFVSpecies.integrate
out={'status':'PASS_SCOPED','reviewer':'independent theory_literature agent; not builder implementer',
     'scope':'source-derived initial map and initial fields/RHS; no ODE or benchmark',
     'new_ODE_integrations':0,'global_error_bound':None,
     'builder_sha256':sha(TARGET/'builder.py'),'test_builder_sha256':sha(TARGET/'test_builder.py'),
     'review_script_sha256':sha(Path(__file__)),'source_commit':b.SOURCE_COMMIT,
     'original_integrator_method_identity':True,'static_cases':rows,
     'domain_checks':{'matter_endpoints_A_minus1_plus2':True,'radiation_endpoints_k_plusminus0p5':True,'rejections':rejections},
     'checks':['massive FD*(1+A P2) weights, cell masses and energy normalization rebuilt for every A',
         'actual source Hbase used for full-Frobenius signed shear map',
         'independent full-tensor SI kappa/(H/c)^2 target reconstruction',
         'original CanonicalFVSpecies RHS and integrator retained',
         'initial shear evolution sign and 8*pi*G/c^2 coupling checked directly',
         'photon/neutrino common k stated, both source sectors separately present',
         'domain checks preserve source radiation cap and massive positivity',
         'isotropic physical zero retains raw quadrature roundoff rather than clamping'],
     'findings':[],
     'claim_limits':['validates initial mapping and original RHS identity, not ODE endpoint accuracy',
         'global_error_bound remains null','canonical quadrature and L8 truncation error unchanged',
         'all existence/domain statements use eta0=b0=0 fixed source family',
         'component scalar outputs reconstruct exact LRS diagonal tensors; triaxial tensors are outside scope'],
     'theory_reference':'theory_intake/THEORY_REVIEW_KO.md',
     'implementation_test_receipt_sha256':sha(TARGET/'checks/builder_checks.json')}
with (TARGET/'INDEPENDENT_BUILDER_REVIEW.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'status':out['status'],'ODE':0,'static_cases':len(rows),'max_axis_error':max(max(r['independent_tensor_axis_errors']) for r in rows),'review':str(TARGET/'INDEPENDENT_BUILDER_REVIEW.json')},indent=2))
