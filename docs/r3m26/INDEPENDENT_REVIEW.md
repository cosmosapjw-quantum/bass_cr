# R3M26 독립 검토

2026-09-24 UTC. 판정은 **`PROMOTE_SCOPED_MODEL_FOUNDATION_AND_PROSPECTIVE_ANALYZERS`**다. 검토한 이론·사전 판정 규칙·작은 분석기 범위에 미해결 Blocker/Major/Minor는 없다. 문서의 Minor 두 건은 작성자가 수정했고 실제 수정문을 다시 확인했다. **전체 production은 HOLD**, 실제 B3와 전역 시간오차 검증은 미실행이다.

## 독립성·검토 범위

검토자는 아래 세 분석기, 시험, 이론·정책 문서와 해당 검증 설계의 작성자가 아니다. 별도 검토 역할에서 원문 코드, 기존 입력, 시험을 읽고 직접 CPU 시험과 반례 계산을 실행했다. 같은 연구 맥락과 모델 계열을 공유하므로 blind review, 외부 peer review 또는 독립 장비 재현으로 부르지 않는다.

검토 범위는 `scripts/r3m26_{temporal,budget,foundation}.py`, 대응 시험3개, `MODEL_FOUNDATION_KO.md`, `NUMERICAL_STRATEGY_KO.md`, `SCIENTIFIC_CONTRACT.md`, `MODEL_CONTRACT.json`, 두 Codex handoff와 변경된 claim/method/roadmap 정책이다. 총17개 파일의 검토 시점 SHA-256은 [INDEPENDENT_REVIEW.json](../../results/R3M26/INDEPENDENT_REVIEW.json)에 있다. 기준 HEAD는 `90d6cbad25e4bc49e9563f8721fdc408761b31c7`다.

검토자가 작성한 `CROSS_THREAD_REVIEW_KO.md`, `PERFORMANCE_AND_CODE_REVIEW_KO.md`, `CROSS_THREAD_RECEIPT.json`은 독립 판정에서 제외한다. 최종 종합 보고서·배송·원격 backup 검증도 이 판정의 범위가 아니다. `cr_repro`와 R3M25 문서·결과의 tracked diff는 비어 있으며 numerical source digest는 `581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`다.

## 요구사항과 직접 근거

| 요구/위험 | 확인한 근거 | 판정 |
|---|---|---|
| 모형을 논문 재현과 구분하면서 목표를 보존 | 차원 있는 Hamiltonian→atomic units→ETF→Gram projector→all-bound/b 적분의 유도, original50/100/225keV/u 목표, n≤3 중간 범위 명시 | 해당 이론·정책 범위 PASS |
| scalar gauge·ETF 부호·비직교 확률 | scalar phase 유도 재검토, isolated moving1s 직접 미분6점, Gram/whitened QR와 basis change 시험 | 수식/작은 대수 검사 PASS |
| local reference를 global certificate로 부풀리지 않음 | CAP dissipativity/Duhamel의 가정, residual 부호·initial term·quadratic goal term, weighted norm의 역할, 현재 global NOT_EVALUATED | PASS |
| B3 뒤 기준을 고쳐 맞추지 않음 | code-pinned forecast payload, 실제 dt7172step, historical raw hashes, tampered self-hash 거절, config/initial/witness 검증 | prospective evaluator 범위 PASS |
| clean p=2가 아닌 mixed-order도 검증 가능 | held-out discrepancy와 four-model envelope, 같은 부호·수축·pair를 모두 검사; synthetic 높은p PASS 및 tiny pair/large remainder FAIL | empirical rule 구현 PASS |
| 정확도·관측량·오차 유형 보존 | typed model/energy/domain/units/reference, raw/local evidence 불승인, 누락→OPEN, h_dt 한 번, L1 합·각 allocation 동시 검사 | ledger 범위 PASS |
| 경계에서 오차가 float 반올림으로 사라지지 않음 | JSON Decimal→Fraction 경로, .00001000000000000000001이 .00001 한도를 초과함을 직접 확인 | PASS |
| 첫 실행 범위를 통제 | 두 handoff 모두 B3 한 번 뒤 결과/독립 검토/spatial 계약 반환, 후속 B–F는 별도 유한 실행 단위, 자동 B4/finerh/representation/GPU병렬 금지 | 구체적인 범위 모순 없음 |

모형 유도는 fixed-target prescribed-trajectory 근사를 정확한 양자3체 항등식으로 부르지 않는다. incoming scalar Coulomb phase와 finite-start tidal dynamics, finite sampled span과 continuum all-bound, CAP loss와 ionization, keV/u와 proton totalkeV를 구분한다. 이 구분을 없애는 정책 변경은 발견하지 못했다. 외부 문헌의 새 독립 전수 재검색은 이 검토에서 수행하지 않았으며, 위 유도와 코드 의미를 직접 검토했다.

## 실제 시험과 반례

