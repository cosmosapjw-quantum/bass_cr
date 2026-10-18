# C21F R5: photon-number Radau의 실제 실패와 누적 optical depth 변수

2026-10-18. Parent bass_cr PR80 code 1ee8cb5a3377381de35b6b9a0e3b8dc1cfb12f41, delivery head 82c71000fccf0e353534080efbbf4eff7f31ac4c.

Backup-first intake: established Dropbox /bass_cr/C21 and Drive/Library bass_cr backup locations showed no new C21E native execution beyond the prior restore receipt. GitHub PR80 likewise retained native NOT_RUN. This is a scoped observation, not proof that unpublished NCP data do not exist. No remote terminal or NCP work is performed here.

## Observed defect
Original continuous Radau, original test gas at a0=.09, Delta ln(a)=1e-4, **unscaled Verner opacity=1**, ZeroMicro and the unchanged nine manufactured-energy cohorts throws RADAU_INTERNAL_NEGATIVE_PHOTON during an internal collocation iterate. Failure took 0.3775s in this sandbox. This is a numerical coordinate/domain failure, not negative photons in the exact physical solution. The negative-state guard is NOT removed or clipped.

## Exact change of variables
For a cohort of B_i>=0 photons/H born at x_bi, q_i=a_bi E_bi, x=ln(a),
N_i(x)=B_i exp[-tau_i(x)], tau_i(x_bi)=0,
tau_i'=sum_j k_ij(x) alpha_j(g)/H(x), k_ij=c nH0 exp(-3x) sigma_j(q_i exp(-x)).
Before birth its active mask is exactly zero and tau remains zero. No log(0) or artificial photon floor is needed. The source remains the same fixed impulse measure; this does NOT refine emission times or change energy weights.

Exact differentiation yields N_i'=-N_i tau_i' and (E_i N_i)'=-E_i N_i-E_i N_i tau_i'. Same species events, nonphoto microphysics, thermal/binding, escape/CMB, photon work and gas work can therefore be reused unchanged. Wolfram verified residuals {0,0,0}, nonnegativity True, relative photon perturbation exp(-delta_tau)-1=-delta_tau+delta_tau^2/2+... . This is a standard analytic attenuation coordinate, not a new opacity or physics claim.

## Accuracy and domain
Accepted tau must be finite, nonnegative and monotone for active cohorts. Radau's internal tau trials may cross zero; exponentiation remains positive and is an explicitly stated solver-coordinate extension, not clipping. Guard overflow. Finite floating-point underflow is recorded as representation loss, with an upper bound per packet; no positive tail is asserted resolved below floating precision. Gas state, native temperature domain, and physical energy gates remain independent. Radau component tolerances now carry optical-depth units and must be declared and independently refined; copying a photon-number atol has no same-norm implication.

## Selected output and checks
Implement an additive reference/runner on immutable C21E, replay the exact failure, compare number/hazard coordinates on overlapping well-resolved cases, verify analytic attenuation and transparent/source-birth limits, use independent tolerance refinement and conservation checks. Keep native Rust and NCP as NOT_RUN in this sandbox. Add per-lane failure preservation so one rejected comparator never erases independent completed results.

References: Mackey 2012 DOI10.1051/0004-6361/201117984; Friedrich et al.2012 DOI10.1111/j.1365-2966.2012.20449.x; SciPy Radau official documentation. They motivate accuracy checks, not this measured result.
