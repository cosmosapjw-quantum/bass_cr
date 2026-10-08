from pathlib import Path
import json,hashlib,sqlite3,shutil,datetime

BASE=Path('/workspace/scratch/63ee2321a512')
REPO=BASE/'bass_cr'; G=REPO/'research/gap_closure_20261001'
R=G/'cancellation_followup_20261001'; OUT=BASE/'deliverables'
OUT.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
oldreg=json.loads((G/'GAP_REGISTRY.json').read_text())
oldmatrix=json.loads((G/'CLAIM_EVIDENCE_MATRIX.json').read_text())
assert not any(x['claim_id'].startswith('R4T_') for x in oldmatrix['claims'])
prefix='cancellation_followup_20261001/'
specs=[
 ('PROJECTOR_FACTORIZATION','Exact selected/complement rate factorization rho=||E||, moving-selector connection and scalar/gauge cancellation.', ['G01','G08'], ['DERIVED','SYMBOLICALLY_VERIFIED','IMPLEMENTATION_VERIFIED'], ['projector/PROJECTOR_RATE_THEOREM.md','projector/projector_rate.py','projector/VALIDATION.json']),
 ('STATE_AWARE_ANGLE','Conditional sharp state-dependent angle integral theorem and outward rational sufficient probability budget.', ['G06'], ['DERIVED','IMPLEMENTATION_VERIFIED'], ['projector/PROJECTOR_RATE_THEOREM.md','angle/ANGLE_BUDGET.md','angle/angle_budget.py','angle/VALIDATION.log']),
 ('GALILEAN_WEAK_CANCELLATION','Weak Galilean H-iD identity cancels boosts and isolated selected energies before norms; remote scalar potential cancels in leakage.', ['G04','G05'], ['DERIVED','SYMBOLICALLY_VERIFIED'], ['galilean/WEAK_GALILEAN_CANCELLATION.md','galilean/VALIDATION.json']),
 ('REFERENCE_BRIDGE_BOUND','Named H1 reference raw per-side [32,128] integrated-rate bound improves from55408/11 to25227/50; both capped probability bounds remain1.', ['G04','G05'], ['DERIVED','IMPLEMENTATION_VERIFIED'], ['galilean/GALILEAN_BRIDGE_CERTIFICATE.json','galilean/WEAK_GALILEAN_CANCELLATION.md']),
 ('REGULARITY_OBSTRUCTION','All five repaired radial modes have40 nonzero derivative-jump shells; strong L2 residual cannot substitute for weak residual. Archived tiny value jumps also invalidate global H1 transfer.', ['G04','G11'], ['DERIVED','SYMBOLICALLY_VERIFIED'], ['regularity/EXACT_REGULARITY_OBSTRUCTION.json','regularity/REGULARITY_AND_DYNAMICS_TRANSFER.md']),
 ('FINITE_METRIC_TRANSFER','Finite-model Duhamel comparison including both metric defects, time-dependent map, physical embedding and observable differences; actual input bounds remain unavailable.', ['G11'], ['DERIVED','SYMBOLICALLY_VERIFIED'], ['regularity/REGULARITY_AND_DYNAMICS_TRANSFER.md','regularity/TRANSFER_INPUT_CONTRACT.json','regularity/VALIDATION.json']),
 ('SAVED_MATRIX_PARITY','New factorization agrees with original W generalized-eigenvalue method on six saved original-model matrices: max relative rho discrepancy7.221467647696728e-16.', ['G01','G07'], ['NUMERICALLY_CHECKED','IMPLEMENTATION_VERIFIED'], ['SAVED_MATRIX_REPLAY.json','SAVED_MATRIX_REPLAY_NOTE.md','replay_saved_matrices.py'])
]
claims=[]
for ident,txt,gaps,ev,paths in specs:
 for p in paths: assert (R/p).is_file(),p
 claims.append({'claim_id':'R4T_'+ident,'text':txt,'status':ev,'gap_ids':gaps,
 'scope':'Conditional finite-model theorem / separately named weak H1 reference / explicitly scoped saved-matrix parity; see individual evidence',
 'assumptions':['G01 metric-compatible dynamics for rate/angle theorem; transfer theorem retains defects','exact named R4R reference and source pins for bridge/regularity claims'],
 'sources':[],'project_evidence':[prefix+p for p in paths],
 'does_not_imply':['physical B0 continuous bound or tail target pass','state availability at static snapshots','archived dynamics transfer','G02 independent derivative validation','reference adoption or NCP64 performance validation']})
