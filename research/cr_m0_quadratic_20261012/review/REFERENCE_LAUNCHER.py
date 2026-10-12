"""Execute the independent reference once, preserving actual exit and timeout."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

base = Path(__file__).resolve().parent
script = base/'REFERENCE_CHECK.py'
receipt_path = base/'ACTUAL_EXECUTION.json'
assert not receipt_path.exists(), 'A second reference invocation is not authorized'
command = [sys.executable, str(script)]
started = datetime.now(timezone.utc).isoformat()
begin = time.monotonic()
timed_out = False
try:
    result = subprocess.run(command, cwd=base, capture_output=True, timeout=60)
    stdout, stderr, code = result.stdout, result.stderr, result.returncode
except subprocess.TimeoutExpired as error:
    stdout, stderr, code = error.stdout or b'', error.stderr or b'', None
    timed_out = True
elapsed = time.monotonic()-begin
(base/'REFERENCE.stdout.txt').write_bytes(stdout)
(base/'REFERENCE.stderr.txt').write_bytes(stderr)
receipt = {'schema': 'cr-m0-independent-reference-execution.v1', 'command': command,
           'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
           'external_wall_s': elapsed, 'actual_exit_code': code, 'timeout': timed_out,
           'wall_limit_s': 60, 'actual_reference_invocations': 1,
           'script_sha256': hashlib.sha256(script.read_bytes()).hexdigest(),
           'launcher_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'stdout_sha256': hashlib.sha256(stdout).hexdigest(),
           'stderr_sha256': hashlib.sha256(stderr).hexdigest(),
           'producer_imports': 0, 'producer_reruns': 0, 'old_suites': 0,
           'new_CR_generator': 0, 'CR_linear_solve': 0, 'pulse_propagation': 0,
           'expm': 0, 'resolvent': 0, 'F_retry': 0, 'NCP_dispatch': 0}
with receipt_path.open('x') as handle:
    json.dump(receipt, handle, indent=2)
    handle.write('\n')
print(json.dumps(receipt, indent=2))
if stdout:
    print(stdout.decode(errors='replace'))
if stderr:
    print(stderr.decode(errors='replace'), file=sys.stderr)
raise SystemExit(code if code is not None else 124)
