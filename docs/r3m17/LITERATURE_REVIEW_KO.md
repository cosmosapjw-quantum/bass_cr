# R3M16 후속 원전 조사 및 판별 진단

작성 범위: GPT-6 Astra physmath harness v4 core/evidence/stop policy 열람. Repository `bass_cr`, 기준 HEAD `7844bc0d8122070b267ee77c75cb2c9447435155`; `cr_repro/tdl.py`, `r3m11.py`, `grid.py`, `observables.py`, R3M16 report를 직접 읽었다. 본 문서는 scratch 조사 메모이며 production 계산이나 repository mutation을 수행하지 않았다. 원문 전체를 정독한 것으로 표기하지 않는다. 아래 원문 열람 범위와 새 유도를 구분한다.

## 결정에 직접 영향을 주는 결과

1. `TIME_REFINEMENT_STILL_OPEN`을 유지해야 한다. fixed-grid temporal convergence와 continuum Coulomb splitting regularity를 구분해야 한다. Trotter 고차화만으로 Coulomb cusp 문제를 없앨 수 있다는 전제는 원전이 지지하지 않는다.
2. 기존 target-only ray distance는 정확 이산 Hamiltonian의 실제 evolution/preparation residual과 splitting error를 합친 것이다. 동일 `H_h=T_h+V_h`의 독립 exponential reference와 직접 비교해야 한다.
3. target-only 시험은 움직이는 핵의 시간 표본화와 Galilean translation 오차를 검사하지 않는다. constant-velocity isolated hydrogen null test를 추가하는 것이 물리적 판별력이 높다.
4. `h^-5/2`는 한 formal commutator norm의 cutoff scaling이다. 총 Strang 오차상수나 full collision `P3`의 error law가 아니다.
5. B0/B1/B2 세 점은 signed temporal contraction을 측정하는 최소 단계다. 관측차가 작다는 것만으로 dt=.0125의 절대 오차배분을 certified하게 닫지 않는다. 실제 dt 비, cancellation, 채널별 차수, boundary/CAP sensitivity를 보존한다.

## 확인한 1차 문헌

### L1 — Burgarth et al. (2024)

Daniel Burgarth, Paolo Facchi, Alexander Hahn, Mattias Johnsson, Kazuya Yuasa, *Strong error bounds for Trotter and strang-splittings and their implications for quantum chemistry*, Phys. Rev. Research **6**, 043155, published 2024-11-18, DOI `10.1103/PhysRevResearch.6.043155`.

- Primary: https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.6.043155 ; https://arxiv.org/pdf/2312.08044
- 열람: publisher abstract; PDF §IV and Fig.6, p.11; §VI/Fig.8, pp.13–14; domain discussion pp.7–9; relevant tables.
- `literature-supported; supports/limits`: low-angular-momentum hydrogen states lack domain regularity for ordinary product-formula error estimates. Hydrogen 1s has an upper-bound quarter-order scaling, supported by numerical experiments. Finite Bessel truncations eventually recover formal second-order/fourth-order behavior, but the required number of steps increases with truncation size (Fig.6/8). This directly supports nonuniform space/time limits.
- 한계: autonomous continuum Hamiltonian, hydrogen eigenstate case study, vector error. Does not certify this Cartesian moving two-center/CAP collision, `h^-5/2`, or capture-probability error. Published upper bounds and numerical scaling must not be relabelled as a rigorous fixed-time lower bound.
- root citation ref already opened: `turn384170view0`, `turn630760view1` (root needs own open for use).

### L2 — Fang–Wu (2026), v2를 인용해야 함

Di Fang and Xiaoxu Wu, *Trotterization with Many-body Coulomb Interactions: Convergence for General Initial Conditions and State-Dependent Improvements*, arXiv:2604.07704v2, **2026-08-24**; v1 2026-04-09.

- Primary: https://arxiv.org/html/2604.07704v2 ; https://arxiv.org/pdf/2604.07704
- 열람: §2.1/2.2, Theorem 1 Eq.(8), §6 Theorem 34, Remark 38/39; conclusion.
- `literature-supported; supports/limits`: for autonomous real many-body Coulomb and initial data in `H²`, kinetic-outer `K/2–V–K/2` has an upper bound `C N^(9/2) T dt^(1/4) ||ψ0||H²`, with `0<dt≤1`, `dt<T^(4/3)`. Theorem 34 gives sharp local `dt^(5/4)` asymptotics for a fixed normalized Coulomb-type state.
- Crucial v2 limitation (Remark 39): local sharpness excludes better global exponents uniformly over **all** step counts, but does **not** prove a fixed-final-time many-step lower bound; cancellation/sublinear accumulation remains possible. v1 stronger wording should not be copied.
- 한계: current runner is potential-outer `V/2–K–V/2`, externally moving nuclei and non-Hermitian CAP; theorem does not directly cover it. State/angular assumptions cannot be inferred from a captured `n≤3` readout.
- refs: `turn950938view0`, `turn982488view0`, `turn982488view1`.

