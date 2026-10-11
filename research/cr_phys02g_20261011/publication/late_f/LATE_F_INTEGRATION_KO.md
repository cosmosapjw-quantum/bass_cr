# PHYS02G 게시 중 도착한 실제 F 반환의 통합

## 현재 결과와 우선순위

G의 과학 커밋은 `0ad3be0fec018fbd638063ffd4bf4d0cf2ef8525`이며, 저장 모멘트 분석과 후처리 준비의 독립 판정은 PASS_SCOPED다. 후보를 고정한 뒤 실제 F 반환 PR37이 2026-10-11 07:02:57 UTC에 생성됐고, G의 PR38을 만드는 과정에서 이를 확인했다. 기존 G의 코드·수치·계약·판정·시점별 상태는 바이트 그대로 보존한다.

**현재 실행 상태는 F의 HOLD_OPERATOR_BINDING_UNRESOLVED와 G frontier의 BLOCKED_BY_F_OPERATOR_BINDING_HOLD다.** 이전 내부 상태에 기록된 “조회 범위에서 F 반환을 관측하지 못함”과 WAITING은 당시 기록이다. 다음 작업은 이 문서와 NCP_READONLY_DIAGNOSTIC_CONTRACT.json의 읽기 전용 대조이며, 내부 START의 미예약 F 최초 실행 분기는 이 관측된 실패 실행에 적용되지 않는다.

## 실제로 일어난 일

| 항목 | 관측된 기록 |
| --- | --- |
| F actual PR / head | PR37 / a490ab7af8e7b1b4db9a604293867df8e6d035dd |
| 실행 구간 | 2026-10-11 06:41:06–06:42:54 UTC |
| 모델 | fullBED |
| G 예약 / 생성 완료 | 1 / 1 |
| resolvent / triangular solve / pulse / expm | 0 / 0 / 0 / 0 |
| execute / collect / wrapper 실제 exit | 1 / 0 / 1 |
| coordinator / wrapper wall | 107.954172934 s / 109.790418950 s |
| 중단 | launch_residence.py:119 → residence.py:47, OPERATOR_IDENTITY_MISMATCH |
| 후속 legacy 또는 재시도 | 0; 허용하지 않음 |

두 wall은 중첩 구간이므로 합산하지 않는다. Coordinator wall을 G constructor만의 시간으로 해석하지 않는다. 수집 exit 0은 실패 증거의 수집 성공이며 과학 실행의 성공이 아니다.

행렬은 CSC 9,611×9,611, nnz 36,193,027이며 저장 에너지는 9,600개다. shape, nnz, indices, indptr, 저장 격자 및 method-binding이 일치하지만, data의 raw little-endian C-order SHA256이 다르다.

- 기준: 6bd1d6aeeaccf4cc717229e3f9beff0cf072a157c844dd75ba2353be5f15f4cd
- 현재: 8e33e916c4a24d57c9dad0f82ef046a81a818437e64cafb2e580d4c8809ea3fa

동일 버전·단일 thread 기록 안에서도 OpenBLAS dispatch는 기준 SkylakeX와 현재 Haswell로 달랐다. 이것은 관측된 provenance 차이다. 이 차이가 원인이라는 결론, 오차 크기, roundoff-only 또는 수치적 동등성은 확립되지 않았다. 하드웨어 이름만 보고 dispatch를 강제하거나 기준 SHA를 바꾸지 않는다.

## 왜 이 불일치가 모멘트 계산을 막는가

저장 pulse를 만든 active 연산자를 A, 재구성한 active 연산자를 B=A+ΔA라고 하자. 같은 heat row h를 가정하더라도, 실제 pulse의 마지막 상태 x_A(T)에 B로 구한 q_B=B^{-T}h를 곱한 값이 A의 동일 semigroup에서 나온 잔여열이라고 이 자료만으로 인증할 수 없다. 전체 G의 data hash 차이만으로는 active A, heat row 또는 다른 누적행 중 어느 부분이 변했는지 알 수 없다. 아래 식은 같은 h와 가역 A, B를 가정한 조건부 대수 설명이며, 실제 active ΔA가 비영이라는 관측이나 두 semigroup의 비동등성 증명이 아니다.

