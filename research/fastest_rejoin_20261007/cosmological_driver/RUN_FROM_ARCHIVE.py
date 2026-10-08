#!/usr/bin/env python3
"""Verify and run the sealed CR-F0-R3 package; no remote download or old campaign."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import zipfile

SHA256 = "2624ce1d5a441eda411b819708c39cb67d1280775ee4a590924520bac00e5002"
BYTES = 777922
ROOT = "BASS_CR_FASTEST_COSMO_20261007"


def validate(archive: Path) -> None:
    if archive.stat().st_size != BYTES:
        raise ValueError("ARCHIVE_SIZE_MISMATCH")
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise ValueError("ARCHIVE_SHA256_MISMATCH")
    with zipfile.ZipFile(archive) as bundle:
        names = set()
        for item in bundle.infolist():
            path = PurePosixPath(item.filename)
            if (path.is_absolute() or ".." in path.parts or "\\" in item.filename
                    or not path.parts or path.parts[0] != ROOT
                    or stat.S_ISLNK(item.external_attr >> 16)
                    or item.filename in names):
                raise ValueError("UNSAFE_OR_DUPLICATE_ARCHIVE_ENTRY")
            names.add(item.filename)
        if bundle.testzip() is not None:
            raise ValueError("ARCHIVE_CRC_MISMATCH")
        manifest = json.loads(bundle.read(ROOT + "/MANIFEST.json"))
        expected = {ROOT + "/" + name for name in manifest["files"]}
        if names != expected | {ROOT + "/MANIFEST.json"}:
            raise ValueError("MANIFEST_ENTRY_SET_MISMATCH")
        for name, info in manifest["files"].items():
            data = bundle.read(ROOT + "/" + name)
            if len(data) != info["bytes"] or hashlib.sha256(data).hexdigest() != info["sha256"]:
                raise ValueError("PAYLOAD_MISMATCH: " + name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--rustc", type=Path)
    args = parser.parse_args()
    try:
        validate(args.archive)
        if args.verify_only:
            print("ARCHIVE_AND_PAYLOAD_VERIFIED; no scientific execution")
            return 0
        if args.workspace is None or args.rustc is None:
            parser.error("--workspace (new directory) and --rustc are required to execute")
        workspace = args.workspace.resolve()
        workspace.mkdir(parents=True, exist_ok=False)
        with zipfile.ZipFile(args.archive) as bundle:
            bundle.extractall(workspace)
        return subprocess.call([
            sys.executable, str(workspace / ROOT / "research/reproduce.py"),
            "--rustc", str(args.rustc.resolve()),
            "--output", str(workspace / "execution"),
        ])
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print("REPRODUCTION_REFUSED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
