# R3M13 preparation-transfer theorem and claim policy

R3M12 left the 100 keV/u, b=2 a0 lane at `b-grid NO_GO`. At dx=0.25 a0,
physical dt=0.05 t_a and fixed CAP, the next change is only the imaginary-time
preparation: 0.025 x 1200 -> 0.0125 x 2400, keeping total imaginary time 30 t_a.

The R3M12 finite-span reference is `P_ref=0.00775827737938`; this is the n<=3
sampled-hydrogen Gram span, not all-bound capture.

For normalized preparation states psi, phi define
`d=min_theta ||psi-exp(i theta)phi||`. If K is the same subsequent fixed-CAP
Strang propagator and Q is the same orthogonal finite-span projector, K is a
contraction and
`|sqrt(q)-sqrt(p)|<=d`, so
`max(0,sqrt(p)-d)^2 <= q <= min(1,(sqrt(p)+d)^2)`.

For relative screen s a sufficient condition for `|q-p|/p<=s` is
`d<=sqrt(p)(sqrt(1+s)-1)`. With the R3M12 values and s=.01,
`d_crit=4.3930987793802824e-4`.

This condition is sufficient, not necessary. Failure of the distance threshold
is inconclusive and requires the candidate collision if the 1% screen decision
is needed.

Also record the discrete-Hamiltonian stationary residual. Operator-splitting
literature shows that imaginary-time/Hamiltonian states need not be exactly
stationary under an approximate real-time propagator, so a target-only
one-step split stationarity defect is a useful separate diagnostic.

No b-grid, tail integration, 50/225 keV/u, physical rate, production central,
all-bound promotion, or probabilistic covariance is admitted by this node.
