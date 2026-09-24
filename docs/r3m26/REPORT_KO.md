# R3M26 — 모형 정초와 production 수렴 전략

2026-09-24. **이론 정초·새 수렴 기준·판정 코드의 범위 한정 완료. 전체 production은 HOLD.** 실제 B3/full collision, GPU 작업, preparation, finer h, representation 변경은 이번 작업에서 모두0회다. 현재 데이터를 새 기준으로 소급 PASS 처리하지 않았다.

## 무엇을 바꾸었나

사용자 지시에 따라 production의 중심을 **명시한 원자 모형의 내적 일관성과 그 모형을 정확하게 계산하는 수치 구현**으로 확정했다. 저자 raw data, digitized figure, private source exact match는 필수 gate에서 제외한다. 외부 실험/독립 이론은 유용한 현실 검증이며 알려진 모순을 무시할 수는 없지만, 자료를 더 구해야만 자체 모형을 정의할 수 있는 구조는 끝낸다.

엄밀한 전역 proof certificate와 검증된 보수적 수치 추정을 구별했다. 후자도 사전 등록·새 refinement 예측 확인·모형 민감도·교차효과 증거를 갖추면 model-conditional numerical budget을 닫을 수 있다. 엄밀상한 또는 confidence interval이라고 표기하지 않는다. 기존 **시간.10%, 공간.30%, 전체1%와 나머지 배분은 그대로**다. 원래 목표인50/100/225keV/u all-bound capture 단면적도 유지한다.

[모형 정초](MODEL_FOUNDATION_KO.md), [문제 분류](ISSUE_CLASSIFICATION_KO.md), [수치 전략](NUMERICAL_STRATEGY_KO.md), [모형 계약](MODEL_CONTRACT.json)에 가정→식→코드→검증 의미를 연결했다. `docs/CLAIM_POLICY.md`, method lock, `docs/roadmap/{DAG,ERROR_BUDGET,RESEARCH_PLAN_KO}`도 수정했다. 특히 R3M19에서 멈춰 있던 DAG frontier를 R3M25 local PASS와 현재 단일 B3 node로 갱신했다.

## 원자료 정밀 검토

입력 exact commit은 `90d6cbad25e4bc49e9563f8721fdc408761b31c7`, tree `06021e67906649febec079668b6bbc977a2150b1`다. 첨부9개 모두 해당 repository 파일과 byte-identical이며 RESULT/PREFLIGHT/WARMUP→MANIFEST→COMPLETED와 계약/RUN 봉인을 대조했다. `results/R3M26/INPUT_VALIDATION.json`에 identity를 기록했다. endpoint 배열의 독립 재계산이나 GPU replay는 하지 않았다.

R3M25의 actual t=0 국소 차수4.2020206/4.0458397과 changed-work substep 반복차1.6629e−15를 재계산했다. 국소 GO를 재사용한다. 2523matvec/5046FFTs/585.053s와 sampled minimum GPU free2.9419GiB는 원 실행 기록이며 여기서 새로 측정한 값이 아니다. 최초1matvec 뒤 VRAM 중단 기록도 보존했다.

## 원인 분리

| 층 | 현재 판단 | 다음 해결 |
|---|---|---|
| 물리 | 직선 핵 궤적·단일 비상대론 전자 모형은 일관되게 정의 가능. 시간수렴 실패가 물리 모순이라는 증거 없음. 실제 실험에 대한 model discrepancy는 미정 | 가정·범위를 명시하고 현실 검증은 별도 표기 |
| 수학/관측량 | scalar nuclear gauge, Galilean ETF, weighted Gram projector, CAP contraction 관계를 직접 유도 | P1/P2/P3의 정확한 span 정의 유지, norm loss/finite complement와 혼용 금지 |
| 시간 수치 | B1→B2 P 변화.2566–.2787%로 여전히 예산 초과. p≈2.9는 혼합 오차항과도 양립 | frozen 예측에 대한 새 B3 held-out 검사와 잔여 envelope |
| 공간·경계·준비 | h gap/h_dt 결합이 크고 예산 미해결. byte identity는 continuum 초기상태 정확도의 증명이 아님 | 시간 종료 뒤 지배적인 공간/결합부터 해결, 준비·CAP/box/ti/tf 검증 |
| 완전성 | n≤3≠all-bound, b=2≠단면적 | n/tail과 b 적분·tail을 별도로 닫음 |
| 구현/자원 | 국소 첫 실패는 VRAM 문제. 현재 신규 코드에 decimal 경계 판정 결함을 발견해 수정 | exact identity, typed ledger, 실패 보존과 자원 사전 검증 |

