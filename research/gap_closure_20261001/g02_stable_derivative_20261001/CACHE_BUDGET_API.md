# Frozen G02 component diagnostics

`cache_error_budget.analyze_budget(manifests, output_json, output_csv)` reads the
four completed R4V producer manifests and all 72 exact query pairs through the
existing validated loader. It emits 128 selected block records (8 centers × 4
steps × TT/TP/PT/PP) and 64 cross-resolution records (8 × 4 × TP/PT).
It does not evaluate a basis, integral, native kernel, or propagator.

The channel convention is the actual `symmetric_channels` convention: center 0
is target T, center 1 is projectile P, then radial-bank order, then increasing m.
For this bound bank the T indices are 0–8 and the P indices are 9–17.
Raw caches contain cross TP/PT arrays at quadrature orders 32 and 40, but only the
selected full matrix. Same-center blocks use order 20 and have no independent
order-32 full-matrix payload; no such payload is inferred.

`block_budget(D, Ddagger, Sminus, Splus, h, velocity, rows, columns, floor)` is the
pure-array helper. `Ddagger` must already be the conjugate transpose of the
opposite block. It records local and global indices, absolute and normalized
residuals, denominator-floor binding, both cancelling operands, and absolute
data-perturbation gains. Units are the archived atomic units: S dimensionless,
D and FD in inverse atomic time, h in a0, velocity in a0 per atomic time.

For $F_h=v(S_+-S_-)/(2h)$, external entry-wise input perturbations obey
$|\delta F_h|\le v(|\delta S_+|+|\delta S_-|)/(2h)$ in exact arithmetic.
This algebraic gain is separate from the reported epsilon-scaled surrogate,
which merely assumes operand-relative perturbations of size epsilon and is not
a bound on quadrature, FEM, or total floating-point error. Adjacent-order
differences are also observations, not rigorous error estimators.

The original global scientific gate is unchanged. Block-relative ratios use
their own block norms for diagnosis and cannot replace the global ratios. The
elementwise denominator floor is calculated from the unchanged full-matrix rule.
Exact zero cancellation is represented explicitly with `null` condition ratio,
not infinity in JSON.

The actual frozen results separate two obstructions. At h=0.05 the maximum
cross-block absolute residual is 2.11465e-6; changing raw quadrature from order32
to40 changes the FD by at most 7.96713e-16 over the full ladder. In the same-center
PP block, [9,13] has FD=0 while the two D operands near ±0.560931 cancel to
1.64–1.65e-14, producing a floor-normalized residual of about 0.0165. Same-center
S is analytically constant, but the cached overlap matrices vary by up to
2.22045e-16 because the own-sphere radial quadrature is repartitioned at the
moving nuclear distance. These observations motivate separate truncation and
cancellation treatment; they neither excuse a failed original gate nor certify
the full operator identity.
