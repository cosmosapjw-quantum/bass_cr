#!/usr/bin/env python3
"""Local immutable CR clock stage packager: payload, then actual commit, then zip.

No Git writes, network, science imports, solver runs or provider acknowledgements
are generated here. The root supplies actual Git publication receipts.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import time
from urllib.parse import parse_qs, urlsplit
import zipfile
import zlib

REPOSITORY = "cosmosapjw-quantum/bass_cr"
DEFAULT_UNIT = "research/cr_rr_causal_clock_20261027"
DEFAULT_BRANCH = "research/cr-rr-causal-clock-20261027"
STAGES = tuple(f"{f}{n:02d}" for f in ("R", "C") for n in range(1, 11))
TEXT_SUFFIXES = {".md", ".json", ".py", ".txt", ".csv", ".tsv", ".wl", ".wls", ".tex", ".bib",
    ".yaml", ".yml", ".toml", ".ini", ".cfg", ".sh", ".rs", ".f", ".f90", ".f95",
    ".c", ".h", ".cpp", ".hpp", ".m", ".dat"}
TEXT_NAMES = {"AGENTS.md", "LICENSE", "Makefile", "Dockerfile", ".gitignore"}
BINARY_SUFFIXES = {".npz", ".npy", ".h5", ".hdf5", ".parquet", ".arrow", ".pkl", ".pickle",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".gz", ".bz2", ".xz",
    ".tar", ".so", ".dll", ".dylib", ".o", ".a", ".exe", ".bin"}
CACHE_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".mplconfig", "mpl_config"}
PRIVATE_PARTS = {".git", ".aws", ".ssh", ".gnupg", "private_reading", "private_papers",
    "raw_private_context", "private_conversations"}
SECRET_NAMES = {".env", ".netrc", ".npmrc", ".pypirc", "credentials", "credentials.json",
    "id_rsa", "id_ed25519", "REPOSITORIES.json"}
SIGNED_KEYS = {"sig", "signature", "access_token", "refresh_token", "token", "downloadtoken", "awsaccesskeyid"}
POLICIES = ("AGENTS.md", ".codex/readback-policy.json", "docs/READBACK_POLICY.md",
    "docs/CHATGPT_CODEX_DIVISION_OF_LABOR_KO.md", "docs/HPC_ACCURACY_POLICY_KO.md")
SHA40, SHA64 = re.compile(r"[0-9a-f]{40}"), re.compile(r"[0-9a-f]{64}")


def need(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(raw):
    return {"bytes": len(raw), "sha256": digest(raw)}


def file_pin(path):
    h, size = hashlib.sha256(), 0
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            h.update(block)
            size += len(block)
    return {"bytes": size, "sha256": h.hexdigest()}


def read_json(path):
    def bad_constant(_):
        raise ValueError("NONFINITE_JSON_CONSTANT")
    return json.loads(path.read_bytes(), parse_constant=bad_constant)


def write_new(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)


def relpath(value):
    p = PurePosixPath(value)
    need(not p.is_absolute() and p.parts and "." not in p.parts and ".." not in p.parts,
         "UNSAFE_RELATIVE_PATH")
    need(str(p) == value and not any(ord(c) < 32 for c in value) and "\\" not in value,
         "NONCANONICAL_OR_CONTROL_PATH")
    return value


def safe_unit_path(repo, value):
    path = repo / relpath(value)
    need(path.is_dir() and not path.is_symlink(), "UNIT_DIRECTORY_REQUIRED")
    need(path.resolve().is_relative_to(repo), "UNIT_OUTSIDE_REPOSITORY")
    for parent in (path, *path.parents):
        if parent == repo:
            break
        need(not parent.is_symlink(), "SYMLINKED_UNIT_ANCESTOR")
    return path


def git(repo, *args, required=True):
    proc = subprocess.run(["git", "-C", str(repo), *args], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=False)
    if required:
        need(proc.returncode == 0, "GIT_READ_FAILED:" + args[0])
    return proc.returncode, proc.stdout


def git_text(repo, *args):
    return git(repo, *args)[1].decode("utf-8").strip()


def git_identity(repo):
    _, raw = git(repo, "status", "--porcelain=v1", "-z")
    return {"HEAD": git_text(repo, "rev-parse", "HEAD"),
            "branch": git_text(repo, "branch", "--show-current"),
            "status_bytes": len(raw), "status_sha256": digest(raw),
            "full_status_private_paths_omitted": True}


def index_rows(repo, unit):
    raw, rows = git(repo, "ls-files", "--stage", "-z", "--", unit)[1], {}
    for token in raw.split(b"\0"):
        if not token:
            continue
        fields, name = token.split(b"\t", 1)
        mode, oid, stage = fields.decode("ascii").split()
        path = relpath(name.decode("utf-8"))
        need(path.startswith(unit + "/"), "INDEX_PATH_OUTSIDE_UNIT")
        need(stage == "0" and mode in ("100644", "100755"), "INDEX_CONFLICT_OR_NONREGULAR:" + path)
        need(path not in rows, "DUPLICATE_INDEX_PATH")
        rows[path] = {"mode": mode, "oid": oid}
    return rows


def blob_oid(raw, object_format):
    constructor = hashlib.sha1 if object_format == "sha1" else hashlib.sha256
    return constructor(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def scan_text(path, raw):
    need(b"\0" not in raw, "NUL_BINARY_NOT_TEXT:" + path)
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise ValueError("NON_UTF8_TEXT_REJECTED:" + path) from None
    need(not any(ord(c) < 32 and c not in "\n\r\t" for c in text), "BINARY_CONTROL_CHARACTER:" + path)
    patterns = (
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        r"\bgh[pousr]_[A-Za-z0-9]{30,}\b", r"\bgithub_pat_[A-Za-z0-9_]{50,}\b",
        r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b", r"\bsk_live_[A-Za-z0-9]{20,}\b",
        r"(?i)\bAuthorization\s*:\s*Bearer\s+[A-Za-z0-9._~+/-]{16,}",
    )
    need(not any(re.search(p, text) for p in patterns), "CREDENTIAL_PATTERN_REJECTED:" + path)
    assignment = re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password)"
        r"""["']?\s*[:=]\s*["']([^"'\n]{8,})["']""")
    harmless = {"UNAVAILABLE", "REDACTED", "NOT_SET", "PLACEHOLDER", "CHANGE_ME"}
    for match in assignment.finditer(text):
        value = match.group(1)
        need(value.upper() in harmless or value.startswith(("$" + "{", "<", "os.environ", "env:")),
             "SECRET_ASSIGNMENT_REJECTED:" + path)
    for match in re.finditer(r"""https?://[^\s<>"')\]]+""", text):
        try:
            url = urlsplit(match.group(0))
            keys = {key.lower() for key in parse_qs(url.query, keep_blank_values=True)}
            signed = (any(k.startswith(("x-amz-", "x-goog-")) for k in keys)
                      or bool(keys & SIGNED_KEYS)
                      or ("dropboxusercontent.com" in url.netloc and "/apitl/" in url.path))
            need(not signed and not url.username and not url.password,
                 "SIGNED_OR_CREDENTIAL_URL_REJECTED:" + path)
        except ValueError:
            raise ValueError("UNSAFE_URL_REJECTED:" + path) from None
    return text


