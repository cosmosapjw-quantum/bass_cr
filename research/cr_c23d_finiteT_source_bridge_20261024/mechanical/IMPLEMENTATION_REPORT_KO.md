# C23D 구현·새 실행 인계

## 현재 결과

고정 C23B source를 기존 Maxwellian EE provider에 결속한 adapter와 runner를 구현했다. 주 실행은 frozen numerical checks를 통과했으며 독립 C9/과학 판정은 root/reviewer 소유다. Named candidate는 C23D_FROZEN_MAXWELL_EE_LOW10_V1. Full stopping은 PARTIAL/OPEN이며 atomic coverage/N6 coupled evolution과 별도다.

기존 provider는 수정하지 않고 import했다. 3984 bytes, SHA256 `0fae93ddfd555e1d135606eab51cfe010911c7624f661d27317024cf3f54ba86`; C23B CSV는1681578 bytes, SHA256 `f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3`. 기존 source quadrature,18-case binding,KC/2048 Landau suite 재실행은0이다. 새 계산은 저장source의 희박pulse·EE계수·MFPT·선형population evolution이다.

## Source와 applicability

노출10000s, 열bath10000K, n_e,thermal=0.14cm^-3, explicit five-label density를 사용했다. 모든 parent depletion은10eV선택 이전 전체atom으로 계산했다. 계산된 source분율과 pulse비는 다음과 같다.

| z | selected atoms | source count fraction | source energy fraction | pulse/bath count | pulse/bath energy |
| --- | --- | --- | --- | --- | --- |
| 2.316 | 384 | 0.91314593 | 0.64456301 | 7.3489413e-08 | 1.5636125e-07 |
| 2.479 | 384 | 0.9146558 | 0.65086334 | 7.2516667e-08 | 1.5424168e-07 |
| 2.649 | 384 | 0.91654139 | 0.65896264 | 7.0716481e-08 | 1.5045276e-07 |

theta=0.8617333262145178eV, tau/s=1.352315003066568e-05, loss_anchor=2.3306698113647e-05eV/s. Count/energy 희박성 비는 모두1e-3 기준을 통과했다. 처방된 lnLambda20은 screening 자가일관 계산이 아니다. 전체/제외 source count·energy와 exact0/10eV endpoint, 각 parent depletion, 상대론·Debye·coupling·degeneracy 진단은 APPLICABILITY.json에 저장했다.

## First-entry와 evolution

MFPT는 초기W<=q의 time0을 포함한 first entry이며 영구 동화시간이 아니다. Reflecting upper40theta/80theta를 비교했다.

| z | chi | active mean seconds,40theta | all-selected mean seconds | active mean /1e10s | upper40→80 relative |
| --- | --- | --- | --- | --- | --- |
| 2.316 | 1.5 | 282051.683 | 180798.621 | 2.82051683e-05 | 1.197e-14 |
| 2.316 | 3.0 | 271510.074 | 113963.261 | 2.71510074e-05 | 1.8651e-14 |
| 2.479 | 1.5 | 281690.158 | 180654.227 | 2.81690158e-05 | 1.1985e-14 |
| 2.479 | 3.0 | 270615.538 | 113748.361 | 2.70615538e-05 | 1.8498e-14 |
| 2.649 | 1.5 | 281491.197 | 180671.513 | 2.81491197e-05 | 1.1993e-14 |
| 2.649 | 3.0 | 269776.031 | 113655.583 | 2.69776031e-05 | 1.8556e-14 |

새 주 evolution은 z2.479에서256/.005,512/.01,512/.005의3개 trajectory다. Spatial mean-energy 차이는0.00018700194 (기준5e-3), temporal 차이는0.00014715806 (기준3e-3)다. Projection/count/nonnegativity/entropy/opposite-energy/common-face ledger와9개입력guard가 통과했다. 저장된 H/count의 per-particle entropy는512/.005에서0.9022112523→0.001261573942로 감소했고 모든 저장시점 및 매step 최대증분의 rescaling은 양의증분0이다.

