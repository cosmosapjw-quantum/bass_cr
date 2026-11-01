# REI F05: original H excitation cooling versus source-backed H I 1s→2p (theory checkpoint)

2026-11-01; BASS-CR branch only, original REI F05 owner read-only. Parent BASS-CR PR161 exact a555eeb75eae79a5b05ee9054323c3ce06e3075d. Accepted REI tick 160/131072 only; tick161 preview NONAUTHORITATIVE. Central 28/88, working 33/88, optional BASS-CR extension 0/3, all deltas zero. Production HOLD / CR-OFF / no merge / no REI mutation.

## R1–R3: actual physical source and objective

Original private owner F05 46,080-cell source preview SHA256 713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d. Public BASS-CR PR161 derived 12,528-cell 1s→2p excitation source SHA256 09c564df9400b171617ce5006b2c7eee94085f8d321f8d41648fc9456cbd1628. Original REI owner PR356 head cc1929982948265f6d0b0f699353b3170ccd1792. The exact source-owned reduced interval RHS (locked by parent Case-B) ALREADY contains an H excitation cooling coefficient, and therefore no new 2p term may be simply appended.

Original reduced_interval_rhs.py:
  Lambda_H_legacy(T) = 7.5e-19 * exp(-118348 K/T) / (1+sqrt(T/(1e5 K))) [erg cm^3 s^-1].
  Qdot_H_exc_legacy = n_e n_HI Lambda_H_legacy [erg cm^-3 s^-1].
The original RHS computes d(log T)/dt = (heating-cooling-expansion)/u - (d n_particles/dt)/n_particles. This channel is within the existing cooling term. The original source code is not edited.

PR161 conditional 1s→2p effective collision strength:
  Upsilon(T) linearly interpolates the published Pradhan table at (5000,0.416), (10000,0.472), (15000,0.528), (20000,0.585) K.
  q12 = 8.629e-6 Upsilon(T) exp[-E12/(k_B T)] / [2 sqrt(T)] cm^3 s^-1.
  E12 = 10.198835887565243 eV.
  Lambda_2p = E12 q12, with energy converted via 1 eV = 1.602176634e-12 erg.
Scholz et al. (1990), DOI 10.1093/mnras/242.4.692; primary REI source is code-bound, not literature-derived. Source T in 5000–20000 K only (12,528 of 46,080 cells). Te=Tgas and neutral 1s fraction f1s=1 are conditional, NOT measured.

## R4–R5: physical partition and non-double-counting identity

At fixed original source tick160, with original proper V, H count N_H, electron N_e, HII fraction x:
  K_j = [N_H,j (1-x_j)] [N_e,j/V_j] [s^-1/(cm^3 s^-1)].
  P_legacy,j = K_j Lambda_H_legacy(T_j).
  P_2p,j = K_j Lambda_2p(T_j) = E12 R_exc,j.
  P_residual,j = K_j (Lambda_H_legacy - Lambda_2p).
  P_legacy = P_2p + P_residual EXACT algebraically under the frozen model.
The positive P_residual is a phenomenological remaining budget, NOT identified specifically with 2s, higher transitions, or true multilevel populations. A positive residual does NOT prove the legacy approximate cooling model accurately contains those channels.

For an ideal, single local matter thermal bath and fixed source particle counts,
  U_j = (3/2) (N_H,j+N_He,j+N_e,j) k_B T_j.
  epsilon_2p,j = P_2p,j dt / U_j; epsilon_legacy,j = P_legacy,j dt/U_j.
  d(log T)/dt contribution of 2p = -P_2p/U_j.
  d(log T)_{one-freeze-first-order} = -epsilon_2p.
This is source-local instantaneous response and NOT a time-evolved owner trajectory. Do NOT add epsilon_2p to original cooling: it is already included conceptually in legacy excitation cooling, and not safe to replace all legacy cooling with 2p alone. The 2p output photons are NOT escaping photons. Radiative trapping, local reabsorption, non-Maxwellian electrons, excitation to 2s/higher, and full four-group/line transport remain unresolved.

For each original positive interval source [T-,T+], [N-,N+] and fixed exact native V, construct positive interval enclosures for K, U, Lambda(T), and powers. Original 2p parent rates are independently bound on the same input. Strongly compare eps_2p,lower to max(abs(native_original_twohalf_delta_logT endpoints)), not solely midpoint; owner preview t161 remains NONAUTHORITATIVE.

## R6–R8: review, discrimination, and scientific decision

The naive earlier proposal to ADD PR161 Ly-alpha cooling to original REI F05 was rejected: original source already includes 7.5e-19 hydrogen excitation cooling. Simply REPLACE the legacy formula by 1s→2p is likewise unjustified because it discards unspecified other channels. This corrected partition is the bounded constructive unit.

Independent Wolfram check for Lambda_2p/Lambda_legacy at T=5000,10000,15000,20000 K: 0.6760564508233273, 0.5837199358663981, 0.5620253178553837, 0.5626059816131181. Positivity and partition must be verified for each ORIGINAL cell interval, not asserted from knots alone. Earlier one-pass frozen-source midpoint screen: total hypothetical 2p energy over dt approx 4.002924347883664e47 erg; supported bath U approx 2.7486360671295096e55 erg; per-cell eps max approx 1.08e-5, ratio eps/|native preview Delta lnT| > 1 in 180 source cells. These are BASELINE DIAGNOSTICS to reproduce, not approval or a missing-energy claim.

## R9–R10: computation and handoff

Implement an independent original-native 12,528-row sector partition with direct source-owned V, source intervals, protected SHA, legacy operator provenance, bounded [P_legacy,P_2p,P_residual], thermal-response screening and robust/non-robust materiality flags. Record aggregate and per-node data, tests, cold replay, hashes. Preserve original and parent unchanged; publish Draft stacked on BASS-CR PR161 only. Any native F05 owner change needs a separate owner acceptance path; keep CR-OFF, central 28/88 unchanged.

native_subagent: NOT_RUN (current callable inventory exposes no native delegation).
distinct_author_referee: NOT_RUN; same-author adversarial logic check above.
