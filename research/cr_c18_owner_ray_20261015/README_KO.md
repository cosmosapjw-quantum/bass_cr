# C18: genuine AXBI Rust checkpoint -> H/He photoevent + thermal input

Parent bass_cr C17 commit 1c15983e86909c44620201f2da2a63dddef6b2e1.
Read-only rei_bianchi commit 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.

This is a SOURCE07 owner-compatible native photon-stock adapter.
It reads actual AXBI_CHECKPOINT_V2 files through the original Rust
Driver::read_checkpoint, not a manufactured ray photon distribution.
Cases: FLRW ZERO q=0,a=.08873655 and Bianchi-I SHEAR_PLUS
q=.01,a=.06657701. They are at DIFFERENT physical times.

Owner Rust exports its exact 8 rays x49 energy-node stocks,
Verner HI/HeI/HeII cross sections, current ray J/mu directions
and source-emission rates projected to the original energy nodes
using public Driver::deposit with source angular normalized
count_fraction*J. The J weight is not applied again in Python.

C17 then uses these real native packet/source rates at frozen
proper gas and energy for a bounded local dt=1e10 proper seconds,
calculating positive species photoevents, bindings, photoheats
and number/energy ledgers per original hydrogen nucleus.
Native owner_photo_rhs.rs passes photo gamma per absorber [s^-1]
and heat per absorber [erg/s] into the real igm_thermal::igm_point_rhs
at h=0, as in owner AXBI chemical_stage, and exports original
H/He collisional/recombination/thermal rate components.

Useful numerical results and source SHA are in results/,
OWNER_LOCK.json, docs/THEORY_KO.md and NEXT_DAG.json.
Do not identify this local fixed-gas adapter with full owner
Backward-Euler time evolution, age-history photon ray transfer,
or completed reionization xHI/HeII/Tgas(z) solutions.

Reproduce from C18 bass_cr branch root:
    export REI_BIANCHI_ROOT=/home/cosmosapjw/Dropbox/bianchi/rei_bianchi
    export C18=$PWD/research/cr_c18_owner_ray_20261015
    export PYTHONPATH="$C18/src:$PWD/research/cr_c17_species_20261015/src:$PWD/research/cr_c16_endpoint_20261015/src:$PWD/research/cr_c15_duhamel_20261015/src:$PWD/research/cr_c14_recomb_order_20261015/src:$PWD/research/cr_c13_transport_20261015/src:$PWD/research/cr_c12_physical_age_20261015/src:$PWD/research/cr_c11_heii_age_20261015/src"
    export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
    bash "$C18/src/run_native.sh" "$REI_BIANCHI_ROOT" "$PWD"
    python3 -m pytest -q -p no:cacheprovider "$C18/tests"
    python3 "$C18/src/owner_adapter.py" --zero "$C18/results/AXBI_ZERO_native.tsv" --plus "$C18/results/AXBI_PLUS_native.tsv" --out /tmp/C18_NATIVE_HHE.json

Rust CARGO_TARGET_DIR goes only under the isolated bass_cr worktree.
Original rei_bianchi files are read-only; no local Codex or native
subagent tools are used.
