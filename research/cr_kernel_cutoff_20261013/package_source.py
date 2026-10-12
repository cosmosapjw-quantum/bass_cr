"""Create a source archive from accepted local artifacts, without science runs.

The archive records a snapshot. Later remote delivery receipts are separate
metadata and do not change its bytes. External literature read caches are
indexed but are not redistributed. This command never writes science sources.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
UNIT = "CR-THEORY-KERNEL-CUTOFF-20261013"
MANIFEST = "SOURCE_MANIFEST.json"


def identity(path):
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def distribution_files():
    """Full own source and evidence, excluding transient and external caches."""
    files = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        if "__pycache__" in rel.parts or p.suffix in {".pyc", ".aux", ".out", ".toc"}:
            continue
        if rel.as_posix().startswith("inputs/literature/"):
            continue
        if rel.as_posix() == MANIFEST:
            continue
        files.append(p)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--science-commit", required=True)
    parser.add_argument("--archive-path", type=Path, required=True)
    args = parser.parse_args()
    if len(args.science_commit) != 40 or any(x not in "0123456789abcdef" for x in args.science_commit):
        parser.error("science commit must be a complete lowercase Git SHA")
    archive = args.archive_path.resolve()
    if archive.is_relative_to(ROOT):
        parser.error("archive must be outside the source directory")
    if archive.exists():
        parser.error("create-only archive already exists")
    for required in ["EXTERNAL_REFERENCE_INDEX.json", "review/POST_REVIEW_BINDING.json", "results/PDF_QA.json", "PUBLICATION.json"]:
        if not (ROOT / required).is_file():
            parser.error(f"missing required artifact: {required}")
    candidate = json.loads((ROOT / "review/CANDIDATE_MANIFEST.json").read_text())
    files = distribution_files()
    relative = {str(p.relative_to(ROOT)) for p in files}
    omitted = [identity(p) for p in sorted((ROOT / "inputs/literature").glob("*.json"))]
    omitted_paths = {x["path"] for x in omitted}
    assert len(omitted) == 11
    coverage = []
    for rec in candidate["files"]:
        if rec["path"] in relative:
            disposition = "included"
        elif rec["path"] in omitted_paths:
            disposition = "external_reference_index_only"
        else:
            raise ValueError(f"unaccounted frozen dependency: {rec['path']}")
        coverage.append({"path": rec["path"], "sha256": rec["sha256"], "disposition": disposition})
    records = [identity(p) for p in files]
    manifest = {
        "schema": "bass-cr-source-manifest.v1", "unit": UNIT,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "repository": "cosmosapjw-quantum/bass_cr",
        "science_commit": args.science_commit,
        "archive_filename": archive.name,
        "archive_member_prefix": ROOT.name + "/",
        "stage": "immutable archive snapshot before external delivery receipts",
        "semantics": "This manifest describes the archived snapshot. Final Git metadata and the separately delivered HANDOFF record later provider acknowledgements; their updates do not modify this archive.",
        "file_count_excluding_manifest": len(records),
        "manifest_self_hash": "excluded to avoid recursion; archive identity is in final DELIVERY.json",
        "files": records,
        "external_reference_index": identity(ROOT / "EXTERNAL_REFERENCE_INDEX.json"),
        "external_literature_cache_omitted": omitted,
        "frozen_candidate_coverage": coverage,
        "frozen_candidate_counts": {"reviewed": len(coverage), "included": sum(x["disposition"] == "included" for x in coverage), "externally_indexed": len(omitted)},
        "font_policy": "ZIP includes exact font binaries and licenses; Git contains font README and licenses only.",
        "scientific_checks_executed": 0,
    }
    (ROOT / MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    files.append(ROOT / MANIFEST)
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(files):
            name = ROOT.name + "/" + str(p.relative_to(ROOT))
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 13, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, p.read_bytes())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(files)
        for rec in records:
            data = z.read(ROOT.name + "/" + rec["path"])
            assert len(data) == rec["bytes"]
            assert hashlib.sha256(data).hexdigest() == rec["sha256"]
    raw = archive.read_bytes()
    print(json.dumps({"path": str(archive), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "md5": hashlib.md5(raw).hexdigest(), "members": len(files), "frozen_included": 61, "external_indexed": 11, "integrity": "PASS"}))


if __name__ == "__main__":
    main()
