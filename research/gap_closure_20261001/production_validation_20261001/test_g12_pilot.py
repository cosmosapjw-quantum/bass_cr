import copy
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from scipy.linalg import expm
import g12_pilot as g


class AnalyticMovingMetric:
    """Known unitary lab trajectory in a changing nonorthogonal basis."""
    sx=np.array([[0,1],[1,0]],complex)
    sz=np.diag([1.,-1.]).astype(complex)

    def __init__(self,grid):
        self.allowed=set(grid['times_hex']);self.calls=[]

    def parts(self,t):
        R=np.array([[np.exp(.12*np.sin(t)),.2*np.sin(.7*t)+.1j*np.cos(.9*t)],
                    [0.,np.exp(-.1*np.cos(.5*t))]],complex)
        Rd=np.array([[.12*np.cos(t)*R[0,0],.14*np.cos(.7*t)-.09j*np.sin(.9*t)],
                     [0.,.05*np.sin(.5*t)*R[1,1]]],complex)
        phi=.3*t+.11*np.sin(1.4*t);phid=.3+.154*np.cos(1.4*t)
        theta=.5*t+.07*np.sin(.9*t);thetad=.5+.063*np.cos(.9*t)
        Z=expm(-1j*phi*self.sz);U=Z@expm(-1j*theta*self.sx)
        H=phid*self.sz+thetad*Z@self.sx@Z.conj().T
        return R,Rd,U,H

    def at(self,t):
        th=float(t).hex()
        if th not in self.allowed:
            raise KeyError('exact toy cache miss: '+th)
        self.calls.append(th);R,Rd,U,H=self.parts(t)
        return SimpleNamespace(S=R.conj().T@R,H=R.conj().T@H@R,D=R.conj().T@Rd)

    def exact(self,t):
        R,Rd,U,H=self.parts(t)
        v=np.array([1.,.3j],complex);v/=np.linalg.norm(v)
        return np.linalg.solve(R,U@v)