### L3 — Gradinaru metadata and scope

V. Gradinaru, *Strang Splitting for the Time-Dependent Schrödinger Equation on Sparse Grids*, SIAM J. Numer. Anal. **46**(1), 103–123, DOI `10.1137/050629823`.

- Primary: https://epubs.siam.org/doi/10.1137/050629823
- Publisher metadata: online **2007-12-20**, volume issue labelled **2007–2008**, copyright 2007; cite online year explicitly instead of declaring 2007/2008 an error.
- 열람: publisher abstract and metadata; theorem full text not retrieved.
- `literature-supported; contextual`: sparse-grid pseudospectral Strang convergence depends on potential/initial-data smoothness, giving first or second order under its sufficient conditions. This supports the regularity warning, not a specific Coulomb exponent for present full Cartesian grid.
- refs: `turn309174view2`, `turn630760view2`.

### L4 — Gordon–Jirauschek–Kärtner

Ariel Gordon, Christian Jirauschek, Franz X. Kärtner, *Numerical solver of the time-dependent Schrödinger equation with Coulomb singularities*, Phys. Rev. A **73**, 042505, **2006-04-28**, DOI `10.1103/PhysRevA.73.042505`.

- Primary: https://journals.aps.org/pra/abstract/10.1103/PhysRevA.73.042505
- 열람: publisher abstract only. PDF link returned access failure; no stencil equations verified.
- `literature-supported; contextual`: asymptotic behavior correspondence (ABC) constructs Cartesian/cylindrical/spherical discretizations using cusp asymptotics rather than a nonexistent ordinary Taylor expansion. Paper uses a generalized leapfrog accommodating absorption; also discusses compatibility with Crank–Nicolson/Peaceman–Rachford.
- 한계: cannot infer a ready-made GPU FFT potential correction or moving arbitrary subcell nucleus treatment from this abstract. It is a spatial discretization design candidate requiring full-text stencil, self-adjointness, translation, and two-center validation before implementation.
- ref: `turn309174view1`.

### L5 — Majorosi–Czirják Coulomb-aware hybrid solver

Szilárd Majorosi and Attila Czirják, *Fourth order real space solver for the time-dependent Schrödinger equation with singular Coulomb potential*, arXiv:1604.00947; Computer Physics Communications publication linked from arXiv.

- Primary: https://arxiv.org/abs/1604.00947 ; https://arxiv.org/pdf/1604.00947
- 열람: §2.2 Eq.(12), §4.2/4.3 Eq.(62), Fig.1, conclusion, Appendix A pp.25–26.
- `literature-supported; supports/limits`: cylindrical solver enforces the Coulomb cusp as a Robin condition. Hybrid propagation avoids directional splitting near the singularity via a local two-dimensional Crank–Nicolson region, splitting in the outer region. Multiple cores on the symmetry axis can share the cusp treatment.
- 한계: arbitrary `b=2` two-center collision is not globally axisymmetric about a fixed axis. Direct replacement would require moving/rotating coordinates and connection terms or genuine 3-D treatment. A fourth-order result for this method is not a guarantee for a higher-order composition of current point-sampled FFT factors. Appendix A notes that its boundary treatment does not give exact conservation of a standard grid norm; inner-product quadrature and self-adjointness need independent assessment.
- refs: `turn309174view3`, `turn630760view3`, `turn630760view4`.

### L6 — Alvermann–Fehske exponential propagation

Andreas Alvermann and Holger Fehske, *High-order commutator-free exponential time-propagation of driven quantum systems*, J. Comput. Phys. **230**, 5930–5956 (2011), arXiv:1102.5071.

- Primary: https://arxiv.org/pdf/1102.5071 ; https://arxiv.org/abs/1102.5071
- 열람: §7 Eq.(61) CF4:2, §8.1/8.2 exponential action/Krylov/Chebyshev discussion.
- `literature-supported; supports/limits`: Gauss-node combinations of the **full** Hamiltonian provide commutator-free time-ordering approximations; exponential actions can use Krylov or Chebyshev. Exponential-action error must be controlled separately from time-ordering error. Krylov memory grows with stored vectors.
- 한계: wrapping a low-order kinetic/potential split inside each CF exponential does not preserve the advertised CF order. Hermitian Lanczos is inappropriate for full `H-iW`; a CAP reference needs general Arnoldi or another non-Hermitian-capable method. No claim of uniform accuracy for a moving Coulomb cusp is imported.
- refs: `turn900086view1`, `turn449084view3`, `turn449084view4`.

