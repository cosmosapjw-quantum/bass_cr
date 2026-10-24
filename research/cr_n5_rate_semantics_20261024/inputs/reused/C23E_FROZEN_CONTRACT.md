# C23E_D43_PHOTO_RR_SOURCE_BINDING — frozen V2

Root/Astra scientific contract, 2026-10-24 11:11 KST. Replaces history/FROZEN_CONTRACT_V1_SUPERSEDED.md before any V1 science execution. One R1–R10 / C1–C10 theory-to-code loop; no automatic next cycle. Parent CR_N5_ATOMIC_ISOTOPE_COVERAGE stays partial.

## Baselines and actual preflight

- bass_cr documentation HEAD4a0bbc0ed618ab6eae1b7b2714e366d803186b86, branch research/cr-c23d-finite-t-source-bridge-20261024, PR99; tree4501f5428a9883c4f37c67b05b66573b3689893a. Actual ref rechecked unchanged before this node.
- Central REI expected HEAD8b6e741ceb305cb0a6fde244ee002eb5926559fe, orchestration-sandbox branch/PR222; actual ref unchanged. Fresh expected-SHA check again before writes.
- AGENTS: intake/bass_AGENTS.md, intake/rei_AGENTS.md; existing selective-readback and tiered scientific delegation apply. Local workspace is not a checkout (observed exit128); existing connector route, no clone/worktree.
- Seven-repo intake:1310 branch heads,845 open PRs, terminal pagination; all metadata/PR bodies, selected file contents. Full other conversations UNAVAILABLE; retrieved Personal Context excerpts AVAILABLE_PARTIAL. Latest Library WORK_THREAD_PROMPT UNAVAILABLE after empty read and actual network failure.
- Existing C23D Library/Dropbox R3 evidence reused. Drive UNKNOWN_NO_ACK remains unresolved. No completed science replay or old ZIP redownload.

## Reuse and new contribution

REI ISO-COUPLE-P1 PR180 c4a148a8e5b2071d0ede96a316522455b70dc56d and P2 PR181 b6551164bc192a2ba1f3458717b96e6fc2386c9c already contain H/D CX, exact isothermal reduction, shared-source coupling and the raw Savin-fit detailed-balance issue. WU PHYS79 PR134 final3304d16db1dc9bf868c185a8eeb6cc9dbc270e50/science338fb7728e8b41f49551200b1f1ba73c047fb90c supplies the21-population D43K CX model and controls. These are reused, not new findings. Cancelled V1 thermal12+4 runs and geometric-mean model must not run.

New: bind saved C23B PW19 source moments to that D43K potential and C22A conditional Case-A RR moment. Evaluate only a new narrow spectral band, independently check new D-target moments, implement21-population instantaneous source terms with explicit thermal/fast electron pools. No ODE, stopping, full cosmological adoption or full21 rate coverage.

## Exact inputs

Source digests: implementation/reuse/INTAKE_MANIFEST.json; preserve all exact reused bytes.

- C23B spectral_photo_source.py blob e7d474d5145cb264102206e0403b0aa5916c3140, SHA25671b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d, pinned CONTRACT/data. PW19 z=2.316,2.479,2.649;626 knots each, positive log-log interpolation, no z interpolation/extrapolation. Verner H threshold13.6eV, upper50000eV.
- Parent saved totals intake/c23b/CASES.json. Parent saved atoms /workspace/scratch/30d955d9ea43/n4_resume_transport_20261024/verified_restore/main/repository/research/cr_c23c_stopping_coverage_20261023/inputs/photoelectron_atoms.csv,1681578bytes,SHA256f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3. Reading/summing saved atoms allowed; reconstructing completed H source forbidden.
- C23C atomic_contract.py blob e308ceef315e9f40f96fa62c2667253a1283523e provides named21 inventory.
- C22A rr_energy_moment.py blob3585c16fc4afe57153ffd14b75b301f9c44ac1e7; C21O rr_table.dat blobc89720bbfdb615bb376926aca99c1e8d92f7bf35. Read actual H row(7.982e-11,.7480,3.148,7.036e5).
- WU source intake/prior_hdx/WU79_collisional.py: small attributed d_cx_rates extraction allowed. Do not import unrelated He/Li potentials into C23B.

## Model, units and domain

