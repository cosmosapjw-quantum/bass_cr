#!/usr/bin/env python3
"""Create-only packaging and explicit R3 for CR_PHYS02_PARENT_EVENT_NATIVE25_V1.

Standard library only. No scientific imports, Git writes, uploads, automatic
fetch, retries, cleanup, Library operations, or successor-unit work. Network
reads occur ONLY in the explicit provider-r3 and git-r3 subcommands.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import urllib.parse
import urllib.request
import zipfile
import zlib


UNIT = "CR_PHYS02_PARENT_EVENT_NATIVE25_V1"
UNIT_PATH = "research/cr_parent_event_native25_20261028"
REPOSITORY = "cosmosapjw-quantum/bass_cr"
BRANCH = "research/cr-parent-event-native25-20261028"
INPUT_PATH = UNIT_PATH + "/inputs/INPUT_MANIFEST.json"
INPUT_SHA = "2273f08ac1716d233097d17c73818d39a9337da34712290a4b4171430d24f9b3"
CONTRACT_SHA = "01cc2d2835e3ad61c49cd0b68b8c413ebd7e0b8fb5228877804159c4e3f71162"
MANIFEST = "MANIFEST.json"
CHUNK = 1024 * 1024
STAGES = [f"{prefix}{n:02}" for prefix in ("R", "C") for n in range(1, 11)]
CACHE_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
               "mplcache", ".matplotlib", ".cache", ".git"}
PRIVATE_NAME = re.compile(
    r"(?:^|[_.-])(?:private|raw_private|signed_urls?|presigned_urls?)(?:[_.-]|$)", re.I)
PRIVATE_BYTES = re.compile(
    rb'"(?:download_url|signed_url|presigned_url)"\s*:\s*"https?://'
    rb'|(?:x-amz-signature|x-goog-signature|awsaccesskeyid)='
    rb'|https?://[^\s"<>]{0,4096}[?&](?:sig|signature|access_token)=', re.I)


class Refusal(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def hex_value(value, length):
    need(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{" + str(length) + r"}", value),
         "INVALID_HEX_IDENTITY")
    return value


def integer(value):
    need(type(value) is int and value >= 0, "NONNEGATIVE_INTEGER_REQUIRED")
    return value


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def decode(raw):
    def invalid_constant(_):
        raise Refusal("NONFINITE_JSON_NUMBER")
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=invalid_constant)


def private_name(path):
    return any(PRIVATE_NAME.search(part) for part in Path(path).parts)


def public_bytes(raw):
    if PRIVATE_BYTES.search(raw) is None:
        return

    def immutable_contents_record(value):
        # A public contents-API record is source evidence, not a signed link.
        # Require its path/revision/blob endpoints to agree; no arbitrary URL
        # or other download_url-shaped object receives this narrow exception.
        if not isinstance(value, dict) or value.get("type") != "file":
            return False
        url, path, blob = (value.get(k) for k in ("download_url", "path", "sha"))
        if not all(isinstance(v, str) for v in (url, path, blob)):
            return False
        parsed = urllib.parse.urlsplit(url)
        parts = parsed.path.split("/", 4)
        if (parsed.scheme != "https" or parsed.netloc != "raw.githubusercontent.com"
                or parsed.query or parsed.fragment or len(parts) != 5
                or parts[1] != "cosmosapjw-quantum"
                or re.fullmatch(r"[A-Za-z0-9_.-]+", parts[2]) is None
                or re.fullmatch(r"[0-9a-f]{40}", parts[3]) is None
                or re.fullmatch(r"[0-9a-f]{40}", blob) is None):
            return False
        repo, revision = parts[2:4]
        if (not path or urllib.parse.unquote(parts[4]) != path
                or any(p in ("", ".", "..") for p in path.split("/"))
                or "\\" in path or any(ord(c) < 32 or ord(c) == 127 for c in path)
                or value.get("name") != path.rsplit("/", 1)[-1]
                or type(value.get("size")) is not int or value["size"] < 0):
            return False
        api_url = value.get("url")
        if not isinstance(api_url, str):
            return False
        api = urllib.parse.urlsplit(api_url)
        return (api.scheme == "https" and api.netloc == "api.github.com"
                and urllib.parse.unquote(api.path)
                == f"/repos/cosmosapjw-quantum/{repo}/contents/{path}"
                and api.query == "ref=" + revision and not api.fragment
                and value.get("git_url")
                == f"https://api.github.com/repos/cosmosapjw-quantum/{repo}/git/blobs/{blob}")

    def inspection_copy(value):
        if isinstance(value, list):
            return [inspection_copy(v) for v in value]
        if isinstance(value, dict):
            allowed = immutable_contents_record(value)
            return {k: None if k == "download_url" and allowed else inspection_copy(v)
                    for k, v in value.items()}
        return value

    try:
        inspected = encode(inspection_copy(decode(raw)))
    except (ValueError, TypeError, UnicodeError):
        raise Refusal("SIGNED_TRANSPORT_CONTENT_REFUSED") from None
    # Inspection uses a temporary copy only; callers retain the exact original
    # raw bytes. Signed URL keys and token/signature patterns remain forbidden.
    need(PRIVATE_BYTES.search(inspected) is None, "SIGNED_TRANSPORT_CONTENT_REFUSED")


def safe_name(name):
    need(isinstance(name, str) and name and "\\" not in name,
         "SAFE_RELATIVE_ARCHIVE_NAME_REQUIRED")
    need(not PurePosixPath(name).is_absolute()
         and not any(ord(c) < 32 or ord(c) == 127 for c in name), "UNSAFE_ARCHIVE_NAME")
    parts = name.split("/")
    need(all(p not in ("", ".", "..") and ":" not in p for p in parts),
         "UNSAFE_ARCHIVE_NAME")
    need(parts[0].casefold() != MANIFEST.casefold(), "MANIFEST_NAME_RESERVED")
    need(not private_name(name), "PRIVATE_TRANSPORT_NAME_REFUSED")
    return name


def unique_names(names):
    seen, parents = set(), set()
    for name in names:
        key = safe_name(name).casefold()
        ancestors = {"/".join(key.split("/")[:i]) for i in range(1, len(key.split("/")))}
        need(key not in seen and key not in parents and not ancestors.intersection(seen),
             "DUPLICATE_CASEFOLD_OR_PREFIX_PATH")
        seen.add(key)
        parents.update(ancestors)


def absolute(path):
    path = Path(path)
    need(path.is_absolute(), "ABSOLUTE_LOCAL_PATH_REQUIRED")
    need(".." not in path.parts and not any(p.is_symlink() for p in (path, *path.parents)),
         "SYMLINK_OR_PARENT_TRAVERSAL_REFUSED")
    return path


def snapshot(path):
    path = absolute(path)
    value = path.lstat()
    need(stat.S_ISREG(value.st_mode), "REGULAR_NON_SYMLINK_SOURCE_REQUIRED")
    return [value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns]


def file_bytes(path, *, sensitive=False, expected_snapshot=None, inspect_contents=True):
    path = absolute(path)
    need(sensitive or not private_name(path), "PRIVATE_TRANSPORT_FILE_REFUSED")
    before = snapshot(path)
    if expected_snapshot is not None:
        need(before == expected_snapshot, "SOURCE_SNAPSHOT_CHANGED")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, "rb") as handle:
        info = os.fstat(handle.fileno())
        need([info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns] == before,
             "SOURCE_CHANGED_BEFORE_READ")
        raw = handle.read()
        info = os.fstat(handle.fileno())
        need([info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns] == before
             and snapshot(path) == before and len(raw) == before[2], "SOURCE_CHANGED_DURING_READ")
    if not sensitive and inspect_contents:
        public_bytes(raw)
    return raw, before


def file_pin(path, *, sensitive=False):
    raw, _ = file_bytes(path, sensitive=sensitive)
    return {"path": str(absolute(path)), "bytes": len(raw), "sha256": sha(raw)}


def read_json(path, *, sensitive=False):
    raw, _ = file_bytes(path, sensitive=sensitive)
    return decode(raw)


def pinned_bytes(pin, *, sensitive=False):
    need(isinstance(pin, dict) and set(pin) == {"path", "bytes", "sha256"}, "EXACT_FILE_PIN_REQUIRED")
    raw, _ = file_bytes(pin["path"], sensitive=sensitive)
    need(len(raw) == integer(pin["bytes"]) and sha(raw) == hex_value(pin["sha256"], 64),
         "ACTUAL_FILE_PIN_MISMATCH")
    return raw


def write_new(path, raw):
    path = absolute(path)
    with path.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def write_json(path, value):
    write_new(path, encode(value))


def git(repo, *args):
    # Read-only local object operations only; never fetch missing objects.
    result = subprocess.run(["git", "-C", str(absolute(repo)), *args],
                            capture_output=True, check=False,
                            env={**os.environ, "GIT_NO_LAZY_FETCH": "1"})
    need(result.returncode == 0, "LOCAL_GIT_OBJECT_UNAVAILABLE_OR_READ_FAILED")
    return result.stdout


def tree_rows(repo, commit, prefix=None):
    args = ["ls-tree", "-r", "-z", hex_value(commit, 40)]
    if prefix:
        args.extend(["--", prefix])
    rows = {}
    for record in git(repo, *args).split(b"\0"):
        if not record:
            continue
        header, raw_path = record.split(b"\t", 1)
        mode, kind, blob = header.decode().split()
        path = raw_path.decode("utf-8")
        if prefix:
            need(mode in ("100644", "100755") and kind == "blob", "NONREGULAR_GIT_UNIT_OBJECT")
        rows[path] = {"mode": mode, "type": kind, "blob": blob}
    return rows


def git_bytes(repo, row):
    need(row["mode"] in ("100644", "100755") and row["type"] == "blob", "REGULAR_GIT_BLOB_REQUIRED")
    raw = git(repo, "cat-file", "blob", hex_value(row["blob"], 40))
    need(git_blob(raw) == row["blob"], "GIT_BLOB_IDENTITY_MISMATCH")
    public_bytes(raw)
    return raw


def check_stage(row, stage, ordinal):
    need(row.get("schema") == "CR_PARENT_EVENT_STAGE_PUBLICATION_V1"
         and row.get("stage") == stage and row.get("force") is False
         and row.get("Git_ref_readback") is True
         and row.get("completed_loop_stage") == ordinal
         and row.get("total_loop_stages") == 20, "ACTUAL_STAGE_RECEIPT_REQUIRED")
    for key in ("commit", "tree", "expected_parent"):
        hex_value(row[key], 40)
    archive = row["archive"]
    hex_value(archive["sha256"], 64)
    size = integer(archive["bytes"])
    for provider in ("Dropbox", "Drive"):
        item = row[provider]
        need(item.get("ack") is True and item.get("tier") in ("R2", "R3")
             and isinstance(item.get("id"), str) and item["id"]
             and item.get("bytes") == size, "DUAL_STAGE_R2_RECEIPT_REQUIRED")
        need(int(item["metadata"]["size"]) == size and item["metadata"]["id"] == item["id"],
             "STAGE_PROVIDER_METADATA_ID_OR_SIZE_MISMATCH")


def check_state(state, count, head):
    need(state.get("repo") == REPOSITORY and state.get("branch") == BRANCH
         and state.get("head") == head, "CURRENT_UNIT_PUBLICATION_STATE_MISMATCH")
    rows = state["stages"]
    need([r.get("stage") for r in rows] == STAGES[:count], "EXACT_ACTUAL_STAGE_SEQUENCE_REQUIRED")
    for i, row in enumerate(rows, 1):
        check_stage(row, STAGES[i - 1], i)
        if i > 1:
            need(row["expected_parent"] == rows[i - 2]["commit"], "STAGE_PARENT_CHAIN_MISMATCH")
    need(rows[-1]["commit"] == head and state["tree"] == rows[-1]["tree"], "STAGE_HEAD_TREE_MISMATCH")
    return rows


def inventory(repo):
    base = absolute(repo) / UNIT_PATH
    need(base.is_dir() and not base.is_symlink(), "CURRENT_UNIT_DIRECTORY_REQUIRED")
    included, excluded = [], []
    for directory, dirs, files in os.walk(base, followlinks=False):
        directory = Path(directory)
        kept = []
        for name in sorted(dirs):
            child = directory / name
            rel = child.relative_to(repo).as_posix()
            need(not child.is_symlink(), "UNIT_DIRECTORY_SYMLINK_REFUSED")
            if name in CACHE_PARTS or private_name(name):
                excluded.append({"path": rel + "/", "reason": "CACHE_OR_PRIVATE_DIRECTORY"})
            else:
                kept.append(name)
        dirs[:] = kept
        for name in sorted(files):
            child = directory / name
            rel = child.relative_to(repo).as_posix()
            if private_name(name) or name.endswith((".pyc", ".pyo")):
                excluded.append({"path": rel, "reason": "CACHE_OR_PRIVATE_FILE"})
                continue
            snapshot(child)
            included.append(safe_name(rel))
    return sorted(included), sorted(excluded, key=lambda r: r["path"])


def source_identity(S):
    return {"unit": UNIT, "unit_path": UNIT_PATH, "repository": REPOSITORY,
            "S": hex_value(S, 40), "D": None, "M": None,
            "actual_published_loop_stages": 19, "total_loop_stages": 20,
            "source_input_payloads": 17, "scientific_execution_by_packager": False,
            "old_science_replays": 0, "metadata_CPU_s": None,
            "global_physical_completion": None, "global_error": None,
            "global_budget_remaining": None, "currency": None,
            "future_SOURCE_self_hash_or_provider_ids": None}


def local_row(path, name, all_git, repo):
    raw, snap = file_bytes(path)
    entry = all_git.get(name)
    published = bool(entry and entry["type"] == "blob"
                     and entry["mode"] in ("100644", "100755")
                     and git_blob(raw) == entry["blob"])
    return {"path": safe_name(name), "bytes": len(raw), "sha256": sha(raw),
            "crc32": f"{zlib.crc32(raw) & 0xffffffff:08x}",
            "publication_class": "git_published_at_S" if published else "archive_only",
            "git_blob_sha1_at_S": entry["blob"] if published else None,
            "git_path_present_at_S": bool(entry),
            "origin": {"kind": "local", "local_path": str(absolute(path)), "snapshot": snap}}


def source_plan(args):
    repo, S = absolute(args.repo_root), hex_value(args.S, 40)
    need(git(repo, "rev-parse", "HEAD").decode().strip() == S, "SOURCE_REQUIRES_CURRENT_LOCAL_HEAD_S")
    state = read_json(args.state)
    stages = check_state(state, 19, S)
    c09 = read_json(args.c09_receipt)
    need(c09 == stages[-1], "C09_RECEIPT_NOT_IDENTICAL_TO_ACTUAL_STATE")
    need(git(repo, "rev-parse", S + "^{tree}").decode().strip() == c09["tree"], "S_TREE_MISMATCH")
    unit_tree = tree_rows(repo, S, UNIT_PATH + "/")
    all_git = tree_rows(repo, S)
    need(unit_tree, "NO_PUBLISHED_CURRENT_UNIT_FILES_AT_S")
    published = read_json(args.published_paths)
    need(isinstance(published, list) and published and len(published) == len(set(published)),
         "UNIQUE_PUBLISHED_PATHS_LIST_REQUIRED")
    unique_names(published)
    selected = set(unit_tree) | set(published)
    rows = {}
    for name in sorted(selected):
        safe_name(name)
        need(not any(p in CACHE_PARTS for p in name.split("/")), "PUBLISHED_CACHE_PATH_REFUSED")
        need(name in all_git, "DECLARED_PUBLISHED_PATH_ABSENT_AT_S")
        raw = git_bytes(repo, all_git[name])
        local = repo / name
        if local.exists() or local.is_symlink():
            local_raw, _ = file_bytes(local)
            need(local_raw == raw, "PUBLISHED_LOCAL_BYTES_CHANGED_SINCE_S")
        rows[name] = {"path": name, "bytes": len(raw), "sha256": sha(raw),
                      "crc32": f"{zlib.crc32(raw) & 0xffffffff:08x}",
                      "publication_class": "git_published_at_S",
                      "git_blob_sha1_at_S": all_git[name]["blob"], "git_path_present_at_S": True,
                      "origin": {"kind": "git", **all_git[name]}}
    names, excluded = inventory(repo)
    for name in names:
        if name not in rows:
            rows[name] = local_row(repo / name, name, all_git, repo)
    need(INPUT_PATH in rows and rows[INPUT_PATH]["sha256"] == INPUT_SHA, "FROZEN_17_INPUT_MANIFEST_MISMATCH")
    contract = rows.get(UNIT_PATH + "/CONTRACT.json", {})
    need(contract.get("sha256") == CONTRACT_SHA, "FROZEN_CONTRACT_MISMATCH")
    inputs = decode(git_bytes(repo, all_git[INPUT_PATH]))["files"]
    need(len(inputs) == 17 and len({i["path"] for i in inputs}) == 17, "EXACT_17_SOURCE_PAYLOADS_REQUIRED")
    for item in inputs:
        name = safe_name(item["path"])
        if name not in rows:
            rows[name] = local_row(repo / name, name, all_git, repo)
        need(rows[name]["bytes"] == integer(item["bytes"])
             and rows[name]["sha256"] == hex_value(item["sha256"], 64), "SOURCE_PAYLOAD_PIN_MISMATCH")
        rows[name]["frozen_source_payload"] = True
    extras = read_json(args.extras) if args.extras else []
    need(isinstance(extras, list), "EXPLICIT_EXTRAS_LIST_REQUIRED")
    extras = extras + [
        {"local_path": str(absolute(args.state)), "archive_path": "release_metadata/PUBLICATION_STATE_AT_S.json"},
        {"local_path": str(Path(__file__).absolute()), "archive_path": "release_ops/release_parent.py"},
    ]
    for extra in extras:
        need(set(extra) == {"local_path", "archive_path"}, "EXACT_EXTRA_KEYS_REQUIRED")
        name = safe_name(extra["archive_path"])
        need(name not in rows, "EXTRA_ARCHIVE_PATH_COLLISION")
        rows[name] = local_row(absolute(extra["local_path"]), name, all_git, repo)
    unique_names(rows)
    # A post-plan failure/debit or new run must invalidate the plan, not disappear.
    need(inventory(repo) == (names, excluded), "UNIT_INVENTORY_CHANGED_DURING_PLAN")
    controls = {key: file_pin(getattr(args, key)) for key in ("state", "c09_receipt", "published_paths")}
    if args.extras:
        controls["extras"] = file_pin(args.extras)
    result = {"schema": "CR_PARENT_EVENT_SOURCE_PLAN_V1", "identity": source_identity(S),
              "repo_root": str(repo), "S_tree": c09["tree"], "created_utc": now(),
              "controls": controls, "input_manifest_sha256": INPUT_SHA,
              "unit_local_inventory": names, "excluded_paths": excluded,
              "files": [rows[k] for k in sorted(rows)],
              "published_current_unit_paths": sorted(unit_tree),
              "source_payload_paths": [r["path"] for r in inputs],
              "later_D_M_and_closeout_receipts_belong_to_separate_archive": True}
    output = args.attempt_dir / "SOURCE_PLAN.json"
    write_json(output, result)
    return {"plan": file_pin(output), "payloads": len(rows), "S": S, "archive_created": False}


def planned_raw(row, repo=None):
    origin = row["origin"]
    if origin["kind"] == "git":
        need(repo is not None, "GIT_REPO_REQUIRED")
        raw = git_bytes(repo, origin)
    else:
        need(origin["kind"] == "local", "UNKNOWN_PAYLOAD_ORIGIN")
        raw, _ = file_bytes(origin["local_path"], expected_snapshot=origin["snapshot"])
    need(len(raw) == integer(row["bytes"]) and sha(raw) == hex_value(row["sha256"], 64)
         and f"{zlib.crc32(raw) & 0xffffffff:08x}" == row["crc32"], "PLANNED_PAYLOAD_CHANGED")
    return raw


def zip_info(name):
    item = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    item.create_system = 3
    item.external_attr = (stat.S_IFREG | 0o644) << 16
    item.compress_type = zipfile.ZIP_DEFLATED
    return item


def archive_metadata(path):
    # The compressed container is not text. Its manifest and each decompressed
    # payload are inspected separately below; private filenames still fail here.
    raw, _ = file_bytes(path, inspect_contents=False)
    return {"path": str(absolute(path)), "name": path.name, "bytes": len(raw), "sha256": sha(raw)}


def verify_zip(path, expected=None):
    before = snapshot(path)
    meta = archive_metadata(path)
    need(snapshot(path) == before, "ARCHIVE_CHANGED_BEFORE_MEMBER_VERIFICATION")
    if expected:
        for key in ("name", "bytes", "sha256"):
            need(meta[key] == expected[key], "ARCHIVE_IDENTITY_MISMATCH")
    with zipfile.ZipFile(path, "r") as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) and MANIFEST in names, "INVALID_ZIP_MEMBERSHIP")
        need(archive.testzip() is None, "ZIP_CRC_TEST_FAILED")
        manifest_raw = archive.read(MANIFEST)
        public_bytes(manifest_raw)
        manifest = decode(manifest_raw)
        rows = manifest["files"]
        need(isinstance(rows, list) and rows, "MANIFEST_PAYLOAD_ROWS_REQUIRED")
        unique_names([r["path"] for r in rows])
        need(names == [r["path"] for r in rows] + [MANIFEST], "EXACT_ORDERED_MANIFEST_MEMBERSHIP_REQUIRED")
        need((zlib.crc32(manifest_raw) & 0xffffffff) == archive.getinfo(MANIFEST).CRC, "MANIFEST_CRC_FAILED")
        for row in rows:
            info = archive.getinfo(row["path"])
            need(not info.is_dir() and stat.S_IFMT(info.external_attr >> 16) == stat.S_IFREG,
                 "REGULAR_ZIP_PAYLOAD_REQUIRED")
            digest, crc, size = hashlib.sha256(), 0, 0
            overlap = b""
            with archive.open(info) as stream:
                for chunk in iter(lambda: stream.read(CHUNK), b""):
                    public_bytes(overlap + chunk)
                    overlap = (overlap + chunk)[-8192:]
                    digest.update(chunk)
                    crc = zlib.crc32(chunk, crc)
                    size += len(chunk)
            need(size == integer(row["bytes"]) == info.file_size
                 and digest.hexdigest() == hex_value(row["sha256"], 64)
                 and (crc & 0xffffffff) == info.CRC
                 and row.get("crc32", f"{info.CRC:08x}") == f"{info.CRC:08x}", "PAYLOAD_HASH_BYTES_OR_CRC_FAILED")
    meta.update(members=len(rows) + 1, payloads=len(rows), manifest_sha256=sha(manifest_raw))
    need(snapshot(path) == before, "ARCHIVE_CHANGED_DURING_MEMBER_VERIFICATION")
    if expected:
        for key in ("members", "payloads", "manifest_sha256"):
            need(meta[key] == expected[key], "ARCHIVE_MEMBER_OR_MANIFEST_PIN_MISMATCH")
    return meta, manifest


def package(args, name, manifest, rows, repo=None, recheck=None):
    unique_names([r["path"] for r in rows])
    need(name == Path(name).name, "ARCHIVE_BASENAME_REQUIRED")
    output = args.attempt_dir / name
    public_rows = [{k: v for k, v in row.items() if k != "origin"} for row in rows]
    manifest = {**manifest, "files": public_rows}
    manifest_raw = encode(manifest)
    public_bytes(manifest_raw)
    with zipfile.ZipFile(output, "x", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for row in rows:
            archive.writestr(zip_info(row["path"]), planned_raw(row, repo))
        archive.writestr(zip_info(MANIFEST), manifest_raw)
    if recheck:
        recheck()
    meta, restored = verify_zip(output)
    need(restored == manifest and meta["manifest_sha256"] == sha(manifest_raw), "RESTORED_MANIFEST_MISMATCH")
    receipt = {"schema": "CR_PARENT_EVENT_ARCHIVE_RECEIPT_V1", "unit": UNIT,
               "kind": manifest["kind"], "identity": manifest["identity"], "archive": meta,
               "all_members_SHA256_bytes_CRC_verified": True, "ZIP_testzip_PASS": True,
               "scientific_execution": False, "old_science_replays": 0,
               "metadata_CPU_s": None, "created_utc": now(), "source_archive_rebuilt": False}
    destination = args.attempt_dir / "ARCHIVE_RECEIPT.json"
    write_json(destination, receipt)
    return {"receipt": file_pin(destination), "archive": meta}


def source_build(args):
    plan_raw, _ = file_bytes(args.plan)
    need(sha(plan_raw) == hex_value(args.plan_sha256, 64), "SOURCE_PLAN_SHA_MISMATCH")
    plan = decode(plan_raw)
    need(plan["schema"] == "CR_PARENT_EVENT_SOURCE_PLAN_V1", "SOURCE_PLAN_SCHEMA_MISMATCH")
    S = plan["identity"]["S"]
    need(plan["identity"] == source_identity(S) and plan["input_manifest_sha256"] == INPUT_SHA,
         "SOURCE_PLAN_IDENTITY_MISMATCH")
    repo = absolute(plan["repo_root"])
    rows = plan["files"]
    def recheck():
        for pin in plan["controls"].values():
            pinned_bytes(pin)
        state = decode(pinned_bytes(plan["controls"]["state"]))
        stages = check_state(state, 19, S)
        need(decode(pinned_bytes(plan["controls"]["c09_receipt"])) == stages[-1], "C09_STATE_CHANGED")
        need(git(repo, "rev-parse", "HEAD").decode().strip() == S, "SOURCE_HEAD_ADVANCED")
        need(inventory(repo) == (plan["unit_local_inventory"], plan["excluded_paths"]),
             "POST_PLAN_UNIT_FILE_OR_FAILURE_CREATED")
        current_tree = tree_rows(repo, S, UNIT_PATH + "/")
        all_git = tree_rows(repo, S)
        need(sorted(current_tree) == plan["published_current_unit_paths"], "PUBLISHED_UNIT_COVERAGE_MISMATCH")
        indexed = {r["path"]: r for r in rows}
        need(len(indexed) == len(rows) and set(plan["unit_local_inventory"]).issubset(indexed),
             "UNIT_LOCAL_COVERAGE_MISMATCH")
        for name in current_tree:
            row = indexed[name]
            need(row["publication_class"] == "git_published_at_S"
                 and row["git_blob_sha1_at_S"] == current_tree[name]["blob"], "PUBLISHED_UNIT_BLOB_MISMATCH")
        for row in rows:
            raw = planned_raw(row, repo)
            actual = all_git.get(row["path"])
            matches = bool(actual and actual["type"] == "blob"
                           and actual["mode"] in ("100644", "100755")
                           and git_blob(raw) == actual["blob"])
            need(row["publication_class"] == ("git_published_at_S" if matches else "archive_only")
                 and row["git_path_present_at_S"] == bool(actual)
                 and row["git_blob_sha1_at_S"] == (actual["blob"] if matches else None),
                 "ACTUAL_GIT_PUBLICATION_CLASSIFICATION_MISMATCH")
            if row["origin"]["kind"] == "git":
                local = repo / row["path"]
                if local.exists() or local.is_symlink():
                    need(file_bytes(local)[0] == raw, "PUBLISHED_LOCAL_CHANGED_AFTER_PLAN")
        input_raw = planned_raw(indexed[INPUT_PATH], repo)
        need(sha(input_raw) == INPUT_SHA, "FROZEN_INPUT_MANIFEST_CHANGED")
        inputs = decode(input_raw)["files"]
        need(len(inputs) == 17 and plan["source_payload_paths"] == [i["path"] for i in inputs],
             "FROZEN_SOURCE_PAYLOAD_COVERAGE_MISMATCH")
        for item in inputs:
            row = indexed[item["path"]]
            need(row["bytes"] == item["bytes"] and row["sha256"] == item["sha256"], "SOURCE_PIN_CHANGED")
    recheck()
    published = [r["path"] for r in rows if r["publication_class"] == "git_published_at_S"]
    archive_only = [r["path"] for r in rows if r["publication_class"] == "archive_only"]
    need(len(published) + len(archive_only) == len(rows), "INVALID_PUBLICATION_CLASS")
    # One canonical S gets one claim, even if a later invocation chooses a new
    # attempt directory. A failed/interrupted claim is retained for explicit
    # owner investigation; this command never unlinks it or silently rebuilds.
    registry = repo.parent / "parent_release_source" / "seal_registry" / S
    absolute(registry).mkdir(parents=True, exist_ok=False)
    write_json(registry / "CLAIM.json", {"unit": UNIT, "S": S,
               "source_plan_sha256": sha(plan_raw), "attempt_dir": str(args.attempt_dir),
               "claimed_utc": now(), "missing_sealed_receipt_status": "UNKNOWN_NO_ACK_OR_FAILED",
               "automatic_retry_or_rebuild": False})
    result = package(args, f"BASS_CR_PARENT_EVENT_SOURCE_20261028_{S[:12]}.zip",
                     {"schema": "CR_PARENT_EVENT_SOURCE_MANIFEST_V1", "kind": "SOURCE",
                      "identity": plan["identity"], "source_plan_sha256": sha(plan_raw),
                      "input_manifest_sha256": INPUT_SHA,
                      "git_published_paths": published, "archive_only_paths": archive_only,
                      "source_payload_paths": plan["source_payload_paths"],
                      "excluded_paths": plan["excluded_paths"],
                      "publication_definition": "Archived bytes equal the regular Git blob at exact S; archive-only paths are not raw-Git R3 targets."},
                     rows, repo=repo, recheck=recheck)
    write_json(registry / "SEALED.json", {"unit": UNIT, "S": S, **result,
               "source_plan_sha256": sha(plan_raw), "sealed_utc": now()})
    return result


def check_dual_r3(r3, archive):
    need(r3.get("schema") == "CR_PARENT_EVENT_DUAL_RAW_R3_V1"
         and r3.get("unit") == UNIT and r3.get("both_original_full_GET_and_all_members_PASS") is True,
         "ACTUAL_CURRENT_UNIT_DUAL_R3_REQUIRED")
    for key in ("name", "bytes", "sha256", "members", "payloads", "manifest_sha256"):
        need(r3["archive"][key] == archive[key], "R3_ARCHIVE_IDENTITY_MISMATCH")
    need([r["provider"] for r in r3["providers"]] == ["Dropbox", "Drive"], "EXACT_TWO_PROVIDER_RECEIPTS_REQUIRED")
    for row in r3["providers"]:
        need(row.get("status") == "PASS" and row.get("verification_tier") == "R3"
             and row.get("HTTP_status") == 200 and row.get("raw_HTTP_method") == "GET"
             and row.get("HEAD_or_Range_used") is False and row.get("downloaded_original_file") is True
             and row.get("all_payload_sha256_and_CRC_PASS") is True
             and row.get("downloaded_bytes") == archive["bytes"]
             and row.get("archive_sha256") == archive["sha256"], "FULL_ORIGINAL_PROVIDER_R3_REQUIRED")


def closeout(args):
    control_names = ("identity", "inputs", "state", "source_receipt", "source_r3", "central_receipt",
                     "central_git_r3", "central_return", "handoff", "report")
    original_controls = {key: file_pin(getattr(args, key)) for key in control_names}
    identity = read_json(args.identity)
    need(set(identity) == {"schema", "unit", "S", "D", "M"}
         and identity["schema"] == "CR_PARENT_EVENT_CLOSEOUT_IDENTITY_V1"
         and identity["unit"] == UNIT, "EXACT_CLOSEOUT_IDENTITY_KEYS_REQUIRED")
    S, D, M = [hex_value(identity[k], 40) for k in ("S", "D", "M")]
    state = read_json(args.state)
    stages = check_state(state, 20, D)
    need(stages[-2]["commit"] == S, "ACTUAL_C09_S_C10_D_CHAIN_REQUIRED")
    source_receipt = read_json(args.source_receipt)
    need(source_receipt.get("kind") == "SOURCE" and source_receipt.get("unit") == UNIT
         and source_receipt["identity"]["S"] == S
         and source_receipt.get("all_members_SHA256_bytes_CRC_verified") is True,
         "SEALED_CURRENT_SOURCE_RECEIPT_REQUIRED")
    source = source_receipt["archive"]
    source_meta, source_manifest = verify_zip(absolute(source["path"]), source)
    need(source_manifest.get("kind") == "SOURCE" and source_manifest["identity"]["S"] == S,
         "SEALED_SOURCE_MANIFEST_IDENTITY_MISMATCH")
    r3 = read_json(args.source_r3)
    check_dual_r3(r3, source)
    central = read_json(args.central_receipt)
    need(central.get("science_commit_S") == S and central.get("documents_commit_D") == D
         and central.get("commit_M") == M and central.get("actual_remote_ref") == M
         and central.get("force") is False and central.get("count_effect") == 0,
         "ACTUAL_NONFORCE_CENTRAL_S_D_M_RECEIPT_REQUIRED")
    hex_value(central["expected_parent"], 40)
    need(central.get("nodes") == 88 and central.get("integration_edges") == 17
         and central.get("original_central_total") == 88
         and 0 <= integer(central["original_central_completed"]) <= 88, "CENTRAL_COUNT_SCOPE_MISMATCH")
    reviewed = central["reviewed_identity"]
    need(reviewed.get("unit") == UNIT and reviewed.get("science_commit_S") == S
         and reviewed.get("documents_commit_D") == D, "CENTRAL_REVIEWED_UNIT_IDENTITY_MISMATCH")
    m_r3 = read_json(args.central_git_r3)
    need(m_r3.get("repository") == "cosmosapjw-quantum/rei_bianchi" and m_r3.get("commit") == M
         and m_r3.get("all_bytes_equal") is True and m_r3.get("full_public_blobs") == 2,
         "ACTUAL_CENTRAL_TWO_BLOB_R3_REQUIRED")
    m_rows = m_r3["files"]
    need(len(m_rows) == 2 and len(set(central["paths"])) == 2
         and sorted(r["path"] for r in m_rows) == sorted(central["paths"]), "CENTRAL_R3_EXACT_PATHS_MISMATCH")
    dag_path = "research/orchestration_expansion_20261025/DAG.json"
    return_rows = [r for r in m_rows if r["path"].startswith("research/orchestration_expansion_20261025/returns/")]
    need(dag_path in central["paths"] and len(return_rows) == 1, "CENTRAL_DAG_AND_OWNER_RETURN_ONLY_REQUIRED")
    for row in m_rows:
        need(row.get("HTTP_status") == 200 and row.get("full_GET") is True
             and row.get("identical") is True, "CENTRAL_ACTUAL_FULL_RAW_R3_REQUIRED")
    return_pin = file_pin(args.central_return)
    need(return_rows[0]["bytes"] == return_pin["bytes"]
         and return_rows[0]["sha256"] == return_pin["sha256"], "CENTRAL_RETURN_NOT_ACTUAL_M_BLOB")
    roles = {key: absolute(getattr(args, key)) for key in
             ("identity", "state", "source_receipt", "source_r3", "central_receipt", "central_git_r3",
              "central_return", "handoff", "report")}
    values = read_json(args.inputs)
    need(isinstance(values, list) and values, "EXPLICIT_ORDERED_CLOSEOUT_INPUTS_REQUIRED")
    rows, paths, inodes = [], {}, set()
    for item in values:
        need(set(item) == {"local_path", "archive_path"}, "EXACT_CLOSEOUT_INPUT_KEYS_REQUIRED")
        path, name = absolute(item["local_path"]), safe_name(item["archive_path"])
        need(path != absolute(source["path"]), "SEALED_SOURCE_REEMBED_OR_REBUILD_REFUSED")
        need(path not in paths, "DUPLICATE_CLOSEOUT_LOCAL_SOURCE")
        row = local_row(path, name, {}, None)
        inode = tuple(row["origin"]["snapshot"][:2])
        need(inode not in inodes, "DUPLICATE_CLOSEOUT_PHYSICAL_SOURCE")
        paths[path] = name
        inodes.add(inode)
        row["publication_class"] = "explicit_closeout_payload_no_Git_claim"
        rows.append(row)
    need(all(path in paths for path in roles.values()), "REQUIRED_CLOSEOUT_ROLE_NOT_IN_EXPLICIT_INPUTS")
    role_pins = {role: {"archive_path": paths[path], **file_pin(path)} for role, path in roles.items()}
    for pin in original_controls.values():
        pinned_bytes(pin)
    final_identity = {**identity, "source_archive": source_meta,
                      "source_provider_ids": {r["provider"]: r["id"] for r in r3["providers"]},
                      "actual_published_loop_stages": len(stages), "dual_R2_stages": len(stages),
                      "central_completed": central["original_central_completed"], "central_total": 88,
                      "central_nodes": 88, "central_edges": 17, "CR_count_effect": 0,
                      "historical_central_completed": central.get("historical_original_central_completed"),
                      "closeout_self_hash_bytes_provider_ids_Library_R3": None,
                      "source_archive_rebuilt": False, "old_science_replays": 0,
                      "metadata_CPU_s": None, "global_physical_completion": None,
                      "global_error": None, "global_budget_remaining": None, "currency": None}
    def recheck():
        for pin in original_controls.values():
            pinned_bytes(pin)
        need(archive_metadata(absolute(source["path"]))["sha256"] == source["sha256"], "SEALED_SOURCE_CHANGED")
        for row in rows:
            planned_raw(row)
    # Fixed beside this root-owned parent_ops helper, not beneath the caller's
    # fresh attempt directory. A new namespace cannot rebuild the same D/M.
    # As for SOURCE, a failed claim remains for explicit owner recovery.
    registry = (Path(__file__).absolute().parent.parent / "parent_release_closeout"
                / "seal_registry" / (D + "_" + M))
    absolute(registry).mkdir(parents=True, exist_ok=False)
    write_json(registry / "CLAIM.json", {"unit": UNIT, "S": S, "D": D, "M": M,
               "source_archive_sha256": source["sha256"],
               "explicit_input_list_sha256": original_controls["inputs"]["sha256"],
               "control_pins": original_controls, "attempt_dir": str(args.attempt_dir),
               "claimed_utc": now(), "missing_sealed_receipt_status": "UNKNOWN_NO_ACK_OR_FAILED",
               "automatic_retry_or_rebuild": False})
    result = package(args, f"BASS_CR_PARENT_EVENT_CLOSEOUT_20261028_{D[:12]}_{M[:12]}.zip",
                     {"schema": "CR_PARENT_EVENT_CLOSEOUT_MANIFEST_V1", "kind": "CLOSEOUT",
                      "identity": final_identity, "role_pins": role_pins,
                      "explicit_input_list_sha256": original_controls["inputs"]["sha256"],
                      "self_reference_note": "Actual post-archive hash, provider IDs, Library ID and R3 belong to later receipts; this ZIP and SOURCE remain sealed."},
                     rows, recheck=recheck)
    write_json(registry / "SEALED.json", {"unit": UNIT, "S": S, "D": D, "M": M,
               **result, "source_archive_sha256": source["sha256"],
               "explicit_input_list_sha256": original_controls["inputs"]["sha256"],
               "sealed_utc": now()})
    return result


def pointer(value, path):
    need(isinstance(path, str) and path.startswith("/"), "ABSOLUTE_JSON_POINTER_REQUIRED")
    for part in path[1:].split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def get_file(url, destination, expected_bytes):
    parsed = urllib.parse.urlsplit(url)
    need(parsed.scheme == "https" and parsed.hostname and parsed.username is None and parsed.password is None,
         "HTTPS_TOOL_RETURNED_ORIGINAL_URL_REQUIRED")
    request = urllib.request.Request(url, headers={"Accept-Encoding": "identity"}, method="GET")
    digest, size = hashlib.sha256(), 0
    # Stream unmodified bytes, no HEAD, Range, local synchronized substitutes, or retries.
    with destination.open("xb") as output:
        with urllib.request.urlopen(request, timeout=55) as response:
            need(response.status == 200 and response.headers.get("Content-Range") is None
                 and response.headers.get("Content-Encoding", "identity").lower() == "identity",
                 "COMPLETE_UNENCODED_HTTP_200_REQUIRED")
            need(urllib.parse.urlsplit(response.geturl()).scheme == "https", "HTTPS_REDIRECT_REQUIRED")
            for chunk in iter(lambda: response.read(CHUNK), b""):
                size += len(chunk)
                need(size <= expected_bytes, "HTTP_BODY_EXCEEDS_PINNED_BYTES")
                output.write(chunk)
                digest.update(chunk)
        output.flush()
        os.fsync(output.fileno())
    need(size == expected_bytes, "HTTP_BODY_SIZE_MISMATCH")
    return {"HTTP_status": 200, "bytes": size, "sha256": digest.hexdigest()}


def provider_r3(args):
    receipt = read_json(args.archive_receipt)
    need(receipt.get("schema") == "CR_PARENT_EVENT_ARCHIVE_RECEIPT_V1" and receipt.get("unit") == UNIT,
         "CURRENT_ARCHIVE_RECEIPT_REQUIRED")
    archive = receipt["archive"]
    verify_zip(absolute(archive["path"]), archive)
    backup = read_json(args.backup_receipt)
    need(backup.get("complete") is True and backup.get("metadata_tier") == "R2"
         and backup["dropbox"]["status"] == "completed", "ACTUAL_DUAL_BACKUP_PENDING_COMPLETE_REQUIRED")
    for key in ("name", "bytes", "sha256"):
        need(backup["archive"][key] == archive[key], "BACKUP_ARCHIVE_PIN_MISMATCH")
    need(backup["dropbox_id"] == backup["dropbox"]["file"]["file_id"], "DROPBOX_UPLOAD_ID_MISMATCH")
    drive_id = backup["drive"].get("id") or backup["drive"].get("file", {}).get("id") or backup["drive"].get("file_id")
    need(backup["drive_id"] == drive_id, "DRIVE_UPLOAD_ID_MISMATCH")
    for provider, key in (("Dropbox", "dropbox"), ("Drive", "drive")):
        need(int(backup[key + "_metadata"]["size"]) == archive["bytes"]
             and backup[key + "_metadata"]["id"] == backup[key + "_id"], "PROVIDER_R2_METADATA_MISMATCH")
    acquisition = read_json(args.acquisition)
    need(acquisition.get("schema") == "CR_PARENT_EVENT_ORIGINAL_LINK_ACQUISITION_V1"
         and acquisition.get("unit") == UNIT and acquisition.get("archive_sha256") == archive["sha256"],
         "PINNED_ORIGINAL_LINK_ACQUISITION_REQUIRED")
    links = acquisition["providers"]
    need([r["provider"] for r in links] == ["Dropbox", "Drive"], "EXACT_DUAL_LINK_ORDER_REQUIRED")
    results = []
    for item in links:
        provider = item["provider"]
        key = "dropbox" if provider == "Dropbox" else "drive"
        try:
            need(set(item) == {"provider", "id", "original_file", "actual_request", "raw_response",
                               "url_pointer", "id_pointer"}, "EXACT_ORIGINAL_LINK_FIELDS_REQUIRED")
            need(item["id"] == backup[key + "_id"] and item.get("original_file") is True, "LINK_PROVIDER_IDENTITY_MISMATCH")
            request = item["actual_request"]
            if provider == "Dropbox":
                need(set(request) in ({"entries"}, {"entries", "expiration_in_sec"})
                     and request["entries"] == [item["id"]], "DROPBOX_ORIGINAL_LINK_REQUEST_REQUIRED")
                if "expiration_in_sec" in request:
                    expiry = request["expiration_in_sec"]
                    need(type(expiry) is int and (expiry == 0 or 60 <= expiry <= 900), "DROPBOX_LINK_EXPIRY_INVALID")
            else:
                need(set(request) in ({"url", "download_raw_file", "include_base64"},
                                      {"url", "download_raw_file", "include_base64", "raw_export_mime_type"})
                     and request["download_raw_file"] is True and request["include_base64"] is False
                     and request.get("raw_export_mime_type") is None, "DRIVE_ORIGINAL_FETCH_REQUEST_REQUIRED")
                requested_url = urllib.parse.urlsplit(request["url"])
                need(requested_url.scheme == "https" and requested_url.netloc == "drive.google.com"
                     and requested_url.path in ("/file/d/" + item["id"], "/file/d/" + item["id"] + "/view")
                     and not requested_url.query and not requested_url.fragment,
                     "DRIVE_ACTUAL_CANONICAL_FILE_URL_ID_MISMATCH")
            raw = pinned_bytes(item["raw_response"], sensitive=True)
            response = decode(raw)
            if provider == "Dropbox":
                need(pointer(response, item["id_pointer"]) == item["id"], "DROPBOX_RAW_LINK_ID_MISMATCH")
            elif item.get("id_pointer") is not None:
                need(pointer(response, item["id_pointer"]) == item["id"], "DRIVE_RAW_LINK_ID_MISMATCH")
            url = pointer(response, item["url_pointer"])
            provider_dir = args.attempt_dir / provider
            provider_dir.mkdir()
            destination = provider_dir / archive["name"]
            actual = get_file(url, destination, archive["bytes"])
            need(actual["sha256"] == archive["sha256"], "PROVIDER_ORIGINAL_ARCHIVE_SHA_MISMATCH")
            meta, _ = verify_zip(destination, archive)
            row = {"provider": provider, "id": item["id"], "status": "PASS", "verification_tier": "R3",
                   "raw_HTTP_method": "GET", "HTTP_status": 200, "HEAD_or_Range_used": False,
                   "downloaded_original_file": True, "downloaded_bytes": actual["bytes"],
                   "archive_sha256": actual["sha256"], "archive_members": meta["members"],
                   "manifest_payloads": meta["payloads"], "manifest_sha256": meta["manifest_sha256"],
                   "all_payload_sha256_and_CRC_PASS": True, "local_readback_file": str(destination),
                   "original_request_and_raw_response_pin": {k: v for k, v in item.items() if k != "url_pointer"},
                   "observed_utc": now()}
        except Exception as error:
            # Never serialize a URL, HTTP error body, signed token or raw exception text.
            row = {"provider": provider, "id": backup[key + "_id"], "status": "FAILED",
                   "verification_tier": "R3_NOT_ESTABLISHED", "error_class": type(error).__name__,
                   "refusal_code": str(error) if isinstance(error, Refusal) else None,
                   "observed_utc": now(), "partial_download_preserved": True}
        write_json(args.attempt_dir / (provider + "_R3.json"), row)
        results.append(row)
    passed = all(r["status"] == "PASS" for r in results)
    result = {"schema": "CR_PARENT_EVENT_DUAL_RAW_R3_V1", "unit": UNIT, "archive": archive,
              "both_original_full_GET_and_all_members_PASS": passed, "providers": results,
              "archive_receipt_pin": file_pin(args.archive_receipt),
              "backup_receipt_pin": file_pin(args.backup_receipt), "acquisition_receipt_pin": file_pin(args.acquisition),
              "old_science_replays": 0, "source_archive_rebuilt": False, "metadata_CPU_s": None}
    output = args.attempt_dir / "DUAL_R3.json"
    write_json(output, result)
    need(passed, "ONE_OR_BOTH_PROVIDER_R3_FAILED_SEE_INDIVIDUAL_RECEIPTS")
    return {"receipt": file_pin(output), "both_original_full_GET_and_all_members_PASS": True}


def git_r3(args):
    source = read_json(args.source_receipt)
    need(source.get("kind") == "SOURCE" and source.get("unit") == UNIT, "SEALED_SOURCE_RECEIPT_REQUIRED")
    _, manifest = verify_zip(absolute(source["archive"]["path"]), source["archive"])
    S = hex_value(manifest["identity"]["S"], 40)
    need(manifest["identity"]["repository"] == REPOSITORY, "GIT_REPOSITORY_MISMATCH")
    paths = read_json(args.paths)
    need(isinstance(paths, list) and paths, "EXPLICIT_SELECTIVE_GIT_PATHS_REQUIRED")
    unique_names(paths)
    indexed = {r["path"]: r for r in manifest["files"]}
    for name in paths:
        need(name in manifest["git_published_paths"] and name in indexed
             and indexed[name]["publication_class"] == "git_published_at_S"
             and indexed[name]["git_blob_sha1_at_S"], "ARCHIVE_ONLY_OR_UNPUBLISHED_GIT_TARGET_REFUSED")
    rows = []
    for number, name in enumerate(paths):
        expected = indexed[name]
        try:
            url = "https://raw.githubusercontent.com/" + REPOSITORY + "/" + S + "/" + urllib.parse.quote(name, safe="/")
            destination = args.attempt_dir / f"blob_{number:05}.raw"
            actual = get_file(url, destination, expected["bytes"])
            raw, _ = file_bytes(destination)
            need(actual["sha256"] == expected["sha256"]
                 and git_blob(raw) == expected["git_blob_sha1_at_S"], "GIT_RAW_BLOB_BYTE_IDENTITY_MISMATCH")
            row = {"path": name, "status": "PASS", "bytes": len(raw), "sha256": sha(raw),
                   "git_blob_sha1": git_blob(raw), "HTTP_status": 200, "full_GET": True,
                   "HEAD_or_Range_used": False, "identical": True, "local_readback_file": str(destination)}
        except Exception as error:
            row = {"path": name, "status": "FAILED", "error_class": type(error).__name__,
                   "refusal_code": str(error) if isinstance(error, Refusal) else None}
        write_json(args.attempt_dir / f"blob_{number:05}_RECEIPT.json", row)
        rows.append(row)
    passed = all(r["status"] == "PASS" for r in rows)
    result = {"schema": "CR_PARENT_EVENT_GIT_RAW_R3_V1", "unit": UNIT,
              "repository": REPOSITORY, "commit": S, "verification_tier": "R3" if passed else "R3_INCOMPLETE",
              "all_bytes_equal": passed, "selected_public_blobs": len(paths),
              "full_public_blobs": sum(r["status"] == "PASS" for r in rows), "files": rows,
              "expected_bytes_basis": "Sealed SOURCE manifest's actual Git S blobs; no mutable working-tree oracle",
              "source_receipt_pin": file_pin(args.source_receipt), "paths_pin": file_pin(args.paths),
              "observed_utc": now(), "scientific_replay": 0, "metadata_CPU_s": None}
    output = args.attempt_dir / "GIT_R3.json"
    write_json(output, result)
    need(passed, "SELECTIVE_GIT_R3_FAILED_SEE_INDIVIDUAL_RECEIPTS")
    return {"receipt": file_pin(output), "full_public_blobs": len(paths), "S": S}


def verify_local(args):
    receipt = read_json(args.archive_receipt)
    need(receipt.get("unit") == UNIT, "CURRENT_UNIT_ARCHIVE_REQUIRED")
    meta, _ = verify_zip(absolute(receipt["archive"]["path"]), receipt["archive"])
    result = {"schema": "CR_PARENT_EVENT_LOCAL_ARCHIVE_VERIFICATION_V1", "archive": meta,
              "all_members_SHA256_bytes_CRC_verified": True, "provider_R3": False,
              "content_read_from": "local file only", "scientific_execution": False, "metadata_CPU_s": None}
    output = args.attempt_dir / "LOCAL_VERIFICATION.json"
    write_json(output, result)
    return {"receipt": file_pin(output)}


def parser():
    main = argparse.ArgumentParser(description=__doc__)
    commands = main.add_subparsers(dest="command", required=True)
    handlers = {"source-plan": source_plan, "source-build": source_build, "closeout": closeout,
                "provider-r3": provider_r3, "git-r3": git_r3, "verify-local": verify_local}
    fields = {
        "source-plan": ("repo-root", "S", "state", "c09-receipt", "published-paths"),
        "source-build": ("plan", "plan-sha256"),
        "closeout": ("identity", "inputs", "state", "source-receipt", "source-r3",
                     "central-receipt", "central-git-r3", "central-return", "handoff", "report"),
        "provider-r3": ("archive-receipt", "backup-receipt", "acquisition"),
        "git-r3": ("source-receipt", "paths"),
        "verify-local": ("archive-receipt",),
    }
    for name, handler in handlers.items():
        command = commands.add_parser(name)
        command.add_argument("--attempt-dir", required=True, type=Path,
                             help="Fresh absolute directory outside the current unit; never reused")
        for field in fields[name]:
            command.add_argument("--" + field, required=True)
        if name == "source-plan":
            command.add_argument("--extras")
        command.set_defaults(handler=handler)
    return main


def main():
    args = parser().parse_args()
    args.attempt_dir = absolute(args.attempt_dir)
    # A directory is the immutable invocation namespace. A START without TERMINAL
    # remains UNKNOWN_NO_ACK; later explicit attempts never erase it.
    need(UNIT_PATH not in args.attempt_dir.as_posix(), "ATTEMPT_DIRECTORY_MUST_BE_OUTSIDE_UNIT")
    args.attempt_dir.mkdir(parents=True, exist_ok=False)
    write_json(args.attempt_dir / "START.json",
               {"schema": "CR_PARENT_EVENT_RELEASE_ATTEMPT_V1", "unit": UNIT,
                "command": args.command, "started_utc": now(), "helper": file_pin(Path(__file__).absolute()),
                "scientific_execution": False, "metadata_CPU_s": None,
                "missing_terminal_status": "UNKNOWN_NO_ACK", "automatic_retry": False})
    try:
        result = args.handler(args)
        write_json(args.attempt_dir / "TERMINAL.json", {"status": "PASS", "observed_utc": now(), **result})
        print(json.dumps({"status": "PASS", "command": args.command,
                          "attempt_dir": str(args.attempt_dir), **result}, ensure_ascii=False))
        return 0
    except Exception as error:
        result = {"status": "FAILED", "command": args.command, "observed_utc": now(),
                  "error_class": type(error).__name__,
                  "refusal_code": str(error) if isinstance(error, Refusal) else None,
                  "created_files_preserved": True, "automatic_retry": False,
                  "scientific_execution": False, "metadata_CPU_s": None}
        write_json(args.attempt_dir / "TERMINAL.json", result)
        print(json.dumps(result, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
