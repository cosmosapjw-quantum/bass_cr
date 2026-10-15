# C17: competing HI/HeI/HeII absorption events with time-varying source and opacity

## Protected physics and code authority

Git baseline bass_cr C16: df39cd31447a405e4dbaac273369e34c57b7ed72.
Read-only rei_bianchi reference: 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
C11 owner source/Scenario/C8 SHA checks are preserved. Signature (-,+,+,+).
Photon N, species events and energy moments are normalized per original
hydrogen nucleus; local proper time dt in seconds, species rates lambda_j
in s^-1, source S in photons/H/s, physical photon energy eV.

C16 integrates the TOTAL photon survivor accurately for a local linear
time-variable source and total opacity but assigns absorbed events among
HI, HeI and HeII using a single positive *effective rate fraction*.
When species rates evolve in opposite directions this assigns events to
the wrong gas even when total photons are conserved to machine precision.

## Theory: exact time-ordered species reaction formula

For t in [0,h], species j in {HI,HeI,HeII}:

  lambda_j(t)=lambda_j0+(lambda_j1-lambda_j0)*t/h >= 0.
  Lambda(t)=sum_j lambda_j(t), S(t)=S0+(S1-S0)*t/h>=0.

The local photon equation is dot N(t)=S(t)-Lambda(t)*N(t).
Its formal nonnegative solution is

  N(t)=N0 exp[-integral_0^t Lambda(v)dv]
        + integral_0^t S(s)exp[-integral_s^t Lambda(v)dv]ds.

The number of photoionization events in species j is

  A_j = integral_0^h lambda_j(t)N(t)dt
      = A_j^old + A_j^source,

  A_j^old=N0 integral_0^h lambda_j(t)exp[-integral_0^t Lambda]dt,
  A_j^source=integral_0^h dt lambda_j(t)
                 integral_0^t ds S(s)exp[-integral_s^t Lambda].

All integrands are nonnegative, so A_j>=0. Exact summation gives
sum_j A_j=N0+integral_0^h S(t)dt-N(h).
This is NOT a generic exact formula for full cosmological ray transport:
the equation is a single local photon channel with specified rates.

Wolfram independently returned the linear-rate optical depth identity
  integral_s^t Lambda(v)dv =
  (t-s)[Lambda0+(Lambda1-Lambda0)(t+s)/(2h)].
The positive nested Gauss integrator uses optical-scaled nodes:
- Old photons: time since interval start t/h scaled by the old-photon
  extinction length, capturing arbitrarily large initial opacity.
- New photons: for each reaction time, integrate the past time of birth
  backwards with the local optical depth, obtaining N_source(t), then
  integrate lambda_j(t)N_source(t).
Both integrals are vectorized over photon packets, with bounded
chunks to control memory. User-controllable outer/inner nodes allow
convergence and performance studies.

## Positivity and numerical conservation

The total photon survivor is computed independently with C16
positive optical quadrature. The same positive species reaction
integrals return A_j^old and A_j^source. They need not sum to the
exact total photon losses at finite numerical quadrature resolution.
For EACH of old and source contributions separately, the measured
nonnegative species time moments are multiplied by
  (exact total loss)/(sum of independently quadrature events).
This preserves positive attribution and closes the total photon
ledger. It is a numerical normalization of finite quadrature,
NOT a claim that the species integrals are exactly evaluated.
The raw relative moment defects are exposed in diagnostics and
a separate 1e-3 numerical fidelity budget rejects insufficient
quadrature, without changing physical science gate tolerances.
Only EXACT zero-opacity channels use the mathematical N_end=N0+
h(S0+S1)/2, A_j=0 branch, avoiding subtraction roundoff false events.

## Constructive counterexample: C16 species swap

Let h=1, initial photon/H=1, S0=S1=1, total Lambda=100.
HI rate 100 -> 0, HeI rate 0 -> 100, HeII=0.
Both methods produce N_final=0.01 and total absorbed photons=1.99.
However C16 effective-rate fraction yields
  (A_HI,A_HeI,A_HeII)=(0.5099,1.4801,0),
while C17 directly integrated values are
  (1.4801,0.5099,0),
consistent with independent Radau N+species-events ODE.
The discrepancy of 0.9702 photons/H in EACH of HI and HeI
demonstrates that total photon conservation is insufficient to
establish accuracy of species ionization and photoheating.

## Actual owner-anchored Bianchi I source and threshold test

