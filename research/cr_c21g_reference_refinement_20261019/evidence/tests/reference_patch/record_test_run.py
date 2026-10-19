"""Record one create-only focused unittest run, including a deliberate RED run."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
phase = sys.argv[1]
if phase not in ('RED', 'GREEN', 'GREEN_GRID'):
    raise SystemExit('phase must be RED, GREEN or GREEN_GRID')
source = Path(os.environ.get(
    'C21F_SOURCE_DIR', str(HERE.parent / 'upstream' / 'c21f' / 'src')))
command = [sys.executable, '-m', 'unittest', 'discover', '-s', str(HERE),
           '-p', 'test_reference_patch.py', '-v']
started = datetime.now(timezone.utc).isoformat()
tic = time.monotonic()
run = subprocess.run(command, cwd=HERE.parent.parent,
                     capture_output=True, text=True, check=False)
wall = time.monotonic() - tic
record = {
    'phase': phase, 'started_utc': started,
    'finished_utc': datetime.now(timezone.utc).isoformat(),
    'command_argv': command, 'cwd': str(HERE.parent.parent),
    'source_path': str(source / 'reference_tau.py'),
    'source_sha256': hashlib.sha256((source / 'reference_tau.py').read_bytes()).hexdigest(),
    'tests_sha256': hashlib.sha256((HERE / 'test_reference_patch.py').read_bytes()).hexdigest(),
    'exit_code': run.returncode, 'wall_s': wall,
    'stdout': run.stdout, 'stderr': run.stderr,
    'scope': 'new small zero-microphysics fixtures; no native executable; no inherited suite',
}
with (HERE / (phase + '.json')).open('x') as file:
    json.dump(record, file, indent=2, allow_nan=False)
    file.write('\n')
with (HERE / (phase + '.log')).open('x') as file:
    file.write(run.stdout)
    file.write(run.stderr)
print(json.dumps({key: record[key] for key in (
    'phase', 'started_utc', 'finished_utc', 'exit_code', 'wall_s',
    'source_sha256', 'tests_sha256')}, indent=2))
print('\n'.join(run.stderr.splitlines()[-20:]))
