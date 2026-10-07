#!/usr/bin/env python3
"""Verify and optionally execute the sealed CR-F0-R2 source-step package offline."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

SHA256 = "f3156ba8e07d4cfe263cb793c424a66958fa9730cbe9c1779c96007e10a11434"
ROOT = "BASS_CR_FASTEST_STEP_20261007"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--workspace", type=Path)
    p.add_argument("--rustc", type=Path)
    p.add_argument("--verify-only", action="store_true")
    a = p.parse_args()
    if hashlib.sha256(a.archive.read_bytes()).hexdigest() != SHA256:
        raise SystemExit("ARCHIVE_IDENTITY_MISMATCH")
    with zipfile.ZipFile(a.archive) as z:
        if z.testzip() is not None:
            raise SystemExit("ZIP_CRC_FAILED")
        for n in z.namelist():
            parts = Path(n).parts
            if not parts or parts[0] != ROOT or ".." in parts or Path(n).is_absolute():
                raise SystemExit("UNSAFE_ARCHIVE_PATH")
        manifest = json.loads(z.read(ROOT + "/MANIFEST.json"))
        for name, record in manifest["files"].items():
            data = z.read(ROOT + "/" + name)
            if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
                raise SystemExit("PAYLOAD_IDENTITY_MISMATCH: " + name)
        if a.verify_only:
            print(json.dumps({"status": "VERIFIED", "payloads": len(manifest["files"])}))
            return
        if a.workspace is None or a.rustc is None:
            p.error("execution requires --workspace NEW_DIRECTORY and --rustc")
        a.workspace.mkdir(parents=True, exist_ok=False)
        z.extractall(a.workspace)
    work = a.workspace.resolve()
    subprocess.run([sys.executable, str(work / ROOT / "research/reproduce.py"),
                    "--rustc", str(a.rustc.resolve()), "--output", str(work / "run")], check=True)

if __name__ == "__main__":
    main()
