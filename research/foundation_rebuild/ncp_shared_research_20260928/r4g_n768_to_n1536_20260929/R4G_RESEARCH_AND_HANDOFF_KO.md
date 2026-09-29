# R4G: 완료된 N768 분석과 N1536 준비 계약

상태: N768_EVIDENCE_ADMITTED__SECOND_ORDER_SUPPORTED__N1536_PREPARATION_ONLY.
새 native operator 계산, reference 적분, N768 재전파 또는 N1536 실행은 하지 않았다. 이 문서는 새 executable이나 native authorization이 아니다.

## 1. 실제 원본과 검증 범위

N768 executable commit=11100b35f78ec26100ea732971bb4ce0f9925719
tree=05976e386c0a39591247d69c32c8cb28fa3f2a97
completed authorization=R4F-N768-MIGRATION-REPAIR-20260929-A2

Dropbox object id:BSpOijBcT10AAAAAADvMpg의 실제 bytes를 Files materialize로 확보했다.
filename=R4F-N768-MIGRATION-REPAIR-20260929-A2_RETURN_dd8b3b18.zip
bytes=66755501
SHA256=dd8b3b185ce7c31a16b85d929291ef38d3d8ad666992e5bc1a9e03789e4384f3
Dropbox content_hash=6fce6004e5c6f3f4a6f201ecef205f436cee1d75ba48682e91e97781ec77b948

ZIP CRC 정상, 6467 entries, 내부 manifest 6466 entries의 size/hash 불일치 0. 실제 계산한 Dropbox block-content hash도 provider metadata와 일치한다. canonical query store의 2047개 pair에 대해 query identity/payload hash를 검사했다. 이것은 Dropbox 원본 복원 검증이며 원본 Drive copy의 재다운로드 검증은 아니다. 실제 NCP 프로그램을 여기서 재실행하지 않았다.

핵심 원본 파일 해시:
- RETURN_REPORT.json: 31cf9c0545237c6597227dc7fcf1d7a9ae678c9d52936b270adcb378e28f8869
- CANDIDATE_N768.npz: ff2c2513e933fbae0540317f943bded344b5367e301c7cf23fbecc210ef7bea3
- EXECUTION_ADMISSION.json: 26393b50c85d6c46b0e49e74e6c34b540d604fbf0efd75d62646aa9556a9b499

원본 RETURN/supervisor에 따르면 종료는 2026-09-29 16:31:06 KST, coordinator wall=5089.434736543s, exit=0, descendants_exited=true다. 과학 상태는 R4E_N768_BRIDGE_COMPLETE__N1536_DECISION_PENDING이다.

## 2. 관측 수치와 실제 후처리 검산

원본 pair 값:
d384_ref=2.634560877280569e-6
d192_384=7.904769432369909e-6
d768_ref=6.586233081176365e-7
d384_768=1.9759375704674717e-6

N768 weighted norm drift=8.659739592076221e-15
N384 weighted norm drift=8.548717289613705e-15
DOP853 reference norm drift=4.259903541026233e-11
reference rtol=1e-10, atol=1e-12; numerical reference이지 exact solution은 아니다.

원본은 required770/770, cache-only replay native operator calls0을 보고한다. 저장된 최종18성분 상태와 같은 S_final로 거리만 독립 재계산하여 receipt와 약1e-17 이하 범위에서 일치했다. reference나 시간전파는 재실행하지 않았다.

Python과 Wolfram 산술이 일치한다:
p_ref=log2(d384_ref/d768_ref)=2.0000370430175645
p_self=log2(d192_384/d384_768)=2.000186016578518

상수 관측 order를 가정한 다음 rung heuristic:
d_ref1536_pred=d768_ref^2/d384_ref=1.646515993373354e-7
d_self1536_pred=d384_768^2/d192_384=4.939207039229666e-7

d384_768/(3*d768_ref)=1.0000342361173318.
이것은 near-second-order temporal regime을 지지하지만 operator/basis/reference 공통오차를 인증하지 않는다. Richardson 외삽 상태로 reference를 교체하거나 frozen thresholds를 완화하지 않는다.

## 3. N1536에서 두 거리 기준을 함께 만족하는 충분조건

같은 positive-definite Hermitian S_final에 대해 d(a,b)=min_phi ||a-exp(i phi)b||_S는 phase quotient metric이다. A=c768, X=c1536, R=numerical reference라 두면 삼각부등식으로

d(A,X) <= d(A,R)+d(R,X).

따라서 실제 d(X,R)<=1e-6-d(A,R)=3.413766918823635e-7 이면 두 distance screens가 모두 통과한다. 이는 reference가 exact라는 가정을 필요로 하지 않는 상태들 사이의 기하학적 충분조건이다. norm/operator screens는 별도로 유지한다.

현재 heuristic을 대입한 보수적 upper proxy는
d768_ref+d_ref1536_pred=8.232749074549719e-7<1e-6.
단, 미래 d_ref 예측이므로 아직 실제 PASS가 아니다.

