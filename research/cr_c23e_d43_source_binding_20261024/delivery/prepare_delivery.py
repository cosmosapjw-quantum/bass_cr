#!/usr/bin/env python3
"""Mechanical publication payload and closed ZIP assembly; never runs science."""
import argparse,base64,datetime,hashlib,json,pathlib,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
PREFIX='research/cr_c23e_d43_source_binding_20261024'

def selected():
    cfg=json.loads((ROOT/'delivery/PUBLIC_FILES.json').read_text())
    paths=set(cfg['files'])
    for pattern in cfg['include_globs']:
        paths.update(str(p.relative_to(ROOT)) for p in ROOT.glob(pattern) if p.is_file())
    def allowed(s):
        return '__pycache__' not in pathlib.PurePosixPath(s).parts and not s.endswith(('.pyc','.zip')) and '_private' not in s
    paths=sorted(s for s in paths if allowed(s))
    for s in paths:
        p=ROOT/s
        if not p.is_file() or p.is_symlink(): raise ValueError('Missing/nonregular selected file: '+s)
    return paths

def tree():
    entries=[]; blobs=[]
    for s in selected():
        b=(ROOT/s).read_bytes(); path=PREFIX+'/'+s
        try: text=b.decode('utf-8')
        except UnicodeDecodeError:
            oid=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
            blobs.append({'path':path,'sha':oid,'content':base64.b64encode(b).decode(),'encoding':'base64'})
            entries.append({'path':path,'mode':'100644','type':'blob','sha':oid})
        else: entries.append({'path':path,'mode':'100644','type':'blob','content':text})
    print(json.dumps({'prefix':PREFIX,'instructions':'Create each binary blob with its base64 payload and verify returned SHA before create_tree; text entries are ready.','entries':entries,'binary_blob_payloads':blobs},ensure_ascii=False))

def package(sha):
    if len(sha)!=40 or any(x not in '0123456789abcdef' for x in sha): raise ValueError('Exact 40-character science SHA required')
    files=selected(); stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    name='BASS_CR_C23E_D43_SOURCE_BINDING_DELIVERY_'+stamp
    dest=ROOT/'delivery'/name; dest.mkdir(exist_ok=False)
    manifest={'science_sha':sha,'publication_prefix':PREFIX,'created_at_utc':stamp,'scope':'Frozen C23E conditional D43 source binding; parent N5 remains partial','members':[{'path':s,'size_bytes':(ROOT/s).stat().st_size,'sha256':hashlib.sha256((ROOT/s).read_bytes()).hexdigest()} for s in files]}
    notice='Historical V1 contract/code are CANCELLED/SUPERSEDED. Preserve for diagnosis only; do not run superseded V1. Active contract is FROZEN_CONTRACT.md.\n'
    manifest['members'].append({'path':'HISTORY_CANCELLATION_NOTICE.txt','size_bytes':len(notice.encode()),'sha256':hashlib.sha256(notice.encode()).hexdigest()})
    mb=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode(); (dest/'MANIFEST.json').write_bytes(mb)
    zp=dest/(name+'.zip')
    with zipfile.ZipFile(zp,'x',zipfile.ZIP_DEFLATED) as z:
        for s in files:z.write(ROOT/s,s)
        z.writestr('HISTORY_CANCELLATION_NOTICE.txt',notice); z.writestr('MANIFEST.json',mb)
    with zipfile.ZipFile(zp) as z:
        assert z.testzip() is None
        assert set(z.namelist())=={x['path'] for x in manifest['members']}|{'MANIFEST.json'}
        for x in manifest['members']:
            b=z.read(x['path']); assert len(b)==x['size_bytes'] and hashlib.sha256(b).hexdigest()==x['sha256']
    print(json.dumps({'zip':str(zp),'manifest':str(dest/'MANIFEST.json'),'bytes':zp.stat().st_size,'sha256':hashlib.sha256(zp.read_bytes()).hexdigest(),'crc':'PASS','closed_members':'PASS','payload_count':len(manifest['members'])}))

p=argparse.ArgumentParser(); p.add_argument('command',choices=['list','tree','package']); p.add_argument('--science-sha'); a=p.parse_args()
if a.command=='list':print(json.dumps(selected(),indent=2))
elif a.command=='tree':tree()
else:
    if not a.science_sha:p.error('package requires --science-sha')
    package(a.science_sha)
