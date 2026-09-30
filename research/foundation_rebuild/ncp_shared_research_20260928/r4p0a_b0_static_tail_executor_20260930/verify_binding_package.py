"""Fresh NON-NATIVE replay of binding package; never invokes the science launcher."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,os,py_compile,subprocess,sys,tempfile,zipfile

def verify(archive,expected):
    if hashlib.sha256(Path(archive).read_bytes()).hexdigest()!=expected:raise ValueError('external package SHA mismatch')
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('ZIP CRC failed')
        names=z.namelist();manifest=json.loads(z.read('MANIFEST.json'))
        if len(set(names))!=len(names) or set(names)!=set(manifest['files'])|{'MANIFEST.json'}:raise ValueError('manifest coverage/duplicate mismatch')
        for n,pin in manifest['files'].items():
            if PurePosixPath(n).is_absolute() or '..' in PurePosixPath(n).parts or '\\' in n:raise ValueError('unsafe member')
            b=z.read(n)
            if len(b)!=pin['bytes'] or hashlib.sha256(b).hexdigest()!=pin['sha256']:raise ValueError('manifest byte mismatch: '+n)
        pins=json.loads(z.read('SOURCE_PINS.json'));proposal=json.loads(z.read('AUTHORIZATION_PROPOSAL.json'));proposal_pin=json.loads(z.read('PROPOSAL_PIN.json'))
        for doc in (pins,proposal):
            if any(doc[k]!=manifest[k] for k in ('execution_commit','execution_tree')):raise ValueError('authority identity mismatch')
        if proposal['source_pins_sha256']!=hashlib.sha256(z.read('SOURCE_PINS.json')).hexdigest():raise ValueError('authority source hash mismatch')
        if proposal_pin['proposal_sha256']!=hashlib.sha256(z.read('AUTHORIZATION_PROPOSAL.json')).hexdigest():raise ValueError('authority proposal hash mismatch')
        for n,pin in pins['source_files'].items():
            if hashlib.sha256(z.read('source/'+n)).hexdigest()!=pin:raise ValueError('pinned source byte mismatch')
        with tempfile.TemporaryDirectory(prefix='b0-tail-fresh-') as temp:
            root=Path(temp);z.extractall(root)
            side=root/'source/research/foundation_rebuild/ncp_shared_research_20260928/r4p0a_b0_static_tail_executor_20260930'
            for i,n in enumerate(('static_tail.py','tail_worker.py','run_tail.py','supervise_tail.py','prepare_authority.py')):
                py_compile.compile(str(side/n),cfile=str(root/('compile_'+str(i)+'.pyc')),doraise=True)
            env=os.environ.copy()
            for k in ('PYTHONPATH','BASS_ANALYTIC_SOURCE_ROOT','ALLOW_NEW_NATIVE_R4P0','R4P0_APPROVED_PROPOSAL_SHA256'):env.pop(k,None)
            env.update(PYTHONNOUSERSITE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',R4P0A_RUNTIME_INPUTS=str(root/'runtime_inputs'),R4P0A_NATIVE_BUILD=str(root/'native_build'))
            command=[sys.executable,'-B','-m','pytest','-q','-p','no:cacheprovider',str(side/'tests')]
            result=subprocess.run(command,cwd=root/'source',env=env,text=True,capture_output=True)
            if result.returncode:raise ValueError('fresh binding suite failed: '+result.stdout+result.stderr)
            if list(root.rglob('AUTHORIZATION_CONSUMED.json')):raise ValueError('nonce created in package replay')
            return {'SELF_CONTAINED_TEST_REPLAY_VERIFIED':True,'zip_crc':'PASS','manifest_verified_files':len(manifest['files']),
                    'authority_verification':'PASS','py_compile':'PASS','test_command':command,'test_output':result.stdout,'test_exit':result.returncode,
                    'native_operator_calls':0,'new_authorization_consumed':0,'external_PYTHONPATH_used':False,
                    'execution_commit':manifest['execution_commit'],'execution_tree':manifest['execution_tree']}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('archive');p.add_argument('--expected-sha256',required=True);a=p.parse_args()
    print(json.dumps(verify(a.archive,a.expected_sha256),indent=2))
