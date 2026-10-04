"""Source-bound one-cell R4AO pilot; never a full atomic matrix executor.

prepare fixes the candidate, origin-P chart, one p/p mode pair, environment,
native identity, Gaussian rule and a finite run budget. run consumes that exact
contract once. The existing R4AN and R4AH runtimes are never changed or invoked.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json,os,platform,resource,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'source'),str(ROOT/'vendor_r4am/source'),str(ROOT/'vendor_r4am/vendor')]
from weak_kernel import Candidate,Cell,Context,cover,kernel
from dyadic import I,ZERO,SCALE,sym
from complex_box import C,ellipse_box
from quadrature import legendre,gauss_constant
from finite_adapter import serialize
KEYS=('S_TP','H_TP','D_TP','K_TP')
ENTRY=(4,3,1,-1)
CANDIDATE='17c0215979675e40db364207ce138c5efb58cb24c22824e418f5abe3cfeb49ef'
METHOD={'precision_fractional_bits':256,'degree':32,'rho':'2','subdivisions':0,'complex_L1_target':'1/10000000000000000'}
CAPS={'candidate_geometries':1,'cells':1,'channel_pairs':1,'native_attempts':1,'native_nodes':1024,'complex_majorant_calls':2,'root_finder_calls':0,'full_matrix_calls':0,'historical_replays':0}
RESOURCES={'native_memory_limit_bytes':536870912,'native_cpu_seconds':120,'native_wall_seconds':120,'total_wall_seconds':420,'minimum_visible_free_bytes':1073741824,'minimum_cpu_capacity':'1','scope':'LOCAL_BOUNDED_CELL_NOT_R4AH_RESOURCE_AMENDMENT'}

def sha(path:Path)->str:return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path:Path,data)->None:
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(data,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
def canon(x)->str:return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def dumpc(c):return {'real':c.re.dump(),'imag':c.im.dump()}
def loadc(c):return C(I.load(c['real']),I.load(c['imag']))
def frozen_pins():
    paths=[]
    for d in ('source','native','vendor_r4am/source','vendor_r4am/vendor','inputs'):
        paths.extend(p for p in (ROOT/d).iterdir() if p.is_file() and not p.name.endswith('.pyc'))
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}
def observed():
    """Actual local-session visible cgroup snapshot, not a global NCP certificate.

    No missing value becomes zero or unlimited. The native has independent hard
    address-space/CPU limits. Hidden ancestor limits remain explicitly unknown.
    """
    q,period=Path('/sys/fs/cgroup/cpu.max').read_text().split()
    maximum=Path('/sys/fs/cgroup/memory.max').read_text().strip()
    current=int(Path('/sys/fs/cgroup/memory.current').read_text().strip())
    if maximum=='max':raise RuntimeError('this local profile requires a visible finite cgroup limit')
    maximum=int(maximum)
    info=dict(line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines())
    available=int(info['MemAvailable'].split()[0])*1024
    aff=sorted(os.sched_getaffinity(0))
    capacity=F(len(aff)) if q=='max' else min(F(len(aff)),F(int(q),int(period)))
    return {'profile':'OBSERVED_LOCAL_SESSION_VISIBLE_CGROUP_PLUS_NATIVE_RLIMIT',
            'visible_memory_limit':maximum,'visible_memory_current':current,
            'visible_available_bytes':min(available,max(0,maximum-current)),
            'cpu_capacity':str(capacity),'affinity':aff,
            'membership':Path('/proc/self/cgroup').read_text(),
            'mountinfo_sha256':sha('/proc/self/mountinfo'),
            'namespaces':{k:os.readlink('/proc/self/ns/'+k) for k in ('pid','mnt','cgroup')},
            'hidden_ancestor_limits':'NOT_ASSERTED','python_sha256':sha(sys.executable),
            'platform':platform.platform(),'python':sys.version,
            'numpy':__import__('numpy').__version__,'fixture':False}
def admit(e):
    if e['fixture'] is not False or e['profile']!='OBSERVED_LOCAL_SESSION_VISIBLE_CGROUP_PLUS_NATIVE_RLIMIT':raise ValueError('no synthetic resource admission')
    if e['visible_available_bytes']<RESOURCES['minimum_visible_free_bytes'] or F(e['cpu_capacity'])<F(RESOURCES['minimum_cpu_capacity']):raise RuntimeError('insufficient observed local-session resource headroom')
def identity(e):return {k:e[k] for k in ('profile','membership','mountinfo_sha256','namespaces','python_sha256','platform','numpy')}
def model():
    candidate=Candidate.load(ROOT/'inputs/CANDIDATE.npz',ROOT/'inputs/CANDIDATE.json')
    if candidate.identity!=CANDIDATE:raise ValueError('unregistered candidate')
    g=json.loads((ROOT/'inputs/ANCHOR_GEOMETRY.json').read_text())['geometry']
    ctx=Context(F(2),F(float(g['actual_z_a0'])),F(float(g['speed_a0_per_ta'])),F(float(g['time_ta'])))
    if ctx.z!=-32 or ctx.b!=2:raise ValueError('registered anchor only')
    cell=Cell('origin_P',28,0)
    return candidate,cell,ctx

def binding_of(candidate,cell,ctx):
    return {'candidate':candidate.identity,'profile':candidate.profile,'cell':cell.dump(),
            'entry':list(ENTRY),'context':{k:str(getattr(ctx,k)) for k in ('b','z','v','t')},'node_limit':1024}
def build(directory:Path):
    directory.mkdir(parents=True,exist_ok=False);binary=directory/'weak_cell'
    cmd=['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off',str(ROOT/'native/weak_cell.cpp'),'-lgmpxx','-lgmp','-o',str(binary)]
    start=time.monotonic();p=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
    (directory/'COMPILE.stdout').write_text(p.stdout);(directory/'COMPILE.stderr').write_text(p.stderr)
    if p.returncode:raise RuntimeError('native compile/link failure')
    ldd=subprocess.run(['ldd',str(binary)],capture_output=True,text=True,check=True).stdout
    (directory/'LDD.txt').write_text(ldd)
    libs={}
    for line in ldd.splitlines():
        for x in line.split():
            if x.startswith('/') and Path(x).is_file():libs[x]=sha(x)
    import shutil
    compiler=Path(shutil.which('g++')).resolve()
    report={'command':cmd,'native_path':str(binary),'native_sha256':sha(binary),'source_sha256':sha(ROOT/'native/weak_cell.cpp'),'libraries':libs,'compiler_path':str(compiler),'compiler_sha256':sha(compiler),'compiler_version':subprocess.run([str(compiler),'--version'],capture_output=True,text=True,check=True).stdout,'wall_seconds':time.monotonic()-start}
    write(directory/'BUILD.json',report);return report

def prepare(path,output):
    path,output=Path(path),Path(output)
    if not path.is_absolute() or not output.is_absolute() or path.exists() or output.exists() or path.is_symlink() or output.is_symlink():raise ValueError('fresh absolute contract and output paths required')
    env=observed();admit(env)
    candidate,cell,ctx=model();cells,coverage=cover(candidate,ctx.R)
    if sum(x.dump()==cell.dump() for x in cells)!=1:raise ValueError('selected origin chart not unique in complete cover')
    br=build(path.parent/(path.stem+'_build'))
    contract={'schema':'R4AO_FINITE_CANDIDATE_SINGLE_CELL_V1','source_root':str(ROOT),'output':str(output),
              'binding':binding_of(candidate,cell,ctx),'coverage':coverage,'method':METHOD,'caps':CAPS,'resources':RESOURCES,
              'source_input_pins':frozen_pins(),'environment':env,'native':br,'science_execution_started':False,
              'units':{'S':'1','H':'Eh','D':'ta^-1','K':'Eh','ta':'hbar/Eh'},
              'inheritance':{'native_source':'R4AN byte identical','complex_provider':'R4AM byte identical','fixture_majorant_inherited':False,'S_M9_inherited_for_K':False}}
    write(path,contract);return {'status':'PREPARED_LOCAL_SINGLE_CELL','contract':str(path),'sha256':sha(path),'actual_integrals':0}

def validate(c,path,approval):
    if sha(path)!=approval:raise ValueError('contract hash mismatch')
    if c['schema']!='R4AO_FINITE_CANDIDATE_SINGLE_CELL_V1' or c['source_root']!=str(ROOT):raise ValueError('schema/source root')
    if c['method']!=METHOD or c['caps']!=CAPS or c['resources']!=RESOURCES:raise ValueError('scope/method/resource amendment not authorized')
    if c['units']!={'S':'1','H':'Eh','D':'ta^-1','K':'Eh','ta':'hbar/Eh'}:raise ValueError('units changed')
    if c['source_input_pins']!=frozen_pins():raise ValueError('source/input identity changed')
    candidate,cell,ctx=model()
    if c['binding']!=binding_of(candidate,cell,ctx):raise ValueError('candidate/geometry/epoch/cell/entry binding changed')
    out=Path(c['output'])
    if not out.is_absolute() or out.exists() or out.is_symlink():raise ValueError('consumed/nonabsolute output')
    if any(p.is_symlink() for p in out.parents):raise ValueError('output path through symlink')
    n=c['native']
    if sha(n['native_path'])!=n['native_sha256'] or sha(ROOT/'native/weak_cell.cpp')!=n['source_sha256']:raise ValueError('native identity changed')
    for p,h in n['libraries'].items():
        if sha(p)!=h:raise ValueError('library identity changed')
    now=observed();admit(now)
    if identity(now)!=identity(c['environment']):raise ValueError('local execution environment changed')
    return candidate,cell,ctx,out,now

def rule():
    prior=json.loads((ROOT/'inputs/SAVED_RULE_EVIDENCE.json').read_text())
    r=prior['fixture_results'][0]['enclosure']
    if r['degree']!=32:raise ValueError('stored n32 rule missing')
    nodes=[I.bounds(F(x['lower']),F(x['upper'])) for x in r['root_brackets']]
    if len(nodes)!=32 or any(nodes[i].hi>=nodes[i+1].lo for i in range(31)):raise ValueError('root bracket count/order')
    weights=[]
    for x in nodes:
        der=32*(x*legendre(32,x)-legendre(31,x))/(x*x-1)
        w=2/((1-x*x)*der*der)
        if w.lo<=0:raise ValueError('nonpositive Gauss weight')
        weights.append(w)
    if not sum(weights,ZERO).contains(2):raise ValueError('Gauss normalization')
    return [(x/2+F(1,2),y/2+F(1,2),wx*wy/4) for x,wx in zip(nodes,weights) for y,wy in zip(nodes,weights)]
def limits():
    resource.setrlimit(resource.RLIMIT_AS,(RESOURCES['native_memory_limit_bytes'],)*2)
    resource.setrlimit(resource.RLIMIT_CPU,(RESOURCES['native_cpu_seconds'],)*2)

def run(path,approval):
    path=Path(path);c=json.loads(path.read_text())
    candidate,cell,ctx,out,live=validate(c,path,approval)
    out.mkdir(parents=True,exist_ok=False)
    write(out/'RESERVATION.json',{'state':'STARTED','contract_sha256':approval,'attempt':1,'scope':CAPS,'user_instruction':'Continue next research loop per R4AN_NEXT_HANDOFF; bounded local cell only','environment':live})
    start=time.monotonic();majorants=0;native_calls=0
    try:
        ubox=ellipse_box(F(1,2),F(1,2),F(2));real=C(I.bounds(0,1))
        mu=kernel(candidate,cell,ctx,ubox,real,*ENTRY).upper();majorants+=1
        mw=kernel(candidate,cell,ctx,real,ubox,*ENTRY).upper();majorants+=1
        errors={k:(mu[k]+mw[k])*F(1,2)*gauss_constant(32,F(2)) for k in KEYS}
        # This bound has no origin pole: remote radial coordinate is R+r*eta.
        radius=candidate.edges[1]
        other_u=C(ctx.R)+ubox*radius*(real*2-1)
        other_w=C(ctx.R)+real*radius*(ubox*2-1)
        write(out/'ANALYTIC_REMAINDER.json',{'source_input_pins_sha256':canon(c['source_input_pins']),'entry':list(ENTRY),'cell':cell.dump(),'complex_sup_u':{k:x.dump() for k,x in mu.items()},'complex_sup_w':{k:x.dump() for k,x in mw.items()},'modulus_error':{k:x.dump() for k,x in errors.items()},'rho':'2','degree':32,'mapped_factor':'1/2','gauss_constant':str(gauss_constant(32,F(2))),'remote_denominator_u':dumpc(other_u),'remote_denominator_w':dumpc(other_w),'zero_excluded':other_u.re.lo>0 and other_w.re.lo>0,'origin_r_denominator_eliminated':True,'old_fixture_errors_used':False})
        if other_u.re.lo<=0 or other_w.re.lo<=0:raise ValueError('remote pole exclusion failed')
        if time.monotonic()-start>RESOURCES['total_wall_seconds']:raise TimeoutError('total budget before native')
        samples=rule();text=serialize(candidate,cell,ctx,ENTRY,samples,c['binding'])
        (out/'INPUT.txt').write_text(text);native_calls+=1
        tick=time.monotonic()
        proc=subprocess.run([c['native']['native_path']],input=text,capture_output=True,text=True,preexec_fn=limits,timeout=RESOURCES['native_wall_seconds'])
        nativewall=time.monotonic()-tick
        (out/'STDOUT.txt').write_text(proc.stdout);(out/'STDERR.txt').write_text(proc.stderr)
        if proc.returncode:raise RuntimeError(f'native exit {proc.returncode}: {proc.stderr}')
        lines=proc.stdout.splitlines()
        if len(lines)!=5 or lines[0]!='R4AN_NUMERIC_V1 256 1024':raise ValueError('native response header/count')
        results={}
        for key,line in zip(KEYS,lines[1:]):
            k,a,b,d,e=line.split()
            if k!=key:raise ValueError('native result ordering')
            numeric=C(I.raw(int(a),int(b)),I.raw(int(d),int(e)))
            bound=numeric+C(sym(errors[key]),sym(errors[key]))
            rad=bound.re.radius()+bound.im.radius()
            results[key]={'numeric':dumpc(numeric),'enclosure':dumpc(bound),'radius_L1_upper':str(rad),'midpoint_real':str(bound.re.mid()),'midpoint_imag':str(bound.im.mid()),'analytic_modulus_error':errors[key].dump(),'target_met':rad<=F(METHOD['complex_L1_target'])}
        if time.monotonic()-start>RESOURCES['total_wall_seconds']:raise TimeoutError('total budget after native')
        target=all(results[k]['target_met'] for k in ('H_TP','D_TP','K_TP'))
        result={'schema':'R4AO_FINITE_SINGLE_CELL_RESULT_V1','status':'FINITE_CANDIDATE_SINGLE_CELL_ENCLOSURE_TARGET_MET' if target else 'VALID_ENCLOSURE_TARGET_NOT_MET',
                'contract_sha256':approval,'candidate':candidate.identity,'binding':c['binding'],'units':c['units'],'values':results,
                'native_source_sha256':c['native']['source_sha256'],'native_sha256':c['native']['native_sha256'],
                'input_sha256':sha(out/'INPUT.txt'),'native_output_sha256':sha(out/'STDOUT.txt'),'analytic_sha256':sha(out/'ANALYTIC_REMAINDER.json'),
                'actual_candidate_native_calls':native_calls,'native_nodes':1024,'analytic_majorant_calls':majorants,'new_geometry_count':1,'new_cell_count':1,'new_channel_pair_count':1,
                'historical_replays':0,'root_finder_calls':0,'full_K_calls':0,'subdivisions':0,'target_met':target,'native_wall_seconds':nativewall,'wall_seconds':time.monotonic()-start,
                'K_window_derivative_bound':None,'physical_bridge_upper':None,'precise_full_matrix_K_cubature_error':None,
                'global_ceiling':{'G02':'UNRESOLVED','production':'HOLD','capture':False,'all_bound':'OPEN','b_grid':'NO_GO'}}
        write(out/'RESULT.json',result);write(out/'COMPLETED.json',{'state':'COMPLETE','result_sha256':sha(out/'RESULT.json'),'target_met':target})
        return result
    except Exception as error:
        write(out/'FAILURE.json',{'error':type(error).__name__,'message':str(error),'traceback':traceback.format_exc(),'native_calls':native_calls,'majorant_calls':majorants,'automatic_retry':False,'wall_seconds':time.monotonic()-start})
        raise
    finally:
        write(out/'RETURN_MANIFEST.json',{'files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(out.iterdir()) if p.is_file()},'automatic_expansion':False})

def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    a=s.add_parser('prepare');a.add_argument('--contract',required=True);a.add_argument('--output',required=True)
    a=s.add_parser('run');a.add_argument('--contract',required=True);a.add_argument('--contract-sha256',required=True)
    a=p.parse_args();r=prepare(a.contract,a.output) if a.action=='prepare' else run(a.contract,a.contract_sha256)
    if a.action=='run':r={k:r[k] for k in ('status','target_met','native_nodes','wall_seconds')}
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
