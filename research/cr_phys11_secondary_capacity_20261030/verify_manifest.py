#!/usr/bin/env python3
import hashlib,json,sys,zipfile
from pathlib import Path
p=Path(sys.argv[1]); prefix='research/cr_phys11_secondary_capacity_20261030/'
with zipfile.ZipFile(p) as z:
    assert z.testzip() is None,'ZIP_CRC_FAIL'
    m=json.loads(z.read('SOURCE_MANIFEST.json'))
    for row in m['members']:
        data=z.read(prefix+row['path'])
        assert hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
        assert len(data)==row['size'],row['path']
    assert m['original_parent_SHA256']=='faf883bec9aa8852792856c170bcf4974b7b95c40c611790e23d6afb11197033'
print('MANIFEST_CRC_PASS',len(m['members']))
