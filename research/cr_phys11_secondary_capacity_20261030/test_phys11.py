import csv
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
import numpy as np
from phys11_capacity import (load_source,physical_capabilities,ORIGINAL_PARENT_SHA256,
                            EV_J,TARGETS,TIMES,WINDOWS)

HERE=Path(__file__).resolve().parent
PARENT=HERE/'sources/PR135_ORIGINAL_SOURCE.zip'
OUTPUT=HERE/'results'


def rows(name):
    with (OUTPUT/name).open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))


def piecewise_probability(ka,khe,s,T,u,v,a,b,lam=0.):
    """Adversarial implementation: integrate survival over piecewise constant hazards.

    No PHYS09 log_response call, source original hazard input only.
    """
    if s>=T:return 0.
    bounds=sorted(set([float(s),float(T)]+[float(x) for x in [u,v] if s<x<T]))
    S=1.;result=0.
    for left,right in zip(bounds[:-1],bounds[1:]):
        mid=(left+right)*0.5
        x=math.exp(lam) if u<=mid<v else 1.
        kh=ka*(x if b==0 else 1.)
        ke=khe*(x if b==1 else 1.)
        kk=kh+ke
        if kk>0:
            delta=right-left
            result+=S*([kh,ke][a]/kk)*(-math.expm1(-kk*delta))
            S*=math.exp(-kk*delta)
    return result

