"""80-digit direct rest-angle integration of source-table interpolation."""
from pathlib import Path
import bisect,json,math,os,resource,sys,time
BASE=Path(__file__).resolve().parent
RUN=Path(sys.argv[1]).resolve()
if os.sched_getaffinity(0)!={4}:raise RuntimeError('Assigned reviewer CPU4 required')
THREADS=('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')
if any(os.environ.get(k)!='1' for k in THREADS):raise RuntimeError('Native threads must be1')
sys.path.insert(0,str(RUN/'source_snapshot'))
from boost_kernel import Boost,ElectronMeasure,ELECTRON_REST_EV
from boosted_deposition import prepare_boosted
from vendor.fs2010_operator import FS2010Response,CONTRACTED_COLUMNS
from independent_reference import reference
import mpmath as mp
mp.mp.dps=80
START=time.perf_counter()
def save(name,value):
    with (RUN/name).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')

# Separate table reader: the reference adopts the same stored FP64 numeric
# values but does not call the producer bracket/blend/interval/basis code.
table_dir=RUN/'source_snapshot/vendor/21cmFAST/tables'
entries=[(.1,'log_xi_-1.0.dat'),(.5,'xi_0.500.dat'),(.9,'xi_0.900.dat'),(.99,'xi_0.990.dat'),(.999,'xi_0.999.dat')]
igrid=[mp.mpf(x) for x,_ in entries]
tables=[]
for _,name in entries:
    rows=[[mp.mpf(float(x)) for x in line.split()] for line in (table_dir/name).read_text().splitlines()[3:] if line.strip()]
    tables.append(rows)
grid=[row[0] for row in tables[0]]

def reference_response(energies,weights,u_float,xi_float):
    xi=mp.mpf(xi_float)
    i=min(len(igrid)-2,max(0,bisect.bisect_right(igrid,xi)-1))
    tx=(xi-igrid[i])/(igrid[i+1]-igrid[i])
    nodes=[[(1-tx)*tables[i][j][c+1]+tx*tables[i+1][j][c+1] for c in range(7)] for j in range(len(grid))]
    out=[mp.mpf(0)]*7
    u=mp.mpf(u_float);m=mp.mpf(ELECTRON_REST_EV);g=mp.sqrt(1+u*u)
    for k_float,w_float in zip(energies,weights):
        k=mp.mpf(k_float);weight=mp.mpf(w_float);q=mp.sqrt(k*(k+2*m))
        a=g*(k+m)-m;b=u*q
        if not u or not k:
            if not grid[0]<=a<=grid[-1]:continue
            j=min(len(grid)-2,max(0,bisect.bisect_right(grid,a)-1))
            t=(a-grid[j])/(grid[j+1]-grid[j])
            for c in range(7):out[c]+=weight*((1-t)*nodes[j][c]+t*nodes[j+1][c])*(a if c<3 else 1)
            continue
        for j,(left,right) in enumerate(zip(grid[:-1],grid[1:])):
            low=max(mp.mpf(-1),(left-a)/b);high=min(mp.mpf(1),(right-a)/b)
            if high<=low:continue
            half=(high-low)/2;mid=(high+low)/2
            for mu in (mid-half/mp.sqrt(3),mid+half/mp.sqrt(3)):
                energy=g*(k+m)+u*q*mu-m
                t=(energy-left)/(right-left)
                vals=[(1-t)*nodes[j][c]+t*nodes[j+1][c] for c in range(7)]
                for c in range(7):out[c]+=weight*half/2*vals[c]*(energy if c<3 else 1)
    partition={key:[mp.mpf(0)]*4 for key in ('below','covered','above','all')}
    for k,w in zip(energies,weights):
        for key,lo,hi,lc,uc in [('below',0.,float(grid[0]),True,False),('covered',float(grid[0]),float(grid[-1]),True,True),('above',float(grid[-1]),math.inf,False,False),('all',0.,math.inf,True,False)]:
            r=reference(k,u_float,ELECTRON_REST_EV,lo,hi,lower_closed=lc,upper_closed=uc)
            partition[key]=[a+mp.mpf(w)*b for a,b in zip(partition[key],r)]
    return out,partition

