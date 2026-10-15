# BASS_CR moment-shape-free C7 supplier

이 패키지는 `rei_bianchi` SOURCE07 C6의 **현재 q-cell N,U만으로 임의의 hardened spectrum 종별 photoevent/heat 값을 안전하게 감싸는 독립 실험**이다. Spectrum을 최대 entropy 분포라고 강제하거나 원래 BB50K로 되돌리지 않는다. Original parent PR69 source identity is preserved.

```bash
python verify_package.py
PYTHONPATH=src python -m pytest -q tests/test_moment_envelopes.py
PYTHONPATH=src python src/moment_benchmark.py --single 64 128 256 512 1024 --preview 10000
PYTHONPATH=src python src/cold_scaling.py --bins 512 --reps 2
```

Use `src/moment_envelopes.py::enclose_q_bins(ref_edges,N,Uref,R,proper_neutrals,proper_dt,nodes_per_branch=4)` per **one actual q ray and current proper clock**. Counts per original H; E/eV and Uref/(eV per H), cm^-3, seconds. Return event/heat shape `(3,2)` with lower and upper endpoints. Input must have nonnegative N,U, and U/N inside corresponding ref-q-bin. Topological fit threshold crossing is treated as a discontinuity; physically distinct binding energies are used only for heat.

The `vector_preview` is a fast, NONCERTIFIED floating presentation of precomputed hulls, not the authoritative Fraction+directed interval result. Certification here is conditional on the specified Verner fit/data constants and C9 sufficient derivative bounds, not on experiment/whole-cosmology numerical errors. Full backup source/tests and proof in REPORT_KO.md.
