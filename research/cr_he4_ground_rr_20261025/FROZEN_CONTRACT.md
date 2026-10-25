# He4 neutral-ground spontaneous RR on the saved H1 chain

Unit `CR_HE4_GROUND_RR_CONSUMER_NEXT`; named consumer
`CR_HE4_GROUND_RR_ON_H1_SAVED_CHAIN_V1`; workflow 1.0.0.
Current user request and root acceptance on 2026-10-25 authorize only this new
bounded changed-consumer verification. Historical budgets remain unchanged.

## Source, physical domain and frozen conventions

The added channel is He4+(1s) + tagged electron -> He4(1s2 singlet) + spontaneous
photon. C23B's exact Verner96 `HeI` smooth fit and REI151's electronic Milne
convention are reused. Native I=24.59 eV, g_bound=1, g_ion=2,
d=2*g_ion/g_bound=4, capturing-ion density=0.02 cm^-3. The finite PI photon
support is [24.59,50000] eV. E=0 and unsupported energies are rejected.
The HeI smooth ground-channel interpretation is the adopted REI151/C23B model;
exact experimental residual-ion-state resolution is a conditional model
assumption. Conditional elemental He -> He4 mapping is retained.

T=10000 K, theta=0.8617333262145178 eV, thermal ne=0.14 cm^-3,
lnLambda=20, HI/HII/HeI/HeII/HeIII=(0.9,0.1,0.07,0.02,0.01) cm^-3,
stationary common Maxwell baths, stationary-heavy-target, zero recoil,
nonrelativistic electron, closed box, proper seconds. Constants are
m_e=9.1093837015e-31 kg, c=299792458 m/s, 1 eV=1.602176634e-19 J.
Actual photon occupation, stimulated and all-level RR, finite-mass
relative-target averaging, angular emission, and post-capture feedback remain
separate inputs. HeIII capture is a candidate, outside this single-channel unit.

For E>0, epsilon=E+I inside native support,

    sigma_RR_cm2 = sigma_PI_cm2(epsilon)*epsilon^2/(d*m_e*c^2/eV_J*E)
    lambda_He_s_inverse = n_HeII_cm3*100*sqrt(2*E*eV_J/m_e)*sigma_RR_cm2.

The target density is not ne. No numerical floor, threshold substitution,
source extrapolation or excited/all-level RR addition is admitted.

## Inputs and exact new problem

Recover the H1 canonical archive `BASS_CR_N5_RR_MILNE_CANONICAL_20261025_V1.zip`,
18232953 bytes, SHA256
`f1afdb40303b28a498a62f9f8d38858b8bea584d0ed8a4e63bd87e4e11d362c5`.
Its manifest and the 21 copied immutable input files are hash-verified.
Reuse eight PR104 NPZs, eight PR105 H1 NPZs, three384-atom C23D pulse sources,
and the exact C23B point provider/table. No source/thermal quadrature, old
generator construction, old solve, projection or ODE is rerun.

K_H1 is the stored PR105 `K_diag,K_lower,K_upper` matrix. These stored binary64
values define this numerical baseline exactly. The intended new operator is
the real sum K_new=K_H1+diag(lambda_He). Its binary64 diagonal addition loss
is recorded. Independent Decimal70 forms Decimal(K_H1_saved)+Decimal(lambda_He),
not Decimal(rounded K_new). The original H1 intended-versus-rounded diagnostic
is inherited evidence and is not silently redefined.

Eight cases have chi={1.5,3}, U/theta={40,80}, nominal N={1024,2048}.
Their E grid, PR104 source projection/masks, off-diagonals, first6 and bath6
RHS are immutable. H1 capture remains present, with I_H=13.60 eV and its
stored hazard; adding a second independently solved RR probability is invalid.

Per case solve 24 new RHS, for 192 primary RHS total:

* 16 physical RHS: first6, H1 lambda and lambda*E, He lambda and lambda*E,
  six signed bath rewards.
* Four conditional-time RHS: the two CE probabilities and H1/He probabilities.
* Three cancellation-free responses: -K_new^-1[lambda_He*(old CE,old time,
  old H1 RR probability)].
* One w=K_H1^-1 lambda_He.

With p=K_new^-1 lambda_He and eta=max(w), positivity gives
w/(1+eta)<=p<=w. The active stopping partition is
p_entry+p_CE_s+p_CE_p+p_H1+p_He=1. Changes in CE, stopping time and H1
capture are nonpositive and computed through response equations, not near-equal
subtraction. The latter remains a numerical diagnostic only.

## Number and energy owners

For each He event, DeltaN_fast_e=-1, DeltaN_HeII=-1, DeltaN_HeI=+1,
DeltaN_photon=+1. Charge and He nuclei are conserved. The signed energies are
-E (electron removal), -(24.59 eV) atomic internal, +(E+24.59 eV) photon;
their sum is zero. H1 uses its distinct13.60 eV binding value.
The stopped final-energy account includes six signed baths, first-entry kinetic,
CE outgoing kinetic/internal, H1 retained photon/internal, He retained
photon/internal, and unchanged initially inactive kinetic. Electron removal is
a diagnostic, not an additional final reservoir. Retained photons are not heat.
This is frozen-background first-event accounting; caloric partition is not
irreversible assimilation or coupled composition/temperature evolution.

## Frozen acceptance and independent review

Reuse H1 criteria unchanged: per-RHS backward residual<=2e-12,
partition maxabs<=2e-8, scaled total energy<=2e-8, probability tolerance2e-10,
strictly positive added RR for positive density, relative rare-bound<=5e-10,
event-scale signed-energy<=5e-13. Controls cover wrong density, factor,
threshold, finite support, missing/NaN values, channel identity, zero target,
stoichiometry, binding sign and a small shared-competition analytic example.

For every chi,z compare N1024/2048 at each R and R40/80 at N2048.
Relative grid<=0.005 and boundary<=1e-5 for added RR probability,
conditional kinetic/photon energy/time, separate photon/internal rewards,
updated H1 probability, CE probability and mean time.
Stable paired CE/time/H1 changes use grid<=0.01 and boundary<=1e-5.
These are finite-grid comparisons, not global error bounds.

Independent reviewer imports no production module and checks both R80,N2048
cases, all24 RHS per case in Decimal70 (48 total), plus selected independently
computed He coefficients. Each solution column uses its own infinity norm,
relative criterion5e-10. The R6 source/theory decision precedes primary launch.
Actual failures are retained without changing thresholds.

## Bounded execution and state

New unit ceiling30 CPU seconds including failed attempts; controls<=5 CPU,
primary<=8 CPU, independent review<=10 CPU, optional saved-only plot<=5 CPU.
Each invocation wall<=60 s, one native thread, RLIMIT_AS512 MiB.
Actual cgroup quota/affinity and conservative clean inactive-file reclaimability
are checked; reserve1 GiB and CPU8 for the coordinator, workerCPU0,
independent reviewerCPU2. Own-task leases are create-only. Resource measurements
and exact source snapshots accompany every run. No unrelated process is killed.

Historical known H1 lineage39.097868524 CPU s and separate C23E15.493261114 CPU s
are preserved, not summed without overlap evidence. Unused old allowance is
not reused. Global remaining/currency/error/completion are null.
N4/N5 remain PARTIAL_OPEN and N6/N7 PREDECESSOR_GATED. Publication and backup
are root-owned axes, separate from scientific checks. Dense NPZ/native tables
are private backup inputs; public source and integrated results are separate.
No new strong no-go is proposed (NG1-NG7 not applicable).
