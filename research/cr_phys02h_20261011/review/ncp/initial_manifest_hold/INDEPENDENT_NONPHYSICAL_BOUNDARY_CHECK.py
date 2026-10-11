"""One bounded reviewer reproduction of frozen NCP failure-boundary defects.

Mocks execute no OS child or scientific code. Collector fixtures contain only
literal tiny text/binary files. The immutable snapshot is used, not mutable work.
"""
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock
import hashlib
import importlib.util
import json
import signal
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def run():
    assert sha(HERE/'ncp/qualify_parallel.py')=='7a986b12852ad6163ad2808ac47239ff43e64e584b6e414a700bb03754b75ec3'
    assert sha(HERE/'ncp/run_and_collect.py')=='31955b87e51cffbbaf6e671b8f6e016c0622fe51d24c2cf00f00cd363d49112b'
    assert sha(HERE/'ncp/EXECUTION_SOURCE_MANIFEST.json')=='0a0281dccbbae4f53a167bdb0af421c2cf760f0ca0926c9be08f716887aab280'
    q=load('qualify_parallel',HERE/'ncp/qualify_parallel.py')
    wrapper=load('reviewer_frozen_ncp_wrapper',HERE/'ncp/run_and_collect.py')
    assert 'numpy' not in sys.modules and 'parallel_operator' not in sys.modules
    results=[]
    with tempfile.TemporaryDirectory() as temp:
        base=Path(temp)
        root=base/'source';root.mkdir()
        runpath=base/'run';out=base/'out'
        class AlreadyDeadQualifier:
            pid=260001
            returncode=-9
            def __init__(self,*args,**kwargs):
                runpath.mkdir()
                (runpath/'PROCESS_EVENTS.jsonl').write_text(json.dumps({'pid':260002,'process_group':260002})+'\n')
            def poll(self):return self.returncode
        with mock.patch.object(wrapper.subprocess,'Popen',side_effect=AlreadyDeadQualifier), \
             mock.patch.object(wrapper.os,'killpg') as kills, \
             mock.patch.object(wrapper,'collect',return_value={'mock_collection':True}) as collect:
            returned=wrapper.execute_and_collect(root,runpath,out)
        assert returned['actual_exit']==-9 and kills.call_count==0 and collect.call_count==1
        results.append({'case':'qualifier_already_died_with_logged_separate_lane',
                        'qualifier_returncode':-9,'owned_group_kill_calls':kills.call_count,
                        'collection_calls':collect.call_count,
                        'finding':'Collection starts without cleaning the recorded lane group.'})
    for bad_file in ('START.json','READY','EXECUTION_MANIFEST','INPUT_MANIFEST'):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);root=base/'source';root.mkdir();runpath=base/'run';runpath.mkdir();out=base/'out'
            (runpath/'partial.npy').write_bytes(b'NONPHYSICAL_LITERAL_PARTIAL\x00\xff')
            if bad_file=='START.json':
                (runpath/'START.json').write_text('{\n')
            else:
                ready=root/q.READY_REL;ready.parent.mkdir(parents=True)
                if bad_file=='READY':
                    ready.write_text('{\n')
                else:
                    group='execution_manifest' if bad_file=='EXECUTION_MANIFEST' else 'input_manifest'
                    name='fixture/'+group+'.json';path=root/name;path.parent.mkdir();path.write_text('{\n')
                    ready.write_text(json.dumps({group:{'path':name,**q.file_identity(path)}}))
            observed=None
            try:wrapper.collect(root,runpath,out)
            except Exception as error:observed={'type':type(error).__name__,'message':str(error)}
            assert observed and observed['type']=='JSONDecodeError'
            assert not list(out.glob('*.zip'))
            results.append({'case':'truncated_'+bad_file,'error':observed,
                            'raw_partial_exists':True,'archive_created':False,
                            'finding':'Malformed metadata aborts collection instead of preserving raw evidence.'})
    with tempfile.TemporaryDirectory() as temp:
        base=Path(temp);root=base/'source';root.mkdir();runpath=base/'run';out=base/'out'
        class TimedOutQualifier:
            pid=270001
            returncode=None
            def __init__(self,*args,**kwargs):
                runpath.mkdir()
                (runpath/'PROCESS_EVENTS.jsonl').write_text('{\n'+json.dumps({'pid':270002,'process_group':270002})+'\n')
            def poll(self):return self.returncode
            def terminate(self):self.returncode=-15
            def wait(self,timeout=None):return self.returncode
        observed=None
        with mock.patch.object(wrapper.subprocess,'Popen',side_effect=TimedOutQualifier), \
             mock.patch.object(wrapper.time,'monotonic',side_effect=[0,901]), \
             mock.patch.object(wrapper.os,'killpg') as kills, \
             mock.patch.object(wrapper,'collect',return_value={'mock_collection':True}) as collect:
            try:wrapper.execute_and_collect(root,runpath,out)
            except Exception as error:observed={'type':type(error).__name__,'message':str(error)}
        assert observed and observed['type']=='JSONDecodeError'
        assert kills.call_count==0 and collect.call_count==0
        assert not list(out.glob('LAUNCH_*/WRAPPER_ACTUAL_EXIT.json'))
        results.append({'case':'malformed_process_event_before_valid_owned_group',
                        'error':observed,'later_owned_group_kill_calls':kills.call_count,
                        'collection_calls':collect.call_count,'terminal_wrapper_receipt_created':False,
                        'deadline_is_mocked':True,'finding':'One malformed event blocks later cleanup and failure collection.'})
    return {'cases':results,'reproduced_cases':len(results),
            'new_OS_children':0,'new_physical_calls':0,'producer_test_reruns':0,
            'runtime_modules_absent':[name for name in ('numpy','scipy','parallel_operator') if name not in sys.modules]}


if __name__=='__main__':
    started=datetime.now(timezone.utc).isoformat();t0=time.monotonic()
    receipt={'schema':'cr-phys02h-independent-ncp-boundary-check.v1','start_utc':started,
             'command':sys.argv,'timeout_s':60,'execution_count':1,'script_sha256':sha(__file__),
             'frozen_execution_manifest_sha256':'0a0281dccbbae4f53a167bdb0af421c2cf760f0ca0926c9be08f716887aab280'}
    signal.signal(signal.SIGALRM,lambda signum,frame:(_ for _ in ()).throw(TimeoutError('60s nonphysical review limit')))
    signal.alarm(60)
    try:
        receipt.update(run(),status='BLOCKING_FAILURE_BOUNDARIES_REPRODUCED',actual_exit=0)
    except BaseException as error:
        receipt.update(status='REVIEW_FIXTURE_FAILURE_PRESERVED',actual_exit=1,error=repr(error))
        raise
    finally:
        signal.alarm(0)
        receipt.update(end_utc=datetime.now(timezone.utc).isoformat(),wall_s=time.monotonic()-t0)
        with (HERE/'INDEPENDENT_BOUNDARY_RECEIPT.json').open('x') as f:
            json.dump(receipt,f,indent=2,ensure_ascii=False);f.write('\n')
        print(json.dumps({k:receipt[k] for k in ('status','actual_exit','wall_s')}))