matched=.1*(.1/(math.hypot(1,.1)+1))*ELECTRON_REST_EV
cases=[
    ('lower_knot_dirac',(10.,),(1.,),0.),
    ('upper_knot_dirac',(9937.21,),(1.,),0.),
    ('zero_rest_energy',(0.,),(1.,),.01),
    ('tiny_u_table_knots',(10.,100.,9937.21),(.2,.3,.5),1e-12),
    ('finite_box_both_domain_and_high',(5690.,),(1.,),.1),
    ('matched_speed_three_way',(matched,),(1.,),.1),
    ('neutron_energy_atom',(301370.,),(1.,),1.),
    ('finite_mixture_unboosted',(0.,10.,18590.,301370.),(.1,.2,.3,.4),0.),
    ('entire_high_tail',(1e9,),(1.,),1e3),
]
response=FS2010Response(table_dir,axis='unambiguous_high_ionization')
records=[];maxerr=mp.mpf(0);basis_max=mp.mpf(0);partition_max=mp.mpf(0);failed=[]
for name,ks,ws,u in cases:
    source=ElectronMeasure(tuple(ks),tuple(ws),'parent_rest','electrons_per_event','C23B_REVIEW_'+name)
    prepared=prepare_boosted(response,source,Boost(u))
    for xi in (.1,.37,.9):
        got=prepared.at(xi);expected,parts=reference_response(ks,ws,u,xi)
        channel_errors=[abs(mp.mpf(got[col])-ex)/max(mp.mpf('1e-30'),abs(ex)) for col,ex in zip(CONTRACTED_COLUMNS,expected)]
        maxerr=max(maxerr,*channel_errors)
        basis_errors=[abs(mp.mpf(math.fsum(prepared.number_basis))-parts['covered'][0])/max(mp.mpf(1),parts['all'][0]),abs(mp.mpf(math.fsum(prepared.energy_basis))-parts['covered'][1])/max(mp.mpf(1),parts['all'][1])]
        basis_max=max(basis_max,*basis_errors)
        p_errors=[]
        for key in parts:
            for c,actual in enumerate(prepared.partition[key].as_tuple()):
                scale=max(mp.mpf(1),abs(parts['all'][c])) if c<3 else max(mp.mpf(1),parts['all'][2])
                p_errors.append(abs(mp.mpf(actual)-parts[key][c])/scale)
        partition_max=max(partition_max,*p_errors)
        defect=parts['covered'][1]-sum(expected[:3])
        defect_error=abs(mp.mpf(got['reported_energy_defect'])-defect)/max(mp.mpf(1),parts['covered'][1])
        positive_basis=all(v>=0 for v in prepared.number_basis+prepared.energy_basis)
        null_tails=got['unresolved_tail_heat'] is None and got['unresolved_tail_ionization'] is None
        ok=max(channel_errors+basis_errors+p_errors+[defect_error])<=mp.mpf('2e-12') and positive_basis and null_tails
        row={'case':name,'K_eV':ks,'weights':ws,'u':u,'xi':xi,'channel_reference80':{col:mp.nstr(val,83) for col,val in zip(CONTRACTED_COLUMNS,expected)},'channel_values':{col:got[col] for col in CONTRACTED_COLUMNS},'channel_relative_errors':[float(x) for x in channel_errors],'basis_number_energy_scaled_errors':[float(x) for x in basis_errors],'maximum_partition_scaled_error':float(max(p_errors)),'raw_energy_defect_actual':got['reported_energy_defect'],'raw_energy_defect_reference80':mp.nstr(defect,83),'raw_defect_energy_scaled_error':float(defect_error),'basis_positive':positive_basis,'unresolved_deposition_tails_null':null_tails,'result':'PASS' if ok else 'FAIL'}
        records.append(row)
        if not ok:failed.append(row)
save('DIRECT_ANGULAR_DEPOSITION_CHECKS.json',records)
result={'schema':'C23B_INDEPENDENT_DEPOSITION_REVIEW_V1','status':'PASS_SCOPED' if not failed else 'FAIL','spectral_cases':len(cases),'xi_queries':[.1,.37,.9],'query_count':len(records),'channels_per_query':7,'channel_comparisons':len(records)*7,'failed_queries':len(failed),'failure_examples':failed[:4],'maximum_channel_relative_error':float(maxerr),'maximum_basis_scaled_error':float(basis_max),'maximum_partition_scaled_error':float(partition_max),'all_basis_nonnegative':all(x['basis_positive'] for x in records),'unresolved_tail_outputs_preserved_null':all(x['unresolved_deposition_tails_null'] for x in records),'max_raw_defect_energy_scaled_error':max(x['raw_defect_energy_scaled_error'] for x in records),'method':'Independent table parser +80digit xi interpolation +direct rest-cosine clipping per energy cell +two-node Gauss integration; no producerAngularBox/bracket/blend/Bernstein basis used by reference','scope':'finite interpolant+positive discrete rest spectrum+declared boost; physical FS gas applicability and radiation closure unchanged','tolerance':2e-12,'global_error_bound':None,'new_ODE_calls':0,'historical_ODE_calls':0,'worker_cpu':4,'native_threads_per_worker':1,'wall_s':time.perf_counter()-START,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'EXECUTION':'COMPLETE_SCOPED_NEW_DEPOSITION_REVIEW','PUBLICATION':'PARENT_PENDING','BACKUP':'PARENT_PENDING','DAG':'closed boost/clock suite reused; new deposition contraction independently checked; physical source coupling awaits provider contract'}
save('COMPLETE.json',result)
print(json.dumps({k:v for k,v in result.items() if k!='failure_examples'}))
