import copy
import math
import pathlib
import sys
import unittest
from unittest.mock import patch
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
import frontier
from frontier import T0, FrontierError, prepare, envelope, horizon_brackets, state_bounds

def toy():
    # Three states, independent exponential heat kernels; the third has zero yield.
    b=np.array([[1.,.4],[0.,1.2],[0.,0.]])
    x=b*np.array([math.exp(-1),math.exp(-.5),1.])[:,None]
    arrays={'energy_eV':np.array([1.,2.,3.]),'q0':np.array([1.,.5,0.]),'q1':np.array([1.,1.,0.]),'q2':np.array([1.,2.,0.]),'b_active':b,'xT':x}
    H=np.array([1.,1.]);mu=np.array([1.,1.6])*T0;m2=np.array([2.,5.6])*T0*T0
    tail=np.array([1.,.5,0.])@x;ex1=T0*(np.array([1.,1.,0.])@x);ex2=2*T0*T0*(np.array([1.,2.,0.])@x)
    scalars={'H0':H,'H1':H*mu,'H2':H*m2,'Htail':tail,'Eex1':ex1,'Eex2':ex2}
    own={'scalars':{k:v.tolist() for k,v in scalars.items()},'selected':{k:float(v.sum()) for k,v in scalars.items()}}
    rows=[]
    for i in range(3):
        s={k:v[i] if i<2 else v.sum() for k,v in scalars.items()};h=s['H0'];mean=s['H1']/h;second=s['H2']/h;q=s['Htail']/h
        R=(s['Eex1']/h-mean)/T0+1;S=1-(s['Eex2']/h-second+2*T0*mean)/(T0*T0)
        rows.append({'H0':h,'mu_s':mean,'m2_s2':second,'p':1-q,'R':R,'S':S,
                     'tail_residual':{'mean_s':s['Eex1']/s['Htail'],'second_s2':s['Eex2']/s['Htail']}})
    return arrays,own,{'birth_columns':rows[:2],'selected':rows[2]}

class FrontierTests(unittest.TestCase):
    def test_three_state_moments_endpoint_and_enclosing_exact_survival(self):
        arrays,own,cached=toy();p=prepare(arrays,own,cached,n=3)
        self.assertEqual(p['zero_q0_states'],1)
        for t in (T0,1.5*T0,2*T0,5*T0,20*T0):
            row=envelope(p,t);exact=(1.4*math.exp(-t/T0)+.6*math.exp(-t/(2*T0)))/2
            self.assertLessEqual(row['intersection'][0],exact+2e-12)
            self.assertGreaterEqual(row['intersection'][1],exact-2e-12)
            self.assertTrue(row['dominance']['pass'])
        row=envelope(p,T0);self.assertEqual(row['intersection'],[1-cached['selected']['p']]*2)
    def test_no_probability_clipping_or_zero_mean_state(self):
        for key,index,value in [('q0',0,-1e-30),('q1',2,1e-30),('q2',0,.1),('q1',0,0),('xT',(0,0),-1e-30),('b_active',(0,0),-1e-30)]:
            arrays,own,cached=toy();arrays[key][index]=value
            with self.assertRaises(FrontierError) as cm:prepare(arrays,own,cached,n=3)
            self.assertEqual(cm.exception.reason,'FRONTIER_MOMENT_NOT_PROBABILITY_COMPATIBLE')
    def test_saved_crosscheck_and_dtype_are_required(self):
        arrays,own,cached=toy();own['selected']['Htail']+=1e-6
        with self.assertRaisesRegex(FrontierError,'CROSSCHECK'):prepare(arrays,own,cached,n=3)
        arrays,own,cached=toy();arrays['q0']=arrays['q0'].astype('float32')
        with self.assertRaisesRegex(FrontierError,'ARRAY_INVALID'):prepare(arrays,own,cached,n=3)
    def test_vectorized_generic_bounds_equal_scalar_oracle(self):
        from moment_bounds import bounds
        a=np.array([1.,2.,3.,4.,.25,7.])*T0
        b=a*a*np.array([1.,2.,3.,1.1,4.,1.])
        for x in (0.,.25*T0,T0,2*T0,3*T0,4*T0,7*T0,20*T0):
            actual=state_bounds(a,b,x)
            expected=np.array([[bounds(float(ai),float(bi),x)[k] for k in ('lower','upper')] for ai,bi in zip(a,b)])
            np.testing.assert_allclose(actual,expected,rtol=2e-12,atol=2e-14)
    def test_refined_horizons_enclose_independent_exponential_quantiles(self):
        arrays,own,cached=toy();p=prepare(arrays,own,cached,n=3)
        for f in (.5,.9,.95,.99,.999):
            row=horizon_brackets(p,f);eps=1-f
            if f<=cached['selected']['p']:
                self.assertEqual(row['status'],'KNOWN_T_ANCHOR_ONLY');continue
            lo=0.;hi=100*T0
            for _ in range(100):
                mid=(lo+hi)/2
                survival=(1.4*math.exp(-mid/T0)+.6*math.exp(-mid/(2*T0)))/2
                if survival>eps:lo=mid
                else:hi=mid
            self.assertLessEqual(row['lower_s'],hi);self.assertGreaterEqual(row['upper_s'],lo)
            self.assertGreater(row['lower_value'],eps);self.assertLessEqual(row['upper_value'],eps)
            for key in ('lower_bisection','upper_bisection'):self.assertLessEqual(row[key]['iterations'],80)
        self.assertEqual(horizon_brackets(p,.1)['status'],'KNOWN_T_ANCHOR_ONLY')
    def test_raw_intersection_order_rejects_even_subtolerance_gap(self):
        arrays,own,cached=toy();p=prepare(arrays,own,cached,n=3);t=4*T0
        upper=envelope(p,t)['intersection'][1];original=frontier._bounds
        def contradictory(x,a,b):
            if x==t:return upper+1e-16,upper
            return original(x,a,b)
        with patch.object(frontier,'_bounds',side_effect=contradictory):
            with self.assertRaisesRegex(FrontierError,'INTERSECTION_INVALID'):envelope(p,t)
if __name__=='__main__':unittest.main()
