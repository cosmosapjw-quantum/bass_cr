"""R4AG CLI: prepare -> explicit authorize -> run -> read-only collect."""
from __future__ import annotations
import argparse,fcntl,os,signal,subprocess,sys,time
from pathlib import Path
from common import ROOT,ContractError,read,sha,write_new
from runtime_contract import prepare_batch,authorize_batch,validate_batch
from collect import verify_node_payload,collect

def run_batch(batch_path,max_new_nodes=1):
    if type(max_new_nodes) is not int or not 1<=max_new_nodes<=10:raise ContractError('1..10 max new points')
    b=validate_batch(batch_path);base=Path(batch_path).resolve().parent;auth_path=base/'AUTHORIZATION.json'
    a=read(auth_path)
    if a['batch_sha256']!=sha(batch_path):raise ContractError('authorization binding')
    available={x['node_id'] for x in b['nodes']}
    if not set(a['authorized_nodes'])<=available or a['attempt_cap_per_node']!=1:raise ContractError('authorization scope')
    with (base/'COORDINATOR.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as e:raise ContractError('batch coordinator already active') from e
        started=time.monotonic();completed=[];launched=0
        for item in b['nodes']:
            if item['node_id'] not in a['authorized_nodes']:continue
            out=Path(item['output'])
            if out.exists():
                verify_node_payload(b,item) # raises for FAILED/PARTIAL, never silently retries
                completed.append({'node_id':item['node_id'],'action':'REUSED_COMPLETE_HASH_VERIFIED'});continue
            if launched>=max_new_nodes:break
            if time.monotonic()-started>b['resources']['batch_wall_seconds']:raise TimeoutError('batch wall budget')
            logfile=base/('launch_'+item['node_id']+'.log')
            with logfile.open('x') as log:
                proc=subprocess.Popen([sys.executable,str(ROOT/'source/point_engine.py'),item['contract'],str(auth_path)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
                try:rc=proc.wait(timeout=b['resources']['wall_seconds']+30)
                except BaseException:
                    os.killpg(proc.pid,signal.SIGTERM)
                    try:proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                    # A launcher attempt is never automatically repeated, even if
                    # failure occurred before the engine's reservation write.
                    if not out.exists():out.mkdir()
                    marker=out/'LAUNCH_INTERRUPTED.json'
                    if not marker.exists():write_new(marker,{'node_id':item['node_id'],'scientific_progress':'UNKNOWN','automatic_retry':False})
                    raise
            launched+=1
            if rc:
                if not out.exists():out.mkdir();write_new(out/'LAUNCH_FAILED.json',{'returncode':rc,'automatic_retry':False})
                raise ContractError('node failed; outputs retained and batch stopped: '+item['node_id'])
            packet=verify_node_payload(b,item)
            if packet is None:raise ContractError('missing completed node')
            completed.append({'node_id':item['node_id'],'action':'NEW_EXECUTION_RETURN_VERIFIED'})
            if not read(out/'RESULT.json')['target_met']:raise ContractError('valid enclosure too wide; no automatic escalation')
        return {'launched_this_command':launched,'nodes':completed,'M9_replays':0}

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
    q=sub.add_parser('prepare');q.add_argument('--output',required=True);q.add_argument('--workers',type=int,default=1)
    q=sub.add_parser('authorize');q.add_argument('--batch',required=True);q.add_argument('--confirm-sha256',required=True);q.add_argument('--nodes',nargs='+',required=True);q.add_argument('--authorize-native',action='store_true',required=True)
    q=sub.add_parser('run');q.add_argument('--batch',required=True);q.add_argument('--max-new-nodes',type=int,default=1)
    q=sub.add_parser('collect');q.add_argument('--batch',required=True);q.add_argument('--output',required=True)
    s=p.parse_args()
    if s.cmd=='prepare':r=prepare_batch(s.output,s.workers);print(r);print('SHA256='+sha(r));print('NO_SCIENTIFIC_EXECUTION')
    elif s.cmd=='authorize':print(authorize_batch(s.batch,s.confirm_sha256,s.nodes))
    elif s.cmd=='run':print(run_batch(s.batch,s.max_new_nodes))
    else:print(collect(s.batch,s.output)['available_nodes'])
if __name__=='__main__':main()
