# PHYS02F cached scalar tail diagnostics

`NUMERICAL_ARTIFACT.json` contains raw early/tail moments, conditional moments, remaining-tail moments, retained signed variance, all raw and relative identity checks, source birth posterior weights and empirical selected model differences. `DECIMAL80_ORACLE.json` preserves independent 80-digit scalar arithmetic and independent mixture arithmetic. `PLOTTING_DATA.json` is the sole figure data source; its densities are kernel_per_s / H0.

The first targeted invocation passed four exact Fraction finite-measure, mixture, degenerate and malformed tests. The single actual offline analysis passed; exact argv, cwd, source/test/input hashes, wall time, exit and raw stdout/stderr are preserved. No failure or repair occurred. No G construction, pulse propagation, expm or prior suite rerun occurred.

At T = 316.8808781402895 years, selected early heat is about 6.39%; the remaining heat fraction is about 93.61%. Selected fullBED early conditional mean is 147.370 years, uncapped mean 14719.994 years, and conditional remaining-tail mean 15397.975 years. The low-energy birth column supplies 10.591% of eventual heat, 67.627% of early heat, 6.697% of tail heat, and 0.3783% of the uncapped first-moment contribution.

The displayed CDF joins only the saved 17 samples. No interpolation-based quantile is computed. Means refer to heat-normalized kernel delays and frozen finite-operator continuation, not particle lifetimes or cosmic history. Current-ramp ancestry is copied from the accepted saved result and is a distinct weighting. Mesh convergence, long-time bath validity and inherited gates remain unresolved. Analysis implementation does not own scientific acceptance.
