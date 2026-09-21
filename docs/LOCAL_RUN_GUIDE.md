# Local run guide

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
pytest -q
```
For RTX 3090, optionally install the CuPy package matching the installed CUDA runtime and set `"backend":"cupy"` or leave `auto`.

## Mandatory smoke tests
```bash
python -m cr_repro.cli tdl --config configs/tdl_smoke_100kevu_b2.json --out runs/tdl_smoke
python -m cr_repro.cli aocc --config configs/aocc_smoke_100kevu_b2.json --out runs/aocc_smoke
```

## First physics run: TDL 100 keV/u, b=2 a0
```bash
python -m cr_repro.cli tdl --config configs/tdl_prod_100kevu_b2_baseline.json --out runs/tdl_100_b2
```
Restart is automatic from `state.npy/state.json` if config is unchanged. Use `--max-steps 50` for interruption-safe bounded chunks.

Then run dt, capture-plane and final-separation variants. Do not launch a full b-grid before the single-b observable identity and numerical refinements are inspected.

## First physics run: one-electron AOCC
```bash
python -m cr_repro.cli aocc --config configs/aocc_prod_100kevu_b2_baseline.json --out runs/aocc_100_b2
python -m cr_repro.cli aocc --config configs/aocc_prod_100kevu_b2_basis_large.json --out runs/aocc_100_b2_large
```

The AOCC implementation uses target-frame ETF k_T=0, k_P=v and the temporal projectile Galilean phase. It reports a metric projector onto negative-energy projectile pseudostates.
