"""Verify raw manifest and fresh self-contained NON-NATIVE package replay."""
import argparse
import hashlib
import json
import os
from pathlib import Path,PurePosixPath
import py_compile
import subprocess
import sys
import tempfile
import zipfile


def checked_payload(package):
    with zipfile.ZipFile(package) as z:
        if z.testzip() is not None:raise ValueError('ZIP CRC failure')
        names=z.namelist()
        if len(set(names))!=len(names):raise ValueError('duplicate ZIP member')
        for n in names:
            p=PurePosixPath(n)
            if p.is_absolute() or '..' in p.parts or '\\' in n:raise ValueError('unsafe ZIP member')
            info=z.getinfo(n)
            if (info.external_attr >> 16)&0o170000==0o120000:raise ValueError('ZIP symlink')
        m=json.loads(z.read('MANIFEST.json'))
        if set(names)!=set(m['files'])|{'MANIFEST.json'}:raise ValueError('manifest coverage mismatch')
        for n,pin in m['files'].items():
            b=z.read(n)
            if len(b)!=pin['bytes'] or hashlib.sha256(b).hexdigest()!=pin['sha256']:raise ValueError('manifest byte mismatch: '+n)
        return m,{n:z.read(n) for n in names}


def check_authority(manifest,payload):
    pins=json.loads(payload['SOURCE_PINS.json']);template=json.loads(payload['FUTURE_AUTHORIZATION_TEMPLATE.json'])
    for value in (pins,template):
        if any(value[k]!=manifest[k] for k in ('preparation_commit','preparation_tree')):raise ValueError('authority execution identity mismatch')
    if template['source_pins_sha256']!=hashlib.sha256(payload['SOURCE_PINS.json']).hexdigest():raise ValueError('authority source pin mismatch')
    for n,pin in pins['source_files'].items():
        if hashlib.sha256(payload[n]).hexdigest()!=pin:raise ValueError('source byte pin mismatch: '+n)
    for n,pin in template['contract_pins'].items():
        if hashlib.sha256(payload['receipts/'+n]).hexdigest()!=pin:raise ValueError('contract byte pin mismatch: '+n)
    proposed=template['operator_only']
    if proposed['status']!='USER_APPROVAL_REQUIRED' or any(proposed[k] is not None for k in ('authorization_id','cpus','workers','worker_ram_bytes','total_ram_cap_bytes','deadline_unix','wall_seconds','termination_grace_seconds','cost_scope')):
        raise ValueError('unapproved authority fields changed')
    if manifest['native_authorized'] is not False:raise ValueError('native scope mismatch')

def verify(package,expected_sha256=None):
    if expected_sha256 is not None and hashlib.sha256(Path(package).read_bytes()).hexdigest()!=expected_sha256:raise ValueError('external package SHA mismatch')
    manifest,payload=checked_payload(package)
    check_authority(manifest,payload)
    with tempfile.TemporaryDirectory(prefix='r4p0-fresh-extract-') as temporary:
        root=Path(temporary)
        for n,b in payload.items():
            p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        for i,name in enumerate(('preflight.py','prepare_closeout.py','make_preparation_package.py','verify_preparation_package.py')):
            py_compile.compile(str(root/name),cfile=str(root/('compile_'+str(i)+'.pyc')),doraise=True)
        env=os.environ.copy()
        for n in ('PYTHONPATH','R4P0_INPUT_DIR'):env.pop(n,None)
        env.update(PYTHONNOUSERSITE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
        command=[sys.executable,'-B','-m','pytest','-q','-p','no:cacheprovider','tests']
        r=subprocess.run(command,cwd=root,env=env,text=True,capture_output=True)
        if r.returncode:raise ValueError('extracted focused suite failed: '+r.stdout+r.stderr)
        cli=[sys.executable,'-B','prepare_closeout.py','--out',str(root/'smoke')]
        s=subprocess.run(cli,cwd=root,env=env,text=True,capture_output=True)
        if s.returncode:raise ValueError('extracted preparation CLI failed: '+s.stdout+s.stderr)
        receipt=json.loads(s.stdout)
        if receipt['native_operator_calls']!=0 or receipt['authorization_nonce_consumed']:raise ValueError('preparation boundary violation')
        if list(root.rglob('*CONSUMED*')):raise ValueError('nonce artifact created')
        return {'SELF_CONTAINED_TEST_REPLAY_VERIFIED':True,'zip_crc':'PASS','manifest_verification':'PASS',
                'manifest_verified_files':len(manifest['files']),'authority_verification':'PASS','external_package_sha_checked':expected_sha256 is not None,'py_compile':'PASS',
                'test_command':command,'test_exit':r.returncode,'test_output':r.stdout,'test_stderr':r.stderr,
                'cli_command':cli,'cli_exit':s.returncode,'native_operator_calls':0,
                'authorization_nonce_consumed':False,'external_PYTHONPATH_used':False,
                'preparation_commit':manifest['preparation_commit'],'preparation_tree':manifest['preparation_tree']}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('package');p.add_argument('--expected-sha256');a=p.parse_args()
    print(json.dumps(verify(a.package,a.expected_sha256),indent=2))
