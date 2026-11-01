# BASS-CR / REI IGM: original-published H+ + H CX Table 2 and conditional momentum–energy moment bridge

**Scientific status (2026-11-01):** LITERATURE_SUPPORTED seven-point CX TOTAL cross-section benchmark and **48 published sparse quantum DCS values** from 2016 Table 1; DERIVED Maxwellian kinetic moment identities; **26/26 Python regular and 26/26 optimized local scoped tests**; **FULL ORIGINAL 1301-energy/768-angle QUANTUM DCS FILES NOT_RETRIEVED**; **JOINT ELASTIC+CX SPIN-VALIDATED COLLISION KERNEL NOT_AVAILABLE**. Only a source-verification and physics-derivation gate, NOT another 192-row fitted atlas or IGM production operator.

## 1. Immutable owner and mission relation

- Local owner: `cosmosapjw-quantum/bass_cr`. Immutable starting PR #155 `9674159a5c123b87f3ff17ee2340830f64e4147a`; #154 `88b15fe3d6a0457d8bf63eba5b815da99d2e39b1`; #153 `ac2ed86c8b59fe7c7b5e78b0716c6c4d4677072e`.
- Original BASS193/REI source PR #311 `63052797e382b438ef375e8389f539118a7e2a0c`, private source ZIP SHA256 `4f2682e5885040fa69f0fe05095505cb7724b2d84c4707af8e1a78c8db41cb52`. Not included in public git; its actual content is **not** used or re-run by the present unit.
- REI concurrent PR #348 `fcc90939b6b7cc842fae65d5a0ffbb69a3ec3120` and newer #349 `1605236b8172db411d862caa219322d6af6953b1` are read-only. #349's F08 S0 proper-electron history is a DIFFERENT source and clock from the PR #311 BASS193 source. No transfer or blending is established.
- Central REI DAG **28/88 REPORTED, +0**; working **33/88 REPORTED, +0**; BASS-CR extension **0/3, +0**. CR-OFF remains independently valid, no REI mutation, no merge, no force push, PRODUCTION HOLD and auto-next false. Explicit existing PR #152 priority throttle applies.

## 2. Original peer-reviewed primary source and exact source scope

D. R. Schultz, S. Yu. Ovchinnikov, P. C. Stancil and T. Zaman, *Elastic, charge transfer, and related transport cross sections for proton impact of atomic hydrogen for astrophysical and laboratory plasma modeling*, J. Phys. B **49** (2016) 084004, DOI **10.1088/0953-4075/49/8/084004**, §3.3, Tables 1–2 and Appendix.

- Original author calculation 1301 centre-of-mass energies in [10^-4,10^4] eV, both elastic and CX integral and differential cross sections; data posted to the University of Georgia atomic-molecular database, cited in paper Appendix and reference [36].
- The accessible original PDF's **Table 2** gives 7 numerical *total CX cross sections for the distinguishable-particle approach*, manually transcribed into `PRIMARY_CX_SCHULTZ2016_TABLE2.csv`; this is NOT the unretrieved raw angle-resolved data. Unit conversion uses the Appendix's rounded `a0^2 = 2.8003e-17 cm^2`, not an invented precision.
- From E_cm [1e-4,1e-3,1e-2,0.1,1,10,100] eV, corrected 2016 CX values [4047,1154,327.2,223.2,162.2,121.0,85.10] a0². The earlier omitted-l=0 values [3640,1111,322.5,222.7,162.2,121.0,85.10] a0² and 2008 figures are recorded distinctly. E=1e-4 difference: corrected/omitted − 1 = **11.18%**.
- Crucial corrected-source notice: §3.3 identifies older Krstić–Schultz spin-exchange partial-wave expressions requiring division by 4 and angular argument replacement `P_l(cos(pi-theta))`, and missing contributions to earlier transport expressions. This is an original-publication correction and must prevent mixing old/new formula families.
- For *indistinguishable protons*, coherent interference of direct/exchange channels prevents naive addition of the distinguishable elastic and CX event cross sections at low energy; nuclear-spin exchange/hyperfine population is not supplied or verified here. This is a **scope-specific incompatibility**, not an impossibility theorem.
- Original DCS files are *preweighted angular data*: `f(theta)=2*pi*sin(theta)*dSigma/dOmega` in a0² per rad, 768 angles, theta in [0,pi]. Thus `sigma_total=integral f(theta)dtheta`; charge-angle `sigma_mt=integral (1-cos(theta_ch)) f(theta_ch)dtheta_ch`; viscosity `integral sin^2(theta_ch) f dtheta`. Adding a second `sin(theta)` is physically WRONG. For CX nuclear-labelled theta, `cos(theta_charge)=-cos(theta_nuclear)`; then the momentum weight becomes `1+cos(theta_nuclear)`.
- Original source retrieval attempted via official UGA link on this machine but remote HTTPS timed out. Original raw CX DCS and 2023 elastic DCS remain NOT_RETRIEVED; no substitute interpolation is silently substituted.

