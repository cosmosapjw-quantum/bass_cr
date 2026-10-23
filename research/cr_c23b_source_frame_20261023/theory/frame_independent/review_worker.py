"""Independent finite source review. Called by the leased coordinator."""
from pathlib import Path
import hashlib, json, math, os, resource, sys, time

BASE=Path(__file__).resolve().parent
RUN=Path(sys.argv[1]).resolve()
if os.sched_getaffinity(0)!={4}:
    raise RuntimeError('Reviewer worker must have exclusive assigned CPU4 affinity')
THREADS=('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')
if any(os.environ.get(k)!='1' for k in THREADS):
    raise RuntimeError('native thread environment not1')
sys.path.insert(0,str(RUN/'source_snapshot'))
from boost_kernel import AngularBox,Boost,ELECTRON_REST_EV,ElectronMeasure
from source_ledger import DecayClock
from independent_reference import reference,endpoints
import mpmath as mp
mp.mp.dps=80
START=time.perf_counter()

def save(name,value):
    with (RUN/name).open('x') as stream:
        json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')

energies=[0.,1e-15,1e-6,1.,10.,5690.,9937.21,18590.,301370.,782347.,1e9]
boosts=[0.,1e-12,1e-8,1e-4,.1,1.,10.,1e3]
cases=[(k,u,'grid') for k in energies for u in boosts]
for u in (1e-8,1e-4,.1,1.,10.,1e3):
    dm=u*(u/(math.hypot(1,u)+1)); k=dm*ELECTRON_REST_EV
    cases.extend((kk,u,'matched_nextafter') for kk in (math.nextafter(k,0),k,math.nextafter(k,math.inf)))
checks=[];failed=[];edge_max=mp.mpf(0)
for k,u,label in cases:
    box=AngularBox.from_energy(k,Boost(u))
    ml,mh,ma,mb=endpoints(k,u,ELECTRON_REST_EV)
    edge_err=max(abs(mp.mpf(box.lower_ev)-ml),abs(mp.mpf(box.upper_ev)-mh))/max(mp.mpf(1),ma+ELECTRON_REST_EV)
    edge_max=max(edge_max,edge_err)
    intervals=[(0.,10.),(10.,100.),(100.,9937.21),(9937.21,1e6),(1e6,math.inf),(0.,math.inf)]
    if k>0: intervals += [(0.,k),(k,math.inf)]
    for lo,hi in intervals:
        actual=box.interval(lo,hi).as_tuple()
        expected=reference(k,u,ELECTRON_REST_EV,lo,hi)
        scales=(mp.mpf(1),max(mp.mpf(1),ma),max(mp.mpf(1),ma+ELECTRON_REST_EV),max(mp.mpf(1),ma+ELECTRON_REST_EV))
        errors=[abs(mp.mpf(a)-e)/s for a,e,s in zip(actual,expected,scales)]
        ok=all(e<=mp.mpf('2e-12') for e in errors)
        row={'K_eV':k,'u':u,'case':label,'lo_eV':lo,'hi_eV':None if math.isinf(hi) else hi,'actual':actual,'reference80':[mp.nstr(x,83) for x in expected],'normalized_errors':[float(e) for e in errors],'result':'PASS' if ok else 'FAIL'}
        checks.append(row)
        if not ok:failed.append(row)

# Independent decay-clock/parent-direction assertions use the declared spectrum,
# not any reconstructed beta shape or parent Q ceiling.
measure=ElectronMeasure((10.,18590.),(.25,.75),'parent_rest','electrons_per_event','C23B_REVIEW_ATOM_PAIR')
sources=[]
for u in (0.,1e-12,.1,1.,1e3):
    clock=DecayClock(2.3,17.,Boost(u),.2,3.1,4.7)
    g=mp.sqrt(1+mp.mpf(u)**2)
    est=mp.mpf('.25')*(10+mp.mpf(ELECTRON_REST_EV))+mp.mpf('.75')*(18590+mp.mpf(ELECTRON_REST_EV))
    expected_number=mp.mpf(2.3)/(17*g)
    expected_total=mp.mpf(2.3)*est/17
    expected_kinetic=mp.mpf(2.3)/17*(est-mp.mpf(ELECTRON_REST_EV)/g)
    for direction in ('isotropic','equal_opposite_lrs_beams','single_beam'):
        out=clock.electron_sources(measure,parent_directions=direction)
        vals=out['physical_number_kinetic_total_parallelpc_per_m3_s']
        errors=[float(abs(mp.mpf(v)-e)/max(mp.mpf(1),abs(e))) for v,e in zip(vals[:3],(expected_number,expected_kinetic,expected_total))]
        flux_expected=mp.mpf(2.3)*mp.mpf(u)/g*est/17 if direction=='single_beam' else mp.mpf(0)
        flux_error=float(abs(mp.mpf(out['net_parallel_pc_source_ev_m3_s'])-flux_expected)/max(mp.mpf(1),abs(expected_total)))
        ensemble_tuple_consistent=(direction=='single_beam' or vals[3]==0.)
        sources.append({'u':u,'direction':direction,'errors':errors,'flux_error':flux_error,'ensemble_tuple_consistent':ensemble_tuple_consistent})
save('ANGULAR_REFERENCE_CHECKS.json',checks)
save('DECAY_CLOCK_CHECKS.json',sources)
complete={'schema':'C23B_INDEPENDENT_FRAME_REVIEW_V1','status':'PASS_SCOPED' if not failed and all(x['ensemble_tuple_consistent'] and max(x['errors']+[x['flux_error']])<=2e-12 for x in sources) else 'FAIL','cases':len(cases),'bin_checks':len(checks),'failed_bin_checks':len(failed),'failure_examples':failed[:12],'max_normalized_errors':[max(row['normalized_errors'][i] for row in checks) for i in range(4)],'max_endpoint_error_totalenergy_scaled':float(edge_max),'decay_clock_cases':len(sources),'ensemble_tuple_inconsistent_cases':sum(not x['ensemble_tuple_consistent'] for x in sources),'method':'80-digit independent rest-cosine clipping and 2-point Gauss integration (degree<=1 exact); source rates independently evaluated from proper lifetime and rest total-energy moments','mpmath_version':mp.__version__,'reference_digits':80,'tolerance_normalized':2e-12,'worker_cpu':4,'native_threads_per_worker':1,'wall_s':time.perf_counter()-START,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'global_error_bound':None,'historical_ODE_calls':0,'new_ODE_calls':0,'EXECUTION':'COMPLETE_SCOPED_NEW_REVIEW','PUBLICATION':'PARENT_PENDING','BACKUP':'PARENT_PENDING','DAG':'independent theorem+producer snapshot review; resolve actual findings before adoption'}
save('COMPLETE.json',complete)
print(json.dumps({k:v for k,v in complete.items() if k!='failure_examples'}))
