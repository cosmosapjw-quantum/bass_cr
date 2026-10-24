"""Finite text/binary publication inventory and post-S canonical ZIP. NO science."""
import argparse,datetime,hashlib,json,pathlib,shutil,zipfile
UNIT=pathlib.Path(__file__).resolve().parents[1]
SUBTREE='research/cr_c23d_finiteT_source_bridge_20261024/'
BASE='ec0c2cb8cc9feae64fe028ca2a4ea0eb7d79c8f8'
BRANCH='research/cr-c23d-finite-t-source-bridge-20261024'
REQUIRED=['CLAIM_GATE.json','LOOP_LEDGER.json','BUDGET_CONTINUITY.json','NEXT_DAG.json','HANDOFF_KO.md','FROZEN_CONTRACT.md','REPORT_KO.md','README_KO.md']
GENERATED=UNIT/'mechanical/generated'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def selected_files():
 for name in REQUIRED:
  if not (UNIT/name).is_file():raise FileNotFoundError('root-owned final gate file not ready: '+name)
 paths={UNIT/name for name in REQUIRED}
 for name in ['implementation','inputs','runs','figures','runtime','mechanical','theory']:
  for p in (UNIT/name).rglob('*'):
   if not p.is_file() or '__pycache__' in p.parts or 'generated' in p.relative_to(UNIT).parts or p.suffix in ('.pyc','.pyo'):continue
   paths.add(p)
 for name in ['CURRENT_INTAKE.json','CURRENT_INTAKE_KO.md','REF_DELTA.json','OPEN_PR_DELTA.json','SELECTED_SOURCE_EXPECTATIONS.json','SELECTED_BLOB_VERIFICATION.json','INHERITED_BUDGET_CONTINUITY.json']:
  p=UNIT/'intake'/name
  if p.is_file():paths.add(p)
 for p in (UNIT/'intake/policy').rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:paths.add(p)
 p=UNIT/'intake/selected_text/bass_cr/research/cr_coulomb_partition_20261014/RESULT_AND_DELIVERY_KO.md'
 if p.is_file():paths.add(p)
 return sorted(paths)

def build_git():
 GENERATED.mkdir(parents=True,exist_ok=True);text=[];binary=[];inventory=[]
 for p in selected_files():
  rel=str(p.relative_to(UNIT));raw=p.read_bytes();record={'path':SUBTREE+rel,'bytes':len(raw),'sha256':sha(raw)}
  if p.suffix.lower() in ('.png','.pdf'):
   binary.append({**record,'local_path':str(p),'mode':'100644','type':'blob','encoding':'binary'});record['kind']='binary'
  else:
   content=raw.decode('utf-8')
   if ('X-Amz-'+'Signature=') in content or ('X-Goog-'+'Signature=') in content:raise ValueError('private signedURL not admitted: '+rel)
   text.append({'path':SUBTREE+rel,'mode':'100644','type':'blob','content':content});record['kind']='utf8_text'
  inventory.append(record)
 payload={'schema':'C23D_GIT_PUBLICATION_PAYLOAD_V1','repository':'cosmosapjw-quantum/bass_cr','expected_base':BASE,'new_branch':BRANCH,'subtree':SUBTREE,'tree_elements':text,'binary_elements':binary}
 write(GENERATED/'GIT_PUBLICATION_PAYLOAD.json',payload);write(GENERATED/'PUBLICATION_INVENTORY.json',{'schema':'C23D_FINITE_PUBLICATION_INVENTORY_V1','subtree':SUBTREE,'files':inventory,'text_count':len(text),'binary_count':len(binary),'total_source_bytes':sum(x['bytes'] for x in inventory),'science_executed_by_packaging':False})
 print(json.dumps({'payload_path':str(GENERATED/'GIT_PUBLICATION_PAYLOAD.json'),'payload_bytes':(GENERATED/'GIT_PUBLICATION_PAYLOAD.json').stat().st_size,'inventory_path':str(GENERATED/'PUBLICATION_INVENTORY.json'),'files':len(inventory),'text_files':len(text),'binary_files':len(binary),'total_source_bytes':sum(x['bytes'] for x in inventory)}))

