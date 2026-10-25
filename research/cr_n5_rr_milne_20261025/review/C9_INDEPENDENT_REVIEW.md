# Independent C9 review — scoped PASS

The two finest R80,N2048 chains passed the frozen independent criteria: all
40 new RHS and all72 selected native H I photo/Milne coefficient nodes passed.
The reviewer imported no production module and performed no old primary replay,
source quadrature, thermal-rate quadrature or ODE execution.

| Check | Observed maximum | Frozen threshold |
|---|---:|---:|
| Per-column own infinity-norm difference | 7.69509483627e-11 | 5e-10 |
| Primary backward residual against intended real operator | 4.36604660049e-13 | 2e-12 |
| Independent native-fit coefficient relative difference | 3.13773236206e-15 | 5e-13 |
| RR event-scale signed energy residual | 5.54759269833e-17 | 5e-13 |
| Independent stopping partition error | 4.87977011140e-11 | 2e-8 |
| Independent gross energy residual | 2.19169877443e-11 | 2e-8 |

Decimal precision70 was used throughout the independent tridiagonal solutions.
The operator diagonal is the real sum of exactly converted saved binary64 K0
and lambda values. Conditional-time RHS were recomputed from the independent
probabilities. Every physical and response column used its own nonzero norm.
The old K0 solve used the new lambda RHS only; this is not a replay of old science.

Both finite-chain M-matrix factorizations had positive pivots and nonpositive
off-diagonals. RR probabilities were positive; paired CE and stopping-time
changes were nonpositive. Componentwise rare-event bounds and six immutable
source summaries passed. Signed bath and atomic rewards remain separate.

The binary64 diagonal-addition diagnostic is material: some individual tiny
lambda additions are entirely rounded away (maximum lost fraction1.0), with
maximum absolute loss2.79606568596e-15 s^-1. This observation is retained.
Comparisons against the unrounded Decimal operator pass the frozen observable
criteria. The calculation does not establish zero roundoff or a continuum error
certificate.

The reference run used1.222584 worker CPU seconds,1.271532 wall seconds and
49,136KiB peak RSS. Its40 RHS count is separate from the160 primary RHS.
The native-thread limit was1; reviewCPU1 and coordinatorCPU8 were used.
The owned lease was cleared after completion.

Blocking findings:0. This is a scoped finite-chain consumer admission. N5 stays
PARTIAL/OPEN; N6 and N7 remain gated. Original old-vector uncertainty is inherited;
global_error_bound, global_model_error_bound and global_completion_percent are null.
Publication and backups are root-owned and separately recorded. Dense Decimal
reference CSVs belong with private raw backup, not public Git.
