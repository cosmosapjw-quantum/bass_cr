"""Create an R4X archive with immutable R4W base and hash-verified new evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


BASE_NAME = "BASS_CR_R4W_G02_RESEARCH_PACKAGE_20261001_v1.zip"
BASE_SHA256 = "eb3332f61be633f38e22bf6294f1e5537e6be25d960e7f708fd9794af46d69f5"
BASE_BYTES = 26227037
SOURCE_REL = "research/gap_closure_20261001/g02_continuous_basis_20261002"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def allowed(path):
    return (not path.is_symlink() and path.is_file()
            and not any(part.startswith(".") or part == "__pycache__" for part in path.parts)
            and path.suffix not in (".pyc", ".pyo", ".tmp", ".part", ".swp")
            and not path.name.endswith("~"))


def build(root, output, new_native_calls):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError("create-only archive required")
    if not isinstance(new_native_calls, int) or new_native_calls < 0:
        raise ValueError("actual nonnegative new native call count required")
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

    base = root / "deliverables_r4w" / BASE_NAME
    base_data = base.read_bytes()
    if len(base_data) != BASE_BYTES or sha(base_data) != BASE_SHA256:
        raise ValueError("R4W base package identity mismatch")
    add("base/" + base.name, base)
    source = root / "recovered_r4u/source"
    tree(source / SOURCE_REL, "source/" + SOURCE_REL)
    add("source/AGENTS.md", source / "AGENTS.md")
    tree(root / "runs_r4x", "runs_r4x")
    reports = root / "deliverables_r4x"
    if not reports.is_dir():
        raise ValueError("required deliverables directory missing")
    for path in sorted(reports.iterdir()):
        if (allowed(path) and path.suffix in (".md", ".json", ".csv", ".sqlite")
                and "RECEIPT" not in path.name and "PACKAGE_VALIDATION" not in path.name):
            add("reports/" + path.name, path)
    add("publication/PUBLICATION_RECEIPT.json", root / "publication_r4x/PUBLICATION_RECEIPT.json")
    manifest = {
        "schema": "BASS_R4X_PACKAGE_MANIFEST_V1", "base_package_sha256": BASE_SHA256,
        "base_package_bytes": BASE_BYTES,
        "members": [{"path": name, "bytes": path.stat().st_size, "sha256": sha(path.read_bytes())}
                    for name, path in sorted(members.items())],
        "scope": "One G02 continuous-basis research step; immutable R4W base contains all earlier evidence and DBv9",
        "physical_G02_closed": False, "production": "HOLD", "capture": False,
        "new_native_calls": new_native_calls,
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
    return {"schema": "BASS_R4X_PACKAGE_VALIDATION_V1", "file": output.name,
            "bytes": output.stat().st_size, "sha256": sha(output.read_bytes()),
            "members": len(members) + 1, "CRC": "PASS", "member_sha256": "PASS",
            "base_package_sha256": BASE_SHA256, "new_native_calls": new_native_calls,
            "production": "HOLD", "capture": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "output", "receipt"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--new-native-calls", type=int, required=True,
                        help="Actual new native calls in this research step; do not infer from older base")
    args = parser.parse_args()
    if args.receipt.exists() or args.output.resolve() == args.receipt.resolve():
        raise ValueError("create-only distinct receipt required")
    result = build(args.root, args.output, args.new_native_calls)
    with args.receipt.open("x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps(result))