## 3. Actual published seven-point numeric crosswalk to previously frozen 2025 A4

Masses and `sigma_CX,A4(g)` inherited **unchanged** from PR #154 source module `source_cx_screen.py`: `mu=m_p*m_H/(m_p+m_H)`, `E_cm=mu*g^2/2`. Existing fit support g = 3–200 km/s is E_cm = **0.02349585857–104.42603810 eV**. Exactly four published points (0.1, 1, 10, 100 eV) lie in this speed window.

| E_cm [eV] | g [km/s] | published CX [a0²] | A4 / published − 1 |
|---:|---:|---:|---:|
| 0.1 | 6.19 | 223.2 | -4.96% |
| 1 | 19.57 | 162.2 | +0.40% |
| 10 | 61.89 | 121.0 | -0.77% |
| 100 | 195.72 | 85.10 | -1.53% |

At 1e-4 eV, **outside** the admitted fit's speed support, direct A4 extrapolation is ~90.14% **below** the original published total-CX value. Therefore the pre-existing velocity cutoff is physically substantive. These are **total-event** comparisons, not independent verification of angular momentum transfer, Model-6 A7, species drift or thermal energy transport.

## 4. Constructive mathematical derivation of the conditional joint first moments

Define physical local orthonormal ion-neutral frame and masses `m_i,m_n>0`, `M=m_i+m_n`, `mu=m_i*m_n/M`, `g=v_i-v_n`, `V=(m_i v_i+m_n v_n)/M`. For **elastic energy-conserving resonant exchange in ground-state channel and a valid charge-labelled DCS** `dSigma(g,chi)`, define `sigma_mt(g)=integral_(Omega_ch)(1-cos chi) dSigma`. This is a definition only until the quantum spin/charge convention is validated.

Under isotropic azimuthal average the collision impulse to the ion is `Delta p_i=mu(g'-g)`; the per-collision kinetic energy transfer is `Delta E_i=V dot Delta p_i` because `|g'|=|g|`. Hence

`R_i = -mu*n_i*n_n <sigma_mt(g)*g*g_vector> = -R_n`,

`Q_i = -mu*n_i*n_n <sigma_mt(g)*g*V dot g_vector> = -Q_n`.

The angle-integrated energy transfer **needs no new independent cross-sectional angular weight** for this strictly energy-elastic, isotropic, two-body closure, but still needs original spin-valid `sigma_mt(g)` and actual species distribution functions. This is the useful constructive physics bridge, NOT a source-validated temperature evolution.

For independent Maxwellians `f_i(v_i),f_n(v_n)` with mean drifts `u_i,u_n` and possibly different temperatures, define `U=u_i-u_n`, `V0=(m_i u_i+m_n u_n)/M`, `B=k_B(T_i/m_i+T_n/m_n)`. The conditional Gaussian identity is

