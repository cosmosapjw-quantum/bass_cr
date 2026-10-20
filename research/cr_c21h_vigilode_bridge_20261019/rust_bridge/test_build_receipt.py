#!/usr/bin/env python3
"""Check only the build-receipt contract using explicitly labelled tool stubs.

These three tests never compile Rust. The separate actual Rust build and
test_bridge_protocol.py evidence establishes compiler and solver execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


CARGO_STUB = '''#!/usr/bin/env python3
from pathlib import Path
import os,sys
if "--version" in sys.argv:
 print("cargo TEST_FIXTURE_ONLY")
 raise SystemExit(0)
target=Path(sys.argv[sys.argv.index("--target-dir")+1])
scenario=os.environ["C21H_RECEIPT_TEST_SCENARIO"]
if scenario=="cargo_failure":
 raise SystemExit(37)
binary=target/"release"/"bass-cr-c21h-rust-bridge"
binary.parent.mkdir()
binary.write_bytes(b"TEST_FIXTURE_NOT_A_RUST_BINARY\\n")
binary.chmod(0o755)
if scenario=="source_drift":
 with (Path(os.environ["C21H_RECEIPT_TEST_SOURCE"])/"src"/"main.rs").open("ab") as f:
  f.write(b"\\n// deliberate drift in an isolated test copy\\n")
'''


def identity(path: Path) -> dict:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir()
    actual_source = Path(__file__).resolve().parent
    rows = []
    for scenario in ["unchanged_success", "source_drift", "cargo_failure"]:
        folder = args.output_dir / scenario
        source = folder / "source"
        (source / "src").mkdir(parents=True)
        for name in ["Cargo.toml", "Cargo.lock", "src/main.rs", "build_bridge.sh"]:
            shutil.copyfile(actual_source / name, source / name)
        cargo = folder / "cargo_stub.py"
        cargo.write_text(CARGO_STUB)
        cargo.chmod(0o755)
        rustc = folder / "rustc_stub.py"
        rustc.write_text('#!/usr/bin/env python3\nprint("rustc TEST_FIXTURE_ONLY")\n')
        rustc.chmod(0o755)
        target = (folder / "build").resolve()
        env = os.environ.copy()
        env.update(C21H_RECEIPT_TEST_SCENARIO=scenario,
                   C21H_RECEIPT_TEST_SOURCE=str(source.resolve()))
        command = ["bash", str(source / "build_bridge.sh"), "--cargo", str(cargo.resolve()),
                   "--rustc", str(rustc.resolve()), "--target-dir", str(target)]
        with (folder / "wrapper.stdout").open("xb") as stdout, (folder / "wrapper.stderr").open("xb") as stderr:
            run = subprocess.run(command, env=env, stdout=stdout, stderr=stderr,
                                 timeout=15, check=False)
        try:
            receipt = json.loads((target / "BUILD_RECEIPT.json").read_text())
            expected = {"unchanged_success": 0, "source_drift": 78, "cargo_failure": 37}[scenario]
            assert run.returncode == receipt["exit_code"] == expected
            assert receipt["cargo_exit_code"] == (37 if scenario == "cargo_failure" else 0)
            before = json.loads((target / "SOURCE_BEFORE.json").read_text())
            assert receipt["source_files"] == {
                "rust_bridge/" + name: before[name]
                for name in ["Cargo.toml", "Cargo.lock", "src/main.rs"]}
            assert receipt["source_files_unchanged"] == (scenario != "source_drift")
            assert (receipt["binary_sha256"] is not None) == (scenario == "unchanged_success")
            if scenario == "source_drift":
                assert receipt["sources_before"] != receipt["sources_after"]
                assert receipt["build_failure_reason"] == "source files changed during build"
            status, error = "PASS", None
        except (AssertionError, KeyError, ValueError, OSError) as exc:
            status, error = "FAIL", f"{type(exc).__name__}: {exc}"
        row = {"case": scenario, "status": status, "error": error,
               "exit_code": run.returncode, "command": command,
               "actual_rust_compiler_executed": False,
               "logs": {name: identity(folder / name) for name in ["wrapper.stdout", "wrapper.stderr"]}}
        rows.append(row)
        print(json.dumps(row), flush=True)
    summary = {"schema": "C21H_BUILD_RECEIPT_CONTRACT_V1", "rows": rows,
               "all_pass": all(row["status"] == "PASS" for row in rows),
               "actual_rust_compiler_executed": False,
               "wrapper_source": identity(actual_source / "build_bridge.sh"),
               "test_source": identity(Path(__file__))}
    with (args.output_dir / "SUMMARY.json").open("x") as stream:
        json.dump(summary, stream, indent=2)
        stream.write("\n")
    return 0 if summary["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