Use owner Scenario.rate(a), H(a,q), 50000K BB spectrum,
n_H(a) proportional to a^-3, physical Bianchi-I photon redshift,
actual Verner HI/HeI/HeII fits.
Five manufactured birth-frame source channels at a0=.1:
E=(14,20,32,70,90)eV, mu=(-1,-.5,0,.5,1),
fixed gas fractions (.9,.85,.15 of respective H/He species),
time interval a=.1..11. The exact threshold crossing for
E=14eV and HI chi=13.6eV is explicitly inserted into the
log-a time grid. This is a *five-channel manufactured source
allocation*, NOT the actual SOURCE07 spatial age-resolved ray set.

Reference independent SciPy Radau integrates 5 photon occupations
plus 15 HI/HeI/HeII cumulative event equations in ln a.
The C16 and C17 survivors agree for the same source and total
opacity. But species event totals differ:

   q=0, time steps:       8       16       32       64      128
   C16 max rel error:  0.003876  0.002041 0.001024 0.000511 0.000254
   C17 max rel error:  0.0000611 0.0000164 0.00000411 0.00000103 0.000000261

C16 is first-order-like in time for species allocation, whereas
C17 is second-order-like. Signed q=-.01,0,+.01 show the same
scoped pattern. The owner gas fractions remain fixed.
No real evolving ionization/thermal/OTS feedback has yet been
integrated into this C17 photon/source reference.

## Species reaction temporal moments and physical heating

For each j, additionally compute
  M_j=(1/h) integral_0^h t lambda_j(t)N(t)dt.
The integrand and source/old decomposition use the same positive
Gauss quadrature and normalization as A_j. Under the linear local
energy approximation E(t)=E0+(E1-E0)t/h, one obtains the
photoelectron heating moment per original H:

  Q_j=(E0-I_j)A_j+(E1-E0)M_j
      =(E0-I_j)(A_j-M_j)+(E1-I_j)M_j.

When E0,E1 >= physical binding I_j and A_j>=M_j>=0, the
second form is explicitly nonnegative.
If physical E crosses binding inside an interval while reaction
rates remain nonzero, the code FAILS with an explicit requirement
to split at the threshold. Numerically checked against an
independently integrated Radau state comprising N, A_j, M_j,
and Q_j for synthetic but nontrivial affine rates/energies.
This is a temporal heat moment for the local affine problem,
not a complete thermal-gas evolution law or a claim of heating
after collisional cooling/secondary ionizations.

## Optimization, reproducibility and admission

The high-order vectorized kernel uses bounded chunks and
outer/inner positive Gauss rules (standard 64x48; exploratory
fast 32x24). 4096 owner-Verner sample packets:
C16 total-photon/approx species ~0.0060 s median;
C17 standard 64x48 ~0.7424 s median;
C17 exploratory 32x24 ~0.0899 s median (three trials).
This is an accuracy/compute tradeoff, NOT a speedup compared to
the scientifically inaccurate C16 species allocation. At all
three owner q and n32,64,128, reduced 32x24 C17 species error
agrees with standard within the observed tested range; raw
positive quadrature conservation mismatch is separately recorded
to prevent generalizing to arbitrary opacity histories.
Independent OS three-q C17 benchmark ~4.57 s with 1 process,
~2.48 s with 3 processes (3-trial medians), with identical results.
No claim on full Rust SOURCE07 production throughput.

The mathematical kernels are separately tested with 0/large
opacity, changing species rates, photon balance, negative-input
rejection and external Radau ODE, and parent C10-C16 tests.
Native subagent unavailable (NOT_RUN); local Codex not used.

## Next scientific gate

Connect the *actual* owner SOURCE07 birth-age/ray photon stock and
the single-application R J_Omega frame mapping. Then couple the
time-variable species photoevents and photoheating to the
original igm_rates+igm_thermal H/He network, OTS and photoelectron
degradation/secondary ionizations. Test evolving gas with
independent stiff reference, proper energy work and threshold
events, then compare xHI(z),HeII/HeIII(z),Tg(z).
Global scientific EoR admission remains HOLD.

Literature context, not originality claims:
Friedrich et al. 2012, MNRAS 421 2232,
doi:10.1111/j.1365-2966.2012.20449.x, photon-conserving C2-Ray
multifrequency/He OTS and thermal timestep constraints.
Norman et al. 2015, ApJS 216 16,
doi:10.1088/0067-0049/216/1/16, fully coupled radiation/
chemistry operator splitting.