다음 명령을 새로 실행하여 **45passed in2.64s**, exit0을 확인했다.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../test_deps:. python -m pytest \
  -p no:cacheprovider -q tests/test_r3m26_temporal.py \
  tests/test_r3m26_budget.py tests/test_r3m26_foundation.py
```

CPU 환경은 Python3.12.14/NumPy2.3.5/SciPy1.17.0이다. GPU 생산 환경 Python3.12.3/NumPy2.5.3/SciPy1.18.1/CuPy14.2.0에서 재실행했다고 주장하지 않는다. 최초 기본 명령은 `No module named pytest`로 exit1이었다. 기존 시험 의존성 경로를 명시해 해결했으며 패키지 설치나 scientific source 변경은 하지 않았다. 최초 실패와 명령을 JSON에 보존했다.

독립 반례·검산:

1. **finite-data inference의 한계:** `y(τ)=.008−.01τ²−20τ⁴`, τ=.05/.025/.0125/.00625에 대해 empirical gate는 PASS하고 U_time=2.74658203125e−6이다. 여기에 `1e−4×∏(τ²−τj²)/∏τj²`를 더하면 네 관측값은 정확히 같지만 τ=0 극한이1e−4 바뀌고 실제 fine error는1.00421142578e−4가 된다. 따라서 이 gate는 무제한 remainder의 엄밀상한이 될 수 없다. 코드의 `certified_error_bound=null`과 문서의 model-conditional 해석이 정확하다. 이것을 실제 충돌에서 그 반례 모형이 실현된다는 주장으로 사용하지 않는다.
2. **ETF sign:** 직접 유도한 translated1s의 시간 미분과 moving-one-center Hamiltonian 작용은6점에서 같은 값이었다. 공간 ETF 부호를 뒤집으면 검사한 점에서 최소1.90583637의 잔차가 발생했다. 실제 격자 이동원자 실행이나 collision 정확도 인증은 아니다.
3. **projector sufficient bound:** 별도 whitened-QR 구현으로128개 작은 복소 벡터 예를 검사했다. 실제 관측오차/`2sqrt(p)δ+δ²` 최대는0.71740062였다. 이 표본 검산은 문서의 대수 유도를 지지하며 roundoff-certified theorem을 새로 만든 것은 아니다.
4. **ledger 반례:** h_dt 삭제는 OPEN/합null, 정확한 decimal 한도 초과는 EXCEEDED였다. 가상 `CERTIFIED_BOUND` 선언의 합은 exact rational로 반환되지만 scope에 `EVIDENCE_NOT_REPROVED_BY_LEDGER`가 있고 production=false다. 실제 evidence refs·proof·roundoff 검토는 최종 독립 결과 검토자의 책임으로 남는다.

반례 계산의 첫 JSON 기록 시 NumPy Boolean 직렬화 오류가 있었다. 계산/검토 대상 코드는 바꾸지 않고 기록 값을 Python bool로 바꿔 재기록했다. 이 검토 instrumentation 실패도 JSON에 남겼다.

## 발견과 해결

| ID | 심각도 | 발견 | 해결 확인 |
|---|---|---|---|
| R26-IR-1 | Minor | 문서는 fit을 finest dt로 scale한다고 했으나 구현은 max(dt) 사용 | 작성자가 max(dt)로 정정; 재열람 확인 |
| R26-IR-2 | Minor | zero/small channel에 absolute criterion이 등록된 듯한 문구; 실제 이번 B family에는 없음 | zero 입력 거절, unresolved 차분 OPEN, 별도 absolute 기준 미등록으로 정정; 재열람 확인 |

수정은 설명을 실제 API/정책에 맞춘 것이므로 numerical source나 frozen forecast 변경을 요구하지 않는다. 이 수정 뒤 같은 numerical tests를 불필요하게 반복하지 않았다.

## 판정의 범위와 다음 실행

Specification/engineering 두 축 모두 위 검토 범위에서 PASS다. 범위 한정 PROMOTE 대상은 **모델의 이론 연결, prospective B3 평가 정책과 구현, typed error ledger, synthetic algebra 검사**다. 안전계수2의 경험적 유효성은 실제 B3로 아직 점검되지 않았다. B3 결과·준비 receipt·endpoint/manifest 연결·runtime 환경을 별도로 감사해야 하며 이 작은 분석기만으로 GPU 계산 provenance가 자동 증명되지는 않는다.

새 full collision0, GPU 실행0, production array readback0, restore0이다. 전역 시간·공간·준비/경계·all-bound·b적분과 실제 물리 검증은 미해결이다. 다음 canonical node는 `N1_TDL_PRODUCTION_H_B3_FULL_COLLISION_CONTRACT_AND_TIME_REFINEMENT` 한 개다. 새 계약과 조정기를 검증한 뒤 기존 frozen scientific path로 B3를 실행하고 사전 등록 판정을 적용한다. 이 PROMOTE는 B3 PASS나 전체 production 승인을 뜻하지 않는다.
