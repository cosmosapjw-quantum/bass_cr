"""Validated signed time-dependent adjoint, explicit births, bounded secant defect."""
import argparse,hashlib,json,os,resource,time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from validated import IV,D,UP,DOWN,Aff,total,matvec,center,symmetric,volterra_tube,backward_step,birth_transpose
from prepare import compute_cell,load

def restore(panel):
    return [[IV(*v) for v in row] for row in panel['Ahat']],[IV(*v) for v in panel['residual']],[IV(*v) for v in panel['goal']],[D(v) for v in panel['nonlinear_remainder_upper']],D(panel['dt'])
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def cell_data(out):return [load(out/f'cell_{i:02d}.json') for i in range(32)]

def backward(cells,out):
    lam=[IV(0)]*cells[-1]['dimension'];forcing=IV(0);rem=D(0);birth=IV(0);trace=[]
    for c in reversed(cells):
        spans=[]
        for p in reversed(c['panels']):
            A,r,g,q,d=restore(p);left,tube=backward_step(A,g,lam,d)
            term=-IV(d)*total(v*w for v,w in zip(tube,r));forcing=forcing+term
            radius=UP.multiply(d,total(IV(v.mag())*IV(w) for v,w in zip(tube,q)).hi)
            rem=UP.add(rem,radius)
            spans.append({'k':p['k'],'lambda_right':[v.data() for v in lam],'lambda_left':[v.data() for v in left],
                          'lambda_full_time':[v.data() for v in tube],'residual_goal_interval':term.data(),'nonlinear_goal_radius':str(radius)})
            lam=left
        event=c['event_before'];event_term=IV(0)
        if event:
            event_term=total(l*IV(*d) for l,d in zip(lam,event['delta']));birth=birth+event_term
            lam=birth_transpose(lam,event['dimension_before'])
        trace.append({'index':c['index'],'event':event,'event_goal_interval':event_term.data(),
                      'lambda_before':[v.data() for v in lam],'panels':list(reversed(spans))})
        print('ADJOINT',c['index'],'FORCING',forcing.data(),'NL',str(rem),flush=True)
    ans=forcing+birth+symmetric(rem)
    dump(out/'ADJOINT_EVIDENCE.json',list(reversed(trace)))
    return {'signed_interval':ans.data(),'forcing':forcing.data(),'births':birth.data(),'nonlinear_radius':str(rem),
            'lambda_at_initial':[v.data() for v in lam],'initial_error_term':'0 (original initial gas/count exact); later incoming states not reset'}

def forward_affine(cells,out):
    e=[Aff(0) for _ in range(cells[0]['dimension'])];goal=Aff(0);trace=[]
    for c in cells:
        event=c['event_before']
        if event:
            dv=IV(*event['delta'][-1]);cc=center(dv)
            e.append(Aff(cc,{event['shared_noise_label']:IV((dv-IV(cc)).mag())}))
        before=[v.box().data() for v in e]
        for p in c['panels']:
            A,r,g,q,d=restore(p);eb=[v.box() for v in e]
            forcing=[-v+symmetric(u) for v,u in zip(r,q)]
            tube,rho,proof=volterra_tube(A,forcing,eb,d)
            amid=[[center(v) for v in row] for row in A];gmid=[center(v) for v in g]
            optical=Aff(0)
            for gi,ei in zip(gmid,e):optical=optical+ei.scale(IV(d)*IV(gi))
            optical_remainder=IV(d)*total((gi-IV(gm))*x+gi*symmetric(rad) for gi,gm,x,rad in zip(g,gmid,eb,rho))
            goal=goal+optical.add_box(optical_remainder,f'optical_{c["index"]}_{p["k"]}')
            nxt=[]
            for j,(row,mid) in enumerate(zip(A,amid)):
                base=e[j]
                for a,x in zip(mid,e):base=base+x.scale(IV(d)*IV(a))
                fc=center(forcing[j]);base=base+Aff(IV(d)*IV(fc))
                defect=IV(d)*(total((a-IV(ac))*x+a*symmetric(rad) for a,ac,x,rad in zip(row,mid,eb,rho))+(forcing[j]-IV(fc)))
                nxt.append(base.add_box(defect,f'flow_{c["index"]}_{p["k"]}_{j}'))
            e=nxt
            if (p['k']+1)%8==0:
                # Explicit outward relaxation of non-birth generators only.
                # Birth theta labels remain common in state and optical goal.
                e=[x.compress(f'compressed_state_{c["index"]}_{p["k"]}_{j}') for j,x in enumerate(e)]
                goal=goal.compress(f'compressed_goal_{c["index"]}_{p["k"]}')
        trace.append({'index':c['index'],'incoming_affine_box':before,'outgoing_affine_box':[v.box().data() for v in e],
                      'goal_prefix_interval':goal.box().data(),'shared_birth_goal_coefficients':{k:v.data() for k,v in goal.noise.items() if k.startswith('theta_birth')},
                      'shared_birth_state_coefficients':[{k:v.data() for k,v in x.noise.items() if k.startswith('theta_birth')} for x in e],
                      'affine_generator_count':len(goal.noise)})
        print('FORWARD',c['index'],'GOAL',goal.box().data(),flush=True)
    dump(out/'FORWARD_AFFINE_EVIDENCE.json',trace)
    return {'signed_interval':goal.box().data(),'shared_birth_labels':sorted(k for k in goal.noise if k.startswith('theta_birth')),
            'correlation':'same generators retained in incoming state, old photons and accumulated goal; only coefficient/nonlinear defects receive fresh remainder generators'}

