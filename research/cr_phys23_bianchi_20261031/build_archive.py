from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json,os
ROOT=Path(__file__).resolve().parent
ARCH=ROOT.parent/'BASS_CR_PHYS23_BIANCHI_I_LYA_SOURCE_CONDITIONAL_FULL_20261031.zip'
files=[]
for p in ROOT.rglob('*'):
 if not p.is_file() or '__pycache__' in p.parts or p.name.endswith('.pyc') or p.name=='.DS_Store':continue
 files.append(p)
files.sort()
manifest={'unit':'CR_PHYS23_SOURCE_CONDITIONAL_BIANCHI_I_LYA_GEODESIC_SCREEN',
 'immutable_parent_PR147_HEAD':'fac9a25d53468502b3807da2034e4bfa99325c8f',
 'original_source_Git_blob_SHA1':'d7034188ca5a02dc37db24aaf8f7d550624567bd',
 'source_PHYS22_ZIP_SHA256':'c40decf905f146ebe5e3fe40ba39f59fbf29567819cfc6be4c629e3aaf8f5aa6',
 'source_authentic_angular_model':'PHYS22_source_weighted_chi_exact',
 'geometry_provenance':'EXPLICIT_CONDITIONAL_TRACEFREE_SHEAR_NOT_REAL_BIANCHI_IVP',
 'central_DAG':'28/88_DELTA0','extension_DAG':'0/3_DELTA0',
 'production':'HOLD','native25':'HOLD','L4':'HOLD',
 'original_copyright_PDFs_included':False,
 'members':[{'name':str(p.relative_to(ROOT)),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
with ZipFile(ARCH,'w',compression=ZIP_DEFLATED,compresslevel=9,allowZip64=True) as z:
 for p in files:z.write(p,p.relative_to(ROOT))
 z.writestr('MANIFEST_SHA256.json',json.dumps(manifest,indent=2,sort_keys=True)+'\n')
with ZipFile(ARCH)as z:
 assert z.testzip() is None
 saved=json.loads(z.read('MANIFEST_SHA256.json'))
 assert len(saved['members'])==len(files)
 for f in saved['members']:
  b=z.read(f['name']);assert hashlib.sha256(b).hexdigest()==f['sha256'] and len(b)==f['size_bytes'],f['name']
print(json.dumps({'path':str(ARCH),'bytes':ARCH.stat().st_size,'sha256':hashlib.sha256(ARCH.read_bytes()).hexdigest(),'members':len(files)+1,'source_rows':92160,'spectral_rows':46800,'stage_records':20,'crc_pass':True},indent=2))