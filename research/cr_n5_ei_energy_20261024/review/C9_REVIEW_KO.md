# 독립 C9 검토 — 선택 EI Maxwellian 에너지 교환

## 판정과 권위

**PASS_SCOPED, blocking finding 0.** 독립 검토자는 생산 구현·생산 실행에 참여하지 않았고 생산 모듈을 import하지 않았다. Frozen `PREPARED_V4` source digest `ea17062954ac8fba8e9b00c1a2d59e28c2793ed596b9f364beef05f068e39476`의 실제 실행 결과를 읽어 검토했다. 최종 과학 admission은 root의 별도 결정이다.

검토 대상은 `CR_N5_EI_MAXWELLIAN_ENERGY_EXCHANGE` / `N5_C23D_H1_HE4_EI_ENERGY_V1`이다. T=10000 K, thermal ne=0.14 cm⁻³, prescribed lnΛ=20, H1+/He4+/He4++의 같은 온도 Maxwell bath와 저장된 유한 체인에 한정한다. 전체 N5는 PARTIAL/OPEN이며 N6/N7을 활성화하지 않는다. [`C9_REVIEW.json`](C9_REVIEW.json), [실제 raw 결과](independent_c9_20261024_v1/run_attempt3/RESULT.json)가 이 검토의 상세 권위다.

## 실제 독립 계산

저장된 곡선의 7개 에너지 × EE와 3개 이온, 원래 source 3개 × 입자 인덱스 0/191/383 × 이온 3개를 선택하여 총 **55 coefficient pairs**를 80자리 mpmath lower incomplete gamma로 비교했다. 입력 binary64 값을 그대로 고정했으며, 이는 물리 상수의 80자리 정확도 주장이 아니다.

R80·N2048의 χ=1.5와 χ=3, 각각 2480 full nodes에서 저장된 binary64 K와 RHS를 `Decimal.from_float`로 받아 80자리 Thomas 소거로 풀었다. case당 확률 3개, CE incoming energy 1개, bath reward 4개와 `K⁻¹|bath RHS|` 4개를 계산하여 **총 24 RHS**이다. 절댓값 reward는 부호 상쇄가 있는 비교의 분모를 제공한다. 생산 SciPy 풀이, 생산 generator 또는 옛 primary를 재실행하지 않았다.

| 검토량 | 실제 최대 오차/잔차 | 동결 허용값 |
|---|---:|---:|
| 계수 55쌍, signed μ는 비상쇄 분모 | 3.329476627936e-15 | 5e-10 |
| finest 행렬의 독립 reward/확률 비교 | 2.983316599389e-11 | 5e-10 |
| 원시 edge drift의 비상쇄 비교 | 1.846183175646e-16 | 2e-13 |
| 원시 K 및 총 generator 조립 | 3.512525762141e-16 | 2e-13 |
| 원시 state energy ledger | 2.168468782792e-11 | 2e-8 |
| 80자리 reference state energy ledger | 1.035272674590e-11 | 2e-8 |
| source 6개 reward/ledger 비교 | 1.078774935467e-11 | 5e-10 |
| source 6개 energy ledger | 2.672833341938e-13 | 2e-8 |

총 **39 검토 그룹 PASS**다. 80자리 전체 state reference CSV 2개, 계수 reference, source ledger, 실행 source snapshot 및 실제 자원 receipt를 모두 남겼다. 저장된 생산 controls 25/25, 8행렬/96 RHS/24 source rows, finite comparison 18개가 PASS임을 읽었다. 이 읽기는 생산 계산의 재실행이 아니다.

## 물리·보존·의미 검토

선택 이온의 정확한 선언 decimal 전하는 0.1+0.02+2×0.01=0.14로 닫힌다. 이 elastic EI 연산자는 전하·핵종의 화학양론 변화가 없다. 질량비를 species마다 유지했고 He4+ inertia의 alpha+bound-electron 근사 및 binding mass defect 생략은 기존 조건대로 남는다. 다른 동위원소 밀도, finite elastic event count/hazard는 null이다.

계수는 signed drift와 diffusion을 구분하며, `D=θ b A/r`, `μ=b(A′−A/r)`와 같은 온도의 Maxwell 평형 관계에 부합한다. 이론 R6의 Ito 에너지 변환과 transverse covariance 항을 확인했다. 독립 raw 검토는 저장된 conductance/π, 전체 에너지 증가량과 q 경계 전이를 이용하여 각 bath의 반대 부호 에너지 reward, 총 Q, 전치된 backward K 및 RHS가 맞물리는지 확인했다.

원래 active source 분모와 q에 projection된 질량, 원래 inactive 입자의 자기 에너지를 유지한다. CE terminal incoming energy를 post-kinetic과 internal energy로 나누어 장부에 각각 보존한다. Internal energy를 최종 gas heat로 바꾸지 않는다. 10000 proper s exposure는 initial impulse 정의에 한 번 사용하며 continuous chemistry 적분이나 추가 heat duration으로 취급하지 않는다. First entry는 irreversible assimilation 또는 Maxwellization이 아니다.

