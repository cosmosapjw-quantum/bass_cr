# External code / representation survey — BASS CR R3M16

Read-only investigator; no repository edits. Base read: bass_cr R3M16; user selected HEAD 7844bc0d8122070b267ee77c75cb2c9447435155. Read harness research PROJECT_INSTRUCTIONS/state and coding AGENTS/SCIENTIFIC_CONTRACT/RUN_STATE. Their state files are unfilled templates, not scientific evidence. Inspected cr_repro/{aocc,tdl,observables}.py, vendor_w1r/gaussian_cartesian.py and docs/roadmap/RESEARCH_PLAN_KO.md. Research acquired 2026-09-22 UTC.

## Decision relevant conclusion

No inspected external package supplies a demonstrated drop-in 1%-accurate moving-three-dimensional-two-Coulomb-center capture solver matching this project's finite-span observables. Best immediate step is a **same discrete Hamiltonian, independent time-evolution oracle**; separately improve the existing AOCC metric/channel auditing. Preserve the physical Coulomb potential and separate propagator accuracy from spatial continuum accuracy. A package being mature for laser ionization is not evidence for accurate proton-H capture.

## Viable methods and concrete interfaces

| Method | Actual source / interface inspected | Practical role | Compatibility limit and needed acceptance |
|---|---|---|---|
| Matrix-exponential action of the current H_h | SciPy v1.16.2 official `scipy.sparse.linalg.expm_multiply(A, B, start=None, stop=None, num=None, endpoint=None, traceA=None)` accepts a transposable LinearOperator. | Most direct independent temporal oracle for target-only H_h=T_FFT+V_target. Use A=-i H_h in atomic units; provide matvec and adjoint. Supply traceA when known. Tiny-grid dense eigh is a second oracle. | Shares spatial H_h and therefore cannot validate continuum physics. Large 63M arrays need local memory/operation budgeting; do not silently run full CPU production. time-dependent collisions need separate nonautonomous integrator/order validation. |
| tRecX FE-DVR / nonorthogonal multicoordinate basis | Official paper Sec.2.6 `Pot3d: potential=radial[0,0,65,-1/Q]`, `[[Pot3d]]`, `PolarOffCenter` and `tutorial/510OffCenterScatter`; `OperatorAbstract::apply`, `OperatorInverse`, `TimePropagator` / `ODEstep`. Archive DOI 10.17632/zdjbnjxzrn.1, GPLv2. | Strongest inspected extensible external framework for a singularity-aware, actual -1/r independent discretization. FE-DVR provides separate radial/angular convergence. | Published example is a stationary off-center scatterer. Moving origin, time-dependent overlap D, both-center bound-channel projectors and ETF validation are not demonstrated by that example. irECS/tSURFF photoelectron observables do not automatically supply capture. Use stationary and translated atom acceptance before collision. Source GitLab could not be fetched; archive metadata/paper inspected, no compiled execution or exact commit claimed. |
| Existing two-center AOCC, upgraded as independent comparator | `OneElectronAOCC.matrix(t)`, `generator(t)` and vendor analytic GTO overlap/kinetic/nuclear/moving_ket_overlap. Generic Cartesian powers exist in primitive layer, but driver instantiates only s and p. | Lowest integration-cost independent spatial lane; analytic Coulomb integrals with ETFs already present. Prioritize independent moving-metric test, final coefficient/metric persistence and common 1s/n≤2/n≤3 span readout. | s+p aggregate is not n≤3. Actual d construction/rotations and complete shell/radial convergence needed. Gaussian cusp convergence can be slow; benchmark isolated spectra and analytic orbital overlaps, not only total norm. Published SC-CCC/TC-BGM support two-center channels but are not executable source imports. |
| Coulomb-wave DVR / H0-plus-projectile splitting | Gombosuren et al., arXiv:1907.00634, Eqs.3–9: split exp(-iH0 Δt/2) exp(-iV_P(tmid)Δt) exp(-iH0 Δt/2), radial Coulomb-wave nodes and H0 eigenvectors. | Useful alternative factorization: treat target Coulomb exactly within radial discretization and test target-only drift/atomic spectrum without Cartesian cusp sampling. | Their reported use is antiproton ionization; attractive projectile capture and translating bound packet are materially different. A target-centered expansion may need very high angular/radial resolution to follow projectile-bound states to z=60. No public implementation/license/commit verified. Method-design candidate only; source cannot be claimed restored. |
| Qprop as isolated-atom reference only | Official Rostock download page lists 3.2. Inspected older public `timy/Qprop` mirror HEAD e8e3d73e095fa8949d499f2763d632aeb6be4128 (2011), tree 5ab34bc1f19f27364b564bb0679e4de19d5fe8ef; `src/core/wavefunction.h` blob ee915961eb88ffb815ffffde4781fa4ec4100f70 exposes energy, norm, project, propagate, do_muller_ell/ellm. Mirror README contains MIT license text with Bauer/Koval copyright. | Radial/angular hydrogen eigenstate/propagation reference at low adaptation cost. Pin actual official archive if used; do not confuse 2011 mirror API with 3.2. | Spherical-system/laser-atom focus. Off-center moving Coulomb multipoles, full capture projection and basis truncation need a substantial new implementation. Not a full collision drop-in. |

