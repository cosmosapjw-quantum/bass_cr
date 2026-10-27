import sys,json,pathlib,hashlib,zipfile,datetime,subprocess
ROOT=pathlib.Path('/workspace/scratch/865c84d871b7');REPO=ROOT/'bass_cr';UNIT=REPO/'research/cr_parent_event_native25_20261028'
def digest(p):
 b=p.read_bytes();return {'path':str(p.relative_to(REPO)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
data=json.load(sys.stdin);cmd=data['cmd'];stage=data['stage']
if cmd=='prepare':
 files=[]
 for rel in data['files']:
  p=(UNIT/rel).resolve(); assert p.is_relative_to(REPO)
  files.extend(sorted(x for x in p.rglob('*') if x.is_file() and '__pycache__' not in str(x)) if p.is_dir() else [p])
 pre=UNIT/'intake/preflight'/f'{stage}.json'; assert pre.exists();files.append(pre)
 for p in files: assert p.exists(),p
 assert json.loads(pre.read_text())['owners']['CR']['head']==data['expected_head'],'own HEAD changed'
 preflight=json.loads(pre.read_text())
 record={'schema':'CR_PARENT_EVENT_STAGE_EVIDENCE_V1','stage':stage,'objective':data['purpose'],'status':'complete','basis':data.get('basis',['derived']),'evidence':[digest(p) for p in files],'central_completed':preflight['central_completed'],'central_total':preflight['central_total'],'central_count_effect':0,'publication_status':'POSTCOMMIT_RECEIPT_OUTSIDE_THIS_PREIMAGE','old_science_replays':0}
 target=UNIT/'stages'/f'{stage}.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n');files.append(target)
 pubfile=ROOT/'parent_ops/published_paths.json'; old=json.loads(pubfile.read_text()) if pubfile.exists() else []
 union=sorted(set(old+[str(p.relative_to(REPO)) for p in files]));(ROOT/'parent_ops/candidate_paths.json').write_text(json.dumps(union))
 elements=[]
 for p in sorted(set(files)):
  rel=str(p.relative_to(REPO)); raw=p.read_bytes(); element={'path':rel,'mode':'100644','type':'blob'}
  if rel in data.get('binary_blobs',{}):
   blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
   assert blob==data['binary_blobs'][rel], 'BINARY_BLOB_IDENTITY_MISMATCH'
   element['sha']=blob
  else: element['content']=raw.decode('utf-8')
  elements.append(element)
 result={'tree_elements':elements,'paths':[str(p.relative_to(REPO)) for p in files],'base_tree':subprocess.run(['git','rev-parse','HEAD^{tree}'],cwd=REPO,capture_output=True,text=True,check=True).stdout.strip()}
 if data.get('response_file'):
  chunks=[];chunk=[];size=0
  for element in elements:
   n=len(json.dumps(element))
   if chunk and size+n>120000:chunks.append(chunk);chunk=[];size=0
   chunk.append(element);size+=n
  if chunk:chunks.append(chunk)
  result['chunks']=chunks;path=pathlib.Path(data['response_file']);path.write_text(json.dumps(result));print(json.dumps({'response_file':str(path),'chunk_count':len(chunks),'base_tree':result['base_tree']}))
 else: print(json.dumps(result))
elif cmd=='package':
 paths=json.loads((ROOT/'parent_ops/candidate_paths.json').read_text()); public_paths=list(paths)
 extras=[]
 if (UNIT/'runs').exists():
  extras.extend(p for p in (UNIT/'runs').rglob('*') if p.is_file() and not any(x in p.parts for x in ('__pycache__','mplcache')))
  for row in json.loads((UNIT/'inputs/INPUT_MANIFEST.json').read_text())['files']:
   p=REPO/row['path']; assert digest(p)['sha256']==row['sha256']; extras.append(p)
 paths=sorted(set(paths+[str(p.relative_to(REPO)) for p in extras])); files=[REPO/p for p in paths]
 manifest={'schema':'CR_PARENT_EVENT_STAGE_MANIFEST_V1','stage':stage,'commit':data['commit'],'expected_parent':data['parent'],'force':False,'git_published_paths':public_paths,'archive_only_paths':sorted(set(paths)-set(public_paths)),'files':[digest(p) for p in files]}
 outdir=ROOT/'parent_deliverables';outdir.mkdir(exist_ok=True);archive=outdir/f"BASS_CR_PARENT_EVENT_{stage}_20261028_{data['commit'][:12]}.zip"
 with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:z.write(p,str(p.relative_to(REPO)))
  z.writestr('MANIFEST.json',json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
 b=archive.read_bytes();meta={'path':str(archive),'name':archive.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'members':len(paths)+1,'payloads':len(paths)}
 (ROOT/'parent_ops/published_paths.json').write_text(json.dumps(public_paths));print(json.dumps(meta))
elif cmd=='receipt':
 p=UNIT/'publication'/f'{stage}_RECEIPT.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data['receipt'],indent=2,ensure_ascii=False)+'\n');print(str(p))
