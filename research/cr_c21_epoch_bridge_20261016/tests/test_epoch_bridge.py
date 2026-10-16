"""Focused parity and epoch-domain checks against the original C19 bridge."""
from __future__ import annotations

import math
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
C19 = ROOT / "research/cr_c19_coupled_20261015/src/c19_rhs.rs"
C21 = HERE / "src/c21_epoch_rhs.rs"
INPUTS = ROOT / "research/cr_c20_original_recovery_20261016/inputs"
OWNER_TARGET = Path(os.environ.get("C21_OWNER_TARGET", "/root/BASS_CR_C20_20261015_002/target/release"))
RLIB = OWNER_TARGET / "librei_microphysics.rlib"
DEPS = OWNER_TARGET / "deps"
GAS_AND_PHOTO = (
    "1.0e-1", "1.0e-1", "1.0e-5", "1.0e0",
    "1.0e-16", "1.0e-16", "1.0e-16",
    "1.0e-27", "1.0e-27", "1.0e-27",
)


def invoke(binary: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(binary), str(INPUTS / "config.cfg"), str(INPUTS / "checkpoint.txt"), *args],
        text=True, capture_output=True, check=False, timeout=30,
    )


def rows(stdout: str) -> tuple[str, dict[str, tuple[float, ...]]]:
    lines = stdout.splitlines()
    return lines[0], {
        parts[0]: tuple(map(float, parts[1:]))
        for line in lines[1:] if (parts := line.split("\t"))
    }


class EpochBridgeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        for path in (RLIB, DEPS, C19, C21, INPUTS / "config.cfg", INPUTS / "checkpoint.txt"):
            if not path.exists():
                raise RuntimeError(f"required pinned native input missing: {path}")
        cls.tempdir = tempfile.TemporaryDirectory(prefix="c21_epoch_bridge_")
        cls.bin19 = Path(cls.tempdir.name) / "c19_rhs"
        cls.bin21 = Path(cls.tempdir.name) / "c21_epoch_rhs"
        for source, binary in ((C19, cls.bin19), (C21, cls.bin21)):
            subprocess.run([
                "rustc", "--edition=2021", "-O", str(source),
                "--extern", f"rei_microphysics={RLIB}",
                "-L", f"dependency={DEPS}", "-o", str(binary),
            ], check=True, capture_output=True, text=True, timeout=120)
        cls.a0 = float((INPUTS / "checkpoint.txt").read_text().splitlines()[1].split()[0])

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tempdir.cleanup()

    def test_c19_parity_at_checkpoint_scale(self) -> None:
        old = invoke(self.bin19, *GAS_AND_PHOTO)
        new = invoke(self.bin21, f"{self.a0:.17e}", *GAS_AND_PHOTO)
        self.assertEqual(old.returncode, 0, old.stderr)
        self.assertEqual(new.returncode, 0, new.stderr)
        old_schema, old_rows = rows(old.stdout)
        new_schema, new_rows = rows(new.stdout)
        self.assertEqual(old_schema, "C19_NATIVE_RHS_V1")
        self.assertEqual(new_schema, "C21_NATIVE_RHS_EPOCH_V1")
        for key, values in old_rows.items():
            self.assertEqual(new_rows[key], values, key)
        self.assertEqual(new_rows["EVAL_A"], (self.a0,))

    def test_epoch_density_cmb_and_photo_rate_scaling(self) -> None:
        a1 = self.a0 * 1.001
        at0 = invoke(self.bin21, f"{self.a0:.17e}", *GAS_AND_PHOTO)
        at1 = invoke(self.bin21, f"{a1:.17e}", *GAS_AND_PHOTO)
        self.assertEqual(at0.returncode, 0, at0.stderr)
        self.assertEqual(at1.returncode, 0, at1.stderr)
        _, r0 = rows(at0.stdout)
        _, r1 = rows(at1.stdout)
        expected_density_ratio = (self.a0 / a1) ** 3
        for key in ("NH_CM3", "NHE_CM3"):
            self.assertTrue(math.isclose(r1[key][0] / r0[key][0], expected_density_ratio, rel_tol=5e-15), key)
        self.assertTrue(math.isclose(r1["TCMB_K"][0] / r0["TCMB_K"][0], self.a0 / a1, rel_tol=5e-15))
        for before, after in zip(r0["PHOTO_EVENTS"], r1["PHOTO_EVENTS"]):
            self.assertTrue(math.isclose(after / before, expected_density_ratio, rel_tol=5e-15))
        self.assertTrue(math.isclose(r0["TEMP_K"][0], r1["TEMP_K"][0], rel_tol=5e-15))

    def test_rejects_invalid_epoch(self) -> None:
        before = invoke(self.bin21, f"{self.a0 * 0.999:.17e}", *GAS_AND_PHOTO)
        outside = invoke(self.bin21, "3.0e-1", *GAS_AND_PHOTO)
        nonfinite = invoke(self.bin21, "nan", *GAS_AND_PHOTO)
        self.assertEqual(before.returncode, 2)
        self.assertIn("PRECHECKPOINT", before.stderr)
        self.assertEqual(outside.returncode, 2)
        self.assertEqual(nonfinite.returncode, 2)
        self.assertIn("NONFINITE", nonfinite.stderr)


if __name__ == "__main__":
    unittest.main()