## Screened out as an immediate replacement

**BDSCx (Tseliakhovich, Hirata, Heng 2012)** is highly relevant to proton-H capture and variable transverse + Fourier-longitudinal grids. However Eq.(17), PDF pp.5–6 uses a capped Coulomb potential inside R0=.2 a0. Vanishing volume integral of V_capped−V_true does not make the Hamiltonians identical. Sec.3.3 reports selected grid cross-section differences <3%; it is not a certified 1% reference. Adopt its moving-atom and channel support tests as design guidance only. No public source repository/license/commit found in the bounded search. Its 5–80 keV published range does not supply the current 100/225 keV benchmark. [Primary: https://arxiv.org/pdf/1201.4778; DOI 10.1111/j.1365-2966.2012.20787.x]

**Joel-Venzke/TDSE**: inspected master 83f0eaaf28a7b67f55d004d72e7bae95b0d39e48, tree 39b27785e39231ba1b42a3ee9d048702b0f164a3. `src/Hamiltonian.h` blob ef546f2bb791e6e86f9f7d4cdd8c597bad3240ea offers `GetTotalHamiltonian(time_idx,ecs)`, finite-difference weights and multiple static nuclear locations; it also explicitly carries atomic soft-core parameters. Root tree has no detected LICENSE and no moving-nucleus interface was established. PETSc/HDF5/MPI numerical design reference, not approved vendorable or physical production substitute. [https://github.com/Joel-Venzke/TDSE/tree/83f0eaaf28a7b67f55d004d72e7bae95b0d39e48]

## AOCC invariant derivation and concrete implementation work

For columns Φ_a(t), ψ=Φ C, define O=Φ†Φ, H=Φ†ĤΦ, D=Φ†dotΦ. In the project's atomic units:

- `i O dot C=(H-iD) C`.
- `dot O=D+D†` and `H=H†` imply d(C†OC)/dt=0.
- Factor O=R†R with upper-triangular R and positive real diagonal. With y=RC, `G=dotR R^-1-R^-†D R^-1-iR^-†H R^-1` is anti-Hermitian if these identities hold.
- Current code instead constructs W=R^-†(D+D†)R^-1 and X=triu(W,1)+diag(real(diag(W))/2). Consequently X+X†=W algebraically; current G+G† defect cannot independently validate dot O=D+D†. `unitary_step` additionally Hermitian-symmetrizes iG.

Required meaningful tests:

1. Independently form `(O(t+eps)-O(t-eps))/(2eps)` and compare to D+D† across eps sweep, incoming/closest/outgoing times, nonzero v and nonzero b. Check convergence region vs roundoff. A wrong D multiplied by 1.01 must be rejected even if constructed G remains anti-Hermitian.
2. Save unsymmetrized H/H†, O/O† residuals, min/max O eigenvalues, condition, D identity residual and raw G anti-Hermiticity. Preserve failure, do not floor eigenvalues.
3. Test Galilean ETF: isolated translating hydrogen should follow `exp[i v·r-i v²t/2] φ_nlm(r-R(t)) exp[-iE_n t]`; compare complete phases/coordinate direction, and then ray-invariant readout. Common nuclear-nuclear scalar potential changes only overall phase for prescribed trajectories; record convention.
4. For channel columns B, P=C† O B (B†OB)^-1 B† O C. Check span invariance under nonsingular B basis changes, positivity ≤ norm, nested P1≤P2≤P3, ill-conditioning rejection. n assignment must use isolated-H wavefunction identity/overlap, not an arbitrary energy bin. Cartesian d block decomposes into trace s-like and traceless l=2 pieces, so merely adding xx/yy/zz is insufficient evidence for clean d channels.
5. Persist final C/O, per-channel basis map, eigenvectors/eigenvalues, time/phase conventions and source identity. Rank and finite-box support are required for comparing to TDL.
6. Use symmetric target/projectile completeness in present AOCC convergence ladders; changing one center may cause slower convergence or symmetry failures. Toshima 1999 supports this concern but is a statement about convergence, not a proof that every asymmetric dynamic basis is invalid (TC-BGM is a counterexample to a blanket rule).

## Best external full-collision literature benchmark

Leung & Kirchner, EPJD 73,246 (2019), arXiv:1907.08234v2, DOI 10.1140/epjd/e2019-100380-x: TC-BGM proton-H initial n=1,2 over 1–300 keV. Equations 2–7 give physical two-Coulomb Hamiltonian, moving two-center ETFs and overlap-metric evolution. The regularized generating potential WP is a basis generator, not replacement of physical Hamiltonian (critical distinction). Paper uses bound states through n=6 and pseudostates, notes detailed state-selective results available from authors. Numerical curves are external comparisons; they do not directly validate single-b P3, and no source code/API/license was verified. Do not send author messages without user authorization. This is a more relevant energy-range guide for 100/225 keV than BDSCx. Important limit (original PDF printed p.7 / PDF index6): for initial H(2p), capture at >=100 keV develops anomalously large n=6 populations, attributed by the authors to numerical precision; those high-energy results were not repaired. Treat them as a failure-mode example, not a 1% oracle, and do not transfer that initial-state-specific failure automatically to H(1s).

SC-CCC: Avazbaev et al., PRA 93,022710 (2016), DOI 10.1103/PhysRevA.93.022710, accepted manuscript https://link.aps.org/accepted/10.1103/PhysRevA.93.022710. Two-center excitation/capture with Lyman-alpha alignment over 1 keV–1 MeV; suitable channel-resolved benchmark family. Source executable/commit/license unresolved here.

Toshima, PRA 59,1981 (1999), DOI 10.1103/PhysRevA.59.1981: compares pseudocontinuum on both/target-only/projectile-only centers; one-center choices can converge much slower and show low-energy symmetry defects. Primary abstract only inspected; do not claim full equation audit.

## Source ledger for root to reopen/cite

- https://docs.scipy.org/doc/scipy-1.16.2/reference/generated/scipy.sparse.linalg.expm_multiply.html — API and transposable operator/traceA requirements; web ref turn256272view0.
- https://arxiv.org/pdf/2101.08171 — tRecX Sections 2.6, 3.4–3.5, 4.3, 4.7 inspected; refs turn258751view0 / turn410150view1 / turn733873view5.
- https://data.mendeley.com/datasets/zdjbnjxzrn/1 — archival version and GPLv2; ref turn256272view1.
- https://www.qtmps.physik.uni-rostock.de/forschung/qprop/download/ — official 3.2 download; ref turn410150view0.
- https://github.com/timy/Qprop — mirror license and intended scope; ref turn179111view1. API files fetched using GitHub connector pinned SHA above.
- https://arxiv.org/pdf/1907.00634 — CW-DVR Sections 2–3 inspected; ref turn273165view0.
- https://arxiv.org/pdf/1201.4778 — BDSCx Sections 2.2–3.3 inspected; ref turn256272view3.
- https://arxiv.org/pdf/1907.08234 — TC-BGM Sections II/III inspected; ref turn181243view1.
- https://journals.aps.org/pra/abstract/10.1103/PhysRevA.59.1981 — pseudostate convergence abstract; ref turn582863search1.
- https://link.aps.org/accepted/10.1103/PhysRevA.93.022710 — SC-CCC primary fulltext retrieved; ref turn181243view3.

No external solver built/run; no source imported into bass_cr; no provider backup claim. All compatibility/adoption recommendations are inference from inspected material, not implementation-verified production performance. System1 broad queries returned many irrelevant results; authoritative details were checked via direct primary URLs and pinned GitHub reads, not those irrelevant hits.
