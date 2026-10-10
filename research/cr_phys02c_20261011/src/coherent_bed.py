# SPDX-License-Identifier: GPL-3.0-only
"""Frozen CR-PHYS02C full BED atomic replacement; parent transport unchanged."""
from pathlib import Path
import hashlib, importlib.util, json, sys, math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
def checked_file(path,digest):
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=digest: raise ValueError('HASH_MISMATCH '+str(path))
    return raw
checked_file(ROOT/'state/SCIENTIFIC_CONTRACT.json','e0445ecbf052a3441f6203f9e0463defcf0c24c0ee018a67e112d338991f47ee')
manifest=json.loads(checked_file(ROOT/'inputs/PARENT_IDENTITY.json','a733b00ed6da96c9c05bcb80ac9b64d12bb48b742fe5c7738debe8faddb63c50'))
for rel,entry in manifest['files'].items(): checked_file(REPO/rel,entry['sha256'])
ORACLE=json.loads(checked_file(ROOT/'research/ionization_sources/SOURCE_ALGEBRA_RESULT.json','7eb9d5abfa9eec757475194aaaee5b0660d8a493fc30b0891cb7b356a1c2ffa3'))
path=REPO/'research/cr_phys02b_20261010/src/causal_cascade.py'
spec=importlib.util.spec_from_file_location('cr_phys02c_checked_parent',path)
parent=importlib.util.module_from_spec(spec);sys.modules[spec.name]=parent;spec.loader.exec_module(parent)
class Ionization:
    def __init__(self,species):
        self.species=species
        self.B_eV,self.U_eV,self.N=(13.6057,13.6057,1.) if species=='HI' else (24.587,39.51,2.)
        self.coefficients=(0.,8.24012,-10.4769,3.96496,-.0445976)
        self.Ni=float(ORACLE['H']['Ni']) if species=='HI' else 1.61008048
        self.oscillator_Q=float(ORACLE['H']['Q']) if species=='HI' else float(ORACLE['He']['Q_decimal'])
        self.K=2-self.Ni/self.N
        self.S_m2=4*math.pi*parent.A0_M**2*self.N*(13.6057/self.B_eV)**2
    def g(self,w):
        w=np.asarray(w,dtype=float)
        if np.any(~np.isfinite(w)) or np.any(w<0): raise ValueError('OSCILLATOR_DOMAIN')
        if self.species=='HeI':
            y=1/(1+w);return sum(c*y**k for k,c in enumerate(self.coefficients,2))
        root=np.sqrt(w);ratio=np.ones_like(root);np.divide(np.arctan(root),root,out=ratio,where=root>0)
        inverse=np.full_like(root,np.inf);np.divide(2*math.pi,root,out=inverse,where=root>0)
        return (128/3)*np.exp(-4*ratio)/(1+w)**4/(-np.expm1(-inverse))
    def D(self,t):
        t=np.asarray(t,dtype=float)
        if np.any(~np.isfinite(t)) or np.any(t<1):raise ValueError('D_DOMAIN')
        if self.species=='HeI':
            logy=-np.log1p((t-1)/2)
            return sum(c/k*(-np.expm1(k*logy)) for k,c in enumerate(self.coefficients,2))/self.N
        x,weight=parent.gauss(128);half=(t-1)/2
        w=half[...,None]/2*(1+x)
        return half/2*np.sum(weight*self.g(w)/(1+w),axis=-1)/self.N
    def total_m2(self,energy):
        E=parent.checked_energy(energy);t=np.maximum(E/self.B_eV,1.);logt=np.log(t)
        bracket=self.D(t)*logt+self.K*(-np.expm1(-logt)-logt/(t+1))
        out=np.where(E>self.B_eV,self.S_m2/(t+self.U_eV/self.B_eV+1)*bracket,0.)
        if np.any(~np.isfinite(out)) or np.any(out<0):raise ArithmeticError('INVALID_TOTAL')
        return out
    def raw_bed_m2_eV(self,energy,slow_eV):
        E=float(parent.checked_energy(energy));W=np.asarray(slow_eV,dtype=float)
        if E<=self.B_eV or np.any(~np.isfinite(W)) or np.any(W<0) or np.any(W>(E-self.B_eV)/2):raise ValueError('BED_SLOW_ELECTRON_DOMAIN')
        t=E/self.B_eV;w=W/self.B_eV;y=1/(1+w);r=1/(t-w)
        out=self.S_m2/(self.B_eV*(t+self.U_eV/self.B_eV+1))*(self.K*(y*y+r*r-(y+r)/(t+1))+np.log(t)*self.g(w)*y/self.N)
        if np.any(~np.isfinite(out)) or np.any(out<0):raise ArithmeticError('NEGATIVE_OR_NONFINITE_BED_DENSITY')
        return out
    raw_integral_m2=parent.Ionization.raw_integral_m2
    def normalized_sdcs_m2_eV(self,energy,slow_eV,order=128):
        """Compatibility API: physical SDCS has no external rate normalization."""
        return self.raw_bed_m2_eV(energy,slow_eV)
class AtomicData(parent.AtomicData):
    def __init__(self):
        super().__init__();self.ionization={sp:Ionization(sp) for sp in ('HI','HeI')}
Cascade=parent.Cascade
ElectronSource=parent.ElectronSource
