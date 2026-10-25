"""One bounded plotting child, with the implementation's resource policy."""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

unit = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(unit/'implementation'))
from dispatcher import resource_snapshot, child_limits, write_json, THREAD_ENV

run_id = 'n5_saved_output_plot_20261024_v2'
output = unit/'figures'/run_id
output.mkdir(exist_ok=False)
lease = unit/'implementation/.n5_local_lease'
fd = os.open(lease, os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600)
with os.fdopen(fd, 'w') as out:
    json.dump({'run_id': run_id, 'pid': os.getpid(), 'mode': 'plot_saved_output'}, out)
start, own_start = time.monotonic(), time.process_time()
before = resource.getrusage(resource.RUSAGE_CHILDREN)
status, error, code = 'NOT_RUN', None, None
try:
    snapshot = resource_snapshot()
    if not snapshot['memory_admission']['admitted'] or not {0,8}.issubset(snapshot['affinity']):
        raise RuntimeError('RESOURCE_ADMISSION_REJECTED')
    script = Path(__file__).with_name('plot_saved_results.py')
    write_json(output/'PRE_EXECUTION.json', {'run_id':run_id, 'resources':snapshot,
              'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(), 'new_science':False})
    os.sched_setaffinity(0, {8})
    env = os.environ.copy();env.update({key:'1' for key in THREAD_ENV})
    env['PYTHONDONTWRITEBYTECODE']='1';env['MPLCONFIGDIR']=str(output/'mpl_cache')
    with (output/'stdout.txt').open('x') as stdout, (output/'stderr.txt').open('x') as stderr:
        run = subprocess.run([sys.executable, '-B', str(script), '--output', str(output)],
              env=env, stdout=stdout, stderr=stderr, timeout=60, preexec_fn=child_limits)
    code=run.returncode;status='PASS' if code==0 else 'FAILED_RETAINED'
except Exception as exc:
    status='FAILED_RETAINED';error={'type':type(exc).__name__, 'message':str(exc)}
finally:
    lease.unlink()
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={'run_id':run_id, 'status':status, 'error':error, 'returncode':code,
        'worker_cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
        'coordinator_cpu_s':time.process_time()-own_start, 'wall_s':time.monotonic()-start,
        'peak_rss_kib':after.ru_maxrss, 'new_science':False,
        'EXECUTION':status, 'PUBLICATION':'PENDING', 'BACKUP':'PENDING', 'DAG':'NO_GATE_CHANGE'}
    write_json(output/'DISPATCH_RECEIPT.json',receipt)
    print(json.dumps(receipt))
raise SystemExit(0 if status=='PASS' else 1)
