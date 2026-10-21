"""Source and publication admission for the additive C21K native runner.

No scientific import, provider construction or numerical execution occurs here.
H/I receipts keep their original content identities; the new K receipt admits a
detached descendant whose inherited execution bytes remain the pinned originals.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess

REPOSITORY = "cosmosapjw-quantum/bass_cr"
UNIT = "research/cr_c21k_epoch_cache_campaign_20261021"
H_NAME = "cr_c21h_vigilode_bridge_20261019"
I_NAME = "cr_c21i_callback_optimization_20261020"
G_NAME = "cr_c21g_reference_refinement_20261019"
F_NAME = "cr_c21e_event_native_20261018"
H_CONTENT = "40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8"
I_CONTENT = "fe6bbaec2de5032b938aed0713623b9618ba70e6"
H_MANIFEST_SHA256 = "7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb"
I_MANIFEST_SHA256 = "f868b23a3188e959e60b79ffc8974ae399a28d63228a79b18c2da3c40f0cb9ec"
G_MANIFEST_SHA256 = "7b14b62a20714fc66216ebd9d446af1ed1a05de889447ec410158b52e5923fed"
OPTIMIZATIONS = ("vectorized", "vectorized_exact")
RUNTIME_FILES = frozenset(("run_epoch_pilot.py", "epoch_adapter.py", "epoch_pilot_contract.py"))
I_RUNTIME_FILES = frozenset(("run_optimized_pilot.py", "optimized_adapter.py", "native_cache_contract.py"))
EPOCH_POLICY = "PRIVATE_CELL_EPOCH_OPTIMIZATION_V1"


class EpochPilotError(RuntimeError):
    pass


def record(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def read_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise EpochPilotError("DUPLICATE_JSON_KEY " + key)
            result[key] = value
        return result

    def reject(value):
        raise EpochPilotError("NONFINITE_JSON_NUMBER " + value)

    value = json.loads(raw, object_pairs_hook=unique, parse_constant=reject)
    if type(value) is not dict:
        raise EpochPilotError("JSON_OBJECT_REQUIRED")
    return value


def _regular_file(unit, name):
    unit = Path(unit).resolve()
    rel = Path(name)
    if not name or rel.is_absolute() or ".." in rel.parts or "\n" in name:
        raise EpochPilotError("RUNTIME_SOURCE_PATH " + name)
    path = unit
    for part in rel.parts:
        path = path / part
        if path.is_symlink():
            raise EpochPilotError("RUNTIME_SOURCE_SYMLINK " + name)
    if not path.is_file() or not path.resolve().is_relative_to(unit):
        raise EpochPilotError("RUNTIME_SOURCE_PATH " + name)
    return path.read_bytes()


def _records(mapping):
    if type(mapping) is not dict or not mapping:
        raise EpochPilotError("NONEMPTY_RUNTIME_MAP_REQUIRED")
    for name, value in mapping.items():
        if (type(name) is not str or type(value) is not dict
                or set(value) != {"bytes", "sha256"}
                or type(value["bytes"]) is not int or value["bytes"] < 0
                or type(value["sha256"]) is not str
                or re.fullmatch(r"[0-9a-f]{64}", value["sha256"]) is None):
            raise EpochPilotError("EXACT_FILE_RECORD_REQUIRED")
    return mapping


def _source(unit, *, manifest_sha256=None):
    raw = _regular_file(unit, "EXECUTION_MANIFEST.json")
    if manifest_sha256 is not None and record(raw)["sha256"] != manifest_sha256:
        raise EpochPilotError("PINNED_EXECUTION_MANIFEST_REQUIRED")
    manifest = read_json(raw)
    files = {}
    for name, expected in _records(manifest.get("runtime_files")).items():
        data = _regular_file(unit, name)
        if record(data) != expected:
            raise EpochPilotError("RUNTIME_SOURCE_MISMATCH " + name)
        files[name] = data
    identity = {"manifest": record(raw), "runtime_files": copy.deepcopy(manifest["runtime_files"])}
    return manifest, identity, files


def verify_inherited_sources(i_unit):
    i_unit = Path(i_unit).resolve()
    h_unit = i_unit.parent / H_NAME
    hm, h, hf = _source(h_unit, manifest_sha256=H_MANIFEST_SHA256)
    im, i, inf = _source(i_unit, manifest_sha256=I_MANIFEST_SHA256)
    if (i_unit.name != I_NAME or len(hf) != 8 or set(inf) != I_RUNTIME_FILES
            or hm.get("schema") != "C21H_EXECUTION_MANIFEST_V1"
            or im.get("schema") != "C21I_EXECUTION_MANIFEST_V1"
            or im.get("c21h_manifest_sha256") != H_MANIFEST_SHA256):
        raise EpochPilotError("PINNED_H_I_RUNTIME_CLOSURE_REQUIRED")
    return h, i, inf


def verify_k_source(mode, unit):
    if mode not in OPTIMIZATIONS:
        raise EpochPilotError("UNKNOWN_C21K_OPTIMIZATION")
    manifest, own, files = _source(unit)
    if (manifest.get("schema") != "C21K_EXECUTION_MANIFEST_V1"
            or manifest.get("unit") != UNIT or set(files) != RUNTIME_FILES
            or manifest.get("c21h_manifest_sha256") != H_MANIFEST_SHA256
            or manifest.get("c21i_manifest_sha256") != I_MANIFEST_SHA256):
        raise EpochPilotError("C21K_THREE_SOURCE_MANIFEST_REQUIRED")
    identity = {"schema": "C21K_SOURCE_IDENTITY_V1", "optimization": mode,
                "epoch_policy": EPOCH_POLICY, **own,
                "inherited_c21i_content": I_CONTENT,
                "c21h_manifest_sha256": H_MANIFEST_SHA256,
                "c21i_manifest_sha256": I_MANIFEST_SHA256}
    return identity, files


def _git(root, *args, allowed=(0,), input_bytes=None):
    completed = subprocess.run(["git", "-C", str(root), *args], input=input_bytes,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               timeout=15, check=False)
    if completed.returncode not in allowed:
        raise EpochPilotError("PUBLICATION_GIT_CHECK_FAILED " + " ".join(args))
    return completed


def _committed_records(root, specifications):
    """Read all requested committed blobs in one bounded Git child process."""
    queries = list(specifications)
    response = _git(root, "cat-file", "--batch",
                    input_bytes=("\n".join(queries) + "\n").encode()).stdout
    offset = 0
    for query in queries:
        end = response.find(b"\n", offset)
        if end < 0:
            raise EpochPilotError("COMMITTED_BLOB_RESPONSE_TRUNCATED")
        fields = response[offset:end].split()
        if (len(fields) != 3 or re.fullmatch(rb"[0-9a-f]{40}", fields[0]) is None
                or fields[1] != b"blob" or not fields[2].isdigit()):
            raise EpochPilotError("COMMITTED_BLOB_REQUIRED " + query)
        size = int(fields[2])
        start, stop = end + 1, end + 1 + size
        if stop >= len(response) or response[stop:stop + 1] != b"\n":
            raise EpochPilotError("COMMITTED_BLOB_RESPONSE_TRUNCATED")
        if record(response[start:stop]) != specifications[query]:
            raise EpochPilotError("PUBLISHED_RUNTIME_CONTENT_MISMATCH " + query)
        offset = stop + 1
    if offset != len(response):
        raise EpochPilotError("COMMITTED_BLOB_RESPONSE_TRAILING_DATA")


def _publication(path, unit, own, root, expected_commit=None):
    if path is None:
        raise EpochPilotError("EXTERNAL_PUBLISHED_RECEIPTS_REQUIRED")
    path = Path(path)
    if path.is_symlink():
        raise EpochPilotError("PUBLICATION_RECEIPT_SYMLINK")
    path = path.resolve(strict=True)
    if path.is_relative_to(root):
        raise EpochPilotError("PUBLICATION_CONTROL_MUST_BE_OUTSIDE_CHECKOUT")
    raw = path.read_bytes()
    receipt = read_json(raw)
    relative = Path(unit).resolve().relative_to(root).as_posix()
    commit = receipt.get("content_commit")
    if (receipt.get("status") != "PUBLISHED"
            or receipt.get("repository") != REPOSITORY
            or receipt.get("unit") != relative
            or type(commit) is not str or re.fullmatch(r"[0-9a-f]{40}", commit) is None
            or type(receipt.get("branch")) is not str or not receipt["branch"]
            or receipt.get("execution_manifest_sha256") != own["manifest"]["sha256"]
            or (expected_commit is not None and commit != expected_commit)):
        raise EpochPilotError("MATCHING_PUBLISHED_CONTENT_RECEIPT_REQUIRED " + relative)
    if _git(root, "cat-file", "-t", commit).stdout.strip() != b"commit":
        raise EpochPilotError("PUBLISHED_CONTENT_COMMIT_REQUIRED")
    return {"receipt_path": str(path), "receipt": record(raw), "repository": REPOSITORY,
            "unit": relative, "content_commit": commit, "manifest": own["manifest"]}


def _fg_records(research):
    """The fixed G manifest is authority for unchanged F/G code and six baselines."""
    raw = _regular_file(Path(research) / G_NAME, "EXECUTION_MANIFEST.json")
    if record(raw)["sha256"] != G_MANIFEST_SHA256:
        raise EpochPilotError("PINNED_C21G_MANIFEST_REQUIRED")
    manifest = read_json(raw)
    groups = ((F_NAME, "c21f_runtime_files", 10),
              (G_NAME, "c21g_runtime_files", 4),
              (F_NAME + "/evidence/C21F_NATIVE_NCP_20261018T1358Z", "baseline_files", 6))
    result = {"research/" + G_NAME + "/EXECUTION_MANIFEST.json": record(raw)}
    for prefix, key, count in groups:
        entries = _records(manifest.get(key))
        if len(entries) != count:
            raise EpochPilotError("PINNED_F_G_CLOSURE_REQUIRED")
        result.update({"research/" + prefix + "/" + name: expected
                       for name, expected in entries.items()})
    return result


def verify_publications(k_receipt, i_receipt, h_receipt, k_own, i_own, h_own,
                        *, k_unit, i_unit):
    k_unit, i_unit = Path(k_unit).resolve(), Path(i_unit).resolve()
    h_unit = i_unit.parent / H_NAME
    units = (h_unit, i_unit, k_unit)
    roots = [Path(_git(unit, "rev-parse", "--show-toplevel").stdout.decode().strip()).resolve()
             for unit in units]
    root = roots[0]
    if (any(other != root for other in roots)
            or k_unit.relative_to(root).as_posix() != UNIT
            or h_unit.parent != k_unit.parent or i_unit.parent != k_unit.parent):
        raise EpochPilotError("PUBLISHED_UNITS_REQUIRE_ONE_CHECKOUT")
    h = _publication(h_receipt, h_unit, h_own, root, H_CONTENT)
    i = _publication(i_receipt, i_unit, i_own, root, I_CONTENT)
    k = _publication(k_receipt, k_unit, k_own, root)
    _git(root, "merge-base", "--is-ancestor", H_CONTENT, I_CONTENT)
    _git(root, "merge-base", "--is-ancestor", I_CONTENT, k["content_commit"])
    head = _git(root, "rev-parse", "HEAD").stdout.decode().strip()
    attached = _git(root, "symbolic-ref", "-q", "HEAD", allowed=(0, 1))
    if head != k["content_commit"] or attached.returncode != 1:
        raise EpochPilotError("DETACHED_PUBLISHED_C21K_CONTENT_CHECKOUT_REQUIRED")
    specifications = {}
    for published, own in ((h, h_own), (i, i_own), (k, k_own)):
        for name, expected in {"EXECUTION_MANIFEST.json": own["manifest"],
                               **own["runtime_files"]}.items():
            relative = published["unit"] + "/" + name
            specifications[published["content_commit"] + ":" + relative] = expected
            specifications[k["content_commit"] + ":" + relative] = expected
    for name, expected in _fg_records(k_unit.parent).items():
        specifications[k["content_commit"] + ":" + name] = expected
    _committed_records(root, specifications)
    return {"schema": "C21K_NATIVE_PUBLICATION_IDENTITY_V1", "c21h": h,
            "c21i": i, "c21k": k, "inherited_execution_bytes_unchanged": True}
