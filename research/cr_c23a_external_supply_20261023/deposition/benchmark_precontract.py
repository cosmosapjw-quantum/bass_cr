"""Bounded same-input timings and a finite-response moment counterexample."""
import hashlib
import json
import os
from pathlib import Path
import resource
from statistics import median
import time
from datetime import datetime, timezone
from math import fsum

from fs2010_operator import FS2010Response, PLSpectrum, CONTRACTED_COLUMNS
from audit_fs2010_operator import reference_gauss


def main():
    base=Path(__file__).resolve().parent
    out=base/'c23a_precontraction_timing_20261023_v1'
    out.mkdir(exist_ok=False)
    if 3 not in os.sched_getaffinity(0):raise RuntimeError('CPU3 unavailable')
    os.sched_setaffinity(0,{3})
    def write(name,obj):
        with (out/name).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
    start=time.perf_counter();cpu=time.process_time()
    write('LEASE_START.json',{'owner':'/root/cr_deposition','cpu':3,'pid':os.getpid(),'threads':1,'UTC':datetime.now(timezone.utc).isoformat()})
    response=FS2010Response(base/'upstream/x_int_tables',axis='unambiguous_high_ionization')
    energies=(10.,10.2,13.6,24.6,54.4,100.,300.,1000.,3000.,9937.21)
    xis=tuple(.1+i*(.999-.1)/63 for i in range(64))
    # Force exact endpoints rather than make an endpoint depend on multiplication.
    xis=xis[:-1]+(.999,)
    spectra=[]
    for power in (0.,1.5,2.5):
        raw=PLSpectrum(energies,tuple(e**(-power) for e in energies))
        spectra.append(PLSpectrum(energies,tuple(q/raw.injected_energy() for q in raw.number_rate)))
    contract={'number_spectra':[{'energy_eV':s.energy,'PL_node_number_rate':s.number_rate,'units':s.units} for s in spectra], 'xi_queries':xis,'repeats':3,'source_axis':response.axis,'reference':'Gauss-Legendre2 on all PL union cells','query':'precontract xi nodes, then convex xi interpolation','normalization':'Each diagnostic spectrum integrates to 1 eV/Href/eta; no astrophysical amplitude claim'}
    write('INPUT.json',contract)
    input_sha=hashlib.sha256((out/'INPUT.json').read_bytes()).hexdigest()
    results=[];maxdiff=0.
    for repeat in range(3):
        for si,spectrum in enumerate(spectra):
            t=time.perf_counter();prepared=response.prepare(spectrum);build=time.perf_counter()-t
            if repeat%2:
                t=time.perf_counter();fast=[prepared.at(x) for x in xis];fast_t=time.perf_counter()-t
                t=time.perf_counter();slow=[reference_gauss(response,spectrum,x) for x in xis];slow_t=time.perf_counter()-t
            else:
                t=time.perf_counter();slow=[reference_gauss(response,spectrum,x) for x in xis];slow_t=time.perf_counter()-t
                t=time.perf_counter();fast=[prepared.at(x) for x in xis];fast_t=time.perf_counter()-t
            local=max(abs(f[k]-r)/max(abs(r),1e-300) for f,s in zip(fast,slow) for k,r in zip(CONTRACTED_COLUMNS,s))
            maxdiff=max(maxdiff,local)
            results.append({'repeat':repeat,'spectrum_index':si,'queries':len(xis),'intervals':prepared.interval_count,'prepare_s':build,'direct_s':slow_t,'prepared_query_s':fast_t,'direct_over_query':slow_t/fast_t,'direct_over_build_plus_queries':slow_t/(build+fast_t),'amortization_queries':build/((slow_t-fast_t)/len(xis)),'max_relative_difference':local})
    counter=[]
    for xi in (.1,.5,.9):
        mono=response.at(100.,xi);low=response.at(10.,xi);high=response.at(190.,xi)
        mono_energy=[100.*v for v in mono[:3]]
        mix_energy=[.5*(10.*a+190.*b) for a,b in zip(low[:3],high[:3])]
        mono_counts=list(mono[3:]);mix_counts=[.5*(a+b) for a,b in zip(low[3:],high[3:])]
        counter.append({'xi':xi,'sourceA_atoms_eV_weights':[[100.,1.]],'sourceB_atoms_eV_weights':[[10.,.5],[190.,.5]],'same_electron_number':1.,'same_kinetic_energy_eV':100.,'A_energy_ion_heat_exc_eV':mono_energy,'B_energy_ion_heat_exc_eV':mix_energy,'B_minus_A_heat_eV':mix_energy[1]-mono_energy[1],'A_numbers_Lya_HI_HeI_HeII':mono_counts,'B_numbers_Lya_HI_HeI_HeII':mix_counts,'source_scope':'finite downloaded table interpolant; frozen source gas slice; not an IGM evolution'})
    write('MOMENT_COUNTEREXAMPLE.json',counter)
    report={'status':'PASS_SCOPED' if maxdiff<2e-13 and all(abs(c['B_minus_A_heat_eV'])>1e-4 for c in counter) else 'FAIL','input_sha256':input_sha,'pairs':results,'median_query_only_ratio':median(r['direct_over_query'] for r in results),'median_build_plus_64_queries_ratio':median(r['direct_over_build_plus_queries'] for r in results),'median_amortization_queries':median(r['amortization_queries'] for r in results),'max_relative_difference':maxdiff,'timing_claim':'Observed bounded microbenchmark; stable, cosmological-ODE, and NCP speedups NOT_ESTABLISHED','resources':{'cpu':3,'affinity':sorted(os.sched_getaffinity(0)),'native_threads':1,'wall_s':time.perf_counter()-start,'cpu_s':time.process_time()-cpu,'ru_maxrss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},'new_ODE':0,'physical_coupling':'NOT_ADMITTED'}
    write('RESULT.json',report)
    write('LEASE_COMPLETE.json',{'owner':'/root/cr_deposition','cpu':3,'status':'RELEASED','UTC':datetime.now(timezone.utc).isoformat()})
    print(json.dumps({k:v for k,v in report.items() if k!='pairs'},indent=2))
    print(json.dumps(counter,indent=2))
    if report['status']!='PASS_SCOPED':raise SystemExit(1)


if __name__=='__main__':main()
