# HeIII ground RR on exact stored PR106 HeI chains — frozen consumer contract

Unit: CR_HEIII_GROUND_RR_ON_HEI_SAVED_CHAIN_V1. This user requested the next
full R1–R10 and implementing C1–C10 cycle on 2026-10-27. A new bounded local
30 CPU-second ceiling covers changed-consumer science, including failed attempts.
Historical allowances are not transferred. Root owns publication and preservation.

## Physical and source identity

He4III + tagged fast electron -> He4II(1s) + spontaneous retained photon.
Use native Verner96 HeII row (Z,N)=(2,1):
I=54.42 eV, Emax=50000 eV, E0=1.720 eV, sigma0=13690 Mb,
ya=32.88, P=2.963, yw=y0=y1=0. g_bound=2, g_ion=1, d=1.
Target density n_HeIII=.01 cm^-3. Electron-bath density .14 cm^-3 is distinct.
Fixed T=10000 K, theta=.8617333262145178 eV, lnLambda20,
HI/HII/HeI/HeII/HeIII=(.9,.1,.07,.02,.01) cm^-3 are inherited.
Use m_e=9.1093837015e-31 kg, c=299792458 m/s, eV_J=1.602176634e-19.
Conditional elemental-He-to-He4 mapping; stationary heavy target, zero recoil,
nonrelativistic scalar, ground spontaneous only, frozen baths, closed box,
proper seconds. No new stimulated, total/excited, finite-mass or angular model.
Table SHA256 a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389.
Point-provider SHA256 71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d.

For positive E and E+I in native support:
sigma_RR = sigma_PI(E+I)*(E+I)^2/[d*(m_e*c^2/eV_J)*E] in cm^2,
lambda = n_HeIII*100*sqrt(2*E*eV_J/m_e)*sigma_RR in s^-1.
Reject missing, boolean, nonfinite, negative or unsupported physical inputs.
A zero target density is an explicit control and yields zero count/energy;
its conditional moments are null. No rate floor or source extrapolation.

## Exact numerical baseline and inputs

K0 is exact stored PR106 HeI K_diag/K_lower/K_upper from previous source
S=4caf4273eefd51f2c605a8667c3533d8489dd0f5, D=b11b2e9255f2b10fb5582376412e045bd1e9151c.
The prior archive SHA256 is 7e39930b862a0af5f87e5d3e4dd9d9fa4b37694dda496221e6e311957a087aaa.
Its historical HeI addition loss is inherited. New intended K1=K0+diag(lambda).
Independent Decimal70 forms Decimal.from_float(K0_diag)+Decimal.from_float(lambda),
not Decimal.from_float(rounded K1_diag). Record new diagonal addition loss.

Reuse all8 old PR104 source/grid/RHS files, all8 PR106 HeI result files,
three384-atom source CSVs and the original point provider/table. Bind their exact
bytes in the new input manifest. Old H1, HeI, CE, EE/EI/neutral generators,
source projections, quadrature and completed primary solves are not replayed.
A new w RHS on old K0 is a new diagnostic, not an old reward solve.
Cases chi={1.5,3}, R={40,80}, nominalN={1024,2048}; actual array lengths govern.
Stored source_z={2.316,2.479,2.649}, masks and p[0] boundary mass are unchanged.

Physical18 columns: first6, H1 count/kinetic2, HeI count/kinetic2,
new HeII count/kinetic2, signed bath6. Conditional5 columns use physical
indices[0,1,6,8,10]. Stable4 RHS use -lambda*storedHeI[CE,time,p_H1,p_HeI].
One w=K0^-1 lambda. Total28 percase/224 primary RHS;24 source-weighted rows.
Independent review: two R80,N2048 cases, all28 columns each/56 RHS.
Each column uses its own infinity norm. Conditional RHS use independent solutions.
New coefficient samples are computed without importing production modules.

## Observables and event ownership

