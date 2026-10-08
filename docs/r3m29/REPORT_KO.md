# R3M29 — point-Coulomb cell 및 subcell phase 국소 판별

## 판정

입력은 R3M28 exact `8656736dd1b45b748b0669f4a7dafdb71787e032`와 사전 등록 [DESIGN](../../results/R3M29/DESIGN.json) SHA `3515a656ea9d2c8b5bad912b6bf815024c5ab44973d908ebfba3358b039be6ca`다. A3/B3 결과, frozen `cr_repro/tdl.py` 및 grid/config bytes를 묶었다. 새 preparation/full collision/GPU run은 각각 **0회**이며 production source나 representation을 바꾸지 않았다.

[최종 국소 결과](../../results/R3M29/RESULT_V3.json)는 point-sampled (1/r)과 특이점 인접 cell의 체적평균을 비교한다. 핵이 x,y cell 경계에 있고 z subcell 위치를 \(\alpha\)라 두면, z 방향은 해석적으로 적분하고 남은 적분 가능한 로그 모서리 특이점의 2차원 적분을 adaptive SciPy 적분과 별도 Gauss–Legendre 64/128/256차로 확인했다. 직접 3차원 적분도 시험했다. 256차 대 adaptive 상대차는 세 위치에서 `1.5e-10` 이하다. 아래 값은 `h × cell mean`과 `h × midpoint`로 정규화되어 h=.25와 .20 모두에 적용된다.

| z phase α | h×체적평균 | h×점값 | 점값의 상대 bias |
|---:|---:|---:|---:|
| 0 | 1.1900386819897764 | 1.1547005383792517 | −2.9694953740% |
| .25 | 1.3689537864661967 | 1.3333333333333333 | −2.6020201328% |
| .5 | 1.4272601797003581 | 1.414213562373095 | −0.9141022438% |

A3/B3 config에서 target 원점과 b=2 projectile의 x/y 핵 위치가 두 cell-centered 격자 모두 **cell 경계/vertex**에 놓이는 기하를 확인했다. 실제 7172개 시간 중점에서 projectile z 위치의 32-bin phase histogram은 h=.25와 h=.20의 총변동거리 `0.000557724484104849`로 사전 기준 `.01`보다 작았다. 이는 phase 방문 빈도의 큰 불균형이 보이지 않는다는 진단이지, phase-dependent 동역학 효과가 작다는 증명은 아니다.

사전 기준의 수치 판정은 `LOCAL_CELL_AVERAGE_CANDIDATE_PRIORITIZED_PHASE_OCCUPANCY_BALANCED_NOT_CAUSALLY_RESOLVED`다. 특이 cell에서 기존 점값의 체적평균 대비 국소 bias가 모든 세 phase에서 .5%를 넘고, 두 격자의 phase 방문 분포는 비슷하다. 따라서 **cell-averaged point-Coulomb은 다음 한정된 동일-h 검증 후보로 선정**한다. 기존 점값 표현의 production 사용을 지금 변경하거나, 이 국소 bias를 R3M28 최종 포획확률 3.03–3.29% gap의 원인·오차상한으로 해석하지 않는다. FFT kinetic, preparation, projector, 전체 trajectory의 비선형 반응은 이번 계산에 없다.

가장 강한 반론은 국소 (1/r) bias와 최종 확률 gap의 퍼센트가 비슷해도 sensitivity 및 상쇄가 전혀 검증되지 않았다는 것이다. 그래서 이 결과는 **후보 선택 GO / 공간 budget 및 production NO_GO**로 범위를 나눈다. 다음 시험은 보존된 같은-h state에서 point-sampled와 cell-average action의 짧은 창 endpoint와 독립 기준을 비교해 차이의 방향·크기·비용을 검증해야 한다. 그 전에는 representation 변경을 승인하지 않는다.

## 실행·검증과 보존

[원래 첫 결과](../../results/R3M29/RESULT.json)와 기하 결합을 추가한 `RESULT_V2.json`도 보존했다. [독립 검토](../../results/R3M29/INDEPENDENT_REVIEW.md)는 V2의 재구성 궤적 연산 순서가 frozen TDL의 시간 중점 계산과 달라 일부 경계 bin이 1개씩 이동함을 발견했다. 최종 V3는 `v*(t0+(j+.5)*dt_actual)` 순서를 그대로 사용한다. h=.25의 bin 0/31은 228/224→227/225, h=.20의 bin 7/8은 224/226→225/225로 바뀌었다. 총변동거리와 후보 판정은 그대로다. V1/V2를 덮어쓰지 않았다. 적분 함수 표현과 역사적 DAG 문장도 바로잡았다. 수치 계산 CPU wall은 약 `0.06 s`이며 큰 격자나 full collision 성능 추정이 아니다. 소규모 독립적분과 실제 phase-count의 4개 전용 시험이 통과했다. 전체 repository 시험은 수정 전과 수정 후 모두 `492 passed, 3 skipped`이며 [수정 후 로그](../../results/R3M29/FULL_TESTS_AFTER_REVIEW.stdout)에 보존했다. 과거 R3M28 공간 pair NO_GO, R3M27 고정-h 시간 검증, `production=HOLD`, `all-bound=OPEN`, `b-grid=NO_GO`, preparation/CAP/box/final-time 미해결은 유지한다.

## 다음 canonical node 하나

`N1_TDL_PRODUCTION_H_CELL_AVERAGED_COULOMB_SAME_H_SHORT_WINDOW_VALIDATION`: production source와 별도의 opt-in 후보에서 cell average의 수학적 구현을 작은 독립 기준으로 검증하고, 보존된 B3 state의 짧은 동일-h 창에서 point-sampled와 accuracy-matched reference에 대한 endpoint 차이·실측 비용을 비교한다. 새 full collision, preparation, finer h, B4, b-grid는 이 node의 자동 동작이 아니다.
