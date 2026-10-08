"""One owner-authorized h=.20 finer preparation; never launches a collision."""
import argparse
import fcntl
import json
from pathlib import Path
import shutil
import time
from r3m15_coordinator import SCIENCE, REPO, command, sha, verify_seal, write_new

def run(root):
    for _ in range(450):
        if (root/'C/FAILURE.json').exists():raise RuntimeError('C structural failure')
        if (root/'C/COMPLETE.json').exists():break
        time.sleep(2)
    else:raise RuntimeError('bounded C wait exhausted')
    with (root/'matrix.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        out=root/'B_preparation_refinement';out.mkdir(exist_ok=False);(out/'receipts').mkdir()
        config=REPO/'configs/r3m15/B_preparation_only.json'
        cfg=json.loads(config.read_text());base=json.loads((root/'B/config.json').read_text())
        expected=dict(base,imag_dt=.003125,imag_steps=9600)
        if cfg!=expected:raise ValueError('optional preparation config drift')
        shutil.copy2(config,out/'config.json');verify_seal(root/'B/collision')
        probability=json.loads((root/'B/collision/result.json').read_text())['analysis']['gram_audit']['P_span_nmax']
        import mlflow
        mlflow.set_tracking_uri('sqlite:///'+str(root/'mlflow.db'));mlflow.set_experiment('R3M15_CONTROLLED_SPATIAL')
        try:
            command('resource_preflight',[SCIENCE,'scripts/r3m15_resource_probe.py','--config',str(config),'--out',str(out/'resource.json')],out)
            command('prepare',[SCIENCE,'scripts/r3m13_initial_state_pair.py','prepare','--config',str(config),'--out',str(out/'preparation')],out)
            for name in ['initial.npy','receipt.json','attempt.json']:(out/'preparation'/name).chmod(0o444)
            command('compare',[SCIENCE,'scripts/r3m13_initial_state_pair.py','compare','--first',str(root/'B/preparation'),'--second',str(out/'preparation'),'--out',str(out/'pair.json'),'--reference-probability',repr(probability)],out,memory_guard=False)
            pair=json.loads((out/'pair.json').read_text());interval=pair['conditional_interval']
            witness=json.loads((root/'B/collision/r3m14_initial_binding.json').read_text())
            assert witness['prepared_state_file_sha256']==pair['first_state_sha256']
            assert witness['status']=='PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED'
            write_new(out/'INTERPRETATION.json',dict(
                a_priori_pair_certificate='SUFFICIENT_CONDITIONAL_PAIR_ONLY' if interval['floating_pair_screen'] else 'INCONCLUSIVE',
                measured_same_grid_capture_test='NOT_RUN_NO_ADDITIONAL_COLLISION',
                reference_B_initial_binding_verified=True,reference_B_result_sha256=sha(root/'B/collision/result.json'),
                scalar_probability=probability,conditional_relative_upper=interval['relative_error_upper'],
                roundoff_certified=False,global_preparation_error_certified=False,
                historical_reference_anchor_verified=False,historical_decision_changed=False,
                new_collision_count=0,bgrid='NO_GO'))
            write_new(out/'COMPLETE.json',{'status':'PREPARATION_AND_CONDITIONAL_COMPARE_COMPLETE','new_collision_count':0,'pair_sha256':sha(out/'pair.json')})
        except BaseException as exc:
            write_new(out/'FAILURE.json',{'type':type(exc).__name__,'message':str(exc)})
            raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    run(p.parse_args().root)
