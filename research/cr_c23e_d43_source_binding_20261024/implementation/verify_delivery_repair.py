"""Delivery-only checks. Never invokes numerical validation main."""
import sys,os,json,hashlib,importlib.util,tempfile,difflib
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
run=ROOT/'runs/C23E_D43_SOURCE_BINDING_20261024T021612Z_v1';dest=run/'delivery_repair';dest.mkdir(exist_ok=False)
checks=[]
def add(name,ok):
 checks.append({'name':name,'passed':bool(ok)})
 assert ok,name
before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in run.rglob('*')if p.is_file() and 'delivery_repair' not in p.parts}
mods={}
with patch('subprocess.run',side_effect=AssertionError('import spawned process')),patch('pathlib.Path.mkdir',side_effect=AssertionError('import mkdir')),patch('pathlib.Path.write_text',side_effect=AssertionError('import write')),patch('pathlib.Path.open',side_effect=AssertionError('import open')):
 for name in ['d_binding','validate_d_binding','dispatch_d_binding']:
  spec=importlib.util.spec_from_file_location(name,ROOT/'implementation'/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);mods[name]=m
add('three_module_import_no_write_no_spawn',True)
for name,size,sha in [('C23B_CASES_EXACT.json',25699,'61bcbc0b44206f496534da6bdffcdfe1731ad063'),('photoelectron_atoms.csv',1681578,'b01f4c94faffd9a44ca4dcf31231bd6b7da2b766')]:
 b=(ROOT/'inputs'/name).read_bytes();add('exact_input_'+name,len(b)==size and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==sha)
# Dispatcher collision fails at mkdir before preflight, lease or numerical launch.
with tempfile.TemporaryDirectory() as tmp:
 m=mods['dispatch_d_binding'];fake=Path(tmp);(fake/'runs').mkdir();fixed='FIXED_COLLISION';(fake/'runs'/('C23E_D43_SOURCE_BINDING_'+fixed+'_v1')).mkdir()
 with patch.object(m,'ROOT',fake),patch.object(m.datetime,'datetime') as dt,patch.object(m.subprocess,'run',side_effect=AssertionError('collision spawned process')):
  dt.now.return_value.strftime.return_value=fixed
  try:m.main()
  except FileExistsError:add('create_only_collision_refused_before_spawn',True)
  else:add('create_only_collision_refused_before_spawn',False)
for p,sha in before.items():add('preserved_'+p,hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha)
manifest=[]
for name in ['d_binding.py','validate_d_binding.py','dispatch_d_binding.py']:
 old=(run/'source_snapshot'/name).read_text();p=ROOT/'implementation'/name;b=p.read_bytes();manifest.append({'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});(dest/(name+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),b.decode().splitlines(True),fromfile='executed/'+name,tofile='delivered/'+name)))
contract=ROOT/'FROZEN_CONTRACT.md';manifest.append({'path':'FROZEN_CONTRACT.md','sha256':hashlib.sha256(contract.read_bytes()).hexdigest()})
# Pin comparison to the original execution manifest.
old=json.loads((run/'EXECUTED_SOURCE_MANIFEST.json').read_text());expected=next(x['sha256']for x in old if x['path'].endswith('FROZEN_CONTRACT.md'));add('frozen_contract_unchanged',manifest[-1]['sha256']==expected)
(dest/'DELIVERED_SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2));(dest/'TARGETED_REPAIR_RECEIPT.json').write_text(json.dumps({'status':'DELIVERY_ONLY_CHECKS_PASS','checks':checks,'new_science':0,'source_quad_calls':0,'point_source_calls':0,'numerical_main_calls':0,'primary_104_checks_replayed':False,'scope':'ROOT relative existing inputs, import guard, exact packaging inputs'},indent=2))
print(json.dumps({'status':'PASS','checks':len(checks),'receipt':str(dest/'TARGETED_REPAIR_RECEIPT.json')}))