### L7 — charge-transfer benchmark and moving-atom null test

Dmitriy Tseliakhovich, Christopher M. Hirata, Kevin Heng, *Excitation and charge transfer in hydrogen-proton collisions at 5–80 keV and application to astrophysical shocks*, arXiv:1201.4778.

- Primary: https://arxiv.org/pdf/1201.4778 ; https://arxiv.org/abs/1201.4778
- 열람: §2 potential Eq.(17), §3.1 support requirements, §3.3/Fig.4 consistency tests, tables of state-resolved cross sections.
- `literature-supported; supports/limits`: BDSCx uses a hybrid spatial/Fourier grid and verifies both stationary and moving isolated hydrogen. That moving-atom null test is directly useful here. However Eq.(17) caps Coulomb within `R0=.2 a0`, with zero volume-integral correction and capped/uncapped sensitivity tests. This is not the same Hamiltonian as the current physical `-1/r` without an independently controlled regularization limit.
- 한계: 5–80-keV cross sections are not a 100-keV `b=2` probability datum. Published box/nmax requirements and cap sensitivity cannot serve as this repo's error certificate.
- refs: `turn900086view0`, `turn449084view0`, `turn216104view3`.

### L8 — CWDVR independent static reference candidate

Liang-You Peng and Anthony F. Starace, *Application of Coulomb wave function discrete variable representation to atomic systems in strong laser fields*, J. Chem. Phys. **125**, 154311 (2006); arXiv:physics/0604181.

- Primary: https://arxiv.org/pdf/physics/0604181 ; https://digitalcommons.unl.edu/physicsstarace/99/
- 열람: radial matrices Eq.(30)/(31), spherical harmonic Eq.(39), §III.B Eq.(59), convergence discussion.
- `literature-supported; contextual`: Coulomb-wave DVR adapts the radial grid to singular/continuum physics; spherical harmonics plus Arnoldi propagation provide an independent representation for the one-center problem. The paper distinguishes Arnoldi for general matrices from Hermitian Lanczos and separately varies radial, angular, time-step, Arnoldi-order and absorber parameters.
- 한계: stationary single-center strong-field benchmarks do not solve arbitrary moving off-center nuclear cusps automatically. Use for static target/reference verification first; extending to capture requires two-center/angular-completeness checks.
- refs: `turn216104view2`, `turn179963view0`, `turn179963view1`.

## 직접 유도: h^-5/2 설명이 말하는 것과 말하지 않는 것

이 부분은 위 논문에서 인용한 정리가 아니라 원전과 현 구현을 바탕으로 한 직접 유도이다. Atomic units are already fixed by the repository: `ħ=m_e=e²/(4πε0)=1`.

For smooth compactly supported ψ away from nuclei,
`T=-½Δ`, `[T,V]ψ=-½(ΔV)ψ-∇V·∇ψ`, hence `[V,[T,V]]ψ=|∇V|²ψ=r^-4 ψ`.
For normalized 1s, `||r^-4 ψ||²_(r>a)=4∫_a∞ exp(-2r) r^-6 dr ~ (4/5)a^-5`.
This yields a **cutoff contribution norm** `~a^-5/2`. It does not make the uncut commutator an L² vector. The other Strang nested commutator, distributional terms at the origin, state error direction, finite-grid aliasing, and time dependence are absent. Finite FFT differentiation does not obey continuum product rules exactly, so a direct discrete commutator is not pointwise `r^-4`. A/B ratio similarity therefore remains conjectural.

At fixed h and finite box all matrices are bounded; genuine dt→0 Strang asymptotics exist. Their constants and onset can deteriorate as h→0. The formal inequality `dt^3 h^-5/2 <<1` is neither sufficient nor necessary for full collision accuracy.

## 직접 유도: reference가 필요한 이유

For normalized ψ and self-adjoint discrete H, with `E=<ψ,Hψ>`, `r=(H-E)ψ`,
`||exp(-iHt)ψ-exp(-iEt)ψ|| ≤ |t| ||r||` (Duhamel and unitarity).
Thus comparing a split step to the *initial ray* contains true stationary residual drift. The robust diagnostic is `||S_h(dt)ψ-exp(-iH_h dt)ψ||`, optionally phase-aligned, where the exponential action has an independent verified numerical tolerance.

