"""Authenticated create-only Dropbox download with exact SHA-256/size checks.

Use connected Dropbox tools or an existing local sync first. This fallback
uses only an already-configured DROPBOX_ACCESS_TOKEN, never prints that token,
and never creates shares or credentials. IDs and digests come from a receipt.
"""
from pathlib import Path
import argparse,hashlib,json,os,sys,urllib.request

def download(file_id,expected_sha256,expected_bytes,output):
    if not isinstance(file_id,str) or not file_id.startswith('id:'):raise ValueError('exact Dropbox file ID required')
    if len(expected_sha256)!=64 or any(c not in '0123456789abcdef' for c in expected_sha256):raise ValueError('SHA256 required')
    if expected_bytes<=0:raise ValueError('positive byte length required')
    output=Path(output)
    if output.exists() or output.with_name(output.name+'.part').exists():raise FileExistsError('create-only target')
    token=os.environ.get('DROPBOX_ACCESS_TOKEN')
    if not token:raise ValueError('use connected Dropbox or existing sync; no configured DROPBOX_ACCESS_TOKEN')
    req=urllib.request.Request('https://content.dropboxapi.com/2/files/download',data=b'',method='POST',
        headers={'Authorization':'Bearer '+token,'Dropbox-API-Arg':json.dumps({'path':file_id})})
    h=hashlib.sha256();n=0;part=output.with_name(output.name+'.part')
    with urllib.request.urlopen(req,timeout=60) as response,part.open('xb') as f:
        while True:
            b=response.read(1024*1024)
            if not b:break
            n+=len(b)
            if n>expected_bytes:raise ValueError('download exceeds expected size; .part retained')
            h.update(b);f.write(b)
    if n!=expected_bytes or h.hexdigest()!=expected_sha256:raise ValueError('download identity mismatch; .part retained')
    # Hard-link gives atomic create-only publication without overwriting a race.
    os.link(part,output);part.unlink()
    return {'file_id':file_id,'bytes':n,'sha256':h.hexdigest(),'output':str(output),'status':'DOWNLOAD_BYTES_VERIFIED'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--id',required=True);p.add_argument('--sha256',required=True);p.add_argument('--bytes',required=True,type=int);p.add_argument('--output',required=True)
    a=p.parse_args()
    try:print(json.dumps(download(a.id,a.sha256,a.bytes,a.output)))
    except Exception as e:
        # Never emit Request headers or authentication values.
        print(type(e).__name__+': '+str(e),file=sys.stderr);sys.exit(2)
