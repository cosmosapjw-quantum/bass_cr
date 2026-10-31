#!/usr/bin/env python3
"""Restore the complete PHYS25 source/data/figure ZIP from twelve exact Git blobs."""
from pathlib import Path
import argparse, hashlib, io, json, zipfile

EXPECTED_SIZE = 5759964
EXPECTED_SHA256 = "5d51ae1e9c0def6707e11307c370e1b7d57635272abd7273da0e78121c09d22d"
EXPECTED_PART_SHA1 = [
    "0d3cff156879e314f011771ad541aa023f799e90",
    "7b7a19648409faf87c808df5e6f281555328d94f",
    "94cb00c596b15cad07f6d23bebbcf9d6784a4c01",
    "0986cd8c5803ed8ff73a455556b91f37ec0592b7",
    "4173fd7de8c0b91f2b92d5ab6352d48ae409a207",
    "b6a746cf844514c2eec4b25ab22401eb8de213d6",
    "4c05241f0c8cdfb1c53cce310ed174dd2dd0a08e",
    "46e2e91eaa93566658fd375892042534640ebef7",
    "85e3d707fd14385c355dd97e438177f96559ba7f",
    "95b61dfdce62c4b7b33945b5dcdc79e2327f81d5",
    "73e06e98635d1f91defc1f79a7a2385103c080c4",
    "5031c5b684e1827353eb6e1b27f3fa8164ad107f",
]

def restore(output: Path):
    directory = Path(__file__).resolve().parent / "zip_parts"
    data = bytearray()
    for i, expected in enumerate(EXPECTED_PART_SHA1):
        part = directory / ("PHYS25_FULL.zip.part%03d" % i)
        chunk = part.read_bytes()
        gitsha = hashlib.sha1(b"blob " + str(len(chunk)).encode() + b"\x00" + chunk).hexdigest()
        if gitsha != expected:
            raise ValueError("Git blob mismatch: %s" % part)
        data.extend(chunk)
    actual = hashlib.sha256(data).hexdigest()
    if len(data) != EXPECTED_SIZE or actual != EXPECTED_SHA256:
        raise ValueError("Full ZIP byte-identity mismatch: size=%d sha=%s" % (len(data), actual))
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() is not None:
            raise ValueError("ZIP CRC failure")
        manifest = json.loads(z.read("MANIFEST.json"))
        names = set(z.namelist())
        if names != set(manifest["members"]) | {"MANIFEST.json"}:
            raise ValueError("ZIP manifest member mismatch")
        for name, rec in manifest["members"].items():
            raw = z.read(name)
            if len(raw) != rec["bytes"] or hashlib.sha256(raw).hexdigest() != rec["sha256"]:
                raise ValueError("ZIP member digest mismatch: %s" % name)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    print("PHYS25_GITHUB_FULL_RESTORE_PASS",len(EXPECTED_PART_SHA1),len(names),len(data),actual,output)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=Path("/tmp/BASS_CR_PHYS25_FULL.zip"))
    restore(p.parse_args().output)
