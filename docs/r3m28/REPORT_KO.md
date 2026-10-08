# R3M28 — 동일 horizon A3 공간 pair 및 h–dt 관측

## 판정과 범위

`N1_TDL_PRODUCTION_H_SPATIAL_H_DT_BUDGET`의 사전 등록 0.30% **raw pair screen은 NO_GO**다. 100 keV/u, b=2, selected projectile hydrogen n≤3 spans에서 B3(h=.20)와 A3(h=.25)의 실제 dt=.00624946176119497, horizon=44.821139751290325 au 결과 차이가 P1–P3 모두 3%를 넘었다. 이는 이 두 격자 계산 사이의 관측 차이이며 B3의 continuum 공간오차에 대한 엄밀한 하한이나 검증된 전체 공간오차 추정치는 아니다. 고정 h=.20 selected spans의 R3M27 시간 추정 검증은 유지된다. Production `HOLD`, all-bound `OPEN`, b-grid `NO_GO`다.

| channel | A1 h=.25 dt≈.025 | B1 h=.20 dt≈.025 | A3 h=.25 dt≈.00625 | B3 h=.20 dt≈.00625 | `|B3−A3|/B3` | .30% screen |
|---|---:|---:|---:|---:|---:|---|
| P1 | .005873247874601518 | .006068282194867191 | .005888839447660162 | .006089329814044807 | 3.292486570890308% | FAIL |
| P2 | .007336491989743904 | .007562290857479282 | .007354202175313995 | .007586698170080142 | 3.064521476326126% | FAIL |
| P3 | .007825354867138081 | .008063449050040342 | .007844123441462061 | .008089219135272727 | 3.0299054792808814% | FAIL |

A1/B1 coarse gap과 A3/B3 fine gap을 각각 비교한 raw `h_dt = (B3−A3)−(B1−A1)`은 P1 `5.456046118971526e-6`, P2 `6.6971270307686695e-6`, P3 `7.001510908405395e-6`다. P3의 B3 대비 값은 약 0.08655%다. 이는 측정된 교호차이며 전체 상호작용 오차 추정치로 입장시키지 않았다. Ledger에서 h_dt는 별도 additive 항으로 한 번만 기재했으며 `RAW_INTERACTION_DIFFERENCE`, `UNADMITTED`이다.

## 계약, 실행, 증거

입력 branch `cr/r3m27-b3-full-collision-20260924` exact `1ff87bf27a18fd0acfe8cffe788ae07deac7650a`에서 전용 branch `cr/r3m28-spatial-hdt-budget-20260924`를 만들었다. Frozen `cr_repro` digest `581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`를 유지했다. [DESIGN](../../results/R3M28/DESIGN.json) SHA `eb8157a58cf9f5765af91af328c207f7921cc19cf3f16fc90067538e66372bc6`은 A3 관측 전 기준과 PASS interval을 고정했다. [CONTRACT](../../results/R3M28/CONTRACT.json) SHA `4a1c144b91472ad697e5258ddbd16d168fbe3821fa72ec6744a50d41b109c853`으로 source, config, 환경, 입력, 출력 root, 자원 한계, 57-generation 보존, 무재시도를 묶었다. 계약 source commit은 `bbcb31b2a4e50e397ac2e5b8cb9d029ef1f5111a`다.

정확한 A3 config preparation을 **한 번** 수행해 initial.npy SHA `08595a1a42900da0a86f0401d28e98f79c0663524a8222d3c51756223a13ee8e`가 historical A1 canonical initial과 일치했다. Collision 내부 witness preparation도 같은 array를 확인했다. 새 full collision은 **한 건**, nstep=7172, 128-step 56 chunk와 마지막 4-step chunk다. 57개 generation을 각 chunk 직후 원자적으로 게시하고 전부 보존했다. [전체 generation 감사](../../results/R3M28/FULL_GENERATION_AUDIT.json)는 29,417,479,296 state bytes의 SHA/manifest/receipt를 재검증했고 최종 state SHA `4c23a1b023eb0c41db9f2efb8aa79d36b53f177e987d023b895a7e412e0e7831`, raw result SHA `e03295595ca64e90bd4c8c78ac208f4c4e1de5c59a77db930fa2d3ef68339c14`를 확인했다. 자동 retry 0회, first runtime failure 0회다. Endpoint 배열을 별도 독립 구현으로 재계산했다고 주장하지 않는다.

