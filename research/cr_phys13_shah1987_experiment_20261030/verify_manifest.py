#!/usr/bin/env python3
import argparse,zipfile,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('archive',type=Path);a=p.parse_args()
with zipfile.ZipFile(a.archive) as z:
    if z.testzip():raise SystemExit('CRC_FAIL')
    entries=json.loads(z.read('SOURCE_MANIFEST.json'))['members']
    for e in entries:
        d=z.read('research/cr_phys13_shah1987_experiment_20261030/'+e['path'])
        if len(d)!=e['size'] or hashlib.sha256(d).hexdigest()!=e['sha256']:raise SystemExit('SHA_OR_SIZE_FAIL:'+e['path'])
    print('MANIFEST',len(entries),'/',len(entries),'CRC_SHA_SIZE_PASS')
