#!/usr/bin/env python3
"""Verify exact archive bytes, then optionally restore files without executing them.

Use the size and SHA256 from the separately delivered final authority. The ZIP
is parsed only from the very same memory bytes whose size and SHA were checked.
Completed scientific runs are never executed by this program.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile


def verify(raw, expected_size, expected_sha256):
    if len(raw) != expected_size:
        raise ValueError("ARCHIVE_SIZE_MISMATCH")
    if hashlib.sha256(raw).hexdigest() != expected_sha256.lower():
        raise ValueError("ARCHIVE_SHA256_MISMATCH")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or len(names) > 20000:
            raise ValueError("DUPLICATE_OR_EXCESSIVE_ARCHIVE_MEMBERS")
        if sum(info.file_size for info in infos) > 2 * 1024**3:
            raise ValueError("UNCOMPRESSED_ARCHIVE_LIMIT")
        for info in infos:
            path = PurePosixPath(info.filename)
            mode = stat.S_IFMT(info.external_attr >> 16)
            if (not info.filename or "\\" in info.filename or path.is_absolute()
                    or ".." in path.parts or str(path) != info.filename
                    or info.is_dir() or mode not in (0, stat.S_IFREG)):
                raise ValueError("UNSAFE_OR_NONREGULAR_ARCHIVE_MEMBER:" + info.filename)
        manifest_raw = archive.read("MANIFEST.json")
        manifest = json.loads(manifest_raw)
        if manifest.get("schema") != "BASS_CR_C22D_DELIVERY_MANIFEST_V1":
            raise ValueError("UNSUPPORTED_MANIFEST_SCHEMA")
        records = manifest["files"]
        paths = [row["path"] for row in records]
        if len(paths) != len(set(paths)) or set(names) != {"MANIFEST.json", *paths}:
            raise ValueError("PAYLOAD_MEMBER_SET_MISMATCH")
        payload = {}
        for row in records:
            data = archive.read(row["path"])  # Full read checks this member's CRC.
            if len(data) != row["size_bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
                raise ValueError("PAYLOAD_SIZE_OR_SHA256_MISMATCH:" + row["path"])
            payload[row["path"]] = data
    return manifest_raw, payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, required=True)
    parser.add_argument("--size", type=int, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--dest", type=Path)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(argv)
    if args.size <= 0 or not re.fullmatch(r"[0-9a-fA-F]{64}", args.sha256):
        parser.error("a positive byte size and exact SHA256 are required")
    if args.verify_only == (args.dest is not None):
        parser.error("choose --verify-only or --dest NEW_DIRECTORY")
    raw = args.zip.read_bytes()
    manifest_raw, payload = verify(raw, args.size, args.sha256)
    if args.dest is not None:
        args.dest.mkdir(parents=True, exist_ok=False)
        root = args.dest.resolve()
        for name, data in payload.items():
            target = root.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.resolve().is_relative_to(root):
                raise ValueError("RESTORE_PATH_ESCAPED_ROOT")
            with target.open("xb") as handle:
                handle.write(data)
        with (root / "MANIFEST.json").open("xb") as handle:
            handle.write(manifest_raw)
    print(json.dumps({"status": "VERIFIED" if args.verify_only else "RESTORED_CREATE_ONLY",
                      "archive_size_bytes": len(raw), "archive_sha256": hashlib.sha256(raw).hexdigest(),
                      "payload_files": len(payload), "CRC": "ALL_MEMBERS_FULL_READ_PASS",
                      "payload_size_SHA256": "PASS", "new_ODE": 0, "old_ODE_reruns": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
