"""Independent C9: exact-binary64-input Decimal banded solves, no producer import."""
import argparse, bisect, csv, gzip, hashlib, json, math, os, resource, time
from decimal import Decimal as D, localcontext
from pathlib import Path
import numpy as np

def exact(x):
    return D.from_float(float(x))

def rel(a, b):
    if b == 0:
        return D(0) if a == 0 else D('Infinity')
    return abs(a-b)/abs(b)

def jwrite(p, obj):
    with Path(p).open('x') as f:
        json.dump(obj, f, indent=2, allow_nan=False); f.write('\n')

def fact(diag, lower, upper):
    piv = list(diag); multipliers = []
    for i in range(1, len(piv)):
        assert piv[i-1] > 0
        m = lower[i-1]/piv[i-1]
        multipliers.append(m); piv[i] -= m*upper[i-1]
    assert piv[-1] > 0
    return piv, multipliers, upper

def solve(factor, rhs):
    piv, multipliers, upper = factor; y = list(rhs)
    for i in range(1, len(y)): y[i] -= multipliers[i-1]*y[i-1]
    x = [D(0)]*len(y); x[-1] = y[-1]/piv[-1]
    for i in range(len(y)-2, -1, -1): x[i] = (y[i]-upper[i]*x[i+1])/piv[i]
    return x

def dot(a,b):
    return sum((x*y for x,y in zip(a,b)), D(0))

def native_curve(unit, channel):
    path = unit/'inputs/reused/phys83/source_data'/('CCC_'+channel+'.1S')
    lines = path.read_text().splitlines()
    assert ('1S -> '+channel+';') in ' '.join(lines[0].split())
    assert 'a0^2' in lines[0]
    rows = [line.split() for line in lines if line.strip() and not line.lstrip().startswith('#')]
    nodes = [float(row[0]) for row in rows]; sig = [float(row[1]) for row in rows]
    assert len(nodes)==452 and nodes[0]==10.20435 and sig[0]==0 and nodes[-1]==968.6058
    # Exact same represented source-array convention, read from pinned provider source.
    # This is independent arithmetic on raw tables, not a provider constructor/evaluate call.
    area = (100.0*5.29177210544e-11)**2
    flux = [e*(s*area) for e,s in zip(nodes,sig)]
    return nodes, flux

def hazard_reference(energies, curve):
    nodes, flux = curve
    constant = exact(.9)*100*(2*exact(1.602176634e-19)/exact(9.1093837139e-31)).sqrt()
    values=[]
    for e in energies:
        if e <= nodes[0]: values.append(D(0)); continue
        assert e <= nodes[-1]
        i = min(bisect.bisect_right(nodes,float(e))-1,len(nodes)-2)
        w = exact(flux[i])+(exact(flux[i+1])-exact(flux[i]))*(exact(e)-exact(nodes[i]))/(exact(nodes[i+1])-exact(nodes[i]))
        values.append(constant*w/exact(e).sqrt())
    return values

def source_reference(unit, z, energies):
    with (unit/f'inputs/reused/c23d/ATOMS_{z}.csv').open(newline='') as f: rows=list(csv.DictReader(f))
    ws=[float(r['W_eV']) for r in rows]; ms=[float(r['pulse_count_cm3']) for r in rows]
    assert len(ws)==384 and all(0<w<10 for w in ws) and all(m>=0 for m in ms)
    p=[D(0)]*len(energies); mask=[]; active=D(0); selected=sum(map(exact,ms),D(0)); energy=D(0)
    for w,m in zip(ws,ms):
        yes=w>energies[0]; mask.append(yes)
        if not yes: continue
        active+=exact(m);energy+=exact(m)*exact(w)
        right=min(bisect.bisect_right(energies,w),len(energies)-1); left=right-1
        t=(exact(w)-exact(energies[left]))/(exact(energies[right])-exact(energies[left]))
        assert 0<=t<=1
        p[left]+=exact(m)*(1-t);p[right]+=exact(m)*t
    return p,mask,active,selected,energy

