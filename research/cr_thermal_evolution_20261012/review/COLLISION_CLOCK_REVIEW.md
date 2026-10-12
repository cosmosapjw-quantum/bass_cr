# Collision-clock independent review

First-read candidate core: collision_clock/COLLISION_CLOCK_DERIVATION_KO.md, SHA-256 3a146037daab7613d35a35a7babe89fe0fea91072c13837501b77a61b384e55e, 15059 bytes. The first-read core snapshot is preserved in COLLISION_CLOCK_INITIAL_READ.md. The reviewer subsequently read §§6–10, the SI number-row amendment and the strengthened V, a, q example. The final manuscript identity will be attached to the integrated decision. This reviewer did not generate the candidate or design the owner's checks.

## Exact clock and volume map

Directly differentiating X=Vx cancels only proper-volume dilution. Division by dot tau=a gives X_tau=L_0X+Vs/a. Variation of constants followed by d tau=a dt cancels the source Jacobian exactly and gives CC1. Evaluating the physical output row adds the factor a/V. Integrating the parcel heat uses V p_h dt=a h_0^T X dt=h_0^T X d tau. These three separate transformations verify CC2 and its physical-volume interpretation.

Source projection into an absorbing output is an additional direct source term. The candidate includes it in Eq.2.12 and keeps it separate from a collision-generated output. The original two source columns keep their original common energy denominator.

## Code-specific density dependence

Read actual causal_cascade.py stopping_eV_s, project and generator expressions. For n_e=d n_e0, omega=sqrt(d) omega_0. Both branches of the actual Coulomb logarithm shift by -log(d)/2. The minimum commutes with a common scalar shift, giving B_j(d)=d B_j0-d log(d) kappa_j/2. The discrete drift construction is linear in B_j and each atomic rate is linear in its target density. Therefore the full fixed-grid generator is dG_0-d log(d) C_0/2, with the specified positive-log domain. Direct sources remain independently prescribed. This is an exact identity for the extended stored prescription.

The actual active states store energy. w=1 is consequently the active energy norm. In SI coordinates an energy output row is G_u/T0, while a number row is G_u/(T0 epsilon_eV). The amended Eq.1.2a and diagonal similarity transform give this correspondence explicitly. The same conversion is stated for C_0's number rows.

## Independent residual argument

For a Metzler actual A, positive energy weights w and w^T A<=beta w^T, positivity implies |Phi_A z|<=Phi_A |z|. Taking w^T and applying the scalar integrating factor gives the stated propagator norm. This is also obtained from the upper Dini derivative used in CC3.

Subtracting the actual and reference equations gives e'=Ae+Delta Xhat+(S-Shat). The exact variation-of-constants formula uses the actual propagator. Bound its norm as above, bound Delta Xhat by ||Delta||_w w^T Xhat, and use reference passivity to bound w^T Xhat by input energy plus initial stock. This yields CC4, including initial error and source mismatch, with no commutation assumption.

For CC5 append the heat-deposition state. The extended weights are (w,1) and the extended column inequality is w^T A+h^T<=0. The last column of the operator difference is zero, so its action depends only on the reference active state. Applying the preceding residual argument yields the sum of state-energy error and cumulative heat error. Number outputs use the separate weighted dual norm. The reference direct-source and output-row differences are included. The contraction result explicitly assumes passivity of the actual energy-plus-selected-output system; CC4 supplies the beta-dependent alternative.

## Rate bound, clock choice and exact example

The triangle inequality gives the sum over reaction-rate differences in Eq.7.3. Each conservative reaction column has weighted absolute sum twice its diagonal energy loss, giving Eq.7.4 and the stated Coulomb norm when all genuine outgoing energy ledgers are included. The low-cross diagnostic is correctly excluded as a repeated energy count.

The clock objective is a weighted sum of absolute distances to rate ratios. Its subgradient has zero precisely when neither strict side carries more than half the weight. Clipping a weighted median to the permitted interval yields a constrained minimizer; the zero-weight case is also covered in the amended text. Since the input-energy envelope and fixed physical source are independent of the clock, this choice minimizes the displayed coefficient upper bound under those assumptions.

For the amended two-stage example V=1+t/t_*, a=V², q=q_0V, the transformed source is q_0. The listed triangular-system solution has weighted active energy q_0[3-(3+u)e^-u]/(2lambda). Subtracting it from total injected parcel energy q_0 tau yields the heat expression. At lambda=1/t_* and T=t_*, u=7/3, giving p_h=2q_0[1-(13/6)e^-7/3] and Q_h=q_0t_*[5/6+(8/3)e^-7/3]. The two reaction matrices have commutator entry (2,1)=1 and augmented norms 2. Integrating the source envelope gives the perturbation factor T²+2T³/(3t_*)+T⁴/(6t_*²), whose ratio to total injected energy at T=t_* is (11/14)delta_0t_*.

## Findings and disposition

CR-01, SI number-row conversion: corrected by explicit Eq.1.2a and diagonal similarity/source scaling.

CR-02, constrained median: corrected by explicit clipping and the all-zero-weight case.

CR-03, source-shape positivity: Eq.5.6 now explicitly requires b and bhat to be nonnegative along with energy normalization. This justifies their weighted norm being one and the total-variation interpretation. Signed source differences continue to use Eq.5.3.

Final branch manuscript identity: 27355 bytes, SHA-256 280b027c5c284f3d8608ba8ff968fb5a6fad5a939d7c956eec69ca0e37e60fdb. The final changes were read directly. The author's 21-check symbolic execution is reviewed separately in EXECUTION_REVIEW.md.

No remaining mathematical finding in the reviewed core and amendments. General mechanisms are established variable-change, positive-system and variation-of-constants results. The BASS_CR contribution is their explicit physical-source/output mapping, exact density-dependent drift decomposition and conditional energy/number-to-temperature application.

Execution: analytical independent derivation and direct source-code reading. No candidate code, generator construction, transport, pulse, NCP or old suite was executed by this reviewer.
