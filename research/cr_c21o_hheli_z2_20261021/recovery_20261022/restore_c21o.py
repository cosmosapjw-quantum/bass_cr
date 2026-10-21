#!/usr/bin/env python3
"""Restore the immutable C21O content and later document snapshots; no ODE runs.

Inputs are exact archived deliveries. The destination must not already exist.
Original ZIPs remain unchanged. Source and raw members retain their content
identity; only the documented later Git documentation delta is overlaid.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile

PINS = {
    "content": (28473836, "5741bcac7943e91cdacd8ca15cd8c34ff8a83b7b08b6d8a6bfad31cdb5b2c781"),
    "document": (40319, "a8cf3cd2431332becd39465010e121ebc4ff172feab81a81c9da948883e79b1c"),
    "authority": (22972, "81a313ac58ca015f725f479a507c78fa40b19af0de60541b489c23272f99a796"),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pinned_bytes(path: Path, role: str) -> bytes:
    data = path.read_bytes()
    if (len(data), digest(data)) != PINS[role]:
        raise ValueError(f"{role}: archive size/SHA256 differs from the immutable pin")
    return data


def checked_members(path: Path, role: str) -> tuple[dict[str, bytes], dict]:
    verified = pinned_bytes(path, role)
    with zipfile.ZipFile(io.BytesIO(verified)) as z:
        names = z.namelist()
        if len(names) != len(set(names)):
            raise ValueError(f"{role}: duplicate archive member")
        members = {}
        for info in z.infolist():
            p = PurePosixPath(info.filename)
            if p.is_absolute() or ".." in p.parts or "\\" in info.filename or ":" in info.filename:
                raise ValueError(f"{role}: unsafe member name")
            if info.is_dir():
                continue
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError(f"{role}: symlink member")
            members[info.filename] = z.read(info)  # ZIP CRC checked by read.
    manifest = json.loads(members["SHA256_MANIFEST.json"])
    expected = set()
    for entry in manifest["files"]:
        name = entry["path"]
        if name in expected:
            raise ValueError(f"{role}: duplicate manifest entry")
        expected.add(name)
        data = members[name]
        size = entry.get("size_bytes", entry.get("bytes"))
        if len(data) != size or digest(data) != entry["sha256"]:
            raise ValueError(f"{role}: manifest mismatch: {name}")
        if "git_blob_sha1" in entry:
            git_sha = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
            if git_sha != entry["git_blob_sha1"]:
                raise ValueError(f"{role}: Git blob mismatch: {name}")
    allowed_extra = {"SHA256_MANIFEST.json", "SHA256SUMS"}
    if set(members) - expected - allowed_extra:
        raise ValueError(f"{role}: unmanifested payload")
    if "SHA256SUMS" in members:
        for line in members["SHA256SUMS"].decode().splitlines():
            sha, name = line.split(maxsplit=1)
            if digest(members[name.lstrip("*")]) != sha:
                raise ValueError(f"{role}: SHA256SUMS mismatch")
    return members, {"members": len(members), "manifest_payloads": len(expected),
                     "size_bytes": PINS[role][0], "sha256": PINS[role][1],
                     "manifest_and_CRC": "PASS"}


def restore(content: Path, document: Path, authority: Path, output: Path) -> dict:
    if output.exists():
        raise FileExistsError("Use a fresh create-only output directory")
    cm, cv = checked_members(content, "content")
    dm, dv = checked_members(document, "document")
    ab = pinned_bytes(authority, "authority")
    a = json.loads(ab)
    if a["content_commit"] != "6b6db06e8148e6826a2d5bf7dbc53d362126ca62" or a["document_head"] != "f7ca6905729f7d8d36ca0605f7b1dd7ad5595819":
        raise ValueError("Authority commit binding differs")
    payload = {n: b for n, b in cm.items() if n.startswith("research/")}
    overlay = {n: b for n, b in dm.items() if n.startswith("research/")}
    if len(overlay) != 11 or any(not n.endswith((".md", ".json")) for n in overlay):
        raise ValueError("Document overlay differs from the pinned 11-file delta")
    payload.update(overlay)
    output.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        dest = output / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("xb") as f:
            f.write(data)
    meta = output / "recovery_evidence"
    meta.mkdir()
    (meta / "C21O_FINAL_AUTHORITY_20261021T1603Z.json").write_bytes(ab)
    for role, members in (("content", cm), ("document", dm)):
        (meta / (role + "_SHA256_MANIFEST.json")).write_bytes(members["SHA256_MANIFEST.json"])
    for name, data in payload.items():
        if (output / name).read_bytes() != data:
            raise ValueError(f"Restored member byte mismatch: {name}")
    result = {
        "schema": "C21O_CREATE_ONLY_RECOVERY_V1",
        "utc": datetime.now(timezone.utc).isoformat(),
        "content_commit": a["content_commit"], "document_head": a["document_head"],
        "archives": {"content": cv, "document": dv},
        "authority_sha256": PINS["authority"][1],
        "restore_helper_sha256": digest(Path(__file__).read_bytes()),
        "restored_research_files": len(payload), "document_overlay_files": len(overlay),
        "output": str(output.resolve()), "restored_bytes": "PASS",
        "original_archives_modified": False, "ODE_integrations": 0,
        "global_error_bound": None,
    }
    (meta / "RESTORE_RECEIPT.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--content", type=Path, required=True)
    p.add_argument("--document", type=Path, required=True)
    p.add_argument("--authority", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(restore(args.content, args.document, args.authority, args.output), indent=2))
