#!/usr/bin/env python3
"""Create canonical recovery ZIP, or verify independently downloaded bytes. Stdlib only."""
import argparse, hashlib, json, pathlib, sys, time, zipfile

def sha(b): return hashlib.sha256(b).hexdigest()
def excluded(p): return '__pycache__' in p.parts or 'mpl_cache' in p.parts or p.suffix=='.pyc'
def require(ok,msg):
    if not ok: raise ValueError(msg)
def safe_name(name):
    p=pathlib.PurePosixPath(name)
    require(name and not p.is_absolute() and '..' not in p.parts and '\\' not in name,'invalid archive name')
    return str(p)
def jbytes(x): return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def main():
    start=time.process_time(); p=argparse.ArgumentParser(description=__doc__); sp=p.add_subparsers(dest='command',required=True)
    b=sp.add_parser('build'); b.add_argument('--unit',required=True); b.add_argument('--unit-prefix',default='research/cr_n5_rate_semantics_20261024'); b.add_argument('--receipt',action='append',default=[],help='ARCHIVE_NAME=LOCAL_PATH; repeatable')
    b.add_argument('--variant',choices=['initial','final'],required=True); b.add_argument('--variant-id',required=True); b.add_argument('--out',required=True)
    v=sp.add_parser('verify'); v.add_argument('--zip',required=True); v.add_argument('--expected-json',required=True,help='saved build stdout, which provides exact ZIP bytes and SHA256')
    a=p.parse_args()
    if a.command=='build':
        unit=pathlib.Path(a.unit); require(unit.is_dir(),'unit directory missing'); payload={}
        prefix=safe_name(a.unit_prefix)
        for f in sorted(unit.rglob('*')):
            rel=f.relative_to(unit)
            if f.is_file() and not excluded(rel): payload[safe_name(prefix+'/'+rel.as_posix())]=f.read_bytes()
        require(payload,'empty unit')
        for spec in a.receipt:
            name,sep,local=spec.partition('=');require(sep,'receipt requires ARCHIVE_NAME=LOCAL_PATH'); name=safe_name(name)
            require(name not in payload and name!='MANIFEST.json','duplicate/reserved receipt name');require(not excluded(pathlib.PurePosixPath(name)),'excluded receipt name')
            payload[name]=pathlib.Path(local).read_bytes()
        require('MANIFEST.json' not in payload,'reserved manifest path')
        manifest={'schema':'N5_CANONICAL_RECOVERY_MANIFEST_V1','variant':a.variant,'variant_id':a.variant_id,'files':{n:{'bytes':len(data),'sha256':sha(data)} for n,data in sorted(payload.items())},'exclusions':['__pycache__','.pyc','mpl_cache']}
        payload['MANIFEST.json']=jbytes(manifest); out=pathlib.Path(a.out)
        # Opening exclusively also ensures a prior archive is never replaced.
        with out.open('xb') as stream:
            with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
                for name,data in sorted(payload.items()):
                    info=zipfile.ZipInfo(name,date_time=(2026,10,24,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
                    z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        data=out.read_bytes()
        result={'schema':'N5_CANONICAL_ZIP_BUILD_RECEIPT_V1','variant':a.variant,'variant_id':a.variant_id,'zip_bytes':len(data),'zip_sha256':sha(data),'payload_count':len(payload)-1,'manifest_sha256':sha(payload['MANIFEST.json']),'local_path':str(out.resolve())}
    else:
        expected=json.loads(pathlib.Path(a.expected_json).read_bytes()); data=pathlib.Path(a.zip).read_bytes()
        require(len(data)==expected['zip_bytes'],'ZIP size differs from canonical build')
        require(sha(data)==expected['zip_sha256'],'ZIP SHA256 differs from canonical build')
        with zipfile.ZipFile(a.zip) as z:
            names=z.namelist(); require(len(names)==len(set(names)),'duplicate archive names')
            require(z.testzip() is None,'ZIP CRC failure'); require('MANIFEST.json' in names,'missing manifest')
            mb=z.read('MANIFEST.json'); require(sha(mb)==expected['manifest_sha256'],'manifest differs')
            manifest=json.loads(mb); files=manifest['files']; require(set(files)==set(names)-{'MANIFEST.json'},'manifest/payload set mismatch')
            for name,row in files.items():
                require(safe_name(name)==name and not excluded(pathlib.PurePosixPath(name)),'excluded or noncanonical payload')
                b=z.read(name); require(len(b)==row['bytes'] and sha(b)==row['sha256'],'payload mismatch: '+name)
            require(len(files)==expected['payload_count'],'payload count differs')
        result={'schema':'N5_CANONICAL_ZIP_READBACK_RECEIPT_V1','status':'PASS','variant':manifest['variant'],'variant_id':manifest['variant_id'],'zip_bytes':len(data),'zip_sha256':sha(data),'CRC':'PASS','all_manifest_payloads':'PASS','payload_count':len(files),'readback_path':str(pathlib.Path(a.zip).resolve()),'independent_download':'CALLER_ATTESTED; helper verifies actual supplied bytes, not remote provenance'}
    result.update(requested_model='gpt-6.1-sol',observed_runtime_model='UNOBSERVED',helper_process_cpu_s=time.process_time()-start)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,zipfile.BadZipFile) as e:sys.exit(str(e))
