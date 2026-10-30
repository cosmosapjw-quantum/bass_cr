#!/usr/bin/env python3
"""Bounded author tests; NOT distinct-author R06/C09."""
from __future__ import annotations
import csv, hashlib, json, math, tempfile, unittest
from pathlib import Path
import numpy as np
import mpmath as mp
from phys10_energy import *

SOURCE=Path(__file__).resolve().parent/'sources/PR134_ORIGINAL_SOURCE.zip'
RESULTS=Path(__file__).resolve().parent/'results'

def piecewise_probability(ka,kb,s,T,u,v,b,delta,a):
    """Independently enumerate the three constant competing-hazard segments."""
    if T<=s:return 0.
    times=sorted(set([s,T]+([max(s,min(T,u)),max(s,min(T,v))] if v>u else [])))
    survive=1.;p=0.
    for l,r in zip(times,times[1:]):
        if r<=l:continue
        inside=(u<=0.5*(l+r)<v)
        rates=[ka,kb]
        if inside:rates[b]*=math.exp(delta)
        total=sum(rates)
        if total>0:
            event=-math.expm1(-total*(r-l))
            p+=survive*rates[a]/total*event
            survive*=math.exp(-total*(r-l))
    return p

class Phys10Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod,cls.edges,cls.prep,cls.params,cls.dens=load_owner(SOURCE)
        cls.data=json.loads((RESULTS/'RESULT.json').read_text())
    def test_01_source_exact(self):self.assertEqual(sha(SOURCE.read_bytes()),PR134_SOURCE_SHA256)
    def test_02_owner_atom_count(self):self.assertEqual(sum(len(x['energy']) for x in self.prep),6400)
    def test_03_owner_birth_count(self):self.assertEqual(len(self.edges)-1,4)
    def test_04_source_temperature(self):self.assertEqual(self.data['temperature_K'],100)
    def test_05_energies_nonnegative(self):
        for pp in self.prep:
            for a in range(2):self.assertTrue((target_energy(pp,a,self.params)>=0).all())
    def test_06_h_origin_cannot_ionize_He(self):
        pp=self.prep[0]; self.assertEqual(pp['source'],'H')
        self.assertTrue((np.asarray(pp['k'])*np.asarray(pp['frac'])[1]==0).all())
    def test_07_time_rows(self):
        with (RESULTS/'TIME_ENERGY_LEDGER.csv').open() as f:self.assertEqual(len(list(csv.DictReader(f))),27)
    def test_08_channel_rows(self):
        with (RESULTS/'TIME_CHANNEL_ENERGY.csv').open() as f:self.assertEqual(len(list(csv.DictReader(f))),108)
    def test_09_causal_rows(self):
        with (RESULTS/'CAUSAL_ELECTRON_ENERGY.csv').open() as f:self.assertEqual(len(list(csv.DictReader(f))),1728)
    def test_10_spectral_rows(self):
        with (RESULTS/'FINAL_ENERGY_RESPONSE.csv').open() as f:self.assertEqual(len(list(csv.DictReader(f))),368)
    def test_11_earliest_larger_absorption(self):
        E=self.data['final_earliest'];L=self.data['final_latest']
        self.assertGreater(E['total_primary_J_m3'],L['total_primary_J_m3'])
    def test_12_final_energy_budget(self):
        for key in ('final_earliest','final_latest'):
            o=self.data[key];lhs=o['total_absorbed_photon_J_m3'];rhs=o['total_primary_J_m3']+o['total_binding_J_m3']
            self.assertLess(abs(lhs-rhs),1e-55)
    def test_13_ph09_baseline(self):
        p0=per_source(self.prep,self.params,self.edges,self.mod,1e10,'earliest',None,0)
        p1=per_source(self.prep,self.params,self.edges,self.mod,1e10,'earliest',None,1)
        self.assertTrue(math.isclose(p0[0]+p1[0],1.719391366604854e-26,rel_tol=3e-13))
    def test_14_bound_chemical_J(self):
        for x in self.data['final_earliest'],self.data['final_latest']:
            self.assertGreater(x['total_binding_J_m3'],0)
            self.assertGreater(x['total_primary_J_m3'],0)
            self.assertGreater(x['total_absorbed_photon_J_m3'],0)
    def test_15_causal_future_zero(self):
        pp=self.prep[1];ka=pp['k']*pp['frac'][0];kb=pp['k']*pp['frac'][1]
        for a in range(2):
            for b in range(2):
                x=self.mod.log_response(ka,kb,1e8,2e9,4e9,5e9,a,b)
                self.assertTrue(np.all(x==0))
    def test_16_interval_partition(self):
        T=1e10
        for policy in ('earliest','latest'):
            for a in range(2):
                for b in range(2):
                    total=per_source(self.prep,self.params,self.edges,self.mod,T,policy,None,a,b,(0,T))
                    pieces=[per_source(self.prep,self.params,self.edges,self.mod,T,policy,None,a,b,w) for w in WINDOWS]
                    self.assertTrue(math.isclose(total[0],math.fsum(x[0] for x in pieces),rel_tol=1e-12,abs_tol=1e-42))
                    self.assertTrue(math.isclose(total[1],math.fsum(x[1] for x in pieces),rel_tol=1e-12,abs_tol=1e-42))
    def test_17_negative_cross_response(self):
        for policy in ('earliest','latest'):
            for a,b in ((0,1),(1,0)):
                x=per_source(self.prep,self.params,self.edges,self.mod,1e10,policy,None,a,b,(0,1e10))
                self.assertLessEqual(x[0],1e-40)
                self.assertLessEqual(x[1],1e-40)
    def test_18_direct_finite_difference(self):
        # Piecewise hazard probability with independent positive/negative change.
        # Each E atom contributes epsilon_a times the exact first-event response.
        # Binary64 central differences at 1e-4 exhibit O(h^2) truncation;
        # use MP70 small h to separate FD truncation from implementation errors.
        mp.mp.dps=70;h=mp.mpf("1e-6");errors=[]
        for pp in self.prep:
            E=np.asarray(pp['energy']);kH=np.asarray(pp['k'])*np.asarray(pp['frac'])[0];kHe=np.asarray(pp['k'])*np.asarray(pp['frac'])[1]
            for ii in (0,55,100,533,1250,3100):
                for a,b in ((0,0),(0,1),(1,0),(1,1)):
                    s=0.;T=1e10;u=2.5e9;v=5e9
                    an=float(self.mod.log_response(kH[ii:ii+1],kHe[ii:ii+1],s,T,u,v,a,b)[0])
                    def f(eta):
                        rates=[mp.mpf(str(float(kH[ii]))),mp.mpf(str(float(kHe[ii])))]
                        times=[mp.mpf(0),mp.mpf(str(u)),mp.mpf(str(v)),mp.mpf(str(T))]
                        survival=mp.mpf(1);total_p=mp.mpf(0)
                        for j,(lo,hi) in enumerate(zip(times,times[1:])):
                            r=list(rates)
                            if j==1:r[b]*=mp.exp(eta)
                            kt=sum(r);length=hi-lo
                            if kt:
                                total_p+=survival*r[a]/kt*(-mp.expm1(-kt*length))
                                survival*=mp.exp(-kt*length)
                        return total_p
                    fd=float((f(h)-f(-h))/(2*h))
                    errors.append(abs(fd-an)/max(abs(an),1e-20))
                    epsilon=float(target_energy(pp,a,self.params)[ii]);self.assertLess(abs((fd-an)*epsilon),1e-11)
        self.assertLess(max(errors),1e-6)
    def test_19_reproduce_byte(self):
        expected=json.loads((Path(__file__).resolve().parent/'EXPECTED_OUTPUT_SHA256.json').read_text())
        for name,digest in expected.items():
            self.assertEqual(sha((RESULTS/name).read_bytes()),digest,name)
    def test_20_guard_source_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            tamper=Path(d)/'bad.zip';tamper.write_bytes(SOURCE.read_bytes()[:1000])
            with self.assertRaisesRegex(ValueError,'SOURCE_SHA256_MISMATCH'):load_owner(tamper)

if __name__=='__main__':unittest.main()
