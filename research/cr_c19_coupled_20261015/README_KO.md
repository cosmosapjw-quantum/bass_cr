# bass_cr C19: 실제 AXBI 광자 stock + coupled H/He 원자·열 진화의 국소 보존 검증

2026-10-15. Parent: bass_cr C18 `a6678e50b4d284e3188a74229a47736611f92d91`.
Original immutable `rei_bianchi` owner: `0fcb2dddf5de6b583c2e00f150abff0b2afb6315` (18/18 referenced file SHA-256 matched).
This is an **isolated companion research calculation**, not a mutation of the current production `rei_bianchi` PR #150 or its original checkpoints.

## Direct theoretical construction (R5, derived)

At one fixed proper-time epoch, for photon packet \(p=(r,i)\) and absorber species \(j\in\{\mathrm{HI,HeI,HeII}\}\),
\[
\lambda_{pj}(g)=c\,n_{\mathrm H}\,\alpha_j(g)\,\sigma_j(E_i),\quad
\alpha_j=(1-x_{\mathrm{HII}},\,Y(1-x_{\mathrm{HeII}}-x_{\mathrm{HeIII}}),\,Y x_{\mathrm{HeII}}),\quad Y=n_{\mathrm{He}}/n_{\mathrm H}.
\]
With constant-in-step original packet source \(s_p\ge0\), \(g\) held at its *implicit endpoint* and \(L_p=\sum_j\lambda_{pj}\),
\[
N_{p,1}=N_{p,0}\exp(-L_p \Delta t)+s_p\Delta t\,\varphi_1(-L_p\Delta t),
\quad \varphi_1(-u)=(1-e^{-u})/u,\quad \varphi_1(0)=1,
\]
\[
A_{pj}=\frac{\lambda_{pj}}{L_p}(N_{p,0}+s_p\Delta t-N_{p,1}),
\quad L_p=0\Rightarrow A_{pj}=0.
\]
The source-loss expression uses stable `expm1` and the small-\(u\) series from source-locked C14. Thus \(N_{p,1}\ge0\), \(A_{pj}\ge0\) for any admissible endpoint gas state, and *exactly on the discrete packet representation*:
\[
\sum_p(N_{p,1}+\sum_j A_{pj})=\sum_p(N_{p,0}+s_p\Delta t).
\]
Absorbed photoheat \(Q_j=\sum_p A_{pj}(E_i-I_j)\), with native physical binding thresholds \(I_j=(13.598434599702,24.587389011,54.41776)\,\mathrm{eV}\), not Verner fit thresholds \((13.60,24.59,54.42)\,\mathrm{eV}\).

Convert integrated events and heat to the original native per-absorber inputs:
\[
\Gamma_j=\frac{\sum_p A_{pj}}{\Delta t\,\alpha_j(g_1)}\ [\mathrm{s}^{-1}],\quad
h_j=\frac{Q_j\,\mathrm{eV\to erg}}{\Delta t\,\alpha_j(g_1)}
\ [\mathrm{erg\,absorber}^{-1}\,\mathrm{s}^{-1}].
\]
The Rust `igm_point_rhs` then supplies original collisional ionization, radiative+dielectronic recombination, excitation/free-free cooling, CMB exchange and thermal RHS, evaluated at this *same* endpoint state. The numerical gas equation is
\[
g_1-g_0-\Delta t\,F_{\mathrm{Rust}}(g_1;\Gamma(g_1),h(g_1))=0,\qquad
g=(x_{\mathrm{HII}},x_{\mathrm{HeII}},x_{\mathrm{HeIII}},w_{\mathrm{eV/H}}).
\]
Native temperature is recovered through the H/He ideal-gas EOS, not evolved as a second independent unknown. A damped finite-difference Newton solver enforces \(0\le x_{\mathrm{HII}}\le1\), \(x_{\mathrm{HeII}},x_{\mathrm{HeIII}}\ge0\), \(x_{\mathrm{HeII}}+x_{\mathrm{HeIII}}\le1\), \(w>0\); an iteration/restriction failure **HOLDs**, not clips the state.

The first and second helium ionization energies must be counted separately. Define the bound-ionization reservoir per original H nucleus
\[
B(g)=I_{\mathrm{HI}}x_{\mathrm{HII}}
       +Y\{I_{\mathrm{HeI}}(x_{\mathrm{HeII}}+x_{\mathrm{HeIII}})
              +I_{\mathrm{HeII}}x_{\mathrm{HeIII}}\}.
\]
For \(U_\gamma=\sum_p E_iN_p\), step-integrated CMB-to-gas input \(Q_{\rm CMB}\) and radiation escape \(Q_{\rm esc}\), the **local** Case-A/constant-volume energy ledger is
\[
(U_{\gamma,1}-U_{\gamma,0})-U_{\rm src}
+(w_1-w_0)+(B_1-B_0)+Q_{\rm esc}-Q_{\rm CMB}=0.
\]
Here \(Q_{\rm esc},Q_{\rm CMB}\) are original owner RHS rates multiplied by \(\Delta t/n_{\rm H}\) and converted to eV/H, not independently invented rates. Wolfram Language CAS checked four relevant analytic/helium-binding identities at zero residual (its direct limiting calculations emitted harmless indeterminate intermediate messages; the final identity was zero). **The discrete one-step conservation identity does not itself establish solution accuracy.**

## Local actual execution (C5–C8, scoped)