A scalar `d(t)=a t+b t³` is not a decomposition of independent norm contributions. Residual and splitting error are vectors whose cross term matters. Under sufficient finite-dimensional regularity the squared ray distance has even expansion `d²=σ_H²t²+c4 t⁴+c6 t⁶+...`; fitting this remains empirical, while comparison to an unsplit reference isolates the intended quantity.

For non-unitary/CAP states, record both normalized-ray distance and raw norm-weighted difference. Normalizing both states must not hide norm loss. For any orthogonal projector Q,
`|<u,Qu>-<v,Qv>|≤(||u||+||v||)||u-v||`.
This is a full-state sufficient bound, generally pessimistic for a rare capture channel; direct observable refinements remain essential.

## 직접 유도: 움직이는 핵 시간표본화

Projectile `Vp=-1/sqrt(ρ²+(z-vt)²)` with `ρ²=(x-b)²+y²` has a pointwise near-cusp time variation scale `ρ/v`; therefore `v dt/h` is a separate diagnostic parameter from kinetic `dt/h²`. For fixed ρ>0,
`∫[t1,t2] Vp dt = (asinh((z-vt2)/ρ)-asinh((z-vt1)/ρ))/v`.
This exact diagonal phase integral can test pure potential time quadrature in a side experiment. It is **not** an exact full-H propagator; noncommutation with T and time ordering remain. Do not silently install it as a production fix.

The exact continuum constant-velocity one-center solution is
`ψ_v(x,t)=exp[i v·x-i(v²/2+E)t] φ(x-R0-vt)`
for `[-½Δ-1/|x|]φ=Eφ`. A moving-atom no-CAP probe compares norm, comoving 1s survival and phase-aligned shape over the same travel distance, at multiple subcell initial offsets and dt. Finite FFT/periodic grid and sampled orbitals themselves break exact continuum covariance; distinguish representation error from time error by dt-refinement plus a same-grid unsplit reference and boundary support checks.

Computed from repository speed constants using local Python (not production GPU): `v(100 keV/u)=2.00798106651023 a0/t_a`. At h=.20, dt≈.0499678/.02499785/.0125 gives `v dt/h=.501672/.250976/.125499` and `dt T_max=18.4936/9.25196/4.62638`, where `T_max≤3π²/(2h²)`. These are resolution indicators, not instability criteria: split unitary factors are norm-stable irrespective of these phase sizes, and occupied high-k weight matters.

## 권고 판별 순서 및 claim gate

A. Keep present single full-collision B2 budget as historical decision. Before resource-expensive execution, finish code-side bounded probes and guards. Do not automatically launch h refinement or replacement.
B. Same-grid one-center exact exponential reference separates preparation/splitting. Coarse toy matrices can validate implementation against dense eigendecomposition. Large production-grid Krylov vector memory must be estimated before launch; do not infer feasibility from one state array.
C. Add moving-hydrogen null probe and fixed-grid short **two-center** full-H reference. The difference `Strang midpoint – full-H exponential midpoint` probes kinetic/potential splitting; `midpoint full-H – higher time-order reference` probes moving-potential time ordering, each at the same frozen spatial representation.
D. Use actual B0/B1/B2 dt values. Determine signed differences first; no observed order across sign reversals/unresolved differences. For unequal ratios solve `(d0^p-d1^p)/(d1^p-d2^p)=Δ01/Δ12`; use cancellation-safe `expm1/log` numerics. A three-point inferred p and Richardson remainder are empirical, not certified. Require P1/P2/P3 consistency, separate norm/CAP behavior, and record all excluded regimes.
E. If fixed-grid temporal cost proves prohibitive, compare full-H exponential/CFE propagation on the same grid before changing the physical spatial Hamiltonian. If spatial error remains, ABC/FE-DVR/CWDVR/two-center close-coupling are design candidates; none is promoted by literature alone.
F. Production endpoint still requires start/stop separation, CAP/box convergence, common channel projection, all-bound truncation, b quadrature/tail, energy coverage, release provenance and independent validation. No single-b convergence claim admits physical rates.

## 한계와 소스 기록

- No claim of external-code reproduction or full paper proof audit.
- Gordon and Gradinaru full theorem/stencil access remained incomplete; explicit above.
- No production replacement selected; current evidence supports discriminating reference diagnostics.
- All literature arguments are source-scoped; inferences and calculations are labeled separately.
- This source-scoped research note is delivered with the R3M17 repository report and handoff; no external solver reproduction is claimed.
