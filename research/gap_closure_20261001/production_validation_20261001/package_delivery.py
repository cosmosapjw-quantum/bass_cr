"""Build a create-only R4V continuation archive with exact member identities.

Run only after all computations, reviews, and report/DB updates are terminal.
The preceding R4U archive is included as an immutable recovery base.
"""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile


def build(root: Path, output: Path):
    if output.exists():
        raise ValueError("create-only archive required")
    members = {}

    def add(path, name):
        if name in members:
            raise ValueError("duplicate archive member: " + name)
        members[name] = path

    def tree(folder, prefix, exclude_receipts=False):
        for p in sorted(folder.rglob("*")):
            if not p.is_file() or p.is_symlink():
                continue
            if "__pycache__" in p.parts or p.suffix == ".pyc" or ".openai-download-" in p.name:
                continue
            if exclude_receipts and (p.suffix == ".zip" or "LIBRARY_RECEIPT" in p.name):
                continue
            add(p, prefix + "/" + p.relative_to(folder).as_posix())

    base = root / "recovery_r4v/BASS_CR_R4U_SOLVER_AUDIT_PACKAGE_20261001_v1.zip"
    expected = "f3ebd034b795751235c154f56c5e69bb75953fef8d3d94e34b7e96defa867a69"
    if hashlib.sha256(base.read_bytes()).hexdigest() != expected:
        raise ValueError("recovery base identity mismatch")
    add(base, "base/" + base.name)
    for name in ("source", "runtime_inputs", "native_build_portable"):
        tree(root / "recovered_r4u" / name, name)
    tree(root / "runs_r4v", "runs_r4v")
    tree(root / "recovery_r4v", "recovery_r4v", exclude_receipts=True)
    for p in sorted((root / "deliverables_r4v").iterdir()):
        if p.is_file() and p.suffix in {".md", ".json", ".csv", ".png", ".sqlite"} and "RECEIPT" not in p.name:
            add(p, "reports/" + p.name)

    manifest = {
        "schema": "BASS_R4V_ARCHIVE_MANIFEST_V1",
        "recovery_base_sha256": expected,
        "member_count_excluding_manifest": len(members),
        "members": [
            {"path": name, "bytes": p.stat().st_size,
             "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
            for name, p in sorted(members.items())
        ],
        "scope": "R4U immutable base plus R4V source, inputs, native binaries, actual runs, reviews, report and DB overlay",
        "excluded": ["earlier continuation ZIP checkpoints", "partial download fragments", "Library receipts", "pycache"],
        "scientific_ceiling": {"production": "HOLD", "capture": False, "all_bound": "OPEN", "b_grid": "NO_GO"},
    }
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, p in sorted(members.items()):
            z.writestr(name, p.read_bytes())
        z.writestr("MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    with zipfile.ZipFile(output) as z:
        if z.testzip() is not None:
            raise ValueError("archive CRC validation failed")
        if len(z.namelist()) != len(members) + 1:
            raise ValueError("archive membership validation failed")
        for e in manifest["members"]:
            content = z.read(e["path"])
            if len(content) != e["bytes"] or hashlib.sha256(content).hexdigest() != e["sha256"]:
                raise ValueError("archive member identity validation failed: " + e["path"])
    return {"schema": "BASS_R4V_PACKAGE_VALIDATION_V1", "file": output.name,
            "bytes": output.stat().st_size, "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "members_including_manifest": len(members) + 1, "CRC": "PASS", "member_sha256_check": "PASS",
            "production": "HOLD", "capture": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    a = parser.parse_args()
    if a.receipt.exists():
        raise ValueError("create-only receipt required")
    result = build(a.root.resolve(), a.output.resolve())
    with a.receipt.open("x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps(result))
