#!/usr/bin/env python3
"""Physical source-contract tests; no distinct-author R6/C9 implied."""
from __future__ import annotations
import csv, math, unittest
import numpy as np
from pathlib import Path
import neutral_response as Q

class SourceResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ed,cls.prep,cls.params,cls.dens,cls.prev=Q.original_source()
    def test_01_source_and_counts(self):
        self.assertEqual(sum(len(p['energy']) for p in self.prep),6400)
        self.assertEqual(len(self.ed),5)
        self.assertEqual(self.dens['HI'],138.6)
        self.assertTrue(all(np.all(p['weights']>=0) for p in self.prep))
    def test_02_causality_prebirth(self):
        z=Q.log_response(np.array([.5]),np.array([.3]),3.,2.,0.,1.,0,0)
        self.assertEqual(z.item(),0.)
    def test_03_causality_future_window(self):
        z=Q.log_response(np.array([.5]),np.array([.3]),0.,3.,4.,5.,0,0)
        self.assertEqual(z.item(),0.)
    def test_04_positive_own_negative_competition(self):
        pp=self.prep[1];i=np.array([0,100,700,3199]);a=pp['k'][i]*pp['frac'][0,i];b=pp['k'][i]*pp['frac'][1,i]
        for t in (0,1):
            self.assertTrue(np.all(Q.log_response(a,b,0.,1e10,1e9,3e9,t,t)>=-1e-14))
            self.assertTrue(np.all(Q.log_response(a,b,0.,1e10,1e9,3e9,t,1-t)<=1e-14))
    def test_05_target_sum_exponential(self):
        pp=self.prep[1];i=np.array([12,510,1800,3050]);a=pp['k'][i]*pp['frac'][0,i];b=pp['k'][i]*pp['frac'][1,i]
        s,T,u,v=0.,1e10,2.5e9,3.75e9
        for par in (0,1):
            lhs=sum(Q.log_response(a,b,s,T,u,v,t,par) for t in (0,1))
            rhs=(a,b)[par]*(v-u)*np.exp(-(a+b)*(T-s))
            self.assertTrue(np.allclose(lhs,rhs,rtol=2e-12,atol=1e-16))
    def test_06_h_origin_no_HeI_channel(self):
        pp=self.prep[0]
        self.assertTrue(np.all(pp['frac'][1]==0))
        self.assertEqual(Q.integrated_response(self.prep,self.ed,1e10,'earliest','H',1,0,(0,1e10)),0.)
        self.assertEqual(Q.integrated_response(self.prep,self.ed,1e10,'earliest','H',1,1,(0,1e10)),0.)
    def test_07_uniform_window_sum(self):
        pp=self.prep[1];i=np.array([7,411,2071,3199]);a=pp['k'][i]*pp['frac'][0,i];b=pp['k'][i]*pp['frac'][1,i]
        for source_time in (0.,2.5e9,5e9):
            for t in (0,1):
                for par in (0,1):
                    segments=sum((Q.log_response(a,b,source_time,1e10,*window,t,par) for window in Q.WINDOWS))
                    uniform=Q.uniform_log_response(a,b,1e10-source_time,t,par)
                    self.assertTrue(np.allclose(segments,uniform,rtol=2e-12,atol=3e-16))
    def test_08_finite_log_density_difference(self):
        pp=self.prep[1];i=np.array([15,130,800,2050]);a=pp['k'][i]*pp['frac'][0,i];b=pp['k'][i]*pp['frac'][1,i]
        h=1e-4
        for t in (0,1):
            for par in (0,1):
                p=(Q.first_probability(a*np.exp(h),b,1e10,t) if par==0 else Q.first_probability(a,b*np.exp(h),1e10,t))
                m=(Q.first_probability(a*np.exp(-h),b,1e10,t) if par==0 else Q.first_probability(a,b*np.exp(-h),1e10,t))
                num=(p-m)/(2*h)
                analytic=Q.uniform_log_response(a,b,1e10,t,par)
                self.assertTrue(np.allclose(num,analytic,rtol=8e-7,atol=2e-12))
    def test_09_zero_opacity(self):
        a=np.zeros(4);b=np.zeros(4)
        self.assertTrue(np.all(Q.log_response(a,b,0.,10.,2.,4.,0,0)==0))
        self.assertTrue(np.all(Q.first_probability(a,b,10.,0)==0))
    def test_10_invalid_input_rejected(self):
        with self.assertRaises(ValueError): Q.log_response(np.array([-1.]),np.array([0.]),0.,5.,1.,3.,0,0)
        with self.assertRaises(ValueError): Q.log_response(np.array([1.]),np.array([0.]),0.,5.,3.,1.,0,0)
    def test_11_cross_symmetry(self):
        pp=self.prep[1];a=pp['k']*pp['frac'][0];b=pp['k']*pp['frac'][1]
        x=Q.log_response(a,b,0,1e10,2e9,3e9,0,1)
        y=Q.log_response(a,b,0,1e10,2e9,3e9,1,0)
        self.assertTrue(np.allclose(x,y,rtol=3e-13,atol=1e-17))
    def test_12_original_source_endpoints(self):
        e=Q.baseline_by_target(self.prep,self.ed,1e10,'earliest',target=0)+Q.baseline_by_target(self.prep,self.ed,1e10,'earliest',target=1)
        l=Q.baseline_by_target(self.prep,self.ed,1e10,'latest',target=0)+Q.baseline_by_target(self.prep,self.ed,1e10,'latest',target=1)
        self.assertTrue(math.isclose(e,1.719391366604854e-26,rel_tol=3e-14))
        self.assertTrue(math.isclose(l,6.536559924836172e-27,rel_tol=3e-14))
    def test_13_time_grid(self):
        self.assertEqual(len(Q.TIMES),9)
        self.assertEqual(len(Q.WINDOWS),8)
        self.assertEqual(Q.WINDOWS[0],(0,1.25e9))
    def test_14_inherited_dag(self):
        self.assertEqual(self.prev['central_dag']['completed'],28)
        self.assertEqual(self.prev['extension_dag']['completed'],0)
    def test_15_source_integrated_cross_sign(self):
        a=Q.integrated_response(self.prep,self.ed,1e10,'earliest',None,0,1,(0,1e10))
        self.assertLess(a,0)
        b=Q.integrated_response(self.prep,self.ed,1e10,'earliest',None,1,0,(0,1e10))
        self.assertTrue(math.isclose(a,b,rel_tol=1e-11))

if __name__=='__main__':unittest.main()
