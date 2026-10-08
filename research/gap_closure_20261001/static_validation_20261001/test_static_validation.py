"""Offline scientific-contract tests; these do not invoke a physical evaluator."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import numpy as np
import static_validation as sv


class StaticValidationTests(unittest.TestCase):
    def test_central_difference_order_and_wrong_derivative(self):
        v = 2.00798106651023
        z = 1.1
        S = lambda x: np.diag([2 + .1*np.sin(x), 3 + .2*np.cos(x)])
        D = .5*v*np.diag([.1*np.cos(z), -.2*np.sin(z)])
        ladder = [(h, S(z-h), S(z+h)) for h in sv.H_LADDER]
        good = sv.compare_ladder(D, ladder, v, relative_target=1e-3)
        wrong = sv.compare_ladder(1.1*D, ladder, v, relative_target=1e-3)
        self.assertTrue(good['passed'])
        self.assertTrue(all(1.9 < p < 2.1 for p in good['observed_orders']))
        self.assertFalse(wrong['passed'])
        self.assertGreater(wrong['rows'][-1]['spectral_relative'], .08)

    def test_zero_derivative_is_not_fake_order_evidence(self):
        S = np.eye(2)
        out = sv.compare_ladder(np.zeros((2,2)), [(h,S,S) for h in sv.H_LADDER], 2)
        self.assertFalse(out['passed'])
        self.assertEqual(out['status'], 'ORDER_NOT_RESOLVED')

    def test_single_h_rejected_and_velocity_required(self):
        with self.assertRaises(ValueError):
            sv.compare_ladder(np.eye(2),[(.1,np.eye(2),np.eye(2))],2)
        with self.assertRaises(ValueError):
            sv.compare_ladder(np.eye(2),[(h,np.eye(2),np.eye(2)) for h in sv.H_LADDER],-2)

    def test_plan_counts_and_no_authority_inheritance(self):
        plan=sv.make_plan(sv.load_source_plan())
        self.assertEqual(len(plan['queries']),72)
        self.assertEqual(plan['new_query_count'],72)
        self.assertEqual(plan['max_raw_operator_evaluations'],792)
        self.assertFalse(plan['native_authorized'])
        self.assertFalse(plan['temporal_gate_inherited'])
        self.assertEqual(len({r['z_hex'] for r in plan['queries']}),72)
        for q in plan['queries']:
            self.assertEqual(q['time_hex'],float(q['z_a0']/plan['identity']['velocity_au']).hex())

    def test_strict_saved_payload_and_metadata(self):
        plan=sv.make_plan(sv.load_source_plan())
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); q=next(q for q in plan['queries'] if q['z_a0']==16)
            desc=self.write_saved(root,q,plan)
            result=sv.load_saved(root,desc,plan)
            self.assertEqual(result['S'].shape,(18,18))
            bad=copy.deepcopy(desc);bad['identity']['basis_identity']='wrong'
            with self.assertRaises(ValueError):sv.load_saved(root,bad,plan)
            bad=copy.deepcopy(desc);bad['units']['D']='a0'
            with self.assertRaises(ValueError):sv.load_saved(root,bad,plan)
            bad=copy.deepcopy(desc);bad['time_hex']=float(3).hex()
            with self.assertRaises(ValueError):sv.load_saved(root,bad,plan)
            (root/'snapshot.npz').write_bytes(b'bad')
            with self.assertRaises(ValueError):sv.load_saved(root,desc,plan)

    @staticmethod
    def write_saved(root,q,plan):
        np.savez(root/'snapshot.npz',selected__S=np.eye(18),selected__D=np.zeros((18,18)))
        ctx=plan['context_id']
        rec={'schema':'BASS_TP2D_QUALIFIED_RUNTIME_QUERY_V1','context_id':ctx,
             'time_hex':q['time_hex'],'query_id':sv.query_id(ctx,q['time_hex']),
             'payload_sha256':sv.sha(root/'snapshot.npz'),
             'qualification':{'status':'RUNTIME_QUERY_QUALIFIED','lower_resolution':plan['qualification_ladder'][0],
                'selected_resolution':plan['qualification_ladder'][1],
                'max_raw_cross_relative_difference':0},
             'selected_diagnostics':{'S_hermiticity_relative':0,'H_hermiticity_relative':0,'metric_ratio':1}}
        (root/'snapshot.json').write_text(json.dumps(rec))
        return {'z_a0':q['z_a0'],'z_hex':q['z_hex'],'time_hex':q['time_hex'],
             'identity':copy.deepcopy(plan['identity']),'units':copy.deepcopy(sv.UNITS),
             'record':'snapshot.json','payload':'snapshot.npz','record_sha256':sv.sha(root/'snapshot.json')}

    def test_reuse_is_verified_not_metadata_only(self):
        plan=sv.make_plan(sv.load_source_plan())
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);q=next(q for q in plan['queries'] if q['z_a0']==16)
            d=self.write_saved(root,q,plan)
            reuse=sv.verify_manifest(root,{'identity':plan['identity'],'snapshots':[d]},plan)
            p=sv.make_plan(sv.load_source_plan(),reuse)
            self.assertEqual(p['new_query_count'],71)
            self.assertEqual(p['max_raw_operator_evaluations'],781)
            self.assertEqual(p['verified_reuse_count'],1)
            with self.assertRaises(ValueError):
                sv.verify_manifest(root,{'identity':plan['identity'],'snapshots':[d,d]},plan)

    def test_three_level_catches_false_agreement_and_respects_qualification(self):
        # Correlated fixed offset fools any finite difference consistency test.
        c=sv.three_level([np.array([5.01]),np.array([5.0025]),np.array([5.000625])],
                         resolutions=[1,.5,.25],adjacent_tolerance=.01)
        self.assertTrue(c['conditional_richardson_compatible'])
        self.assertFalse(c['rigorous_error_bound'])
        plateau=sv.three_level([np.array([5.]),np.array([5.]),np.array([5.])],
                         resolutions=[1,.5,.25],adjacent_tolerance=1e-9)
        self.assertEqual(plateau['status'],'PLATEAU_OR_EXACTNESS_UNRESOLVED')
        false_pair=sv.three_level([np.array([1.]),np.array([1.+1e-12]),np.array([2.])],
                         resolutions=[1,.5,.25],adjacent_tolerance=1e-9)
        self.assertFalse(false_pair['three_level_consistency'])
        self.assertFalse(false_pair['changes_existing_qualification'])

    def test_nonmonotone_and_ineligible_ladder(self):
        out=sv.three_level([np.array([1.1]),np.array([.975]),np.array([1.00625])],
                    resolutions=[1,.5,.25],adjacent_tolerance=.2)
        self.assertFalse(out['conditional_richardson_compatible'])
        # Project q/subdivision ladder is not a uniform h refinement.
        out=sv.three_level([np.array([1.1]),np.array([1.025]),np.array([1.00625])],
                    resolutions=None,adjacent_tolerance=.2)
        self.assertIsNone(out['observed_order'])


if __name__=='__main__':unittest.main()
