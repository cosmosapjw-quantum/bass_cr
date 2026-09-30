# R4P0A: B0-only tail 연구와 handoff

Status: R4P0_PREPARATION_ACCEPTED__B0_OPERATOR_ONLY_NEXT.

## 검토 대상과 증거

Input commit=f7b5eef95895f299327562859ce0b278ffa8679c
Input tree=a48f84aa757da786304171c51458002707f72c6a
Input branch=codex/r4p0-tail-basis-preflight-20260930
R4P0 package bytes=75053
R4P0 package SHA256=60ed70b65c8fd37fee8a6d7d83602ef20a0de4d745e68655502d9a45f5af5528

이번 연구에서 Google Drive 원본을 받아 SHA/CRC/33 manifest data files를 확인하고, 원본 verifier를 fresh directory에서 실행해 40 passed 및 preparation CLI exit0을 재현했다. 이전 N1536 science는 실행하지 않았다. Native 호출0, nonce 소비0. 원래 양쪽 provider restore 성공은 사용자 보고이며, 이번 독립 입력 readback은 Drive 사본 한 개다.

R4P0은 명시적으로 preparation-only이며 native launcher가 없다. 이것은 준비 패키지의 결함이 아니다. B1–B3 higher-l/actual Gram blocker도 B0 tail 작업을 막지 않는다.

## 이전 해석 정정

R4O에서 raw coordinate block ||K_TP|| 또는 그 cross/full ratio를 temporal probability error와 직접 비교한 해석은 채택하지 않는다. K=S^(-1)(H-i hbar D)는 에너지 차원이며 한 시각의 generator norm은 무차원 총 확률 오차가 아니다. Ratio는 무차원이지만 시간 의존 기저 위상에도 영향을 받는다.

예: S=I,H=[[0,g],[g,0]],D=0에서 R=diag(1,r)로 좌표를 바꾸면 K'_12=r*g이다. 물리적인 상태와 선택 부분공간도 같이 변환하면 population은 불변이다. 공통 시간 위상으로 K에 상수 대각항을 더하면 cross/full ratio를 바꿀 수도 있다. 따라서 raw block은 같은 좌표 convention의 engineering diagnostic으로 유지하되 tail error certificate나 error-axis 우선순위 증거로 쓰지 않는다.

## 새 직접 유도

Finite Galerkin model에서 S=B†B>0, H=H†, D=B†Bdot, Sdot=D+D†를 가정한다.

A=-(i/hbar) solve(S,H)-solve(S,D), cdot=A c.
J=[e9,e10,e12,e13,e14], G=J†SJ, Q=SJ G^-1 J†S, P=c†Qc.

고정 J에서
Qdot=Sdot J G^-1 J†S+SJ G^-1 J†Sdot-SJ G^-1(J†Sdot J)G^-1 J†S.
W=Qdot+A†Q+QA.
Pdot=c†Wc.
rho=||S^-1/2 W S^-1/2||_2.
|Pdot| <= (c†Sc)*rho.

Q의 올바른 projector identity는 Q S^-1 Q=Q이다. rho는 inverse-time 차원이다. S=L L†이면 L^-1 W L^-†의 Hermitian spectrum으로 계산할 수 있다. 입력 inverse/clipping/regularization/hidden deletion을 사용하지 않는다.

시간 의존 좌표변환 R에서는 S'=R†SR, D'=R†DR+R†S Rdot, J'=R^-1J 및 Jdot'까지 함께 변환한다. W'=R†WR이고 generalized spectrum/rho가 불변이다. 원래 J가 상수여도 새 좌표 Jdot'=0을 강제하면 안 된다.

정규화된 정확한 유한모델 해와 전체 구간에 유효한 rho 상계가 있다면 |P(t2)-P(t1)|<=integral rho dt가 따른다. 그러나 이번에는 그 적분도 무한 tail 지배함수도 인증하지 않았다. 8점이나 empirical fit으로 continuous upper bound를 주장하지 않는다. Sdot=D+D† 대입 residual은 independent derivative validation이 아니다.

## 저장 endpoint 결과

13개 pinned input bytes 및 기존18x18 S/H/D와 N1536 c만 사용했다. Atomic-unit data에 hbar=1을 적용:
P_selected=0.009653428615023815
Pdot=+1.6382726202381236e-4 / atomic time
rho=6.2271258107070085e-3 / atomic time
v=2.00798106651023 a0/atomic time
Pdot/v=8.1588051180450567e-5 / a0
metric norm=1.0000000000000189
W Hermiticity defect~2.67e-18
metric algebraic identity residual~1.87e-16

이것은 같은 finite Galerkin model의 local derivative이며 full-space derivative, numerical time-step difference 또는 total tail error가 아니다. 새 tail time에는 c(t)가 없으므로 rho만 가능하며 Pdot는 unavailable로 기록한다.

Wolfram exact rational3x3 검산7개: S positivity, Q/W Hermiticity, metric sign identity, Q/W time-dependent coordinate covariance, generalized characteristic-polynomial invariance. 별도 basis-count Table iterator 오류는 보존하고 Map으로 수정해 counts18/46/92/124와 raw8*11=88을 확인했다. 실제18x18 endpoint는 Python 계산이며 Wolfram이 이를 다시 계산했다고 주장하지 않는다.

## 전달 구현/검증 패키지

