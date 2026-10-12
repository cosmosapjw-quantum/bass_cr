# Reviewed focused executions

The independent reviewer read the source and output of these executions without rerunning them. The general propositions were checked separately by analytic arguments recorded in the three branch review notes.

## Receiver and new theory checks

- receiver_interface.py: 8426 bytes, SHA-256 4c8a23e81c2babe56765b4ffc97a1b2771966b01f99fba6bc84a71a62848c868.
- checks/run_theory_checks.py: 10472 bytes, SHA-256 0be5b9f62a6eee82aaa7ffeb12fa77ff9ae275623938f778cd48695d799dfd2b.
- results/THEORY_CHECKS.json: 4239 bytes, SHA-256 ce4d0fc25fbe89449ac5efe2ba61f01daf8a07afb1a18efb3eb676bbd832c13f.
- checks/RUN.stdout.txt: SHA-256 1583589ec0597650dc3eb53267d1ac4a6f26bce648a0c26ed9833f4b31a01705. The displayed 15/15 result agrees with the JSON. The stderr file is empty.

The interface implements the direct transfer temperature derivative, its total-moment equivalent, a conservative finite packet update and the endpoint temperature-error bound. Scalar input checks preserve exact Fraction arithmetic. The total-moment route retains active pressure work and uses n_all-n_active as the thermal count; the direct route avoids subtracting large active and total energy terms when the net thermal transfer is small.

The actual result records 15/15 passes in 0.016807850988698192 seconds. Rational fixtures distinguish active birth from thermal addition, verify the particle reference-energy term, cover reverse packet transfer and attain the EOS error bound. Separate examples preserve actual daughter energy and anisotropic work. The source-pinned Coulomb check extracts only checked_energy and stopping_eV_s from the restored source, evaluates 30 density/prescription/energy combinations and finds maximum relative difference 2.6865747820368525e-16 in the proposed decomposition.

The distinct dimensionless eight-state IVP uses two energy coordinates, cumulative heat and thermal energy for each of actual/reference systems. Its positive generators do not commute. The reference solution has tau=1-exp(-t); the actual perturbation is t exp(-t) C_0/2. The input-only certificate is 1-(t+1)exp(-t). The reported exact-reference discrepancy is 1.115496583992126e-12. At the endpoint, state-plus-heat error is 0.06991553248830631 and its bound is 0.26424111765711533. Thermal-energy error is 0.010496505174731219 and its bound is 0.3222814580782103. These values are dimensionless model diagnostics. The 65-point check supplements the continuous analytic theorem rather than establishing a general bound by sampling.

## Collision-clock exact example

- verify_analytic_case.wl: 2037 bytes, SHA-256 b37a067ee47ad1b4c06a8ab5a9fe7111354f5a38c3fd63e06de0bffee98593ce.
- ANALYTIC_CHECK_RESULT.json: SHA-256 9d8fb2b392be36098f1af7df7a8ed0b51ad715aecc7e995052fbfdbbd448b964.
- WOLFRAM_RAW_RESULT.json: SHA-256 f16e8ce8d69924a7cdc34e9443d1914dcb0e098782c65f4917d99ccf49905442.

One actual Wolfram evaluation returned 21/21 true checks. The script verifies the proper-volume and comoving differential equations, source Jacobian, heat prefactor, cumulative energy, initial conditions, matrix noncommutation, residual integral and endpoint expressions for the strengthened two-stage case. Positive symbolic assumptions match the stated domain. The original raw response contains all 21 true entries and isError=false. Earlier missing-SymPy imports and a Wolfram context failure are identified separately in the result; they executed none of these symbolic checks.

## Scope of execution support

The executions support the receiver algebra, selected discriminating cases and correspondence to the restored stopping prescription. General moving-interface, inverse-state, propagator, residual and EOS statements rest on the supplied analytic proofs and independent proof review. The independent reviewer executed zero candidate programs, transport integrations, generator constructions, pulses, historical suites or NCP jobs.