def classify(path, relative):
    parts = set(PurePosixPath(relative).parts)
    need(not (parts & PRIVATE_PARTS) and path.name not in SECRET_NAMES
         and not path.name.startswith(".env.") and path.suffix.lower() not in {".pem", ".key"},
         "PRIVATE_OR_SECRET_PATH_REJECTED:" + relative)
    if parts & CACHE_PARTS or path.suffix.lower() in {".pyc", ".pyo"}:
        return "DISPOSABLE_CACHE"
    if path.name.endswith(".lease") or "task_lease" in path.name:
        return "TEMPORARY_TASK_LEASE"
    if path.suffix.lower() in BINARY_SUFFIXES:
        return "BINARY_OR_DENSE_PAYLOAD_DEFERRED_TO_SOURCE_RELEASE"
    need(path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES,
         "UNREVIEWED_FILE_TYPE:" + relative)
    return None


def policy_context(repo, unit):
    paths = set(POLICIES)
    parent = PurePosixPath(unit)
    while str(parent) != ".":
        paths.add(str(parent / "AGENTS.md"))
        parent = parent.parent
    rows = []
    for name in sorted(paths):
        path = repo / name
        if path.exists():
            need(path.is_file() and not path.is_symlink(), "POLICY_NOT_REGULAR:" + name)
            rows.append({"path": name, "status": "LOCAL_BYTES_READ", **file_pin(path)})
        else:
            rows.append({"path": name, "status": "NOT_PRESENT_LOCALLY", "sha256": None})
    return {"policies": rows, "semantic_authority_review": "ROOT_OWNED", "remote_HEAD_check": "ROOT_OWNED"}