def run(stage,out,panels,workers,prepared=None):
    started=time.monotonic();out.mkdir(parents=True,exist_ok=False)
    if prepared:
        import shutil
        for i in range(32):shutil.copyfile(prepared/f'cell_{i:02d}.json',out/f'cell_{i:02d}.json')
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for c in pool.map(compute_cell,[(str(stage),i,panels) for i in range(32)]):
                dump(out/f'cell_{c["index"]:02d}.json',c);print('PANELS_READY',c['index'],'RSS',c['worker_peak_RSS_KiB'],flush=True)
    cells=cell_data(out);b=backward(cells,out);f=forward_affine(cells,out)
    bi=IV(*b['signed_interval']);fi=IV(*f['signed_interval']);inter=IV(max(bi.lo,fi.lo),min(bi.hi,fi.hi))
    old=load(stage/'r15/source/research/cr_xthread_r15_20261008/RESULTS.json')
    from fractions import Fraction as Q
    oldlo,oldhi=[Q(int(x['num']),int(x['den'])) for x in old['signed_tau_difference_interval']]
    if Q(inter.hi)<oldlo or Q(inter.lo)>oldhi:raise ValueError('EMPTY_R15_INTERSECTION')
    improved=Q(inter.hi)-Q(inter.lo)<oldhi-oldlo
    result={'task':'R16B_CERTIFIED_SIGNED_ADJOINT_WITH_BIRTHS','status':'CERTIFIED_SHARPENING' if improved else 'NO_CERTIFIED_SHARPENING',
        'signed_optical_depth_interval':inter.data(),'adjoint':b,'forward_affine':f,
        'panels_per_cell':panels,'full_time_panels':sum(len(c['panels']) for c in cells),
        'births':6,'dimension_progression':[c['dimension'] for c in cells],'time_s':[0,1250000000],
        'R15_interval_exact':old['signed_tau_difference_interval'],'nonempty_R15_overlap':True,
        'width_ratio_to_R15':float((Q(inter.hi)-Q(inter.lo))/(oldhi-oldlo)),
        'strict_sign_positive':inter.lo>0,'backward_error_term_used':'actual signed time-dependent nominal Jacobian; full-time interval Volterra enclosures',
        'nonlinear_bound':'secant-Jacobian minus nominal-Jacobian at common time panel, contracted state tube from inherited all-prefix E',
        'conditional_on':'donor physical Picard/all-prefix proof and unchanged Decimal60 directed/outward arithmetic; no independent interval RHS or proof assistant',
        'physical':'HOLD','production':'HOLD','elapsed_s':time.monotonic()-started,
        'coordinator_peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'workers':workers,
        'worker_peak_RSS_KiB_max':max(c['worker_peak_RSS_KiB'] for c in cells)}
    dump(out/'R16B_RESULTS.json',result);print('RESULT',json.dumps(result),flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--stage',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    a.add_argument('--panels',type=int,default=64);a.add_argument('--workers',type=int,default=1);a.add_argument('--prepared',type=Path)
    x=a.parse_args()
    if x.panels not in (16,32,64,128,256) or not 1<=x.workers<=8:a.error('BOUNDED_RESOURCE_DOMAIN')
    run(x.stage,x.output,x.panels,x.workers,x.prepared)