- Source identity: all 18 pinned original AXBI owner files verified byte-for-byte. TWO checkpoint cases use original Rust AXBI loader, genuine 8 rays × 49 energy nodes, native \(\sigma_{\mathrm{HI,HeI,HeII}}\) and source deposition; source angular \(RJ\) is *not* multiplied again.
- Native implementation: `src/c19_rhs.rs` compiled with the C18 byte-locked owner's `librei_microphysics.rlib`; Python `src/coupled.py` calls the original Rust point evaluator on every implicit residual and accepts only successful real native rate outputs.
- Fresh tests: **12/12 PASS** in local Ubuntu. Exact-time \(\Delta t=10^{10}\,\mathrm{s}\) two actual cases; \(\Delta t=10^9,10^{10},10^{11},10^{12}\,\mathrm{s}\) sensitivity and full-step vs two-half tests. See `TEST_RECEIPT.log`, `RESULT.json` and `SENSITIVITY.json`.
- Across the exploratory time-sensitivity sweep, absolute *local total-energy ledger residual* \(\le4.621\times10^{-16}\,\mathrm{eV/H}\). Endpoint gas feedback changes an individual species's fixed-gas photoevent count by at most **0.02186% (ZERO)** and **0.04001% (SHEAR_PLUS)** over the chosen \(\Delta t\) range, peaking at \(10^{12}\,\mathrm{s}\). This is a finite-step constitutive sensitivity, **not** a controlled same-time Bianchi contrast, spectral-resolution error bar or cosmological observable.

## Source and model exclusions

- ZERO \((q=0,a\simeq0.08873655)\) and SHEAR_PLUS \((q=+0.01,a\simeq0.06657701)\) **are different cosmological epochs**. No anisotropy contrast is inferred by subtracting them.
- Fixed within each local step: owner proper \(n_H,n_{He}\), scale factor \(a\), 49 discrete physical photon energies, per-ray source rate, cross sections. No evolving redshift-angle transport, photon source-age clock, true 3D radiative transfer or global cosmology.
- Original `igm_point_rhs` implements **Case A escape**, not on-the-spot/Case B. This is not full OTS/secondary reaction chemistry. The original owner uses a distinct backward-Euler photon update; the new exact endpoint-opacity exponential is a **proposed alternate local discretization** whose global accuracy remains OPEN. Do not replace production defaults without controlled convergence against latest PR #150.
- Current `rei_bianchi` PR #150 introduces covariant reference-energy transport, source subcells, conservative cut cells and isotope work. Its scientific gates must not be inferred from this earlier-owner C19 result.
- BASS_HE PR #64 conditional warm P01 and WU088_HH PR #89 high-\(\ell\) DtN bounds are kept separate: neither authorizes photo rates or production EoR solutions here.
- Old full-history numerical failures, PR #71 adaptive-grid shape-free spectral uncertainty, and AOCC capture NO_GO are untouched. `SOURCE07_C8_GLOBAL_REIONIZATION_ADMISSION=HOLD`.
- Only light local work performed; the registered NCP SSH root key login returned `Permission denied (publickey,password)`. No 64-vCPU/128GB NCP result or benchmarking is claimed.

## Reproduce on the authorized Ubuntu workstation

Set `W` to this bass_cr worktree and `R` to the **pinned** owner `rei_bianchi` checkout (verify all 18 SHA-256 in the C18 `OWNER_LOCK.json` before recomputing). With the C18 release `librei_microphysics.rlib` already compiled against this exact owner:
```bash
cd "$W"
mkdir -p "$W/../c19_native_target_20261015"
rustc --edition=2021 -O research/cr_c19_coupled_20261015/src/c19_rhs.rs \
 --extern rei_microphysics="$W/../c18_native_target_20261015/release/librei_microphysics.rlib" \
 -L dependency="$W/../c18_native_target_20261015/release/deps" \
 -o "$W/../c19_native_target_20261015/c19_rhs"
export PYTHONPATH="$W/research/cr_c19_coupled_20261015/src:$W/research/cr_c18_owner_ray_20261015/src:$W/research/cr_c17_species_20261015/src:$W/research/cr_c14_recomb_order_20261015/src"
export REI_BIANCHI_ROOT="$R"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 -m pytest -q -p no:cacheprovider research/cr_c19_coupled_20261015/tests
python3 research/cr_c19_coupled_20261015/src/coupled.py \
 --zero research/cr_c18_owner_ray_20261015/results/AXBI_ZERO_native.tsv \
 --plus research/cr_c18_owner_ray_20261015/results/AXBI_PLUS_native.tsv \
 --native "$W/../c19_native_target_20261015/c19_rhs" \
 --owner-root "$R" --out /tmp/c19_replay.json --dt 1e10
```
The `C18 owner_adapter` imports `C17 species_events` and `C14 exponential_source`; never mix other owner commit checkpoint/source rates to chase a passing number. See `NEXT_DAG.json` for the one next physical task. Native subagents were not available for dispatch: `NOT_RUN`.

Primary methods: Mellema et al., *New Astronomy* **11** (2006), 374, DOI [10.1016/j.newast.2005.09.004](https://doi.org/10.1016/j.newast.2005.09.004); Mirocha et al., *ApJ* **756** (2012), 94, DOI [10.1088/0004-637X/756/1/94](https://doi.org/10.1088/0004-637X/756/1/94); Norman et al., *ApJS* **216** (2015), 16, DOI [10.1088/0067-0049/216/1/16](https://doi.org/10.1088/0067-0049/216/1/16). Method motivation is literature-supported; this C19 coupled exponential+BE equation and its numerical measurement are **derived/implementation-verified locally**, not copied numerical results.
