"""C21H provenance and failure contracts; no solver/native process is executed.

Temporary binary/build/receipt files below are explicitly synthetic. Their
hashes test byte binding only, never establish a real compiler or native run.
The pinned C21G source and baseline are read; any tampering uses temporary
copies. The original C21F/C21G regression suites are not invoked.
"""
from __future__ import annotations

import contextlib
import copy
import importlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

sys.dont_write_bytecode=True
for key in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS","RAYON_NUM_THREADS"):
    os.environ[key]="1"
HERE=Path(__file__).resolve().parents[1]
SOURCE=Path(os.environ["C21F_SOURCE_DIR"]).resolve()
C21G=Path(os.environ["C21G_UNIT_DIR"]).resolve()
BASELINE=Path(os.environ.get("C21G_BASELINE_DIR",str(C21G/"baseline"))).resolve()
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(C21G))
import run_pilot as pilot
import campaign_contract as contract

METRICS={"native_execution":False,"ode_integration":False,
         "synthetic_binary_and_receipt_fixtures":True}


def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,sort_keys=True)+"\n")


def arguments(**updates):
    values=dict(source_dir=SOURCE,c21g_unit=C21G,baseline_dir=BASELINE)
    values.update(updates)
    return SimpleNamespace(**values)


def mock_base(root,command="native"):
    """Create a complete *synthetic* receipt to test followup binding."""
    root=Path(root);root.mkdir()
    expected={"command":command,"fixture_name":"synthetic_fixture",
        "fixture_sha256":"a"*64,"method":pilot.METHODS[0],
        "input_identity":{"manifest_sha256":"b"*64},
        "binary_identity":{"path":"/synthetic/bridge","bytes":8,"sha256":"c"*64},
        "native_identity":{"path":"/synthetic/native","bytes":9,"sha256":"d"*64} if command=="native" else None,
        "own":{"manifest":{"bytes":7,"sha256":"e"*64},"runtime_files":{"code.py":{"bytes":6,"sha256":"f"*64}}}}
    save(root/"result.json",{"mock_only":True,"value":1})
    save(root/"nested/JOB_RECEIPT.json",{"mock_only":True,"phase":"segment"})
    if command=="native":save(root/"NATIVE_IDENTITY.json",expected["native_identity"])
    receipt={"execution":"COMPLETE","variant":"base",
        **{key:expected[key] for key in ("command","fixture_name","fixture_sha256","method","input_identity","native_identity")},
        "bridge_identity":expected["binary_identity"],"source_identity":expected["own"],
        "payload_files":pilot.payload_inventory(root)}
    save(root/"JOB_RECEIPT.json",receipt)
    return expected,receipt


def check_base(root,expected):
    return pilot.verified_base(root,**expected)


class FakeNative:
    kind="EXPLICIT_UNIT_TEST_PROVIDER"
    def __init__(self):
        self.calls=0;self.timeout=None;self.process=object()
        self.closed=False;self.observed=[]
    def __call__(self,*args):
        self.calls+=1;self.observed.append((args,self.timeout))
        return ("synthetic",args)
    def close(self):self.closed=True


