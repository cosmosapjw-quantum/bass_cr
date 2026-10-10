# SPDX-License-Identifier: GPL-3.0-only
"""Conditional CR-PHYS02B electron branching and stopping, fixed gas.

This is a source-pinned, truncated research operator, not a production REI
provider. It keeps ion binding, atomic excitation/radiation, Coulomb heat,
active electrons and the unresolved cutoff kinetic energy disjoint.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import sys

import numpy as np
from scipy import sparse
from scipy.constants import e as EV_J, epsilon_0, m_e, hbar
from scipy.sparse.linalg import expm_multiply, spsolve

ROOT = Path(__file__).resolve().parents[1]
CUT = .1
SPLIT = 10.
UPPER = 900.
T_END = 1.e10
N_H = 140.
N_HE = N_H*.248/(4*(1-.248))
N_E = .01*(N_H+N_HE)
DENSITIES = {'HI': .99*N_H, 'HeI': .99*N_HE}
A0_M = 5.29177210544e-11
KAPPA = EV_J**2/(4*math.pi*epsilon_0)
LEDGERS = ('heat', 'binding_HI', 'binding_HeI', 'excitation_HI',
           'excitation_HeI', 'cutoff_energy', 'ionizations_HI',
           'ionizations_HeI', 'cutoff_number', 'low_cross_energy',
           'low_cross_number')
ENERGY_LEDGERS = LEDGERS[:6]


def read_checked(path, digest):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError('SOURCE_HASH_MISMATCH: '+str(path))
    return raw


@lru_cache(maxsize=1)
def parent_low():
    manifest = json.loads((ROOT/'inputs/PARENT_SOURCE_MANIFEST.json').read_text())
    for rel, info in manifest['files'].items():
        read_checked(ROOT.parent/rel, info['sha256'])
    path = ROOT.parent/'cr_phys02a_20261010/src/causal_subthreshold.py'
    name = 'cr_phys02b_exact_parent_low'
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@lru_cache(maxsize=8)
def gauss(order):
    if type(order) is not int or not 2 <= order <= 512:
        raise ValueError('INVALID_QUADRATURE_ORDER')
    return np.polynomial.legendre.leggauss(order)


def checked_energy(energy, lower=0.):
    E = np.asarray(energy, dtype=float)
    if np.any(~np.isfinite(E)) or np.any(E < lower) or np.any(E > UPPER):
        raise ValueError('ELECTRON_ENERGY_OUT_OF_SCOPED_DOMAIN')
    return E


class ElectronSource:
    def __init__(self, proton_order=64):
        self.low = parent_low()
        self.parent = self.low.DirectElectronSource(order=proton_order)
        self.coefficients = self.parent.coefficients
        self.minimum_endpoint_eV = min(float(np.min(
            self.parent.rudd.secondary_max_eV(self.parent.K, sp)))
            for sp in self.parent.densities)
        if self.minimum_endpoint_eV <= UPPER:
            raise ValueError('RATIONAL_SOURCE_ENDPOINT_NOT_COVERED')
        self.selected_A_energy = self.parent.source_energy_coefficient(CUT, UPPER)
        self.energy_scale_eV_m3 = T_END**2*self.selected_A_energy

    def spectrum_A(self, energy):
        W = checked_energy(energy)
        out = np.zeros_like(W)
        for c1, c2, binding in self.coefficients.values():
            w = W/binding
            out += (c1+c2*w)/(1+w)**3
        return out

    def coverage(self):
        total = self.parent.source_energy_coefficient(0., None)
        bands = {'below_cutoff': (0., CUT), 'direct_low': (CUT, SPLIT),
                 'direct_high_selected': (SPLIT, UPPER),
                 'unselected_900_1000': (UPPER, 1000.),
                 'unselected_above_1000': (1000., None)}
        vals = {k: self.parent.source_energy_coefficient(*b) for k,b in bands.items()}
        return {'all_direct_A_energy_eV_m3_s2': total,
                'band_A_energy_eV_m3_s2': vals,
                'band_fractions_of_all_direct': {k:v/total for k,v in vals.items()},
                'selected_fraction_of_all_direct': self.selected_A_energy/total,
                'minimum_sampled_proton_ejection_endpoint_eV': self.minimum_endpoint_eV,
                'selected_injected_energy_at_T_J_m3': .5*self.energy_scale_eV_m3*EV_J}


@dataclass(frozen=True)
class Ionization:
    species: str
    B_eV: float
    U_eV: float
    N: float
    Q: float
    coefficients: tuple

    @property
    def Ni(self):
        return sum(a/(k-1) for k,a in enumerate(self.coefficients, start=2))

    @property
    def oscillator_Q(self):
        return 2/self.N*sum(a/k for k,a in enumerate(self.coefficients, start=2))

    @property
    def S_m2(self):
        return 4*math.pi*A0_M**2*self.N*(13.6057/self.B_eV)**2

    def total_m2(self, energy):
        E = checked_energy(energy)
        t = np.maximum(E/self.B_eV, 1.)
        logt = np.log(t)
        bracket = (.5*self.Q*logt*(-np.expm1(-2*logt))
                   +(2-self.Q)*(-np.expm1(-logt)-logt/(t+1)))
        return np.where(E > self.B_eV,
                        self.S_m2/(t+self.U_eV/self.B_eV+1)*bracket, 0.)

    def raw_bed_m2_eV(self, energy, slow_eV):
        E = float(checked_energy(energy))
        W = np.asarray(slow_eV, dtype=float)
        if (E <= self.B_eV or np.any(~np.isfinite(W)) or np.any(W < 0)
                or np.any(W > (E-self.B_eV)/2)):
            raise ValueError('BED_SLOW_ELECTRON_DOMAIN')
        t, w = E/self.B_eV, W/self.B_eV
        y = 1/(1+w)
        oscillator = sum(a*y**k for k,a in enumerate(self.coefficients, start=2))
        c = 2-self.Ni/self.N
        shape = (-c/(t+1)*(y+1/(t-w))
                 +c*(y*y+1/(t-w)**2)+np.log(t)/self.N*y*oscillator)
        result = self.S_m2/(self.B_eV*(t+self.U_eV/self.B_eV+1))*shape
        if np.any(~np.isfinite(result)) or np.any(result < 0):
            raise ArithmeticError('NEGATIVE_OR_NONFINITE_BED_DENSITY')
        return result

    def raw_integral_m2(self, energy, order=128):
        E = float(checked_energy(energy))
        if E <= self.B_eV:
            return 0.
        x,w = gauss(order)
        upper = (E-self.B_eV)/2
        return float(upper/2*np.dot(w, self.raw_bed_m2_eV(E, upper/2*(1+x))))

    def normalized_sdcs_m2_eV(self, energy, slow_eV, order=128):
        return self.raw_bed_m2_eV(energy,slow_eV)*float(self.total_m2(energy))/self.raw_integral_m2(energy,order)


class AtomicData:
    def __init__(self):
        used = json.loads((ROOT/'inputs/CCC_USED_CHANNELS.json').read_text())
        self.excitation = []
        for c in used['channels']:
            path = ROOT/c['path']
            read_checked(path, c['raw_sha256'])
            arr = np.loadtxt(path, comments='#', usecols=(0,1))
            factor = used['a0_m']**2 if c['native_unit']=='a0^2' else 1.e-4
            if (np.any(np.diff(arr[:,0]) <= 0) or np.any(~np.isfinite(arr))
                    or np.any(arr[:,1] < 0) or arr[-1,0] < UPPER):
                raise ValueError('INVALID_CCC_TABLE')
            self.excitation.append({**c, 'energy':arr[:,0], 'sigma':arr[:,1]*factor})
        path = ROOT/'inputs/NIST_IONIZATION.json'
        identity = json.loads((ROOT/'inputs/NIST_IDENTITY.json').read_text())
        read_checked(path, identity['parameters_sha256'])
        nist = json.loads(path.read_text())
        self.nist_metadata = nist
        self.ionization = {sp:Ionization(sp, float(d['B_eV']), float(d['U_eV']),
                                       float(d['N']), float(d['Q']), tuple(d['coefficients']))
                           for sp,d in nist['species'].items()}
        if set(self.ionization) != {'HI','HeI'}:
            raise ValueError('NIST_SPECIES_IDENTITY_MISMATCH')

    def excitation_sigma(self, channel, energy):
        E = checked_energy(energy)
        return np.interp(E, channel['energy'], channel['sigma'], left=0.)


def stopping_eV_s(energy, quantum_constant=0.):
    E = checked_energy(energy, CUT)
    if quantum_constant not in (0., -.5):
        raise ValueError('UNDECLARED_COULOMB_PRESCRIPTION')
    v = np.sqrt(2*E*EV_J/m_e)
    omega = math.sqrt(N_E*EV_J**2/(epsilon_0*m_e))
    classical = np.log(v*E*EV_J/(KAPPA*omega))
    quantum = np.log(2*E*EV_J/(hbar*omega))+quantum_constant
    coulomb_log = np.minimum(classical,quantum)
    if np.any(coulomb_log <= 0):
        raise ArithmeticError('NONPOSITIVE_COULOMB_LOG')
    return 4*math.pi*KAPPA**2*N_E/(m_e*v*EV_J)*coulomb_log


def energy_grid(low_cells, high_cells):
    if (type(low_cells) is not int or type(high_cells) is not int
            or low_cells < 10 or high_cells < 10):
        raise ValueError('INVALID_ENERGY_GRID')
    return np.r_[np.linspace(CUT,SPLIT,low_cells+1)[1:],
                 np.geomspace(SPLIT,UPPER,high_cells+1)[1:]]


class Cascade:
    def __init__(self, low_cells=400, high_cells=800, sharing_order=4,
                 quantum_constant=0., atomic=None):
        self.E = energy_grid(low_cells,high_cells)
        self.n = len(self.E)
        self.size = self.n+len(LEDGERS)
        self.ix = {name:self.n+k for k,name in enumerate(LEDGERS)}
        self.atomic = atomic or AtomicData()
        self.sharing_order = sharing_order
        self.quantum_constant = quantum_constant
        self.mesh = (low_cells, high_cells)
        self.normalization_diagnostics = []
        self.G = self._generator()

    def project(self, energies, counts, from_high=False):
        """Count/energy preserving projection, with actual below-cutoff energy.

        The near-cutoff interval projects between the ghost E=0.1 absorber
        and the first active node; its resolution error is checked against
        the inherited continuum response. No residual becomes heat here.
        """
        W, p = np.broadcast_arrays(np.asarray(energies,dtype=float),
                                    np.asarray(counts,dtype=float))
        W, p = W.ravel(), p.ravel()
        if (np.any(~np.isfinite(W)) or np.any(~np.isfinite(p))
                or np.any(W < 0) or np.any(W > UPPER) or np.any(p < 0)):
            raise ValueError('INVALID_ELECTRON_PROJECTION')
        out = np.zeros(self.size)
        absorbed = W <= CUT
        cut_n = float(np.sum(p[absorbed]))
        cut_u = float(np.dot(p[absorbed],W[absorbed]))
        W, p = W[~absorbed], p[~absorbed]
        idx = np.searchsorted(self.E,W,side='left')
        upper = self.E[idx]
        lower = np.r_[CUT,self.E[:-1]][idx]
        frac = (W-lower)/(upper-lower)
        if np.any(frac < 0) or np.any(frac > 1):
            raise ArithmeticError('NONCONVEX_ELECTRON_PROJECTION')
        up_counts = np.bincount(idx,weights=p*frac,minlength=self.n)
        ghost = idx==0
        cut_from_grid = float(np.sum(p[ghost]*(1-frac[ghost])))
        down_counts = np.bincount(idx[~ghost]-1,
                                 weights=p[~ghost]*(1-frac[~ghost]),minlength=self.n)
        active_counts = up_counts+down_counts
        out[:self.n] = self.E*active_counts
        cut_n += cut_from_grid
        cut_u += CUT*cut_from_grid
        out[self.ix['cutoff_energy']] = cut_u
        out[self.ix['cutoff_number']] = cut_n
        if from_high:
            low = self.E <= SPLIT
            out[self.ix['low_cross_energy']] = np.sum(out[:self.n][low])+cut_u
            out[self.ix['low_cross_number']] = np.sum(active_counts[low])+cut_n
        return out

    def _sharing(self, ion, energy):
        available = energy-ion.B_eV
        half = available/2
        nodes = np.r_[CUT,self.E]
        reflected = available-nodes
        knots = np.unique(np.r_[0.,half,nodes[(nodes>0)&(nodes<half)],
                                reflected[(reflected>0)&(reflected<half)]])
        x,w = gauss(self.sharing_order)
        mids = .5*(knots[1:]+knots[:-1])
        widths = .5*np.diff(knots)
        values = (mids[:,None]+widths[:,None]*x).ravel()
        weights = (widths[:,None]*w*ion.raw_bed_m2_eV(energy,
                              mids[:,None]+widths[:,None]*x)).ravel()
        norm = float(np.sum(weights))
        if not math.isfinite(norm) or norm <= 0:
            raise ArithmeticError('INVALID_BED_NORMALIZATION')
        reference = ion.raw_integral_m2(energy)
        error = abs(norm-reference)/reference
        if error > 2.e-8:
            raise ArithmeticError('SHARING_QUADRATURE_NORMALIZATION_FAILED')
        self.normalization_diagnostics.append((ion.species,energy,error,
                                                float(ion.total_m2(energy))/norm))
        return values, weights/norm

    def _generator(self):
        rows, cols, values = [], [], []
        speed = np.sqrt(2*self.E*EV_J/m_e)
        b = stopping_eV_s(self.E,self.quantum_constant)
        ion_rates = {sp:DENSITIES[sp]*speed*ion.total_m2(self.E)
                     for sp,ion in self.atomic.ionization.items()}
        excitation_rates = [(c,DENSITIES[c['species']]*speed*
                              self.atomic.excitation_sigma(c,self.E))
                            for c in self.atomic.excitation]
        self.rates = {'stopping_eV_s':b, **{'ion_'+k:v for k,v in ion_rates.items()}}
        for sp in DENSITIES:
            self.rates['exc_'+sp] = sum(r for c,r in excitation_rates if c['species']==sp)
        for j,energy in enumerate(self.E):
            col = np.zeros(self.size)
            previous = CUT if j==0 else self.E[j-1]
            drift = b[j]/(energy-previous)
            col[j] -= drift
            col += drift/energy*self.project(previous,1.,energy>SPLIT)
            col[self.ix['heat']] += drift*(energy-previous)/energy
            for sp,ion in self.atomic.ionization.items():
                rate = ion_rates[sp][j]
                if rate == 0:
                    continue
                slow,p = self._sharing(ion,energy)
                fast = energy-ion.B_eV-slow
                col[j] -= rate
                col += rate/energy*(self.project(slow,p,energy>SPLIT)
                                    +self.project(fast,p,energy>SPLIT))
                col[self.ix['binding_'+sp]] += rate*ion.B_eV/energy
                col[self.ix['ionizations_'+sp]] += rate/energy
            for channel,rates in excitation_rates:
                rate = rates[j]
                if rate == 0:
                    continue
                cost = channel['adopted_effective_cost_eV']
                col[j] -= rate
                col += rate/energy*self.project(energy-cost,1.,energy>SPLIT)
                col[self.ix['excitation_'+channel['species']]] += rate*cost/energy
            nonzero = np.flatnonzero(col)
            rows.extend(nonzero.tolist())
            cols.extend([j]*len(nonzero))
            values.extend(col[nonzero].tolist())
        return sparse.csc_matrix((np.asarray(values)*T_END,(rows,cols)),
                                 shape=(self.size,self.size))

    def functionals(self):
        energy = np.zeros(self.size)
        energy[:self.n] = 1
        for k in ENERGY_LEDGERS: energy[self.ix[k]] = 1
        number = np.zeros(self.size)
        number[:self.n] = 1/self.E
        number[self.ix['cutoff_number']] = 1
        number[self.ix['ionizations_HI']] = -1
        number[self.ix['ionizations_HeI']] = -1
        return energy,number

    def source_vectors(self, source, order=8, enabled=True):
        if type(enabled) is not bool:
            raise ValueError('SOURCE_ENABLED_MUST_BE_BOOL')
        out = np.zeros((self.size,2))
        x,w = gauss(order)
        edges = np.r_[CUT,self.E]
        for j,(lo,hi) in enumerate(zip(edges[:-1],edges[1:])):
            points = (lo+hi)/2+(hi-lo)/2*x
            weights = (hi-lo)/2*w*source.spectrum_A(points)/source.selected_A_energy
            high = lo >= SPLIT
            out[:,int(high)] += self.project(points,weights,from_high=high)
        return out if enabled else np.zeros_like(out)

    def augmented(self, source_vectors):
        tags = source_vectors.shape[1]
        z1 = sparse.csc_matrix((self.size,tags))
        z2 = sparse.csc_matrix((tags,self.size))
        z3 = sparse.csc_matrix((tags,tags))
        matrix = sparse.bmat([[self.G,sparse.csc_matrix(source_vectors),z1],
                              [z2,z3,sparse.eye(tags,format='csc')],
                              [z2,z3,z3]],format='csc')
        initial = np.zeros((self.size+2*tags,tags))
        initial[self.size+tags:,:] = np.eye(tags)
        return matrix,initial

    def evolve(self, source_vectors, time_s=T_END, samples=2):
        if (not np.isscalar(time_s) or isinstance(time_s,(bool,np.bool_))
                or not math.isfinite(float(time_s)) or not 0<=time_s<=T_END):
            raise ValueError('TIME_OUT_OF_SOURCE_DOMAIN')
        if type(samples) is not int or samples<2:
            raise ValueError('INVALID_TIME_SAMPLE_COUNT')
        if time_s==0:
            return np.zeros((samples,self.size,source_vectors.shape[1]))
        matrix,initial = self.augmented(source_vectors)
        return expm_multiply(matrix,initial,start=0.,stop=time_s/T_END,
                             num=samples,endpoint=True,traceA=float(matrix.diagonal().sum()))[:,:self.size,:]

    def terminal_yields(self, source_vectors):
        residence = spsolve(-self.G[:self.n,:self.n],source_vectors[:self.n,:])
        if residence.ndim==1: residence = residence[:,None]
        out = self.G[:, :self.n]@residence+source_vectors
        out[:self.n,:] = 0.  # This output reports integrated absorber yields only.
        return np.asarray(out)

    def summarize(self, state, source_vectors, source, u):
        """Return both disjoint source tags and their linear sum in SI."""
        z = np.column_stack([state,np.sum(state,axis=1)])
        a = np.column_stack([source_vectors,np.sum(source_vectors,axis=1)])
        rate = self.G@z+a*u
        ef,nf = self.functionals()
        scale = source.energy_scale_eV_m3
        ans = {}
        for k,name in enumerate(('direct_0p1_10','direct_10_900','selected_total')):
            v, r = z[:,k], rate[:,k]
            d = {'active_electron_energy_J_m3':float(np.sum(v[:self.n])*scale*EV_J),
                 'active_electron_number_m3':float(np.dot(1/self.E,v[:self.n])*scale),
                 'injected_energy_J_m3':float(.5*u*u*np.dot(ef,a[:,k])*scale*EV_J),
                 'injected_number_m3':float(.5*u*u*np.dot(nf,a[:,k])*scale)}
            for field in ENERGY_LEDGERS:
                d[field+'_J_m3'] = float(v[self.ix[field]]*scale*EV_J)
                d[field+'_power_J_m3_s'] = float(r[self.ix[field]]*scale*EV_J/T_END)
            for field in LEDGERS[6:]:
                energy_field = field.endswith('energy')
                factor = scale*(EV_J if energy_field else 1.)
                suffix = '_J_m3' if energy_field else '_m3'
                d[field+suffix] = float(v[self.ix[field]]*factor)
                d[field+('_power_J_m3_s' if energy_field else '_rate_m3_s')] = float(r[self.ix[field]]*factor/T_END)
            d['energy_ledger_relative_residual'] = float((np.dot(ef,v)-.5*u*u*np.dot(ef,a[:,k]))/max(.5*u*u*np.dot(ef,a[:,k]),1e-100))
            d['number_ledger_relative_residual'] = float((np.dot(nf,v)-.5*u*u*np.dot(nf,a[:,k]))/max(.5*u*u*np.dot(nf,a[:,k]),1e-100))
            ans[name] = d
        return {'u':float(u),'time_s':float(u*T_END),'time_year':float(u*T_END/31557600.),'components':ans}
