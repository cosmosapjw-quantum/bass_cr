"""Execute the delivered probe once, retaining its temporary native artifacts.

Only TemporaryDirectory cleanup is observed. The supplied Python/Rust bytes,
compiler arguments, StepControl, fixtures and numerical checks stay unchanged.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import runpy
import shutil
import sys
import tempfile
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", type=Path, required=True)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--toolchain-bin", type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    original_temp = tempfile.TemporaryDirectory
    captures = []

    class CaptureTemp(original_temp):
        def __exit__(self, *exc):
            destination = args.output / f"native_artifacts_{len(captures)}"
            shutil.copytree(self.name, destination)
            captures.append(str(destination))
            return super().__exit__(*exc)

    tempfile.TemporaryDirectory = CaptureTemp
    os.environ["PATH"] = str(args.toolchain_bin) + os.pathsep + os.environ["PATH"]
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[name] = "1"
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    sys.argv = [str(args.script), "--repo", str(args.repo), "--output",
                str(args.output / "NATIVE_RESULT.json")]
    started = time.monotonic()
    code = 1
    try:
        runpy.run_path(str(args.script), run_name="__main__")
        code = 0
    except SystemExit as stop:
        code = stop.code if isinstance(stop.code, int) else 1
    finally:
        files = {}
        for folder in captures:
            for p in Path(folder).iterdir():
                if p.is_file():
                    files[str(p.relative_to(args.output))] = {
                        "bytes": p.stat().st_size,
                        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                    }
        result = {"exit_code": code, "wall_seconds": time.monotonic()-started,
                  "children_peak_RSS_KiB": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                  "execution_attempt_count": 1, "automatic_retries": 0,
                  "script_sha256": hashlib.sha256(args.script.read_bytes()).hexdigest(),
                  "observer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  "retained_native_files": files,
                  "affinity": sorted(os.sched_getaffinity(0)),
                  "observation_scope": "Cleanup retention only; no numerical/source/argument changes"}
        (args.output / "OBSERVATION_RECEIPT.json").write_text(json.dumps(result, indent=2)+"\n")
    raise SystemExit(code)


if __name__ == "__main__":
    main()
