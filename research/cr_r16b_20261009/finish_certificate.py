"""Reuse completed full-time panels/adjoint; finish changed bounded affine flow."""
import argparse,json,resource,shutil,time
from fractions import Fraction as Q
from pathlib import Path
from validated import IV,D,UP,total,symmetric
from run_certificate import cell_data,forward_affine,dump
from prepare import load

def finish(prepared,stage,out):
    started=time.monotonic();out.mkdir(parents=True,exist_ok=False)
    for i in range(32):shutil.copyfile(prepared/f'cell_{i:02d}.json',out/f'cell_{i:02d}.json')
    shutil.copyfile(prepared/'ADJOINT_EVIDENCE.json',out/'ADJOINT_EVIDENCE.json')
    cells=cell_data(out);trace=load(out/'ADJOINT_EVIDENCE.json')
    forcing=IV(0);birth=IV(0);rem=D(0)
    for c in reversed(trace):
        for p in reversed(c['panels']):
            forcing=forcing+IV(*p['residual_goal_interval']);rem=UP.add(rem,D(p['nonlinear_goal_radius']))
        birth=birth+IV(*c['event_goal_interval'])
    adj=forcing+birth+symmetric(rem)
    b={'signed_interval':adj.data(),'forcing':forcing.data(),'births':birth.data(),'nonlinear_radius':str(rem),
       'lambda_at_initial':trace[0]['lambda_before'],'computed_in':'pilot_serial_v1; adjoint not rerun after affine storage change'}
    f=forward_affine(cells,out);fv=IV(*f['signed_interval']);inter=IV(max(adj.lo,fv.lo),min(adj.hi,fv.hi))
    old=load(stage/'r15/source/research/cr_xthread_r15_20261008/RESULTS.json')
    oldlo,oldhi=[Q(int(x['num']),int(x['den'])) for x in old['signed_tau_difference_interval']]
    assert Q(inter.hi)>=oldlo and Q(inter.lo)<=oldhi,'EMPTY_R15_INTERSECTION'
    ratio=(Q(inter.hi)-Q(inter.lo))/(oldhi-oldlo)
    result={'task':'R16B_CERTIFIED_SIGNED_ADJOINT_WITH_BIRTHS','status':'CERTIFIED_SHARPENING' if ratio<1 else 'NO_CERTIFIED_SHARPENING',
        'signed_optical_depth_interval':inter.data(),'adjoint':b,'forward_affine':f,
        'panels_per_cell':64,'full_time_panels':2048,'births':6,'dimension_progression':[c['dimension'] for c in cells],
        'time_s':[0,1250000000],'R15_interval_exact':old['signed_tau_difference_interval'],
        'nonempty_R15_overlap':True,'width_ratio_to_R15':float(ratio),'strict_sign_positive':inter.lo>0,
        'conditional_on':'unchanged Decimal60 directed/outward arithmetic and archived donor Picard/all-prefix proofs; no independent interval RHS/proof assistant',
        'midpoint_R16_used_as_proof':False,'physical':'HOLD','production':'HOLD','finish_wall_s':time.monotonic()-started,
        'coordinator_peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'prep_worker_peak_RSS_KiB_max':max(c['worker_peak_RSS_KiB'] for c in cells),
        'forward_birth_labels_preserved':f['shared_birth_labels'],
        'non_birth_generator_compression':'outward, every8panels; cannot shrink any state/goal marginal; shared birth labels never compressed'}
    dump(out/'R16B_RESULTS.json',result);print('RESULT',json.dumps(result),flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--prepared',type=Path,required=True);a.add_argument('--stage',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    x=a.parse_args();finish(x.prepared,x.stage,x.output)
