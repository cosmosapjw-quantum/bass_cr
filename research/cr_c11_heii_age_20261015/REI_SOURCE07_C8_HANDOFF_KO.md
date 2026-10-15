# REI SOURCE07 C8 수신자 계약: HeII 입자수·광가열 종별 8-모멘트 age 압축

## Actual source identities (read-only)

- Owner rei_bianchi HEAD 0fcb2dddf5de6b583c2e00f150abff0b2afb6315,
  branch codex/rux-science-delivery-20261014.
- Source research/source07_c1_baseline_20261014/q_emission_baseline.py,
  SHA-256 43f7805703f08516b2b4b8e686b097b1c38e2140ac06b556e7de07159cf42b06.
- Source research/source07_c8_age_compression_20261015/experiment.py,
  SHA-256 f8a7d7ecbf7b839ef138c024384bed0fa16ec6889a332ef2ade2dc7c9d47b72b.
- Scenario research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json,
  SHA-256 07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696.
- New bass_cr supplier is additional code in a separate worktree. It does
  not edit original Rust, SOURCE07 C7/C8 or AX08 source and does not replay
  the user's previous long AX08 jobs.

## Receiver API contract to carry forward

Source-age response has eight scalar moments per time/ray/gas:

    (N, E_phys, N_HI, N_HeI, N_HeII, Q_HI, Q_HeI, Q_HeII).

N and N_species are photon counts PER SOURCE-EMITTED PHOTON; the
physical source H-normalization is an external owner multiplier, and
the radiation R*J angular frame conversion is applied only once by
the owner. E_phys and Q species are eV per emitted photon. n_HI,
n_HeI,n_HeII are proper cm^-3. dt is a proper duration in seconds.
For a single photon E_phys, tau_j=c dt n_j sigma_j(E_phys), and
N_j = (tau_j/tau) * (1-e^-tau); energy Q_j=N_j(E_phys-I_j).
Thresholds of Verner fit and physical binding energies are not
interchangeable. The new source can be evaluated for nonzero HeII
receiver density, unlike the prior owner zero-HeII benchmark.

Use nonnegative age weights normalized to the owner source history,
and use a separate age/source identity for arbitrary hardened spectra.
Neither a full broadband spectral law nor true child q-cell moments
can be reconstructed from the parent N,U_ref alone.

## Admission contract: not yet passed

Required before any production attachment:
1. Actual proper source emissivity vs emission epoch and assigned ray
   identities/geometry with photon-number/energy ledger.
2. Evolving H/He/electron/T receiver and independently recomputed
   photoevents; matched continuous-integral reference and error budget.
3. Strict uncertainty budget for source age and opacity holdout,
   explicit HeII event/heat sensitivity and ionization threshold
   crossing; HeII fraction and HeIII equations must be coupled by
   an authorized owner integration.
4. Positive/number/energy/temperature conservation and real memory
   and CPU comparisons at matched accuracy.
5. Owner SOURCE07 C8 and AX08/AX11/AX12 gates, current code revision and
   independent reproduction. This supplier's 5.43e-10 is NOT a uniform
   opacity bound, full history error, or radiation solver speedup.

Existing other-lane separation:
- H+ + H(1s) resonant capture in bass_cr R3Mxx changes label/identity
  of ion and neutral but not HII abundance by itself. Do not put its
  unconverged 100 keV/u capture cross section in the H/He
  photoionization reaction law.
- BASS_HE high-temperature Case A atomic provider uses distinct domain
  and does not supply the missing HeII age/opacity function.
- Existing SOURCE07 C10 source-subcell supplier remains valid for the
  originally specified fresh blackbody source; not generic for
  arbitrarily hardened radiation.

Next reusable action: an isolated owner Rust C8 prototype may read a
versioned 8-moment source/age input only after the above scientific
conditions are sufficiently established. Owner's existing 36-age
reference should be retained as an independent oracle.
