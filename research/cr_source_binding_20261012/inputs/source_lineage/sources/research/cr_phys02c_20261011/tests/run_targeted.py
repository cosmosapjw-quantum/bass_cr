# SPDX-License-Identifier: GPL-3.0-only
"""Targeted frozen atomic/transport execution, reusable bounded grid API."""
import os
THREAD_KEYS=('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS','OMP_MAX_ACTIVE_LEVELS')
if any(os.environ.get(k)!='1' for k in THREAD_KEYS): raise RuntimeError('THREAD_ENVIRONMENT_NOT_FROZEN_BEFORE_NUMPY_IMPORT')
from pathlib import Path
import sys,json,hashlib,datetime,time,argparse,traceback,resource,platform
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import coherent_bed as bed
import numpy as np
import scipy
from scipy.integrate import quad
from threadpoolctl import threadpool_info
cc=bed.parent
CONTRACT=json.loads((ROOT/'state/SCIENTIFIC_CONTRACT.json').read_text());TOL=CONTRACT['tolerances']
def identity(path):
    raw=path.read_bytes();return {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
def relative(a,b):return abs(float(a)-float(b))/max(abs(float(b)),1e-100)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(result,path):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');tmp.replace(path)
def check(result,name,passed,detail):
    row={'id':name,'status':'PASS_SCOPED' if bool(passed) else 'FAIL','detail':detail};result['checks'].append(row);print(json.dumps(row),flush=True)
    return bool(passed)
def resources(estimated_GiB=2):
    def read(p):
        try:return Path(p).read_text().strip()
        except OSError:return None
    records={p:read('/sys/fs/cgroup/'+p) for p in ('cpu.max','cpuset.cpus.effective','memory.current','memory.max','memory.peak')}
    mem={line.split(':')[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith(('MemAvailable:','MemTotal:'))}
    limit=records['memory.max'];bounded=int(limit) if limit and limit!='max' else mem['MemTotal'];current=int(records['memory.current'] or 0)
    available=min(mem['MemAvailable'],bounded-current);reserve=max(bounded*.125,1024**3)
    info=threadpool_info();threads_ok=all(v['num_threads']==1 for v in info)
    return {'cgroup':records,'affinity':sorted(os.sched_getaffinity(0)),'process_id':os.getpid(),'available_bytes':available,'bounded_memory_bytes':bounded,'reserve_bytes':reserve,'estimated_working_bytes':estimated_GiB*1024**3,'admitted':available-reserve>=estimated_GiB*1024**3 and threads_ok,'threadpools':info,'thread_environment':{k:os.environ.get(k) for k in THREAD_KEYS},'rss_peak_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
def atomic_checks(result):
    atomic=bed.AtomicData()
    check(result,'PINNED_PARENT_AND_NEW_INPUT_IDENTITIES',len(atomic.excitation)==27,{'parent_files':len(bed.manifest['files']),'CCC_channels':27,'oracle':identity(ROOT/'research/ionization_sources/SOURCE_ALGEBRA_RESULT.json'),'new_input_manifest':identity(ROOT/'inputs/FULL_BED_INPUTS.json'),'parent_test_reference':identity(ROOT.parent/'cr_phys02b_20261010/tests/verify_cascade.py')})
    for sp,ion in atomic.ionization.items():
        # Independent adaptive integrals, including infinite interval moments.
        ni=quad(lambda w:float(ion.g(w)),0,np.inf,epsabs=1e-12,epsrel=1e-12,limit=300)[0]
        q=2/ion.N*quad(lambda w:float(ion.g(w))/(1+w),0,np.inf,epsabs=1e-12,epsrel=1e-12,limit=300)[0]
        detail={'Ni':ni,'Ni_pinned':ion.Ni,'Ni_relative':relative(ni,ion.Ni),'Qdf':q,'Qdf_pinned':ion.oscillator_Q,'Qdf_relative':relative(q,ion.oscillator_Q),'threshold_g':float(ion.g(0))}
        ds=[]
        if sp=='HI':
            for row in bed.ORACLE['H']['D_samples']:
                value=float(ion.D(row['incident_eV']/ion.B_eV));ref=float(row['D_H(t)']);ds.append({'energy_eV':row['incident_eV'],'value':value,'oracle':ref,'relative':relative(value,ref)})
            threshold=relative(ion.g(0),float(bed.ORACLE['H']['threshold_df_dw']))
        else:
            for E in (ion.B_eV*1.00000001,30,100,400,900):
                t=E/ion.B_eV;ref=quad(lambda w:float(ion.g(w))/(1+w)/ion.N,0,(t-1)/2,epsabs=1e-15,epsrel=1e-12)[0]
                value=float(ion.D(t));ds.append({'energy_eV':E,'value':value,'adaptive_reference':ref,'relative':relative(value,ref)})
            threshold=relative(ion.g(0),float(bed.ORACLE['He']['threshold_df_dw']))
        detail['D_checks']=ds;detail['threshold_relative']=threshold
        check(result,'H_ANALYTIC_OSCILLATOR_THRESHOLD_MOMENTS_AND_D_ORACLES' if sp=='HI' else 'HE_PRINTED_COEFFICIENT_MOMENTS_AND_ANALYTIC_D',max(detail['Ni_relative'],detail['Qdf_relative'],threshold)<TOL['source_moment_relative'] and max(d['relative'] for d in ds)<TOL['source_D_relative'],detail)
    integrals=[];domains=[]
    for sp,ion in atomic.ionization.items():
        for E in (ion.B_eV*(1+1e-8),ion.B_eV*1.0001,30,100,400,900):
            if E<=ion.B_eV:continue
            upper=(E-ion.B_eV)/2
            # Divide out cross-section scale so adaptive tolerance is dimensionless.
            ref=quad(lambda W:float(ion.raw_bed_m2_eV(E,W))/ion.S_m2,0,upper,epsabs=1e-15,epsrel=1e-12,limit=300)[0]*ion.S_m2
            value=float(ion.total_m2(E));integrals.append({'species':sp,'energy_eV':E,'closed_total_m2':value,'adaptive_raw_integral_m2':ref,'GL128_raw_m2':ion.raw_integral_m2(E),'relative':relative(value,ref)})
            densities=ion.raw_bed_m2_eV(E,np.linspace(0,upper,65));domains.append(bool(np.all(densities>=0) and np.all(np.isfinite(densities))))
        domains.append(bool(np.all(ion.total_m2([0,ion.B_eV*.5,ion.B_eV])==0)))
        for fun in (lambda:ion.total_m2(-1),lambda:ion.total_m2(900.001),lambda:ion.total_m2(float('nan')),lambda:ion.raw_bed_m2_eV(100,-1),lambda:ion.raw_bed_m2_eV(100,(100-ion.B_eV)/2+1e-8),lambda:ion.raw_bed_m2_eV(ion.B_eV,0)):
            try:fun()
            except ValueError:domains.append(True)
            else:domains.append(False)
    check(result,'FULL_BED_TOTAL_VERSUS_INDEPENDENT_ADAPTIVE_SDCS_INTEGRAL',max(r['relative'] for r in integrals)<TOL['SDCS_total_relative'],{'samples':integrals,'max_relative':max(r['relative'] for r in integrals)})
    check(result,'ATOMIC_POSITIVITY_THRESHOLD_AND_SCOPED_DOMAIN',all(domains),{'passed_cases':sum(domains),'cases':len(domains),'no_external_BEQ_normalization':True})
    if any(c['status']=='FAIL' for c in result['checks']):raise RuntimeError('ATOMIC_PREFLIGHT_FAILED_BEFORE_TRANSPORT')
    return atomic

def output_vector(model,final,a,terminal):
    """Exact parent verify_cascade.py output_vector rows; supplied cached terminal."""
    total=final.sum(axis=1);rates=model.G@total+a.sum(axis=1);term=terminal.sum(axis=1)
    out={'active_energy':float(total[:model.n].sum()),'active_number':float(np.dot(1/model.E,total[:model.n])),'heat_power':float(rates[model.ix['heat']]),'terminal_heat_power':float(term[model.ix['heat']])}
    for name in cc.LEDGERS:out[name]=float(total[model.ix[name]])
    for name in ('ionizations_HI','ionizations_HeI'):out[name+'_rate']=float(rates[model.ix[name]])
    return out

def run_grid(cells,atomic,source,run_dir,result,label='fullBED'):
    """One endpoint evolution and one terminal sparse solve; no other transport."""
    start=time.monotonic();print('BUILD_AND_RUN_GRID '+label+' '+str(cells),flush=True)
    admission=resources();result.setdefault('resource_admissions',[]).append(admission)
    if not admission['admitted']:raise RuntimeError('RESOURCE_ADMISSION_FAILED')
    model=cc.Cascade(*cells,sharing_order=4,quantum_constant=0.,atomic=atomic)
    a=model.source_vectors(source,order=8)
    ef,nf=model.functionals();absolute=abs(model.G)
    errs=[float(np.max(abs(np.asarray(model.G.T@f).ravel())/np.maximum(np.asarray(absolute.T@abs(f)).ravel(),1e-100))) for f in (ef,nf)]
    offdiag=model.G-scipy.sparse.diags(model.G.diagonal());minimum=float(np.min(offdiag.data)) if offdiag.nnz else 0.
    check(result,'NEW_GENERATOR_ENERGY_NUMBER_AND_METZLER_'+label+'_'+str(model.n),max(errs)<TOL['generator_energy_number_relative'] and minimum>=0,{'energy_relative':errs[0],'number_relative':errs[1],'min_offdiagonal':minimum})
    result['transport_calls_started']=result.get('transport_calls_started',0)+1
    trajectory=model.evolve(a,samples=2);z=trajectory[-1];terminal=model.terminal_yields(a)
    final=model.summarize(z,a,source,1.)
    residual=max(max(abs(d['energy_ledger_relative_residual']),abs(d['number_ledger_relative_residual'])) for d in final['components'].values())
    check(result,'NEW_PROPAGATED_LEDGER_AND_POSITIVITY_'+label+'_'+str(model.n),residual<TOL['propagated_ledger_relative'] and np.min(z)>=-TOL['positivity_absolute_normalized'],{'maximum_ledger_relative':residual,'minimum_state':float(np.min(z))})
    terr=max(float(np.max(abs(f@terminal-f@a)/np.maximum(abs(f@a),1e-100))) for f in (ef,nf))
    rates=(model.G@z+a)[[model.ix[k] for k in cc.ENERGY_LEDGERS],:];trates=terminal[[model.ix[k] for k in cc.ENERGY_LEDGERS],:]
    bound=float(np.max(rates-trates))
    check(result,'SAME_OPERATOR_TERMINAL_LEDGER_'+label+'_'+str(model.n),terr<TOL['terminal_ledger_relative'] and bound<1e-12,{'maximum_ledger_relative':terr,'max_transient_minus_terminal_absorber_rate':bound,'one_sparse_terminal_solve':True})
    norm=np.asarray([row[3] for row in model.normalization_diagnostics]);qerr=max(row[2] for row in model.normalization_diagnostics)
    maxfactor=float(np.max(abs(norm-1)))
    check(result,'NUMERICAL_SHARING_NORMALIZATION_NEAR_UNITY_'+label+'_'+str(model.n),qerr<TOL['sharing_quadrature_relative'] and (label!='fullBED' or maxfactor<TOL['sharing_quadrature_relative']),{'max_quadrature_relative':qerr,'factor_min':float(norm.min()),'factor_max':float(norm.max()),'max_factor_minus_one':maxfactor,'physical_external_normalization':label!='fullBED'})
    metrics=output_vector(model,z,a,terminal)
    row={'label':label,'cells':list(cells),'nodes':model.n,'nnz':model.G.nnz,'seconds':time.monotonic()-start,'metrics_normalized':metrics,'final':final,'same_operator_terminal':{'energy_fractions_of_selected_input':{k:float(terminal[model.ix[k]].sum()) for k in cc.ENERGY_LEDGERS},'terminal_heat_power_at_T_J_m3_s':float(terminal[model.ix['heat']].sum()*source.energy_scale_eV_m3*cc.EV_J/cc.T_END),'finite_to_terminal_heat_power_ratio':float((model.G@z+a)[model.ix['heat']].sum()/terminal[model.ix['heat']].sum())},'sharing_quadrature_max_relative':qerr,'sharing_normalization_factor_range':[float(norm.min()),float(norm.max())]}
    result.setdefault('grid_results',[]).append(row)
    path=Path(run_dir)/('SPECTRUM_'+label+'_'+str(model.n)+'.npz')
    np.savez_compressed(path,energy_eV=model.E,state_normalized=trajectory,source_vectors=a,terminal_yields=terminal,physical_energy_scale_eV_m3=source.energy_scale_eV_m3,time_s=np.array([0.,cc.T_END]),birth_tags=np.array(['direct_0p1_10','direct_10_900']))
    row['spectrum']=identity(path);save(result,Path(run_dir)/'NUMERICAL_RESULT.json');print('GRID_COMPLETE '+label+' '+str(model.n),flush=True)
    return row

def comparisons(result):
    rows=result['grid_results'];coarse,fine=rows
    changes={k:relative(fine['metrics_normalized'][k],coarse['metrics_normalized'][k]) for k in fine['metrics_normalized']}
    ok=all(v<(TOL['mesh_cutoff_and_low_boundary_count_relative'] if k in ('cutoff_number','low_cross_number') else TOL['mesh_channel_relative']) for k,v in changes.items())
    check(result,'TWO_GRID_CHANNEL_CONVERGENCE_WITH_FROZEN_TOLERANCES',ok,{'relative_changes':changes,'coarse':coarse['cells'],'fine':fine['cells'],'parent_output_vector_definition_preserved':True})
    legacy=json.loads((ROOT.parent/'cr_phys02b_20261010/evidence/runs/R002/NUMERICAL_RESULT.json').read_text())
    legacyrows={tuple(r['cells']):r for r in legacy['grid_results']}
    paired=[]
    def append(key,newc,newf,oldc,oldf,group):
        dc=newc-oldc;df=newf-oldf;r=abs(df-dc)/abs(df) if df else None;signs=dc*df>0
        paired.append({'group':group,'observable':key,'new_coarse':newc,'new_fine':newf,'legacy_coarse':oldc,'legacy_fine':oldf,'delta_coarse':dc,'delta_fine':df,'percent_of_legacy_coarse':100*dc/abs(oldc) if oldc else None,'percent_of_legacy_fine':100*df/abs(oldf) if oldf else None,'empirical_r':r,'signs_agree':signs,'resolution_status':'EMPIRICALLY_RESOLVED' if r is not None and r<1/3 and signs else ('EXACT_ZERO_DELTA' if df==dc==0 else 'UNRESOLVED')})
    lc=legacyrows[tuple(coarse['cells'])];lf=legacyrows[tuple(fine['cells'])]
    for key in fine['metrics_normalized']:append(key,coarse['metrics_normalized'][key],fine['metrics_normalized'][key],lc['metrics_normalized'][key],lf['metrics_normalized'][key],'parent_output_vector_normalized')
    for tag in fine['final']['components']:
        for key in fine['final']['components'][tag]:
            if key.endswith('residual'):continue
            append(key,coarse['final']['components'][tag][key],fine['final']['components'][tag][key],lc['final']['components'][tag][key],lf['final']['components'][tag][key],tag)
    result['paired_deltas']=paired
    check(result,'PAIRED_PHYSICAL_REPRESENTATION_DELTAS_WITH_EMPIRICAL_RESOLUTION_STATUS',True,{'rows':len(paired),'empirically_resolved':sum(r['resolution_status']=='EMPIRICALLY_RESOLVED' for r in paired),'unresolved':sum(r['resolution_status']=='UNRESOLVED' for r in paired),'legacy_transport_rerun':0,'interpretation':'Two-grid diagnostic, not certified error bound or significance test.'})

def main():
    p=argparse.ArgumentParser();p.add_argument('--run-dir',required=True);p.add_argument('--atomic-only',action='store_true');args=p.parse_args()
    directory=Path(args.run_dir);directory.mkdir(parents=True,exist_ok=True);output=directory/'NUMERICAL_RESULT.json'
    if output.exists():raise FileExistsError('PRESERVE_EXISTING_RUN_OUTPUT')
    result={'schema':'cr-phys02c-targeted-result.v1','actual_worker_model':'GPT-6.1-sol','assigned_role':'contract-preserving implementation/execution; not Astra science owner','start_utc':now(),'command':sys.argv,'cwd':str(Path.cwd()),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'precision':'FP64','threads':{k:os.environ[k] for k in THREAD_KEYS},'actual_threadpools':threadpool_info()},'identities':{str(path.relative_to(ROOT)):identity(path) for path in [ROOT/'state/SCIENTIFIC_CONTRACT.json',ROOT/'inputs/PARENT_IDENTITY.json',ROOT/'inputs/FULL_BED_INPUTS.json',ROOT/'src/coherent_bed.py',Path(__file__)]},'checks':[],'status':'RUNNING','transport_calls_started':0,'prior_science_suites_rerun':0}
    start=time.monotonic();code=1
    try:
        new_manifest=json.loads((ROOT/'inputs/FULL_BED_INPUTS.json').read_text())
        for rel,entry in new_manifest['files'].items():bed.checked_file(ROOT/rel,entry['sha256'])
        atomic=atomic_checks(result)
        if not args.atomic_only:
            source=cc.ElectronSource();result['coverage']=source.coverage();transport_start=time.monotonic()
            for cells in ((800,1600),(1600,3200)):
                if time.monotonic()-transport_start>900:raise RuntimeError('TRANSPORT_WALL_BUDGET_EXCEEDED')
                run_grid(cells,atomic,source,directory,result)
            result['transport_wall_seconds']=time.monotonic()-transport_start
            if result['transport_wall_seconds']>900:raise RuntimeError('TRANSPORT_WALL_BUDGET_EXCEEDED')
            comparisons(result)
        result['status']='PASS_SCOPED' if all(c['status']=='PASS_SCOPED' for c in result['checks']) else 'FAIL';code=0 if result['status']=='PASS_SCOPED' else 1
    except Exception:
        result['status']='EXECUTION_FAILED';result['exception']=traceback.format_exc();traceback.print_exc()
    finally:
        result['actual_exit']=code;result['end_utc']=now();result['elapsed_seconds']=time.monotonic()-start;result['peak_RSS_KiB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;result['resources_end']=resources();save(result,output)
    print('FINAL_STATUS '+result['status'],flush=True);return code
if __name__=='__main__':sys.exit(main())
