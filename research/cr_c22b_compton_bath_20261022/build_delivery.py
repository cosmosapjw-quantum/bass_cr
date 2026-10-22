#!/usr/bin/env python3
"""Create a self-contained C22B handoff with preserved C22A context and Git bundle."""
import argparse
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
from zoneinfo import ZoneInfo
import zipfile
from verify_delivery import verify

HERE=Path(__file__).resolve().parent
REPO=HERE.parent.parent

def add_tree(files,folder):
    for p in sorted(folder.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
            files['repository/'+str(p.relative_to(REPO))]=p.read_bytes()

def build(out,bundle,publication_receipt):
    files={}
    add_tree(files,HERE)
    add_tree(files,HERE.parent/'cr_c22a_thermochemical_20261022')
    frozen=json.loads((HERE/'evidence/SOURCE_FREEZE.json').read_text())
    for row in frozen['files']:
        data=(REPO/row['path']).read_bytes()
        if len(data)!=row['size_bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('FROZEN_RUNTIME_DRIFT')
        files['repository/'+row['path']]=data
    files['publication/'+bundle.name]=bundle.read_bytes()
    files['publication/'+publication_receipt.name]=publication_receipt.read_bytes()
    files['verify_delivery.py']=(HERE/'verify_delivery.py').read_bytes()
    files['RESTORE_README.md']=('''# C22B delivery

This archive contains the new C22B scientific unit, its31frozen runtime files,
the preserved complete C22A unit used for matched baseline review, and a Git
bundle carrying local C22A+C22B commits after authoritativeR. Completed ODEs
must not be rerun just to restore evidence. C22A failures and rejected analysis
versions are preserved. C22B final analysis is analysis_v2.

Use the separately delivered final authority to obtain the ZIP SHA256 and size.
Run verify_delivery.py with those values. --restore-root requires a new directory
and uses the same in-memory bytes that passed SHA/size/CRC/member checks.
The verifier has no model, ODE or RHS calls. Git bundle verification is metadata
and object validation only, not remote publication.

Scientific scope is a prescribed isotropic external CMB thermostat. Full
thermochemical/radiative closure remains OPEN and global_error_bound=null.
Provider ACK/readback and remote GitHub publication are separately recorded in
C22B_FINAL_AUTHORITY_20261022.json; no triple-backup claim is implied.
''').encode()
    manifest={'schema':'BASS_CR_C22B_DELIVERY_MANIFEST_V1','created_KST':datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),
        'execution_source_identity':frozen['identity_sha256'],'scientific_status':'PASS_SCOPED',
        'new_C22B_trajectories':4,'old_ODE_replayed_for_recovery':0,'global_error_bound':None,
        'files':[{'path':name,'size_bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()} for name,data in sorted(files.items())]}
    with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,data in sorted(files.items()):z.writestr(name,data)
        z.writestr('MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    receipt=verify(out)
    receipt.update(publication_bundle_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),
        publication_bundle_bytes=bundle.stat().st_size,package_snapshot='BEFORE_FINAL_PROVIDER_ACK;finalauthoritysidecargoverns',
        created_KST=datetime.now(ZoneInfo('Asia/Seoul')).isoformat())
    target=out.with_suffix('.receipt.json')
    with target.open('x') as f:json.dump(receipt,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(receipt))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--bundle',type=Path,required=True);p.add_argument('--publication-receipt',type=Path,required=True)
    a=p.parse_args();build(a.out,a.bundle,a.publication_receipt)
