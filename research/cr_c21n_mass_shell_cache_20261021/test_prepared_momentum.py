"""Focused no-ODE qualification of the new constructor preparation boundary."""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
os.environ.setdefault('MPLCONFIGDIR', '/tmp/c21n_mplconfig')
import argparse
from dataclasses import FrozenInstanceError
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
M = HERE.parent / 'cr_c21m_independent_stress_20261021'
L = HERE.parent / 'cr_c21l_rei_pilot_20261021'
sys.path.insert(0, str(HERE))
import builder as prepared_builder
import prepared_momentum as pm

spec = importlib.util.spec_from_file_location('c21m_frozen_builder_for_prepared_check', M/'builder.py')
old = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = old
spec.loader.exec_module(old)

RESULT = {'schema':'C21N_PREPARED_MOMENTUM_CHECK_V1', 'new_ODE_solves':0,
          'performance_benchmark':False, 'global_error_bound':None,
          'counts':{}, 'source':{}}


def same_float(a, b):
    return np.asarray(a, dtype=np.float64).tobytes() == np.asarray(b, dtype=np.float64).tobytes()


class PreparedChecks(unittest.TestCase):
    def test_original_constructor_and_moment_bytes(self):
        count = 0
        for mass,nr,nm,ng in [(30.,24,12,3),(3.,4,4,2),(1e5,8,6,4)]:
            factory = pm.PreparedMomentumFactory(mass,nr,nm,ng)
            for amplitude in (-1.,-.292571798,0.,.292571798,2.):
                a = factory.make(amplitude)
                b = pm.parent.CanonicalMomentumFV(mass,amplitude,nr,nm,gauss_order=ng)
                for key in ('_q','_mu2','_numbers','_cell_numbers'):
                    aa,bb = getattr(a,key),getattr(b,key)
                    self.assertEqual(aa.shape,bb.shape)
                    self.assertEqual(aa.dtype,bb.dtype)
                    self.assertEqual(aa.tobytes(),bb.tobytes(),(key,mass,amplitude))
                for key in ('reference_energy_norm','total_cell_number'):
                    self.assertTrue(same_float(getattr(a,key),getattr(b,key)),key)
                for eta,beta in [(0.,0.),(.5,-.01),(math.log(21/5),.02)]:
                    self.assertTrue(same_float(list(vars(a.moments(eta,beta)).values()),
                                               list(vars(b.moments(eta,beta)).values())))
                count += 1
        RESULT['counts']['constructor_configurations'] = count
        RESULT['counts']['moment_states'] = count*3

    def test_immutability_and_case_local_distributions(self):
        f = pm.PreparedMomentumFactory()
        a,b = f.make(-.25),f.make(.25)
        self.assertTrue(np.shares_memory(a._q,b._q))
        self.assertTrue(np.shares_memory(a._mu2,b._mu2))
        self.assertFalse(np.shares_memory(a._numbers,b._numbers))
        self.assertFalse(np.shares_memory(a._cell_numbers,b._cell_numbers))
        for arr in list(f._arrays.values())+[a._q,a._mu2,a._numbers,a._cell_numbers]:
            with self.assertRaises(ValueError):
                arr.setflags(write=True)
        with self.assertRaises(FrozenInstanceError):
            f.mass = 40.
        with self.assertRaises(TypeError):
            f._arrays['q'] = np.zeros(3)
        old_shape=f._arrays['q'].shape
        f._arrays['q'].shape=(old_shape[0],1)
        with self.assertRaisesRegex(RuntimeError,'METADATA_CHANGED'):
            f.make(0.)
        f._arrays['q'].shape=old_shape
        f.make(0.)

    def test_source_domains_and_preparation_count(self):
        for kwargs in ({'mass':2.},{'mass':float('nan')},{'radial_cells':3},
                       {'angular_cells':129},{'gauss_order':5}):
            with self.assertRaises(ValueError):
                pm.PreparedMomentumFactory(**kwargs)
        f=pm.PreparedMomentumFactory()
        for value in (-1.0001,2.0001,float('nan'),float('inf')):
            with self.assertRaises(ValueError):
                f.make(value)
        saved=pm.leggauss
        def forbidden(*args,**kwargs):
            raise AssertionError('QUADRATURE_REBUILT_AFTER_PREPARATION')
        pm.leggauss=forbidden
        try:
            for a in (-1.,-.1,0.,.1,2.):
                f.make(a)
        finally:
            pm.leggauss=saved
        RESULT['counts']['repeated_A_trials_without_quadrature_call']=5

    def test_actual125_mapping_fields_rhs_without_integration(self):
        def forbidden(*args,**kwargs):
            raise AssertionError('SCIENCE_ODE_FORBIDDEN_IN_STATIC_CHECK')
        saved = pm.parent.CanonicalFVSpecies.integrate
        pm.parent.CanonicalFVSpecies.integrate = forbidden
        try:
            new = prepared_builder.IndependentStressBuilder()
            original = old.IndependentStressBuilder(optimized=False)
            cases=[]
            for name in ('pilot26','ncp_refinement98_20261021'):
                run=M/'runs'/name
                manifest=json.loads((run/'MANIFEST.json').read_text())
                for case in manifest['manifest']['grid']['cases']:
                    cases.append((tuple(case[k] for k in ('S0','Pm0','Pr0')),
                                  run/'cases'/case['case_id']/'history.npz'))
            cases.append(((0.,0.,0.),L/'runs/pilot81/cases/s04_p04/history.npz'))
            fields_count=rhs_count=0
            for target,path in cases:
                a,ra=new.build(*target)
                b,rb=original.build(*target)
                self.assertEqual(ra,rb,('mapping',target))
                self.assertTrue(same_float(a.initial_state(),b.initial_state()))
                with np.load(path,allow_pickle=False) as history:
                    for index in (0,50,100):
                        eta=float(history['eta'][index]); y=history['Y'][:,index]
                        da,db=a.fields(eta,y),b.fields(eta,y)
                        self.assertEqual(set(da),set(db))
                        for key,v in da.items():
                            if isinstance(v,(float,int,np.floating,np.integer,np.ndarray)):
                                self.assertTrue(same_float(v,db[key]),(target,index,key))
                                fields_count += np.asarray(v).size
                            else:
                                self.assertEqual(v,db[key])
                        self.assertTrue(same_float(a.rhs(eta,y),b.rhs(eta,y)),('rhs',target,index))
                        rhs_count += len(y)
            RESULT['counts'].update(mapping_cases=len(cases), saved_states=3*len(cases),
                                    field_numeric_FP64_values=fields_count, rhs_FP64_values=rhs_count)
            RESULT['source']['prepared_identity']=new.identity()
            RESULT['source']['frozen_builder_sha256']=hashlib.sha256((M/'builder.py').read_bytes()).hexdigest()
        finally:
            pm.parent.CanonicalFVSpecies.integrate=saved


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    if args.output.exists():
        raise FileExistsError('CREATE_ONLY_CHECK_RECEIPT')
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(PreparedChecks)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    RESULT['status']='PASS_SCOPED' if result.wasSuccessful() else 'FAIL'
    RESULT['tests_run']=result.testsRun
    RESULT['failures']=[{'test':str(t),'traceback':s} for t,s in result.failures+result.errors]
    RESULT['source']['test_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as out:
        json.dump(RESULT,out,indent=2,sort_keys=True,allow_nan=False);out.write('\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__=='__main__':
    main()
