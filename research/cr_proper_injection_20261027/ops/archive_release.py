#!/usr/bin/env python3
"""Create and locally verify the one immutable SOURCE ZIP after root freezes S.

No science modules, providers, quadrature, projections or solvers are executed.
Scope: this unit's files plus the five exact INPUT_MANIFEST entries and the
explicit qualified provenance files below. Top-level ops/library helpers,
credentials, .git and other units' unrelated work are outside the archive.

Usage:
  python ops/archive_release.py --repo /absolute/bass_cr --source-sha ACTUAL_S \
    --published-paths /absolute/ops/published_paths.json --output-dir /absolute/releases

Outputs are create-only. ZIP and receipt stay outside the unit. Use the exact
same successful ZIP bytes for both later provider uploads/R3; never rebuild it
to insert later D/M or backup metadata. Closeout packaging is a separate action.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import zipfile
import zlib

UNIT = "research/cr_proper_injection_20261027"
RAW = "research/cr_phys02c_paired_9600_closeout_20261011/raw/THIRD_GRID_LOCAL_20261011_EXEC01"
BASE_D = "ec463db0c7e5c7fb5070796071c926caa4db6445"
MANIFEST_NAME = "MANIFEST.json"
INPUT_PATHS = {
    RAW + "/SPECTRUM_fullBED_9600.npz",
    RAW + "/NUMERICAL_RESULT.json",
    "research/cr_heiii_ground_rr_20261027/ADMISSION.json",
    "research/cr_heiii_ground_rr_20261027/implementation/export_adapter.py",
    "research/cr_external_interfaces_20261025/INTERFACE_CONTRACT.json",
}
# Sizes/hashes for these are read from the already qualified intake record.
QUALIFIED_PATHS = (
    "research/cr_phys01_20261010/src/injection.py",
    "research/cr_phys01_20261010/src/rudd.py",
    "research/cr_phys02a_20261010/src/causal_subthreshold.py",
    "research/cr_phys02b_20261010/src/causal_cascade.py",
    "research/cr_phys02c_20261011/state/SCIENTIFIC_CONTRACT.json",
    RAW + "/ACTUAL_EXIT.json",
)
# Actual admission is PLAN_AND_ADMISSION, not an invented PHYS02 ADMISSION path.
EXTRA_PINS = {
    RAW + "/PLAN_AND_ADMISSION.json":
        (12432, "4e4c7fd3fc25f0e686fa3d03ac84ae151099d512ada33db8b22d8aa41a9413ab"),
    "research/cr_phys02c_paired_9600_closeout_20261011/INDEPENDENT_DECISION.json":
        (2864, "1c0f45db150efba6fc0b97572309c97fec8ba04b103a28d4e1fa283e7943e354"),
    "research/cr_source_binding_20261012/CONTRACT.json":
        (5700, "55c7630675b9de175215413ba0273e4a2db3af3154d7dc307aa2f58016a324cc"),
    "research/cr_heiii_ground_rr_20261027/FROZEN_CONTRACT.md":
        (7527, "73ec000acf2dc737bd5902bc761b2f3ccb662f1d800565b85a3cb128bd632e9b"),
}
SKIP_DIRS = {"__pycache__", "mplcache", ".git", ".ssh", ".aws", "tmp", "temp"}
SKIP_SUFFIXES = (".pyc", ".pyo", ".lock", ".tmp", ".temp", ".part", ".swp", ".swo", "~")


class ArchiveError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise ArchiveError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def crc(raw):
    return format(zlib.crc32(raw) & 0xffffffff, "08x")


def safe_relative(value):
    need(isinstance(value, str), "Repository path must be a string")
    p = PurePosixPath(value)
    need(not p.is_absolute() and ".." not in p.parts and str(p) == value
         and "\\" not in value and value not in ("", "."), "Unsafe repository path")
    return value


def excluded(rel):
    p = PurePosixPath(rel)
    if any(part in SKIP_DIRS for part in p.parts):
        return "cache/temp/private-metadata directory"
    name = p.name.lower()
    if name.endswith(SKIP_SUFFIXES):
        return "cache/lock/temp file"
    if (name == ".env" or name.startswith(".env.") or name.startswith("credentials")
            or name in {".netrc", "id_rsa", "id_ed25519"}
            or name.endswith((".pem", ".key", ".p12", ".pfx"))):
        return "credential/key path excluded"
    return None


def unit_files(repo):
    chosen, omitted = {}, []
    for current, dirs, files in os.walk(repo / UNIT, followlinks=False):
        current = Path(current)
        for name in list(dirs):
            p = current / name
            rel = p.relative_to(repo).as_posix()
            reason = excluded(rel)
            if reason:
                dirs.remove(name)
                omitted.append({"path": rel + "/", "reason": reason})
            else:
                need(not p.is_symlink(), "Unit symlink directories are not archived")
        for name in files:
            p = current / name
            rel = p.relative_to(repo).as_posix()
            reason = excluded(rel)
            if reason:
                omitted.append({"path": rel, "reason": reason})
            else:
                need(p.is_file() and p.resolve() == p, "Unit symlinks/nonfiles are not archived")
                chosen[rel] = p
    return chosen, sorted(omitted, key=lambda row: row["path"])


def local_git(repo, *args):
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(["git", "-c", "protocol.allow=never", *args],
                            cwd=repo, env=env, capture_output=True)
    need(result.returncode == 0,
         "Read-only local Git query failed; materialize the exact S commit/trees before packaging")
    return result.stdout


def git_entries(repo, source, paths):
    result = {}
    raw = local_git(repo, "ls-tree", "-r", "-z", "--full-tree", source, "--", *paths)
    for item in raw.split(b"\0"):
        if not item:
            continue
        metadata, name = item.split(b"\t", 1)
        mode, kind, oid = metadata.decode("ascii").split()
        rel = safe_relative(name.decode("utf-8"))
        need(kind == "blob" and mode in ("100644", "100755"), "Unsupported Git entry in source scope")
        result[rel] = {"mode": mode, "blob_sha1": oid}
    return result


def pinned_file(repo, rel):
    original = repo / rel
    retained = repo / "research/cr_source_binding_20261012/inputs/source_lineage/sources" / rel
    p = original if original.is_file() else retained
    need(p.is_file() and p.resolve() == p, "Required exact dependency is missing or symlinked: " + rel)
    return p


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--published-paths", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve(strict=True)
    source = args.source_sha
    need(re.fullmatch(r"[0-9a-f]{40}", source) is not None, "Actual immutable source S required")
    need(local_git(repo, "rev-parse", "HEAD").decode().strip() == source,
         "Local HEAD must equal source S; do not substitute later D/M bytes")
    out = args.output_dir.resolve()
    need(out != repo / UNIT and repo / UNIT not in out.parents, "Outputs must be outside the unit")
    name = "BASS_CR_PROPER_SOURCE_20261027_" + source[:12]
    archive, receipt_path = out / (name + ".zip"), out / (name + ".receipt.json")
    need(not archive.exists() and not receipt_path.exists(), "Create-only source archive/receipt already exists")

    published_path = args.published_paths.resolve(strict=True)
    published_raw = published_path.read_bytes()
    inventory = json.loads(published_raw)
    need(type(inventory) is list and all(isinstance(p, str) for p in inventory),
         "published_paths.json must be root's repository-relative path list")
    published = {safe_relative(p) for p in inventory}
    need(len(published) == len(inventory), "Duplicate published inventory paths")
    selected, omitted = unit_files(repo)
    need(bool(selected), "Unit directory is empty")
    input_manifest = json.loads((repo / UNIT / "inputs/INPUT_MANIFEST.json").read_bytes())
    entries = input_manifest.get("files")
    need(type(entries) is list and len(entries) == 5
         and {row.get("path") for row in entries} == INPUT_PATHS,
         "Exactly the five frozen INPUT_MANIFEST dependency paths are required")
    pins = {}
    for row in entries:
        need(row.get("commit") == BASE_D, "INPUT_MANIFEST baseline commit changed")
        pins[row["path"]] = (row["bytes"], row["sha256"], "INPUT_MANIFEST", BASE_D)
    qualification = json.loads((repo / UNIT / "intake/SOURCE_QUALIFICATION.json").read_bytes())
    qualified = {row["original_git_path"]: row for row in qualification["read_evidence"]}
    for rel in QUALIFIED_PATHS:
        row = qualified[rel]
        pins[rel] = (row["bytes"], row["sha256"], "QUALIFIED_ORIGINAL_SOURCE",
                     row["source_commit"])
    for rel, (size, checksum) in EXTRA_PINS.items():
        pins[rel] = (size, checksum, "EXPLICIT_ADMISSION_OR_CONTRACT", BASE_D)
    for rel in pins:
        selected[rel] = pinned_file(repo, rel)

    tree = git_entries(repo, source, [UNIT, *sorted(pins)])
    for rel in published:
        if rel.startswith(UNIT + "/") and not excluded(rel):
            need(rel in selected and rel in tree, "Published unit path absent locally or at S: " + rel)
    for rel in tree:
        if rel.startswith(UNIT + "/") and not excluded(rel):
            need(rel in selected, "Git-at-S unit file missing from local closure: " + rel)

    records = []
    for rel, path in sorted(selected.items()):
        raw = path.read_bytes()
        if rel in pins:
            size, checksum, role, commit = pins[rel]
            need(len(raw) == size and sha(raw) == checksum, "Pinned dependency mismatch: " + rel)
        else:
            role, commit = "CURRENT_UNIT_FILE", None
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        entry = tree.get(rel)
        if entry:
            need(blob == entry["blob_sha1"], "Local bytes differ from Git S: " + rel)
            publication = ("GIT_PUBLISHED_AT_S_ROOT_INVENTORY" if rel in published
                           else "GIT_PRESENT_AT_S_NOT_LISTED_IN_ROOT_INVENTORY")
        else:
            need(rel not in published, "Root inventory claims a path absent at S: " + rel)
            publication = "ARCHIVE_ONLY_NOT_PRESENT_IN_GIT_S"
        records.append({
            "path": rel, "bytes": len(raw), "sha256": sha(raw), "crc32": crc(raw),
            "role": role, "dependency_pin_commit": commit,
            "local_source_path": path.relative_to(repo).as_posix(),
            "publication_class": publication, "listed_in_root_published_paths": rel in published,
            "git_blob_sha1_at_S": None if entry is None else entry["blob_sha1"],
            "zip_mode": "100644" if entry is None else entry["mode"],
        })
    manifest = {
        "schema": "CR_PROPER_SOURCE_ARCHIVE_MANIFEST_V1", "unit": "CR_PROPER_INJECTION_RETURN_V1",
        "source_commit_S": source, "source_tree": local_git(repo, "rev-parse", source + "^{tree}").decode().strip(),
        "created_utc": datetime.now(timezone.utc).isoformat(), "archive_filename": archive.name,
        "scope": "Entire selected unit plus five frozen inputs and explicit qualified source/admission/contracts",
        "published_paths_inventory_sha256": sha(published_raw), "published_inventory_entries": len(inventory),
        "archive_only_meaning": "Exact frozen local artifact; not falsely represented as a Git S file",
        "earlier_source_snapshot": qualification["source_commit_original"],
        "baseline_D": BASE_D, "files": records, "payload_files": len(records),
        "excluded_unit_paths": omitted, "manifest_does_not_hash_itself": True,
        "old_science_replays": 0, "new_scientific_executions": 0,
        "scope_limits": "Upstream model/errors, old failures/budgets and physical input gates are unchanged",
    }
    manifest_raw = (json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for row in records:
            raw = selected[row["path"]].read_bytes()
            need(len(raw) == row["bytes"] and sha(raw) == row["sha256"], "File changed while packaging")
            info = zipfile.ZipInfo(row["path"], date_time=(2026, 10, 27, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = int(row["zip_mode"], 8) << 16
            z.writestr(info, raw)
        z.writestr(MANIFEST_NAME, manifest_raw)
    with zipfile.ZipFile(archive, "r") as z:
        need(z.testzip() is None, "ZIP CRC validation failed")
        need(len(z.namelist()) == len(records) + 1
             and set(z.namelist()) == {MANIFEST_NAME, *selected}, "ZIP member set mismatch")
        need(z.read(MANIFEST_NAME) == manifest_raw, "ZIP manifest byte mismatch")
        for row in records:
            raw = z.read(row["path"]); info = z.getinfo(row["path"])
            need(len(raw) == row["bytes"] and sha(raw) == row["sha256"]
                 and crc(raw) == row["crc32"] and format(info.CRC, "08x") == row["crc32"],
                 "ZIP member size/hash/CRC mismatch: " + row["path"])
    current_files, _ = unit_files(repo)
    need(set(current_files) == {p for p in selected if p.startswith(UNIT + "/")},
         "Unit file set changed while packaging; retain this attempt for diagnosis")
    for row in records:
        need(sha(selected[row["path"]].read_bytes()) == row["sha256"], "Source changed during packaging")
    need(published_path.read_bytes() == published_raw, "Published inventory changed while packaging")
    need(local_git(repo, "rev-parse", "HEAD").decode().strip() == source, "HEAD advanced while packaging")
    whole = archive.read_bytes()
    receipt = {
        "schema": "CR_PROPER_SOURCE_ARCHIVE_LOCAL_RECEIPT_V1", "status": "PASS_LOCAL_BYTES_HASH_CRC_ALL_MEMBERS",
        "source_commit_S": source, "source_tree": manifest["source_tree"], "archive": str(archive),
        "bytes": len(whole), "sha256": sha(whole), "members": len(records) + 1, "payloads": len(records),
        "manifest_sha256": sha(manifest_raw), "manifest_bytes": len(manifest_raw),
        "testzip": "PASS", "every_payload_size_sha256_crc32": "PASS",
        "published_paths_inventory_sha256": sha(published_raw),
        "publication_class_counts": {key: len([r for r in records if r["publication_class"] == key])
                                     for key in sorted({r["publication_class"] for r in records})},
        "remote_backup_or_R3_performed_by_this_helper": False,
        "next_action": "Upload these exact immutable ZIP bytes twice; independently full-GET both originals for R3. Later D/M metadata goes in a separate closeout.",
        "old_science_replays": 0, "new_scientific_executions": 0,
    }
    with receipt_path.open("x") as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write("\n")
    print(json.dumps(receipt, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except (ArchiveError, OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
        print("Source archive preparation failed; retain any new partial files: " + str(exc), file=sys.stderr)
        raise SystemExit(2)

