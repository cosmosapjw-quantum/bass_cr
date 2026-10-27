#!/usr/bin/env python3
"""One create-only C4 metadata/resource admission, charged to this unit."""
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import pathlib
import platform
import resource
import sys

UNIT=pathlib.Path(__file__).resolve().parents[1]
UNIT_ID='CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1'
def write_new(path,value):
    with path.open('x') as f: json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
budget=json.loads((UNIT/'implementation/RESOURCE_PROPOSAL.json').read_text())
assert budget['unit']==UNIT_ID and budget['local_science_cpu_cap_s']==40
assert not budget['historical_allowance_transferred'] and not budget['parallel_PR108_budget_transferred']
for path in ['evidence/C04_HOST_ADMISSION.json','evidence/C04_CODE_MANIFEST.json','EXECUTION_BUDGET.json']:
    assert not (UNIT/path).exists(), 'CREATE_ONLY_C4_ADMISSION_REQUIRED:'+path
spec=importlib.util.spec_from_file_location('new_unit_resource_runner',UNIT/'implementation/run_bounded.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
memory=runner.memory_capacity(budget,max(x['selected_memory_limit_bytes'] for x in budget['run_allocations']))
manifest={'unit':UNIT_ID,'files':[]}
for folder in ['implementation','review']:
    for p in sorted((UNIT/folder).rglob('*.py')):
        if '__pycache__' not in p.parts: manifest['files'].append({'path':str(p.relative_to(UNIT)),'bytes':p.stat().st_size,'sha256':sha(p)})
write_new(UNIT/'evidence/C04_CODE_MANIFEST.json',manifest)
source_pins=json.loads((UNIT/'inputs/INPUT_MANIFEST.json').read_text())
repo=UNIT.parents[1]
for row in source_pins['files']:
    p=repo/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
versions={x:importlib.metadata.version(x) for x in ['numpy','scipy','matplotlib']}
usage=resource.getrusage(resource.RUSAGE_SELF);cpu=usage.ru_utime+usage.ru_stime
tail=.05;charged=cpu+tail
host={'schema':'CR_LOW_BIRTH_C4_HOST_ADMISSION_V1','unit':UNIT_ID,'memory_gate':'PASS' if memory['admission_pass'] else 'FAIL','memory':memory,'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'allowed_CPU_affinity':sorted(os.sched_getaffinity(0)),'worker_native_threads':1,'package_versions':versions,'code_manifest_sha256':sha(UNIT/'evidence/C04_CODE_MANIFEST.json'),'admission_script_sha256':sha(pathlib.Path(__file__)),'source_pins_checked':source_pins,'preparation_process_CPU_through_receipt_s':cpu,'preparation_receipt_tail_reserve_s':tail,'charged_preparation_CPU_s':charged,'preparation_cpu_includes_interpreter_startup':True,'new_scientific_workers_before_admission':0,'old_science_replays':0,'provider_CPU_s':None,'global_remaining':None,'aggregate_preventive_CPU_hard_proof':False}
write_new(UNIT/'evidence/C04_HOST_ADMISSION.json',host)
budget.update(status='FROZEN_C4_ADMITTED' if memory['admission_pass'] else 'BLOCKED_C4_HOST_MEMORY',spent_before_C4_admission=charged,host_admission_sha256=sha(UNIT/'evidence/C04_HOST_ADMISSION.json'),code_manifest_sha256=sha(UNIT/'evidence/C04_CODE_MANIFEST.json'))
budget['unallocated_failure_and_repair_reserve_s']=40-charged-budget['nominal_worker_sum_s']-budget['nominal_coordinator_reservations_s']
assert budget['unallocated_failure_and_repair_reserve_s']>0
write_new(UNIT/'EXECUTION_BUDGET.json',budget)
usage2=resource.getrusage(resource.RUSAGE_SELF);actual_after=usage2.ru_utime+usage2.ru_stime
assert actual_after<=charged, 'C4_RECEIPT_TAIL_RESERVE_EXCEEDED'
print(json.dumps({'status':budget['status'],'charged_preparation_CPU_s':charged,'measured_CPU_after_writes_s':actual_after,'cap_s':40,'code_files':len(manifest['files']),'memory_available_estimate':memory['host_capped_available_estimate_bytes'],'memory_required':memory['required_worker_plus_reserve_bytes'],'versions':versions,'budget_sha256':sha(UNIT/'EXECUTION_BUDGET.json')}))
if not memory['admission_pass']:sys.exit(2)
