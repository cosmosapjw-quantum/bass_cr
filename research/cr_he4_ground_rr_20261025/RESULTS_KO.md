# He4 ground RR 소비자 — scoped 계산 결과

선택한 `He4+(1s)+e -> He4(1s2 singlet)+photon` spontaneous 성분을
저장된 H1 RR 사슬에 결합했다. 8개 case의 192개 새 RHS, 24개 source row와
216개 grid/domain 비교를 계산했고, 별도 검토자의 Decimal70 48 RHS와
72개 미시 계수 비교가 원 기준을 통과했다. 채택 상태는
`NUMERICALLY_CHECKED_SCOPED_CONDITIONAL_HE4_SMOOTH_GROUND_RR_ON_SAVED_H1_CHAIN`다.

## 고정 조건과 실제 수치

T=10000 K, thermal ne=0.14 cm⁻³, capturing ground HeII density=0.02 cm⁻³,
native fitted binding24.59 eV, electronic d=4, stationary heavy target/zero recoil다.
Source는 원 C23D의 세 redshift `2.316,2.479,2.649`와 저장된 impulsive
population을 썼다. 기존 H1 RR는 shared new operator에서 계속 경쟁한다.

아래 범위는 `R80,N2048`, chi1.5/3의 여섯 finest source row다.

| 양 | 최솟값–최댓값 | 의미 |
|---|---:|---|
| He RR probability / active initial electron | 3.28466398e-10–3.90541038e-10 | q 위의 초기 active electron 기준 |
| He RR probability / selected initial electron | 1.38381604e-10–2.50385331e-10 | 처음 inactive였던 성분도 분모에 포함 |
| Conditional captured kinetic energy | 4.22096689–5.44279938 eV | capture가 발생한 사건의 조건부 평균 |
| Conditional emitted photon energy | 28.8109669–30.0327994 eV | kinetic + native24.59 eV |
| Conditional capture time | 341040.80–352078.81 proper s | frozen-background first-event moment |
| Mean stop-time change | −0.12037728–−0.10248204 ms | saved H1 baseline에 대한 paired response |
| CE probability change / active electron | −1.86895975e-14–−1.21831196e-14 | 새 He 경쟁으로 감소 |
| H1 RR probability change / active electron | −6.89384019e-19–−4.79181652e-19 | 같은 shared operator의 경쟁 효과 |

원 source field와 weights를 다시 만들지 않았다. H1/He capture probability를
독립 계산 후 합산하는 방식도 사용하지 않았다. 새 probability, kinetic 및
conditional-time RHS를 하나의 변경된 연산자로 풀었다.

## 실제 검증

| 검사 | 실제 결과 | 고정 기준 |
|---|---:|---:|
| 변경 계약 control | 31/31 PASS | source/domain/density/weight/stoichiometry/energy/SI 및 analytic 경쟁 검사 |
| Primary per-RHS backward residual 최대 | 7.77806859e-13 | 2e-12 |
| Primary probability partition maxabs | 9.55053814e-11 | 2e-8 |
| Primary scaled energy residual 최대 | 4.32832129e-11 | 2e-8 |
| He RR 자체 energy-scale residual 최대 | 6.67064048e-17 | 5e-13 |
| Grid 비교 상대차 최대 | 1.14389357e-4 | 일반0.005, paired0.01 |
| Upper-domain 비교 상대차 최대 | 7.38237247e-11 | 1e-5 |
| Independent Decimal70 RHS own-norm 상대차 최대 | 4.24321624e-11 | 5e-10 |
| 독립 미시 계수 상대차 최대 | 1.18719841e-15 | 5e-13 |
| Primary와 의도된 새 대각의 backward residual 최대 | 5.58163581e-13 | 2e-12 |
| 독립 source observable 상대차 최대 | 2.08644090e-11 | 5e-10 |

독립 검토자는 production module을 import하지 않았다. 두 R80,N2048 case에서
각24개 RHS, 총48개를 Decimal70으로 계산했다. 대각은 저장 PR105 binary64
값을 정확히 Decimal로 올린 뒤 new He hazard를 더했다. 이 때문에 새 대각의
반올림 값을 다시 정밀하게 푼 자기 비교가 아니다.

일부 grid node에서는 He hazard가 큰 대각에 더해질 때 binary64에서 전부
손실된다. 최대 국소 addition loss / lambda_He는1.0이다. 해당 진단은
`chi*.json`과 C9 결과에 보존했고, 각 observable/RHS의 상대오차는 의도된
실수 합 기준 독립 검토로 따로 확인했다. unit-scale absolute tolerance로
희귀 확률이나 tiny paired response를 숨기지 않았다.

## 소스 자격과 남은 물리 의무

HeI 공급자는 REI151/C23B에서 채택한 Verner96 smooth ground-channel 모형이다.
Fitted threshold와 source domain을 원본대로 사용했고, 원 전자질량 convention을
보존했다. Elemental He 자료의 He4 적용과 exact residual-ion-state resolution은
명시된 조건부 가정이다. HeIII capture, stimulated/all-level RR, angular emission,
finite-mass target averaging/recoil과 post-capture radiation feedback은 별도
공급자·consumer 의무로 남는다. Native source 상한은 물리적 정확도 인증의
상한과 동일하지 않다.

He event의 retained photon reward는 `r+24.59*p`, atomic internal reward는
`−24.59*p`다. H1에는 별도의13.60 eV를 사용했다. 두 reward의 합은 제거한
electron kinetic energy와 같으며, electron-removal diagnostic을 추가 deposit으로
계상하지 않았다. Thermal energy, particle number, binding energy와 radiation을
구분했으며, caloric partition이나 first entry를 irreversible heating 완료로
승격하지 않았다.

따라서 N4/N5는 `PARTIAL_OPEN`, N6/N7은 `PREDECESSOR_GATED`를 유지한다.
`global_error_bound`와 `global_completion_percent`는 null이다.

## 실행·자원·실패 보존

H1 canonical의164개 manifest payload를 직접 검증하고21개 새 입력을
정확히 복사했다. 새 primary192 RHS, independent48 RHS 및 control의
synthetic4 RHS 외에 old primary, old generator, old source projection,
source/thermal quadrature, ODE 재실행은0이다. Plot은 저장된 finest6개 row만
읽었다.

첫 controls_v1은 worker 시작 전에 memory admission이 거부됐다. 과학 계산은0,
worker CPU0이며 refusal receipt를 보존했다. 측정상 memory.current는 file
cache가 지배하고 anonymous usage는 약162 MiB였다. 루트 승인 후 clean active
cache의50%를 추가로 고려하되 dirty/writeback/shmem/unevictable을 한 번 제외하고
1 GiB reserve와512 MiB worker 제한을 유지했다. 별도 controls_v2가31개 검사를
통과했다. 전역 cache 삭제나 다른 process 종료는 수행하지 않았다.

새 worker CPU 합은4.189415 s, coordinator 합은0.018524602 s,
새 단위 charge는4.207939602 s다. 한도30 CPU s에 대해 남은 것은 이 단위의
25.792060398 s이며, 과거 budget의 미사용량을 가져오지 않았다. 기계적 원본 복구
CPU0.039411097 s는 별도다. 과거 H1 known lineage39.097868524 s와
C23E 별도15.493261114 s는 원 scope 그대로 보존하고 중복 증명 없이 합산하지 않았다.

원 실행 영수증, 원 코드 snapshot, 입력 해시, 비교와 실패는 `runs/`, `review/`,
`evidence/`에 있다. 게시·백업 상태와 전체 DAG 반영은 루트 delivery 기록의
실제 commit/provider ACK를 따른다.
