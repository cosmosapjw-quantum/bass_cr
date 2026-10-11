import zipfile,tarfile,stat,hashlib,json,time
from pathlib import Path
def safe(name,directory=False):
 p=Path(name);assert name and not p.is_absolute() and '..' not in p.parts and '\\' not in name and name.rstrip('/')==p.as_posix(),name
 return p
def restore(src,dst):
 start=time.monotonic();dst.mkdir(); files=[]
 if src.name.endswith('.zip'):
  with zipfile.ZipFile(src) as a:
   members=a.infolist();assert len(members)<=10000 and sum(v.file_size for v in members)<=1073741824
   assert len({v.filename for v in members})==len(members)
   for v in members:
    p=safe(v.filename,v.is_dir());mode=v.external_attr>>16;assert stat.S_IFMT(mode) in (0,stat.S_IFREG,stat.S_IFDIR) and (not stat.S_ISDIR(mode) or v.is_dir())
    target=dst/p
    if v.is_dir():target.mkdir(parents=True,exist_ok=True);continue
    b=a.read(v);target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as h:h.write(b)
    files.append({'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 else:
  with tarfile.open(src) as a:
   members=a.getmembers();assert len(members)<=10000 and sum(v.size for v in members)<=1073741824;assert len({v.name for v in members})==len(members)
   for v in members:
    p=safe(v.name,v.isdir());assert v.isfile() or v.isdir(),v.name
    target=dst/p
    if v.isdir():target.mkdir(parents=True,exist_ok=True);continue
    b=a.extractfile(v).read();target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as h:h.write(b)
    files.append({'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 return {'source':str(src),'destination':str(dst),'members':len(members),'files':files,'wall_s':time.monotonic()-start,'safe':True}
def check_manifest(path,root=None,exact=True):
 m=json.loads(path.read_text());root=root or path.parent; f=m['files'];f={v['path']:v for v in f} if isinstance(f,list) else f
 for name,v in f.items():
  p=root/safe(name);assert p.is_file(),p;b=p.read_bytes();assert len(b)==v['bytes'] and hashlib.sha256(b).hexdigest()==v['sha256'],p
 actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
 if exact:assert actual==set(f)|{path.relative_to(root).as_posix()},(path,len(actual),len(f),actual-set(f))
 return {'manifest':str(path),'schema':m.get('schema'),'listed':len(f),'bytes_sha256_verified':True,'exact':exact,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
