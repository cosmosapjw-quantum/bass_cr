# Thermal-excess independent review

Candidate first read: bass_cr_theory_20261012/derivations/THERMAL_EXCESS_KO.md, SHA-256 569fccf6a6773e999312c8c942900fb8bfe79d7a8adbf1a3e646106aad0ec85c, 13566 bytes. The exact first-read bytes are in THERMAL_EXCESS_INITIAL_READ.md. Scope: T1–T5, T.1–T.18 and the computational interface. The reviewer did not generate this candidate or design the owner's checks.

## Exact inverse check

Write c_v=3k_B/2, n_th=n_all-n_A, u_ex=u_A-c_vT n_A and Pi_ex=Pi_A-k_BT n_A I. Starting from the proposed all-free temperature equation, substitute

D u_ex=D u_A-c_vT D n_A-c_v n_A dot T.

The derivative term adds c_v n_A dot T to the right. The pressure terms combine as -k_BT n_all theta-K:Pi_ex=-k_BT n_th theta-K:Pi_A. The source and active-energy terms combine by T.2 into Q_d+P_h+J_E. Finally S_all-D n_A=S_d+J_N. Moving the derivative term to the left gives exactly

c_v n_th dot T=Q_d+P_h+J_E-k_BT n_th theta-c_vT(S_d+J_N).

This verifies the derivative coupling and the positive coefficient c_v n_th directly, rather than treating D u_ex as an independent prescribed number. The state map is invertible on n_th>0 when the active state is retained, and T.8 recovers total energy and stress exactly. The signed excess energy is properly excluded from passive energy norms.

## Source and geometry checks

The active-birth example includes both primary kinetic energy W_b S and total-particle source S. The excess-energy derivative removes their net effect from the thermal equation, giving dot T=0 under the declared no-transfer conditions. Secondary electron multiplication is separately counted through S_sec. Chemical loss L is subtracted once from electron kinetic energy; primary proton binding cost belongs to the external proton/chemical bookkeeping.

Exact active kinetic pressure uses p v=W(W+2m_e c²)/(W+m_e c²). No isotropic or nonrelativistic pressure replacement enters T.9–T.11; the tensor K:Pi_A carries the anisotropic work. The thermal EOS remains the explicitly chosen nonrelativistic bath closure. Full kinetic repartition and thermal replacement are distinguished in the text.

## EOS error and finite updates

The identity T-hat T=(U-hat U)/(c_v N)+hat T(hat N-N)/N gives T.18 with the stated positive lower bound and nonnegative reference temperature. The bound concerns endpoint thermal energy and count. The text correctly includes work/cooling differences before identifying a deposition error with thermal-energy error.

For a material volume, U_th=V u_th has derivative V Q_th-(2/3)theta U_th, so the stated integrating factor V^(2/3) is correct. The finite update followed by T=U_th/(c_v N_th) preserves the supplied number and energy integrals algebraically.

## Finding requiring terminology alignment

TR-01: T4 defines P_h as continuous stopping only, whereas the moving-cutoff candidate uses P_h=P_h,d+P_h,j when a jump deposits direct thermal heat. The formulas already work for total collisional thermal heat. Minimal correction: either include that jump contribution in the P_h definition or explicitly retain the zero jump-heat specialization. L then retains the chemical/excitation/radiative debit. This is a localized inter-document convention issue; the displayed conditional identities are mathematically correct.

TR-01 is resolved in candidate SHA-256 f5ed4a9f88aace5d74dfa69973dc5e71b97d37d27e9b952739ba2423e3c9bf30: T4 now includes continuous plus declared direct jump heat, and the opening of §2 splits the total medium debit into jump heat and L.

## Added deposition-to-temperature bridge

Reviewed T.19–T.22 in full. From p_th=2u_th/3, the material energy U satisfies Udot+(2/3)theta U=Hdot. With mu=(V/V0)^(2/3), the integrated equation is mu(t)U(t)=U(0)+integral(mu dH). For two histories with the same V, integration by parts gives integral(mu d(delta H))=mu(t)delta H(t)-integral(mu' delta H), because delta H(0)=0. Taking absolute values and using the uniform-in-time cumulative bound produces T.21. If theta>=0 and B_H is nondecreasing, integral(mu' B_H)<=B_H(t)[mu(t)-1], yielding T.22. The coefficient 2-1/mu(t) therefore follows directly.

The combined route controls endpoint thermal energy before applying the independently checked EOS bound T.18. It correctly requires a bound on the complete thermal-deposition ledger, including heat plus cutoff energy when both join the bath. Other differing sources and cooling histories must be included in that same cumulative difference. This supplies a complete conditional error-transfer map for a prescribed common expansion history.

Disposition: pass_scoped for T.1–T.22 after the recorded definition alignment. No new scientific execution was needed for these algebraic identities.
