# Source-verified hydrogen excitation diagnostic

This additive node resolves the unavailable SW91 Table3 column assignment in C22B. It supplies a separate H1s→2s/2p coefficient and analytic temperature slope, with NaN/False outside2000–1e8K. It does not alter any completed C21O/C22A/C22B source or trajectory.

Run `OPENBLAS_NUM_THREADS=1 python verify_diagnostic.py --out results` in this directory. NumPy is required; the high-precision reference uses Python's standard decimal module. Output creation is exclusive. Verification uses80-digit evaluation and checks energy pairing and the original piecewise boundaries. It is not an independent atomic-scattering validation.

The coefficient is a primary-paper analytic reconstruction, not extraction from a plotted curve. Low-temperature coverage below2000K, higher-n excitation, He/Li excitation, optical-depth feedback and an active thermochemical ODE remain separate tasks.