class PilotHelperTests(unittest.TestCase):
    def test_own_source_manifest_pins_bytes_commit_and_safe_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/"runtime.py").write_bytes(b"# unit fixture\n")
            manifest={"runtime_files":{"runtime.py":pilot.file_record(root/"runtime.py")},
                      "vigilode_commit":pilot.VIGILODE_COMMIT}
            save(root/"EXECUTION_MANIFEST.json",manifest)
            with mock.patch.object(pilot,"HERE",root):
                own=pilot.verify_own_source()
                self.assertEqual(own["runtime_files"],manifest["runtime_files"])
                (root/"runtime.py").write_bytes(b"# changed byte fixture\n")
                with self.assertRaisesRegex(pilot.AdapterError,"C21H_EXECUTION_MANIFEST_MISMATCH"):
                    pilot.verify_own_source()
                for invalid in ("../outside.py","/outside.py"):
                    with self.subTest(path=invalid):
                        save(root/"EXECUTION_MANIFEST.json",{
                            "runtime_files":{invalid:{"bytes":1,"sha256":"0"*64}},
                            "vigilode_commit":pilot.VIGILODE_COMMIT})
                        with self.assertRaisesRegex(pilot.AdapterError,"C21H_EXECUTION_MANIFEST_MISMATCH"):
                            pilot.verify_own_source()
                save(root/"EXECUTION_MANIFEST.json",{"runtime_files":{},"vigilode_commit":"wrong"})
                with self.assertRaisesRegex(pilot.AdapterError,"C21H_VIGILODE_PIN_MISMATCH"):
                    pilot.verify_own_source()

    def test_payload_inventory_includes_nested_receipt_and_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            save(root/"JOB_RECEIPT.json",{"terminal":"excluded"})
            save(root/"nested/JOB_RECEIPT.json",{"segment":1})
            save(root/"result.json",{"mock":True})
            records=pilot.payload_inventory(root)
            self.assertEqual(set(records),{"nested/JOB_RECEIPT.json","result.json"})
            save(root/"nested/JOB_RECEIPT.json",{"segment":2})
            self.assertNotEqual(pilot.payload_inventory(root),records)
            (root/"alias.json").symlink_to(root/"result.json")
            with self.assertRaisesRegex(pilot.AdapterError,"PAYLOAD_SYMLINK"):
                pilot.payload_inventory(root)

    def test_fd_base_requires_complete_base_and_exact_job_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"base";expected,receipt=mock_base(root)
            actual=check_base(root,expected)
            self.assertEqual(actual,{"path":str(root.resolve()),"receipt":pilot.file_record(root/"JOB_RECEIPT.json")})
            for key,value in (("execution","RUNNING"),("execution","FAILED"),("variant","fd_half")):
                with self.subTest(key=key,value=value):
                    changed=copy.deepcopy(receipt);changed[key]=value;save(root/"JOB_RECEIPT.json",changed)
                    with self.assertRaisesRegex(pilot.AdapterError,"FD_FOLLOWUP_BASE_NOT_COMPLETE"):
                        check_base(root,expected)
            save(root/"JOB_RECEIPT.json",receipt)
            for key,value in (("command","smoke"),("fixture_name","other_fixture"),
                              ("fixture_sha256","9"*64),("method",pilot.METHODS[1])):
                with self.subTest(key=key):
                    changed=copy.deepcopy(expected);changed[key]=value
                    with self.assertRaisesRegex(pilot.AdapterError,"FD_FOLLOWUP_BASE_IDENTITY"):
                        check_base(root,changed)
            smoke=Path(temp)/"smoke";smoke_expected,_=mock_base(smoke,"smoke")
            self.assertEqual(check_base(smoke,smoke_expected)["path"],str(smoke.resolve()))
            smoke_expected["command"]="native"
            with self.assertRaisesRegex(pilot.AdapterError,"FD_FOLLOWUP_BASE_IDENTITY"):
                check_base(smoke,smoke_expected)

    def test_fd_base_binds_source_input_bridge_and_native_identities(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"base";expected,_=mock_base(root)
            for key in ("input_identity","binary_identity","native_identity","own"):
                with self.subTest(identity=key):
                    changed=copy.deepcopy(expected);changed[key]["changed_identity"]=True
                    with self.assertRaisesRegex(pilot.AdapterError,"FD_FOLLOWUP_CONTEXT_MISMATCH"):
                        check_base(root,changed)

    def test_fd_base_binds_actual_payload_and_native_identity_files(self):
        with tempfile.TemporaryDirectory() as temp:
            for kind in ("native_json","result_byte","nested_receipt_byte","unexpected_file"):
                with self.subTest(tamper=kind):
                    root=Path(temp)/kind;expected,_=mock_base(root)
                    if kind=="native_json":
                        save(root/"NATIVE_IDENTITY.json",{"tampered":True})
                        reason="FD_FOLLOWUP_NATIVE_IDENTITY"
                    else:
                        target={"result_byte":"result.json","nested_receipt_byte":"nested/JOB_RECEIPT.json",
                                "unexpected_file":"extra.txt"}[kind]
                        (root/target).write_bytes(b"altered test bytes\n")
                        reason="FD_FOLLOWUP_PAYLOAD_CHANGED"
                    with self.assertRaisesRegex(pilot.AdapterError,reason):check_base(root,expected)

    def test_context_checks_pinned_source_fixture_and_raw_baseline_bytes(self):
        with mock.patch.object(sys,"path",list(sys.path)):
            source,c21g,baseline,got_contract,identity=pilot.context(arguments())
        self.assertEqual((source,c21g,baseline),(SOURCE,C21G,BASELINE))
        self.assertIs(got_contract,contract)
        self.assertEqual(identity["manifest_sha256"],pilot.C21G_MANIFEST_SHA256)
        manifest=pilot.read_json(C21G/"EXECUTION_MANIFEST.json")
        originals={str(SOURCE/rel):pilot.file_record(SOURCE/rel) for rel in manifest["c21f_runtime_files"]}
        originals.update({str(BASELINE/rel):pilot.file_record(BASELINE/rel) for rel in manifest["baseline_files"]})
        with tempfile.TemporaryDirectory() as temp:
            source_copy=Path(temp)/"source";baseline_copy=Path(temp)/"baseline"
            for original,destination,records in ((SOURCE,source_copy,manifest["c21f_runtime_files"]),
                                                  (BASELINE,baseline_copy,manifest["baseline_files"])):
                for rel in records:
                    target=destination/rel;target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(original/rel,target)
            for location,rel in ((source_copy,"src/reference_tau.py"),
                                 (baseline_copy,"common_ic/fixture.json"),
                                 (baseline_copy,"native_source/radau.json")):
                with self.subTest(tamper=rel):
                    target=location/rel;data=target.read_bytes();target.write_bytes(data+b" ")
                    with mock.patch.object(sys,"path",list(sys.path)):
                        with self.assertRaisesRegex(ValueError,"PINNED_FILE_MISMATCH"):
                            pilot.context(arguments(source_dir=source_copy,baseline_dir=baseline_copy))
                    target.write_bytes(data)
        self.assertEqual({path:pilot.file_record(path) for path in originals},originals)
        METRICS["pinned_input_files_read"]=len(originals)
        METRICS["original_input_bytes_unchanged"]=True

    def test_context_rejects_unpinned_manifest_and_import_alias(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);save(root/"EXECUTION_MANIFEST.json",{"synthetic_wrong_manifest":True})
            with self.assertRaisesRegex(pilot.AdapterError,"PINNED_C21G_MANIFEST_MISMATCH"):
                pilot.context(arguments(c21g_unit=root))
        for name in ("campaign_contract","diagnostics","run_campaign"):
            with self.subTest(module=name):
                with mock.patch.dict(sys.modules,{name:SimpleNamespace(__file__="/wrong/"+name+".py")}):
                    with self.assertRaisesRegex(pilot.AdapterError,"C21G_IMPORT_LOCATION"):
                        pilot.context(arguments())

    def test_native_build_record_binds_temporary_binary_wrapper_and_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            build=Path(temp);binary=build/"native_point"
            binary.write_bytes(b"SYNTHETIC; NEVER EXECUTE THIS FILE\n")
            (build/"owner_source.tar").write_bytes(b"SYNTHETIC ARCHIVE HASH FIXTURE; NOT A TAR\n")
            (build/"owner_commit.txt").write_text(contract.OWNER+"\n")
            (build/"build_exit.txt").write_text("exit_code=0\n")
            rows={"native_point":contract.sha256(binary),
                  "native_point.rs":contract.sha256(SOURCE/"native/native_point.rs"),
                  "owner_source.tar":contract.sha256(build/"owner_source.tar")}
            def write_rows(values):
                (build/"input_sha256.txt").write_text("".join(f"{digest}  {name}\n" for name,digest in values.items()))
            write_rows(rows)
            record=contract.verify_native_binary(binary,SOURCE,build)
            self.assertEqual(record["sha256"],rows["native_point"])
            self.assertEqual(record["owner_source_archive"]["sha256"],rows["owner_source.tar"])
            for name,reason in (("native_point","BUILD_INPUT_OR_BINARY_HASH_MISMATCH"),
                                ("native_point.rs","BUILD_INPUT_OR_BINARY_HASH_MISMATCH"),
                                ("owner_source.tar","BUILD_OWNER_ARCHIVE_HASH_MISMATCH")):
                with self.subTest(bound_file=name):
                    changed=dict(rows);changed[name]="0"*64;write_rows(changed)
                    with self.assertRaisesRegex(ValueError,reason):contract.verify_native_binary(binary,SOURCE,build)
            write_rows(rows);binary.write_bytes(b"ALTERED SYNTHETIC BINARY\n")
            with self.assertRaisesRegex(ValueError,"BUILD_INPUT_OR_BINARY_HASH_MISMATCH"):
                contract.verify_native_binary(binary,SOURCE,build)
            with self.assertRaisesRegex(ValueError,"NEW_BINARY_REQUIRES_RECORDED_BUILD_DIRECTORY"):
                contract.verify_native_binary(binary,SOURCE)

    def test_native_budget_caps_timeout_and_delegates_observed_state(self):
        native=FakeNative();provider=pilot.BudgetedNativeMicro(native,100.)
        for times,expected in (((1.,2.),15.),((97.,99.),3.)):
            with self.subTest(remaining_timeout=expected):
                with mock.patch.object(pilot.time,"monotonic",side_effect=times):
                    self.assertEqual(provider("input"),("synthetic",("input",)))
                self.assertEqual(native.observed[-1][1],expected)
        self.assertEqual(provider.kind,native.kind)
        self.assertEqual(provider.calls,2)
        self.assertIs(provider.process,native.process)
        provider.close();self.assertTrue(native.closed)

    def test_native_budget_rejects_before_and_after_call_without_fallback(self):
        native=FakeNative();provider=pilot.BudgetedNativeMicro(native,100.)
        with mock.patch.object(pilot.time,"monotonic",return_value=100.):
            with self.assertRaisesRegex(pilot.AdapterError,"NATIVE_JOB_WALL_BUDGET"):
                provider("expired")
        self.assertEqual(native.calls,0)
        with mock.patch.object(pilot.time,"monotonic",side_effect=(99.,100.01)):
            with self.assertRaisesRegex(pilot.AdapterError,"NATIVE_JOB_WALL_BUDGET"):
                provider("late")
        self.assertEqual(native.calls,1)
        self.assertEqual(native.observed,[(('late',),1.)])
        class OriginalFailure(RuntimeError):pass
        class Broken(FakeNative):
            def __call__(self,*args):
                self.calls+=1;raise OriginalFailure("do not replace")
        broken=Broken();wrapper=pilot.BudgetedNativeMicro(broken,100.)
        with mock.patch.object(pilot.time,"monotonic",return_value=1.):
            with self.assertRaisesRegex(OriginalFailure,"do not replace"):wrapper("input")
        self.assertEqual(broken.calls,1)


class PilotMainTests(unittest.TestCase):
    """Run only after the real C21H runtime manifest has been frozen."""
    def argv(self,command,out,*extra):
        return [command,"--source-dir",str(SOURCE),"--c21g-unit",str(C21G),
                "--baseline-dir",str(BASELINE),"--out",str(out),*map(str,extra)]

    @contextlib.contextmanager
    def forbid_execution(self):
        with mock.patch.object(pilot,"run_rust_reference",side_effect=AssertionError("ODE execution forbidden in contract test")) as ode:
            with mock.patch("subprocess.Popen",side_effect=AssertionError("Child process forbidden in contract test")) as process:
                with mock.patch.object(os,"sched_setaffinity",side_effect=AssertionError("Affinity mutation forbidden in contract test")) as affinity:
                    with contextlib.redirect_stdout(io.StringIO()):yield
                affinity.assert_not_called()
            process.assert_not_called()
        ode.assert_not_called()

    def test_plan_verifies_real_pins_and_preserves_existing_output(self):
        # Reuse the already completed real plan; do not create a second plan
        # merely to reproduce its verification. The only main call must stop
        # at the create-only existing-directory check before writing anything.
        out=HERE/"evidence/wiring/plan_02"
        self.assertEqual(pilot.read_json(out/"PLAN_RECEIPT.json")["status"],"READY_EXECUTABLE_INPUTS_VERIFIED")
        self.assertFalse(pilot.read_json(out/"PLAN_RECEIPT.json")["native_executed"])
        recorded_inputs=pilot.read_json(out/"INPUT_IDENTITY.json")
        actual_inputs=contract.verify_inputs(SOURCE,BASELINE)
        # The original host's absolute path is provenance metadata. Every
        # pinned hash and payload record must still match on another host.
        self.assertTrue(Path(recorded_inputs["manifest_path"]).is_absolute())
        self.assertEqual({key:value for key,value in recorded_inputs.items() if key!="manifest_path"},
                         {key:value for key,value in actual_inputs.items() if key!="manifest_path"})
        self.assertEqual(pilot.read_json(out/"C21H_SOURCE_IDENTITY.json"),pilot.verify_own_source())
        before=pilot.payload_inventory(out)
        with self.forbid_execution():
            with self.assertRaises(FileExistsError):pilot.main(self.argv("plan",out))
        self.assertEqual(pilot.payload_inventory(out),before)
        self.assertFalse((out/"JOB_RECEIPT.json").exists())
        METRICS["completed_real_plan_reused"]={"path":str(out),"payloads":before}

    def test_missing_bridge_writes_explicit_failed_nonexecution_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            for command in ("smoke","native"):
                with self.subTest(command=command):
                    out=Path(temp)/command
                    with self.forbid_execution():self.assertEqual(pilot.main(self.argv(command,out)),1)
                    receipt=pilot.read_json(out/"JOB_RECEIPT.json")
                    self.assertEqual(receipt["execution"],"FAILED")
                    self.assertEqual(receipt["error"],"BRIDGE_BINARY_REQUIRED")
                    self.assertEqual(receipt["error_class"],"AdapterError")
                    for flag in ("native_executed","native_launch_attempted","native_process_started"):
                        self.assertFalse(receipt[flag])
                    self.assertEqual(receipt["physics"],"NOT_EVALUATED")
                    self.assertEqual(receipt["numerics"],"NOT_EVALUATED")
                    self.assertEqual(receipt["payload_files"],pilot.payload_inventory(out))
                    self.assertIn("BRIDGE_BINARY_REQUIRED",(out/"failure_traceback.log").read_text())

    def test_native_admission_rejects_bad_build_thread_and_cpu_before_execution(self):
        own=pilot.verify_own_source()
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);binary=root/"bridge"
            binary.write_bytes(b"SYNTHETIC BRIDGE; NEVER EXECUTE\n")
            build={"binary_sha256":pilot.file_hash(binary),"vigilode_commit":pilot.VIGILODE_COMMIT,
                   "diffsol_version":"0.17.1","exit_code":0,
                   "source_files":{key:own["runtime_files"][key] for key in
                       ("rust_bridge/Cargo.toml","rust_bridge/Cargo.lock","rust_bridge/src/main.rs")}}
            build_path=root/"synthetic_build.json"
            cases=[("missing_build",None,False,55,"NATIVE_JOB_REQUIRES_BRIDGE_BUILD_RECEIPT"),
                   ("changed_binary",{**build,"binary_sha256":"0"*64},False,55,"BRIDGE_BUILD_PROVENANCE_MISMATCH"),
                   ("changed_source",{**build,"source_files":{}},False,55,"BRIDGE_BUILD_SOURCE_MISMATCH"),
                   ("thread_guard",build,True,55,"NATIVE_REQUIRES_FRESH_SINGLE_THREAD_PYTHON_PROCESS"),
                   ("protected_cpu",build,False,55,"CPU_NOT_ADMITTED"),
                   ("not_allocated_cpu",build,False,8,"CPU_NOT_ADMITTED")]
            for name,build_record,preimport,cpu,reason in cases:
                with self.subTest(admission=name):
                    extra=["--bridge",binary,"--native",root/"not_executed_native","--cpu",cpu]
                    if build_record is not None:
                        save(build_path,build_record);extra.extend(["--bridge-build-receipt",build_path])
                    out=root/name
                    with mock.patch.object(pilot,"NUMPY_ALREADY_IMPORTED",preimport):
                        with mock.patch.object(os,"sched_getaffinity",return_value={2,55}):
                            with self.forbid_execution():
                                self.assertEqual(pilot.main(self.argv("native",out,*extra)),1)
                    receipt=pilot.read_json(out/"JOB_RECEIPT.json")
                    self.assertEqual(receipt["execution"],"FAILED")
                    self.assertEqual(receipt["error"],reason)
                    self.assertFalse(receipt["native_launch_attempted"])
                    self.assertFalse(receipt["native_process_started"])
                    self.assertFalse(receipt["native_executed"])


if __name__=="__main__":unittest.main(verbosity=2)
