import datetime, json, pathlib, subprocess, sys, time, uuid
RESTORE_ROOT = pathlib.Path('/root/bass_cr_phys02d_ncp_20261011/CR_PHYS02D_RESTORE_20261011T002628Z_0b7ab12389ba43329cdbcf2834a1c237').resolve()
if 'REPLACE_WITH' in str(RESTORE_ROOT):
    raise SystemExit('ACTUAL_RESTORE_ROOT_REQUIRED')
unit = RESTORE_ROOT / 'research/cr_phys02d_20261011'
if not (unit / 'ncp/launch_pulse.py').is_file():
    raise SystemExit('RESTORED_UNIT_MISSING')
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
identifier = 'PULSE_' + stamp + '_' + uuid.uuid4().hex
operational = RESTORE_ROOT.parent / ('CR_PHYS02D_LOCAL_RECEIPTS_' + identifier)
operational.mkdir(exist_ok=False)
command = [sys.executable, 'ncp/launch_pulse.py']
plan = subprocess.run(command + ['--plan'], cwd=unit, capture_output=True, text=True)
(operational / 'PLAN.stdout.json').write_text(plan.stdout)
(operational / 'PLAN.stderr.log').write_text(plan.stderr)
if plan.returncode != 0:
    raise SystemExit('PLAN_COMMAND_FAILED; physical calls not started')
result = json.loads(plan.stdout)
if result.get('admission_status') != 'READY' or result.get('resource_probe', {}).get('admitted') is not True:
    raise SystemExit('SCOPED_ADMISSION_OR_RESOURCE_HOLD; physical calls not started')
run_dir = unit / 'evidence/runs' / identifier
return_dir = unit / 'evidence/returns' / identifier
if run_dir.exists() or return_dir.exists():
    raise SystemExit('CREATE_ONLY_RUN_OR_RETURN_COLLISION')
start = time.monotonic()
execution = None
try:
    execution = subprocess.run(command + ['--execute', '--run-dir', str(run_dir)], cwd=unit)
finally:
    record = {'command': command + ['--execute', '--run-dir', str(run_dir)],
              'cwd': str(unit), 'run_dir': str(run_dir),
              'actual_process_exit': execution.returncode if execution is not None else None,
              'elapsed_s': time.monotonic() - start,
              'execute_invocations': 1, 'automatic_retry': False}
    with (operational / 'LOCAL_EXECUTE_RECEIPT.json').open('x') as handle:
        json.dump(record, handle, indent=2)
    if run_dir.is_dir():
        collection = subprocess.run(command + ['--collect', '--run-dir', str(run_dir),
                                              '--out', str(return_dir)], cwd=unit,
                                    capture_output=True, text=True)
        (operational / 'COLLECT.stdout.json').write_text(collection.stdout)
        (operational / 'COLLECT.stderr.log').write_text(collection.stderr)
        with (operational / 'LOCAL_COLLECT_RECEIPT.json').open('x') as handle:
            json.dump({'actual_exit': collection.returncode, 'run_dir': str(run_dir),
                       'return_dir': str(return_dir)}, handle, indent=2)
        if collection.returncode != 0:
            print('COLLECTION_FAILED_PRESERVE_ALL_RAW_FILES: ' + str(operational))
    else:
        print('EXECUTE_CREATED_NO_RUN_DIRECTORY; preserve external receipts: ' + str(operational))
print('Local receipts: ' + str(operational))