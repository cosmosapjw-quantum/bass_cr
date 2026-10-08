"""Frozen external validator for the one-file target-only candidate patch."""
import subprocess
import sys


if __name__ == "__main__":
    raise SystemExit(
        subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "tests/test_r3m16_hdt.py"],
            check=False,
        ).returncode
    )