def run(unit,primary,out):
    start=time.process_time(); summaries=[]; details=[]; counts={'factorizations':0,'direct_probability_solves':0,'energy_reward_solves':0,'time_reward_solves':0,'adjoint_source_solves':0,'provider_imports':0,'provider_constructors':0,'ODE':0,'source_quadrature':0,'rate_quadrature':0}
    prod=json.loads((primary/'SOURCE_WEIGHTED_RESULTS.json').read_text()); curves={c:native_curve(unit,c) for c in ['2S','2P']}
    for chi in [1.5,3.0]:
        stem=f'chi{chi:g}_R80_N2048'
        with np.load(primary/(stem+'.npz'),allow_pickle=False) as f: raw={k:f[k].copy() for k in f.files}
        E=raw['E_eV'].tolist(); n=len(E)-1
        assert all(E[i]<E[i+1] for i in range(n)) and all(k in E for k in [chi*.8617333262145178,10.,10.20435,40*.8617333262145178,80*.8617333262145178])
        assert np.array_equal(raw['G_diag'],raw['Q_diag'][1:])
        assert np.array_equal(raw['G_lower'],raw['Q_upper'][1:])
        assert np.array_equal(raw['G_upper'],raw['Q_lower'][1:])
        assert raw['absorption'][0]==raw['Q_upper'][0] and np.all(raw['absorption'][1:]==0)
        assert np.array_equal(raw['K_diag'],raw['hazard_2S_s_inv']+raw['hazard_2P_s_inv']-raw['G_diag'])
        assert np.array_equal(raw['K_lower'],-raw['G_lower']) and np.array_equal(raw['K_upper'],-raw['G_upper'])
        d=list(map(exact,raw['K_diag']));lo=list(map(exact,raw['K_lower']));up=list(map(exact,raw['K_upper']))
        kf=fact(d,lo,up);kt=fact(d,up,lo);counts['factorizations']+=2
        h={c:list(map(exact,raw['hazard_'+c+'_s_inv'])) for c in ['2S','2P']}
        u={c:solve(kf,h[c]) for c in h}; counts['direct_probability_solves']+=2
        er={c:solve(kf,list(map(exact,raw['rhs'][:,4+i]))) for i,c in enumerate(h)};counts['energy_reward_solves']+=2
        vt={c:solve(kf,u[c]) for c in h};counts['time_reward_solves']+=2
        herrors={}
        for c in h:
            href=hazard_reference(E[1:],curves[c]);err=max(rel(a,b) for a,b in zip(h[c],href));herrors[c]=str(err);assert err<=D('5e-13'),('hazard',chi,c,str(err))
        qlo,qhi,qdiag=raw['Q_lower'],raw['Q_upper'],raw['Q_diag']
        conserved=[]
        for i in range(len(E)):
            entries=[exact(qdiag[i])]
            if i>0:entries.append(exact(qhi[i-1]))
            if i<len(E)-1:entries.append(exact(qlo[i]))
            conserved.append(abs(sum(entries))/sum(map(abs,entries)))
        assert max(conserved)<=D('2e-13')
        arrays={'precision_decimal_digits':80,'binary64_conversion':'Decimal.from_float','u_2S':list(map(str,u['2S'])),'u_2P':list(map(str,u['2P'])),'r_2S':list(map(str,er['2S'])),'r_2P':list(map(str,er['2P'])),'v_2S':list(map(str,vt['2S'])),'v_2P':list(map(str,vt['2P'])),'adjoint_sources':{},'independent_projected_sources':{}}
        case_details={'case':stem,'nodes':len(E),'hazard_relative_error':herrors,'exact_saved_column_conservation_scaled_max':str(max(conserved)),'sources':[]}
        for z in ['2.316','2.479','2.649']:
            row=next(r for r in prod if (r['chi'],r['R'],r['N'],r['z'])==(chi,80,2048,z)); info=row['projection']; saved=raw['source_'+z]
            sp=list(map(exact,saved));q,mask,active_exact,selected_exact,source_energy=source_reference(unit,z,E)
            assert np.array_equal(raw['active_mask_'+z],np.array(mask,dtype=bool))
            projection_l1=sum(abs(a-b) for a,b in zip(sp,q))/active_exact
            assert projection_l1<=D('2e-12')
            assert rel(exact(info['original_active_count_cm3']),active_exact)<=D('2e-12') and rel(exact(info['selected_count_cm3']),selected_exact)<=D('2e-12')
            assert sum(sp[i] for i,e in enumerate(E) if e>10)==0
            assert sum(sp[i+1] for i in range(n) if h['2S'][i]+h['2P'][i]>0)==0
            assert rel(dot(sp,list(map(exact,E))),source_energy)<=D('2e-12')
            pop=sp[1:]; adj=solve(kt,pop);counts['adjoint_source_solves']+=1
            arrays['adjoint_sources'][z]=list(map(str,adj));arrays['independent_projected_sources'][z]=list(map(str,q))
            da=exact(info['original_active_count_cm3']); ds=exact(info['selected_count_cm3'])
            case_details['sources'].append({'z':z,'projection_L1_relative_error':str(projection_l1),'boundary_mass_fraction_from_exact_inputs':str(q[0]/active_exact),'original_active_fraction_from_exact_inputs':str(active_exact/selected_exact)})
            for c in ['2S','2P','sum']:
                if c=='sum':
                    uc=[a+b for a,b in zip(u['2S'],u['2P'])];hc=[a+b for a,b in zip(h['2S'],h['2P'])];ec=[a+b for a,b in zip(er['2S'],er['2P'])];tc=[a+b for a,b in zip(vt['2S'],vt['2P'])]
                else:uc,hc,ec,tc=u[c],h[c],er[c],vt[c]
                num=dot(pop,uc);adjnum=dot(adj,hc);assert num>0
                pa=num/da;ps=num/ds;meanE=dot(pop,ec)/num;meanT=dot(pop,tc)/num
                refs={'P_active':pa,'P_selected':ps,'conditional_incoming_eV':meanE,'conditional_event_time_s':meanT}
                errors={k:rel(exact(row['values'][c][k]),v) for k,v in refs.items()}
                assert all(v<=D('5e-10') for v in errors.values()),('reference',chi,z,c,{k:str(v) for k,v in errors.items()})
                erradj=rel(adjnum,num);assert erradj<=D('1e-60')
                summaries.append({'chi':chi,'R':80,'N':2048,'z':z,'channel':c,'reference':{k:str(v) for k,v in refs.items()},'relative_errors':{k:str(v) for k,v in errors.items()},'direct_adjoint_relative_error':str(erradj),'pass':True})
        ap=out/(stem+'_DECIMAL_ARRAYS.json.gz')
        with ap.open('xb') as fh:
            with gzip.GzipFile(fileobj=fh,mode='wb',mtime=0) as gz:gz.write(json.dumps(arrays,separators=(',',':')).encode())
        case_details['saved_reference_arrays']={'path':ap.name,'bytes':ap.stat().st_size,'sha256':hashlib.sha256(ap.read_bytes()).hexdigest()};details.append(case_details)
    diagnostics=[];knotdetails=[];grid_identity_checks=[]
    baseline=unit/'runs/n5_ce_resolvent_recovery_primary_20261024_v2'
    for chi in [1.5,3.0]:
        for z in ['2.316','2.479','2.649']:
            for c in ['2S','2P','sum']:
                rr=[next(r for r in prod if (r['chi'],r['R'],r['N'],r['z'])==(chi,80,N,z)) for N in [1024,2048]]
                vals=[r['values'][c]['P_active'] for r in rr]
                diagnostics.append({'chi':chi,'z':z,'channel':c,'N':[1024,2048],'P_active':vals,'relative_change':abs(vals[1]-vals[0])/max(map(abs,vals)),'boundary_active_fractions':[r['projection']['boundary_active_fraction'] for r in rr],'meaning':'Native-knot finite comparison only; no continuum order inferred from two grids'})
        for N in [1024,2048]:
            for band in [40,80]:
                filename=f'chi{chi:g}_R{band}_N{N}.npz'
                with np.load(primary/filename,allow_pickle=False) as f, np.load(baseline/filename,allow_pickle=False) as old:
                    ee=f['E_eV'];oe=old['E_eV'];knots=[v for curve in curves.values() for v in curve[0] if oe[0]<=v<=oe[-1]]
                    expected=np.array(sorted(set(oe.tolist()+knots)),dtype=float)
                    assert np.array_equal(ee,expected),('native_union_mismatch',filename)
                    assert np.array_equal(ee[ee<=10],oe[oe<=10]),('sub10_grid_changed',filename)
                    for z in ['2.316','2.479','2.649']:
                        assert np.array_equal(f['source_'+z][ee<=10],old['source_'+z][oe<=10]),('sub10_projection_changed',filename,z)
                    grid_identity_checks.append({'case':filename,'old_nodes':len(oe),'new_nodes':len(ee),'exact_native_union':True,'below10_grid_and_source_unchanged':True,'minimum_spacing_eV':float(np.diff(ee).min())})
                    if band==80:
                        e=ee.tolist();i=e.index(10.20435);knotdetails.append({'chi':chi,'N':N,'nodes_near_threshold':e[i-2:i+3],'left_gap':e[i]-e[i-1],'right_gap':e[i+1]-e[i],'native_first_source_gap_eV':10.2043885-10.20435})
    comparisons=json.loads((primary/'FINITE_COMPARISONS.json').read_text());failed=[r for r in comparisons if not r['pass']]
    result={'schema':'N5_CE_RESOLVENT_INDEPENDENT_DECIMAL_REFERENCE_NATIVE_V3','status':'PASS_FINITE_CHAIN_ARITHMETIC_GRID_GATE_OPEN' if failed else 'PASS_FINITE_CHAIN_ARITHMETIC','primary_run_id':primary.name,'precision':80,'conversion':'Decimal.from_float for every saved binary64 matrix/source/hazard value; no Decimal(str(float)) conversion','rows':summaries,'case_details':details,'grid_diagnostics_from_saved_results':diagnostics,'threshold_grid_diagnostics':knotdetails,'native_union_identity_checks':grid_identity_checks,'producer_failed_frozen_comparisons':failed,'frozen_grid_gate':'OPEN_FAILED' if failed else 'PASS','counts':counts,'runtime':{'worker_affinity':sorted(os.sched_getaffinity(0)),'native_thread_env':{k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']},'AS_limit':resource.getrlimit(resource.RLIMIT_AS),'CPU_limit':resource.getrlimit(resource.RLIMIT_CPU),'process_CPU_s':time.process_time()-start,'peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},'science_scope':'Independent reference on conditioned exact saved binary64 finite matrices; not certified continuum or provider-physical-error result','old_science_replay':0}
    jwrite(out/'REFERENCE_RESULT.json',result)
    print(json.dumps({'status':result['status'],'rows':len(summaries),'counts':counts,'grid_failures':len(failed),'max_relative_error':str(max(D(v) for row in summaries for v in row['relative_errors'].values())),'process_CPU_s':result['runtime']['process_CPU_s']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--primary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    with localcontext() as context:
        context.prec=80
        run(a.unit,a.primary,a.output)