Filename=BASS_CR_R4P0A_B0_TAIL_RESEARCH_20260930_v1.zip
Bytes=108127
SHA256=6f67bdf78834ab410538840564fac7d752bf830b64bb625771ba38e2bd2a51c0
Google Drive object=1i4lRvC3XQgQvieANqVxZw_BNVxqvBD6u

패키지에는 다음이 있다:
- projector_rate_probe.py: rate matrices/generalized rho 및 frozen endpoint reader
- tail_plan_adapter.py: exact B0 signed8 runtime-ID mapper와 per-sample matrix diagnostics
- tests/:15 synthetic algebra tests +10 planner/diagnostic tests
- BOUND_B0_TAIL_QUERY_PLAN.json, NEXT_SCOPE_CONTRACT.json
- 한국어 full report/handoff, 문헌 provenance, Wolfram 결과/수정기록
- 원본 R4P0 source/input fixtures 및 각 파일 manifest

Fresh 연구 code25 passed. 배포 ZIP fresh extraction도25 passed, manifest50개 일치, endpoint CLI exit0, external PYTHONPATH false. R4P0 원본40개와 별개인 신규 suite다. Native launcher는 이 research ZIP에 없으며 이 문서도 새 native authorization이 아니다. Git에는 원 NPZ를 중복 저장하지 않는다.

## 다음 단계: 최소 B0 실행 연결

전달한 구현을 재작성하지 말고 기존 qualified_provider/analytic_adapter/R4F worker/global budget 및 cooperative supervisor에 최소 연결한다. 실제 source integration/native-trap를 통과한 뒤 새 execution commit/tree 및 명시적 승인 객체를 고정한다. 현재 f7 commit 또는 이 research commit을 native-ready executable로 취급하지 않는다.

Scope:
- B0 18 channels, E100 keV/u,b2 a0
- signed z=[-16,+16,-20,+20,-24,+24,-32,+32] a0
- exactly8 unique operator queries; max88 raw operator evaluations
- 11 ordered ladder/first passing adjacent pair 및 원 static screens 유지
- source/library/BUILD/radial bank coefficient identity/same_center_order20 유지
- no new parity, no derivative FD samples, no native baseline rerun, no full propagation
- B1–B3 actual runtime, N3072, reference rerun, b-grid/all-bound/capture는 제외

기존 R4P0 operator_diagnostics는 z12 baseline용이다. 새 row에 그대로 적용하지 말고 전달 snapshot_diagnostics의 실제 z/R/time 메타데이터를 쓴다. PLAN_ONLY IDs를 qualified provider cache IDs로 쓰지 않는다. 어댑터가 새 static-tail context와 provider schema의 IDs를 별도로 생성한다.

Qualified provider에서 실제 평가되는 것은 raw cross relative convergence, S/H Hermiticity, metric SPD ratio다. 과거 screens dict에 metric derivative/trajectory gates가 들어있다고 static scope에서 PASS로 표시하지 말라.

각 query의 원 JSON+NPZ/raw ladder/최초 실패를 보존한다. Tail의 near-zero block 때문에 relative screen이 막혀도 tolerance/floor를 자동 완화하거나 unqualified sample을 qualified로 바꾸지 않는다. +z와-z를 대칭 가정으로 복제하지 않는다.

4-worker(최대8), numerical threads1, wall3600s/grace60s는 미승인 자원 제안이다. 작업8개에32-worker pilot을 반복하지 않는다. COOPERATIVE_SHARED_HOST 유지: 외부 BASS broad affinity는 telemetry, allowed affinity/quota/RAM/own-pool/identity/budget/deadline는 hard gate. 다른 job은 kill/stop/repin/renice하지 않는다.

Native 연결 후 targeted checks만 수행한다: no approval→native factory0, exact8 times/IDs, synthetic evaluator→기존 ordered provider→durable pair→diagnostics, global cap88, timeout/partial preservation, native-trap, package dependency closure. 원본 source가 그대로면 기존40 tests를 감사용으로 반복하지 않는다.

최종 native 실행 조건은 live census와 새 고유ID/정확CPU/RAM/wall/deadline/cost를 포함한 한 개 proposal JSON에 기계적으로 생성한다. 아직 승인/소비하지 않는다. 기존 A3 소모 nonce/예산/deadline는 재사용하지 않는다.

Stop at R4P0_B0_OPERATOR_EXECUTOR_READY__EXPLICIT_NATIVE_AUTH_PENDING.

## 문헌 범위

SciSpace와 primary publisher abstract를 대조:
- Artacho/O’Regan2017, DOI10.1103/PhysRevB.95.115155: moving-basis connection/derivative framework. 위 W식은 이 연구의 직접 유도.
- Toshima1999, DOI10.1103/PhysRevA.59.1981: pseudostate placement/completeness의 별도 convergence. 무조건 큰 대칭기저 최적이라는 주장이 아님.
- Runge/Micha1996, DOI10.1103/PhysRevA.53.1388: ETF/basis/time-dependent population. 연구 에너지는 주로10keV 이하이며 현재100keV/u endpoint 정량기준이 아님.

원문 전체를 읽은 것으로 표시하지 않는다. Literal evidence와 이번 유도를 구분한다.

Claim ceiling unchanged:
capture=false; production=HOLD; all_bound=OPEN; b_grid=NO_GO;
original_capture_gap_resolved=false; continuous_global_supremum_bound=false;
continuous_trajectory_error_bound=false.
