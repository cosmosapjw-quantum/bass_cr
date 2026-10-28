# Atomic authority contracts — 2026-10-28

Status: theory derived; new coding execution NOT_RUN pending root delegation. These are two additive bounded units, not owner-branch edits. Latest inspected owner identities are WU PR150 ec352ac1328d59e7525530f3fc300bcf22f60f33 and CR PR116 527840221887e9777031f2a6f281d48cb1ac42ef. Recheck before publication: CR116 was actively finishing coding, with an 18/20 payload and no adopted final review observed. Central authority and admission remain root-owned.

## WU_CUBIC_RATIONAL_DOUBLE_ROOT_PREPROCESS_V1

Scientific blocker: R15 accepts supplied nonnegative Bernstein-B3 coefficients. A nonzero cubic with an interior double zero cannot have all nonnegative B3 coefficients on the original cell: every B3 basis function is strictly positive in its interior, so p(r)=0 would force all coefficients zero. R15 NEXT_INPUT_CONTRACT explicitly proposes broader pointwise-nonnegative cubic preprocessing and reports it unstarted.

Frozen domain: x=(t-t0)/(t1-t0) in [0,1], t1>t0. Input p(x)=(x-r)^2(a*x+b), exact rational a,b,r, 0<r<1, b>=0, a+b>=0. p carries forcing units (inverse clock time for a fraction); x,r are dimensionless. Include p=0. This is the supplied factorized rational-double-root family, not a factor finder or the full nonnegative cubic domain. Caller retains actual original time/history and source/state/clock provenance. No physical HD activation.

Derivation: Split at x=r. For each interval [u,v]=[0,r] or [r,1], use y=(x-u)/(v-u), q0=u-r, q1=v-r and l0=a*u+b, l1=a*v+b. The squared affine has B2 coefficients Q=(q0^2,q0*q1,q1^2), all nonnegative because the interval does not cross r. The affine factor has B1 coefficients (l0,l1), nonnegative by endpoint positivity on [0,1]. Bernstein product identity gives B3 coefficients

 c0=q0^2*l0;
 c1=(q0^2*l1+2*q0*q1*l0)/3;
 c2=(2*q0*q1*l1+q1^2*l0)/3;
 c3=q1^2*l1.

All are nonnegative and reconstruct exactly p(u+(v-u)y). At the new knot both one-sided values equal zero. Original source primitive is preserved: integral_[u,v] p(x)dx=(v-u)*(c0+c1+c2+c3)/4. Physical time integral multiplies by t1-t0 once. Keeping the original t0 memory is required; subdivision changes representation only.

Implementation contract: accept exact integer/rational strings only, reject floats, r outside strict interior, negative affine endpoint, nonpositive time span. Input numerator/denominator <=64bits, <=16 cases, output <=4096bits. Output original interval identity, split knots and two B3 coefficient arrays, exact power coefficients, exact integrated forcing. No R15 source imports, convolution campaign replay, ODE or CAS required. Production method uses product coefficients; independent reference expands the power polynomial and integrates that expansion directly, using Fraction.

Frozen fixtures (r,a,b): (1/2,1,1), (1/3,-1,1), (2/3,1,0), (1/2,0,1), (1/4,0,0), (1/1024,3,2), (1023/1024,-2,2). Time mapping t0=2,t1=5 in clock seconds for all; coefficients in s^-1. Controls: first three are true cubic; quadratic limit; identically zero; near-boundary rational roots; negative endpoint; outside root; malformed/float; zero time span. Require exact coefficient equality, nonnegativity, shared root value zero, integral equality and whole-domain polynomial equality (coefficient identity, not sampling). For nonzero cases verify unsplit B3 has at least one negative coefficient. No floating tolerance. C6/C7 counts must be produced from real checks, not prefilled.

Allowed output root: /workspace/scratch/d855c1e0c0ed/orchestration_20261028/units/WU_CUBIC_RATIONAL_DOUBLE_ROOT_PREPROCESS_V1. Create-only primary.py, independent.py, INPUTS.json, PRIMARY.json, REFERENCE.json, resource receipts, result report. Exact commands after implementation: python3 <unit>/primary.py --input <unit>/INPUTS.json --output <unit>/PRIMARY.json; python3 <unit>/independent.py --input <unit>/INPUTS.json --primary <unit>/PRIMARY.json --output <unit>/REFERENCE.json. Root's bounded runner must wrap each command. Proposed new allowance: total10 CPU-s inclusive both workers/coordinator, wall20s each,256MiB,1worker/thread, one primary and one independent attempt, at most one diagnosed targeted repair within same total. Stop on unexpected identity/domain/arithmetic or budget failure; preserve originals. Estimated work <1CPU-s each, not measured. Historical budgets null/separate and no transferred old allowance. R6/C9 fresh independent authority review required before admission.

Claim gate after acceptance: exact preprocessing for the frozen rational-double-root family, enabling conditional R15-compatible positive-cell representation. Full-A/whole-forcing/source-clock assumptions remain unbound physical dependencies. Central/physical completion delta0. Generic nonnegative cubic and irrational roots remain separate work.

## CR_SAME_BIN_HL_CORRECTED_JOINT_FACET_V1