Isotropic bath/rest-target frame and proper seconds; parent normal metric(-,+,+,+), non-tilted LRS unchanged. Per-target moments s^-1/eV s^-1; densities cm^-3; source terms cm^-3 s^-1/eV cm^-3 s^-1. EV_ERG=1.602176634e-12; kB=1.380649e-23/1.602176634e-19 eV/K. delta=43*kB as PHYS79 MODEL; chiH=13.6eV; chiD=chiH+delta. It is not spectroscopic precision or a separately rounded0.0037eV identity.

Conditional D model: sigmaD(E)=sigmaH(E) for E>=chiD,0below the declared threshold. It is threshold-gated H-equality, not empirical isotope-resolved D or finite-mass kinetics. M=50000eV. S(E)=4*pi*nu*J_nu [erg s^-1 cm^-2], not integrated-bin energy. Conditional RR: alphaD=alphaH and captured kinetic momentD=H from C22A. Rate accuracy does not certify temperature-derivative accuracy; this PI/RR pair is not independently established as a microscopic Milne pair. Case-A photons escape; no Planck/LTE claim.

Joint T domain[3,200000]K from VF RR[3,1e9]K and Savin CX[2.7,2e5]K; explicit failure outside. Reused PHYS79 kr=2.06e-10*T^.396*exp(-33/T)+2.03e-9*T^(-.332); kf=kr*exp(-43/T),cm^3/s. Equal-charge-mass/ground-degeneracy thermodynamic model, not the original independently fitted Savin forward rate.

## Constructive boundary transfer

q(E)=S(E)*sigmaH(E)/(EV_ERG*E^2) on[chiH,M]. Saved parent GammaH=int q, KH=int(E-chiH)q, AH=int E q. Production evaluates only the new band[chiH,chiD]:

Glo=int_band q; Alo=int_band E*q; B=int_band(chiD-E)*q.
GammaD=GammaH-Glo; KD=KH-delta*GammaH+B; AD=AH-Alo.

Compute positive B directly; do not subtract nearly equal large terms to obtain it. chiD*GammaD+KD=AD up to inherited parent residual and quadrature. Sparse algebraic boundary update is not measured speedup. Check units/sign/delta0 limit.

Band GL8/16/32 in direct E, split at any native source knots; production16, preserve all outputs. Independent NEW D-target integration q,(E-chiD)q,E*q on[chiD,M] using scipy.quad in log(E) separately over native intervals,epsrel2e-12,epsabs<=1e-35 per interval. Do not re-evaluate full H source.

Diagnostic only: filter saved old HI atoms with K>=delta, shiftK'=K-delta and compare these discrete-measure totals to the continuous D-boundary result. This tests a newly introduced threshold resolution, not the correctness of the old finite measure. Do not assign D FS/cutoff bins or heat from totals.

## One potential and21-population source interface

Require all C23C POPULATION_LABELS byname, finite nonnegative densities. Missing species fail. n_e,all=sum(q_i*n_i); caller supplies nonnegative n_e,thermal,n_e,fast with sum matching ionic charge at relative2e-13/absolute1e-30. RR uses thermal electrons. No thermalization operation here.

Active H PI/RR,D PI/RR,and D0+H+<->D++H0 CX. Other declared populations are spectator stoichiometric zeros, not assigned physical rate0. Use Hneutral0,HionchiH,Dneutral0,DionchiD. Explicit potential descriptor must match all active thresholds/delta; reject old equal H/D thresholds with D43K CXheat. No invented spectator potentials needed for zero derivatives.

PI X: rate=nX0*GammaX; dX0=-rate,dX+=rate; fast+rate,thermal0; bind=chiX*rate; fastenergy=nX0*KX; absorbed=nX0*AX; thermalheat0. Primary electron energy is not secondary heat.

RR X: R=alpha(T)*nX+*n_e,thermal; dX+=-R,dX0=R; thermal-R,fast0; bind=-chiX*R; thermalenergy=-Kcap*R; escaped=(chiX+Kcap)*R; Kcap=kB*T*rr_energy_factor.

CX J=kf*nD0*nH+ - kr*nD+*nH0: dD0=-J,dD+=J,dH0=J,dH+=-J; all electron pools unchanged; bind=delta*J,thermalenergy=-delta*J. Accumulate event energies using math.fsum. Also report state-potential contraction difference scaled by constituent energies, not tiny cancellation remainder.

Eight nuclides and electric charge conserve exactly in integer stoichiometry. State pool residual d_e,all-d_e,thermal-d_e,fast and totalenergy bind+thermal+fast+escaped-absorbed vanish to stated FP tolerance. No anisotropic stress introduced.

