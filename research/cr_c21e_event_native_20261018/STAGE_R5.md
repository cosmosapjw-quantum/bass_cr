# C21E R5 checkpoint, 2026-10-18

Parent: bass_cr PR79 `3e3680fb3dfacfd2bb3a5ecee51fda67f635815c`. Inspected established Dropbox C21 and Drive bass_cr backup folders plus Library C21D/native search before new research. No later bass_cr-native MIDEXP result was found in these inspected sources; this is not a universal absence claim. Sibling REI PR195 reports source-free full thermal midpoint tests; BASS_HE PR75 preserves completed HE27 A/B. Neither validates this new source-on transaction.

The next implementation uses **integrated photon events**, not division by endpoint neutral abundance. Let g=(xHII,xHeII,xHeIII,w_eV/H), Y=nHe/nH, L=(LHI,LHeI,LHeII), S=(LHI,(LHeI-LHeII)/Y,LHeII/Y), and b=(chiHI,Y chiHeI,Y(chiHeI+chiHeII)). Absent helium is a structural zero branch.

Evaluate the unchanged original `igm_point_rhs` at the selected time-centered gas with `photo=0,h=0`. Solve Rg=g1-g0-S(L)-dt*Fmicro and Rw=w1-w0-Q-dt*Fmicro_w. Native microphysics alone owns CI/RR/DR/CE/freefree/CMB/Case-A escape; the external photo operator alone owns photon loss, ionization events and photoheat. Outer geometry maps own adiabatic and photon work once.

From Fmicro_w+b.Fmicro+escape-cmb=0, the local energy defect equals Rw+b.Rg. Require both nonlinear and energy gates; do not correct energy after solving. This removes the Gamma=L/(dt*Aend) representation singularity, NOT every possible positivity or nonlinear-solve failure.

Actual Wolfram checks: residual identity=0, b.S-sum(chi*L)=0; midpoint scalar amplification minus exp(-z) starts at -z^3/12, and is negative at z>2. Thus smooth second-order consistency does not grant unconditional stiff positivity. Failed steps must preserve inputs and return a rejection.

Full derivation, source intake and immutable stage backup are in the C21E phase package. Native authority is rei_bianchi `6ea2b1b4b3875c9163cafc45efe720afded43fc4`; public point API permits an explicit manufactured initial state without reinterpreting a checkpoint.

DAG: INTAKE/R5=COMPLETE; C5/C6=READY; C7/C8=PENDING; C10=PENDING. This sandbox has no rustc/cargo and direct DNS fails. Native compilation/execution=NOT_RUN; native_subagent=NOT_RUN. Python integration, persistent Rust point bridge and complete external build/run scripts are the next deliverable. Original branches and NCP jobs remain untouched.
