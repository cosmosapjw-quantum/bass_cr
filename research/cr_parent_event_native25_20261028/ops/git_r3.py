"""Actual immutable public-blob GET readback; metadata work, no scientific replay."""
import argparse,concurrent.futures,datetime,hashlib,json,pathlib,urllib.request

p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--sha',required=True);p.add_argument('--repo-root',required=True,type=pathlib.Path);p.add_argument('--paths-json',required=True,type=pathlib.Path);p.add_argument('--output',required=True,type=pathlib.Path);a=p.parse_args()
paths=json.loads(a.paths_json.read_text());assert all(isinstance(x,str) and '..' not in pathlib.PurePosixPath(x).parts for x in paths)
def one(path):
 local=(a.repo_root/path).read_bytes()
 url='https://raw.githubusercontent.com/'+a.repository+'/'+a.sha+'/'+path
 with urllib.request.urlopen(url,timeout=45) as response:
  raw=response.read();status=response.status
 expected=hashlib.sha256(local).hexdigest();actual=hashlib.sha256(raw).hexdigest();assert status==200 and local==raw,(path,len(local),len(raw),expected,actual)
 return {'path':path,'bytes':len(raw),'sha256':actual,'git_blob_sha1':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'HTTP_status':status,'full_GET':True,'identical':True}
rows=list(concurrent.futures.ThreadPoolExecutor(max_workers=8).map(one,paths))
r={'schema':'CR_PARENT_EVENT_GIT_RAW_R3_V1','unit':'CR_PHYS02_PARENT_EVENT_NATIVE25_V1','repository':a.repository,'commit':a.sha,'verification_tier':'R3','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'full_public_blobs':len(rows),'all_bytes_equal':True,'files':rows,'scientific_replay':0}
a.output.parent.mkdir(parents=True,exist_ok=True)
with a.output.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps({'commit':a.sha,'blobs':len(rows),'R3':'PASS','receipt':str(a.output)}))
