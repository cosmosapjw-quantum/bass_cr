#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
sha256sum ATTRIBUTION_ARRAYS.npz
python -m unittest -v test_native_budget test_generic_budget_flow
python -O -m unittest -q test_native_budget test_generic_budget_flow
python native_budget.py ATTRIBUTION_ARRAYS.npz --c 0 --c '2162500209241577489/24519928653854221733733552434404946937899825954937634816' --c '2162500209241577489/12259964326927110866866776217202473468949912977468817408'
python verify_compact_witness.py
python plot_generic_frontier.py
