# bass_cr external-first 연구 전환 Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** CR-free rei_bianchi를 원자 K의 완성과 분리하여 즉시 진행하고, CR-on 및 자체 원자 확장을 같은 채널·단위 계약으로 재호출 가능하게 보존한다.

**Architecture:** Fastest `CR-F0`는 CR-off source 계약과 legacy 보존을 전달하여 닫는다. Conditional `CR-M1..M3`는 실제 CR-on 질문이 정해졌을 때 외부 자료와 reservoir/energy adapter를 연결한다. Legacy `CR-L1`은 현재 R4AP를 보존하며 어느 fastest task에도 의존성을 걸지 않는다.

**Tech Stack:** 본 packet Python 3 표준 라이브러리; 기존 atomic C++/GMP/Fortran 코드는 보존만 한다. Rust consumer는 rei_bianchi 소유다.

## Global Constraints

- 원자 연구계획을 별도 lane으로 보존하고 fastest와 중장기 track을 연결한다.
- 기존 G02 UNRESOLVED, production HOLD, capture false, all_bound OPEN, b_grid NO_GO를 변경하지 않는다.
- 기존 연구 branch에 create-only additive 게시, non-force push; main merge/기존 PR 자동 병합 없음.
- `docs/atomic_reionization_handoff_20261004_v1/threads/bass_cr/`를 packet 위치로 사용한다. 이하 `CR_PACKET`은 그 절대경로다.
- 실제 원문 및 source는 `REPO_SNAPSHOT.json`/`LEGACY_SOURCE_MANIFEST.json`에 고정했다. 새 paths는 '제안' 또는 '본 packet에 존재'로 구별한다.
- 문서 게시 승인으로 원자 native one-shot 계약을 재사용하지 않는다. 공통 fasttrack은 원자 실행을 요구하지 않는다.

---

## 경로·관측량 결정

원격에 존재: `research/convergence_20261004/r4ao_finite_cell/{NEXT_DAG.json,SCOPED_RESULT.json,source/pilot.py}`, `docs/roadmap/{DAG.json,RESEARCH_PLAN_KO.md}`, `research/convergence_design_20261002/CR_REION_1S_V1/{PLAN_KO.md,DAG.json}`. 마지막 두 역사 계획은 복사·보존했으며 실행 순서는 최신 R4AO NEXT_DAG가 우선한다.

본 packet에 존재: `reference/cr_contract.py`, `tests/test_cr_contract.py`, 아래 연구/실행 계약. CR-on 구현 제안: `research/external_atomic_provider_20261004/{manifest.json,provider.py,distribution.json,rate_reference.py,tests/}`. 해당 provider 경로는 아직 존재하지 않는다. 이것을 이미 완성된 물리 코드로 보고하지 않는다.

## Task CR-F0 — CR-off 응용 공급 종료 및 archive 보존

**Files:** 본 packet 전체, 실제 receiver interface binding은 rei_bianchi packet의 CR-off task.

**Interfaces:** consumes `enabled: bool`, produces zero-valued optional CR term. Contract는 off 상태에서 외부 source 로드/조회가 0회여야 한다. Output role=`CR_OFF_BASELINE_UNBLOCKED`, scientific production status와 독립.

- [x] 최신 branch와 원 연구자료를 읽고 byte identity와 전역 gate를 고정했다.
- [x] PREWORK의 nuclei/charge·전자회계·normalization을 유도했다.
- [x] focused tests를 먼저 작성하고 missing module import 실패를 확인했다.
- [x] 순수 Python reference를 작성하고 10개 시험 통과를 기록했다.
- [ ] Codex는 게시 후 source/test hash가 동일하면 재실행하지 말고, 실제 receiver의 off 분기 integration test 하나를 수행한다.
- [ ] root 게시 receipt와 receiver binding을 합친 `CR_OFF_ACCEPTANCE.json`(제안)을 작성한다. 원자 science gate는 그대로다.

Command for changed environment only:
`PYTHONPATH="$CR_PACKET/reference" python -m unittest discover -s "$CR_PACKET/tests" -v`
Expected 10 tests OK. 실패가 환경 import면 physical nonconvergence로 분류하지 않는다. 실제 consumer가 provider를 읽으면 작은 CR-off dispatch 수정만 한다. 원자 재계산으로 해결하지 않는다.

PR-CR-00: `docs(cr): preserve atomic lane and deliver CR-off source contract`. docs-only plus portable reference. 현재 패키지 게시의 PR 단위다. 동일 head에 기존 PR이 없음을 확인했다. 실제 PR 번호/게시 SHA는 root receipt에만 기록한다.

## Task CR-M1 — 조건부 외부 source 하나의 채택

**Files (proposed):** `research/external_atomic_provider_20261004/{manifest.json,provider.py,tests/test_provider.py}`.

**Interfaces:** consumes process ID+initial/final states+energy frame+query energy, produces σ in cm² and source/version/domain/error-class metadata. Return below physical threshold=0 only when the chosen source/process defines it; outside supported range=`UNSUPPORTED_DOMAIN` with no clamp/extrapolation. total-vs-state mismatch=`UNSUPPORTED_OBSERVABLE`.

Activation: rei_bianchi가 CR-on 목표·분포·range·출력을 명시한 이후. CR-F0의 blocker가 아니다.

