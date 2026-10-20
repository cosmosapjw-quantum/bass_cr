"""Independent fake-clock reproduction; no Rust/native/ODE is executed."""
from pathlib import Path
from types import ModuleType
from unittest import mock
from datetime import datetime, timezone
from dataclasses import asdict
import hashlib
import json
import sys

ROOT = Path('/workspace/scratch/da42c813ee8c')
SOURCE = ROOT/'bass_cr/research/cr_c21e_event_native_20261018'
I = ROOT/'bass_cr/research/cr_c21i_callback_optimization_20261020'
OUT = ROOT/'c21i_theory/raw/deadline_review'
OUT.mkdir(exist_ok=False)
raw = (I/'optimized_adapter.py').read_bytes()
with (OUT/'optimized_adapter_before_review_fix.py').open('xb') as stream:
    stream.write(raw)
opt = ModuleType('_reviewed_deadline_candidate')
opt.__file__ = str(I/'optimized_adapter.py')
exec(compile(raw, opt.__file__, 'exec'), opt.__dict__)
base = opt.load_frozen_adapter()
reference = base.private_reference(SOURCE)
from run_experiment import make_fixture, initial, breakpoints
from event_coupler import ManufacturedMicro
sys.path.insert(0,str(opt.DEFAULT_C21G))
from campaign_contract import fixture_scales
import numpy as np

f = opt._freeze_fixture(make_fixture(a0=.09,dx=1e-7,opacity_scale=.0003,Y=0.))
m = len(f.q)
dynamic = np.array([j for j in range(m+19) if j not in (m+1,m+2)])
scales_full = fixture_scales(asdict(f))
scales = np.array(scales_full['values'])[dynamic]
full = np.zeros(m+19)
full[m:m+4] = initial(f)[0]
u = full[dynamic]
lo,hi = breakpoints(f)[:2]
t = (lo+hi)/2
clock = {'now':0.}

def guard():
    if clock['now']>=1.:
        raise RuntimeError('REVIEW_PROBE_EXPIRED')

def slow_value(t,u):
    clock['now']=2.
    return np.zeros_like(u)

contract = {'schema':'C21I_DETERMINISTIC_PROVIDER_ADMISSION_V1',
    'deterministic_successful_rhs':True,'provider_kind':'FAKE_CLOCK_ZERO_VALUE',
    'provider_identity':{'purpose':'Deterministic fake-clock operational regression, no physics'},
    'admitted_by':'Independent design reviewer'}
cb = opt.make_callback_type(base,'vectorized_exact',cache_contract=contract,cache_guard=guard)(
    slow_value,f,lo,hi,scales,dynamic,reference)
try:
    value=cb.rhs(t,u/scales)
    row1={'returned':True,'error':None,'cache_entries':len(cb._cache),'clock':clock['now']}
except Exception as error:
    row1={'returned':False,'error':type(error).__name__+': '+str(error),
          'cache_entries':len(cb._cache),'clock':clock['now']}

clock['now']=0.
def final_overrun(*args,**kwargs):
    clock['now']=2.
    return {'solver_diagnostics':{'counter_note':'TOOL_STUB_NO_SOLVER'}}
with mock.patch.object(opt,'load_frozen_adapter',return_value=base), \
        mock.patch.object(base,'run_rust_reference',side_effect=final_overrun), \
        mock.patch.object(opt.time,'monotonic',side_effect=lambda:clock['now']):
    try:
        value=opt.run_optimized_reference(f,ManufacturedMicro(),SOURCE,'NO_BINARY',
            OUT/'NO_EXECUTION',scales_full,wall_s=1.,optimization='vectorized_exact')
        row2={'returned':True,'error':None,'clock':clock['now']}
    except Exception as error:
        row2={'returned':False,'error':type(error).__name__+': '+str(error),'clock':clock['now']}

clock['now']=0.
def setup_overrun(*args,**kwargs):
    clock['now']=2.
    return base
def one_request_after_setup(fixture,*args,**kwargs):
    callbacks=base.CellCallbacks(lambda t,u:np.zeros_like(u),f,lo,hi,scales,dynamic,reference)
    callbacks.rhs(t,u/scales)
    return {'solver_diagnostics':{'counter_note':'TOOL_STUB_NO_SOLVER'}}
with mock.patch.object(opt,'load_frozen_adapter',side_effect=setup_overrun), \
        mock.patch.object(base,'run_rust_reference',side_effect=one_request_after_setup), \
        mock.patch.object(opt.time,'monotonic',side_effect=lambda:clock['now']):
    try:
        value=opt.run_optimized_reference(f,ManufacturedMicro(),SOURCE,'NO_BINARY',
            OUT/'NO_EXECUTION',scales_full,wall_s=1.,optimization='vectorized_exact')
        row3={'returned':True,'error':None,'clock':clock['now']}
    except Exception as error:
        row3={'returned':False,'error':type(error).__name__+': '+str(error),'clock':clock['now']}
rows={'rhs_finishes_after_deadline':row1,'solver_final_return_after_deadline':row2,
      'source_setup_extends_remaining_deadline':row3}
result={'schema':'C21I_INDEPENDENT_DEADLINE_RED_PROBE_V1',
    'recorded_at_utc':datetime.now(timezone.utc).isoformat(),
    'candidate_source':{'path':str(I/'optimized_adapter.py'),'bytes':len(raw),
                        'sha256':hashlib.sha256(raw).hexdigest()},
    'rows':rows,'defect_reproduced':all(row['returned'] for row in rows.values()),
    'scope':'Fake-clock original-value and driver stubs; no solver/native/science execution',
    'tests_status':'EXPECTED_REJECTION_MISSING' if any(row['returned'] for row in rows.values()) else 'REJECTION_PRESENT',
    'native_calls':0,'global_error_bound':None}
with (OUT/'RED_PROBE.json').open('x') as stream:
    json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps(result,indent=2))
