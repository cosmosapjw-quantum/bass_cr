"""Single root-authorized affected namespace repair batch; nonphysical only."""
import contextlib,hashlib,importlib.util,json,platform,sys,time,unittest
from datetime import datetime,timezone
from pathlib import Path
H=Path(__file__).resolve().parents[2]
E=Path(__file__).resolve().parent
cases=[
 'test_dead_qualifier_orphans_malformed_event_and_unregistered_comparator',
 'test_all_new_sessions_receive_ownership_events',
 'test_watchdog_cancels_science_before_unresponsive_root_grace',
 'test_direct_execution_requires_verified_watchdog_route',
 'test_wrapper_child_environment_identifies_only_actual_watchdog_parent',
 'test_namespace_identity_and_memory_accounting_use_actionable_ids',
]
def identity(path):
 return dict(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
source_paths=[H/'ncp/qualify_parallel.py',H/'ncp/run_and_collect.py',H/'tests/test_ncp_qualification.py']
source_identities={str(path.relative_to(H)):identity(path) for path in source_paths}
started=datetime.now(timezone.utc).isoformat();clock=time.perf_counter()
with (E/'NAMESPACE_REPAIR_STDOUT.txt').open('x') as stdout,(E/'NAMESPACE_REPAIR_STDERR.txt').open('x') as stderr:
 with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
  spec=importlib.util.spec_from_file_location('test_ncp_qualification',H/'tests/test_ncp_qualification.py')
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  suite=unittest.TestSuite(module.NCPQualificationTests(case) for case in cases)
  result=unittest.TextTestRunner(stream=stderr,verbosity=2).run(suite)
wall=time.perf_counter()-clock
receipt=dict(command=['timeout','120s',sys.executable,str(Path(__file__).resolve())],cases=cases,
 utc_started=started,utc_finished=datetime.now(timezone.utc).isoformat(),wall_s=wall,
 exit_code=0 if result.wasSuccessful() else 1,tests_run=result.testsRun,
 failures=[dict(case=str(test),traceback=trace) for test,trace in result.failures],
 errors=[dict(case=str(test),traceback=trace) for test,trace in result.errors],
 fixture_lifecycle_observations=module.LIFECYCLE_EVIDENCE,
 first_cleanup_failure_instant_child_state='NOT_OBSERVED',
 source_identities=source_identities,python=platform.python_version(),
 actual_full_G_builds=0,actual_physical_columns=0,physical_pulse_calls=0,old_suite_reruns=0,
 assignment='root-authorized bounded namespace/proc-view implementation repair',
 model_assignment='requested gpt-6.1-sol; no backend attestation')
with (E/'NAMESPACE_REPAIR_TEST_RECEIPT.json').open('x') as handle:json.dump(receipt,handle,indent=2);handle.write('\n')
print(json.dumps(dict(exit_code=receipt['exit_code'],tests_run=result.testsRun,wall_s=wall,
 fixture_states=[dict(fixture=item['fixture'],before=item['before']['lifecycle'],after=item['after']['lifecycle']) for item in module.LIFECYCLE_EVIDENCE])))
sys.exit(receipt['exit_code'])
