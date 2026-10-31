# BASS-CR PHYS23: original event-weighted conditional Bianchi-I Lyα null and screen transfer

Date: 2026-10-31 KST. This package is a **new physical-model calculation**, not a rerun of PHYS22, numerical optimization or standalone code refactor. Its source normalization and E1 polarization are inherited from exact frozen PHYS22 inputs, while the metric shear is explicitly a conditional geometry, not a solved source-compatible Einstein–Boltzmann IVP.

## Immutability/provenance

- Immutable parent `cosmosapjw-quantum/bass_cr` Draft PR #147 HEAD `fac9a25d53468502b3807da2034e4bfa99325c8f`. Original H1s→2p excitation events 2066, source PR143 Git blob SHA1 `d7034188ca5a02dc37db24aaf8f7d550624567bd`. Previous original 6CCO model PHYS21 source momentum tables unchanged.
- Parent PHYS22 ZIP `BASS_CR_PHYS22_E1_OBSERVER_FRAME_SCENARIOS_20261031.zip` 235154 bytes, SHA-256 `c40decf905f146ebe5e3fe40ba39f59fbf29567819cfc6be4c629e3aaf8f5aa6`; from it we read `results/RESULT.json` SHA `5e7245cc8d1bea2248ddce240914763a564c08f7592aa109a3edf4b698178fbd` and `results/SCENARIO_CHI_FROM_GITHUB.json` SHA `9595a898366c9e3b1999066910a12058558d0335c718cbada77ca5615bef8728`. Both are enforced by production code.
- `earliest` 3.315890693452162e-31, `latest` 9.85567761064523e-32 2p excitations m^-3 are original event totals. Five conditional E1 initial anisotropies, two upper Bray anchor choices, both original birth policies remain distinct. This code never modifies the 2066 event IDs, weights or original NIST/Shah rate ownership.
- The original PHYS22 540-row observer Stokes control is read from the parent ZIP, not an independent measurement. It supplies 420 away-from-poles no-shear fixed-frame regression points in the local tests.

## Original literature and reference code authority

1. Pontzen & Challinor, *Bianchi model CMB polarization and its implications for CMB anomalies*, MNRAS 380,1387–1398 (2007), DOI `10.1111/j.1365-2966.2007.12221.x`: photon Liouville/geodesic direction/shear and polarization screen transport in anisotropic cosmology. Our exact diagonal Bianchi-I specialization is independently derived, not copied as code.
2. Portsmouth & Bertschinger, *A tensor formalism for transfer and Compton scattering of polarized light*, arXiv:astro-ph/0412094: photon screen coherency and Lorentz polarization tensor background.
3. Fano & Macek, Rev Mod Phys 45,553 (1973), DOI `10.1103/RevModPhys.45.553`, and Cooper & Zare J Chem Phys 48,942 (1968), DOI `10.1063/1.1668742`: photon–electron angular orientation/formalism behind PHYS22 E1 source.
4. Bray, Konovalov & McCarthy, Phys Rev A 44,5586 (1991), DOI `10.1103/PhysRevA.44.5586`, original published 6CCO λ,R,I/DCS, and Williams Aust J Phys 51,633 (1998) DOI `10.1071/P98023` for measured 16.5-eV crosswalk. The current source-derived χ values are inherited from PHYS22/PHYS21; raw PDFs are not redistributed.
5. PHYS15 original NIST Wiese–Fuhr `A21=6.2649e8 s^-1`, H recoil-free Lyα energy `E21=10.1988 eV`, original 100K gas baseline. The line uses a **conditional normalized thermal Voigt** profile, not the complete source-owned PHYS16 recoil/redistribution spectrum.
6. Curtin CCC e–H original numerical database, https://atom.curtin.edu.au/CCC-WWW/index.html, is authoritative only for its integrated CCC cross sections. It is *not* the source of the polarized 6CCO DCS used here. IAEA CollisionDB D109688 B61 DOI remains provenance-disputed and is not promoted.
7. `bass` KM2N PR297 and KM2O PR298 implement their *own* Einstein–P8–Peebles photons and Bianchi transport but have **no demonstrated event-level source identity** with CR2066. We reuse mathematics only, never their ray arrays or observer tetrad.

## Actual new scientific output

- 92,160 full-sky null-geodesic/screen Stokes rows: 5 original-E1 conditional photon direction scenarios × 2 6CCO upper anchors × 2 original source birth policies × 4 **explicitly conditional** integrated shear choices × 24 Gauss-Legendre mu nodes ×48 azimuth nodes.
- 46,800 frequency-resolved Voigt Lyα line rows: 9 representative observer sky rays ×65 x-values ×80 source/shear cases, including directional gravitational line-center offsets.
- 80 physical source normalization/energy/quadrupole and screen rotation diagnostics; four figures from genuine data.
- Exact Bianchi-I null momentum constants, observed nu_o/nu_e=r, emission-to-observer sphere Jacobian r³ for tracefree Delta beta; initial E1 3D orbital PSD coherency, Levi-Civita parallel-transported 2D transverse screens; photon number and linear Stokes cone preserved across all 80 cases.
- Source emission 100K thermal Voigt with PHYS15 NIST A21 and no source recoil: `nu0=2.4660588682175665e15 Hz`, `DeltaNu=1.0566205589679062e10 Hz`, `a=4.718296433444188e-3`, line profile normalized on the **whole** real line. Output spectral window x∈[-16,16] does not contain exactly 100% of the Lorentz wing; this is explicitly distinguished from spectral integral normalization.
- In FLRW limit, 420 no-pole source PHYS22 angular/Stokes regression cells match at 1e-12 relative; isotropic original-E1 source has Q=U=V=0 in all shears, but anisotropic intensity from geometric focusing. For axisymmetric Delta beta=(2,2,-4)×1e-6, isotropic emission sky l=2 angular quadrupole <P2(nz)>=2.400002058e-6; leading-order result is 6s/5 with s=2e-6. The triaxial case generates geometrical parallel screen rotation max 2.98556166e-6 radians.
- Maximum photon-number residual 4.44e-16 for all 80 cases; maximum screen Gram-matrix residual 1.78e-15. The model is collisionless/instantaneous emission at one conceptual birth surface and has no time-ordered source connection, free-electron stopping, scattering, RII, L4/Native25 or cosmological likelihood.

## Reproduction

From package: `python phys23.py`, `python -m unittest test_phys23.py -q` and `python -O -m unittest test_phys23.py -q`, `python plot_science.py`; no network, no original source PDFs required. The frozen input JSONs are tiny exact PHYS22 summaries and are hash-locked. For a full physical closure, replace the four toy shear-integral diagnostic profiles with original CR-compatible sourced a_i(t), radiation ray and 2p emission-age distribution while retaining byte-identical original source counts.

## Gates

PHYS23 scoped auxiliary data product `1/1 CONSTRUCTED_REVIEW_HOLD`. **Central DAG 28/88 Δ0, extension DAG 0/3 Δ0.** R06/C09 distinct-author `NOT_RUN`; native subagent `NOT_RUN` (not exposed), same-author hostile review and local tests performed. Production/Native25/L4 HOLD; no merge, no force push, auto-next false.