`E[V | g] = V0 + eta(g-U)`,  `eta = k_B (T_i-T_n)/(M*B)`.

Therefore, for `A=<sigma_mt*g*g_vector>` and `J=<sigma_mt*g^3>` under the full relative distribution,

`Q_i = V0 dot R_i - mu*n_i*n_n*eta*(J-U dot A)`,

exact within the **assumed Gaussian species distributions, elastic kinematics, isotropic scattering and valid sigma_mt**, not a quantum-spin result.

At common reference temperature `T`, `a²=2k_B*T*(1/m_i+1/m_n)` and small `|U|/a` and `|DeltaT|/T`,

`K_mt(T) = [2/(3a²)] * <sigma_mt(g)*g^3>_(U=0,Ti=Tn=T)`, unit cm³/s;

`R_i=-mu*n_i*n_n*K_mt*U + O(U³,DeltaT*U)`;

`Q_i=V0 dot R_i - [3 mu k_B/M]*n_i*n_n*K_mt*(T_i-T_n) + higher-order mixed/thermal corrections`;

`R_n=-R_i,\ Q_n=-Q_i`.

Internal energy sources are `S_i=Q_i-u_i dot R_i`, `S_n=Q_n-u_n dot R_n`; combined heating `S_i+S_n=-U dot R_i=mu*n_i*n_n*K_mt*|U|² >= 0` at the retained order. At zero drift, the ion cools for `T_i>T_n` with exact opposite neutral heating. For constant `sigma_mt` the earlier 4/3 Maxwell factor remains valid. Linear relative velocity and temperature relaxation rates are

`lambda_U=mu*K_mt*(n_n/m_i+n_i/m_n)`;

`lambda_T=(2mu/M)*K_mt*(n_i+n_n)`.

For `m_i=m_n` these are identically equal, `K_mt*(n_i+n_n)/2`. Wolfram algebra confirmed this equality and the heat prefactor cancellation (CAS output zero), while executable tests independently check conservation and limiting values.

**Approximation caution:** finite Bianchi I tilt, nonzero internal excitation, source-dependent anisotropic velocity distribution, hyperfine populations or charge-transfer kinematics beyond the elastic equal-channel closure invalidate transport use until the collision operator is reconstructed. A Maxwell rate fit does not itself infer ion-neutral temperatures or tilts.

## 5. Coding output, verification and hostile review

- `primary_source_and_moments.py`: original 7-point table read and existing A4 crosswalk, input-validation, explicitly framed PREWEIGHTED angular moment quadrature for **future** raw DCS (no raw DCS silently supplied), and a local two-fluid momentum and energy exchange algebra with labelled units and approximation diagnostics.
- `PRIMARY_CX_2016_TABLE2_VS_A4_CROSSWALK.csv`: seven newly derived crosswalk rows, not 2016's original 1301 energy table and not 192 source epochs.
- `test_primary_source_and_moments.py`: 20 normal + 20 Python -O local PASS, including independently enumerated Table2 values, 4/7 window, forbidden low-energy extrapolation, isotope masses, isotropic angular moments, nuclear-vs-charge angle reversal, zero and negative tests, source fit comparisons, equality of the two relaxation eigenrates for equal masses, 128 random momentum/energy conservation draws. No original DCS scientific comparison test was run because DCS absent.

**Same-author hostile findings and resolution:**

