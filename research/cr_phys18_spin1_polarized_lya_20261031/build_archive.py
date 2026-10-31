import json,hashlib,zipfile,sys
from pathlib import Path
P=Path(__file__).resolve().parent
prefix='research/cr_phys18_spin1_polarized_lya_20261031/'
target=Path(sys.argv[1]);items=[]
for p in sorted(P.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.name.endswith(('.pyc','.log')):continue
 b=p.read_bytes();items.append((p.relative_to(P).as_posix(),b))
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for rel,b in items:
  meta=zipfile.ZipInfo(prefix+rel,date_time=(1980,1,1,0,0,0));meta.compress_type=zipfile.ZIP_DEFLATED;z.writestr(meta,b,compress_type=zipfile.ZIP_DEFLATED,compresslevel=7)
 manifest={'unit':'PHYS18_SPIN1_CONDITIONAL','original_copyright_1976_PDF_included':False,'members':[{'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()} for rel,b in items]}
 meta=zipfile.ZipInfo('SOURCE_MANIFEST.json',date_time=(1980,1,1,0,0,0));meta.compress_type=zipfile.ZIP_DEFLATED;z.writestr(meta,(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode())
print('ARCHIVE_CREATED',target,len(items),'bytes',target.stat().st_size,'sha256',hashlib.sha256(target.read_bytes()).hexdigest())
