"""One-shot native three-cell fixture run, reusing stored R4AM oracle results.
No historical integral, root finder, M9 or scientific batch is rerun.
"""
from pathlib import Path
from fractions import Fraction as F
import sys,json,hashlib,subprocess,time,resource,os
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'source'),str(ROOT/'parent/source'),str(ROOT/'parent/vendor')]
from native_adapter import serialize,build,BINARY,_limits,sha,KEYS
from weak_kernel import Candidate,Cell,Context
from geometry import Triangle,Affine
from dyadic import I,ZERO,ONE,SCALE,sym
from complex_box import C
from quadrature import legendre

def loadc(d):return C(I.load(d['real']),I.load(d['imag']))
def dumpc(x):return {'real':x.re.dump(),'imag':x.im.dump()}

def run(contract_path):
    cp=Path(contract_path).resolve();c=json.loads(cp.read_text())
    if c['schema']!='R4AN_THREE_FIXTURE_RUN_V1' or c['actual_atomic_integral_cap']!=0 or c['precision_bits']!=256:raise ValueError('contract scope')
    for name,h in c['pins'].items():
        if sha(ROOT/name)!=h:raise ValueError('source/input changed: '+name)
    out=Path(c['output']).resolve()
    out.mkdir(parents=True,exist_ok=False)
    (out/'RESERVATION.json').write_text(json.dumps({'state':'STARTED','contract_sha256':sha(cp),'attempt_cap':1,'actual_atomic_integrals':0}))
    start=time.monotonic()
    try:
        br=build()
        if br['native_sha256']!=c['native_sha256']:raise ValueError('native identity changed')
        for p,h in br['libraries'].items():
            if sha(p)!=h:raise ValueError('library identity changed')
        old=json.loads((ROOT/'parent/evidence/LIGHT_FIXTURE_RESULT.json').read_text())
        if old['status']!='ANALYTIC_FIXTURES_CONTAINED_AND_TARGET_MET':raise ValueError('parent fixture gate')
        oracle=old['fixture_results'];record=[]
        a=F(1,8);edges=(F(0),a,F(1),F(2),F(4),F(8))
        coeff=tuple((lo,hi-lo,F(0),F(0),F(0)) for lo,hi in zip(edges,edges[1:]))
        cand=Candidate(edges,(coeff,coeff),(0,1),'LOCAL_MANUFACTURED_FIELD_U_EQUALS_R')
        ctx=Context(3,4,0,0)
        tri=Triangle(3,4,((Affine(F(2)),Affine(F(4))),(Affine(F(3)),Affine(F(4))),(Affine(F(3)),Affine(F(5)))),(F(1),F(0),F(0)))
        cells=[Cell('origin_T',0,4),Cell('origin_P',4,0),Cell('regular',3,4,tri)]
        for cell,prior in zip(cells,oracle):
            if time.monotonic()-start>c['total_wall_seconds']:raise TimeoutError('fixture batch wall')
            enc=prior['enclosure'];n=enc['degree']
            if n!=32 or enc['entry']!=[0,0,0,0] or enc['chart']!=cell.kind:raise ValueError('oracle domain')
            # Reuse certified root brackets; derive interval weights only.
            nodes=[I.bounds(F(x['lower']),F(x['upper'])) for x in enc['root_brackets']]
            weights=[]
            for x in nodes:
                d=n*(x*legendre(n,x)-legendre(n-1,x))/(x*x-1)
                w=2/((1-x*x)*d*d)
                if w.lo<=0:raise ValueError('weight positivity')
                weights.append(w)
            if not sum(weights,ZERO).contains(2):raise ValueError('weight sum')
            samples=[(x*F(1,2)+F(1,2),y*F(1,2)+F(1,2),wx*wy*F(1,4)) for x,wx in zip(nodes,weights) for y,wy in zip(nodes,weights)]
            data=serialize(cand,cell,ctx,(0,0,0,0),samples)
            case=out/cell.kind;case.mkdir();(case/'INPUT.txt').write_text(data)
            tic=time.monotonic();p=subprocess.run([str(BINARY)],input=data,capture_output=True,text=True,preexec_fn=_limits,timeout=c['per_cell_wall_seconds'])
            wall=time.monotonic()-tic;(case/'STDOUT.txt').write_text(p.stdout);(case/'STDERR.txt').write_text(p.stderr)
            if p.returncode:raise RuntimeError('native fixture failed: '+p.stderr)
            lines=p.stdout.splitlines()
            if lines[0]!='R4AN_NUMERIC_V1 256 1024' or len(lines)!=5:raise ValueError('native response')
            result={};diffs=[];exact_endpoints=0
            for key,line in zip(KEYS,lines[1:]):
                k,rl,rh,il,ih=line.split()
                if k!=key:raise ValueError('key')
                v=C(I.raw(int(rl),int(rh)),I.raw(int(il),int(ih)))
                ref=loadc(enc['numeric'][key]);err=I.load(enc['analytic_modulus_error'][key])
                for x,y in ((v.re,ref.re),(v.im,ref.im)):
                    if max(x.lo,y.lo)>min(x.hi,y.hi):raise ValueError('native/reference numeric disjoint')
                    diffs.append(abs(x.mid()-y.mid()));exact_endpoints+=int((x.lo,x.hi)==(y.lo,y.hi))
                full=v+C(sym(err),sym(err));value=F(prior['expected'][key])
                if not(full.re.contains(value) and full.im.contains(0)):raise ValueError('analytic fixture outside interval')
                result[key]={'numeric':dumpc(v),'enclosure':dumpc(full),'inherited_analytic_modulus_error':err.dump(),'exact_expected':str(value)}
            radius=max(F(int(x['enclosure']['real']['upper_numerator'])-int(x['enclosure']['real']['lower_numerator'])+int(x['enclosure']['imag']['upper_numerator'])-int(x['enclosure']['imag']['lower_numerator']),2*SCALE) for k,x in result.items() if k in ('H_TP','K_TP'))
            if radius>F(c['target_per_complex_entry']):raise ValueError('cell fixture target not met')
            q={'chart':cell.kind,'input_sha256':sha(case/'INPUT.txt'),'output_sha256':sha(case/'STDOUT.txt'),'nodes':1024,'wall_seconds':wall,'returncode':p.returncode,'radius_l1_upper':str(radius),'max_component_midpoint_difference_to_saved_reference':str(max(diffs)),'bit_identical_real_imag_interval_pairs':exact_endpoints,'values':result}
            (case/'RESULT.json').write_text(json.dumps(q,indent=2));record.append(q)
        ans={'schema':'R4AN_NATIVE_SINGLE_CELL_PARITY_RESULT_V1','status':'NATIVE_THREE_CELL_FIXTURE_PARITY_PASS','contract_sha256':sha(cp),'native_sha256':br['native_sha256'],'fixtures':record,'new_native_quadrature_nodes':3072,'actual_candidate_integrals':0,'parent_integrals_reexecuted':0,'full_K_calls':0,'new_time_derivative_bounds':None,'pointwise_value_tests_are_not_cubature_certificates':True,'precise_K_cubature_error':None,'wall_seconds':time.monotonic()-start,'native_cell_walls_sum':sum(x['wall_seconds'] for x in record)}
        (out/'RESULT.json').write_text(json.dumps(ans,indent=2));(out/'COMPLETED.json').write_text(json.dumps({'state':'COMPLETE','result_sha256':sha(out/'RESULT.json')}))
        return ans
    except Exception as e:
        (out/'FAILURE.json').write_text(json.dumps({'state':'FAILED','error':type(e).__name__,'message':str(e),'automatic_retry':False}));raise

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: run_parity.py <sealed contract json>')
    a=run(sys.argv[1]);print(json.dumps({'status':a['status'],'wall_seconds':a['wall_seconds'],'radii':[float(F(x['radius_l1_upper'])) for x in a['fixtures']],'numeric_midpoint_differences':[float(F(x['max_component_midpoint_difference_to_saved_reference'])) for x in a['fixtures']]}))
