# Preserved first failure

The initial qualification exited 1. Its only failing numerical row was raw SDCS parity at `H: W=8700.257950402354 eV`, one part per million below the selected 4 MeV endpoint: `8.099279321817133e-10 > 2e-10`. All other rows and the eight initial tests passed.

The source uses a stable `log1p` interval. The independent comparator instead formed two logarithmic bounds whose subtraction loses relative width accuracy near the endpoint. The single allowed repair maps raw SDCS quadrature to the original linear K interval on `[0,1]`. An elementary constant-integrand width oracle and one targeted regression test check the repair. No source formula, sampling energy, threshold or scientific scope changes. Original `validate.py`, source/test hashes, `VALIDATION.json` and `FIRST_RUN.log` remain intact.