class G12PilotTests(unittest.TestCase):
    def test_physical_stage_union_has_eighteen_exact_times(self):
        v=g.projectile_speed_au(100);grid=g.stage_grid(32/v,32.02/v)
        self.assertEqual(len(grid['times_hex']),18)
        self.assertEqual(len(grid['dop853_rhs_time_hex']),13)
        self.assertEqual(len(set(grid['dop853_rhs_time_hex'])),12)
        self.assertEqual(grid['times_hex'][0],'0x1.fdf70821d530fp+3')
        self.assertEqual(grid['times_hex'][-1],'0x1.fe48a04c180b7p+3')
        self.assertEqual(g.dependency_identity()['scipy'],'1.17.0')
        self.assertEqual(len(g.dependency_identity()['scipy_source_files']),4)

    def test_direct_dop853_matches_known_solution_with_moving_nonorthogonal_metric(self):
        grid=g.stage_grid(0.,.04);provider=AnalyticMovingMetric(grid)
        raw=2*provider.exact(0.)
        result,states=g.compare_methods(provider,raw,grid,[0])
        exact=provider.exact(.04);S=provider.at(.04).S
        self.assertLess(g._distance(states['dop853_final'],exact,S),2e-13)
        errors=[g._distance(states['midpoint_'+str(n)+'_final'],exact,S) for n in (1,2,4)]
        self.assertGreater(errors[0]/errors[1],3.8)
        self.assertGreater(errors[1]/errors[2],3.8)
        self.assertLess(result['dop853']['endpoint_norm_drift'],2e-13)
        self.assertEqual(result['dop853']['nfev'],13)
        self.assertAlmostEqual(result['initial_value']['raw_metric_norm'],4.,places=13)
        self.assertEqual(result['initial_value']['normalizations'],1)
        self.assertEqual(result['dop853']['actual_initial_state'],result['initial_value']['common_initial_state'])
        self.assertFalse(result['physical_G12_closed'])
        self.assertFalse(result['physical_G02_closed'])
        self.assertFalse(result['capture'])
        self.assertEqual(result['production_admission'],'HOLD')
        self.assertEqual(result['new_native_operator_calls'],0)

    def test_missing_exact_stage_fails_without_interpolation_or_native_fallback(self):
        grid=g.stage_grid(0.,.04);provider=AnalyticMovingMetric(grid)
        missing=grid['dop853_rhs_time_hex'][2]
        provider.allowed.remove(missing)
        with self.assertRaisesRegex(KeyError,'exact toy cache miss'):
            g.compare_methods(provider,provider.exact(0.),grid,[0])
        self.assertNotIn(missing,provider.calls)

    def test_rejected_dop853_step_is_stopped_at_first_unplanned_query(self):
        grid=g.stage_grid(0.,1.)
        class FastConstant:
            def at(self,t):
                return SimpleNamespace(S=np.eye(2,dtype=complex),
                    H=np.diag([100.,-100.]).astype(complex),D=np.zeros((2,2),complex))
        with self.assertRaisesRegex(KeyError,'unplanned DOP853 RHS stage/rejection'):
            g.compare_methods(FastConstant(),np.array([1.,1.],complex),grid,[0])

    def test_grid_tampering_and_invalid_initial_conditions_fail(self):
        grid=g.stage_grid(0.,.04);provider=AnalyticMovingMetric(grid)
        bad=copy.deepcopy(grid);bad['dop853_rhs_time_hex'][2]=(0.001).hex()
        with self.assertRaisesRegex(ValueError,'stage grid mismatch'):
            g.compare_methods(provider,provider.exact(0.),bad,[0])
        with self.assertRaises(ArithmeticError):
            g.compare_methods(provider,np.zeros(2,complex),grid,[0])
        with self.assertRaises(ValueError):
            g.compare_methods(provider,np.array([1.,complex('nan')]),grid,[0])

    def test_plan_mutation_rejected_before_cache_read(self):
        with tempfile.TemporaryDirectory() as d:
            plan={'inputs':d,'build':d,'context':{'backend':'fortran','threads':2},'marker':1}
            with patch.object(g,'make_plan',return_value={**plan,'marker':2}):
                with self.assertRaisesRegex(ValueError,'identity changed'):
                    g.ExactUnionCache([d],plan)

    def test_duplicate_source_pair_and_incomplete_cache_fail(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);a=root/'a';b=root/'b';a.mkdir();b.mkdir()
            th=0.0.hex();ctx='x'*64;qid=g.query_id(ctx,th)
            plan={'context':{'context_id':ctx,'qualification_contract':{}},
                  'grid':{'times_hex':[th]},'plan_sha256':'p'}
            with patch.object(g,'validate_plan',return_value=plan):
                with self.assertRaisesRegex(ValueError,'exactly one complete'):
                    g.ExactUnionCache([a,b],plan)
                (a/(qid+'.json')).write_text('{}')
                (b/(qid+'.json')).write_text('{}')
                with self.assertRaisesRegex(ValueError,'exactly one complete'):
                    g.ExactUnionCache([a,b],plan)

    def test_real_qualification_pair_is_admitted_and_later_byte_change_rejected(self):
        contract={'runtime_reference_resolutions':[{'order':4,'subdivisions':1},
                  {'order':8,'subdivisions':1}], 'screens':{'raw_cross_relative_max':1e-9,
                  'operator_hermiticity_relative_max':1e-12,'metric_min_ratio':1e-8}}
        def evaluate(t,q,h):
            raw={key:np.zeros((9,9),complex) for key in
                 ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')}
            full={'S':np.eye(18,dtype=complex),'H':np.eye(18,dtype=complex),
                  'D':np.zeros((18,18),complex),'metadata':{'scope':'SYNTHETIC'}}
            return raw,full
        with tempfile.TemporaryDirectory() as d:
            task=g.hp.build_tasks('synthetic-context',[0.],contract)[0]
            def reserve(i):
                return i+1
            reserve.task_dir=d
            g.hp.qualified_task(task,reserve,evaluate,'synthetic-context',contract)
            plan={'context':{'context_id':'synthetic-context','qualification_contract':contract},
                  'grid':{'times_hex':[0.0.hex()]},'plan_sha256':'synthetic'}
            directory=Path(d)/'runtime_queries'
            with patch.object(g,'validate_plan',return_value=plan):
                cache=g.ExactUnionCache([directory],plan)
                np.testing.assert_array_equal(cache.at(0.).S,np.eye(18))
                self.assertEqual(cache.native_calls,0)
                with self.assertRaisesRegex(KeyError,'exact cache miss'):
                    cache.at(np.nextafter(0.,1.))
                payload=directory/(task['query_id']+'.npz')
                with payload.open('ab') as stream:
                    stream.write(b'changed')
                with self.assertRaisesRegex(ValueError,'changed after admission'):
                    cache.at(0.)


if __name__=='__main__':
    unittest.main()
