#!/usr/bin/env python3
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
binary.write_bytes(b"TEST_FIXTURE_NOT_A_RUST_BINARY\n")
binary.chmod(0o755)
if scenario=="source_drift":
 with (Path(os.environ["C21H_RECEIPT_TEST_SOURCE"])/"src"/"main.rs").open("ab") as f:
  f.write(b"\n// deliberate drift in an isolated test copy\n")
