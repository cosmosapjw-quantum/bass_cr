"""Trace the outer command only; canonical scientific subprocess stays unchanged."""
import json, os, subprocess, sys, time
from pathlib import Path
os.environ['MLFLOW_DISABLE_AGENT_HINT']='1'
import mlflow
OUT=Path('/mnt/sn850x2t/bass_cr_r3m14_20260922')
mlflow.set_tracking_uri('sqlite:///'+str(OUT/'mlflow.db'))
experiment=mlflow.set_experiment('R3M14_PRODUCTION_DX025_INITIAL_PAIR_AND_COLLISION_RETURN')
label=sys.argv[1]
argv=sys.argv[2:]
env=os.environ.copy()
env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH='.',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',LD_LIBRARY_PATH='/home/cosmosapjw/cosmo_lab/.venv/lib/python3.12/site-packages/nvidia/cufft/lib')
start=time.time()
with mlflow.start_span(name=label) as span:
    span.set_inputs({'argv':argv,'cwd':str(OUT/'worktree'),'environment':{k:env[k] for k in ['PYTHONDONTWRITEBYTECODE','PYTHONPATH','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','LD_LIBRARY_PATH']}})
    with (OUT/(label+'.stdout')).open('x') as stdout, (OUT/(label+'.stderr')).open('x') as stderr:
        run=subprocess.run(argv,cwd=OUT/'worktree',env=env,stdout=stdout,stderr=stderr)
    result={'returncode':run.returncode,'started_unix':start,'ended_unix':time.time(),'stdout':(OUT/(label+'.stdout')).read_text(),'stderr':(OUT/(label+'.stderr')).read_text()}
    span.set_outputs(result)
    trace_id=span.trace_id
mlflow.flush_trace_async_logging()
trace=mlflow.get_trace(trace_id)
assert trace and len(trace.data.spans)==1
result.update(label=label,argv=argv,trace_id=trace_id,trace_spans=len(trace.data.spans),experiment_id=experiment.experiment_id)
(OUT/'receipts'/(label+'.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['stdout','stderr']},indent=2))
sys.exit(run.returncode)