def previous_manifest(path, unit):
    if path is None:
        return {}, {}
    value = read_json(path)
    need(isinstance(value, dict), "PUBLIC_MANIFEST_PATH_HASH_MAP_REQUIRED")
    for name, sha in value.items():
        relpath(name)
        need(name.startswith(unit + "/") and isinstance(sha, str) and SHA64.fullmatch(sha),
             "INVALID_PREVIOUS_PUBLIC_PATH_OR_HASH")
    modes_path = path.parent / "UNIT_MANIFEST.json"
    modes = {}
    if modes_path.exists():
        old = read_json(modes_path)
        modes = {r["path"]: r["mode"] for r in old["files"] if r["checkpoint"] == "INCLUDED"}
    return value, modes


def assert_new_outside(repo, output):
    need(not output.exists(), "IMMUTABLE_OUTPUT_ALREADY_EXISTS")
    need(not output.is_relative_to(repo), "OUTPUT_MUST_BE_OUTSIDE_REPOSITORY")


def prepare(args):
    started = time.monotonic()
    repo, output = args.repo.resolve(), args.output.resolve()
    unit = safe_unit_path(repo, args.unit)
    assert_new_outside(repo, output)
    need(SHA40.fullmatch(args.expected_parent), "FULL_EXPECTED_PARENT_SHA_REQUIRED")
    need(re.fullmatch(r"\d{8}", args.date), "DATE_YYYYMMDD_REQUIRED")
    datetime.strptime(args.date, "%Y%m%d")
    need(args.max_text_bytes > 0 and args.max_total_text_bytes >= args.max_text_bytes, "POSITIVE_TEXT_LIMITS_REQUIRED")
    if args.central_count is not None:
        need(re.fullmatch(r"\d+/\d+", args.central_count), "CENTRAL_COUNT_N_OVER_D_REQUIRED")
    if args.completed_stages is not None:
        need(0 <= args.completed_stages <= 20, "COMPLETED_STAGES_RANGE")
    before = git_identity(repo)
    indexed = index_rows(repo, args.unit)
    object_format = git_text(repo, "rev-parse", "--show-object-format")
    need(object_format in {"sha1", "sha256"}, "UNSUPPORTED_GIT_OBJECT_FORMAT")
    previous, old_modes = previous_manifest(args.previous_public_manifest, args.unit)
    pointer_raw = args.prior_recovery_pointer.read_bytes()
    pointer = read_json(args.prior_recovery_pointer)
    need(isinstance(pointer, (dict, list)) and bool(pointer), "PRIOR_ARCHIVE_RECOVERY_POINTER_REQUIRED")
    scan_text("checkpoint/PRIOR_ARCHIVE_POINTER.json", pointer_raw)
    rows, excluded, snapshots, modes, total = [], [], {}, {}, 0
    current_receipt = f"{args.unit}/publication/{args.stage}_RECEIPT.json"
    for path in sorted(unit.rglob("*")):
        rel = path.relative_to(repo).as_posix()
        need(not path.is_symlink(), "SYMLINK_REJECTED:" + rel)
        if path.is_dir():
            continue
        need(stat.S_ISREG(path.stat().st_mode), "NONREGULAR_FILE_REJECTED:" + rel)
        relpath(rel)
        need(rel != current_receipt, "CURRENT_STAGE_RECEIPT_MUST_FOLLOW_ARCHIVE:" + rel)
        reason, identity = classify(path, rel), file_pin(path)
        if reason is None and identity["bytes"] > args.max_text_bytes:
            reason = "OVERSIZED_TEXT_DEFERRED_TO_SOURCE_RELEASE"
        if reason:
            need(rel not in indexed, "STAGED_BINARY_CACHE_OR_OVERSIZED_REJECTED:" + rel)
            row = {"path": rel, **identity, "checkpoint": "EXCLUDED", "reason": reason,
                   "source_release_obligation": reason not in {"DISPOSABLE_CACHE", "TEMPORARY_TASK_LEASE"}}
            excluded.append(row)
            rows.append(row)
            continue
        raw = path.read_bytes()
        need(pin(raw) == identity, "FILE_CHANGED_DURING_MANIFEST:" + rel)
        scan_text(rel, raw)
        need(rel in indexed, "TEXT_FILE_NOT_EXPLICITLY_INDEXED:" + rel)
        need(blob_oid(raw, object_format) == indexed[rel]["oid"], "INDEX_AND_WORKTREE_BYTES_DIFFER:" + rel)
        total += len(raw)
        need(total <= args.max_total_text_bytes, "TOTAL_TEXT_LIMIT_EXCEEDED")
        snapshots[rel], modes[rel] = raw, indexed[rel]["mode"]
        rows.append({"path": rel, **identity, "mode": modes[rel],
                     "git_index_oid": indexed[rel]["oid"], "checkpoint": "INCLUDED"})
    need(snapshots, "EMPTY_UNIT_TEXT_SNAPSHOT")
    need(set(indexed) == set(snapshots), "UNIT_INDEX_CONTAINS_MISSING_OR_UNSELECTED_FILES")
    current = {name: digest(raw) for name, raw in snapshots.items()}
    need(not (set(previous) & {r["path"] for r in excluded}), "PREVIOUS_PUBLIC_FILE_NOW_EXCLUDED_REQUIRES_EXPLICIT_REVIEW")
    deletions = sorted(set(previous) - set(current))
    for name in deletions:
        need(name not in indexed and not (repo / name).exists(), "PUBLIC_DELETION_NOT_EXPLICITLY_INDEXED:" + name)
    changed = sorted(n for n in current if previous.get(n) != current[n] or old_modes.get(n) != modes[n])
    need(changed or deletions, "NO_PUBLIC_CHANGE_FOR_STAGE")
    policies = policy_context(repo, args.unit)
    need(before == git_identity(repo), "LOCAL_GIT_OR_PARALLEL_STATE_CHANGED_DURING_PREPARATION")
    need(indexed == index_rows(repo, args.unit), "UNIT_INDEX_CHANGED_DURING_PREPARATION")
    payload = {
        "schema": "CR_CLOCK_GIT_TEXT_PAYLOAD_V1", "repository": REPOSITORY, "branch": args.branch,
        "stage": args.stage, "expected_parent": args.expected_parent, "force": False,
        "source_commit": None, "provider_ack": None,
        "files": [{"path": n, "mode": modes[n], "type": "blob", "encoding": "utf-8",
                   "content": snapshots[n].decode("utf-8"), "bytes": len(snapshots[n]), "sha256": current[n]} for n in changed],
        "delete_paths": deletions,
        "selection": "Only regular UTF-8 unit files matching the explicit Git index",
        "no_remote_write_performed": True,
    }
    manifest = {
        "schema": "CR_CLOCK_UNIT_FILE_MANIFEST_V1", "stage": args.stage, "unit": args.unit,
        "files": rows, "files_count": len(rows), "included_count": len(snapshots),
        "excluded_count": len(excluded), "all_regular_unit_files_manifested": True,
        "source_release_required_for_deferred_payloads": any(r["source_release_obligation"] for r in excluded),
    }
    generated = {
        "GIT_PAYLOAD.json": canonical(payload), "PUBLIC_MANIFEST.json": canonical(current),
        "UNIT_MANIFEST.json": canonical(manifest),
        "EXCLUSIONS.json": canonical({"files": excluded, "prior_archive_pointer": "PRIOR_ARCHIVE_POINTER.json"}),
        "PRIOR_ARCHIVE_POINTER.json": pointer_raw, "POLICY_CONTEXT.json": canonical(policies),
    }
    prepared = {
        "schema": "CR_CLOCK_PREPARED_STAGE_V1", "status": "FROZEN_LOCAL_PENDING_PUBLICATION",
        "stage": args.stage, "date": args.date, "repository": REPOSITORY, "branch": args.branch,
        "unit": args.unit, "repo_local_path": str(repo), "expected_parent": args.expected_parent,
        "source_commit": None, "created_utc": datetime.now(timezone.utc).isoformat(), "local_git": before,
        "caller_reported_central_count": args.central_count, "caller_reported_completed_stages": args.completed_stages,
        "stage_completion_inferred": False, "total_loop_stages": 20,
        "changed_text_files": len(changed), "deletion_count": len(deletions),
        "snapshot_text_files": len(snapshots), "snapshot_text_bytes": total, "excluded_files": len(excluded),
        "previous_public_manifest_pin": file_pin(args.previous_public_manifest) if args.previous_public_manifest else None,
        "metadata_pins": {name: pin(raw) for name, raw in generated.items()},
        "builder_sha256": file_pin(Path(__file__).resolve())["sha256"],
        "publication": {"git": "PENDING", "library": "PENDING", "dropbox": "PENDING", "drive": "PENDING"},
        "remote_writes": 0, "scientific_replays": 0,
        "current_receipt_rule": "Write actual stage receipt after archive/remote responses; include it in the next stage.",
    }
    output.mkdir(parents=True, exist_ok=False)
    for name, raw in snapshots.items():
        write_new(output / "snapshot" / name, raw)
    for name, raw in generated.items():
        write_new(output / name, raw)
    write_new(output / "PREPARED.json", canonical(prepared))
    print(json.dumps({
        "status": prepared["status"], "stage": args.stage, "directory": str(output),
        "payload": str(output / "GIT_PAYLOAD.json"), "public_manifest": str(output / "PUBLIC_MANIFEST.json"),
        "changed_text_files": len(changed), "deletion_count": len(deletions),
        "snapshot_text_files": len(snapshots), "excluded_files": len(excluded),
        "mechanical_wall_s": time.monotonic() - started, "remote_writes": 0,
    }))
    return 0