[Runtime audit](../../results/R3M28/RUNTIME_AUDIT.json): 외부 preparation command 198.230 s, 내부 witness preparation을 포함한 첫 collision command 204.368 s(그 내부 준비/검증 경계 196.128 s), 전체 collision commands 923.179 s, snapshot commands 115.359 s, resource probe 4.830 s. 합산 command wall 1241.598 s이며 GPU 전파 단독 시간이 아니다. 최소 sampled GPU free 19,154,337,792 B, host available 79,712,722,944 B, disk free 521,287,614,464 B. GPU peak 사용량, D2H, Gram 각각의 독립 시간은 계측하지 않았다. Python 3.12.3/NumPy 2.5.3/SciPy 1.18.1/CuPy 14.2.0/CUDA 12090, RTX 3090 science 환경이었다.

## 검증, 실패 원문, ledger

R3M28 target tests 7 PASS, compileall 및 두 CLI PASS. 처음 science venv full-suite는 `486 passed, 5 failed`였는데 `threadpoolctl` 미설치와 subprocess `PYTHONPATH` 환경의 collection/import 문제가 원인이었다. 패키지 업그레이드나 기준 완화 없이 canonical system Python + 명시적 `PYTHONPATH=.`에서 `488 passed, 3 skipped`로 끝났다. 최초 raw logs는 `results/R3M28/validation/FULL.*`, 정상 재실행 로그는 `FULL_CANONICAL.*`에 보존했다. Budget ledger 최초 초안은 지원되지 않는 h_dt accounting 문자열 때문에 `ValueError: explicit h_dt accounting required`를 냈다. 원문/원인을 [실패 기록](../../results/R3M28/LEDGER_FIRST_FAILURE.txt)에 보존하고 enum만 `SEPARATE_ADDITIVE`로 고쳤다. 관측값과 기준은 바꾸지 않았다.

[공간 분석](../../results/R3M28/SPATIAL_EVALUATION.json)과 [P3 typed ledger](../../results/R3M28/CURRENT_SELECTED_P3_LEDGER.json)를 분리했다. [Budget evaluator](../../results/R3M28/CURRENT_SELECTED_P3_BUDGET_EVALUATION.json)는 `NUMERICAL_BUDGET_OPEN`: real-time만 해당 selected-spans fixed-h 범위에서 admitted이고 spatial/h_dt/preparation/box-CAP-finite-time은 아니다. 수치 total 1%, 시간 .10%, 공간 .30% 배분은 유지한다. 모델 discrepancy는 이 ledger 외부다. Full spatial envelope, projectile subcell translation, preparation, CAP/box/final time, all-bound completeness, b-grid, 50/225 keV/u는 여전히 미해결이다.

[독립 GPT-6 Astra/xhigh 검토](../../results/R3M28/INDEPENDENT_REVIEW.md)는 NO_GO 계산·입력 일치·57 generation·116 command receipt·자원 주장에 결론 변경 결함이 없다고 확인했다. 낮은 심각도의 provenance 지적 하나는 P3 ledger가 R3M27 roadmap SHA를 `current`라고 표기한 것이었다. 현재 R3M28 roadmap bytes SHA `c5eb44b6f98e0b68adc6ed2d0f596c31ea950ea5c66b2a68e4ce787d56dd9ea1`로 포인터를 고쳤고 budget evaluator 재실행 출력이 byte-identical임을 확인했다. 수치값과 gate는 그대로다.

## 다음 하나의 node

`N1_TDL_PRODUCTION_H_SPATIAL_DISCRETIZATION_DISCRIMINATOR`: 현재 3% raw gap의 원인을 point-Coulomb 격자 표현과 projectile subcell phase/공간 이산화 쪽에서 구분하는 사전 등록 소규모 진단을 설계한다. A3/B3를 반복하지 않고, 국소 독립 기준과 기존 checkpoint를 재사용해 한 가지 다음 spatial strategy의 판별력을 정한다. 이 pass에서 finer h, B4, 다른 representation, b-grid, physical rate, main merge는 실행하지 않았다.
