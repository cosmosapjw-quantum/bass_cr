# NEGATIVE_RESULTS

## N1 — Terminal fractions or an arbitrary exponential clock

Attempt considered: derive the finite317yr deposition from a terminal yield table.
Failure class: theory / identifiability. DERIVATION_KO.md §2 proves that identical
terminal yields allow different delays. No arbitrary-lag numerical fit was run.
This excludes the shortcut, not FS10 terminal physics. Revisit only with independent
absolute collision/time information. Repair adopted: explicit causal stopping model.

## N2 — Low-energy extrapolation of the FS10 high-speed Coulomb logarithm

Attempt considered: use Eq12 below its stated E>13.7eV regime, or substitute its compact
printed density coefficient without checking the explicit plasma-frequency formula.
Failure class: physical regime / source algebra. The published expressions and limits
were directly inspected; literature/source_audit.json preserves this evidence.
No corrected FS10 table or erroneous Monte Carlo implementation is inferred. Adopted
alternative is the explicitly conditional classical cutoff in Khrapak2020 Eq6.

## N3 — Common source age for all secondary electrons

An ensemble born throughout a ramp source does not consist of equally old particles.
Even before removal, its mean birth age is t/3. Therefore comparing just one E/b or
cutoff time with317yr cannot establish quasistatic validity. Failure class: theory /
source-time semantics. Repair: integrate the actual Qe(W,t-a) over birth time.

## N4 — Cutoff crossing means thermalization

Rejected at the scientific contract stage. At0.1eV and100K, E/kBT≈11.6; no near-thermal
operator was provided. Residual kinetic energy and particle number/flux are explicitly
retained. Physical error and actual thermal equilibration remain unresolved.

## N5 — Full PHYS02 or production promotion from this subcomponent

Rejected scope extension. The selected direct source carries only4.46752% of active
impact secondary kinetic input and excludes incoming higher-energy cascade flux.
The ~7.05% parent-heat scale comparison is not full heat suppression or a bound.
PHYS02-DELAY admission remainsfalse and production history HOLD. Original atomic
G02/b_grid/all_bound gates and the separate R17B2B negative result remain untouched.

## N6 — Availability and transport limits in evidence acquisition

The first bulk parent-file materialization hit an argument-size limit before process
creation; smaller exact-byte batches succeeded. This was a runtime transport issue,
not a failed physics run. The old source suite was not rerun. Some primary-source
endpoints (Schunk–Hays publisher/repository and NIST numerical endpoints) were blocked;
the source audit records these limitations. No unseen data were adopted.

## Numerical attempts and focused repair

The retained new-study verification runs are successful. PRE_CUTOFF_FLUX and
PRE_FIXED_DENSITY result/log copies preserve earlier executed states. Independent review
identified that execution exit0 was not yet written to a receipt and that the clock's
positive-density interface exceeded its fixed-state contract. The final delta added an
exact canonical-density guard plus a negative-input check and recorded the actual new
execution with exit0 and9/9 PASS_SCOPED. Equations and numerical tolerances were unchanged.
No prior scientific failure is relabeled as a pass by this repair.

Unchanged PHYS01 tests, original atomic failures, photon homotopy searches and production
runs were not repeated. Those archived failures retain their own exact input identities.