class TestSourceKinematics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod,cls.edges,cls.prep,cls.params,cls.dens=load_source(PARENT)
    def test_original_byte_source(self):
        self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),ORIGINAL_PARENT_SHA256)
    def test_source_number_and_energy(self):
        self.assertEqual(sum(len(x['energy']) for x in self.prep),6400)
        self.assertEqual([x['source'] for x in self.prep],['H','He'])
        self.assertAlmostEqual(self.prep[0]['energy'].max(),23.6)
        self.assertAlmostEqual(self.prep[1]['energy'].max(),34.59)
    def test_he_double_zero_both_single_photon_and_primary_secondary(self):
        emin=float(self.params['HI'][0]); ehe=float(self.params['HeI'][0])
        self.assertLess(34.59-emin,ehe)
        self.assertLess(34.59,ehe+54.4177655282)
        self.assertLess(34.59-emin,2*emin)
    def test_eligible_class_single_unique(self):
        ih=float(self.params['HI'][0]); ihe=float(self.params['HeI'][0]); active=[]
        for pp in self.prep:
            for a in (0,1):
                eps,h,he,two=physical_capabilities(pp['energy'],self.params[TARGETS[a]][0],ih,ihe)
                self.assertFalse(he.any());self.assertFalse(two.any())
                n=int(h.sum())
                if n:active.append((pp['source'],TARGETS[a],n))
        self.assertEqual(active,[('He','HI',2389)])
    def test_no_invalid_support_in_source_rows(self):
        a=rows('SUPPORT_PER_SOURCE_ATOM.csv')
        self.assertEqual(len(a),12800)
        self.assertTrue(all(q['He_secondary_kinematically_eligible']=='0' and
                            q['two_additional_H_kinematically_eligible']=='0' and
                            q['direct_He_double_photon_eligible']=='0' for q in a))
        eligible=[q for q in a if q['H_secondary_kinematically_eligible']=='1']
        self.assertEqual(len(eligible),2389)
        self.assertTrue(all(q['source']=='He' and q['first_absorber']=='HI' and
                            float(q['photon_E_eV'])>=27.2 for q in eligible))
    def test_original_source_tamper_negative(self):
        data=bytearray(PARENT.read_bytes());data[-150]^=1
        with tempfile.TemporaryDirectory() as td:
            q=Path(td)/'bad.zip';q.write_bytes(bytes(data))
            with self.assertRaisesRegex(ValueError,'SHA256_MISMATCH'):
                load_source(q)
    def test_zero_first_event_at_T_zero(self):
        a=rows('TIME_CHANNEL_CAPACITY.csv')
        for x in a:
            if float(x['observation_s'])==0:
                self.assertEqual(float(x['H_secondary_upper_events_m3']),0.)
    def test_capacity_subordinate_and_exclusive(self):
        for x in rows('TIME_CHANNEL_CAPACITY.csv'):
            n=float(x['n_first_m3']);c=float(x['H_secondary_upper_events_m3'])
            self.assertGreaterEqual(n,0);self.assertGreaterEqual(c,0)
            self.assertLessEqual(c,n+1e-70)
            if (x['source'],x['first_absorber'])!=('He','HI'):
                self.assertEqual(c,0.)
    def test_causal_response_off_support(self):
        a=rows('CAUSAL_H_SECONDARY_CAPACITY.csv')
        self.assertEqual(len(a),1728)
        for x in a:
            if (x['source'],x['first_absorber'])!=('He','HI'):
                self.assertEqual(float(x['d_H_capacity_dln_neutral_m3']),0.)
    def test_energy_cap_identity(self):
        ih=float(self.params['HI'][0]); err=0.
        for x in rows('TIME_CHANNEL_CAPACITY.csv'):
            c=float(x['H_secondary_upper_events_m3'])
            binding=float(x['H_secondary_max_binding_J_m3'])
            kinetic=float(x['eligible_primary_kinetic_J_m3'])
            leftover=float(x['leftover_if_every_eligible_H_secondary_J_m3'])
            err=max(err,abs(kinetic-binding-leftover))
            self.assertAlmostEqual(binding,c*ih*EV_J,delta=3e-60)
        self.assertLess(err,3e-60)
    def test_totals_vs_source_groups(self):
        g={}
        for x in rows('TIME_CHANNEL_CAPACITY.csv'):
            key=(x['observation_s'],x['birth_policy'])
            g.setdefault(key,[]).append(x)
        for x in rows('TIME_TOTAL_CAPACITY.csv'):
            items=g[(x['observation_s'],x['birth_policy'])]
            self.assertAlmostEqual(float(x['H_secondary_upper_events_m3']),
                math.fsum(float(i['H_secondary_upper_events_m3']) for i in items),delta=1e-42)
    def test_luminosity_nothing_at_obs_start(self):
        for x in rows('TIME_TOTAL_CAPACITY.csv'):
            if float(x['observation_s'])==0:self.assertEqual(float(x['total_first_m3']),0.)
    def test_final_max_small(self):
        result=json.loads((OUTPUT/'RESULT.json').read_text())
        self.assertLess(result['final_earliest']['H_capacity_over_first_fraction'],0.01)
        self.assertGreater(result['final_earliest']['H_capacity_over_first_fraction'],0.007)
    def test_spectral_sum(self):
        spectra=rows('FINAL_CAPACITY_ENERGY_BINS.csv')
        for policy in ('earliest','latest'):
            val=math.fsum(float(q['additional_H_secondary_capacity_m3']) for q in spectra if q['birth_policy']==policy)
            actual=next(x for x in rows('TIME_TOTAL_CAPACITY.csv') if x['birth_policy']==policy and float(x['observation_s'])==1e10)
            self.assertAlmostEqual(val,float(actual['H_secondary_upper_events_m3']),delta=1e-42)
    def test_parent_first_counts_exact_source(self):
        parent=rows('TIME_CHANNEL_CAPACITY.csv')
        orig_name='research/cr_phys10_energy_causal_20261030/results/TIME_CHANNEL_ENERGY.csv'
        from zipfile import ZipFile
        import io
        with ZipFile(PARENT) as z:
            old=list(csv.DictReader(io.StringIO(z.read(orig_name).decode())))
        d={(q['observation_s'],q['birth_policy'],q['source'],q['absorber']):float(q['n_first_m3']) for q in old}
        self.assertEqual(len(parent),108)
        for x in parent:
            k=x['observation_s'],x['birth_policy'],x['source'],x['first_absorber']
            self.assertAlmostEqual(d[k],float(x['n_first_m3']),delta=3e-42)
    def test_full_window_causal_sum_against_direct_derivative(self):
        # independent piecewise probability using one original He atom, not the
        # parent log_response expression. Nontrivial both HI and HeI perturbations.
        pp=next(p for p in self.prep if p['source']=='He')
        i=1100;E=float(pp['energy'][i]); self.assertGreater(E,27.2)
        kh=float(pp['k'][i]*pp['frac'][0][i]);ke=float(pp['k'][i]*pp['frac'][1][i]);
        s=2.5e9; T=1e10; u,v=WINDOWS[3];h=1.0e-4
        for b in (0,1):
            fd=(piecewise_probability(kh,ke,s,T,u,v,0,b,+h)-piecewise_probability(kh,ke,s,T,u,v,0,b,-h))/(2*h)
            analytic=float(self.mod.log_response(np.array([kh]),np.array([ke]),s,T,u,v,0,b)[0])
            self.assertLess(abs(fd-analytic)/max(abs(analytic),1e-15),1e-7)

if __name__=='__main__':unittest.main()
