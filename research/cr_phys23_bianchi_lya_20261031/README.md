# PHYS23: Source-conditioned Bianchi-I Lyα photon geodesic and screen transfer

**Source identity:** PR #147 immutable HEAD `fac9a25d53468502b3807da2034e4bfa99325c8f`; original 2066-event source Git blob `d7034188ca5a02dc37db24aaf8f7d550624567bd`. Source PHYS22 frozen 235154-byte ZIP SHA256 `c40decf905f146ebe5e3fe40ba39f59fbf29567819cfc6be4c629e3aaf8f5aa6`.

**Full original computed science is in nine Git binary zip parts**, 9/9 independently validated local Git blob SHA1. Restore to a byte-exact complete 3,813,848 byte ZIP using:
```bash
python research/cr_phys23_bianchi_lya_20261031/RESTORE_PHYS23_GIT_ZIP.py --output /tmp/PHYS23_FULL.zip
unzip -t /tmp/PHYS23_FULL.zip
```
It contains full Python physics source and input data, 92,160 Bianchi-I sky Stokes rows, 46,800 frequency Voigt Stokes rows, 80 normalization diagnostics, four scientific figures, 19/19 standard+optimized tests, 20 stage JSONs, source/manifests and handoff. Archive SHA256 `22d97f477199e71e2250b83ceb8fb10914457c343125456d981c0f9f34024111`; verified via Google Drive upload/download byte-exact restoration, ZIP member CRC/SHA.

**Physical calculation:** original PHYS22 source-weighted electron-impact E1 state χ(E) and true original earliest/latest 2p photon counts; physical Bianchi-I trace-free conditional integrated shear Δβ ∈ {(0,0,0),(2,2,-4)e-6,(-2,-2,4)e-6,(3,-3,0)e-6}. Exact conserved comoving null p_i: r=νo/νe=1/sqrt(Σ_i exp(2Δβ_i) n_oi²), n_ei=r exp(Δβ_i)n_oi, dΩe/dΩo=r³. Levi-Civita parallel-transported photon polarization screen and J_o=r³ R J_e R^T. PHYS15 NIST E21=10.1988 eV, A21=6.2649e8 s^-1, T=100K thermal Voigt source is a conditional microphysical baseline, **not full PHYS16 recoil and RII**.

**Verified results:** 92,160 sky +46,800 spectral+80 diagnostic rows (all explicitly conditional, not observed Bianchi), 420 fixed-frame PHYS22 zero-shear source Stokes control cells, 19/19 normal and 19/19 -O unit tests; photon number conservation max 4.44e-16, screen orth max 1.78e-15, sky cone/PSD pass. In isotropic unpolarized E1 source, Bianchi shear generates only intensity quadrupole q20=2.400002058e-6 for Δβ=(2,2,-4)e-6, with Q=U=V exactly 0; matches q20=6s/5+O(s²). Fixed source scenario with Q,U nonzero gives covariant geometrical polarization transfer.

**Primary literature:** Pontzen & Challinor (2007) MNRAS 380 1387 DOI `10.1111/j.1365-2966.2007.12221.x`; Portsmouth & Bertschinger arXiv:astro-ph/0412094 polarized tensor formalism; Fano & Macek (1973) RMP45 553; Bray et al. (1991) PRA44 5586, Williams (1998) Aust J Phys51 633. Curtin CCC is original public distributor for integrated collision cross sections, not the 2p angular polarization data.

**Main claim HOLD:** original CR source **does not own** photon ray/polarization or its physical Bianchi a_i(t)/emission times. The four integrated shears are controlled backgrounds, not an Einstein IVP. No source owner switch to external BASS KM2N or REI, no physical K, full RII/detailed balance, He-exclusive or cosmological likelihood. CENTRAL DAG **28/88 Δ0**, EXTENSION **0/3 Δ0**, PHYS23 scoped auxiliary 1/1 constructed REVIEW_HOLD. Production, Native25, L4 HOLD. No merge, force push, auto-next. R06/C09 distinct author and native subagent NOT_RUN. GitHub-native CI NOT_RUN.