핵간 +1/R 생략은 같은 b 전자 확률에 대한 scalar gauge이고, 누락된 incoming global phase도 확률 자체의 bug가 아니다. finite-start 이전의 tidal dynamics 누락은 실제 수치근사다. CAP는 numerical boundary이며 lost norm을 ionization이라고 부르지 않는다. E=100keV/u와 proton total100keV도 다른 convention이므로 비교 시 맞춘다. 이 구분은 [SC-CCC 원전 §II](https://link.aps.org/accepted/10.1103/PhysRevA.93.022710), [BDSCx 원전 §2](https://arxiv.org/pdf/1201.4778), [CAP 원전](https://arxiv.org/pdf/quant-ph/0508084), [NIST 상수](https://physics.nist.gov/cuu/Constants/Table/allascii.txt)와 실제 코드를 대조했다. 각 식의 적용 한계는 정초 문서에 있다.

## 새 코드와 실제 검증

1. `scripts/r3m26_temporal.py`: raw B0/B1/B2·v2 witness·exact config/source/initial을 고정하고 B3의 사전 예측,4점 외삽,LOO,held-out residual을 평가한다.20tests.
2. `scripts/r3m26_budget.py`: 관측량/에너지/b 또는 적분/단위를 구분하며 .70% finite-span single-b, .85% all-bound single-b,1% all-bound cross-section profile을 검증한다. h_dt를 정확히 한 번 계상하고 unknown은 null로 남긴다.16tests. JSON decimal lexeme가 float 반올림으로 한계 초과를 놓치는 반례를 수정했다.
3. `scripts/r3m26_foundation.py`: 비정규 소산2×2계의 Duhamel·adjoint identity, weighted Gram 대 QR, 비직교 raw-overlap 중복과 잘못된 contraction 가정을 검산한다.9tests. identity residual≤약5.6e−17, projector 차이약6.8e−16이며 모두 작은 합성계 결과다.

신규45tests가 통과했다. 현재 `tests/` 전체는 **478passed,3GPU/CuPy skipped,0failed(201.89s)**다. 실행 환경은 CPU Python3.12.14/NumPy2.3.5/SciPy1.17.0이며 사용자 GPU 환경의 재실행이 아니다. 최종 exit와 최초 collection failure는 `results/R3M26/validation/VALIDATION.json`에 기록한다. 현재 실제 P3 ledger는 `NUMERICAL_BUDGET_OPEN`, 총오차·certified bound는 null이다. Synthetic PASS는 `SYNTHETIC_NOT_REAL` 또는 해당 synthetic scope로 별도 표시했다. `cr_repro/*.py`와 과거 결과 bytes는 수정하지 않았다.

## B3 사전 기준과 종료 경로

frozen artifact는 `results/R3M26/temporal/B3_FROZEN_FORECAST.json`이며 SHA `5eb9920d10ed467df7bc512cbbf983ee1ce95d2df94a15d21aa8e6940ebf743e`다. B3는 같은 h=.20 family, requested dt=.00625,actual dt=.00624946176119497,7172steps/57chunks다. 현재 **NOT_RUN**이다.

세 frozen 예측은 과거 single-power,dt²+dt⁴,leading-p2이며 정답이 아니다. 실제 B3 후 네 P∞ 모델과 비교한다.

`E_model=max_M |P∞_M−B3|`, `D_hold=max_F |B3−forecast_F|`, `U_time=2 max(E_model,D_hold)`.

P1/P2/P3 모두 동일 부호·fine contraction, pair≤.10%,U_time/|B3|≤.10%이면 fixed-h selected-span temporal estimate를 승인한다. p∈[1.5,2.5]와 LOO는 진단이며 단독 veto가 아니다. factor2는 설계 선택이지 theorem/확률이 아니다. 기존 R3M18 판정은 바꾸지 않는다. B3를 기존 even forecast와 같다고 가정한 가상 예는 pair약.0507–.0533%,U_time약.0338–.0355%여서 유한 종료 가능한 기준임을 보여준다. **이는 prediction이지 새 관측이 아니다.**

PASS 뒤에는 공간+h_dt→준비/경계→all-bound→b적분→에너지 확장 순으로 진행한다. 같은 국소 oracle를 반복하거나 전체 AOCC 구현을 새 필수 선행조건으로 추가하지 않는다. 현재 마지막 연구 루프의 이론 작업을 종료하고 실제 오차 차원을 닫는 구현·실험으로 전환한다.

## 실제 하드웨어와 다른 스레드 반영

Ryzen5900X12c/24t, 기록상 RAM94.19GiB(약96GiB급),RTX309024GB를 기준으로 계획했다. actual CPU workers4 microbenchmark는약2.09배지만 GPU buffer reuse는약1배다.63M 전체 collision 가속은 미측정이다. B3에는 frozen Strang과 precision을 유지하며 GPU 한 작업, bounded CPU/host staging, 최소2GiB GPU reserve와 durable checkpoint 순서를 적용한다. 측정 범위와 공식 CuPy14.2/SciPy1.18.1 코드 검토는 [성능 문서](PERFORMANCE_AND_CODE_REVIEW_KO.md)에 있다.

새 HH 모형 정초·독립 판정과 개선 보고서를 작은 백업 문서/receipt로 확인했다. 세 readable 원문의 SHA가 receipt와 일치했다. 들여온 것은 model definition/validation/product scope의 분리 원칙이다. HH 두전자 tail·수치·가속률을 CR에 가져오지 않았다. 기존 HOST/Atomic/C17의 새 변경은 제한된 검색에서 확인되지 않았으며 전체 계정에 없다는 뜻은 아니다. [교차 스레드 검토](CROSS_THREAD_REVIEW_KO.md)에 실제 열람 범위와 ID가 있다. 큰 archive readback/restore는 수행하지 않았다.

## 로컬 실행 프롬프트

- [저비용 Codex master prompt](LOW_COST_CODEX_MASTER_PROMPT_KO.md): B3부터 model-conditional production까지 단계별 코드 범위, 실험 계약, 계산 기준, 비용 제어, 상위 검토가 필요한 예외를 상세히 고정했다.
- [첫 B3 실행 handoff](LOCAL_CODEX_HANDOFF.md): exact inputs·forecast hash·B3 전용 coordinator·preparation binding·57chunks·분석 CLI·배송 절차다.

저비용 모델이 이론을 다시 선택하거나 tolerance를 임의로 조정하지 않도록 실행과 판단을 분리했다. 첫 실행 단위는 B3 한 건과 결과/다음 spatial 계약까지다. 이후 단계도 유한 계약으로 진행하며 무제한 자동 계산을 지시하지 않는다. 실제 결과가 미달하면 HOLD와 정확한 잔여 한계를 반환한다.

최종 독립 검토는 [INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md), 배송은 `DELIVERY_RECEIPT.json`, 최종 scope 판정은 `FINAL_DECISION.json`에 기록한다. main merge/force push는 하지 않는다.
