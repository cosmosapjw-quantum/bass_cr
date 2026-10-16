# C21 common-q and source-age photon-chemistry interface: sandbox research unit

**Status:** `SANDBOX_LIGHT_PYTHON_PASS`; 21 new focused pytest cases; production Rust/NCP, full dynamic chemistry and EoR `NOT_RUN` / `HOLD`. The user-reported NCP C21 bridge commit `807a46029cd2ebca16ab58cc3d92669277be3c00` was not available in the GitHub repo branch inventory as of this unit and was not edited, fetched or falsely certified.

## Verified upstream identities (2026-10-16 KST)

- `bass_cr` C19 [PR72](https://github.com/cosmosapjw-quantum/bass_cr/pull/72), `e91ffe368c4e6db64c4b6c5962566302a33402b6`. Original native `igm_point_rhs` frozen-epoch coupled gas bridge: `research/cr_c19_coupled_20261015/src/coupled.py`, GitHub blob `0d18b781b9eee7c69358a125fd54504de2f794a5`.
- `bass_cr` C20 [PR74](https://github.com/cosmosapjw-quantum/bass_cr/pull/74), `caf587b3edf4e27d038c6a918419be498d7d389c`. True C20 original Rust source file `research/cr_c20_original_recovery_20261016/src/c20_native.rs`, GitHub blob `ee9c198d77ceedbbe6cda34d0053b56fff96b1ea`, native original file SHA-256 `13b6bc6fd3279d6b90f95baccf7bae20bbca838ee1eb83583c22071411c64de0`.
- `rei_bianchi` [PR150](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/150), observed HEAD `4e2f0682fb605c6aa940bd756d9869e67b6ded0b`. `rust/rei_microphysics/src/axbi_covariant_transport.rs` GitHub blob `9915d05a00f9c2ad9e0346a1e61ba1d2f37822d3`. `rust/rei_microphysics/src/axbi_driver.rs` GitHub blob `02c6e82c2265f238e5ff77abab1909028e3aa3c2`.
- `rei_bianchi` [PR157](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/157), native photo/Grackle owner split reference, `710f08b2bebaefbd6a28690d450d759877053ebb`.
- `BASS_HE` [PR70](https://github.com/cosmosapjw-quantum/BASS_HE/pull/70), `45b940f1d190713eb4c15bd5560112b6c542c9e4`: total-H rather than HI-only density; two-gate Newton stopping; source-age native 12/12 matrix but time convergence not established.

## New constructive mathematics

Conventions: FLRW, `x=ln a`, proper seconds `dt=dx/H(a)`, photon counts per **total** hydrogen nucleus, energy eV/H, native opacity cm^-1; `a_*=1/21`. No Bianchi tilted extension.

### Canonical photon momentum mapping

The owner `CovariantTransport::ray_geometry` takes reference geometry `a_*` and current geometry `a`, with photon redshift scale `R=a_*/a` in FLRW. `CovariantTransport::inventory` evaluates physical energy `U_phys=R U_ref` and its `inject` stores physical birth-energy `u/R` as reference first energy moment. The earlier C20 `q20=a E_phys` differs by a constant reference normalization:

`q_PR150 = q20/a_* = 21 q20`, `q20=a_* q_PR150`, `E_phys=q20/a=(a_*/a)q_PR150`.

If C20 stores `(N,U20,lo20,hi20)`, its exact reference-cell equivalent is `(N,U20/a_*,lo20/a_*,hi20/a_*)`. The bin support must be converted too. **These are coordinate identities, not spectrum reconstruction or native end-to-end parity.** Same photon number `N` is kept, and native `q_ref` is a *different* signed Bianchi parameter unrelated to canonical photon q.

### Common ionization rate and heat units

Let `Y=nHe,total/nH,total` and `(x,y,z)=(xHII,xHeII,xHeIII)`. The number of available absorbers per total H is

`alpha=[1-x, Y(1-y-z), Y y]`.

For one finite **proper-time** slab of duration `dt_s`, if species photon losses per total H are `A_i` and excess physical photoheat is `Q_i` eV per total H, the original native photo input must be

`Gamma_i=A_i/(alpha_i dt_s)` s^-1, `heat_i=Q_i * EV_ERG/(alpha_i dt_s)` erg per absorber per s,

with exact zero input for absent species and `nH,total(a)=nH0 a^-3` to recover volumetric events. C21 evolving-epoch bridge owns `Tcmb=2.7255/a`, and calls native `igm_point_rhs` with `h=0` only when geometric cooling is accounted elsewhere. Never confuse neutral HI density with the total-H denominator. PR157 provides an independent point-operator comparison for the actual native source.

### Independent analytic photon oracle

For the **manufactured** cross section `sigma_i(E)=sigma_i,t (E/Efit_i)^-3` when `E>=Efit_i`, and fixed gas fractions `alpha_i`, `E=q20/a` and `nH(a)=nH0 a^-3` imply

`lambda_i=c nH(a) alpha_i sigma_i(E(a))=c nH0 alpha_i sigma_i,t (Efit_i/q20)^3`,

constant along a characteristic **until its species cutoff** `a_cut=q20/Efit_i`. Between exact cuts,

`N_{k+1}=N_k exp(-lambda_tot Delta t)`, `A_i= (N_k-N_{k+1}) lambda_i/lambda_tot`.

The continuous photon work is positive in FLRW expansion:

`W_gamma=integral_{ln(a_b)}^{ln(a_end)} E(x) N(x) dx`.

The absorption energy is `Q_i+I_i A_i`. Therefore a packet obeys

`E_b N_b = E_end N_end + sum_i[Q_i+I_i A_i] + W_gamma`.

The retained energy integral is performed in cumulative optical depth `u=lambda_tot (t-t0)` rather than blindly quadraturing near-zero-width stiff `x` boundary layers. First direct-x quadrature displayed an `~3.14e-12 eV/H` manufactured aggregate residual. The diagnosed repair produced `~3.26e-16 eV/H` for the same GL2 birth source at the same physical parameters, **without relaxing numerical gates**. The control uses `DOP853` in `u` against an independent `Radau` IVP in `x`; at `u>52` the omitted energy is bounded by `N E_left exp(-52)` in an expanding interval. This cancellation applies to the toy power-law only, **not** native Verner cross sections.

## Main actual numerical results

New `run_study.py` and `src/c21_reference.py` create `evidence/RESULT.json` deterministically up to floating/solver implementation. `nH0=1.90e-7 cm^-3` is an explicitly manufactured source fixture, **not a recovered owner density checkpoint**. The original MD14 redshift-dependent functional form and the original Verner/BB50K parameters are reused for the separate source response benchmark; no native Rust executable is run here.

### MD14 source birth-time quadrature against independent SciPy quad

| Δln a | midpoint N relative | GL2 N relative | midpoint final-U relative | GL2 final-U relative |
| --- | ---: | ---: | ---: | ---: |
| 0.02 | −3.22893513e-4 | −1.38879398e-8 | −4.86219809e-4 | −3.15076571e-8 |
| 0.12 | −1.15314748e-2 | −1.78381545e-5 | −1.72959407e-2 | −4.02991918e-5 |
| 0.20 | −3.15740091e-2 | −1.35464244e-4 | −4.70235476e-2 | −3.03704768e-4 |

Midpoint-vs-GL2 is a **different time quadrature contract**. Production PR150 midpoint injection is not automatically identical to C20's two birth nodes even when source rate functions match. The numbers are finite-interval test errors, not production EoR errors.

### Unpartitioned per-original-source-cell moment calculation: centroid vs positive GL8

Native `AxbiSource` has three fixed threshold-separated source regions with 16 geometric cells each (48 total). C20 uses Simpson32 first-moment centroids; PR150 `source_moments` uses positive GL8 for each native cell, which may undergo **additional splitting by reference-energy cell boundaries in production**. The local calculation compares only the unsplit source-cell instantaneous optically thin Verner coefficients, **not PR150's subsequent nonlinear closure/absorption**.

| Species | (centroid minus GL8)/GL8, photo coefficient | (centroid minus GL8)/GL8, excess heat coefficient |
| --- | ---: | ---: |
| H I | −5.960317518e-4 | +8.935899608e-4 |
| He I | −3.708947686e-4 | +1.846282425e-3 |
| He II | −5.828673784e-4 | +4.009671797e-3 |

The 16→32→64 native-source-cell refinement reduces these differences approximately by a factor of four at each doubling, as measured in `RESULT.json`. The actual individual centroid differences from Simpson32 vs GL8 are below 4e-8 eV, but nonlinear opacity/heat responses still differ. **Do not claim end-to-end PR150 parity or a certified continuum order from this source-only comparison.**

### Distinct positive spectra with identical N, U and [support lo,hi]

Original Verner HeII cross section at energies `(50,55,60)` eV, positive measures `A=(0.5,0,0.5)` and `B=(0.2,0.6,0.2)` both have `N=1`, mean 55 eV and true support [50,60] eV. Their sigma-weighted photo responses differ: `6.098214716783932e-19` vs `1.1695385626227697e-18 cm²`. This numerical counterexample explains why the owner explicitly treats `N,U,support` as a chosen closure, not a uniquely reconstructed spectrum. The fact of non-uniqueness is not presented as a novel strong no-go.

## Execution and evidence

```
cd C21_SANDBOX_COMMON_Q_20261016
python -m pip install numpy scipy pytest   # only if missing
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 python run_study.py
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 python -m pytest -q -p no:cacheprovider tests
```

Observed environment: Python 3.13 sandbox, NumPy 2.3.5, SciPy 1.17.0, pytest 9.0.2. Fresh targeted tests **21/21 PASS**. Wolfram Language independently returned `{0,0,0,0}` for energy mapping, first moment conversion, opacity cancellation and exact photon number conservation; this is scalar CAS, **not xAct**. `native_subagent: NOT_RUN` (no native stage worker exposed). Neither user workstation nor NCP was invoked for C21 in this research unit.

Historical NCP C21 3/3 RHS bridge checks in the user-provided status are reused as external reports, not independently re-run here. This code is a scientific adapter/reference, and its Python tests cannot certify the C21 Rust implementation.

## Selected literature and why it matters

- Mellema et al., C2-Ray, 2006, [DOI 10.1016/j.newast.2005.09.004](https://doi.org/10.1016/j.newast.2005.09.004): photon-conserving absorption and time-averaged gas chemistry, physical inspiration but not an identical solver.
- Friedrich et al., C2-Ray helium/multifrequency extension, 2012, [DOI 10.1111/j.1365-2966.2012.20449.x](https://doi.org/10.1111/j.1365-2966.2012.20449.x): hydrogen-helium cross-section/photoheat coupling.
- Pawlik & Schaye, TRAPHIC multifrequency thermally coupled RT, 2011, [DOI 10.1111/j.1365-2966.2010.18032.x](https://doi.org/10.1111/j.1365-2966.2010.18032.x): frequency-resolved thermal bias of grey/one-moment approximations.
- Norman et al., fully coupled cosmic reionization numerical methods, 2015, [DOI 10.1088/0067-0049/216/1/16](https://doi.org/10.1088/0067-0049/216/1/16): stiffness and production coupling, which this sandbox does not claim to close.

## Next native integration boundary

1. Access/verify actual NCP local C21 RHS bridge commit `807a...` and PR150 latest HEAD; avoid changes to watcher locks and running REI full-history computations.
2. Convert **all four** photon state quantities N/U/lo/hi from q20 to reference `qPR150`, with birth-time `R(a_b)` and current `R(a)` separately.
3. Fix a common time step and source contract; input-source physical photon N/U (original Simpson32 centroid versus GL8) should be compared independently from transport solver response.
4. In native owner Rust `igm_point_rhs` use per-total-H mapping, per-absorber Gamma/heat and `h=0` only if geometry owns cooling. Enforce simultaneous implicit state and complete energy residual gates from BASS_HE HE23.
5. Implement finite short coupled run and independent time/source/angular/spectral refinement. Nonmonotone global C20/C21 convergence and full-EoR scientific gates stay `HOLD`.

See `CODEX_HANDOFF_KO.md`, `NEXT_DAG.json` and `evidence/RESULT.json`.