두 역행렬이 존재할 때의 정확한 항등식은

\[
B^{-1}-A^{-1}=-B^{-1}\Delta A A^{-1},
\qquad
q_B-q_A=-B^{-T}\Delta A^Tq_A
\]

다. 따라서 data hash 차이를 작다고 추측하는 것만으로 기존 pulse와 새 resolvent를 결합할 수 없다. 실제 ΔA 값, 관련 조건성과 물리 허용기준 없이 오차 크기도 계산할 수 없다. 반대로 해시가 다르다는 사실만으로 큰 물리 오차나 과학적 무결성 위반을 주장할 수도 없다. 이번 중단은 두 입력의 정확한 연결을 요구한 계약이 작동한 결과다.

기존 G의 scalar 분석은 채택한 이전 E/F 저장 모멘트의 수학적 평가로 보존된다. 새 F에서 얻어야 할 q0, q1, q2, xT의 frontier 결과는 아직 없다. 따라서 기존 곡선과 방출시간 구간을 state별 자료로 더 좁혔다고 주장하지 않는다.

## 다음 NCP 작업

`CR-PHYS02G-NCP-OPERATOR-PROVENANCE-INTAKE`를 준비한다. 입력은 완전한 실패 반환과 원래 E/F/G source, 실제 호스트에 이미 보존된 관련 연산자와 runtime 기록이다. 새 G 생성·resolvent·solve·pulse·expm·F retry·G frontier 실행은 모두 0이다.

원래 reference CSC와 실패 당시 current CSC의 실제 값이 둘 다 보존되어 있고 각 identity가 기록과 연결될 때만 저장 배열 비교를 한 번 할 수 있다. 한쪽이라도 없으면 MISSING_PERSISTED_OPERATOR_VALUES로 남긴다. 기존 E cache가 기준 fingerprint와 일치하더라도 provenance와 새 입력 계약이 승인되기 전에는 후보일 뿐이다. 새 재구성이나 재시도는 이 읽기 전용 단위에 포함되지 않는다.

실패 반환의 기존 Astra 판정은 controller가 전사한 기록이다. 독립 reviewer backend의 직접 인증이나 원시 네 명령 transcript가 확보됐다고 말하지 않는다. 이번 세션의 별도 독립 검토는 실제 보존된 실패 파일과 입력 identity를 대상으로 제한한다.

## 완전한 단일 전달본

외부 전달 ZIP은 바이트가 고정된 G core ZIP과 실제 F 실패 tar.gz를 함께 담는다. G core 안에는 이전 완전한 F 준비 ZIP과 실제 E 자료, 두 canonical Astra v4.0.0 하네스가 있다. 실제 F tar 안에는 numerical return ZIP, 원본 family manifest, 외부 종료 sidecar와 실패 로그가 있다. 과거 파일을 다시 전달할 필요가 없다.

G core의 새 디렉터리 복원과 stdlib plan은 한 번 수행해 exit 0, PREPARED_SOURCE_ADMITTED 및 WAITING_FOR_F_ACTUAL_RETURN를 확인했다. 실제 G/F 성공 경로의 실행 검증은 아니다. 현재의 더 엄격한 F HOLD는 이 통합 기록과 외부 시작 파일에서 유지한다. 새 outer envelope의 entry 및 hash 확인은 별도 게시 영수증으로 기록한다.

G-R01도 유지한다. 저장 FP64 산술에서는 10개 방출시간 구간의 끝점 조건이 통과했지만 exact decimal-token 비교에서는 8개 구간에서 약 10^{-17} 확률 여유의 부호 차이가 있었다. 원시 끝점은 directed rounding을 사용한 인증 구간이나 물리 불확실성 구간이 아니다.

PHYS02_DELAY OPEN, production_history HOLD, atomic_G02 UNRESOLVED, b_grid NO_GO, all_bound OPEN, R17B2B NO_CERTIFIED_SOURCE_SHARPENING, CCC_2026_exporter_identity SOURCE_IDENTITY_UNRESOLVED를 유지한다.