## Bounded new inputs/execution

Explicit manufactured verification densities cm^-3:
n:0=0;H1:0=.8,H1:1=.2;D:0=2e-5,D:1=5e-6;T:0=0,T:1=0;
He3:0=8e-6,He3:1=1.5e-6,He3:2=.5e-6;
He4:0=.06,He4:1=.02,He4:2=.003;
Li6:0=4e-12,Li6:1=3e-12,Li6:2=2e-12,Li6:3=1e-12;
Li7:0=2e-10,Li7:1=1.5e-10,Li7:2=1e-10,Li7:3=.5e-10.

Exactly3z x T=[43,300,10000]K x fast-fraction=[0,.1]=18 point-source evaluations. Pure reaction checks may reuse those results. Lightweight checks allowed: delta0 analytic identity, exact integer conservation, mismatched potential, missing species, wrong electron pool sum, domain endpoints/violations, source identity. No further physical parameter campaign.

Inspect actual CPUaffinity/cgroup/RAM/processes before run. One cooperative lease and create-only run directory, worker1; BLAS/OpenMP/MKL/NumExpr1thread. Reserve CPU55 if present; worker affinity excludes55. No NCP/external dispatch. New science CPUcap60s,wall180s,RAM1GiB. One primary suite; failures return to root with raw results, no silent tolerance/model change. At most one root-authorized repair episode. OutputID C23E_D43_SOURCE_BINDING_20261024T<actualUTC>_v1 with mkdir(exist_ok=False).

Inherited known CPU13.331329114s is a tracked-lineage lower bound, not totalproject spend. Add actual measured new science CPU. Unmeasured CAS CPU, monetary spend and remaining budget null. Record requested/observed executor separately. ODE0,completedreruns0,benchmark0.

## Frozen acceptance

- Immutable digests match; providers pinned.
- Band Glo,Alo,B GL8/16/32 relative differences<=2e-10 using max compared positive moment. Report actual tiny-band rounding.
- New D Gamma,K,A reconstructed vs independent D quad relative<=2e-11, same C23B criterion.
- GammaD,KD,AD>0; bandmoments>=0; photoenergy residual/absorbed<=5e-14.
- Integer eight-nuclide/charge residuals exactly0. Floating nucleus/charge residual /sum absolute contributingevents<=2e-13, zero-scale exact0.
- Pool/totalenergy residual /sum absolute terms<=2e-13. Statepotential diagnostic /constituentenergy<=2e-13. Samepotential cycle algebraically0; mixed equal-threshold/D43K model rejected.
- All required failurecases refuse explicitly. Naive-filter diagnostic need not meet2e-11; measured defect is a useful output.
- Full coverage, finite-mass isotope corrections, empirical source uncertainty, cosmological admission and stopping remainOPEN; high-energy nuclear/generalgeometryHOLD. global_error_bound=null;global_completion_fraction=null.

## Artifacts, review, publication

Lower-tier owns implementation/d_binding.py,validate_d_binding.py, prescribed tests/input preparation, runs/newID/**,IMPLEMENTATION_NOTES.md,executionmanifest. Archive old hdx.py under history/superseded_v1. Preserve exact reusedbytes. Relativepaths and no import-time science/writes. Root owns theory/scientific decisions. Userrequested full selectedR/C track; one freshAstra read-only review before admission, at most one bounded repair by coder, then publish or scopedhold.

One useful static PNG+PDF showing fractional H-to-D moment shifts and naivefiltererror with explicit conditional/source labels; no added numericalcampaign. RawCSV+JSON, runnablecommand and source mapping. Publishpath research/cr_c23e_d43_source_binding_20261024/; no prior source edits.

New additive stacked DraftPR research/cr-c23e-d43-source-binding-20261024, expectedSHA writes; no merge/mainoverwrite. Central freshHEAD before updating only CR_N5 child/claim overlay, preserve parallelchanges. CanonicalZIP+manifest,Library/DropboxR3 as recoveryrelease; boundednewDriveattempt actualACKorUNKNOWN, preserveoldUNKNOWN_NO_ACK. Never claim triplebackup without actualevidence.

Each stage ledger EXECUTION | PUBLICATION | BACKUP | DAG. Final Korean report/copyablehandoff include actualSHA/PR/backupIDs,knownbudget,no-rerun and next executable node.