def root_git_receipt(path, prepared, commit):
    if path is None:
        return None
    raw, receipt = path.read_bytes(), read_json(path)
    need(isinstance(receipt, dict), "ACTUAL_ROOT_GIT_RECEIPT_OBJECT_REQUIRED")
    g = receipt.get("git", receipt)
    need(isinstance(g, dict), "GIT_RECEIPT_OBJECT_REQUIRED")
    need(g.get("repository") == prepared["repository"] and g.get("branch") == prepared["branch"]
         and g.get("commit") == commit and g.get("expected_parent") == prepared["expected_parent"]
         and g.get("force") is False and g.get("provider_ack") is True
         and (g.get("ls_remote_equal") is True or g.get("observed_head") == commit),
         "ACTUAL_GIT_ACK_PARENT_REF_BINDING_REQUIRED")
    need(g.get("payload_sha256") == prepared["metadata_pins"]["GIT_PAYLOAD.json"]["sha256"]
         and g.get("public_manifest_sha256") == prepared["metadata_pins"]["PUBLIC_MANIFEST.json"]["sha256"],
         "ROOT_GIT_RECEIPT_MUST_BIND_EXACT_PREPARED_PAYLOAD_AND_MANIFEST")
    return {"receipt_sha256": digest(raw), "receipt_bytes": len(raw),
            "provider_ack": True, "expected_and_observed_ref_equal": True,
            "payload_sha256": g["payload_sha256"], "public_manifest_sha256": g["public_manifest_sha256"],
            "readback_tier": g.get("readback_tier", g.get("tier", "R1")),
            "source": "ACTUAL_ROOT_RECEIPT_INPUT", "receipt_not_embedded_in_current_archive": True}


