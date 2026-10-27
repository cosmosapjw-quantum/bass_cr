from pathlib import Path
import concurrent.futures,datetime,hashlib,json,subprocess,sys,urllib.request,urllib.error
R=Path('/workspace/scratch/865c84d871b7');P=R/'bass_cr';U=P/'research/cr_parent_event_native25_20261028';O=R/'parent_ops';stage=sys.argv[1]
specs={'CR':('bass_cr','research/cr-parent-event-native25-20261028'),'CENTRAL':('rei_bianchi','research/orchestration-sandbox-20261022'),'WU':('WU088_HH','research/provider-registry-20261025'),'REC':('rec_bianchi','research/program-expansion-20261025'),'HE':('BASS_HE','research/he-aperture07-20261027'),'BASS':('bass','research/bass-b3h-endpoint-channel-20261027'),'VIGILODE':('vigilode','research/derivative-free-causal-homotopy-20261027')}
def one(kv):
 k,(repo,branch)=kv;r=subprocess.run(['git','ls-remote','https://github.com/cosmosapjw-quantum/'+repo+'.git','HEAD','refs/heads/*'],capture_output=True,text=True,timeout=30,check=True);refs={x.split('\t')[1]:x.split('\t')[0] for x in r.stdout.splitlines()};head=refs['refs/heads/'+branch]
 url=f'https://raw.githubusercontent.com/cosmosapjw-quantum/{repo}/{head}/AGENTS.md'
 try:
  with urllib.request.urlopen(url,timeout=30) as f:b=f.read()
  h=hashlib.sha256(b).hexdigest();fp=U/'intake/policies'/f'{k}_{h[:12]}.md'
  if fp.exists():assert fp.read_bytes()==b
  else:fp.write_bytes(b)
  pol={'status':'READ','bytes':len(b),'sha256':h,'path':str(fp.relative_to(P))}
 except urllib.error.HTTPError as e:
  if e.code!=404:raise
  pol={'status':'HTTP404_UNAVAILABLE','sha256':None,'path':None}
 return k,{'repository':repo,'branch':branch,'head':head,'AGENTS':pol,'refs':refs}
res=dict(concurrent.futures.ThreadPoolExecutor(max_workers=7).map(one,specs.items()));old=json.loads((O/'last_preflight.json').read_text()) if (O/'last_preflight.json').exists() else {}
if not old:
 initial=json.loads((R/'next_intake_20261028/private/all_public_refs.json').read_text());oldrefs={x['repository'].split('/')[-1]:x['refs'] for x in initial['repositories']}
else:oldrefs={x['repository']:x['refs'] for x in old['owners'].values()}
for x in res.values():
 prev=oldrefs.get(x['repository'],{});x['changed_refs_since_previous']={k:v for k,v in x['refs'].items() if prev.get(k)!=v};x['deleted_refs_since_previous']=[k for k in prev if k not in x['refs']]
state=json.loads((O/'pub_state.json').read_text());local=subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip();localpolicy=(P/'AGENTS.md').read_bytes();assert hashlib.sha256(localpolicy).hexdigest()==res['CR']['AGENTS']['sha256']
pins=json.loads((U/'inputs/INPUT_MANIFEST.json').read_text())
for x in pins['files']:
 b=(P/x['path']).read_bytes();assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'],x['path']
prev_receipt=state['stages'][-1] if state['stages'] else None
if prev_receipt:
 assert prev_receipt['Dropbox']['ack'] and prev_receipt['Drive']['ack'];a=prev_receipt['archive'];b=Path(a['path']).read_bytes();assert len(b)==a['bytes'] and hashlib.sha256(b).hexdigest()==a['sha256']
entry=json.loads((U/'intake/ENTRY_BACKUP_CHECK.json').read_text())
for key in ['local_source_zip','local_closeout_zip']:
 x=entry[key];b=Path(x['path']).read_bytes();assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256']
cent=res['CENTRAL']['head'];url=f'https://raw.githubusercontent.com/cosmosapjw-quantum/rei_bianchi/{cent}/research/orchestration_expansion_20261025/DAG.json'
with urllib.request.urlopen(url,timeout=30) as f:dag=f.read();status=f.status
fp=U/'intake/central'/f'{cent[:12]}_DAG.json'
if fp.exists():assert fp.read_bytes()==dag
else:fp.write_bytes(dag)
baseline=json.loads((O/'central_count_baseline.json').read_text());guards={'own_local_remote_expected_match':local==res['CR']['head']==state['head'],'central_head_and_DAG_qualified':cent==baseline['head'] and hashlib.sha256(dag).hexdigest()==baseline['DAG_sha256']}
r={'schema':'CR_PARENT_NODE_PREFLIGHT_V1','stage':stage,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'user_timezone':'Asia/Seoul','local_HEAD':local,'owners':res,'actual_source_pins_checked':pins,'source_and_previous_backup_receipt_check':'PASS','entry_backup_check_path':str(U/'intake/ENTRY_BACKUP_CHECK.json'),'previous_stage_receipt':prev_receipt,'historical_readback_reused':True,'new_original_archive_GET':False,'personal_full_conversation_search':'UNAVAILABLE_ACTUAL_CURRENT_CALL','Drive_inventory':'PARTIAL','central_baseline':baseline,'central_completed':baseline['completed'],'central_total':baseline['total'],'central_count_effect':0,'guards':guards,'science_replays':0}
target=U/'intake/preflight'/f'{stage}.json'
if not all(guards.values()):
 target=U/'intake/preflight'/f'{stage}_REFUSED_{datetime.datetime.now(datetime.timezone.utc).strftime("%H%M%S")}.json';target.write_text(json.dumps(r,indent=2)+'\n');raise RuntimeError('PREFLIGHT_GUARD_REFUSAL: '+str(target))
with target.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
(O/'last_preflight.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'stage':stage,'local_HEAD':local,'central':str(r['central_completed'])+'/'+str(r['central_total']),'owners':{k:{'head':v['head'],'AGENTS':v['AGENTS']['status'],'changed_refs':v['changed_refs_since_previous']} for k,v in res.items()},'source_pins':len(pins['files']),'source_backup_checks':'PASS','receipt':str(target)}))
