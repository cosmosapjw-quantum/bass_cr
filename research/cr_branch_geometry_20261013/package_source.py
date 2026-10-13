"""Create a new, source-complete BASS_CR distribution ZIP without science runs.

Usage:
  python3 package_source.py --science-commit FULL_SHA --archive-path /abs/source.zip

The archive is a source snapshot. Final provider receipts are bound separately
by the final HANDOFF; publishing receipts later does not change these ZIP bytes.
SOURCE_MANIFEST.json is generated inside the ZIP and never hashes itself.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import uuid
import zipfile

ROOT = Path(__file__).resolve().parent
UNIT = "CR-THEORY-BRANCH-GEOMETRY-20261013"
MANIFEST_NAME = "SOURCE_MANIFEST.json"
INDEX_NAME = "EXTERNAL_REFERENCE_INDEX.json"
TEMP_PREFIX = ".bass-cr-package-"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp", ".gif"}
QA_DIRECTORIES = {"qa", "pdf_qa", "pdf-qa", "qa_images", "qa-images",
                  "qa_render", "qa-renders", "rendered_pages", "rendered-pages",
                  "montage", "montages"}
TEX_SUFFIXES = {".aux", ".log", ".toc", ".out", ".fls", ".fdb_latexmk",
                ".synctex", ".xdv"}


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def _relative_path(value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("index path must be a nonempty relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise ValueError("unsafe or noncanonical index path: " + value)
    return path


def external_cache_exclusions(root=ROOT):
    """Derive and verify the ten omissions from the actual current index."""
    root = Path(root)
    index_path = root / INDEX_NAME
    raw_index = index_path.read_bytes()
    index = json.loads(raw_index)
    retrieval = index.get("retrieval_records", [])
    supplementary = index.get("root_supplementary_records", [])
    if len(retrieval) != 8 or len(supplementary) != 2 or index.get("raw_cache_files") != 10:
        raise ValueError("current index must declare eight retrieval and two supplementary caches")
    records = []
    for family, entries, path_key, size_key, hash_key in (
        ("retrieval_records", retrieval, "cache_path", "cache_bytes", "cache_sha256"),
        ("root_supplementary_records", supplementary, "path", "bytes", "sha256"),
    ):
        for entry in entries:
            rel = _relative_path(entry[path_key])
            if rel.parts[:2] != ("inputs", "literature"):
                raise ValueError("external cache exclusion outside inputs/literature: " + str(rel))
            expected_size, expected_hash = entry[size_key], entry[hash_key]
            if (type(expected_size) is not int or expected_size < 0
                    or not isinstance(expected_hash, str)
                    or not re.fullmatch(r"[0-9a-f]{64}", expected_hash)):
                raise ValueError("invalid indexed cache identity: " + str(rel))
            path = root.joinpath(*rel.parts)
            if path.is_symlink() or not path.is_file():
                raise ValueError("indexed cache is missing or is a symlink: " + str(rel))
            raw = path.read_bytes()
            if len(raw) != expected_size or sha256(raw) != expected_hash:
                raise ValueError("indexed external cache identity mismatch: " + str(rel))
            records.append({"path": rel.as_posix(), "bytes": len(raw),
                            "sha256": sha256(raw), "index_record_family": family,
                            "disposition": "indexed_external_raw_cache_not_redistributed"})
    names = {record["path"] for record in records}
    if len(names) != 10:
        raise ValueError("duplicate external-cache path in index")
    actual = {p.relative_to(root).as_posix()
              for p in (root / "inputs/literature").rglob("*") if p.is_file()}
    if actual != names:
        raise ValueError("inputs/literature differs from the ten indexed raw caches: "
                         + repr(sorted(actual ^ names)))
    return sorted(records, key=lambda record: record["path"]), {
        "path": INDEX_NAME, "bytes": len(raw_index), "sha256": sha256(raw_index)}


def exclusion_reason(relative, external_paths):
    """Exclude execution debris while retaining scientific figures and raw evidence."""
    rel = PurePosixPath(relative)
    name, suffix = rel.name.lower(), rel.suffix.lower()
    lower_parts = tuple(part.lower() for part in rel.parts)
    if rel.as_posix() in external_paths:
        return "indexed_external_raw_cache"
    if rel.as_posix() == MANIFEST_NAME:
        return "manifest_generated_from_actual_archive_members"
    if ".git" in lower_parts:
        return "git_administrative_directory"
    if "__pycache__" in lower_parts or suffix == ".pyc":
        return "python_bytecode_cache"
    if suffix == ".zip":
        return "nested_or_previous_zip"
    if any(part.startswith(TEMP_PREFIX) or part.startswith(".package-source-")
           or part in {"packaging_tmp", "packaging-temp", ".packaging-tmp"}
           for part in lower_parts):
        return "packaging_temporary_file"
    if suffix in IMAGE_SUFFIXES and (
        any(part in QA_DIRECTORIES for part in lower_parts[:-1])
        or "montage" in name
        or re.match(r"(?:pdf[-_]?qa|qa[-_])", name)
        or ("latex" in lower_parts and re.match(r"(?:page|report)[-_]\d+\.", name))
    ):
        return "pdf_qa_raster_or_montage"
    if "latex" in lower_parts:
        if suffix in TEX_SUFFIXES or name.endswith(".synctex.gz"):
            return "tex_intermediate_or_log"
        if re.match(r"(?:compile|attempt01_compile).*\.(?:stdout|stderr)(?:\.txt)?$", name):
            return "tex_compile_stdout_or_stderr"
        if name.startswith("attempt01") and (
            name.endswith(".log") or ".stdout" in name or ".stderr" in name
        ):
            return "tex_attempt01_log"
    return None


def distribution_plan(root=ROOT):
    """Read-only plan, including raw-cache identity checks; creates no artifacts."""
    root = Path(root)
    external, index_identity = external_cache_exclusions(root)
    external_paths = {record["path"] for record in external}
    files, omitted = [], []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("symlink is not an admitted snapshot member: " + str(path))
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        reason = exclusion_reason(rel, external_paths)
        if reason:
            omitted.append({"path": rel, "reason": reason})
        else:
            files.append(path)
    required = {
        INDEX_NAME, "CONTRACT.json", "CLAIMS.json", "RESULTS.json", "SOURCES.json",
        "NEXT_DAG.json", "PLAN_KO.md", "HANDOFF.json", "REPORT_KO.md",
        "geometry_kernel_rebind.py", "coupled_branch_solver.py", "reaction_branch_continuation.py",
        "package_source.py", "latex/report.pdf", "latex/report.tex", "latex/manuscript.md",
        "latex/fonts/DejaVuSansMono.ttf", "latex/fonts/NotoSansCJKkr-Bold.otf",
        "latex/fonts/NotoSansCJKkr-Regular.otf", "latex/fonts/README.md",
        "licenses/DejaVu-LICENSE.txt", "licenses/Noto-OFL.txt",
        "inputs/prior/kernel_event_adapter.py", "inputs/prior/inputs/KERNEL_SOURCE_BINDING.json",
    }
    relative = {path.relative_to(root).as_posix() for path in files}
    if not required <= relative:
        raise ValueError("missing required source/report/font dependency: "
                         + repr(sorted(required - relative)))
    if not any(name.startswith("review/") for name in relative):
        raise ValueError("review metadata is missing from the source snapshot")
    return {"files": files, "omitted": omitted, "external": external,
            "index_identity": index_identity}


def _snapshot(plan, root=ROOT):
    """Freeze member bytes in memory; the manifest hashes these exact payloads."""
    root = Path(root)
    payloads, records = {}, []
    for path in plan["files"]:
        before = path.stat()
        raw = path.read_bytes()
        after = path.stat()
        state0 = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        state1 = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        if state0 != state1 or len(raw) != after.st_size:
            raise ValueError("source changed during snapshot: " + str(path))
        rel = path.relative_to(root).as_posix()
        payloads[rel] = raw
        records.append({"path": rel, "bytes": len(raw), "sha256": sha256(raw),
                        "mode": "0755" if before.st_mode & stat.S_IXUSR else "0644"})
    if sha256(payloads[INDEX_NAME]) != plan["index_identity"]["sha256"]:
        raise ValueError("external-reference index changed while collecting snapshot")
    return payloads, records


def build_manifest(records, plan, science_commit, archive_name, root=ROOT):
    return {
        "schema": "bass-cr-source-manifest.v2", "unit": UNIT,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "repository": "cosmosapjw-quantum/bass_cr", "science_commit": science_commit,
        "science_commit_semantics": "Caller-supplied frozen science commit; member hashes bind the actual archive-stage files, including later packaging metadata.",
        "archive_filename": archive_name, "archive_member_prefix": Path(root).name + "/",
        "stage": "source snapshot before final external-provider delivery receipts",
        "archive_stage_note": "SOURCE_MANIFEST describes only this immutable source snapshot. Final provider receipts and final Git/delivery identities are separately bound by the final HANDOFF. Later HANDOFF or receipt updates do not mutate the archive.",
        "file_count_excluding_manifest": len(records), "archive_member_count": len(records)+1,
        "manifest_self_hash": "omitted to avoid recursion; SOURCE_MANIFEST is not an entry in its own files array",
        "archive_identity_location": "returned packaging receipt and final HANDOFF; not recursively embedded here",
        "files": records, "external_reference_index": plan["index_identity"],
        "external_raw_cache_exclusions": plan["external"],
        "external_raw_cache_count": len(plan["external"]),
        "other_omissions": [record for record in plan["omitted"]
                            if record["reason"] != "indexed_external_raw_cache"],
        "coverage": "All regular current source, result, bound prior-input, LaTeX/PDF, scientific figure, font/license, policy and review files except the explicitly listed omissions.",
        "fonts": "Exact bundled font binaries, their README, and Noto/DejaVu licenses are included.",
        "prior_metadata_semantics": "Nested prior manifests and evidence retain their historical meanings; their bytes are included unchanged.",
        "scientific_checks_executed": 0, "ODE_executions": 0, "NCP_dispatches": 0,
    }


def _archive_info(name, mode="0644"):
    info = zipfile.ZipInfo(name, date_time=(2026, 10, 13, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | int(mode, 8)) << 16
    return info


def create_archive(science_commit, archive_path):
    if not re.fullmatch(r"[0-9a-f]{40}", science_commit):
        raise ValueError("science commit must be a complete lowercase 40-character Git SHA")
    archive = Path(archive_path)
    if not archive.is_absolute() or archive.suffix.lower() != ".zip":
        raise ValueError("archive path must be an absolute .zip path")
    if os.path.lexists(archive):
        raise FileExistsError("create-only archive already exists: " + str(archive))
    archive = archive.resolve()
    if archive.is_relative_to(ROOT.resolve()):
        raise ValueError("archive must be outside the source directory")
    plan = distribution_plan()
    payloads, records = _snapshot(plan)
    manifest = build_manifest(records, plan, science_commit, archive.name)
    manifest_raw = (json.dumps(manifest, ensure_ascii=False, indent=2)+"\n").encode("utf-8")
    prefix = ROOT.name + "/"
    archive.parent.mkdir(parents=True, exist_ok=True)
    temp = archive.parent / (TEMP_PREFIX + uuid.uuid4().hex + ".zip.tmp")
    owns_temp = False
    try:
        with zipfile.ZipFile(temp, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            owns_temp = True
            for record in records:
                z.writestr(_archive_info(prefix+record["path"], record["mode"]),
                           payloads[record["path"]], compresslevel=9)
            z.writestr(_archive_info(prefix+MANIFEST_NAME), manifest_raw, compresslevel=9)
        expected = {prefix+record["path"] for record in records} | {prefix+MANIFEST_NAME}
        with zipfile.ZipFile(temp) as z:
            names = z.namelist()
            if len(names) != len(expected) or set(names) != expected:
                raise ValueError("archive member set does not match the manifest")
            if z.read(prefix+MANIFEST_NAME) != manifest_raw:
                raise ValueError("archived manifest bytes differ from generated manifest")
            for record in records:
                raw = z.read(prefix+record["path"])
                if len(raw) != record["bytes"] or sha256(raw) != record["sha256"]:
                    raise ValueError("archive payload identity mismatch: " + record["path"])
        with temp.open("rb") as handle:
            os.fsync(handle.fileno())
        raw_archive = temp.read_bytes()
        receipt = {"path": str(archive), "bytes": len(raw_archive),
                   "sha256": sha256(raw_archive),
                   "md5": hashlib.md5(raw_archive, usedforsecurity=False).hexdigest(),
                   "manifest_sha256": sha256(manifest_raw),
                   "members": len(expected), "external_caches_indexed_and_excluded": 10,
                   "integrity": "PASS", "scientific_checks_executed": 0,
                   "publication_method": "atomic create-only hard link of fully verified temporary ZIP"}
        # Unlike rename/replace, this fails atomically if another writer has
        # created the destination. The temporary file is on the same filesystem.
        os.link(temp, archive)
        return receipt
    finally:
        if owns_temp:
            temp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--science-commit", required=True)
    parser.add_argument("--archive-path", required=True, type=Path)
    args = parser.parse_args()
    try:
        receipt = create_archive(args.science_commit, args.archive_path)
    except (ValueError, FileExistsError, OSError) as error:
        parser.exit(1, "Packaging failed: " + str(error) + "\n")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
