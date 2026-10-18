# C21E: integrated photo events plus native non-photo thermal chemistry

2026-10-18. Parent bass_cr PR79 `3e3680fb3dfacfd2bb3a5ecee51fda67f635815c`. Complete implementation commit `22623f990f781668dd30dc1a5ea4ac59214cfd0a`. Frozen native owner: rei_bianchi `6ea2b1b4b3875c9163cafc45efe720afded43fc4`.

## Backup-first and source intake

Inspected existing Dropbox `/bass_cr/C21`, Drive `BASS_DERIVATION_DOSSIERS_20260912/bass_cr` and Library result/receipt search before new research. Those locations contained C21C native replay and C21D source/receipts but no later bass_cr native MIDEXP result. This is a scoped inventory observation, not universal absence. REI PR195 source-free native thermal midpoint and BASS_HE PR75 HE27 A/B are separate evidence, not source-on C21E validation.

## Implemented, not deferred to NCP

Readable source includes the four-variable integrated-event nonlinear solver, persistent Rust nonphoto point bridge, actual native MD14 density/source exporter, native PreparedAbsorption delta-point comparator, chronological source-age/threshold transport, independent continuous Radau, analysis, immutable build/run scripts and 43 Python tests.

The native bridge calls original `igm_point_rhs` with **photo=0,h=0**. Native owns CI/RR/DR/cooling/CMB/Case-A escape; external photon events own ionization and photoheat. No Gamma is formed by dividing events by depleted endpoint absorber abundance. All species and energy owners are checked, and failed steps leave inputs unchanged.

For g=(xHII,xHeII,xHeIII,w_eV/H), Y=nHe/nH, integrated events L and photoheat Q, define S=(LHI,(LHeI-LHeII)/Y,LHeII/Y), b=(chiHI,Y chiHeI,Y(chiHeI+chiHeII)). Absent helium is structural zero. Solve R_species=g1-g0-S-dt F_nonphoto and R_w=w1-w0-Q-dt F_nonphoto,w. The native zero-photo identity F_w+b.F+escape-CMB=0 gives **total reaction energy defect=R_w+b.R_species**. Both gates must pass. Outer geometry maps record adiabatic and photon redshift work once.

Wolfram algebra returned `{0,0,-z^3/12,True}`: two zero residuals, scalar midpoint leading error and negative amplification at z>2. Thus full time-centering is not unconditional stiff positivity. The code rejects inadmissible large steps without clipping or tolerance widening.

## Actually executed science

43/43 Python tests passed; Python compilation and shell syntax passed. A predecessor photo-only test exposed the missing recombination feature. One subprocess timeout test initially confused startup with response timing; the test setup was corrected, preserving the first failure. The false server is protocol-only, never native physics evidence.

Twelve manufactured source-on runs compared BE, MIDPHOTO_ENDMICRO and FULLMID at n8/16/32/64 with the same continuous Radau RHS and fixed source times. Real Verner fit forms and original MD14 total-rate clock are used with a manufactured 3-energy spectrum and **manufactured, not Grackle, CI/RR/DR/cooling coefficients**.

| Mode | n64 thermal error eV/H | last normalized-state order |
|---|---:|---:|
| BE | 5.731703422529044e-5 | 0.9965809104 |
| MIDPHOTO_ENDMICRO | 4.5277562166212704e-7 | 0.9887073290 |
| FULLMID | 3.5463669778579288e-9 | 1.9999861117 |

FULLMID n64 max fraction error=1.354404643993945e-9, temperature error=1.1649419320747256e-5 K. Largest cumulative energy defect across the measured matrix=1.566033815212503e-14 eV/H. Fractions, thermal energy, temperature and photons are reported separately. The historical SUMMARY's mixed-unit gas_max_abs_error is not used for ranking; dimensional analysis uses unchanged raw states.

## Native execution status and command

**Rust is authored but UNCOMPILED here because rustc/cargo are absent.** Three Rust unit tests and the native matrices are NOT_RUN. Public source API compatibility has been inspected, not compiler-certified. Minor actual compiler/API corrections may be needed on NCP; the algorithm and complete execution path are already implemented.

Use an isolated checkout and a compatible Python environment or worktree venv with requirements.txt. Read actual CPU allocation and avoid historical CPU55 until explicitly reassigned. Then run:

```bash
bash run_ncp.sh /root/C21E_NATIVE_NEW_RUN "$CPU" /path/to/existing/rei_bianchi/git/repository
```

The final argument is optional; without it the script fetches the exact owner SHA. Original dirty working files are not used: `git archive` exports the immutable commit. The script builds/tests the bridge, performs native delta-point BE parity, and runs two bounded native/Radau matrices. Default explicit IC is at a=.09; no checkpoint is reinterpreted. One matrix uses manufactured3-energy/opacity.001, the other actual native MD14 12-cell centroid source/physical opacity. Both remain explicit test gas states, not full production histories. Complete logs, partial results and failures are preserved.

Source-age GL2 times are fixed during time refinement; source-age/spectral/angular/global convergence is not claimed. Native Grackle, full48 source, Case B, signed Bianchi, full EoR and full-driver PreparedAbsorption equivalence remain unverified. See SCIENTIFIC_RESULT.json, DAG.json and CODEX_HANDOFF_KO.md.

Background: Reynolds et al. JCP2009, DOI10.1016/j.jcp.2009.06.006; Pawlik & Schaye MNRAS2011, DOI10.1111/j.1365-2966.2010.18032.x. These motivate coupling, not our numerical measurements. Stage preservation receipts distinguish upload, byte readback and scientific validity.
