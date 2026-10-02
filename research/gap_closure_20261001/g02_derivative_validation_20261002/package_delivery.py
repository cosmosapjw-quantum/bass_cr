"""Create an R4Z archive with immutable R4Y base and hash-verified new evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


BASE_NAME = "BASS_CR_R4Y_G02_RESEARCH_PACKAGE_20261002_v1.zip"
BASE_SHA256 = "da4d5ac53bc2da7c7693e13e1ebf47c5cee4861fcccf74331a7aae2c7d3f1297"
BASE_BYTES = 30818484
SOURCE_REL = "research/gap_closure_20261001/g02_derivative_validation_20261002"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def allowed(path):
    return (not path.is_symlink() and path.is_file()
            and not any(part.startswith(".") or part == "__pycache__" for part in path.parts)
            and path.suffix not in (".pyc", ".pyo", ".tmp", ".part", ".swp")
            and not path.name.endswith("~"))


def build(root, output, physical_cross_calls):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError("create-only archive required")
    if not isinstance(physical_cross_calls, int) or physical_cross_calls < 0:
        raise ValueError("actual nonnegative physical cross-operator call count required")
    members = {}

    def add(name, path):
        if name in members:
            raise ValueError("duplicate archive member: " + name)
        if not allowed(path):
            raise ValueError("required source missing or excluded: " + str(path))
        members[name] = path

    def tree(path, prefix):
        if not path.is_dir():
            raise ValueError("required evidence directory missing: " + str(path))
        for item in sorted(path.rglob("*")):
            if allowed(item):
                add(prefix + "/" + item.relative_to(path).as_posix(), item)

    base = root / "deliverables_r4y" / BASE_NAME
    base_data = base.read_bytes()
    if len(base_data) != BASE_BYTES or sha(base_data) != BASE_SHA256:
        raise ValueError("R4Y base package identity mismatch")
    add("base/" + base.name, base)
    source = root / "recovered_r4u/source"
    tree(source / SOURCE_REL, "source/" + SOURCE_REL)
    add("source/AGENTS.md", source / "AGENTS.md")
    tree(root / "runs_r4z", "runs_r4z")
    reports = root / "deliverables_r4z"
    if not reports.is_dir():
        raise ValueError("required deliverables directory missing")
    for path in sorted(reports.iterdir()):
        if (allowed(path) and path.suffix in (".md", ".json", ".csv", ".sqlite")
                and "RECEIPT" not in path.name and "PACKAGE_VALIDATION" not in path.name):
            add("reports/" + path.name, path)
    add("publication/PUBLICATION_RECEIPT.json", root / "publication_r4z/PUBLICATION_RECEIPT.json")
    manifest = {
        "schema": "BASS_R4Z_PACKAGE_MANIFEST_V1", "base_package_sha256": BASE_SHA256,
        "base_package_bytes": BASE_BYTES,
        "members": [{"path": name, "bytes": path.stat().st_size, "sha256": sha(path.read_bytes())}
                    for name, path in sorted(members.items())],
        "scope": "One G02 central derivative validation step; immutable R4Y base contains all earlier evidence and DBv11",
        "physical_G02_closed": False, "production": "HOLD", "capture": False,
        "physical_cross_calls": physical_cross_calls,
        "physical_cross_calls_definition": "Complete physical cross-operator evaluations only; excludes per-batch native kernel invocations",
    }
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, path in sorted(members.items()):
            archive.writestr(name, path.read_bytes())
        archive.writestr("MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(members) | {"MANIFEST.json"}:
            raise ValueError("archive membership mismatch")
        if archive.testzip() is not None:
            raise ValueError("archive CRC mismatch")
        if json.loads(archive.read("MANIFEST.json")) != manifest:
            raise ValueError("archive manifest mismatch")
        for entry in manifest["members"]:
            data = archive.read(entry["path"])
            if len(data) != entry["bytes"] or sha(data) != entry["sha256"]:
                raise ValueError("member identity mismatch: " + entry["path"])
    return {"schema": "BASS_R4Z_PACKAGE_VALIDATION_V1", "file": output.name,
            "bytes": output.stat().st_size, "sha256": sha(output.read_bytes()),
            "members": len(members) + 1, "CRC": "PASS", "member_sha256": "PASS",
            "base_package_sha256": BASE_SHA256, "physical_cross_calls": physical_cross_calls,
        "physical_cross_calls_definition": "Complete physical cross-operator evaluations only; excludes per-batch native kernel invocations",
            "production": "HOLD", "capture": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "output", "receipt"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--physical-cross-calls", type=int, required=True,
                        help="Actual complete physical cross-operator evaluations in this step; excludes per-batch native kernel invocations and older base work")
    args = parser.parse_args()
    if args.receipt.exists() or args.output.resolve() == args.receipt.resolve():
        raise ValueError("create-only distinct receipt required")
    result = build(args.root, args.output, args.physical_cross_calls)
    with args.receipt.open("x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps(result))
