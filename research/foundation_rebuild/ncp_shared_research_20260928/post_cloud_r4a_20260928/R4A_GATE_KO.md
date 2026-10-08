# R4A selected-span provenance and transport-authority gate

상태: **PROVENANCE_FOUND__REAL_OBSERVABLE_NOT_AUTHORIZED**

## R3 cloud return audit

Remote ref/tree를 다시 확인했다. `codex/r3-cloud-review-cache-audit-20260928`의
`b20a863baebc232109dc8109d40515809ae4ffee`는 구현 commit
`ae22511993fda12b61be9ff13c62c34a95e689aa`의 직접 자식이며, 추가된 것은
cloud-review evidence JSON 5개뿐이다. 구현 source 변경은 없다.

Cloud review는 cache-only 범위에서 finding 없이 종료했고 실제 prepared environment는
Python 3.12.3 / NumPy 2.3.5 / SciPy 1.17.0이었다. 실행 evidence는 297 task,
2673 array, 새 native evaluation 0을 기록한다. 따라서 scientific/cache 상태는
`R3_CACHE_REUSE_AND_METRIC_AUDIT_COMPLETE`로 유지한다.

Codex의 최종 `R3_CLOUD_BLOCKED`는 Google Drive + Dropbox credential 부재로
정확한 portable ZIP을 이중백업하지 못한 운영 blocker다. 그 ZIP의 기록된 identity는
3,774,880 bytes, SHA-256
`d21755fd5a5ce1d2e7da77d365b02d10a39c296103e9f54a950996492a06549c`다.
현재 ChatGPT runtime에는 그 exact bytes가 없으므로 다른 archive로 대체해
RESTORE/DUAL_BACKUP 완료를 주장하지 않는다.

## selected-span provenance discovery

기존 implementation checkpoint 안의 Git bundle에서 historical archive
`tp2d_runtime_self_qualified_20260927T074944Z_RETURN.zip`를 exact object로 복원했다.
archive SHA-256은
`630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35`다.

다음 prerequisite는 실제로 archive 안에 존재한다.

- `BASIS.json`: SHA-256 `3cf2359dd9802e84f9ec4dc45f3585e0aa9712de38a3fb0a077300d257150131`
- `REFERENCE_STATES.npz`: SHA-256 `6684dd51f5e1f3ac6e98212c38a4db8236c9a01e6c26c67f4da713ac7b0df9e7`
- final-time qualified operator query:
  `runtime_queries/9a30b3744896b21ce0f75284f264165d9bb4ab42f50e92cac926c6329f974ede.npz`,
  SHA-256 `87dc49ef9f9b42fe0022bc0655265b15e524b14d468b42c4ff4bfc3a33ad17d4`
- final reference time is exactly `0x1.7e7946195fe4cp+2` atomic time in both the state archive and operator-query receipt.
- `states[-1]` and `final_state` are byte-equivalent as NumPy arrays; `states[0]` and
  `initial_state` are likewise equal.
- final S is Hermitian to max-abs (5.55\times10^{-17}), has eigenvalues
  approximately 0.9950691391 to 1.0049308609 and condition number about 1.00991059.
  The archived final state's metric norm is approximately 0.999999999996495.

Pinned historical `symmetric_channels` orders channels by center, radial-bank order, then
(m=-\ell,\ldots,+\ell). The unique target 1s channel is index 0. The projectile
negative-energy finite-span candidate is indices **[9, 10, 12, 13, 14]**.
Indices **[11, 15, 16, 17]** are positive-energy pseudostates and are excluded.

No real selected-span probability was evaluated in this gate.

## blocker moved from provenance to transport authority

The same historical archive has return status `TEMPORAL_REFINEMENT_UNRESOLVED`.
Its DOP853 reference path exists and has rtol (10^{-10}), atol (10^{-12}), with
reported max metric-norm drift (4.2599\times10^{-11}), but the frozen candidate
temporal screen was not closed. For N=384,

- candidate-to-reference metric distance =
  `2.634560877280569e-6`
- N=192 to N=384 refinement metric distance =
  `7.904769432369909e-6`

against a frozen (10^{-6}) limit.

Therefore the archived final (c) is now **provenance-resolved** but is not promoted to an
admitted production/capture state. The next decision is whether to permit a strictly
`REFERENCE_PATH_FINITE_SPAN_DIAGNOSTIC_ONLY` projection, or to close temporal refinement
first. Until that explicit gate decision, keep:

`capture_execution_allowed=false`, `production_admission=HOLD`,
`all_bound=OPEN`, `b_grid=NO_GO`.

Do not rerun F0/F1/R2 and do not infer a continuous-time bound from the five metric sentinels.