Scientific blocker: PR116 exact polygon assumes every allowed positive-mass high-low pair is cross-bin; actual K=1,3,10 are explicit rejection targets. Build a conservative joint inequality valid with same-bin HL edges, without modifying or duplicating active PR116's exact-region implementation.

Frozen domain: finite <=4 atoms, nonnegative rational masses a_i and energies E_i in eV, integer bins, K>=0 eV. All unordered pairs E_i+E_j<=K including diagonal2E_i<=K; singles always allowed. Pair masses consume one marginal from each distinct atom or two from a diagonal. Atom masses have source coefficient units m^-3 s^-2 under q=t*a; sums d,C,L,S share these units. Low means2E_i<=K. Let S be maximum capacity-limited matching mass using ONLY same-bin high-low edges. It can be certified by exact bipartite min-cut enumeration for these <=4-atom controls, no external solver needed.

Derivation: no high-high pairs exist. Write m_s,m_c for same-bin and cross-bin HL mass and r_s,r_c for same-bin and cross-bin LL mass. Then d=m_s+m_c+r_s+r_c, C=m_c+r_c, and used low mass U_L=m_s+m_c+2r_s+2r_c<=L. Thus 2d-C=U_L+m_s-r_c<=L+m_s<=L+S. Combined with nonnegativity, C<=d, total-double bound d<=D=(L+M)/2 where M uses all HL edges, this yields d<=min(D,(L+S+C)/2). These are valid upper bounds; generic sufficiency or joint attainment is not asserted. For S=0 recover the PR116 facet.

Observable implication: retain I1=24.59eV,I2=54.42eV, W=integral t dt>=0. At a feasible fixed C, parent event count W(N-d)>=W[N-min(D,(L+S+C)/2)], and chemical energy W[I1*N+(I2-I1)*d]<=W[I1*N+29.83*min(D,(L+S+C)/2)]. Units m^-3 and eV m^-3 respectively. W=0 gives zero; no division by W. No source/bath replacement, actual K or exclusive kernel supplied.

Frozen fixtures (energies,masses,bins,K): A=([1,3],[1,1],[0,0],4) has L=1,S=M=1,D=1 and witness p01=1,d=1,C=0, saturating new facet and violating old 2d-C<=L. B=([1,3],[1,1],[0,1],4) has S=0,M=1 and p01=1,d=C=1. C=([1,1,3],[1,1,1],[0,1,0],4), D=([0,2],[2,1],[0,0],0), E=([1,3],[0,1],[0,0],4), F=([1,3],[1/2,3/2],[0,0],4). Add permuted C, same energies with K=3 strict exclusion, and all-zero masses. Domain rejection controls negative mass/energy, duplicate key, negative K, >4atoms. Exact units are conditional controls, not measured native arrays.

Production: enumerate HL cuts to obtain M,S: each source-high arc capacity a_h, each low-sink capacity a_l, allowed interedge capacity N=sum a_i; enumerate source-side subsets of high+low vertices; min cut exactly. Construct the explicit A/B witnesses and compute the new bound/observable ranges. Independent: form full marginal system over singles and every allowed pair; enumerate basic feasible solutions selecting n columns (singles ensure rank n), solve exact rational linear equations independently, reject negative solutions, and verify inequality for every vertex. Compute maximal 2d-C-L and compare <=S, not equality in all cases. Verify witness marginals/support and inequality for rational mixtures. <=4 atoms implies <=14 columns and <=1001 bases per case. Avoid production imports and do not use the proposed facet to generate the feasible vertices.

Allowed root: /workspace/scratch/d855c1e0c0ed/orchestration_20261028/units/CR_SAME_BIN_HL_CORRECTED_JOINT_FACET_V1; same filenames and exact command form as WU. Proposed new total10CPU-s, each wall20s/256MiB,1worker/thread, primary1/reference1 and at most one diagnosed targeted repair within same total; estimated <2CPU-s each, unmeasured. No native3200 graph, no sourcefit/RR/ODE, no activePR116 edits, no prior allowance transfer. Stop on failure, preserve original. Acceptance exact rational only, complete vertex coverage counts/hashes and explicit A counterexample; fresh independent C9 before adoption. This is an upper-bound extension and scope counterexample, not a strong no-go or full general polygon claim.

## Frozen additive input/resource clarification

CR rational numerator/denominator <=64bits; derived rational numerator/denominator <=4096bits; <=9 accepted frozen fixture cases, <=4 atoms. Save actual enumerated basis/accepted vertex counts. Guards are additional rejection evaluations, not extra scientific fixture solves. Both bounds and fixture cases are fixed before execution. CR owner subsequently advanced to98174c29b98439f70f4cf14c8510f88c6a538c4f, with raw C09 admission PASS_SCOPED and workflow19/20; C10 delivery pending. This new bound remains outside the admitted all-HL-cross polygon's domain and does not alter its inputs.

## Stage handoff

R1 scope and R2 current exact-source review completed as recorded; R3 definitions, R4 selected representations and R5 derivations above are supplied. R6 independent authority review and R7 executed controls remain pending. R8 provisional use decision is bounded coding candidate, R9 contract supplied; R10 checkpoint is this file. C1-C4 may bind this contract; C5-C8 require actual delegated implementation/commands/results; C9 must use a fresh reviewer; C10 requires accepted result and root publication receipts. Do not mark all20 complete before these obligations occur.
