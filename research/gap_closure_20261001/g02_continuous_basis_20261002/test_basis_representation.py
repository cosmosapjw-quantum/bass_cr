"""Targeted mathematical and fail-closed representation tests; no physics calls."""
import dataclasses
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
import basis_representation as br

class ContinuousBasisTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.edges=np.array([0.,1.,2.])
        self.coef=np.array([[[0.,1.,2.,-3.,1.],[1.+2**-48,-1.,0.,0.,0.]]])
        self.npz=self.root/'BASIS.npz';self.js=self.root/'BASIS.json'
        np.savez(self.npz,edges=self.edges,coefficients=self.coef)
        self.meta={'schema':'BASS_TP2A_BASIS_V1','matrix_sha256':br.sha256(self.npz),'modes':[{'l':0,'principal_n':1,'energy':-.5,'identity':'a'*64,'residual':1e-14}]}
        self.meta['identity']=br.digest(self.meta);self.js.write_text(json.dumps(self.meta))
        self.out=self.root/'candidate'
        br.build_candidate(self.npz,self.js,self.out,br.sha256(self.npz),br.sha256(self.js))
        self.mode=br.load_candidate(self.out)[0]

    def tearDown(self):self.temp.cleanup()

    def test_exact_continuity_and_zero_traces(self):
        rows=br.exact_coefficients(self.mode)
        self.assertEqual(rows[0][0],0);self.assertEqual(sum(rows[0]),rows[1][0]);self.assertEqual(sum(rows[-1]),0)
        u,du=self.mode.evaluate(self.edges)
        np.testing.assert_array_equal(u,self.mode.shared_endpoint_values)
        self.assertEqual(du[-1],0)

    def test_exact_original_high_terms_and_small_bubble_rounding(self):
        rows=br.exact_coefficients(self.mode)
        # Integer coefficients in this fixture incur exactly zero bubble rounding.
        for row,c in zip(rows,self.coef[0]):
            self.assertEqual(row[2:],list(map(Fraction.from_float,map(float,c[2:]))))
        self.assertNotEqual(sum(map(Fraction.from_float,map(float,self.coef[0,0]))),rows[1][0])

    def test_evaluation_against_exact_rational_reference(self):
        points=np.array([[0.,.125,.25,.375],[.5,.75,1.,1.75]])
        actual,der=self.mode.evaluate(points)
        ref=[];refder=[];rows=br.exact_coefficients(self.mode)
        for r in points.ravel():
            e=min(int(r),1);s=Fraction.from_float(float(r-e));c=rows[e]
            ref.append(float(sum(v*s**j for j,v in enumerate(c))))
            refder.append(float(sum(j*c[j]*s**(j-1) for j in range(1,5))))
        np.testing.assert_allclose(actual.ravel(),ref,rtol=0,atol=5e-16)
        np.testing.assert_allclose(der.ravel(),refder,rtol=0,atol=5e-16)
        self.assertEqual(self.mode.evaluate(.125)[0].shape,())
        self.assertEqual(self.mode.evaluate(np.array([]))[0].size,0)

    def test_reconstructed_nodes_are_candidate_samples(self):
        self.assertEqual(self.mode.reconstructed_nodal_values.shape,(9,))
        np.testing.assert_array_equal(self.mode.reconstructed_nodal_values[::4],self.mode.shared_endpoint_values)
        self.assertFalse(hasattr(self.mode,'polynomial_coefficients'))
        self.assertEqual(br.validate_continuous_radial(self.mode),self.mode.identity)

    def test_invalid_radii_fail_closed(self):
        for bad in ([-1.],[np.nan],[np.inf],[1+2j],['1'],[True]):
            with self.subTest(bad=bad),self.assertRaises(ValueError):self.mode.evaluate(bad)
        np.testing.assert_array_equal(self.mode.evaluate([2.,3.])[0],[0.,0.])

    def test_invalid_shapes_endpoints_or_identity_fail_closed(self):
        for changes in ({'edges':np.array([0.,0.,2.])},{'bubble_coefficients':np.ones((2,2))},{'shared_endpoint_values':np.array([1.,1.,0.])},{'identity':'b'*64},{'threads':True}):
            with self.subTest(changes=list(changes)),self.assertRaises(ValueError):dataclasses.replace(self.mode,**changes)

    def test_input_sha_and_metadata_rebinding_fail_closed(self):
        with self.assertRaises(ValueError):br.build_candidate(self.npz,self.js,self.root/'wrong','0'*64,br.sha256(self.js))
        self.meta['modes'][0]['energy']=-.6;self.js.write_text(json.dumps(self.meta))
        with self.assertRaises(ValueError):br.validate_original(self.npz,self.js,br.sha256(self.npz),br.sha256(self.js))

    def test_candidate_tampering_and_create_only(self):
        with self.assertRaises(FileExistsError):br.build_candidate(self.npz,self.js,self.out,br.sha256(self.npz),br.sha256(self.js))
        p=self.out/'CANDIDATE.npz';p.write_bytes(p.read_bytes()+b'corrupt')
        with self.assertRaises(ValueError):br.load_candidate(self.out)

    def test_mutated_array_payload_is_rejected_by_fingerprint(self):
        self.mode.bubble_coefficients.setflags(write=True);self.mode.bubble_coefficients[0,0]+=1
        with self.assertRaises(ValueError):br.validate_continuous_radial(self.mode)

    def test_native_requires_exact_manifest_and_thread_bound(self):
        with self.assertRaises(ValueError):br.load_candidate(self.out,backend='fortran')
        with self.assertRaises(ValueError):dataclasses.replace(self.mode,threads=65)

if __name__=='__main__':unittest.main()
