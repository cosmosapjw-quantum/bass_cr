# To rei_bianchi SOURCE07: C15 bounded solver algorithm handoff

Owner SHA locked: rei_bianchi commit
0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
Source research branch is independent bass_cr C15 worktree.
No owner Rust, AX08 or SOURCE07 source has been modified.

Per original H nucleus, photon packet arrays preserve
birth_a, birth_mu, birth_E_eV, photon occupation and current E_eV.
Source rate proper photon/(H second) is derived from
Scenario.rate(a)/H(a,q) dln a. The photon source is positive
and distributed across the subinterval rather than injected at a
single midpoint. Species rate lambda_j=c*n_j*sigma_j(E) in s^-1.

Exact local frozen-coefficient update:
  tau=dt sum_j lambda_j,
  N_final=N_before exp(-tau)+Sdt*(1-exp(-tau))/tau.
Species events:
  A_j=[N_before+Sdt-N_final]lambda_j/sum lambda_j.
Use proper singular limits, nonnegative rates, photon and energy
ledger, gas update with H/He charge and binding-energy conservation.
Time-varying gas opacity uses a *predictive midpoint approximation*;
do not market this as exact time-varying transfer.

Independent future compatibility tasks:
1. The canonical owner ray/angle transfer and current-frame
   R J_Omega must be mapped to the birth-direction number measure
   WITHOUT a second Jacobian or missing redshift factor.
2. Use actual transported age-resolved photon stocks; never replace
   them by fresh emissivity weights if source attenuation/hardening
   or spatial boundary propagation already occurred.
3. Full igm_thermal Case-A/B and OTS recombination/cooling,
   electron/temperature ledger and stiff coupled reference.
4. Rigorously distinguish future physical xHI(z), HeII/HeIII(z),
   Tg(z) abundance histories from C15's controlled one-zone
   short interval gas-state test.
5. Photon survivor first-order-like accuracy in high tau and 5500K
   RR branch-crossing xHI irregularity remain open. Standalone
   positive endpoint-linear source kernel offers a next reference,
   NOT a valid automatic replacement for time-varying opacity.

No science-grade global convergence or PR to original owner implied.
See actual validation, performance, backup receipts and test
logs in the versioned C15 output folder.
