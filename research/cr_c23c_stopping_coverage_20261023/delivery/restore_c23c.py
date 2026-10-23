"""Verify the same in-memory archive bytes, then optionally restore without science."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile


def verify_bytes(data: bytes, *, sha256: str, size: int):
    if len(data) != size or hashlib.sha256(data).hexdigest() != sha256:
        raise ValueError("archive size/SHA256 mismatch")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        infos=z.infolist(); names=[p.filename for p in infos]
        if len(names)!=len(set(names)) or "MANIFEST.json" not in names:
            raise ValueError("duplicate entries or missing manifest")
        for info in infos:
            path=PurePosixPath(info.filename)
            if path.is_absolute() or '..' in path.parts or not path.parts or '\\' in info.filename:
                raise ValueError("unsafe archive path")
            if info.is_dir() or stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError("only regular payload files are admitted")
        bad=z.testzip()
        if bad is not None:
            raise ValueError("ZIP CRC mismatch: "+bad)
        manifest=json.loads(z.read("MANIFEST.json"))
        rows=manifest["files"]
        if len(rows)!=len({r["path"] for r in rows}):
            raise ValueError("duplicate manifest entries")
        if set(names)!={r["path"] for r in rows}|{"MANIFEST.json"}:
            raise ValueError("archive membership mismatch")
        payload={}
        for row in rows:
            body=z.read(row["path"])
            if len(body)!=row["bytes"] or hashlib.sha256(body).hexdigest()!=row["sha256"]:
                raise ValueError("member size/SHA256 mismatch: "+row["path"])
            payload[row["path"]]=body
    return manifest,payload


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("archive",type=Path);p.add_argument("--sha256",required=True)
    p.add_argument("--size",type=int,required=True)
    p.add_argument("--destination",type=Path,help="optional new directory; existing destination is rejected")
    a=p.parse_args()
    data=a.archive.read_bytes()
    manifest,payload=verify_bytes(data,sha256=a.sha256,size=a.size)
    if a.destination is not None:
        a.destination.mkdir(parents=True,exist_ok=False)
        for name,body in payload.items():
            target=a.destination.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open("xb") as f:f.write(body)
        with (a.destination/"MANIFEST.json").open("xb") as f:
            f.write(zipfile.ZipFile(io.BytesIO(data)).read("MANIFEST.json"))
    print(json.dumps({"status":"PASS_SCOPED","archive_bytes":len(data),"sha256":a.sha256,
        "zip_crc":"PASS","payload_members_verified":len(payload),
        "restored":a.destination is not None,"new_science_executions":0,"new_ODE":0}))


if __name__=="__main__":main()
