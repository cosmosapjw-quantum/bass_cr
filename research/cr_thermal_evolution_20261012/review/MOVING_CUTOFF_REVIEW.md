# Moving-cutoff independent review

Reviewed candidate: moving_cutoff/MOVING_CUTOFF_DERIVATION_KO.md, SHA-256 d367731a253232befc6b5e5f0f308e227aaa4faaa947926ef6912cb3869959c1, 20724 bytes. The exact first-read bytes are preserved in MOVING_CUTOFF_INITIAL_READ.md. Scope: MC1–MC36 and their stated assumptions. This reviewer did not produce the candidate or its owner checks.

## Independent route

Use the distribution indicator H_A=H(W-W_c(t)). For the candidate's spectral conservation law, differentiation gives

∂_t(H_A g)+θ H_A g+∂_W(b H_A g)+div_Ω(dot n H_A g)
=H_A(q_g+C_g)+(b-dot W_c)g_c δ(W-W_c).

The sign of the delta term follows independently from ∂_t H_A=-dot W_c δ and ∂_W H_A=δ. Its number integral is -S_c,d with exactly MC1's orientation. Multiplying the conservative equation by W yields the bulk term ∫_A b g and the interface term -W_c S_c,d. The geometric part of the bulk term is -K:Pi_A because v=∇_p W. Therefore MC15 and MC16 follow without relying on the candidate's inner-normal argument. Multiplication by p_i before the spectral-coordinate transformation gives the momentum result MC17.

The pressure trace follows from p v=W(W+2m_e c²)/(W+m_e c²), so the nonrelativistic and ultrarelativistic limits in MC10 are correct. The shear contraction persists for a parity-even anisotropic distribution even though the momentum transfer vanishes.

For each active-parent collision, the active number increment is ν_A-1=(ν-1)-ν_B. Its active kinetic-energy increment is Σ_A W_j-W_x=-ell_E-Σ_B W_j. Integration over event rates gives MC24 with the indicated multiplicity and actual daughter energy. The same interface has the opposite sign in the lower moments; total moment conservation is exact for a complete kinetic partition.

For the thermal closure, differentiate u_th=c_v n_g T with c_v=3k_B/2 and use dot n_g+θn_g=Q_B,N+S_c. The θu_th terms cancel, leaving c_v n_g dot T+P_th θ=Q_th-c_v T(Q_B,N+S_c), which is MC30. With W_c=χk_BT, substitute S_c,d=χk_B ρ_c dot T-B_c. Moving its temperature-derivative part to the left produces C_V-χk_B(W_c-c_vT)ρ_c, agreeing with MC35. This is a branchwise implicit relation because the upwind trace changes with the sign of b-dot W_c.

## Findings and disposition

No blocking mathematical finding in the reviewed snapshot. The two physical constructions are distinguished correctly: full kinetic partition retains both distributions, whereas thermal joining chooses a lower representation with a specified EOS. Reverse transfer requires the lower upwind trace, which the candidate explicitly supplies as an input. The temperature-dependent-cutoff equation states branchwise nonzero-coefficient solvability and makes no global uniqueness claim.

The displayed constant-spectrum redistribution example suppresses units in its numerical coefficient. Read g_0 as the numerical value of a density per eV; the dimensional integrals in MC36 remain unambiguous. This does not affect any theorem.

Decision for this snapshot: pass_scoped, derived identities and specified thermal closure. Final integrated decision awaits the all-free representation and collision-clock candidate.

Execution: analytical proof review only; zero transport, pulse, NCP or old-suite executions.
