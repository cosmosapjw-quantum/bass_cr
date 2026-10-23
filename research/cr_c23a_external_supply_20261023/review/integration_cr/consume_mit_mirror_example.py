"""Standalone public-subset consumer; call only inside an admitted worker.

This helper needs the 49-file deposition public subset, not the original author
tar, C reader, or original-table audit directory. It does not rerun old audits.
It has no automatic execution entry point and was syntax-checked, NOT_RUN.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import types

CODE_SHA256 = "53c9056908fe9a875c35bb7d8047149d3c45f5d0856aac74ebe84e4248a51809"
REUSE_RECEIPT_SHA256 = "65c40c2dbe7b26d06377d63c2a40e357e1aa7fb195f031487d338d1efb9b442f"
MIRROR_COMMIT = "72d8a2d23702f1b69fbc85abd25d4592a7bcd3f5"


def consume_public_subset(deposition_root: str | Path) -> dict:
    """One fresh diagnostic input, supplied by caller; output is a Python dict.

    Caller owns resource/lease admission, one native thread and create-only
    serialization. No P19 spectrum or physical21-state coupling is inferred.
    """
    root = Path(deposition_root).resolve()
    code_path = root / "fs2010_operator.py"
    code_bytes = code_path.read_bytes()
    if hashlib.sha256(code_bytes).hexdigest() != CODE_SHA256:
        raise ValueError("EXAMPLE_REQUIRES_REVIEWED_OPERATOR_IDENTITY")
    receipt_bytes = (root / "EXTERNAL_REUSE_DOWNLOADS.json").read_bytes()
    if hashlib.sha256(receipt_bytes).hexdigest() != REUSE_RECEIPT_SHA256:
        raise ValueError("EXAMPLE_REQUIRES_REVIEWED_MIRROR_RECEIPT")
    receipt = json.loads(receipt_bytes)
    if receipt["repos"]["21cmFAST"]["commit"] != MIRROR_COMMIT:
        raise ValueError("MIRROR_COMMIT_MISMATCH")
    rows = [r for r in receipt["files"] if r["repo"] == "21cmFAST"]
    if len(rows) != 15 or sum(r["path"] == "LICENSE" for r in rows) != 1:
        raise ValueError("MIRROR_TABLES_AND_LICENSE_REQUIRED")
    for row in rows:
        data = (root / "external_comparison" / "21cmFAST" / row["path"]).read_bytes()
        if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise ValueError("MIRROR_BYTES_CHANGED: " + row["path"])
        blob = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
        if hashlib.sha1(blob).hexdigest() != row["blob_sha1"]:
            raise ValueError("MIRROR_GIT_BLOB_CHANGED: " + row["path"])

    # Execute the exact bytes just validated, avoiding an import cache race.
    name = "c23a_reviewed_fs2010_public_consumer"
    module = types.ModuleType(name)
    module.__file__ = str(code_path)
    sys.modules[name] = module
    exec(compile(code_bytes, str(code_path), "exec"), module.__dict__)
    tables = root / "external_comparison/21cmFAST/src/py21cmfast/_data/x_int_tables"
    response = module.FS2010Response(tables, axis="unambiguous_high_ionization")

    # Declared new PL number source, not the historical audit's three spectra.
    spectrum = module.PLSpectrum((20.0, 100.0, 1000.0), (0.002, 0.001, 0.0))
    result = response.prepare(spectrum).at(0.5)
    return {
        "status": "FINITE_SOURCE_RESPONSE_ONLY",
        "mirror_commit": MIRROR_COMMIT,
        "operator_sha256": CODE_SHA256,
        "input": {"energy_eV": spectrum.energy, "PL_number_rate": spectrum.number_rate,
                  "units": spectrum.units, "xi": 0.5},
        "response": result,
        "new_cosmological_ODE": 0,
        "physical_coupling": "NOT_ADMITTED",
        "global_error_bound": None,
        "attribution": "Furlanetto & Stoever (2010), DOI10.1111/j.1365-2966.2010.16401.x; data mirror 21cmFAST with its included MIT LICENSE",
    }
