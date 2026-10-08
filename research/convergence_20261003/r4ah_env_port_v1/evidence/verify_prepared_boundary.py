"""Read-only negative test of a prepared contract; never authorizes or runs.

Only the authorization read is replaced by a memory-only test dictionary.
No authorization file is created, no output directory is created, and changed
resource bindings must be rejected by the actual point-contract validator.
"""
import copy
import json
from pathlib import Path
import sys
from unittest.mock import patch

session=Path(sys.argv[1]).resolve()
batch_path=session/'batch/BATCH.json'
b=json.loads(batch_path.read_text())
sys.path.insert(0,str(Path(b['root'])/'source'))
import runtime_contract as runtime
from common import ContractError,sha

item=next(row for row in b['nodes'] if row['node_id']=='m64')
original_read=runtime.read
ap=batch_path.parent/'AUTHORIZATION.json'
assert not ap.exists()
auth_fixture={'schema':'R4AG_BATCH_AUTHORIZATION_V1','batch_sha256':sha(batch_path),
              'batch_id':b['batch_id'],'output':b['output'],'attempt_cap_per_node':1,
              'authorized_nodes':['m64']}
def fixture_read(path):
    return copy.deepcopy(auth_fixture) if Path(path).resolve()==ap else original_read(path)
observed=runtime.observe_environment()
rejections=[]
for part in ('membership','namespaces','mount'):
    changed=copy.deepcopy(observed)
    binding=changed['resource_hierarchy']['binding']
    if part=='membership':binding[part]='/test-only-other-group'
    elif part=='namespaces':binding[part]['cgroup']='cgroup:[99999999]'
    else:binding[part]['mountpoint']='/test-only-other-mount'
    with patch.object(runtime,'read',side_effect=fixture_read), patch.object(runtime,'observe_environment',return_value=changed):
        try:runtime.validate_point_contract(item['contract'],ap)
        except ContractError as error:
            assert 'changed since preparation' in str(error),str(error)
            rejections.append({'changed':part,'error':str(error)})
        else:raise AssertionError('changed resource binding was accepted')
assert not ap.exists() and not Path(item['output']).exists()
print(json.dumps({'status':'PUBLIC_PRE_RUN_VALIDATOR_REJECTS_CHANGED_RESOURCE_BINDINGS',
                  'rejections':rejections,'authorization_fixture':'MEMORY_ONLY_TEST_BOUNDARY',
                  'authorization_files_created':0,'native_executions':0,'science_calls':0},indent=2))
