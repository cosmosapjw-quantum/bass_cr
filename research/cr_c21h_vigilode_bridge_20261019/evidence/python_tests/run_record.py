"""Run only the independent callback tests and retain a new receipt/log."""
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
LABEL=sys.argv[1] if len(sys.argv)>1 else "initial"
SELECTED=sys.argv[2:]
if not LABEL.replace("_","").isalnum():raise ValueError("label")
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
before=sha(ROOT/"optical_adapter.py")
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
start=time.monotonic()
log=io.StringIO()
details=[]
class Result(unittest.TextTestResult):
    def startTest(self,test):
        super().startTest(test);self.t0=time.monotonic()
    def stopTest(self,test):
        details.append({"test":test.id(),"wall_s":time.monotonic()-self.t0})
        super().stopTest(test)
with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
    if SELECTED:
        sys.path.insert(0,str(ROOT/"tests"))
        suite=unittest.defaultTestLoader.loadTestsFromNames(SELECTED)
    else:
        suite=unittest.defaultTestLoader.discover(str(ROOT/"tests"),pattern="test_optical_adapter.py")
    result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Result).run(suite)
wall=time.monotonic()-start
text=log.getvalue()
logpath=HERE/(LABEL+".log")
with logpath.open("x") as stream:stream.write(text)
import numpy
import scipy
receipt={"schema":"C21H_CALLBACK_INDEPENDENT_UNIT_TESTS_V1",
    "label":LABEL,"started_utc":started,"ended_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "command":[sys.executable,str(Path(__file__).resolve()),LABEL,*SELECTED],"cwd":str(Path.cwd()),
    "selected_tests":SELECTED or "ALL_12_OPTICAL_ADAPTER_METHODS",
    "environment":{k:os.environ.get(k) for k in ("C21F_SOURCE_DIR","C21G_UNIT_DIR","OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","PYTHONDONTWRITEBYTECODE")},
    "python":platform.python_version(),"numpy":numpy.__version__,"scipy":scipy.__version__,
    "adapter_sha256_before":before,"adapter_sha256_after":sha(ROOT/"optical_adapter.py"),
    "test_source_sha256":sha(ROOT/"tests/test_optical_adapter.py"),
    "pinned_reference_sha256":sha(Path(os.environ["C21F_SOURCE_DIR"])/"src/reference_tau.py"),
    "tests_run":result.testsRun,"failure_entries":len(result.failures),"error_entries":len(result.errors),
    "skipped":len(result.skipped),"exit_code":0 if result.wasSuccessful() else 1,
    "wall_s":wall,"test_times":details,"log":{"path":str(logpath),"bytes":logpath.stat().st_size,"sha256":sha(logpath)},
    "metrics":getattr(sys.modules.get("test_optical_adapter"),"METRICS",{}),
    "native_execution":False,"ode_integration":False,"old_suites_rerun":False,
    "counting_note":"12 unique source unittest methods; this receipt counts only tests actually selected. Subtests share each method count. Fresh tests on new adapter, not an all-red-first claim. Original RHS captured by explicit pre-integrator stop; manufactured microphysics. One mocked Rust return trace tests mapping only."}
with (HERE/(LABEL+".json")).open("x") as stream:json.dump(receipt,stream,indent=2);stream.write("\n")
print(text,end="")
print(json.dumps({k:receipt[k] for k in ("label","tests_run","failure_entries","error_entries","exit_code","wall_s","adapter_sha256_before","adapter_sha256_after","metrics")},indent=2))
sys.exit(receipt["exit_code"])