중요: N768에서 사용한 'dual PASS는 inconsistency' guard는 N1536에 적용하면 틀리다. N1536에서는 dual PASS가 가능한 정상 결과다. 기존 N768 경로는 변경하지 않고 새 rung 경로만 올바르게 정의한다.

## 4. Exact N1536 query plan

원 run_candidate 연산 순서를 그대로 사용한다:
dt=(tf-t0)/1536; ta=t0+j*dt; tb=ta+dt; tm=0.5*(ta+tb).
step width=tb-ta. linspace 또는 t0+(j+0.5)*dt로 바꾸지 않는다.

완료된2047 canonical queries와의 exact binary64 query-ID 비교:
- N1536 required unique accesses=1538
- reused exact endpoints=2
- new midpoint IDs=1536
- completed future union store=3583
- dt1536=0.007781447873487904 atomic time

1538 active queries는 기존 per-run cap2048 안이다. inherited union3583을 active count로 오인하지 말고 cache를 삭제하거나 active cap을 자동으로 늘리지 않는다.

PROPOSED_N1536_QUERY_PLAN.json SHA256=586f937a38c768ec91b9facde529a970bf388afdc4914f3ce7518fbc6a60dc0f
이 계획은 실제1538행과 missing ID1536개를 담은 준비 자료이며 실행 승인은 아니다.

## 5. Resource evidence와 새 예산

완료 A2 ledger: parent374 + new reservations2154 = cumulative2528.
new2154 중 endpoint parity4, useful582 queries2150이다. 성공한 전체768 midpoint qualification은 합계2522 raw evaluations를 사용했다.

기존768 midpoint의 resolution 패턴을 새1536 grid에 nearest-neighbour 투영한 예상 useful raw=5044. 같은8-worker 조건에서 실제 A2 wall을 query/raw로 스케일한 중심 추정은 약3.3~3.7시간이다. tail/부하/검증/호스트 변동에 대한 보장이 아니다.

새1536 scope의 deterministic worst case:
useful1536*11=16896 raw attempts.
새 bounded parity2 queries를 별도 승인하는 경우 +22 => incremental16918.
역사적2528을 더한 lifetime reporting worst=19446.

기존8470 cap, A2 nonce, 누적50000원 또는 기존 deadline은 새 rung의 실행 권한이 아니다. 새 exact executable과 query manifest가 준비된 뒤 사용자가 raw/wall/cost/deadline/CPU/RAM을 명시적으로 승인해야 한다. 5h wall은 제안일 뿐 현재 승인값이 아니다. 초기자원 제안은 최대8 workers, CPU0..7, worker당1GiB, 네 수치 thread 변수1이며 실제 공유호스트 배정을 재확인한다.

## 6. Codex에 인계할 준비 작업

Role=N1536_SUCCESSOR_PREPARATION. 이 단계는 non-native 구현/검증/패키징까지만 수행한다. 현재 메시지를 native permission으로 해석하지 않는다.

1. 완료 A2 output_RETURN.zip과 SOURCE_PINS.json을 source로 삼는다. A2는 completed/consumed다. 원본 stop/failed-A1 자료는 과거 lineage로만 남기고 현재 predecessor를 InterruptedError로 요구하지 않는다.
2. 성공 predecessor validator를 별도 추가한다. source zip/report/candidate/reference/basis/context/library/dependency/manifest를 실제 bytes에서 검증한다. 원본1279-only validator나 fixed768 runner를 억지 override하지 않는다.
3. 새 entrypoint는 previous768->next1536 한 rung만 허용한다. previous comparison state=c768; propagation initial state=원래 initial state; reference와 S_final은 동일 계열. c768 final state 뒤에1536 steps를 이어붙이지 않는다.
4. 기존 single-thread native worker/ordered qualification/cache-only reader를 가능한 그대로 재사용한다. planner의 nstep bound와 성공 predecessor adapter를 좁게 분리하고 무제한 ladder/generic retry engine으로 확장하지 않는다.
5. required1538/initial hits2/missing1536을 실제 plan과 대조한다. 완료 query는 재계산하지 않고 missing만 bounded pool에 분배한다. useful pilot8개는 missing에 포함하고 결과를 보존한다. 재사용 가능한 native parity evidence는 재실행하지 않는다. worker/native/runtime가 변해 새 parity가 필요하면 별도22raw scope로 제안한다.
6. strict cache-only replay는 원래 initial state에서 unchanged run_candidate(...,1536)로 수행하는 실행경로만 준비한다. 현재 단계에서 실제 replay는 하지 않는다. future coverage1538/1538 전에는 replay 불가; evaluator 없는 reader가 miss에서 실패해야 한다.
7. 새 gate는 actual d1536_ref<=1e-6, d768_1536<=1e-6, previous/current/reference norm screens 및 operator qualification의 conjunction이다. N768 dualPASS-impossible guard를 새 경로에 복사하지 않는다. 세 거리의 일반 triangle checks만 적용한다. 예측값/새 충분조건은 기존 gate의 대체물이 아니다.
8. focused tests: N768 backward compatibility;1536 exact time_hex/width; successful A2 predecessor admission; identity/hash/nonfinite failures; union3583 vs active1538; missing-only dispatch/global budget;1536 synthetic dualPASS/UNRESOLVED; cache miss zero evaluator; timeout/group shutdown/partial evidence. 실제 launcher->parser->source import->worker boundary까지 native trap을 둔 통합 smoke로 이전 restore-API/exit126/lineage 재발을 검사한다. source파일 mode100644이면 명시 bash로 실행한다.
9. future candidate/metrics/receipt는 gate분류 실패나 UNRESOLVED여도 잃지 않도록 classification 전에 durable 저장한다. scientific FAIL과 timeout/implementation 실패를 구분한다. no automatic3072, retry, new nonce, reference rerun, capture/all-bound/b-grid.
10. 새 code/test 실행결과와 exact commit/tree, source/query manifests, 예산 제안, return contract를 non-force 게시하고 create-only 이중백업한다. 승인문은 검증한 manifest에서 기계적으로 생성하여 hash를 손으로 재입력하지 않는다. N1536_IMPLEMENTATION_READY__NATIVE_AUTHORIZATION_PENDING에서 멈춘다.