One shared K1 determines entry+CEs+CEp+H1+HeI+HeII probabilities.
The single-added-hazard bound is w/(1+max(w))<=p_new<=w.
Stable responses are stored-column responses; prior solution residual terms in
THEORY_KO.md distinguish them from exact old-to-new differences.
Conditional E/time ratios have no assumed monotonicity.
Signed event energies: fast=-E, internal=-54.42, retained photon=E+54.42 eV.
Final stopped-energy bookkeeping uses photon+internal and does not add the
fast-removal diagnostic a second time. Three RR binding energies stay distinct.

Export a source-qualified per-event template plus integrated count m^-3 and
integrated energy J m^-3. Convert count cm^-3 by10^6 and energy eV cm^-3 by
10^6*eV_J exactly once. Rate, exposure and instantaneous RHS are null unless
an independently admitted time history is supplied; this unit supplies none.
Each canonical integrated event ID is unique in one book; mixing frames fails.
Native21 He4III12->He4II11, fast count-1, retained photon+1. For explicit positive
nb[m^-3], use a=Ncap_SI/nb, DeltaY=a(e11-e12), Deltazeta=-a,
Deltaw_nt=-Ue_SI/nb, Deltaw_ext=0, DeltalogT=0 with a separate retained-photon port.
Without nb, leave per-baryon projection null. Do not inject the PW19 donor nb,T.
Moment-equivalent mean photon energy is not a monochromatic emission spectrum.
This is an integrated diagnostic return, not a finite coupled abundance update.

## Fixed acceptance

Per-RHS scaled backward residual<=2e-12, partition maxabs<=2e-8,
scaled total energy<=2e-8, probability tolerance2e-10, event-scale energy<=5e-13,
integrated external-energy scaled residual<=2e-13,
relative rare-bound<=5e-10, independent own-column difference<=5e-10,
independent new-coefficient relative difference<=5e-13.
For everychi,z compareN1024/2048 atR40and80 andR40/80atN2048.
Grid relative<=.005 for newcapture/conditionalE/photon/time/rewards and updated
oldprobabilities/mean time. Stablepaired response grid<=.01. Domain relative<=1e-5.
These finite grid/domain comparisons leave global physical error bound null.
New controls target actual changes: native row/density/d, zero/signed/unsupported
inputs, shared3RR competition, stable signs, explicit18/5/4indices,
energy stoichiometry, native25/retainedport, SI conversion, integrated-vs-rate,
duplicate/frame/source identity. Do not rerun unchanged old suites.

## Resource reservations and preservation

Controls<=5, primary<=8, independent<=10, plot<=5, localmisc<=2 CPU seconds;
unit aggregate<=30 including failures and coordinator time. Per invocation wall<=60s.
Native libraries1thread, RLIMIT_AS512MiB, conservative clean-cache memory estimate,
minimum1GiB reserve, distinct worker/reviewer/coordinator affinity, own create-only
lease. Retain every started attempt; missing/nonfinite/negative/boolean prior cost
is UNKNOWN_PRIOR_ATTEMPT_BUDGET and blocks reuse until recovered.
Do not kill unrelated processes or infer NCP/scaling execution.
Wolfram exact-rational check is one separately recorded20s remote time-constrained
call; provider CPU is unavailable and not reported as zero.

N4/N5 stay PARTIAL_OPEN; N6/N7 stay PREDECESSOR_GATED. Original central88-node
count is unchanged by this child. Globalcompletion/error/budgetremaining/currency
are null, L4=false. Caloric partition and retained photon are not physicalheating.
Preserve each old budget and UNKNOWN_NO_ACK record; observed10/26backfill is new
storage evidence. Publication uses expected-SHA non-force updates. Each stage has
immutable checkpoint ZIP and independent Dropbox+Drive receipt; source-release
and changed authority objects receive actual scoped R3 readback at closeout.

## Frozen implementation details at R9

Actual source exports set nb_m3=null. The explicit-positive-nb control alone tests
the per-baryon map. Independent coefficient samples are the preselected indices
{0,n//4,n//2,3*n//4,n-1} in each of the two finest cases. These ten samples
use the native row without importing production modules. C6 records its positive-nb
example so C9 can independently verify the actual exported vector and photon port.
This contract is frozen before any new local scientific worker starts.
