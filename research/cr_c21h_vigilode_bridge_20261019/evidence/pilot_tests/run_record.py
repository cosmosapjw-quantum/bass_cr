"""Create-only evidence for explicitly selected no-ODE/no-process unit tests."""
import contextlib
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import sys
import time
import unittest

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
if len(sys.argv)<3:raise ValueError("label and explicit unittest selections required")
LABEL=sys.argv[1];SELECTED=sys.argv[2:]
if not LABEL.replace("_","").isalnum():raise ValueError("label")
for key in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS","RAYON_NUM_THREADS"):
    if os.environ.get(key)!="1":raise ValueError("single-thread environment required before imports: "+key)
sys.path.insert(0,str(ROOT/"tests"))
def record(path):
    path=Path(path)
    return {"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
FILES=[ROOT/"run_pilot.py",ROOT/"optical_adapter.py",ROOT/"tests/test_run_pilot.py",
       ROOT/"tests/test_optical_adapter.py",Path(__file__).resolve(),
       Path(os.environ["C21G_UNIT_DIR"])/"EXECUTION_MANIFEST.json",
       Path(os.environ["C21F_SOURCE_DIR"])/"src/reference_tau.py"]
if (ROOT/"EXECUTION_MANIFEST.json").is_file():FILES.append(ROOT/"EXECUTION_MANIFEST.json")
before={str(path):record(path) for path in FILES}
started=datetime.datetime.now(datetime.timezone.utc).isoformat();start=time.monotonic()
log=io.StringIO();details=[]
class Result(unittest.TextTestResult):
    def startTest(self,test):super().startTest(test);self.t0=time.monotonic()
    def stopTest(self,test):
        details.append({"test":test.id(),"wall_s":time.monotonic()-self.t0})
        super().stopTest(test)
with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
    suite=unittest.defaultTestLoader.loadTestsFromNames(SELECTED)
    result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Result).run(suite)
elapsed=time.monotonic()-start
log_path=HERE/(LABEL+".log")
with log_path.open("x") as stream:stream.write(log.getvalue())
after={str(path):record(path) for path in FILES}
import numpy,scipy
receipt={"schema":"C21H_PILOT_CONTRACT_TESTS_V1","label":LABEL,
    "started_utc":started,"ended_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "command":[sys.executable,str(Path(__file__).resolve()),LABEL,*SELECTED],"cwd":str(Path.cwd()),
    "environment":{key:os.environ.get(key) for key in ("C21F_SOURCE_DIR","C21G_UNIT_DIR","C21G_BASELINE_DIR",
        "OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","RAYON_NUM_THREADS","PYTHONDONTWRITEBYTECODE")},
    "python":platform.python_version(),"numpy":numpy.__version__,"scipy":scipy.__version__,
    "selected_tests":SELECTED,"tests_run":result.testsRun,"failures":len(result.failures),
    "errors":len(result.errors),"skipped":len(result.skipped),"wall_s":elapsed,
    "exit_code":0 if result.wasSuccessful() else 1,"test_times":details,
    "source_records_before":before,"source_records_after":after,"source_bytes_stable_during_test":before==after,
    "log":{"path":str(log_path),**record(log_path)},
    "metrics":{name:getattr(sys.modules.get(name),"METRICS",{}) for name in ("test_run_pilot","test_optical_adapter")},
    "native_execution":False,"ode_integration":False,"affinity_mutation":False,"old_suites_rerun":False,
    "interpretation":"Fresh explicitly selected unit methods. Synthetic build/binary/receipt files test contracts only; they are not native execution or compiler evidence. No all-red-first claim. Optical callbacks, when selected, use a pre-integrator sentinel and manufactured provider."}
with (HERE/(LABEL+".json")).open("x") as stream:json.dump(receipt,stream,indent=2);stream.write("\n")
print(log.getvalue(),end="")
print(json.dumps({key:receipt[key] for key in ("label","tests_run","failures","errors","exit_code","wall_s","source_bytes_stable_during_test","metrics")},indent=2))
sys.exit(receipt["exit_code"])
