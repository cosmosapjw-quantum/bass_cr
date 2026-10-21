# C21L: today REI Sigma–Pi pilot contribution (2026-10-21)

## Frozen objective and scope

Create a complete runnable pilot under bass_cr/research/cr_c21l_rei_pilot_20261021,
reusing the exact REI PR147 physics at 3b85dedce84d37b3e165da00685a8a984950aafe.
Do not change another checkout. Source closure is already read into
`rei_today/upstream/rei/`; preserve its bytes and directory structure in `vendor/rei/`.
The executed source is CanonicalFVSpecies with source_lock(), Tcmb0=2.7255 K,
ellmax=8, mass_fraction=.1, mass_over_Tref=30, massive_A=0,
radial_cells=24, angular_cells=12, subcell_gauss_order=3, donor=None.
a_ref=1/21 -> a_end=.2 (z20 ->4). This is a collisionless LRS non-tilted Bianchi I
pilot with gamma/nu energy/number and massive Vlasov. Full H/He/UV/stars and general
triaxial dynamics are not part of this run; preserve existing science HOLDs.

Default grid: signed Frobenius shear amplitude S0 in
[-.04,-.02,-.01,-.005,0,.005,.01,.02,.04], signed normalized total stress P0 in
[-.001,-.00075,-.0005,-.00025,0,.00025,.0005,.00075,.001]. 81 distinct cases.
Use one common initial angular multiplier k_gamma=k_nu=k and isotropic massive
source A=0. This two-dimensional source family fixes all other degrees of freedom;
it is not an exhaustive parameterization of every tensor shape or stress history.
No new NCP C21K/HE/WU/REC campaigns and no detailed performance benchmarking.

## Exact physical map (parent-owned)

Metric scales a_perp=a exp(-b), a_parallel=a exp(2b), s=db/dt, H=da/(a dt).
sigma=diag(-s,-s,2s); total pi=diag(-p,-p,2p), p=sum of signed
Pi_gamma_J_m3, Pi_nu_J_m3, Pi_matter_J_m3 fields (each field is pi_s=DeltaP/3).
S=sqrt(6)*s/H, Sigma_F=abs(S), Sigma_half=Sigma_F/sqrt(2).
P=(8*pi*G/c^2)*sqrt(6)*p/H^2, Pi_F=abs(P), Pi_half=Pi_F/sqrt(2).
Here H is s^-1, stresses J/m^3. With kappa4=8*pi*G/c^4 this is
Pi_F=kappa4*|pi|/(H/c)^2. Do not omit c^2 or sum absolute component stresses.
Store both signed quantities and both norm conventions, source fields and H.

For target S0, source Sigma_ref=abs(S0)/sqrt(2), orientation=sign(S0),
q=S0/sqrt(6-S0^2). Source initial_state must still be called unchanged.
Determine k from ACTUAL initial fields at k=0 and k=.5 (no ODE needed):
P(k)=P(0)+2*k*(P(.5)-P(0)); k=(P_target-P(0))/(2*(P(.5)-P(0))).
This includes tiny massive isotropic quadrature residual and actual H0.
Reject |k|>.5, nonfinite/zero slope, or mapped initial S/P discrepancy >2e-13.
Do not snap solver values to requested axis values. Save actual mapped inputs.

## Approved exact reuse optimization

One immutable CanonicalFVSpecies template per process; copy.copy for each case,
with only Sigma_ref, orientation, k_gamma, k_nu, _nfev changed. Share readonly
energy_matrix, number_matrix, thomson and canonical momentum arrays. All per-case
state arrays remain independent. No broad global monkeypatching.
Optional moment subclass/wrapper can compute `(r*self._q)**2` once and reuse for
qp2/qz2, cache `1-self._mu2`, and cache np.min of immutable cell populations.
Keep every elementwise expression and summation order otherwise identical.
Do NOT replace `(r*q)^2` by r^2*q^2, alter dtype/state width, use fastmath,
change quadrature, turn solve_ivp(vectorized=True) into an ensemble solver, or
reuse solution trajectories across distinct cases.
Use original integrate(n=101, rtol=3e-11, atol=3e-13). Reuse may remove setup and
duplicate work; no empirical speedup is claimed without a matched experiment.

