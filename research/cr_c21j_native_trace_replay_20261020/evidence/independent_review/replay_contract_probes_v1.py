#!/usr/bin/env python3
"""Independent contract probes; no IVP, callback cohort, or native process runs."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path('/workspace/scratch/9979d80514d6')
OUT = ROOT / 'c21hi_new_work/independent_review'
SOURCE = ROOT / 'bass_cr_pinned/research/cr_c21j_native_trace_replay_20261020/replay_callbacks.py'
PINS = SOURCE.with_name('INPUT_PINS.json')
REPO = ROOT / 'bass_cr_pinned'
RETURN = ROOT / 'c21hi_external_intake/native_archive/C21GHI_NATIVE_EXECUTION_20261020'
spec = importlib.util.spec_from_file_location('_c21j_independent_probe_v1', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

result = {'schema': 'C21J_INDEPENDENT_REPLAY_CONTRACT_PROBES_V1',
          'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'input_pins_sha256': hashlib.sha256(PINS.read_bytes()).hexdigest(),
          'new_native_calls': 0, 'new_IVP_solves': 0, 'cases': []}

def probe(name, function, expected):
    try:
        value = function()
        actual = {'returned': value}
    except Exception as e:
        actual = {'exception': type(e).__name__, 'message': str(e)}
    result['cases'].append({'name': name, 'expected': expected, 'actual': actual})

probe('empty_pin_maps', lambda: m.verify_inputs(REPO, RETURN, {'source_files': {}, 'return_files': {}}),
      'Reject incomplete authority/empty maps before declaring fixed-source identity')
bad = copy.deepcopy(json.loads(PINS.read_text()))
bad['source_content'] = '0' * 40
bad['native_return_head'] = '1' * 40
probe('contradictory_pin_metadata', lambda: len(m.verify_inputs(REPO, RETURN, bad)),
      'Reject contradiction between configured pins and fixed source/return commits')

rpc = RETURN / 'evidence/I_common_ic_vigilode_vectorized_base/segments/segment_000/rpc.jsonl'
rows = [json.loads(x) for x in rpc.read_text().splitlines()]
prefix = OUT / 'prefix_without_terminal_v1.jsonl'
prefix.write_text('\n'.join(json.dumps(x) for x in rows[:4]) + '\n')
probe('matched_prefix_without_terminal', lambda: len(m.rpc_pairs(prefix)),
      'Reject incomplete RPC stream, including matching-prefix-only truncation')
failed = copy.deepcopy(rows)
assert failed[-1]['message']['type'] == 'result'
failed[-1]['message']['success'] = False
failed[-1]['message']['ok'] = False
failed_path = OUT / 'failed_terminal_v1.jsonl'
failed_path.write_text('\n'.join(json.dumps(x) for x in failed) + '\n')
probe('failed_terminal_result', lambda: len(m.rpc_pairs(failed_path)),
      'Reject unsuccessful recorded terminal result')

probe('signed_zero_bits', lambda: {'scalar_distinct': m.bits(0.0) != m.bits(-0.0),
                                  'structure_distinct': not m.equal_structure([0.0], [-0.0])},
      'Both true; IEEE signed-zero distinction is preserved')
probe('conflicting_exact_native_replies',
      lambda: m.ReplyTable([{'request':'EVAL\t1','response':'OK\t1'},
                           {'request':'EVAL\t1','response':'OK\t2'}]).row_count,
      'Reject duplicate exact requests with different replies')
probe('missing_native_reply', lambda: m.ReplyTable([{'request':'EVAL\t1','response':'OK\t1'}]).resolve('EVAL\t2'),
      'Reject query absent from immutable table')
probe('complete_original_rpc', lambda: len(m.rpc_pairs(rpc)), '155 original replies')
dest = OUT / 'REPLAY_CONTRACT_PROBES_V1.json'
dest.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
