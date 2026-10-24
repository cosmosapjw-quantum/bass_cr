"""Verify one canonical ZIP entirely in memory, restore bytes only to a new path."""
import argparse,hashlib,io,json,pathlib,zipfile

def main():
 p=argparse.ArgumentParser();p.add_argument('archive');p.add_argument('destination');a=p.parse_args();target=pathlib.Path(a.destination)
 if target.exists():raise FileExistsError('restore destination must not exist')
 raw=pathlib.Path(a.archive).read_bytes()
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  if z.testzip() is not None:raise ValueError('ZIP CRC failure')
  manifest=json.loads(z.read('MANIFEST.json'));members=manifest['payload'];names=[x['path'] for x in members]
  if len(set(z.namelist()))!=len(z.namelist()) or set(z.namelist())!=set(names)|{'MANIFEST.json'}:raise ValueError('member inventory mismatch')
  verified={}
  for entry in members:
   name=entry['path'];path=pathlib.PurePosixPath(name)
   if path.is_absolute() or '..' in path.parts:raise ValueError('invalid project-relative member')
   value=z.read(name)
   if len(value)!=entry['bytes'] or hashlib.sha256(value).hexdigest()!=entry['sha256']:raise ValueError('member digest mismatch: '+name)
   verified[name]=value
  verified['MANIFEST.json']=z.read('MANIFEST.json')
 target.mkdir(parents=True,exist_ok=False)
 for name,value in verified.items():
  p=target/name;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as stream:stream.write(value)
 print(json.dumps({'status':'RESTORED_VERIFIED_BYTES_ONLY','archive_sha256':hashlib.sha256(raw).hexdigest(),'members':len(verified),'destination':str(target.resolve()),'scientific_execution':False}))
if __name__=='__main__':main()