def local_commit_binding(repo, prepared, commit, current, expected_modes):
    found, _ = git(repo, "cat-file", "-e", commit + "^{commit}", required=False)
    if found != 0:
        return {"commit_object_locally_present": False}
    parents = git_text(repo, "rev-list", "--parents", "-n", "1", commit).split()
    need(parents == [commit, prepared["expected_parent"]], "LOCAL_COMMIT_PARENT_MISMATCH")
    tree_rows = {}
    for token in git(repo, "ls-tree", "-r", "-z", commit, "--", prepared["unit"])[1].split(b"\0"):
        if not token:
            continue
        fields, name = token.split(b"\t", 1)
        mode, kind, oid = fields.decode("ascii").split()
        rel = relpath(name.decode("utf-8"))
        need(kind == "blob" and mode in {"100644", "100755"}, "COMMIT_NONREGULAR_UNIT_PATH:" + rel)
        tree_rows[rel] = {"oid": oid, "mode": mode}
    need(set(tree_rows) == set(current), "LOCAL_COMMIT_UNIT_MEMBERSHIP_MISMATCH")
    for name, row in tree_rows.items():
        raw = git(repo, "cat-file", "blob", row["oid"])[1]
        need(digest(raw) == current[name] and row["mode"] == expected_modes[name],
             "LOCAL_COMMIT_UNIT_BYTES_OR_MODE_MISMATCH:" + name)
    changed_raw = git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z",
                      prepared["expected_parent"], commit)[1]
    changed = [p.decode("utf-8") for p in changed_raw.split(b"\0") if p]
    need(all(p.startswith(prepared["unit"] + "/") for p in changed), "LOCAL_COMMIT_ALSO_CHANGED_OUTSIDE_SELECTED_UNIT")
    return {"commit_object_locally_present": True, "parent_exact_match": True,
            "unit_entry_bytes_and_modes_match": True, "commit_changes_selected_unit_only": True,
            "tree": git_text(repo, "rev-parse", commit + "^{tree}")}


