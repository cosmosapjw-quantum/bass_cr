# BASS_CR R4T 연구 결과 — 이동기저 상쇄와 상태별 오차 상계

2026-10-01. R4R 이론과 R4S HPC 구현을 복원한 뒤 다음 연구 단계를 완료했다.
상쇄를 보존하는 정확한 rate 분해, 상태별 누적 오차 정리, 약한 잔차의 정칙성 제약,
기존 모형과 참조모형 사이의 조건부 상태 비교 정리를 추가했다.
새 근거 7건을 DB v6에 반영했다. 실제 B0 꼬리·포획 확률은 아직 인증하지 못했다.

선택 공간과 그 S-직교여공간의 정규화 기저를 X,Y라 하면, 고정 선택자에서

\[
E=Y^\dagger(D+iH/\hbar)X,\qquad \rho=\|E\|_2.
\]

이 식은 기존 W의 일반화 고유값 계산과 정확히 같다. H와 D를 합친 후 선택 공간의
성분을 제거하므로, 큰 개별 항의 노름을 더할 때 사라지던 상쇄를 유지한다.
시간에 따라 변하는 선택자에는 추가 연결항을 포함했고 좌표 변환 불변성도 증명했다.
정규화 점유율 p=P/N에는 다음의 더 날카로운 조건부 경계가 성립한다.

\[
|\dot p|\le2\sqrt{p(1-p)}\,\rho,\qquad
|\arcsin\sqrt{p_1}-\arcsin\sqrt{p_0}|\le\int\rho\,dt.
\]

끝점 p=0,1도 포함한다. 초기 상태를 모를 때의 최적 경계는
\( |p_1-p_0|\le\sin(\min\{\int\rho dt,\pi/2\}) \)다.
정확 유리수 helper는 상태 구간과 rate 적분 상계가 주어졌을 때 안전한 확률 예산을 계산한다.
기존 ±12 결과의 표시값을 사용한 약5.11배 허용 적분량 예시는 설명용이며,
±32의 상태나 실제 꼬리 오차 인증으로 사용하지 않았다.

ETF의 운동항과 이동기저 항은 다른 중심 사이에서도 약형식으로 정확히 상쇄된다.
이후에는 다른 중심의 시험함수에 대한 isolated weak residual과 원격 Coulomb potential의
선택 공간 밖 성분이 남는다. potential 성분에는 불필요한 역 Gram 인자를 제거했다.
기존 정확 입력만 사용한 H1 참조모형의 보수적 결과는 다음과 같다.

| 항목 | R4R | R4T |
|---|---:|---:|
| 편측 [32,128]의 raw rate 적분 상계 | 5037.0909 | 504.54 |
| 확률 범위로 제한한 변화량 상계 | 1 | 1 |
| 편측 목표 0.000005 인증 | 실패 | 실패 |

raw 상계는 줄었지만 실용적인 확률 정확도는 아직 개선되지 않았다. 이 수치는 별도로 정의한
H1 참조모형에 대한 것으로, 원래 B0 궤적에 적용한 결과가 아니다.

정확 계수 검산에서는 repaired radial mode 5개 모두 40개 shell에서 미분 불연속이 확인됐다.
두 l=1 mode에는 원점의 추가 strong-domain 제약도 있다. 따라서 weak residual을
strong L2 residual로 대체할 수 없다. 원래 저장 기저의 작은 값 불연속도 정확히 비영이어서,
셀 내부 미분 차이를 전역 H1 거리로 해석할 수 없다.

이를 피하는 finite-metric Duhamel 비교 정리를 유도했다. 두 모형의 metric compatibility
defect, 시간 의존 비교맵과 그 미분, 초기 상태 차이, 공통 L2 공간에서의 embedding 차이,
관측자 차이를 모두 포함한다. 정리는 완성했지만 실제 연속 행렬 경계와 상태 입력이 없어
B0 상태 전이 오차값은 아직 산출하지 않았다. 필요한 항목은
`regularity/TRANSFER_INPUT_CONTRACT.json`에 명시했다.

검증 결과는 신규 테스트30개 통과·skip0, 별도 Fraction 등식33개 검산, 실제 저장 행렬6개
비교 통과다. 새 분해와 기존 W 방식의 최대 상대 rho 차이는7.2215×10⁻¹⁶이었다.
비교에는 명시적으로 S,H의 Hermitian 부분과 Sdot=D+D†를 사용했다.
이는 수식 구현의 비교이며 G02의 독립 미분 검증이나 연속 상계가 아니다.
첫 실패 기록을 보존했고 독립 검토에서 요청한 strong/weak domain 설명을 보완했다.

새 물리 operator query와 물리 전파는0회다. 기존 시험은 반복하지 않았다.
R4S OpenMPI·Fortran·SIMD 구현과 정확도 정책은 그대로 유지했다. 이번 계산은 작은 행렬의
BLAS/LAPACK 연산과 정확 유리수 증명이므로 병렬 적분 커널을 새로 만들 필요가 없었다.
64코어 NCP 성능이나 binding을 새로 측정한 결과는 없다.

DB v5의 기존30개 표와 연구 주장29건을 보존했고 v6의 연구 주장은36건이다.
13개 공백의 상태 수는 CLOSED3, RESOLVED_WITH_LIMITATION6, BLOCKED1, UNRESOLVED3으로
유지했다. 조건부 세부 명제의 근거가 늘었으며 물리 gate를 승격하지 않았다.
전체 B0 오차 예산 합계는 여전히 미정이다.

다음 최소 연구는 foreign-test weak residual과 centered potential coupling의 연속 구간
상계를 더 정밀하게 만들고, 상태 비교 계약의 실제 입력을 확보하는 것이다. 새로운 물리
실행이 필요해지면 정확한 source/native/context·자원·예산을 별도로 고정해야 한다.
기존 G02/G03 승인을 새 참조모형이나64코어 실행으로 확대하지 않는다.

`capture=false`, `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`를 유지한다.
`original_capture_gap_resolved`, `continuous_global_supremum_bound`,
`continuous_trajectory_error_bound`도 모두 false다.

작업 브랜치는 `research/r4q-gap-closure-20261001`, 시작 HEAD는
`006736c3cbe815c8eaeb09ba5bcc757c30a832c4`다. 최종 HEAD/tree와 게시·백업 결과는
동봉한 `BASS_CR_R4T_CLOSEOUT_20261001.json` 및 `BASS_CR_R4T_DELIVERY_RECEIPT_20261001.json`에
기록했다. 일반 게시와 백업은 R1, 이번 작업 시작 시 패키지 복원은 전 파일 해시 검증 R3다.