1. Main issue: A7/A4 independent rounded fits are not a common exact quantum DCS, and their small bound violation at high speed is still real. **Not repaired by clipping.** No joint operator promoted.
2. Main issue: 2016 paper's older spin/angular formula corrections and coherent nuclear interference. **Retained as exact source convention blocker.** No claim that an elastic event plus CX event σ sums to the physical indistinguishable nuclear observable.
3. Main issue: applying preweighted DCS as if per steradian doubles Jacobian. **Code prevents this** by requiring named frame and taking `integral f(theta)dtheta`; synthetic counterexample tests cover it.
4. Main issue: time-dependent coupled energy transfer requires ion/neutral states, source proper-time clock and Bianchi frame, which PR #311 does not supply independently. **No new source/geometry invented.**
5. Meta-drift: original REI 28/88, optional 0/3, already two preceding optional units. **Stop after this one source-verification bridge**; next actions belong to central source/F05 and to actual DCS acquisition, not another fitted proxy atlas.

Code tests are **same-author** and not a distinct-author blind referee. Original quantum DCS absent; CAS check proves only conditional algebra; no native REI interval/cosmological observable was calculated.

## 6. Final status / stop condition

**Admitted scoped output:** one original-published seven-point total-CX datum/crosswalk, one reusable mathematically derived conditional joint first-moment mapping, one tested future-DCS parser. **Not admitted:** an original angle-resolved DCS data product, a nuclear-spin-consistent joint elastic+CX collision operator, an evolved REI two-fluid state, a Bianchi tilted IVP, any new 88-node DAG milestone or publication-quality cosmological prediction.

Proceed on this BASS-CR optional track ONLY when one or more real original DCS source files (Schultz et al. 2016 and 2023 elastic) with hash, energy/angle/unit provenance have been downloaded, or a matched REI source owner supplies the necessary actual ion-neutral distribution/tilt. Do not open further optional fit-only research loops. Original REI owner should pursue RUX02/RUX03 real source binding and physical source interval independently.


## 7. Primary Table 1: 48 actual quantum angular cross-section values (newer evidence)

The original Schultz et al (2016) PDF's **Table 1** prints 8 partial-wave truncations `ell_max = 100,200,400,600,800,1000,1200,1400`, at E_CM = 1 eV, for three angles `7.69075e-6 rad`, `1.56759 rad`, `3.14158 rad`. For each angle it reports distinguishable elastic ELD and charge-transfer CT values of `2*pi*sin(theta)*dSigma/dOmega` in atomic-area units. Exactly **8 x 3 x 2 = 48 original published angular DCS numbers** are transcribed in `PRIMARY_DCS_SCHULTZ2016_TABLE1_E1EV.csv`; `primary_table1_dcs_samples.py` unfolds them into `PRIMARY_DCS_SCHULTZ2016_TABLE1_SAMPLES_48.csv`, including exact angle labels and source scope.

New numerical source facts:
- Extreme-forward ELD at theta=7.69075e-6: `6.951 -> 12.12` (ell100->1400), relative **+74.36%**; even ell1200->1400 `11.94->12.12` **+1.51%**. This angle cannot be declared converged to percent-level from these published samples.
- Backward CT at theta=3.14158: `0.9539 -> 1.024` (+7.35% across ell100->1400), equal to the displayed precision from ell200 upward.
- Mid-angle CT: `5.568 -> 5.252` (-5.68% across ell100->1400). Angular convergence depends strongly on channel and angle, so no common truncation-error claim is warranted.
- **No angle integral is performed from only three isolated angles.** These original published values partly resolve the "no quantum DCS at all" information gap but do not constitute, replace or reproduce the original 768-angle per-energy author data and its cross-section moments.

`test_primary_table1_dcs_samples.py` independently verifies all 48 original printed values, source angles, number of original points, nonconvergence diagnostic, and explicit no-fake-integration status. The amended scoped suite: **26/26 regular and 26/26 Python -O PASS**. Raw UGA full-DCS download still blocked by the site connection/cache-miss, which is an input acquisition blocker rather than a mathematical no-go.

The UGA provider currently associates 2016 below the first electronic excitation ~10.7 eV with 2023 updated *elastic* scattering above threshold; higher-energy mixed-source use requires explicit cross-source conventions. It does not by itself validate a combined CX+elastic spin-aware operator. Original REI source physics remains independent.
