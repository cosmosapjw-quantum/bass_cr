"""Targeted receiver JSON/document validation only; no scientific code imports."""
import pathlib,json,hashlib
ROOT=pathlib.Path(__file__).resolve().parent
A=ROOT/'intake/sources/orchestration/assembly';B=ROOT/'central_patch'
def j(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=j(A/'DAG.json');b=j(B/'DAG.json');target='CR_N4_C23B_CUTOFF_BINDING';changes=[]
def diff(x,y,path=''):
 if type(x)!=type(y):changes.append(path);return
 if isinstance(x,dict):
  for k in x.keys()|y.keys():
   if k not in x or k not in y:changes.append(path+'/'+k)
   else:diff(x[k],y[k],path+'/'+k)
 elif isinstance(x,list):
  if len(x)!=len(y):changes.append(path)
  else:
   for i,(u,v) in enumerate(zip(x,y)):diff(u,v,path+'/'+str(i))
 elif x!=y:changes.append(path)
diff(a,b);ix=next(i for i,n in enumerate(a['nodes']) if n['id']==target)
assert sorted(changes)==sorted([f'/nodes/{ix}/plan_status',f'/nodes/{ix}/observed_completion'])
assert len(a['nodes'])==len(b['nodes'])==40
assert all(x['contract']==y['contract'] for x,y in zip(a['nodes'],b['nodes']))
assert len(a['authorities'])==7 and a['authorities']==b['authorities']
assert len(a['integration']['edges'])==17 and a['integration']==b['integration']
assert all(x==y for i,(x,y) in enumerate(zip(a['nodes'],b['nodes'])) if i!=ix)
assert b['nodes'][ix]['contract']['status']=='OPEN' and b['nodes'][ix]['contract']['execution']=='NOT_RUN'
assert (B/'HANDOFF_bass_cr_KO.md').read_bytes().endswith((A/'HANDOFF_bass_cr_KO.md').read_bytes())
a_lines=(A/'PR_PLANS_KO.md').read_text().splitlines();b_lines=(B/'PR_PLANS_KO.md').read_text().splitlines();rows=[i for i,(x,y) in enumerate(zip(a_lines,b_lines)) if x!=y]
assert len(a_lines)==len(b_lines) and len(rows)==1
assert a_lines[rows[0]].startswith('| '+target+' |')
assert b_lines[rows[0]]==a_lines[rows[0]].replace('| PROPOSED |','| COMPLETE_SCOPED |',1)
pins=j(ROOT/'EVIDENCE_PINS.json')['objects']; workspace=ROOT.parent
assert all((workspace/p['path']).stat().st_size==p['bytes'] and sha(workspace/p['path'])==p['sha256'] for p in pins)
r={'status':'PASS_STRUCTURAL_ONLY','scientific_verdict':'NOT_ASSESSED','changed_json_paths':sorted(changes),'unchanged_contracts':40,'unchanged_other_wrappers':39,'unchanged_authorities':7,'unchanged_integration_edges':17,'original_handoff_body':'BYTE_PRESERVED_SUFFIX','changed_plan_rows':1,'evidence_objects_hashed':len(pins),'assemble_py_executed':False,'new_scientific_runs':0}
(ROOT/'STRUCTURAL_VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
