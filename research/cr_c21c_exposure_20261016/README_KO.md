# C21C: absorber-exposure-aware photon/native BE interface and source-age Radau oracle

2026-10-16 KST; research-only addition to `bass_cr` [PR76](https://github.com/cosmosapjw-quantum/bass_cr/pull/76), immutable head `172ca4c814b0b5bb05a03b509086e85f9cdd6138`.

## 새 실질 결과

1. **정확한 동적 흡수체 노출량**: `N'=A'=-kNA`에서 `I_A=∫A dt=max(A0-N0,0)Δt+k^-1 log1p(mφ)`; Wolfram differential/antiderivative/equal-population/initial four checks zero. 안정적인 `expm1/log1p/exprel` Python 코드, zero, equal, near-equal, extremely stiff species checks.
2. **원본 native rate 해석의 구분**: `Γ_exp=L/I_A`는 physical-time absorber-weighted mean. 원본 BE endpoint source로 같은 사건 수를 강제하려면 `Γ_BE=L/(Δt A_end)`; 다르면 반드시 별도 interface/solver 필요. `A_end=0,L>0`에서는 수학적으로 불가능하므로 HOLD, epsilon clipping 금지. `Γ_BE/Γ_exp=I_A/(Δt A_end)`은 absorber pure depletion에서 ≥1, HeII가 HeI에서 생성되면 <1도 가능.
3. **원본 H/He/Verner source-age 실제 계산형 제조 기준해**: 3 old photon stocks + 2 birth times × 3 positive source energies = 9 cohorts; fitted H/He photo cross section, cosmic proper nH∝a^-3, q=a_birth E, moving physical thresholds and independent SciPy Radau. Positive original MD14 *rate clock* but **explicit manufactured three-energy emission spectrum**, not original 48-cell source. Real time exposures `∫A_j(x)dx/H(x)` calculated independently and passed to `NativeRateBridge` with correct per-H/per-cm³ units.
4. **distinctive three-species finding**: At `Δln a=.025`, `opacity_scale=1e-3`, ratios endpoint/exposure = HI `1.0071856`, HeI `1.0419782`, HeII `0.8766731`. HeII replenishment invalidates naive pure-loss bound. Source-events/H=(.028136850194,.007549338308,.000496740465); energy ledger Radau ~`-1.85e-15 eV/H`.
5. **numerical experiment**: compare exact retained PR76 source-age Strang reactor with independent time-aligned Radau; 2,4,8,16,32,64,128 substeps per age interval errors `[7.9523e-4,3.8570e-4,1.1327e-4,2.9513e-5,7.7761e-6,1.9599e-6,4.9357e-7]`; last orders ~1.9883/1.9894. Six (Δln a,opacity) combinations n32→64 observed orders 1.975–2.000. No unjustified all-grid second-order claim.

## Tests and execution

```
python -m venv .venv
. .venv/bin/activate
python -m pip install numpy scipy pytest
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=src python -m pytest -q tests -p no:cacheprovider
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=src python src/compare_c21b.py --out evidence/REFERENCE_COMPARE_REGEN.json --n 2 4 8 16 32 64 128
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=src python src/run_scope_matrix.py --out evidence/SCOPED_MATRIX_REGEN.json
```

The complete standalone ZIP includes the exact SHA-pinned PR76 source in `vendor/pr76` as a non-authoritative fixture (Git blob `88002b133c659b8a42b806627796db3f13b8b6b2`; SHA256 `8cca6193747287c5fae84ce58f9249684ba258a8e38869e4626ff402336a29f4`). From a Git checkout stacked on PR76, the original sibling under `research/cr_c21b_age_reactor_20261016/src` is loaded without vendor duplication. For a zipped restore, vendor fallback is used.

Sandbox **28/28 targeted pytest PASS** under Python 3.11+ or 3.13+; raw stdout in `evidence/TEST_RECEIPT.log`, raw C8 comparison in `evidence/REFERENCE_COMPARE.json` and `evidence/SCOPED_MATRIX.json`. All publication-phase ZIPs contain individual SHA manifests; remote Drive and ChatGPT Library object bytes were re-materialized and verified. `native_subagent: NOT_RUN` (host lacks native dispatcher).

## Relation to literature and sibling repos

This work complements but does not replace `rei_bianchi` PR166 (source-age native MD14/Case-A but increasing age-refinement differences), PR167 (old/newborn BE bias), PR168 (source-free native RR/DR 2nd order), BASS_HE PR73 (moving angular/spectral cut source quadrature), and native production PR150. It does not repeat R5 exact-pair dynamics of PR76 but extends them to **exact physical-time exposure and native-interface representability**. Primary algorithms: Mellema et al. C2-Ray (2006), Friedrich et al. C2-Ray helium/multifrequency (2012), Norman et al. fully coupled reionization (2015), Pawlik & Schaye multifrequency thermally coupled TRAPHIC (2011). 

**Do not overclaim:** true native `igm_point_rhs` not invoked this turn; no Case-A RR/CI/DR/CMB, moving Bianchi ray Jacobian, 48-cell source shape, full EoR or guaranteed global error bound. A native Grackle endpoint BE cannot be supplied `Γ_exp` unless its integrated update and per-step event ledger are modified accordingly.

## Stage checkpoints / science DAG

R5: derived/Wolfram + separate ZIP / source GitHub / Library+Drive readback.
C5: three executable Python sources, native two-lane rate contract + separate ZIP / source GitHub / Library+Drive readback.
C6/C7: 28 pytest, physical ledger & conditional absorber inequality counterexample / source and logs GitHub / Library+Drive readback.
C8: six 5-resolution sweeps + primary 2..128 Radau comparisons / GitHub raw JSON / Library+Drive readback.
C10: `CODEX_NCP_HANDOFF_KO.md`, final portable ZIP and `DELIVERY_RECEIPT.json` with limits and hashes.

See `THEORY_R5_KO.md`, `C5_IMPLEMENTATION_KO.md`, `C6_C7_REVIEW_KO.md`, `C8_NUMERICS_KO.md`, `DAG.json` for stage details and scientific scopes.
