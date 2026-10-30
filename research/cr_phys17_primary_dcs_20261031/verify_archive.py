#!/usr/bin/env python3
import sys,json,hashlib,zipfile
from pathlib import Path
PRE='research/cr_phys17_primary_dcs_20261031/'
p=Path(sys.argv[1]);b=p.read_bytes()
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None,'CRC_ERROR'
 m=json.loads(z.read('SOURCE_MANIFEST.json'))['members']
 assert set(z.namelist())=={'SOURCE_MANIFEST.json'}|{PRE+x['path'] for x in m}
 for x in m:
  bb=z.read(PRE+x['path']);assert len(bb)==x['size'] and hashlib.sha256(bb).hexdigest()==x['sha256'],x['path']
 orig=z.read(PRE+'sources/PR141_PHYS16_SOURCE.zip')
 assert hashlib.sha256(orig).hexdigest()=='3b316c595fc1b40109f39d91af92873ba5a215281040d70bcb177dd1ab74a7dc'
print('ARCHIVE_MANIFEST_PASS',len(m),'/',len(m),'bytes',len(b),'sha256',hashlib.sha256(b).hexdigest())