실제 PNG를 `view_image`로 열어 signed drift의 부호, 같은 에너지의 EI/EE diffusion, selected electron당 first-stop ion heat, CE 확률 변화와 no-CE first-entry 시간 변화의 서로 다른 축을 확인했다. [실제 그림 검토 기록](independent_c9_20261024_v1/PLOT_REVIEW.json)의 SHA256은 `2b81e02b297c5b4ad6e69a3b35d7de7865248ad5206374151f31974cee4a1b0a`이다. 그림은 이 범위를 넘어선 완료를 주장하지 않는다.

## source/input 고정과 실행 시도

생산 source 5개, prepared input/manifest 24개(입력 manifest의 23개 payload와 manifest 자체)를 확인하여 **29 pins PASS**, controls/primary/plot의 실제 source snapshot **21 pins PASS**를 얻었다.

| 시도 | 실제 결과 | numerical work | worker CPU s | coordinator CPU s |
|---|---|---:|---:|---:|
| attempt1 | stale plot lease로 child 시작 전 거부 | 0 | 0.000000000 | 0.001035630 |
| attempt2 | mpmath 없는 런타임에서 startup 실패 | 0 | 0.030482000 | 0.003602426 |
| attempt3 | 독립 raw 검토 PASS | 55쌍/24 RHS | 1.124207000 | 0.004952765 |
| 누적 | 실패 포함, 예산 초기화 없음 | 위 1회 | 1.154689000 | 0.009590821 |

누적 attempt wall은 **1.207775320s**, 따로 계측한 syntax/dependency 준비 CPU는 **0.032655035s**다. wheel 검증 비용은 이 준비 합계에 한 번만 포함한다. 성공 worker는 CPU1/native thread1, 주소공간 512MiB 제한, peak RSS 55264KiB였다. Coordinator는 CPU8이다. Attempt3는 이전 비용을 차감한 뒤 CPU hard limit 9s, wall 39.963137803s로 실행했다. 전체 review 허용값 10 CPU s / 40 wall s를 넘지 않았다. 계측되지 않은 기타 기계적 읽기·쓰기 비용과 전역 spend는 null이며 0으로 대체하지 않는다.

Attempt1의 lease는 생산 owner가 실제 완료 PASS/exit0, 현재 matching child 0, exact bytes/inode/stat를 확인하여 조정했으며 [별도 receipt](../delivery/STALE_PLOT_LEASE_RECONCILIATION.json)를 보존했다. 남은 lease의 원인은 UNOBSERVED이다. 검토자는 생산 lease/source/input/result를 수정하지 않았다.

Attempt2 뒤 기존 HE owner 작업의 pure-Python **mpmath 1.3.0 wheel**을 읽기 확인하여 create-only 복사했다. 원본은 `/workspace/scratch/4c25ee00380c/tdcs413_recovery/B1_RESTORED/dependencies/mpmath-1.3.0-py3-none-any.whl`이며, 536198 bytes, SHA256 `a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c`다. ZIP CRC와 RECORD 91 payload가 PASS이며 BSD license/원문 metadata를 복사해 보존했다. 설치 없이 PYTHONPATH zipimport로 동일 oracle을 실행했다. 이는 runtime dependency 재사용이며 scientific provider admission이 아니다. Oracle SHA256 `29e5f3f889877b29a7d637457b8095f3bf7fe2863e62ddd6de6ff8062d4ff422`와 수학·허용값은 모든 시도에서 그대로다. 요청 모델과 관측 런타임 모델은 별도로 기록하며, 관측 모델은 UNOBSERVED다.

## admission 경계와 다음 노드

이 검토는 저장된 유한 체인과 선택된 같은 온도 EI 모델의 numerical agreement 및 energy bookkeeping을 지지한다. Continuum/global error certification, 전체 atomic/isotope coverage, finite-bath thermal evolution, empirical unknown species/rate, 전체 thermal/UV/stars/nuclear network 완료를 지지하지 않는다. Missing channel과 dominant omitted process ranking은 기존 null/OPEN 범위를 유지한다.

`global_error_bound=null`, `global_completion_percent=null`. Non-tilted LRS/full Frobenius와 signed amplitude·norm·cancellation 구분, atomic isotropic closure와 nonbaryonic Vlasov stress 구분을 유지한다. 활성 WU/HE owner의 다른 provider를 구현하거나 완료 provider로 승격하지 않았다. N5 PARTIAL/OPEN 이후 N6 conservative coupling 및 N7 new parcel은 별도 선행 gate 뒤에 남는다.

**EXECUTION:** 독립 C9 PASS_SCOPED. **PUBLICATION:** root 소유의 게시 단계 대기. **BACKUP:** root 소유의 canonical/raw 백업 단계 대기. **DAG:** N5 PARTIAL/OPEN; N6/N7 NOT_ACTIVATED. 이 문서의 백업 대기는 작성 시점 상태이며 이후 terminal authority를 덮어쓰지 않는다.
