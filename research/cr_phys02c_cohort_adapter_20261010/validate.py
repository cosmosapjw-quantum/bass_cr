"""Bounded adapter campaign; no P02B evolution is executed."""
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import cohort_adapter as A

ROOT = Path(__file__).resolve().parent
TOL = 2e-11

def relative(a, b):
    return float(np.max(np.abs(np.asarray(a)-b))/max(float(np.max(np.abs(b))), 1e-300))

def run():
    start = time.monotonic()
    A.verify_inputs()
    packet = json.loads(A.PACKET.read_text())
    grid = A.P.make_grid(128)
    rows = []
    # Saved rows exercise projection; sampling is independently checked below.
    for row in packet['rows']:
        b = row['boundary']
        rate = A.BoundaryRate(np.array([x['energy_meV'] for x in b]),
            np.array([x['flux_per_initial_electron_per_s'] for x in b]),
            np.array([x['m_H'] for x in b]), np.array([x['n_He'] for x in b]),
            row['proper_time_s'], A.PACKET_SHA)
        p = A.project_boundary_rate(rate)
        expected = np.array([rate.rate_per_upstream_electron_s.sum(),
            rate.rate_per_upstream_electron_s @ (rate.energy_meV/1000)])
        actual = np.array([p[:len(grid)].sum()+p[len(grid)+7],
            p[:len(grid)]@grid+p[len(grid)+8]])
        errors = [abs(a-b)/abs(b) if b else abs(a) for a,b in zip(actual,expected)]
        err = float(max(errors))
        rows.append({'energy_eV':row['initial_energy_eV'], 'epoch_s':row['proper_time_s'],
                     'moment_error':err,'nonnegative':bool(np.all(p>=0)),
                     'zero_counters':bool(np.all(p[len(grid):len(grid)+7]==0))})
    source = A.BoundarySource.from_energy(1000.001)
    horizon = 1e11
    rates = A.F.K.rates(1000.001)
    lam = rates.sum()
    analytic = rates/lam*(-np.expm1(-lam*horizon))
    saved = next(r for r in packet['rows'] if r['initial_energy_eV']==1000.001
                 and r['proper_time_s']==horizon)
    cumulative = np.array([b['cumulative_crossing_count_per_initial_electron'] for b in saved['boundary']])
    gl = []
    for order in (16,32):
        cohorts = A.cohort_quadrature(source,0,horizon,order)
        result = sum((c.quadrature_weight_s*c.boundary_rate.rate_per_upstream_electron_s for c in cohorts))
        gl.append({'order':order,'analytic_error':relative(result,analytic),
                   'saved_error':relative(result,cumulative),
                   'positive_weights':all(c.quadrature_weight_s>0 for c in cohorts),
                   'fresh_age':all(c.initial_age_s==0 and c.age_at(horizon)>=0 for c in cohorts)})
    manufactured=[]
    # Analytic manufactured convolution; receiver is deliberately test-only.
    class ToySource:
        def __init__(self, alpha): self.alpha=alpha
        def validate(self): pass
    original=A.sample_boundary
    try:
        def toy(source,tau):
            return A.BoundaryRate(np.array([989797]),np.array([np.exp(-source.alpha*tau)]),
                                 np.array([0]),np.array([0]),tau,A.PACKET_SHA)
        A.sample_boundary=toy
        for alpha,kappa in [(0,0),(0,2e-11),(1e-11,0),(1e-11,2e-11),(2e-11,2e-11)]:
            for order in (16,32):
                cohorts=A.cohort_quadrature(ToySource(alpha),0,horizon,order)
                actual=sum(c.initial_population.sum()*np.exp(-kappa*c.age_at(horizon)) for c in cohorts)
                delta=kappa-alpha
                expected=horizon*np.exp(-kappa*horizon) if delta==0 else np.exp(-kappa*horizon)*np.expm1(delta*horizon)/delta
                manufactured.append({'alpha':alpha,'kappa':kappa,'order':order,'error':relative(actual,expected)})
    finally: A.sample_boundary=original
    off=A.sample_boundary(A.BoundarySource.from_energy(1000.001,False),horizon)
    t0=A.sample_boundary(source,0)
    rejects=[]
    def reject(label,call):
        try:call()
        except ValueError:rejects.append(label); return
        raise AssertionError('DID_NOT_REJECT:'+label)
    reject('wrong_clock',lambda:A.sample_boundary(A.BoundarySource(source.graph,clock='redshift'),0))
    reject('wrong_normalization',lambda:A.sample_boundary(A.BoundarySource(source.graph,normalization='per m3'),0))
    reject('nan_time',lambda:A.sample_boundary(source,float('nan')))
    reject('negative_time',lambda:A.sample_boundary(source,-1))
    reject('invalid_energy',lambda:A.BoundarySource.from_energy(1000))
    reject('nonfinite_rate',lambda:A.project_boundary_rate(A.BoundaryRate(np.array([989797]),np.array([float('nan')]),np.array([0]),np.array([0]),0,A.PACKET_SHA)))
    reject('invalid_boundary_energy',lambda:A.project_boundary_rate(A.BoundaryRate(np.array([1000001]),np.array([1.]),np.array([0]),np.array([0]),0,A.PACKET_SHA)))
    reject('negative_age',lambda:A.age_at(0,1))
    reject('boundary_lower_limit',lambda:A.project_boundary_rate(A.BoundaryRate(np.array([978782]),np.array([1.]),np.array([0]),np.array([0]),0,A.PACKET_SHA)))
    reject('fractional_H_counter',lambda:A.project_boundary_rate(A.BoundaryRate(np.array([989797]),np.array([1.]),np.array([0.5]),np.array([0]),0,A.PACKET_SHA)))
    reject('fractional_He_counter',lambda:A.project_boundary_rate(A.BoundaryRate(np.array([989797]),np.array([1.]),np.array([0]),np.array([0.5]),0,A.PACKET_SHA)))
    reject('source_time_limit',lambda:A.sample_boundary(source,1e13+1))
    reject('cohort_time_limit',lambda:A.cohort_quadrature(source,0,1e13+1,16))
    elapsed=time.monotonic()-start
    passed=(len(rows)==25 and all(r['moment_error']<=TOL and r['nonnegative'] and r['zero_counters'] for r in rows)
        and all(r['analytic_error']<=TOL and r['saved_error']<=TOL and r['positive_weights'] and r['fresh_age'] for r in gl)
        and all(r['error']<=TOL for r in manufactured) and np.all(off.rate_per_upstream_electron_s==0)
        and np.all(np.isfinite(t0.rate_per_upstream_electron_s)) and len(rejects)==13 and elapsed<=120)
    return {'status':'PASS_ADAPTER_PENDING_REVIEW' if passed else 'FAIL','claim':'adapter only; no P02B physics execution',
      'tolerance':TOL,'saved_projection_rows':rows,'actual_one_event_quadrature':gl,
      'manufactured_convolution':manufactured,'rejected':rejects,'off_exact_zero':bool(np.all(off.rate_per_upstream_electron_s==0)),
      't0_finite':bool(np.all(np.isfinite(t0.rate_per_upstream_electron_s))),'wall_s':elapsed,
      'implementation_sha256':hashlib.sha256((ROOT/'cohort_adapter.py').read_bytes()).hexdigest()}

if __name__=='__main__':
    result=run()
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/VALIDATION_REPAIRED.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    raise SystemExit(0 if result['status']=='PASS_ADAPTER_PENDING_REVIEW' else 1)
