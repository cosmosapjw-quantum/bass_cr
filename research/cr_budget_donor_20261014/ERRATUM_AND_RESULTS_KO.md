# BASS_CR: stopping 노름 교정과 예산 기반 donor 활성화

연구 단위: `CR_BUDGET_DONOR_20261014`. Baseline: `15193ccf88207de3a5134a4dc56c72e8ed1c7262` (PR51). physmath-research-loop1.1.0을 실제 읽고 사용했다. 상태는 조건부 직접 유도·구현·포함구간 검증 완료이며 외부 독립 심사는 미수행이다.

## 중요 정오표

TIME_DONOR 보고서 식(14), NT3/NT4는 개별 active-bin 운동에너지, thermal energy, chemical increments를 분리한 벡터 Z의 l1 노름을 사용한다. Interior stopping의 사건 증분은 (-Ep,Ed,Ep-Ed)이며 그 l1 노름은 2Ep다. 이전에 사용한 2(Ep-Ed)는 이 좌표 노름과 다르다. Ep=10, Ed=9이면 직접합은20, 이전계수는2다.

따라서 원 NT4의 0.001465122 K 수치 인증과 그에 의존한 branch 인증을 현 증명의 유효한 결과로 사용하는 근거를 철회한다. 그 숫자가 우연히 실제 오차보다 큰지와, 제시된 증명의 유효성은 별개다. NT1의 노출량 해, NT2의 고정 기체 보존 전파자, NT5의 시간분할 참조, NT6의 공변 회계는 유지한다. 원본 불변 ZIP/실패 기록은 삭제하거나 소급 수정하지 않았다.

동일한 첫 반응 surrogate의 기존 공식을 2Ep로 교정하면 h=1e5 s에서 같은 branch 조건부 상계 값은 약0.946083 K이고 branch bootstrap은 닫히지 않는다. 새 결과에서는 후속 반응을 실제로 활성화하여 이를 해결한다.

## 새 정리와 구현

고정 부피·에너지/prefix23·HI/HeI 이온화·downward Coulomb stopping이라는 동일한 유한 비교 모형을 사용한다. 모든 에너지는 eV/cell, 시간은 proper seconds, 수는 cell count다. Density=N/V, signature=(-,+,+,+), c,k_B와 eV/J 변환을 유지한다.

기체 상태를 고정한 에너지 생성자는 Metzler이고 열 합이0이므로 시간의존 선형 전파자의 l1 노름은1이다. 선택 surrogate의 기원별 stopping chain에서 r번째 점유수는 a_r t^r/r!, a_r=A_root product(lambda_bar_0,...,lambda_bar_(r-1))로 제한된다. 최초 이온화 daughter는 원 mean spectrum과 초기 생성률로 제한한다.