## Process and resource contract

Implement independent persistent processes, threads=1 before NumPy import,
with incremental per-case JSON/NPZ outputs and sorted aggregation. Existing
completed identical case outputs may resume after manifest identity check;
failed attempts remain raw and are not silently retried. Output root create-only.
No case failure deletes good case outputs or turns another case into a failure.

On Linux: actual sched affinity intersect visible cgroup-v2 cpus and ancestor
cpu quotas/memory limits. Exclude CPU55; count coordinator. Take a short bounded
/proc/stat sample to avoid busy cores. Acquire cooperative per-CPU flock leases
in a configurable shared directory, compatible filename cpu_N.lock with C21K.
Do not treat another running job/session as a host-wide blocker. Use unleased,
observably idle allowed cores; if none available, bounded wait/clear resource
status. Leave all unrelated processes alone. Release own locks on normal/exception exit.
Conservative per-worker budget512MiB, coordinator256MiB, reserve max(1GiB,12.5%
effective limit); cap by live available memory and quota. CLI workers/cpu-list can
further restrict, never enlarge actual limits. Expose a plan-only mode and a
bounded --timeout-seconds for campaign; no blind whole-campaign rerun.
Each process uses a fixed unique CPU from admitted pool; coordinator uses its
reserved CPU. Host-wide sample is an observation, leases only coordinate clients
using same directory. Do not claim unmanaged jobs are reserved or controlled.
If a portable sequential mode is needed, explicit --workers 1 can preserve
correctness but distinguish non-NCP execution. Remote availability is not a
prerequisite for a bounded sandbox pilot.

## Deliverable and actual verification

Files: reusable adapter, sweep runner, resource helper, plotter, focused tests,
SOURCE_MANIFEST.json of imported original files (repo/ref/path/size/SHA256),
example commands and concise implementation notes. No root Git mutation by child.
Use numpy/scipy/matplotlib std APIs; no new heavyweight dependency/build.
Plot saved outputs only: two figures of four sign branches (S0 sign, P0 sign),
norm initial axes Sigma0/Pi0, colors final Sigma and final Pi respectively.
Label EXPLORATORY/PRELIMINARY, z20->4, LRS collisionless and Frobenius/time-unit
convention; zero-axis cases may be shared in panels with explicit labeling.
Also CSV of endpoints, NPZ/full histories, per-case physical diagnostics,
source/runtime identity, resource plan/observation and completion counts.
global_error_bound=null; NCP and performance claims depend on actual evidence.

Smallest checks: normalizations and signed stress cancellation; template
independence; bitwise moments baseline vs exact-reuse at representative eta/b;
full baseline vs optimized solution arrays for 3 representative cases at same
settings; resource arithmetic CPU55/quota/memory + held-lease skip; partial
result/resume identity logic. No full previous suites, no speed benchmark.
Then run the 81 requested new physical cases once on bounded sandbox resources
(e.g4 workers if admitted). Preserve all failures. Parent/fresh reviewer will
make scientific admission. If a convention/source/physical-model repair is needed,
stop that part and ask parent; routine implementation defects can be repaired
within this scope and affected checks rerun.

## Workflow and ownership

Parent Astra owns this contract, theorem checks, source/admission and publication.
Lower-tier coding worker owns implementation/testing/run under unit path only.
Fresh read-only Astra review is one pass over actual changes/results, no recursion.
Apply physmath1.3 POLICY_INTEGRATION and C3-C8: bounded progress, reuse unchanged
evidence, no metadata-only loop, typed identity and honest NOT_RUN/PASS scopes.
