"""Independent NEW source/anchor arithmetic. Does not import the production provider."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import csv, datetime, hashlib, json, math, pathlib, resource, sys, time
from decimal import Decimal, getcontext
from scipy import constants as sc

getcontext().prec=110
class IndependentDecimal:
    """Extra internal precision; 80-digit results from an explicit erf series."""
    mpf=Decimal
    pi=Decimal('3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651')
    @staticmethod
    def sqrt(x):return Decimal(x).sqrt()
    @staticmethod
    def exp(x):return Decimal(x).exp()
    @staticmethod
    def fsum(values):return sum(values,Decimal(0))
    @staticmethod
    def nstr(x,n):return format(x,'.'+str(n)+'g')
    @staticmethod
    def erf(x):
        raw=x;total=x;n=0
        while True:
            n+=1;raw*=-(x*x)/n;term=raw/(2*n+1);total+=term
            # Selected energies have x<3.5; after the terms decrease,
            # this alternating remainder is bounded by the next term.
            if n>x*x and abs(term)<Decimal('1e-100'):break
            if n>2000:raise RuntimeError('independent erf series did not converge')
        return 2*total/IndependentDecimal.pi.sqrt()
mp=IndependentDecimal

BASE = pathlib.Path(__file__).resolve().parents[2]
WORKSPACE = BASE.parent
RUN = BASE / 'runs/c23d_source_ee_20261023T220714Z_v1'
SOURCE = WORKSPACE / 'n4_resume_transport_20261024/verified_restore/main/repository/research/cr_c23c_stopping_coverage_20261023/inputs/photoelectron_atoms.csv'
OUT = pathlib.Path(__file__).parent / 'C23D_C9_reference_run_v1'
OUT.mkdir()
def write(name, value):
    with (OUT / name).open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')

before = sorted(os.sched_getaffinity(0))
observed = {'affinity_before': before, 'cpu_max': pathlib.Path('/sys/fs/cgroup/cpu.max').read_text().strip(), 'memory_max': pathlib.Path('/sys/fs/cgroup/memory.max').read_text().strip(), 'active_task_lease': (BASE / 'runtime/ACTIVE_LOCAL_LEASE.json').exists(), 'reviewer_cpu': 1, 'protected_coordinator_cpu': 8, 'cpu55': 'ABSENT_UNTOUCHED', 'external_lease': 'UNOBSERVED', 'native_threads': 1, 'cpu_limit_s': 20, 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
processes=[]
for p in pathlib.Path('/proc').iterdir():
    if p.name.isdigit():
        try:
            argv=(p/'cmdline').read_bytes().split(b'\0')
            if any(x.endswith(b'/run_bridge.py') or x.endswith(b'/dispatch.py') for x in argv):
                processes.append({'pid': int(p.name), 'argv': [x.decode(errors='replace') for x in argv if x]})
        except OSError:
            pass
observed['active_science_processes'] = processes
assert 1 in before and 8 in before
os.sched_setaffinity(0, {1})
resource.setrlimit(resource.RLIMIT_CPU, (20,21))
lease = pathlib.Path(__file__).parent / 'C23D_C9_ACTIVE_LEASE.json'
with lease.open('x') as f:
    json.dump({'pid':os.getpid(),'output':str(OUT),'cpu':1,'native_threads':1},f)
write('RESOURCE_ADMISSION.json',observed)
start=time.perf_counter(); cpu=time.process_time()
try:
    M=mp.mpf
    constants={key:str(getattr(sc,key)) for key in ['e','epsilon_0','m_e','k','c','h']}
    e,eps,m,k,c,h=(M(constants[key]) for key in ['e','epsilon_0','m_e','k','c','h'])
    ne=M('.14')*10**6; T=M('10000'); L=M('20'); theta=k*T/e
    # Independent SI derivation, rather than calling the anchor or provider.
    speed=mp.sqrt(2*k*T/m)
    gamma=ne*L*e**4/(4*mp.pi*eps**2*m**2)
    nu=gamma/speed**3
    b=m*gamma/(e*speed)
    calculated={'theta_eV':theta,'Gamma_SI':gamma,'v_theta_m_s':speed,'tau_per_s':nu,'loss_anchor_eV_s':b}
    production=json.loads((RUN/'APPLICABILITY.json').read_text())
    comparisons=[]
    tolerance=M('2e-12')
    def compare(label,reference,actual):
        err=abs(M(str(actual))-reference)/max(abs(reference),M('1e-100'))
        comparisons.append({'label':label,'reference_80digit':mp.nstr(reference,82),'observed_fp64':actual,'relative_error':float(err),'tolerance':float(tolerance),'pass':bool(err<=tolerance)})
    for key,val in calculated.items():compare('anchor.'+key,val,production['anchor'][key])
    raw=SOURCE.read_bytes()
    assert len(raw)==1681578 and hashlib.sha256(raw).hexdigest()=='f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3'
    rows=list(csv.DictReader(raw.decode().splitlines()))
    density={'HI':M('.9'),'HeI':M('.07'),'HeII':M('.02')}
    cache={}
    def coefficients(w):
        if w not in cache:
            x=mp.sqrt(w/theta); derivative=2/mp.sqrt(mp.pi)*mp.exp(-x*x)
            phi=mp.erf(x)-x*derivative
            cold=b*mp.sqrt(theta/w)
            a=cold*(2*x*derivative-mp.erf(x))
            diffusion=theta*cold*phi
            cache[w]=(a,diffusion)
        return cache[w]
    derived=[]
    for epoch in production['epochs']:
        z=epoch['redshift'];group=[r for r in rows if r['redshift']==z]
        allrows=[(r['channel'],M(r['kinetic_eV']),M(r['number_weight_per_target_s'])) for r in group]
        selected=[(channel,w,q) for channel,w,q in allrows if 0<w<10]
        alln=mp.fsum(density[ch]*q for ch,w,q in allrows)
        allu=mp.fsum(density[ch]*q*w for ch,w,q in allrows)
        ns=mp.fsum(density[ch]*q for ch,w,q in selected)
        us=mp.fsum(density[ch]*q*w for ch,w,q in selected)
        drift=mp.fsum(density[ch]*q*coefficients(w)[0] for ch,w,q in selected)
        up=mp.fsum(density[ch]*q for ch,w,q in selected if coefficients(w)[0]>0)/ns
        values={'source_all_count_cm3_s':alln,'source_all_energy_eV_cm3_s':allu,'selected_count_source_cm3_s':ns,'selected_energy_source_eV_cm3_s':us,'selected_count_fraction':ns/alln,'selected_energy_fraction':us/allu,'count_diluteness_ratio':10**4*ns/M('.14'),'energy_diluteness_ratio':10**4*us/(M('1.5')*M('.14')*theta),'upward_drift_count_fraction':up,'source_weighted_drift_eV_cm3_s2':drift,'pulse_bath_initial_heat_rate_eV_cm3_s':-10**4*drift}
        for key,val in values.items():compare(z+'.'+key,val,epoch[key])
        actual_atoms=list(csv.DictReader((RUN/('ATOMS_'+z+'.csv')).open()))
        assert len(actual_atoms)==len(selected)
        for index in [0,len(selected)//2,len(selected)-1]:
            channel,w,q=selected[index];actual=actual_atoms[index]
            assert channel==actual['channel']
            a,d=coefficients(w)
            compare(z+'.atom'+str(index)+'.drift',a,float(actual['signed_drift_eV_s']))
            compare(z+'.atom'+str(index)+'.diffusion',d,float(actual['diffusion_eV2_s']))
        derived.append({'redshift':z,'all_rows':len(allrows),'selected_rows':len(selected),'mean_selected_energy_eV':mp.nstr(us/ns,82),'selected_pulse_count_cm3':mp.nstr(ns*10**4,82)})
    # Read-only contraction of NEW saved output; no population evolution replay.
    output_checks=[]
    for f in sorted(RUN.glob('EVOLUTION_*.json')):
        d=json.loads(f.read_text());E=list(map(lambda x:M(str(x)),d['centres_eV']));N0=list(map(lambda x:M(str(x)),d['initial_counts_cm3']));Nf=list(map(lambda x:M(str(x)),d['final_counts_cm3']))
        n0=mp.fsum(N0);nf=mp.fsum(Nf);u0=mp.fsum(a*b for a,b in zip(E,N0));uf=mp.fsum(a*b for a,b in zip(E,Nf))
        samples=d['samples'];loss=u0-uf
        output_checks.append({'file':f.name,'initial_count':mp.nstr(n0,82),'final_count':mp.nstr(nf,82),'relative_count_drift':float(abs(nf-n0)/n0),'final_mean_eV':mp.nstr(uf/nf,82),'final_mean_relative_error':float(abs(uf/nf-M(str(samples[-1]['mean_energy_eV'])))/(uf/nf)),'bath_change_relative_error':float(abs(loss-M(str(samples[-1]['opposite_bath_energy_change_eV_cm3'])))/abs(loss)),'nonnegative_final':all(x>=0 for x in Nf)})
    passed=all(x['pass'] for x in comparisons) and all(x['relative_count_drift']<=1e-9 and x['final_mean_relative_error']<=2e-12 and x['bath_change_relative_error']<=2e-12 and x['nonnegative_final'] for x in output_checks)
    write('RESULT.json',{'status':'PASS_SCOPED' if passed else 'FAIL_SCOPED','precision_decimal_digits':80,'internal_decimal_precision':110,'constant_binding':'Exact decimal renderings of scipy.constants values used by production. High arithmetic precision is not physical-constant accuracy.','constants':constants,'source_sha256':hashlib.sha256(raw).hexdigest(),'reference_method':'Decimal exp/sqrt and explicit convergent erf series, direct SI formula, independent raw CSV sums; no production numerical provider import','comparison_count':len(comparisons),'max_relative_error':max(x['relative_error'] for x in comparisons),'comparisons':comparisons,'derived':derived,'saved_output_contractions':output_checks,'new_population_integrations':0,'old_science_replayed':0,'wall_s':time.perf_counter()-start,'cpu_s':time.process_time()-cpu,'maxrss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'affinity':sorted(os.sched_getaffinity(0)),'native_threads':1})
    print(json.dumps({'pass':passed,'comparisons':len(comparisons),'max_relative_error':max(x['relative_error'] for x in comparisons),'cpu_s':time.process_time()-cpu}))
    if not passed:sys.exit(2)
finally:
    lease.unlink()
    write('LEASE_RELEASED.json',{'released':True,'pid':os.getpid(),'cpu':1})
