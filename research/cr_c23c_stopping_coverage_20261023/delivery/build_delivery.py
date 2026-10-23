"""Create-only delivery from an explicit immutable file catalog; never run science."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--catalog',required=True,type=Path)
    p.add_argument('--root',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();rows=json.loads(a.catalog.read_text())['files']
    names=[r['archive_path'] for r in rows]
    if len(names)!=len(set(names)):raise ValueError('duplicate archive path')
    manifest={'schema':'C23C_DELIVERY_MANIFEST_V1','created_utc':datetime.now(timezone.utc).isoformat(),
      'catalog_sha256':hashlib.sha256(a.catalog.read_bytes()).hexdigest(),
      'scope':'explicit C23C source/input/output/provenance payload; historical science reruns zero',
      'files':[]}
    bodies=[]
    for row in rows:
        path=(a.root/row['local_path']).resolve()
        if a.root.resolve() not in path.parents:raise ValueError('source outside declared root')
        b=path.read_bytes();h=hashlib.sha256(b).hexdigest()
        if len(b)!=row['bytes'] or h!=row['sha256']:raise ValueError('catalog drift: '+row['local_path'])
        names=row['archive_path'].split('/')
        if row['archive_path'].startswith('/') or '..' in names or '\\' in row['archive_path']:
            raise ValueError('unsafe archive path')
        manifest['files'].append({'path':row['archive_path'],'bytes':len(b),'sha256':h})
        bodies.append((row['archive_path'],b))
    with zipfile.ZipFile(a.output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,b in bodies:z.writestr(name,b)
        z.writestr('MANIFEST.json',json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    b=a.output.read_bytes()
    print(json.dumps({'archive':str(a.output),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),
                      'payload_files':len(bodies),'new_science_executions':0,'new_ODE':0},indent=2))


if __name__=='__main__':main()