## 7. 문헌과 범위

SciSpace로 문헌 후보를 찾고 원 출판/기관 페이지를 대조했다.
Auzinger,Hofstaetter,Koch,Quell,Thalhammer, ESAIM M2AN53(2019)197-218, DOI10.1051/m2an/2018050: Magnus-type local defect error estimators.
Blanes,Casas,Gonzalez,Thalhammer, IMA J Numer Anal41(2021)594-617, DOI10.1093/imanum/drz058: nonautonomous linear Schrodinger CFQM convergence under regularity/stability assumptions.
이는 order/structure/error의 구분을 뒷받침하며 BASS moving-basis midpoint 구현의 직접 인증은 아니다.

유지: capture=false; production=HOLD; all_bound=OPEN; b_grid=NO_GO; original_capture_gap_resolved=false; continuous_global_supremum_bound=false; continuous_trajectory_error_bound=false.

## Full reproducible research package

BASS_CR_R4G_N768_TO_N1536_20260929_v1.zip
bytes=179388
SHA256=a1f182153bd7cf293ea14e8e0bbf82cfe713d2793a350a89e62e9becc038f3e9
Drive object=18JsiHyhXWEEcAbdHnIKYvkNRu2u_xlNF
내용: 한국어 보고서, 상세Codex prompt, machine-generated SOURCE_PINS,1538행query plan, ANALYSIS, 검산Python/Wolfram 및 원source receipts. 새production runner는 포함하지 않는다. 별도delivery receipt가 provider acknowledgement를 기록한다.

## 8. Adaptive worker scaling addendum (2026-09-29)

N768의 8-worker 상한은 최초 production 병렬 migration의 안전/검증 envelope였으며 물리적 또는 NCP hardware 한계가 아니다. N1536 successor 준비에서는 기존 N768 exact commit을 변경하지 않고 별도 successor-scoped policy를 추가한다.

- policy code: `adaptive_workers.py`
- machine contract: `ADAPTIVE_WORKER_POLICY.json`
- focused tests: `tests/test_adaptive_workers.py`
- updated handoff: `CODEX_HANDOFF_N1536_ADAPTIVE_WORKERS_KO.md`

기본 scaling stage는 `8 -> 16 -> 32`, hard max는 32다. 각 worker 내부의 OMP/OpenBLAS/MKL/NumExpr thread 수는 계속 1로 유지한다. 64-worker stage는 현재 준비 범위 밖이다.

성능 측정을 위해 별도 benchmark query를 재계산하지 않는다. missing 1536개 중 서로 겹치지 않는 useful query를 결정론적으로 stratified sampling하여 8-worker stage에 8개, 16-worker stage에 16개, 32-worker stage에 32개를 배정한다. 성공 결과는 모두 canonical cache에 남기므로 세 stage 전체를 수행해도 scientific missing count는 그대로 1536이며 pilot 뒤에는 1480개만 남는다.

stage 비교 지표는 실제 `queries/second`이며 실패가 없는 stage만 후보로 둔다. 최고 throughput stage를 나머지 fill에 사용하고 exact tie에서는 worker가 적은 stage를 선택한다. 이 scheduling rule은 승인된 CPU/RAM/raw/wall/cost scope를 확대하지 않는다.

resource admission은 live CPU affinity와 shared-host RAM을 다시 읽어야 한다. planning value는 worker당 1 GiB이며 32-worker stage는 worker pool에 32 GiB envelope가 필요하다. 다른 BASS 작업의 자원을 침범하거나 64-vCPU 전체를 자동으로 점유한다고 가정하지 않는다.

이 addendum 자체는 native authorization이 아니다. 새 N1536 runner가 adaptive policy를 실제 admission/pool lifecycle에 통합하고 non-native integration smoke를 통과한 뒤 `N1536_ADAPTIVE_IMPLEMENTATION_READY__NATIVE_AUTHORIZATION_PENDING`에서 멈춘다.
