# CR N5 — provider coverage, rate semantics and first-event envelope

Frozen scope, 2026-10-24. Parent user authority: bass_cr PR99 science d04b2a56adb4a5d55b901420aa544332b41f6dbb, documents 4a0bbc0ed618ab6eae1b7b2714e366d803186b86. Parallel C23E PR100 science 8e4e06361d714939513a11f64a27f02822bde2fa and its D43K PI/RR/CX results are reused. This is an additive child of CR_N5_ATOMIC_ISOTOPE_COVERAGE, not a replacement of either result.

## Goal and authority

Bind the current PHYS81/82/83/84 and HE-ANG owner returns to explicit atomic/isotope coverage and distinguish thermal rate coefficients, tagged-electron hazards, energy relaxation and angular-window observables. Implement a source-pinned semantic adapter. Compute one new, bounded algebraic diagnostic from saved C23D MFPT and PHYS83 rates. No old science replay, provider rate quadrature, ODE, coupling, isotope-source reconstruction, or NCP dispatch.

The inherited C23C atomic_contract.py (Git blob e308ceef315e9f40f96fa62c2667253a1283523e) supplies the 21-population registry, exact incidence and isotope-quotient definitions. Its completed tests are not rerun. C23E already binds conditional D43K PI/RR/CX to one potential; do not rebuild that ledger. The new adapter owns only request admission and the explicitly named diagnostics below.

User-supplied PhysMath1.0.0 R1–R10/C1–C10 applies. The later installed skill1.3.0 bare-next-stage default does not narrow the explicit user continuation scope. Ordinary expected-SHA publication uses R1; final canonical recovery bundle uses actual-byte R3. Missing .codex/readback-policy.json at the observed branch is preserved as a 404; docs/READBACK_POLICY.md is the available policy. No new requirement is inferred from the absent file.

## Fixed physical context

Metric(-,+,+,+), non-tilted LRS, normal/bath frame; proper seconds. Atomic gas isotropic closure and nonbaryonic Vlasov stress remain separate. Preserve signed amplitude, tensor Frobenius norm and cancellation distinctions. T=10000 K, n_e,thermal=0.14 cm^-3, prescribed lnLambda20. Constants kB=1.380649e-23 J/K and epsilon_eV=1.602176634e-19 J/eV remain explicit.

The C23D initial tagged source has 0<W<10 eV. This is not the full reachable EE energy domain. Reused MFPT uses first entry at q=chi*kBT/epsilon_eV, chi in{1.5,3}, and reflecting upper R*kBT/epsilon_eV, R in{40,80}. New tables use R80 saved means, retaining R40 as provenance only. The source-conditioned active mean and active fraction are read, not recomputed. Bound inputs must cover the entire [q,80*kBT/epsilon_eV] domain and use the same frame, clock, bath and stopping-time observable.

## Provider admission

All providers retain exact repository/commit/path/blob and local SHA256. A branch or code file existing is not numerical admission. PHYS83's finite Maxwellian rate table is numerically available at 66 exact temperatures; PHYS84's instantaneous source consumer remains NUMERICAL_ADMISSION_WAIT. HE94's measured conditional DDCS20 window is available only at incident20eV, outgoing3–6eV, theta15–120deg under its declared interpolation. Parent HE-ANG remains SOURCE_INPUT_PENDING.

Request identity includes target nuclide/charge/internal state, process, average/quantity kind, frame, proper-time clock, units, thermal T or tagged W domain, interpolation, isotope mapping and owner status. Unknown/missing rate/species/domain returns null or an explicit rejection, never a fabricated zero. A physical subthreshold zero requires the owner's stated threshold. A mathematical finite-window exclusion is not a physical zero.

Separate source support floor, chemical binding defect and kinematic threshold. Source-native H CE gap10.20435eV must not be replaced by another spectroscopic or C23B convention. PHYS81 CI windows H1[13.6058,968.61],He4[24.6,60],Li7[6,15]eV remain finite-source models with unknown omitted physical contributions; D/T/He3/Li6 cross-section transfer is not admitted. Conditional elemental H-equality/He-equality/Li-equality PI/RR is identified as that model, not empirical isotope resolution. DR, neutral momentum-transfer/finite-T elastic and electron-ion energy-exchange kernels missing from the admitted selected input remain null. Bare-ion DR is physically inapplicable for no bound electron; this is not a supplied numerical zero.

## New algebraic calculations

For an unperturbed admitted EE path W_t and its first-entry time tau, a distinct collision is represented only when a conditionally Poisson mark has nonnegative hazard h(W_t,t). If a source-qualified uniform envelope h<=hmax is supplied over the complete reachable pre-entry path, then

P(mark before tau)=1-E[exp(-integral_0^tau h dt)] <= 1-exp(-hmax E[tau]).

This is a standard survival/Jensen estimate, not claimed as a new no-go or first-entry theorem. With the reused active distribution, the whole-selected bound is f_active*(1-exp(-hmax*m_active)); initially below-cutoff particles have tau0. The saved numerical means give conditional finite-reflecting-model diagnostics, not a certified continuum or physical-model probability enclosure.

For target tolerances epsilon={.01,.1,.5}, calculate hcrit=-log1p(-epsilon)/m_active for each of three redshifts and two chi values: exactly18 new rows. This is the envelope sufficient for an active-population probability at most epsilon, conditional on the bound premises. No actual physical competing hazard is supplied: actual_competing_hazard_per_s=null, actual_competition_probability=null. Use expm1/log1p for small arguments and reject booleans/nonfinite/negative inputs.

