#!/usr/bin/env python3
"""Supplement original E/F --run-dir inventory within the first intake window."""
import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from intake_readonly import safe_walk, path_record, MAX_FILES

END_UTC = datetime(2026, 10, 11, 8, 22, 34, 739000, tzinfo=timezone.utc)


def main():
    start = time.monotonic()
    p = argparse.ArgumentParser()
    p.add_argument('--root', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    root = Path(a.root).absolute()
    out = Path(a.out).absolute()
    if out != root / 'diagnostic' or out.is_symlink() or root.is_symlink():
        raise SystemExit('output must be nonsymlink root/diagnostic')
    now = datetime.now(timezone.utc)
    remaining = (END_UTC - now).total_seconds()
    if remaining <= 0:
        raise SystemExit('original window expired; no supplemental scan')
    deadline = start + min(remaining, 165.0)
    result = {'schema': 'cr-phys02g-readonly-intake-supplement.v1', 'start_utc': now.isoformat(), 'first_intake_start_utc': '2026-10-11T08:19:34.739Z', 'original_window_end_utc': END_UTC.isoformat(), 'command': sys.argv, 'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'reason': 'First intake omitted a recorded --run-dir whose basename was actual_run_<timestamp>. Original omission preserved.', 'execution_counters': {k: 0 for k in ('G_builds','resolvent','linear_solves','pulse','expm','F_retry','G_frontier','saved_comparison')}, 'scopes': []}
    exit_code = 0
    try:
        count = [0]
        for relative in ('e_return_numeric/actual_run/ACTUAL_EXIT.json', 'f_actual_original/F/run/ACTUAL_EXIT.json'):
            source = root / relative
            receipt = path_record(source, deadline)
            scope = {'original_record': receipt}
            if receipt.get('kind') == 'file':
                obj = json.loads(source.read_text())
                command = obj.get('command', [])
                if '--run-dir' in command and command.index('--run-dir') + 1 < len(command):
                    path = Path(command[command.index('--run-dir') + 1])
                    scope['recorded_run_dir'] = str(path)
                    if path.is_absolute() and path != Path('/') and not any(q.is_symlink() for q in path.parents):
                        entries, limits = safe_walk(path, deadline, count)
                        scope.update(root_presence=path_record(path, deadline), entries=entries, **limits)
                    else:
                        scope['status'] = 'REJECTED_UNSAFE_RECORDED_PATH'
                else:
                    scope['status'] = 'NO_RECORDED_RUN_DIR'
            result['scopes'].append(scope)
        result['total_regular_files'] = count[0]
        result['status'] = 'SCOPED_INVENTORY_COMPLETED' if count[0] < MAX_FILES and time.monotonic() < deadline else 'SCOPED_INVENTORY_LIMITED'
    except (OSError, ValueError, TimeoutError) as e:
        result['status'] = 'SCOPED_INVENTORY_ERROR'
        result['error'] = type(e).__name__ + ': ' + str(e)
        exit_code = 2
    result['end_utc'] = datetime.now(timezone.utc).isoformat()
    result['wall_s'] = time.monotonic() - start
    result['exit_code'] = exit_code
    (out / 'SUPPLEMENT_RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'exit_code': exit_code, 'result': str(out / 'SUPPLEMENT_RESULT.json')}))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
