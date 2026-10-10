# Frozen adapter implementation

1. Pin existing crossing packet and P02B projection source.
2. Evaluate actual Q_BA p_A rates at birth time; retain exact residual meV and upstream event counters.
3. Project only injected number/kinetic energy and create positive quadrature-weighted fresh cohorts.
4. Validate 25 saved row projections, actual one-event GL16/32, manufactured analytic convolutions, OFF/time/domain rejection.
5. Return implementation and evidence to independent Astra reviewer. No commit or push by implementation worker.

Selected design: direct adapter around unchanged functions. Saved-packet interpolation and globally-aged injection conflict with the frozen contract and are excluded.