교정된 사건 비용은 cI_j=2E_j sum(kappa_ja X_a0/V), cS_j=2E_j lambda_bar_j이며, 기체 feedback 상수는 Gamma_j=2E_j[sum(kappa_ja/(VB_a))+c_n lambda'_j(n0)/V], c_n=1/Emin이다. 보류된 ionization daughter 전체 반응, 활성 chain 내부의 생략 이온화, 말단 stopping을 모두 포함해 residual <= sum(C_r t^r/r!)를 계산한다.

L_D=sum(Gamma_j Nbar_j(h))를 쓰면 전체 비교 모형과 선택 surrogate의 에너지 오차는

B_D(h)=sum_r C_r h^(r+1) phi_(r+1)(L_D h),
phi_m(x)=sum_(k>=0) x^k/(k+m)!

로 제한된다. 65자리 outward Decimal 연산과 양의 급수/기하꼬리를 사용했다. 온도 상계는 [1/(cv Nmin)+Tmax c_n/Nmin] B_D이다. 각각의 추가 간선 후보는 잔차, 새 terminal population, L_D를 모두 재계산한다. 단순히 이전 비용을 빼거나 비선형 선택의 일반 단조성을 가정하지 않는다.

h=100000 s, 내부 방법 비교 예산0.001 K에서 깊이 (P,S)의 선택은
(1,1):0.975710394 K, (1,2):0.014102021 K, (2,2):0.001984981 K, (2,3):0.000005110127 K다. 첫 값은 동일한 다항식 비교 상계이며 위 saturated bound와 구별한다.

세 추가 간선은 grid4759->4758, grid288->287, grid287->286이다. 원 두 parent의 첫 간선과 이온화는 유지한다. 선택은 기원별 cohort에 적용하고 physical energy bins에는 합산한다. 원 이온화 daughter의 후속 반응과 두 말단 반응은 새 residual에 포함한다. 기존 4739개 rate table을 재사용했고 새 SDCS/전체 generator/NCP 계산은 없다.

선택된 surrogate의 온도 오차 상계는 5.110126551479616e-6 K다. 전체 경로의 cutoff는 [0.1716586467058447,0.1716862520272591] eV로 원 branch(0.17115625,0.17425)의 내부에 있다. 첫 이탈 시각 논증으로 branch 가정을 닫았다.

## 포함구간 reference와 실제 검산

초기 기체율의 작은5상태/4상태 chain을 양의 uniformization과 Poisson tail로 포함했다. 실제 선택 surrogate와 이 fixed-rate reference 사이의 rate 변화는 |delta n_e|<=a_n t, |delta X_a|<=r_a0 t로 제한한다. 보존 count 전파자와 열 합이 root energy인 양의 lift로 B_freeze<=sum(A_root E_root eta_root h^2)를 얻는다.

Reference 온도는99.6160968321333396849... K, 기체 고정의 온도 상계는4.26660975051e-8 K다. Donor omission과 reference 차이를 합한 상계는5.152792648985e-6 K이고, 전체 선택 유한 모형의 endpoint는 [99.61609167934069,99.61610198492599] K에 포함된다. SDCS·격자 모델·움직이는 기하의 물리적 불확실성은 이 상계와 별도다.

두 허용차의10변수 DOP853 검산은99.61609683213688 K로 일치했고 fixed-rate reference와 관측 차이는3.54e-12 K다. 이 관측값을 rigorous bound 대신 쓰지 않는다. 새로운 unit tests8개 및 postchecks16개가 통과했다. Wolfram scalar7묶음27개 영잔차 및 exact counterexample20 vs2, xAct tensor4개 영잔차를 얻었다. Limit 평가의 infinity 경고와 첫 NumPy bool 직렬화 실패를 보존했다. 외부 독립심사 결과를 주장하지 않는다.

## 전체 재현 자료와 백업

전체9쪽 PDF, 단일 LaTeX, 원고, 코드·테스트, exact inputs, rate NPZ, 실제 결과·실패, 정오표·DAG·harness 기록은 57-member archive에 있다. 글꼴 바이너리0개.

- 파일: `BASS_CR_BUDGET_DONOR_20261014_SOURCE.zip`
- Bytes:479993
- SHA256:`f743d601cf67603a2ddb7a3e46f50d7384898e6d269ea3b3ba58a3e2c693af2b`
- [Google Drive](https://drive.google.com/file/d/1OVv9HYbvpXBHXgD1K0SHcyS_Po9Da_p1/view?usp=drivesdk)
- Dropbox:`/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_BUDGET_DONOR_20261014_SOURCE.zip`, ID `id:BSpOijBcT10AAAAAAD4lMA`.

두 provider의 실제 성공 ACK, ID, 이름, 크기479993를 확인한 R1 검증이다. Drive parent도 지정 폴더와 일치했다. Remote redownload/restore 검증은 수행하지 않았다. Git에는 이 실질 유도/정오표/재현 진입점을 게시하며 전체 불변 실행 payload는 위 ZIP에 둔다.

## 다음

`NT_BUDGETED_DONOR_ACTIVATION`: 현재3간선/1e5s/고정모형 범위 완료. 다음은 `NT_GEOMETRY_TEMPORAL_BINDING`: 실제 changing parent energy/rate와 geometry work를 교정된 energy-coordinate budget에 결합하고 angular, donor, time-reference 오차를 분리한다. 이전 F/G/PHYS02/production/atomic/b-grid 및 전역REI 채택 상태는 유지한다. 이 결과를 사용하는 소비자는 먼저 `review/ERRATUM.json`을 읽는다.
