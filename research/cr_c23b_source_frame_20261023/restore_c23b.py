"""Verify the exact memory bytes of a sealed research ZIP before any restore."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile


def verify(raw: bytes, expected_size: int, expected_sha256: str):
    if len(raw) != expected_size or hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("ARCHIVE_SIZE_OR_SHA256_MISMATCH")
    # Do not reopen a path after verification: parse these identical bytes.
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        infos = archive.infolist()
        names = [x.filename for x in infos]
        if len(names) != len(set(names)) or len(names) > 20000:
            raise ValueError("DUPLICATE_OR_EXCESS_MEMBERS")
        if sum(x.file_size for x in infos) > 512*1024**2:
            raise ValueError("UNCOMPRESSED_SIZE_LIMIT")
        for item in infos:
            path = PurePosixPath(item.filename)
            if path.is_absolute() or ".." in path.parts or "\\" in item.filename or item.is_dir():
                raise ValueError("UNSAFE_OR_NONFILE_MEMBER")
            if stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError("SYMLINK_MEMBER")
        manifest = json.loads(archive.read("MANIFEST.json"))
        prefix = "delivery/" if manifest.get("schema") == "C23A_FINAL_DOCUMENTS_RECOVERY_V1" else manifest.get("payload_prefix", "")
        expected = {prefix+name: row for name, row in manifest["files"].items()}
        if set(names) != set(expected) | {"MANIFEST.json"}:
            raise ValueError("MANIFEST_MEMBERSHIP_MISMATCH")
        payload = {}
        for name, row in expected.items():
            data = archive.read(name)  # full read checks each ZIP CRC
            size = row.get("bytes", row.get("size_bytes"))
            if len(data) != size or hashlib.sha256(data).hexdigest() != row["sha256"]:
                raise ValueError("MEMBER_SIZE_OR_SHA256_MISMATCH: "+name)
            payload[name] = data
    return manifest, payload


def restore(raw: bytes, expected_size: int, expected_sha256: str, destination: str | Path):
    manifest, payload = verify(raw, expected_size, expected_sha256)
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        target = root/name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(data)
    return {"restored_files":len(payload), "new_ODE":0, "same_verified_memory_bytes":True}


if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser(description="Restore exact verified C23B delivery bytes without science execution")
    parser.add_argument("archive", type=Path)
    parser.add_argument("--size", type=int, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args=parser.parse_args()
    data=args.archive.read_bytes()
    result=restore(data,args.size,args.sha256,args.destination)
    print(json.dumps(result,ensure_ascii=False,indent=2))
