import hashlib,json,zipfile,sys
from pathlib import Path
ZIP=Path(sys.argv[1]);prefix='research/cr_phys18_spin1_polarized_lya_20261031/'
with zipfile.ZipFile(ZIP) as z:
 assert z.testzip() is None,'ZIP_CRC'
 m=json.loads(z.read('SOURCE_MANIFEST.json'))['members']
 assert set(z.namelist())=={'SOURCE_MANIFEST.json'}|{prefix+x['path'] for x in m}
 for x in m:
  b=z.read(prefix+x['path']);assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'],x['path']
 b=z.read(prefix+'sources/PR142_PHYS17_SOURCE.zip')
 assert hashlib.sha256(b).hexdigest()=='5fc70cfa638f6b6fffbc61f05f46d28a9be1eefef43851a75bb175383d87666d'
print('ARCHIVE_EXACT',len(m),'/',len(m),'bytes',ZIP.stat().st_size,'sha256',hashlib.sha256(ZIP.read_bytes()).hexdigest())