From the PHYS83 exact T10000 CSV rows, read q_up and q_down for2S,2P. Compute lambda_target=n_e,thermal*q(T) and lambda_target*m_active for 4 transitions x6 MFPT contexts=24 new rows. Label them frozen-target thermal-rate/EE-first-entry comparisons. These do not give a tagged electron collision probability, an evolved atomic event count, a heat rate, or a PHYS84 source execution. Excited populations and radiation owner remain unsupplied; heat=null. No thermal rate is re-evaluated or interpolated.

Coverage queries explicitly test initial source support versus the complete MFPT path. H CE may be subthreshold initially and accessible later. He CI [24.6,60] and Li CI [6,15] fail full-path coverage at R80. No scalar total cross section or k(T) is treated as an energy-loss moment or angular/joint secondary law.

## Pre-execution constructive extension — revision 2

The actual PHYS83 source code supplies the positive piecewise-linear quantity W(E)=E*sigma_up(E) through MatchedCEChannel.energy_eV and W_eV_cm2. Reuse its exact pinned constructor and four source files. Do not call its moments/evaluate methods, do not perform new rate quadrature, and do not invoke the unadmitted PHYS84 source adapter.

Add one named conditional channel: fixed ground-state H1 density n_1s=0.9 cm^-3. This equals the C23D total neutral-H density numerically but adds an explicit ground-state-only closure for this diagnostic; no excited populations are inferred. The source-native stationary heavy-target/unpolarized W-PL model defines

h_CE(E)=n_1s*100*sqrt(2*epsilon_eV/m_e)*[W_2S(E)+W_2P(E)]/sqrt(E)

for E>=Delta, and zero below the admitted source-native threshold Delta. The factor100 converts m/s to cm/s. On an affine panel W=aE+b, the only interior stationary candidate is E=b/a, when a!=0 and the candidate lies within the panel; also test both clipped endpoints. Take the maximum over the union of both channel knot grids, the threshold and path endpoints. Evaluate W by nonnegative endpoint interpolation, avoiding cancellation in aE+b at the threshold. Use this new analytic-panel search for individual2S,individual2P and their sum over the full R80 path. Record the maximizing E, panel, candidate type and coefficients/endpoint values. This is a supremum of the declared interpolated source model, evaluated numerically; empirical source uncertainty and continuum certificates remain null.

Compute conditional first-CE-before-first-entry estimates using the saved means and this uniform envelope, six source/chi contexts x three channel selections=18 new rows. Record active and whole-selected bounds separately. These are per-particle first-event upper estimates for the declared frozen bath/ground-target/EE finite-band model. They do not give a full stopping time, late-time heating, or probabilities for missing elastic/CI/RR/DR/CX/EI processes.

Revision2 is frozen before any new scientific call. It replaces the earlier blanket 'no actual competing hazard supplied' statement only for this explicitly constructed H1 ground CE model. All other physical hazards remain null. NumPy and SciPy are allowed solely to import the existing pinned provider and its vendor dependency; no new dependency installation. Bound the numerical worker at512MiB address space after checking current reclaimable memory. Validate the new maximizer with80-digit Decimal candidate evaluation and independent analytic test functions; do not replay PHYS83 rates or reciprocity/population suites. Use provider m_e=9.1093837139e-31 kg and its pinned a0 conversion; do not replace their constant convention.

## Implementation and verification

Python standard library for admission, JSON/CSV and algebra. Keep the production numerical functions separate from tests and dispatcher. Input manifest SHA256 check is mandatory; paths are relative and independent of cwd. No import-time writes or science. Output directory creation is exclusive; retain failed evidence and reject repeated run IDs.

New targeted verification only: thermal/tagged kind mismatch; full-path support versus initial support; missing rates/null; exact T/absent T; isotope mismatch; WAIT provider consumer rejection; HE partial angular support; fixed-bath/frame/clock mismatches; invalid/overflow/underflow arithmetic; create-only outputs. Independent reference uses Decimal or explicit formulas without calling production arithmetic. Jensen examples: deterministic tau=m equality; exponential tau gives hm/(1+hm); two-point0/2m gives(1-exp(-2hm))/2. Analytic synthetic cases are tagged synthetic and not physical rates.

Binary64 versus80-digit Decimal hcrit/rate-product scaled relative<=5e-14, with explicit exact-zero handling. Input source hashes exact. Domain endpoints use exact decimal/Fraction semantics where appropriate. Missing output must serialize JSON null, not NaN. Actual checks and costs, not counts alone, support admission. One independent R6/C9 pass and corrections only for concrete findings.

## Resources, preservation and stop

Check current affinity,cgroup memory and relevant processes before each child. Host observed CPUs0..8/quota8/8GiB, CPU55 absent. Reserve coordinatorCPU8; new numerical workerCPU0, native threads1. Cache-heavy memory.current is distinguished from anon: admit only when current headroom plus clean inactive-file cache leaves>=256MiB after a64MiB worker reserve; do not terminate other processes or alter host memory. Execution CPU30s/wall60s/address-space256MiB, no heavy libraries for science. Plotting is a separately recorded bounded child with current memory check.

Exclusive local cooperative lease and create-only output. Inherited C23D lineage13.331329114 worker CPU seconds plus C23E2.161932 gives15.493261114s known subtotal. These are partial measured lineage costs. Global spend, remaining, currency, external NCP lease, unmeasured costs remain null/UNOBSERVED. No prior budget is reset.

Finish this child with exact source/run evidence, report, current-owner matrix, null obligations, independent review, expected-SHA additive draft publication and canonical backup. Full N5 remains PARTIAL if empirical isotope and rate coverage obligations remain. N6/N7 remain OPEN pending their selected-model gates. Full high-energy nuclear and general triaxial/tilted/polarized CMB HOLD; original network PNG NOT_RECOVERED_NOT_READ; global_error_bound/global_completion_percent=null. Every R/C stage records EXECUTION | PUBLICATION | BACKUP | DAG.
