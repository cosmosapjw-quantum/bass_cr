"""R3M16-labelled reuse of the read-only R3M15 slab/CAP support audit."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.r3m15_support_audit import audit
from scripts.r3m15_coordinator import write_new


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.run)
    result["schema"] = "BASS_CR_R3M16_SUPPORT_AUDIT_V1"
    with Path(__file__).open("rb") as stream:
        result["instrumentation_sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
    result["reused_algorithm"] = "scripts/r3m15_support_audit.py; read-only final-state postprocessing"
    write_new(args.out, result)
    print(json.dumps(result, indent=2, allow_nan=False))