- [ ] 원 source의 node 값·threshold·frame·license를 manifest와 함께 저장한다. FIDASIM 또는 CollisionDB에서 적합한 한 공급자만 먼저 선택한다.
- [ ] 시험: source node reproduction, 1s와 total 요청 거절, lab/COM 변환, coverage 밖 refusal, sigma≥0, unit conversion. 해당 데이터에 interpolation 규약이 없으면 raw node integration 또는 명시한 log-linear model로 선언하며 zero 구간을 로그화하지 않는다.
- [ ] failure를 확인한 뒤 최소 provider를 구현한다. 문헌 fit를 수정하거나 새로운 ab initio data를 생산하지 않는다.
- [ ] `python -m unittest discover -s research/external_atomic_provider_20261004/tests -p 'test_provider.py' -v`를 실행한다. observed source uncertainty와 코드 오차를 분리해 기록한다.
- [ ] 정확한 위 파일들만 stage하여 commit `feat(cr): pin external process-resolved cross section`.

PR-CR-01. Acceptance: named distribution이 소비할 domain에 query 가능, tail 처리와 라이선스가 명확. 소스 unavailable이면 source candidate 하나를 바꾸고 동일 intake 수행; 모든 후보가 부적합이면 CR-on만 BLOCKED다.

## Task CR-M2 — CR distribution·stopping·reservoir adapter

**Files (proposed):** 같은 경로의 `distribution.json`, `rate_reference.py`, `tests/test_rate_reference.py`, `ENERGY_LEDGER.json`.

**Interfaces:** exactly one of normalized velocity PDFs or number-density-per-energy-solid-angle. No hidden n_CR, v, 4π factors. Output species rates [cm^-3 s^-1], heat/chemical/radiation/escape [erg cm^-3 s^-1], momentum only if supported.

- [ ] 모형 선택: isotropic imposed CR spectrum이면 그 normalization/bounds를 저장한다. self-consistent anisotropic CR transport이면 별도 rei_bianchi extension을 요구한다. 둘을 암묵적으로 섞지 않는다.
- [ ] monoenergetic delta quadrature expected `n_t n_CR v σ`, zero CR exact-zero, warm distribution normalization, time-unit adapter 및 reservoir 합 보존 시험을 먼저 작성한다.
- [ ] rate integration은 supplied quadrature의 deterministic weighted sum부터 구현한다. out-of-domain positive mass가 존재하면 정량 tail bound 또는 domain 확대 전까지 `UNSUPPORTED_DOMAIN`.
- [ ] energy partition은 서로 겹치지 않는 항만 사용한다. primary/secondary source 및 stopping table 중복 계수를 시험한다. absent moment=`UNSUPPORTED_CAPABILITY`, 임의 0 아님.
- [ ] focused command: `python -m unittest discover -s research/external_atomic_provider_20261004/tests -p 'test_rate_reference.py' -v`.
- [ ] 위 파일만 commit `feat(cr): add distribution-normalized rate and energy ledger`.

PR-CR-02. Rate quadrature convergence만으로 source physical precision을 주장하지 않는다. 필요한 differential kernel 부재는 CR-on momentum branch의 blocker이고 photon-only baseline에는 영향 없다.

## Task CR-M3 — 실제 consumer 연결 및 공통 감도

**Files (proposed in rei_bianchi):** 해당 packet이 지정한 extension adapter/tests; bass_cr에는 source manifest와 acceptance receipt만 추가한다.

**Interfaces:** gas-frame proper-time rates, source_id/domain/error class, CR reservoirs, budget. Bianchi backgrounds는 재구현하지 않는다.

- [ ] first source call→species/heat mapping을 실제 receiver에 묶는다. imposed spectrum 범위부터 시작하고 transport extension은 별도다.
- [ ] CR-off recovery, charge/nuclei conservation, controlled CR-on reference, timestep/refinement, energy allocation을 focused 검사한다.
- [ ] 같은 source perturbation으로 FLRW/Bianchi paired run을 한다. 결과 변화가 중요할 때만 channel/domain을 확장한다.
- [ ] `CONSUMER_ACCEPTANCE.json`에 source SHA, receiver SHA, exact command, observed error와 remaining source model uncertainty를 기록한다.

PR-CR-03은 rei_bianchi에서 implementation PR, bass_cr에서 receipt 문서 commit이다. 실제 consumer entry point는 receiver packet의 조사 경로가 authority이며 이 문서는 미확인 실행 명령을 발명하지 않는다.

## Task CR-L1 — 원자확장 재개 (현재 PARKED_UNRESOLVED)

**Files:** `LEGACY_LANE.json`, 원격 R4AO NEXT_DAG 및 immutable 원 계획들.

- [ ] `CODEX_START_KO.md`의 legacy read-only recall 명령으로 원 계획을 확인한다.
- [ ] scope가 source 밖/새 state selective 또는 differential/coherent observable임을 명시하고 외부자료 부적합 근거와 비용·정확도 목표를 기록한다.
- [ ] 최신 별도 승인/실행 계약을 확인하고 R4AP complete-cover/error allocation을 진행한다. 완료된 R4AO 계약·m64·318 patch를 반복하지 않는다.
- [ ] 생성한 σ를 CR-M1과 같은 provider schema로 제출하고 관측량 동일조건에서 외부 source와 비교한다.

Legacy PR-LCR-01의 title=`research(cr): resume R4AP selected-entry coverage under external-provider interface`. 자동 개설/실행하지 않는다.

## Unresolved decisions

CR-off 첫 결과에 추가 결정은 없다. CR-on의 실제 spectrum/normalization/energy support, electron compensation/return-current closure, gas/fast neutral transport 범위, observable(1s formation/heat/momentum)은 현재 정해지지 않았다. 그래서 CR-M1..M3은 `CONDITIONAL_NOT_READY`이고 임의 default로 현재 baseline에 넣지 않는다. 이 질문들은 CR-on을 선택할 때만 해결하며 본 fastest handoff를 지연시키지 않는다.
