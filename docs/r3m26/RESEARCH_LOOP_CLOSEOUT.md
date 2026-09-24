# R3M26 GPT6용 연구·코딩 루프 실행 기록

## 적용한 하네스와 권한

사용자가 GPT6용 스킬/하네스와 theory-first final research loop를 지정했다. `physmath-research-loop`의 MODEL_ROUTER에 따라 연구 v4.0.0과 코딩 v4.0.0을 읽고 적용했다. 사용자 현재 방향은 모형 내적 일관성과 충실한 수치 구현이며 paper exact reproduction이 아니다. 하네스의 예시·이전 실행 상태는 새 증거로 가져오지 않았다. 현재 서비스의 내부 모델 식별자는 별도로 확인하지 않았으므로 실제 실행 모델을 추측해 기재하지 않는다.

| 입력 | 실제 identity | 사용 범위 |
|---|---|---|
| 연구 GPT6 v4 zip | `dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7` | START_HERE, PROJECT_INSTRUCTIONS, research state/evidence/decision 구조 |
| 코딩 GPT6 v4 zip | `dc99e7ab2f9629dcce3ec0758d97e19acc5b645f86e208d1b338bb6430ff8d7a` | START_HERE, AGENTS, scientific contract, 검증·독립 검토·scoped promote |
| R3M25 authority | `90d6cbad25e4bc49e9563f8721fdc408761b31c7` | 문서/봉인/작은 raw 결과 및 9개 첨부와 byte 대조 |
| frozen numerical source | `581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b` | 변경하지 않음 |

## 이론 루프: 질문→유도→반례→판정

| 질문/가설 | 실제 조사·계산 | 판정과 한계 |
|---|---|---|
| 시간수렴 실패가 물리 모형 모순인가 | 차원 있는 Hamiltonian, prescribed trajectory, au, scalar gauge, ETF, finite-span Q를 원전·코드에 연결 | 모델은 일관되게 정의 가능. 실제 p+H에 대한 model discrepancy는 미정. 기존 p≈2.9가 물리 반증은 아님 |
| 누락 +1/R 또는 incoming Coulomb phase가 capture bug인가 | scalar-gauge 관계와 far-field expansion 직접 유도 | 같은 b 전자 확률의 scalar phase는 소거. 누락된 finite-start tidal dynamics는 별도 수치근사 |
| 국소 CF4 PASS로 global time이 닫히는가 | uploaded seals, actual p 재계산; Duhamel/global residual과 projector bound 유도 | 국소 PASS 재사용 가능, global residual 적분/시간 예산은 미평가 |
| clean p2 밖이면 무한 refinement가 필요한가 | B0–B2 actual-dt power/even/p2 예측 비교, B3를 held-out으로 설계 | prospective mixed-order empirical route 도입. p screen 진단화; safety factor2는 설계값이며 theorem/확률 아님 |
| 엄밀상한만 production의 유일한 길인가 | model/code/solution/real-world validation 층 분리, typed estimate vs certificate | 사용자 정의에 따라 검증된 보수적 추정으로 조건부 수치 승인 가능. 기존 targets/old failures 보존 |
| all-bound를 유한 n으로 대체할 수 있는가 | exact spectral projector와 finite sampled span 구별 | 중간 finite-channel 제품 가능, 원 최종 all-bound/σ 목표는 유지 |
| 다른 스레드 결과를 수입할 수 있는가 | 새 HH 작은 보고서3+receipt/decision3+Dropbox1 읽음, 기존 관련 가족 변경 범위 검색 | 모델/검증/범위 분리 원칙만 반영. 외부 수치값·두전자 tail·가속률은 CR에 수입하지 않음 |

이론 정초를 먼저 완료한 뒤 아래 구현을 수행했다. 추후 임계값·모형 변경을 결과에 맞추는 사후 선택은 허용하지 않는다.

## 코딩 루프: 구현→실패 보존→검증

| 파일 | 과학적 의미 | 실제 검증 |
|---|---|---|
| `scripts/r3m26_temporal.py` | pinned B0/B1/B2와 exact-config/witness, frozen B3 forecasts, 실제 dt 4점/LOO/held-out 경험 추정 | 20 tests, true even/higher apparent p, held-out miss, sign/noncontraction, identity/tamper/undefined 반례 |
| `scripts/r3m26_budget.py` | typed product/observable units/domain, 검증된 추정과 certificate 구별, 누락 null, h_dt 1회/L1 | 16 tests, mismatched quantity/scope, missing components/coupling, decimal boundary 반례; current P3 OPEN |
| `scripts/r3m26_foundation.py` | dissipative nonnormal Duhamel/adjoint와 weighted Gram projector 유도 검산 | 9 tests, 독립 triangular exponential/QR와 비교, residual sign·stable-but-nondissipative·raw overlap 반례 |

소규모 합성 검산은 production error evidence가 아니다. full collision/GPU/preparation/finer h/representation 변경은 이번 단위에서 모두0이다. 실제 시험과 source identity는 `results/R3M26/validation/VALIDATION.json`에 최종 기록한다.

## 음성 결과와 수정

- temporal 최초 collection/import 실패 및 synthetic 계수 선택 실패는 원 로그에 보존했다. 실제 B3 데이터 실패가 아니다.
- budget fixture extraction의 test-path 오류 및 JSON decimal lexeme 반올림 결함을 보존하고 수정했다. 숫자를 Decimal로 파싱해 exact-rational 합산을 검사한다. flags/reference만으로 증거의 진실을 자동 증명하는 도구는 아니다.
- foundation 초기 pytest 미설치/NumPy bool JSON serialization 실패를 기록하고 수정했다. 안정 고유값만으로 contraction이 성립하지 않는 반례를 추가했다.
- root 무범위 pytest는 보관된 R3M10 source/tests까지 수집해5개 import mismatch로 중단했다. 과거 파일을 삭제/수정하지 않고 현재 `tests/`를 지정하여 다시 실행했다.
- 독립 검토의 문서 scale/zero 처리 minor 두 건을 구현과 일치시키도록 수정했다. 수치 임계값은 바꾸지 않았다.

## 종료와 재개

이번 종료 범위는 **모형 정초·prospective 수렴 전략·판정 도구**다. 독립 검토가 승인한 정확한 범위와 최종 finding은 `INDEPENDENT_REVIEW.md` 및 JSON에 있다. whole production은 HOLD이며 current numerical ledger도 OPEN이다. 새 인증 논문/solver를 더 만들어야만 진행할 수 있는 node를 추가하지 않았다.

다음 canonical node는 `N1_TDL_PRODUCTION_H_B3_FULL_COLLISION_CONTRACT_AND_TIME_REFINEMENT` 하나다. 로컬 저비용 모델은 `LOW_COST_CODEX_MASTER_PROMPT_KO.md`와 `LOCAL_CODEX_HANDOFF.md`의 계약·명령·실패 분기를 실행한다. 첫 단위는 B3 한 건과 판정, 이후 공간→준비/경계→all-bound→b적분→에너지별 release 순서다. scientific unknown을 조용히0/PASS로 바꾸지 않으며, 성공한 차원은 같은 이유로 다시 열지 않는다.