def build_archive(args):
 if not args.science_commit or len(args.science_commit)!=40:raise ValueError('actual science S commit required')
 receipt=pathlib.Path(args.publication_receipt);receipt_raw=receipt.read_bytes();parsed=json.loads(receipt_raw)
 if args.science_commit not in json.dumps(parsed):raise ValueError('actual publication receipt does not bind S')
 payload=json.loads((GENERATED/'GIT_PUBLICATION_PAYLOAD.json').read_text());inventory=json.loads((GENERATED/'PUBLICATION_INVENTORY.json').read_text())['files'];files={}
 for e in payload['tree_elements']:files['repository/'+e['path']]=e['content'].encode()
 for e in payload['binary_elements']:
  raw=pathlib.Path(e['local_path']).read_bytes()
  if len(raw)!=e['bytes'] or sha(raw)!=e['sha256']:raise ValueError('frozen binary changed')
  files['repository/'+e['path']]=raw
 for e in inventory:
  raw=files['repository/'+e['path']]
  if len(raw)!=e['bytes'] or sha(raw)!=e['sha256']:raise ValueError('frozen Git payload/inventory changed')
 provider=next((p for p in [UNIT.parent/'cr_coulomb_partition_20261014/coulomb_partition.py',UNIT/'intake/selected_text/bass_cr/research/cr_coulomb_partition_20261014/coulomb_partition.py'] if p.is_file()),None);csv=next((p for p in [UNIT.parent/'cr_c23c_stopping_coverage_20261023/inputs/photoelectron_atoms.csv',UNIT.parent/'n4_resume_transport_20261024/verified_restore/main/repository/research/cr_c23c_stopping_coverage_20261023/inputs/photoelectron_atoms.csv'] if p.is_file()),None)
 if provider is None or csv is None:raise FileNotFoundError('exact reused provider/source bytes not available for archive')
 reused=[(provider,'research/cr_coulomb_partition_20261014/coulomb_partition.py',3984,'0fae93ddfd555e1d135606eab51cfe010911c7624f661d27317024cf3f54ba86'),(csv,'research/cr_c23c_stopping_coverage_20261023/inputs/photoelectron_atoms.csv',1681578,'f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3')]
 for p,path,size,digest in reused:
  raw=p.read_bytes()
  if len(raw)!=size or sha(raw)!=digest:raise ValueError('reused source identity mismatch')
  files['repository/'+path]=raw
 files['delivery/SCIENCE_PUBLICATION_RECEIPT.json']=receipt_raw
 files['restore_c23d.py']=(UNIT/'mechanical/restore_c23d.py').read_bytes()
 manifest={'schema':'C23D_CANONICAL_RECOVERY_MANIFEST_V1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'publication_roles':{'base_F':{'commit':BASE,'role':'unchanged pre-C23D base'},'science_S':{'commit':args.science_commit,'role':'new C23D additive publication'},'reused_provider':{'repository_path':reused[0][1],'role':'completed EE provider; unchanged'},'reused_source':{'repository_path':reused[1][1],'role':'saved C23B atoms; unchanged'}},'self_hash':'NOT_INCLUDED','payload':[{'path':p,'bytes':len(v),'sha256':sha(v)} for p,v in sorted(files.items())]};files['MANIFEST.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
 out=pathlib.Path(args.output_dir);out.mkdir(parents=True,exist_ok=True);archive=out/args.filename
 if archive.suffix!='.zip' or pathlib.Path(args.filename).name!=args.filename:raise ValueError('unique plain ZIP filename required')
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name,raw in sorted(files.items()):z.writestr(name,raw)
 with zipfile.ZipFile(archive) as z:
  if z.testzip() is not None or set(z.namelist())!=set(files):raise ValueError('canonical ZIP verification failed')
  for name,raw in files.items():
   if z.read(name)!=raw:raise ValueError('ZIP actual member byte mismatch')
 metadata={'schema':'C23D_CANONICAL_ARTIFACT_V1','filename':archive.name,'local_path':str(archive.resolve()),'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes()),'members':len(files),'payload_members':len(files)-1,'ZIP_CRC':'PASS','all_actual_member_bytes':'PASS','science_commit':args.science_commit,'science_executed_by_packaging':False,'backup_providers':{'Library':'NOT_ATTEMPTED','Dropbox':'NOT_ATTEMPTED','Drive':'NOT_ATTEMPTED'}};write(out/(archive.stem+'_METADATA.json'),metadata)
 buffer=pathlib.Path('/tmp/c23d_published_buffer');buffer.mkdir(exist_ok=True);shutil.copy2(archive,buffer/archive.name);shutil.copy2(out/(archive.stem+'_METADATA.json'),buffer/(archive.stem+'_METADATA.json'));print(json.dumps(metadata))

def main():
 parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True);sub.add_parser('git-payload');a=sub.add_parser('archive');a.add_argument('--science-commit',required=True);a.add_argument('--publication-receipt',required=True);a.add_argument('--filename',required=True);a.add_argument('--output-dir',required=True);args=parser.parse_args();build_git() if args.command=='git-payload' else build_archive(args)
if __name__=='__main__':main()
