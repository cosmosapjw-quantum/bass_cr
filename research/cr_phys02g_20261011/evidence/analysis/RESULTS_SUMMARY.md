# Cached scalar moment envelopes

IMPLEMENTATION_VERIFIED_CACHED_SCALAR_PENDING_INDEPENDENT_REVIEW

Raw FP64 primitives were recomputed; saved residual moments and independent Decimal80 expressions agree within the frozen tolerance. No operator, pulse, expm, or linear solve was called.

These are conservative two-moment horizon intervals for the recorded finite-operator scalar moments. They are not fitted quantiles, physical uncertainty bands, or certified forward-error bounds. Independent review is pending.

| Model | Fraction | Lower (years) | Upper (years) |
|---|---:|---:|---:|
| fullBED | 0.5 | 316.880878 | 29085.8916 |
| fullBED | 0.9 | 8746.65501 | 78963.4014 |
| fullBED | 0.95 | 11276.6385 | 107515.973 |
| fullBED | 0.99 | 14379.9138 | 224533.826 |
| fullBED | 0.999 | 16029.0942 | 677157.784 |
| legacy | 0.5 | 316.880878 | 29792.3904 |
| legacy | 0.9 | 8908.38465 | 81223.9154 |
| legacy | 0.95 | 11513.1989 | 110630.093 |
| legacy | 0.99 | 14708.3428 | 231147.354 |
| legacy | 0.999 | 16406.3649 | 697308.486 |
