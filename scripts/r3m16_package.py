"""Create-only R3M16 stage archives with streamed member verification."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile


def sha(path: Path, algorithm: str = "sha256") -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def package(root: Path, stage: str) -> dict:
    if stage not in ("A1", "B1"):
        raise ValueError("only the two registered collision stages may be packaged")
    root = Path(root).resolve(); repo = root / "worktree"; job = root / stage
    if not (job / "COMPLETE.json").is_file():
        raise ValueError("only a completed witnessed collision may be packaged")
    dest = root / "packages" / stage
    dest.mkdir(parents=True, exist_ok=False)
    shutil.copytree(job, dest / stage)
    for name in ("cr_repro", "vendor_w1r", "configs/r3m16", "scripts", "tests", "docs/r3m16", "docs/roadmap"):
        source = repo / name
        if source.exists():
            shutil.copytree(source, dest / "source" / name,
                            ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    for name in ("pyproject.toml", "requirements.txt"):
        shutil.copy2(repo / name, dest / "source" / name)
    manifest = {
        "schema": "BASS_CR_R3M16_STAGE_PACKAGE_V1", "stage": stage,
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        "numerical_source_digest": "581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b",
        "claim_ceiling": "N1_TDL OPEN; all-bound OPEN; b-grid NO_GO; no scientific admission from delivery",
        "files": [{"path": str(path.relative_to(dest)), "bytes": path.stat().st_size,
                   "sha256": sha(path)} for path in sorted(dest.rglob("*")) if path.is_file()],
    }
    manifest_path = dest / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    archive = root / f"BASS_CR_R3M16_{stage}_20260923_v1.tar.zst"
    if archive.exists():
        raise FileExistsError(archive)
    subprocess.run(["tar", "-I", "zstd -T2 -3", "-cf", str(archive), "-C", str(dest), "."], check=True)
    expected = {row["path"]: row for row in manifest["files"]}; seen = set()
    process = subprocess.Popen(["zstd", "-dc", str(archive)], stdout=subprocess.PIPE)
    with tarfile.open(fileobj=process.stdout, mode="r|") as tar:
        for member in tar:
            if not member.isfile():
                continue
            name = member.name.removeprefix("./")
            if name == "MANIFEST.json":
                continue
            if name not in expected:
                raise ValueError(f"unregistered archive member: {name}")
            member_sha = hashlib.file_digest(tar.extractfile(member), "sha256").hexdigest()
            if member.size != expected[name]["bytes"] or member_sha != expected[name]["sha256"]:
                raise ValueError(f"archive member mismatch: {name}")
            seen.add(name)
    if process.wait() != 0 or seen != set(expected):
        raise ValueError("archive streaming verification incomplete")
    archive.chmod(0o444)
    identity = {"stage": stage, "path": str(archive), "name": archive.name,
                "bytes": archive.stat().st_size, "sha256": sha(archive),
                "manifest_sha256": sha(manifest_path),
                "local_archive_members_verified": len(seen),
                "upload_verified": False, "restore_verified": False}
    identity_path = root / f"ARCHIVE_{stage}.json"
    identity_path.write_text(json.dumps(identity, indent=2) + "\n")
    parts_dir = root / "drive_parts" / stage
    parts_dir.mkdir(parents=True, exist_ok=False)
    rows = []; chunk = 32 * 1024 ** 2
    total = (archive.stat().st_size + chunk - 1) // chunk
    with archive.open("rb") as stream:
        for index in range(total):
            data = stream.read(chunk)
            part = parts_dir / f"{archive.name}.part{index + 1:03d}of{total:03d}"
            part.write_bytes(data); part.chmod(0o444)
            rows.append({"index": index + 1, "name": part.name, "path": str(part),
                         "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                         "md5": hashlib.md5(data).hexdigest()})
    (root / f"DRIVE_PARTS_{stage}.json").write_text(json.dumps(
        {"schema": "BASS_CR_R3M16_DRIVE_PARTS_V1", "archive": identity,
         "ordered_parts": rows}, indent=2) + "\n")
    return identity


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--stage", choices=("A1", "B1"), required=True)
    args = parser.parse_args()
    print(json.dumps(package(args.root, args.stage), indent=2))
