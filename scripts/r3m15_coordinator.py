"""Finite outer orchestration; exact scientific interpreter and inherited witness.

Usage (existing MLflow environment): python scripts/r3m15_coordinator.py --job A --root ROOT
Each job is create-only. Interrupted jobs require explicit reconciliation, never replay.
"""
import argparse
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import time

SOURCE='581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b'
SCIENCE='/mnt/sn850x2t/bass_cr_r3m11_20260921/.venv/bin/python'
REPO=Path(__file__).resolve().parents[1]
SPACING={'A':.25,'B':.20,'C':.3125}

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def write_new(path,value):
    with Path(path).open('x') as f:json.dump(value,f,indent=2,allow_nan=False)

def validate_config(job,cfg):
    if job not in SPACING:raise ValueError('only A/B/C, at most three collision jobs')
    base=json.loads((REPO/'configs/r3m13/tdl_dx025_imag0125_T30.json').read_text())
    base.update(backend='cupy',imag_dt=.00625,imag_steps=4800)
    base['grid']['dx']=SPACING[job]
    if cfg!=base:raise ValueError('frozen matrix config mismatch')

def verify_seal(out):
    seal=json.loads((out/'r3m11_checkpoint_seal.json').read_text())
    if seal['source_digest']!=SOURCE:raise ValueError('checkpoint source mismatch')
    if set(seal['files'])!={'state.npy','state.json'}:raise ValueError('incomplete checkpoint seal')
    for name,digest in seal['files'].items():
        if sha(out/name)!=digest:raise ValueError('corrupted checkpoint: '+name)
    state=json.loads((out/'state.json').read_text())
    if not math.isfinite(state['norm']):raise ValueError('nonfinite checkpoint norm')
    return state

def gpu_memory():
    s=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total','--format=csv,noheader,nounits'],text=True)
    used,total=map(int,s.strip().splitlines()[0].split(','));return used,total

def command(label,argv,root,*,memory_guard=True,timeout=1800):
    import mlflow
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(REPO),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',LD_LIBRARY_PATH='/home/cosmosapjw/cosmo_lab/.venv/lib/python3.12/site-packages/nvidia/cufft/lib')
    start=time.time();peak=0;stop_reason=None
    with mlflow.start_span(name=label) as span:
        span.set_inputs({'argv':argv,'cwd':str(REPO)})
        with (root/(label+'.stdout')).open('x') as out,(root/(label+'.stderr')).open('x') as err:
            process=subprocess.Popen(argv,cwd=REPO,env=env,stdout=out,stderr=err)
            while process.poll() is None:
                if memory_guard:
                    used,total=gpu_memory();peak=max(peak,used)
                    if total-used<1536:stop_reason='RESOURCE_HEADROOM_BREACH'
                if time.time()-start>timeout:stop_reason='BOUNDED_COMMAND_TIMEOUT'
                if stop_reason:
                    process.terminate()
                    try:process.wait(timeout=15)
                    except subprocess.TimeoutExpired:process.kill();process.wait()
                    break
                time.sleep(2)
            rc=process.wait()
        rec=dict(label=label,argv=argv,returncode=rc,seconds=time.time()-start,
                 gpu_peak_total_used_mib_sampled=peak,stop_reason=stop_reason,
                 scientific_interpreter=SCIENCE,trace_id=span.trace_id)
        span.set_outputs(rec)
    mlflow.flush_trace_async_logging()
    trace=mlflow.get_trace(rec['trace_id']);rec['verified_trace_spans']=len(trace.data.spans) if trace else 0
    write_new(root/'receipts'/(label+'.json'),rec)
    print(json.dumps(rec),flush=True)
    if rc or stop_reason:raise RuntimeError(f'{label}: exit={rc}; {stop_reason}')

def run_job(job,root):
    cfg_path=REPO/'configs/r3m15'/f'{job}.json';cfg=json.loads(cfg_path.read_text());validate_config(job,cfg)
    jobroot=root/job
    if jobroot.exists():raise FileExistsError('preserve existing job; reconcile before continuation')
    jobroot.mkdir();(jobroot/'receipts').mkdir()
    shutil.copy2(cfg_path,jobroot/'config.json')
    write_new(jobroot/'start.json',dict(job=job,config_sha256=sha(cfg_path),numerical_source_digest=SOURCE,
                 instrumentation={p.name:sha(p) for p in sorted((REPO/'scripts').glob('r3m1[345]*.py'))},
                 source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()))
    try:
        command('resource_preflight',[SCIENCE,'scripts/r3m15_resource_probe.py','--config',str(cfg_path),'--out',str(jobroot/'resource.json')],jobroot)
        command('prepare',[SCIENCE,'scripts/r3m13_initial_state_pair.py','prepare','--config',str(cfg_path),'--out',str(jobroot/'preparation')],jobroot)
        # No state substitution: v2 witness repeats inherited preparation and
        # requires identical typed bytes before the first collision step.
        for chunk in range(1,9):
            out=jobroot/'collision';label=f'collision.chunk{chunk:03d}'
            if chunk>1:verify_seal(out)
            command(label,[SCIENCE,'scripts/r3m14_collision_initial_witness.py','--config',str(cfg_path),'--prepared',str(jobroot/'preparation'),'--out',str(out),'--max-steps','128'],jobroot)
            state=verify_seal(out)
            witness=json.loads((out/'r3m14_initial_binding.json').read_text())
            if witness['status']!='PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED':raise ValueError('initial binding failure')
            snapshot=jobroot/'receipts'/f'{label}.checkpoint.json'
            names=['state.json','r3m11_checkpoint_seal.json','r3m14_initial_binding.json','r3m14_witness_run_receipt.json']
            write_new(snapshot,{name:{'sha256':sha(out/name),'content':json.loads((out/name).read_text())} for name in names})
            if (out/'result.json').exists():
                result=json.loads((out/'result.json').read_text())
                if result['status']!='completed' or state['done']!=state['nstep']:raise ValueError('invalid completion')
                write_new(jobroot/'COMPLETE.json',dict(job=job,chunks=chunk,restarts=chunk-1,nstep=state['done'],result_sha256=sha(out/'result.json')))
                break
        else:raise RuntimeError('eight chunk maximum reached')
    except BaseException as exc:
        write_new(jobroot/'FAILURE.json',{'type':type(exc).__name__,'message':str(exc),'retry_executed':False})
        raise

def main():
    p=argparse.ArgumentParser();p.add_argument('--job',choices=list(SPACING),required=True);p.add_argument('--root',type=Path,required=True)
    args=p.parse_args();root=args.root.resolve();root.mkdir(exist_ok=True)
    # The same root lock serializes the three large GPU jobs.
    with (root/'matrix.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if args.job!='A' and not (root/'A/COMPLETE.json').is_file():raise ValueError('A must complete first')
        import mlflow
        if not (os.environ.get('MLFLOW_TRACKING_URI') and os.environ.get('MLFLOW_EXPERIMENT_ID')):
            mlflow.set_tracking_uri('sqlite:///'+str(root/'mlflow.db'));mlflow.set_experiment('R3M15_CONTROLLED_SPATIAL')
        run_job(args.job,root)

if __name__=='__main__':main()