newreg=json.loads(json.dumps(oldreg)); newmatrix=json.loads(json.dumps(oldmatrix))
newmatrix['claims']+=claims
newmatrix['r4t_followup']='Cancellation identities, state-aware bound and regularity/transfer conditions; no physical gate promotion'
affected=[]
for gap in newreg['gaps']:
 related=[c for c in claims if gap['gap_id'] in c['gap_ids']]
 if not related: continue
 before=gap['status']
 gap['claims_closed']+= [c['text'] for c in related]
 gap['artifacts']=sorted(set(gap['artifacts']+[a for c in related for a in c['project_evidence']]))
 gap['r4t_claims']=[c['claim_id'] for c in related]
 if gap['gap_id'] in ('G04','G05'):
  gap['next_minimum_action']='Certify continuous weak cross-residual and remote-potential leakage with oscillatory cancellation or another justified projector construction; current504.54 raw bridge bound fails5e-6. Do not use nonexistent strong L2 residual. Retain separate G02/G03 approval boundaries.'
 if gap['gap_id']=='G06':
  gap['next_minimum_action']='Obtain a state enclosure at the SAME interval endpoint plus a continuous rho integral; apply sharp angle/state-rate theorem. Actual tail-state tightness still needs a separately authorized qualified stateful run; no +/-12 state reuse at +/-32.'
 if gap['gap_id']=='G11':
  gap['next_minimum_action']='Instantiate finite-metric transfer contract with both metric defects, continuous matrices, initial state error and common-L2 embedding; combine with valid bridge/far-tail controls before any capture closure.'
 assert gap['status']==before
 affected.append(gap)
newreg['status']='R4T_CANCELLATION_FOLLOWUP_APPLIED_NO_GATE_PROMOTION'
newreg['r4t_followup']={'new_claims':len(claims),'gap_status_counts_unchanged':True,'raw_bridge_integral':'25227/50','capped_probability_bound':'1','target':'1/200000','target_met':False,'physical_queries':0,'physical_propagations':0}
save(G/'GAP_REGISTRY.json',newreg);save(G/'CLAIM_EVIDENCE_MATRIX.json',newmatrix)
db0=BASE/'recovery/r4r/BASS_CR_SOURCE_DATABASE_20261001_v5.sqlite'
db1=OUT/'BASS_CR_SOURCE_DATABASE_20261001_v6.sqlite'
assert not db1.exists();shutil.copyfile(db0,db1)
c=sqlite3.connect(db1); old=sqlite3.connect('file:'+str(db0)+'?mode=ro',uri=True)
for cl in claims: c.execute('INSERT INTO research_claims VALUES (?,?)',(cl['claim_id'],json.dumps(cl,ensure_ascii=False)))
for gap in affected:
 js=json.dumps(gap,ensure_ascii=False,sort_keys=True)
 c.execute('UPDATE research_gap_status SET record_json=? WHERE gap_id=?',(js,gap['gap_id']))
 c.execute('INSERT INTO research_events(gap_id,update_sha256,update_json,created_utc) VALUES(?,?,?,?)',(gap['gap_id'],hashlib.sha256(js.encode()).hexdigest(),js,datetime.datetime.now(datetime.timezone.utc).isoformat()))
c.commit(); assert c.execute('pragma integrity_check').fetchone()==('ok',)
legacy=[]
for (name,) in old.execute("select name from sqlite_master where type='table'"):
 if name.startswith('research_') or name=='sqlite_sequence':continue
 quoted='"'+name.replace('"','""')+'"'
 a=old.execute('SELECT * FROM '+quoted).fetchall();b=c.execute('SELECT * FROM '+quoted).fetchall()
 assert sorted(map(repr,a))==sorted(map(repr,b)),name
 legacy.append({'table':name,'rows':len(a),'unchanged':True})
for ident,record in old.execute('SELECT claim_id,record_json FROM research_claims'):
 assert c.execute('SELECT record_json FROM research_claims WHERE claim_id=?',(ident,)).fetchone()==(record,)
result={'input_v5_sha256':sha(db0),'output_v6_sha256':sha(db1),'integrity_check':'ok','legacy_tables_preserved':legacy,'prior_research_claims_preserved':29,'new_claims':len(claims),'research_claims':c.execute('SELECT count(*) FROM research_claims').fetchone()[0],'research_events':c.execute('SELECT count(*) FROM research_events').fetchone()[0]}
c.close();old.close();save(R/'DATABASE_UPDATE.json',result)
save(R/'CLAIM_UPDATE.json',{'claims':claims,'gaps_updated':[g['gap_id'] for g in affected],'no_gap_status_changes':True})
for src,dst in [('GAP_REGISTRY.json','BASS_CR_R4T_GAP_REGISTRY.json'),('CLAIM_EVIDENCE_MATRIX.json','BASS_CR_R4T_CLAIM_EVIDENCE_MATRIX.json'),('ERROR_BUDGET_CURRENT_B0.json','BASS_CR_R4T_ERROR_BUDGET_CURRENT_B0.json'),('GATE_DEPENDENCY_STATE.json','BASS_CR_R4T_GATE_DEPENDENCY_STATE.json')]:
 shutil.copyfile(G/src,OUT/dst)
print(json.dumps({k:v for k,v in result.items() if k!='legacy_tables_preserved'},indent=2))