def archive_hashes(path):
    sha, md5, outer, size = hashlib.sha256(), hashlib.md5(usedforsecurity=False), hashlib.sha256(), 0
    with path.open("rb") as stream:
        while block := stream.read(4 * 1024 * 1024):
            size += len(block)
            sha.update(block)
            md5.update(block)
            outer.update(hashlib.sha256(block).digest())
    return {"bytes": size, "sha256": sha.hexdigest(), "md5": md5.hexdigest(), "dropbox_content_hash": outer.hexdigest()}


def seal(args):
    started_wall, started_cpu = time.monotonic(), time.process_time()
    source = args.prepared.resolve()
    prepared_raw, prepared = (source / "PREPARED.json").read_bytes(), read_json(source / "PREPARED.json")
    need(prepared.get("schema") == "CR_CLOCK_PREPARED_STAGE_V1", "PREPARED_SCHEMA")
    need(prepared["stage"] in STAGES and SHA40.fullmatch(args.source_commit), "STAGE_AND_FULL_ACTUAL_SOURCE_COMMIT_REQUIRED")
    repo = Path(prepared["repo_local_path"]).resolve()
    output = args.output.resolve() if args.output else source / "sealed"
    assert_new_outside(repo, output)
    need(prepared["builder_sha256"] == file_pin(Path(__file__).resolve())["sha256"], "PACKAGER_CHANGED_AFTER_PAYLOAD_PREPARATION")
    generated = {}
    for name, expected in prepared["metadata_pins"].items():
        relpath(name)
        raw = (source / name).read_bytes()
        need(pin(raw) == expected, "PREPARED_METADATA_CHANGED:" + name)
        generated[name] = raw
    current, manifest = read_json(source / "PUBLIC_MANIFEST.json"), read_json(source / "UNIT_MANIFEST.json")
    modes = {r["path"]: r["mode"] for r in manifest["files"] if r["checkpoint"] == "INCLUDED"}
    payloads = {}
    for name, sha in sorted(current.items()):
        relpath(name)
        need(name.startswith(prepared["unit"] + "/"), "SNAPSHOT_PATH_OUTSIDE_UNIT")
        path = source / "snapshot" / name
        need(path.is_file() and not path.is_symlink(), "SNAPSHOT_REGULAR_FILE_REQUIRED")
        raw = path.read_bytes()
        need(digest(raw) == sha, "FROZEN_SNAPSHOT_HASH_CHANGED:" + name)
        scan_text(name, raw)
        payloads[name] = (raw, modes[name], "FROZEN_UNIT_TEXT")
    receipt = root_git_receipt(args.git_receipt, prepared, args.source_commit)
    local = local_commit_binding(repo, prepared, args.source_commit, current, modes)
    need(local["commit_object_locally_present"] or receipt is not None, "ACTUAL_COMMIT_OBJECT_OR_ROOT_ACK_RECEIPT_REQUIRED")
    need(policy_context(repo, prepared["unit"]) == read_json(source / "POLICY_CONTEXT.json"),
         "POLICY_BYTES_CHANGED_SINCE_STAGE_PREPARATION")
    for name in ("UNIT_MANIFEST.json", "PUBLIC_MANIFEST.json", "EXCLUSIONS.json", "PRIOR_ARCHIVE_POINTER.json", "POLICY_CONTEXT.json"):
        payloads["checkpoint/" + name] = (generated[name], "100644", "CHECKPOINT_METADATA")
    payloads["checkpoint/PREPARED.json"] = (prepared_raw, "100644", "PREPUBLICATION_PREPARATION_STATE")
    authority = {
        "schema": "CR_CLOCK_CHECKPOINT_AUTHORITY_V1", "repository": prepared["repository"],
        "branch": prepared["branch"], "stage": prepared["stage"], "commit": args.source_commit,
        "expected_parent": prepared["expected_parent"], "force": False,
        "frozen_snapshot_prepared_utc": prepared["created_utc"], "prepared_sha256": digest(prepared_raw),
        "payload_sha256": prepared["metadata_pins"]["GIT_PAYLOAD.json"]["sha256"],
        "caller_reported_central_count": prepared["caller_reported_central_count"],
        "caller_reported_completed_stages": prepared["caller_reported_completed_stages"],
        "stage_completion_inferred": False, "local_commit_binding": local, "root_git_receipt_binding": receipt,
        "git_publication_status": "ROOT_RECEIPT_BOUND" if receipt else "REMOTE_PENDING_LOCAL_COMMIT_ONLY",
        "backup_status": {"library": "PENDING", "dropbox": "PENDING", "drive": "PENDING"},
        "current_provider_receipt_embedded": False, "remote_writes_by_packager": 0,
        "scientific_replays": 0, "scientific_validity": "NOT_INFERRED_BY_PACKAGER",
        "historical_UNKNOWN_NO_ACK_rewritten": False,
        "self_reference_rule": "Authority has no archive hash; MANIFEST excludes itself; actual transport receipt belongs to the next stage.",
    }
    payloads["CHECKPOINT_AUTHORITY.json"] = (canonical(authority), "100644", "ACTUAL_COMMIT_BOUND_AUTHORITY")
    rows = [{"path": n, **pin(raw), "mode": mode, "role": role} for n, (raw, mode, role) in sorted(payloads.items())]
    zip_manifest = {
        "schema": "CR_CLOCK_CHECKPOINT_MANIFEST_V1", "stage": prepared["stage"], "commit": args.source_commit,
        "files": rows, "files_count": len(rows), "manifest_excludes_own_hash": True,
        "excluded_payload_manifest": "checkpoint/EXCLUSIONS.json",
        "prior_archive_pointer": "checkpoint/PRIOR_ARCHIVE_POINTER.json",
        "source_release_still_required_for_dense_or_oversized_payloads": True,
        "remote_verification_claimed_by_packager": False,
    }
    manifest_raw = canonical(zip_manifest)
    payloads["MANIFEST.json"] = (manifest_raw, "100644", "SELF_EXCLUDING_MANIFEST")
    date = datetime.strptime(prepared["date"], "%Y%m%d")
    output.mkdir(parents=True, exist_ok=False)
    name = f"BASS_CR_CLOCK_{prepared['stage']}_{prepared['date']}_{args.source_commit[:12]}.zip"
    archive_path = output / name
    try:
        with zipfile.ZipFile(archive_path, "x", zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
            for path, (raw, mode, _) in sorted(payloads.items()):
                info = zipfile.ZipInfo(path, (date.year, date.month, date.day, 0, 0, 0))
                info.create_system, info.external_attr = 3, (int(mode, 8) & 0xFFFF) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, raw, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
        verified = []
        with zipfile.ZipFile(archive_path) as archive:
            infos = archive.infolist()
            need(len(infos) == len(payloads) and {i.filename for i in infos} == set(payloads), "ARCHIVE_ENTRY_SET_MISMATCH")
            for info in infos:
                raw, expected = archive.read(info.filename), payloads[info.filename][0]
                crc = zlib.crc32(raw) & 0xFFFFFFFF
                need(pin(raw) == pin(expected) and crc == info.CRC, "ARCHIVE_RAW_HASH_OR_CRC_FAILURE:" + info.filename)
                verified.append({"path": info.filename, **pin(raw), "CRC32": f"{crc:08x}"})
        result = {
            "schema": "CR_CLOCK_LOCAL_STAGE_BUILD_RESULT_V1", "status": "LOCAL_ALL_ENTRY_RAW_HASH_CRC_PASS",
            "stage": prepared["stage"], "source_commit": args.source_commit,
            "archive": {"path": str(archive_path), "name": name, **archive_hashes(archive_path)},
            "manifest": pin(manifest_raw), "archive_entries": len(verified), "all_entry_verification": verified,
            "git_binding": {"local": local, "root_receipt": receipt},
            "publication": {
                "git": "ROOT_RECEIPT_BOUND" if receipt else "REMOTE_PENDING",
                "library": {"status": "NOT_ATTEMPTED_BY_PACKAGER", "ack": None, "tier": None},
                "dropbox": {"status": "NOT_ATTEMPTED_BY_PACKAGER", "ack": None, "tier": None},
                "drive": {"status": "NOT_ATTEMPTED_BY_PACKAGER", "ack": None, "tier": None},
                "dual_backup": "PENDING",
            },
            "actual_provider_receipts": "ROOT_OWNED; carry combined receipt into next stage",
            "observed_local_git_at_seal": git_identity(repo),
            "mechanical_cpu_s": time.process_time() - started_cpu, "mechanical_wall_s": time.monotonic() - started_wall,
            "scientific_replays": 0, "remote_writes": 0, "remote_R3_claimed": False,
        }
        write_new(output / "CHECKPOINT_AUTHORITY.json", canonical(authority))
        write_new(output / "MANIFEST.json", manifest_raw)
        write_new(output / "BUILD_RESULT.json", canonical(result))
        print(json.dumps({k: result[k] for k in ("status", "stage", "source_commit", "archive", "archive_entries")}))
        return 0
    except Exception as error:
        write_new(output / "FAILED_RETAINED.json", canonical({
            "status": "FAILED_RETAINED", "error_type": type(error).__name__, "message": str(error),
            "partial_artifacts_deleted": False, "scientific_replays": 0, "remote_writes": 0,
        }))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    p = commands.add_parser("payload", help="Freeze explicitly indexed unit text and prepare Git payload")
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--unit", default=DEFAULT_UNIT)
    p.add_argument("--branch", default=DEFAULT_BRANCH)
    p.add_argument("--stage", choices=STAGES, required=True)
    p.add_argument("--expected-parent", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--previous-public-manifest", type=Path)
    p.add_argument("--prior-recovery-pointer", type=Path, default=Path(__file__).with_name("PRIOR_ARCHIVE_POINTER.json"))
    p.add_argument("--date", default="20261027")
    p.add_argument("--central-count")
    p.add_argument("--completed-stages", type=int)
    p.add_argument("--max-text-bytes", type=int, default=1024 * 1024)
    p.add_argument("--max-total-text-bytes", type=int, default=16 * 1024 * 1024)
    p.set_defaults(func=prepare)
    z = commands.add_parser("zip", help="Bind frozen payload to actual commit and build immutable ZIP")
    z.add_argument("--prepared", type=Path, required=True)
    z.add_argument("--source-commit", required=True)
    z.add_argument("--git-receipt", type=Path)
    z.add_argument("--output", type=Path)
    z.set_defaults(func=seal)
    args = parser.parse_args()
    try:
        return args.func(args)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "REFUSED", "type": type(error).__name__, "message": str(error),
                          "remote_writes": 0, "scientific_replays": 0}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

