#!/usr/bin/env bash
# C18 native owner source recompile and checkpoint validation
set -euo pipefail
ROOT="$1"
BASS="$2"
P="$BASS/research/cr_c18_owner_ray_20261015"
mkdir -p "$BASS/../c18_native_target_20261015" "$P/results"
export CARGO_TARGET_DIR="$BASS/../c18_native_target_20261015"
cargo build --offline --release --manifest-path "$ROOT/rust/rei_microphysics/Cargo.toml" --lib
for EXE in owner_ray_export owner_photo_rhs; do
 rustc --edition=2021 -O "$P/src/$EXE.rs" \
  --extern "rei_microphysics=$CARGO_TARGET_DIR/release/librei_microphysics.rlib" \
  -L "dependency=$CARGO_TARGET_DIR/release/deps" \
  -o "$CARGO_TARGET_DIR/$EXE"
done
ZERO="research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO"
PLUS="research/axbi_goal_20261014/report/full_progress_32d11e733155/snapshot_20261014T083357015083Z/SHEAR_PLUS"
"$CARGO_TARGET_DIR/owner_ray_export" "$ROOT/$ZERO/config.cfg" "$ROOT/$ZERO/checkpoint.txt" "$P/results/AXBI_ZERO_native.tsv"
"$CARGO_TARGET_DIR/owner_ray_export" "$ROOT/$PLUS/config.cfg" "$ROOT/$PLUS/checkpoint.txt" "$P/results/AXBI_PLUS_native.tsv"

# Recreate native full point RHS parity inputs and outputs with read-only Rust:
export PYTHONPATH="$P/src:$BASS/research/cr_c17_species_20261015/src:$BASS/research/cr_c16_endpoint_20261015/src:$BASS/research/cr_c15_duhamel_20261015/src:$BASS/research/cr_c14_recomb_order_20261015/src:$BASS/research/cr_c13_transport_20261015/src:$BASS/research/cr_c12_physical_age_20261015/src:$BASS/research/cr_c11_heii_age_20261015/src"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 "$P/src/verify_point_rhs.py" --owner "$ROOT" --results "$P/results" --rust-bin "$CARGO_TARGET_DIR/owner_photo_rhs"
python3 "$P/src/owner_adapter.py" --zero "$P/results/AXBI_ZERO_native.tsv" --plus "$P/results/AXBI_PLUS_native.tsv" --out "$P/results/OWNER_LOCAL_PHOTO_INPUT.json"