`new_ODE:0` 원 RESULT의 표현은 cosmological/thermochemical coupled ODE0으로 정확히 해석한다. 실제로는3개 신규 선형EE population ODE를 backward Euler로 진화했다. 원 RESULT를 덮어쓰지 않고 RESULT_CLARIFICATION.json을 추가했다. Worker가 root의3trajectory 의도 명확화 메시지를 받기 직전에256/.01 추가 trajectory 하나를 실행했다. 이 추가 observation은 계약상 불필요하고 admission basis에서 제외하며 실제시간을 비용에 포함했다. 추가/재실행은 중단했다.

Common face는 requestedchi에 가장 가까운 inter-centre q_h를 실제 보고한다. Tail ledger의 SAME edge current와 background+taggedcore reservoir를 background-only heat=-E dot rhs와 구분한다. Finite-band midpoint equilibrium을 사용하며 source core를 Maxwellian으로 치환하지 않는다.

## 실제 실행·수정 범위

- 주명령: `python cr_stopping_loop_20261024/implementation/dispatch.py`, 종료0.
- 주run: `runs/c23d_source_ee_20261023T220714Z_v1/`.
- 추가run: `runs/c23d_source_ee_supplement_20261023T220810Z_v1/`, 종료0, admission basis 제외.
- 주worker wall1.287974s,CPU1.280775s,RSS93912KiB. 실제두run workerCPU합1.343299s,workerwall합1.351788s,dispatchwall합3.212100s. CPU index와 CPU seconds는 별개다.
- CPU0worker/CPU8coordinator/native1, CPU55호스트부재·untouched. 각 dispatch직전 affinity/quota/memory 및 task process를 /proc로 확인하고 exclusive local lease를 획득·반환했다. 외부runtime/NCP lease UNOBSERVED.
- 원실행3개script는 implementation/history/primary_20261023T220714Z/에 exactSHA snapshot으로 보존했다.
- 승인된 deliveryrepair는 현재 adapter/runner의 `--provider`, `--source-csv`, `--inputs`와 repo-relative path resolution이다. 원provider/numerical method와 원run결과는 변경하지 않았다. relocated import/inputresolve/guard smoke와 runner --help만 검사했으며 science evolution을 재실행하지 않았다.
- 현재delivery hashes는 mechanical/DELIVERY_SOURCE_IDENTITIES.json, relocation 결과는 mechanical/RELOCATION_SMOKE.json.
- 그림은 saved output만 이용한 figures/C23D_SOURCE_EE.png 및.pdf이며 렌더를 시각 확인했다.

## 상태와 다음 단계

EXECUTION: 주 frozen checks PASS, 독립review 대기; 실제불필요supplement는 별도보존. PUBLICATION: NOT_ATTEMPTED. BACKUP: NOT_ATTEMPTED. DAG: C23D scoped numerical candidate; full CR_N4_STOPPING_KERNEL PARTIAL/OPEN. Requested model gpt-6.1-sol, observed UNOBSERVED. inherited total spend/remaining/currency=null.

Root의 독립80-digit anchor/source-weighted 확인과 C9가 다음 gate다. physical heating/full stopping/global error는 null; closed-box prescribedbath EE채널 범위만 계산했다.

## 최종 portable-delivery 보완

현재 dispatch는 Git이 빈 directory를 보존하지 않는 점에 맞춰 runtime/runs 부모만 먼저 생성한다. Unique output child와 lease는 계속 create-only다. `python implementation/fresh_parent_smoke.py`는 빈 부모에서 print-only stub을 실행해 directory/lease/exit0만 검증했고 과학 evolution은 하지 않았다. 결과는 mechanical/FRESH_PARENT_SMOKE.json이다. 현재 미래 RESULT producer는 new_linear_EE_population_ODE_trajectories=3, new_coupled_cosmological_ODE=0을 사용한다. 과거 rawRESULT/실행snapshot은 바꾸지 않았다.

독립 reviewer의 새80자리 reference는56 comparisons, 최대상대차1.7389e-15, frozen reference criterion2e-12로 PASS를 반환했다. 전체 C9 판정과 repairedF1 종료는 reviewer/root 기록을 따른다.
