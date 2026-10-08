from pathlib import Path
import os,unittest,json,shutil,tempfile
import numpy as np
from kernel import HPCMomentKernel
from synthetic_inputs import inputs
class KernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory=os.environ.get('BASS_HPC_BUILD')
        if not cls.directory:raise RuntimeError('BASS_HPC_BUILD is required; missing native validation is not a skip/PASS')
        cls.ref=HPCMomentKernel(cls.directory,backend='reference');cls.f90=HPCMomentKernel(cls.directory)
    def same(self,args):
        a=self.ref.accumulate(*args,real_coefficients=True);b=self.f90.accumulate(*args,real_coefficients=True)
        # Initial strict-FP acceptance is bitwise identity, including cancellation.
        np.testing.assert_array_equal(a.view(np.uint64),b.view(np.uint64))
        return b
    def test_static_moving_and_tail_tiles(self):
        for n,nt,np_ in [(1,1,1),(17,3,5),(1024,9,9),(33,11,7)]:
            for moving in [False,True]:
                with self.subTest(n=n,nt=nt,np=np_,moving=moving):self.same(inputs(n,nt,np_,moving=moving))
    def test_thread_invariance(self):
        a=inputs(53,9,9,moving=True);expected=self.same(a)
        for t in [2,4]:
            got=HPCMomentKernel(self.directory,threads=t).accumulate(*a,real_coefficients=True)
            np.testing.assert_array_equal(expected.view(np.uint64),got.view(np.uint64))
        self.f90.accumulate(*a,real_coefficients=True)
        self.assertEqual(self.f90.lib.omp_get_max_threads(),1)
    def test_incomplete_library_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ['BUILD_HPC.json','libreference.so','libmoments_f90.so']:shutil.copy2(Path(self.directory)/name,Path(tmp)/name)
            p=Path(tmp)/'BUILD_HPC.json';rec=json.loads(p.read_text());rec['libraries']={};p.write_text(json.dumps(rec))
            with self.assertRaisesRegex(ValueError,'complete exact library'):HPCMomentKernel(tmp)
    def test_nonzero_accumulator(self):
        a=inputs(19,3,5,moving=True);data=[np.ascontiguousarray(x) for x in a[:8]];rng=np.random.default_rng(912)
        initial=rng.normal(size=(4,3,5))+1j*rng.normal(size=(4,3,5));out=[]
        for fn in [self.ref.real_ref,self.f90.real_f90]:
            b=initial.copy();rc=fn(19,3,5,*(x.ctypes.data_as(self.f90.ptr) for x in data),a[8],*a[9],b.ctypes.data_as(self.f90.ptr));self.assertEqual(rc,0);out.append(b)
        np.testing.assert_array_equal(out[0].view(np.uint64),out[1].view(np.uint64))
    def test_independent_constant_s_orbital_limit(self):
        a=inputs(3,2,3);a[0][:]=[2.,4.,1.,1.];a[1][:,:,0]=1.;a[1][:,:,1]=0.;a[2][:,:,0]=1.;a[2][:,:,1]=0.;a[3][:]=0.;a[4][:]=0.;a[3][:,0]=1.;a[4][:,0]=1.;a[5][:]=0.;a[6][:]=0.;a[6][:,0]=1.;a[7][:]=1.
        b=self.same(a);np.testing.assert_array_equal(b[0],3.);np.testing.assert_array_equal(b[1],-2.25);np.testing.assert_array_equal(b[2:],0.)
    def test_complex_fallback_and_rejection(self):
        a=inputs(11,2,3,complex_coefficients=True)
        np.testing.assert_array_equal(self.ref.accumulate(*a),self.f90.accumulate(*a))
        with self.assertRaises(ValueError):self.f90.accumulate(*a,real_coefficients=True)
    def test_bad_inputs_rejected(self):
        a=inputs(5,2,2);a[0][0,0]=np.nan
        with self.assertRaises(ValueError):self.f90.accumulate(*a,real_coefficients=True)
        a=inputs(5,2,2);a[9]=(1.,)
        with self.assertRaises(ValueError):self.f90.accumulate(*a,real_coefficients=True)
        self.assertEqual(self.f90.real_f90(0,1,1,*([None]*8),1.,1.,1.,None),1)
if __name__=='__main__':unittest.main()
