# Le–Cambier H1 CI source-defined reference

`lc_ionization.py` independently implements the ground-state Eq.85 kernel of Le & Cambier (2016), DOI10.1063/1.4953050, with the explicitly isotropic angular law in §III.E. It is a semiclassical stationary heavy-target approximation. It does not validate the real H1 angular distribution or copy the authors' software. No CCC normalization, energy table, fitting coefficient, RR, nuclear channel, or cosmological IVP is imported.

```python
from lc_ionization import LCModel, sigma_m2, transfer_u
out = LCModel().evaluate([2000., 20000., 200000.])
# out.moments_SI has rows (alpha,beta,gamma,delta), with E in joules.
cross_section = sigma_m2([0., 13.6, 27.2])  # m²
upsilon = transfer_u(27.2, [0., .5, 1.])   # eV
```

All evaluations validate real finite binary64 inputs. A scalar temperature becomes a one-row result. Nonempty1-D arrays are accepted. Booleans, complex values, strings/objects, empty T arrays and out-of-domain temperatures are rejected. Returned arrays use immutable byte storage. Model parameters are fixed. The numerical T contract is2000–200000K; it is not a physical accuracy envelope.

Constants EV_J,KB_J_K,ME_KG,A0_M are copied unchanged from HE36 `maxwellian_moments.py` SHA256`644260261b82d6a528fd049b2bb20702e4c66de087406c7868a395a41ec99c2c`. This component owns those four constants once, avoiding import-time dependencies on an older research directory. The source threshold I=13.6eV is kept. The paper's rounded a0=.529Å is deliberately refined to the pinned HE36 a0=5.29177210544e−11m; therefore source-native denotes the same functional kernel with a documented constant refinement, not a bitwise reproduction of rounded source constants. `MODEL_IDENTITY` binds constants, source PDF hash, algorithm, domain, normalization and approximation policy. Execution receipts independently hash the actual code bytes.

## Equations and normalization

For E>I, sigma(E)=4pi a0² I(E−I)/E². At0≤E≤I sigma=0. The ordered transfer law is p(Upsilon|E)=IE/[(E−I)Upsilon²] on[I,E], so E1=E−Upsilon,E2=Upsilon−I and E1+E2=E−I. Its angular density is G=1/(16pi²). The two outgoing electron contributions are summed; there is no factor2 in the event cross section. The conditional PDF rejects E=I because its event probability is zero; the quantile returns the degenerate limit Upsilon=I. Differential cross sections return0at/below threshold.

Writing theta=kBT, x=I/theta and C=sqrt(8/(pi me))(4pi a0² I)theta^(−3/2), the Maxwellian moments are alpha=Ctheta E2(x),beta=Ctheta²exp(−x),gamma=beta(I+2theta),delta=beta(I²+4Itheta+6theta²). `scipy.special.expn(2,x)` evaluates the positive E2 integral without subtracting nearly equal exp(−x) and xE1(x). These are all-energy moments of this approximate nonrelativistic kernel, not finite-table partial moments. Source code exposes the energy-weighted incoming STF coefficient kappa2=4gamma/(15theta²); its use as a net STF coefficient requires the selected isotropic outgoing model and the infinitesimal Grad assumptions.

No quadrature, benchmark, plot or model evaluation runs on import. `verify_provider.py` is an explicit new affected test program. It saves timestamped receipts and exact input/code identities, returns existing identity-matched completion without replay, and preserves failures. Supported `--group` names permit only the affected group to run after a named correction. Root-owned later diagnostics and benchmarks are separate.

## Original-source boundary

PDF SHA256`5ee591cde0cb90c03b5fc47a8ad439bae93bcc36bd05a4cbb4e1943fec93fc68`; equations audited: Eq7(p5),Eqs11–12(p7),§III.E(pp14–16),Eq85(p25). Source PDF is not redistributed in this package. Metadata and source admission details are in the separate HE37 source report. Low-order source consistency, numerical integration accuracy and calibrated physical cross-section accuracy are distinct claims.
