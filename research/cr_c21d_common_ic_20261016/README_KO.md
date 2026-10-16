# C21D 연구 종료: common-IC photon photo reactions, midpoint absorber exposure

날짜: 2026-10-16 KST. 원본 기준: `cosmosapjw-quantum/bass_cr` PR78 native replay head `12eba7754df154dbd9e8b2947bb2b94199126e51`, 이전 PR77 source-age reference. 원본 NCP Rust, repo PR78, rei_bianchi 및 BASS_HE 생산 계산은 모두 **불변**으로 유지했다.

## 이번 작업에서 새로 얻은 결과

같은 9개 source-age packet (3 old + GL2 × 제조된 3개 positive source energy), 같은 초기 H/He, FLRW proper clock, total-H proper density, MD14 **총** source rate, 원본 Verner H/He 단면적과 energy fit cuts를 고정해 다음 수학적 광전리 세 방법을 독립 Radau 연속 RHS와 비교했다.

- **BE:** photon survivor `N1=N0/(1+dt∑_j k_j A_end,j)`, H/He gas changed by exact absorbed species events.
- **EXP:** positive frozen-end photon hazard, `N1=N0 exp(-dt∑k_j A_end,j)` with positive competing-risk partition. This is **not** native PR150 PreparedAbsorption.
- **MIDEXP:** positive self-consistent *time-centered absorber exposure* `Abar_j=(A0,j+Aend,j)/2` inside frozen midpoint `k_j`, with exact exponential survival and event-conserving H/He gas chemistry. The first two lanes are only first-order on the measured smooth domain; new MIDEXP is near 2nd order.
- **Independent Radau:** physical photo-only time-dependent photon/H/He continuous ODE, original C21C pinned source, genuine Verner fits; does not use those frozen-end nonlinear solvers.

R5 Wolfram derived all nuclei/electron/photon/binding identities (6 zeros), additional smooth midpoint hazard O(dt^3) result (first three coefficients vanish; third `k0 a2/12-k1 a1/12-k2 a0/24`). C5 initial executable third lane was updated in C8 to implement MIDEXP; historic C5 checkpoint retains original code and numeric evidence.

### Verified finite result, manufactured model

At `a0=1/12`, `Δln a=.025`, opacity_multiplier=.001, manufactured source energies instead of owner full48:

| subdivisions | BE vs Radau max state error | EXP vs Radau | MIDEXP vs Radau |
|---:|---:|---:|---:|
|16|.001566462364|.000098988364|6.34612e-7|
|32|.000808236179|.000051273180|1.76632e-7|
|64|.000413547677|.000025972242|4.54570e-8|
|128|.000208474680|.000013087803|1.15577501e-8|

Observed n64→128 order 0.98818/0.98875/1.97565. Relative error reduction at n128 of MIDEXP: approximately 1132× vs EXP, 18038× vs BE in **this one vector infinity norm**, not a universal or astrophysical speed/accuracy improvement. At n2→4 MIDEXP error is nearly flat; this is not a global all-grid convergence theorem. Five additional (dx,opacity multiplier) cases give MIDEXP last-pair observed orders 1.958–2.000, BE/EXP roughly one. Photon number ledger ≤2.1e-17/H and total photo-only energy ledger ≤1.6e-15 eV/H for primary 7-grid, but ledger closure alone does not certify state accuracy.

**42/42 fresh Python pytest PASS** (NumPy/SciPy), source + tests + raw JSON + actual solver first failure and repair retained. Initial numerical optimizer gradient quit with false inactive-HeII photo events ~7.08e-10/H. Exact support-zero channel elimination repaired it without loosening tolerances. An independent finite-dimensional midpoint method and Wolfram check are not an original native Rust certification.

## Native state seeding prerequisite (material scientific boundary)

`a0=1/12≈0.08333333333333` in C21D is **earlier** than the actual C19 original checkpoint `a≈0.08873654701704`. The historical C21 epoch bridge rejects pre-checkpoint epochs. For any NCP same-IC parity comparison, do **not** relabel old checkpoint gas/radiation as if at a0 or bypass the guard. Either use a newly **legally generated, explicitly prescribed** owner-native initial condition at a0 with exactly matching gas/photo/source, or regenerate the C21D test at a common supported epoch/IC and rerun independent reference. The manufactured opacity scaling factor .001 and 3-energy source are opt-in controls, **not original MD14/48-cell production physical inputs**.

## Output and claims

- `THEORY_R5_KO.md`, `THEORY_C8_MIDEXP_KO.md`: exact derived identities and finite smooth-step domain.
- `src/c21d_trilane.py`: independent runnable photo-only three model lanes.
- `vendor/c21c/*.py`: pinned predecessor physical source/Radau original for reference only.
- `tests/test_c21d.py`: 42 focused controls, scope `C6–C8`.
- `evidence/TRILANE.json`: original C5 BE/EXP 7-grid evidence retained immutable.
- `evidence/TRILANE_V2.json`: revised 3-lane 7-grid evidence.
- `evidence/SCOPED_MATRIX.json`: 5 condition matrix.
- `evidence/FIRST_FAILURE_C5.json`: actual failed initial optimizer gate preserved.
- `CODEX_NCP_HANDOFF_KO.md`: user action requires only copying prompt or instructing Codex to open GitHub; no manual download.
- `DAG.json`, `DELIVERY_RECEIPT.json`, ZIP source+test+raw results & exact SHA manifest.

Native C21 dynamic microphysical Case-A/CI/RR/DR/CMB, PR150 PreparedAbsorption bit/parity, actual full source 48-cell and signed Bianchi, source-age/spectral convergence, and full EoR remain **HOLD/NOT_RUN**.

## Primary reference and sibling research

Mellema et al. (2006) C2-Ray arXiv astro-ph/0508416; Friedrich et al. (2012) helium extension arXiv:1201.0602; Norman et al. (2015) fully coupled cosmic reionization ApJS 216 16, doi:10.1088/0067-0049/216/1/16. Actual latest sibling PRs: `rei_bianchi` PR #170 (age Duhamel), PR #171 (native source-matched positive reference, age/spectral HOLD), PR #172 (source-on native first-order clock controls), `BASS_HE` PR #74 (source cut donor). Their results are not conflated with this manufactured benchmark.
