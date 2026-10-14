import pathlib,json,hashlib,zipfile,shutil
b=pathlib.Path(__file__).parent;run=b/'actual_run_20261011T0418Z';f=b/'family';f.mkdir(exist_ok=False)
a=json.loads((run/'WRAPPER_ACTUAL_EXIT.json').read_text());zpath=pathlib.Path(a['return_archive']['path']);z=zipfile.ZipFile(zpath);m=json.loads(z.read('RETURN_MANIFEST.json'));assert len(z.namelist())==len(set(z.namelist()));assert set(z.namelist())==set(m['files'])|{'RETURN_MANIFEST.json'}
for n,v in m['files'].items():
 raw=z.read(n);assert len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['sha256'],n
shutil.copy2(zpath,f/zpath.name)
for n in ['WRAPPER_COLLECTION_EXIT.json','WRAPPER_ACTUAL_EXIT.json']:shutil.copy2(run/n,f/n)
shutil.copytree(b/'logs',f/'external_logs');shutil.copy2(b/'assemble_family.py',f/'assemble_family.py')
files={p.relative_to(f).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(f.rglob('*')) if p.is_file()}
manifest={'schema':'CR-PHYS02E-return-family.v1','scientific_status':'INDEPENDENT_ASTRA_REVIEW_REQUIRED','source_science_commit':'eceec9a0c65f44c3d8b785194b9e40c8ee23b590','publication_receipt_commit':'3bb1bc143486417e58234d51e9ea76d786ecfc25','actual_wrapper_exit':a,'return_zip_verification':{'exact_entries':len(z.namelist()),'all_bytes_sha256':True},'files':files}
p=f/'RETURN_FAMILY_MANIFEST.json';p.write_text(json.dumps(manifest,indent=2)+'\n');h=hashlib.sha256(p.read_bytes()).hexdigest();print('FAMILY_SHA256',h)
with zipfile.ZipFile(b/('CR_PHYS02E_RETURN_FAMILY_'+h[:16]+'.zip'),'x',zipfile.ZIP_DEFLATED) as zz:
 for p in sorted(f.rglob('*')):
  if p.is_file():zz.write(p,p.relative_to(f))
