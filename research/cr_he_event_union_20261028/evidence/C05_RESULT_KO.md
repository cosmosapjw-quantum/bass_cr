# C05 — 완성된 코드 경로와 세 정적 결함의 수정 상태

단위: `CR_PHYS02_HE_EVENT_UNION_V1`. canonical implementation은 기존 draft 여섯 개를 정확히 복사하여 `../implementation/`에 배치한다. `../IMPLEMENTATION_MANIFEST.json`이 각 원본·목적지 bytes, SHA256 및 byte equality를 기록한다. 이 배치는 코드 재작성이나 계약 변경이 아니다. 과학 실행·probe·plot 실행은 아직 NOT_RUN이며 BUDGET을 수정하지 않았다.

## 실제 코드 경로

| 파일 | entry point와 역할 | 과학 입력·출력 |
|---|---|---|
| `event_union.py` | pinned loader, 세 sparse lifts, claim validation, `consume_event_union` | 저장 NPZ 두 배열; typed exact atoms/events; conditional source-ion union/native 부분 반환 |
| `primary.py` | `main(outdir, npz_path=None)` | 실제 3201 atoms, 세 full-source consumer 호출, atom별 exact 비교, 네 prefix·네 birth-time bins; RESULT와 half-shift witness 저장 |
| `controls.py` | `main(outdir)` | 작은 ALGEBRAIC_FIXTURE의 exact acceptance·refusal; 실제 check별 원 결과 저장 |
| `independent.py` | `main(outdir, npz_path=None, primary_path=None, witness_path=None)` | production import 없이 pinned NPZ·primary·witness를 직접 incidence reference와 81-case six-edge DP oracle로 대조 |
| `plot.py` | `main(outdir=None, input_path=None)` | accepted primary RESULT 한 파일에서 단일 figure의 PNG+SVG와 actual input SHA; source/RR 계산 없음 |
| `run_bounded.py` | CLI `run_id mode reservation` | 새 reservation·한 owned worker·실행 source snapshot·actual CPU/tail·결과와 실패 영수증 |

기본 NPZ 위치는 선행 단위 `research/cr_parent_event_native25_20261028/runs/prepare_v1/ATTRIBUTION_ARRAYS.npz`다. independent와 plot의 기본 primary 위치는 이 단위 `runs/primary_v1/RESULT.json`이다. 다른 accepted primary를 써야 하면 실제 entry point의 명시적 path 인자 또는 plot의 `CR_PLOT_INPUT`으로 결속해야 하며 파일명만 보고 최신 결과를 추정하지 않는다. root runner가 해당 attempt source snapshot을 만들고 실행 후 canonical bytes가 변하지 않았는지 확인한다.

## 이미 관찰된 세 결함과 현재 수정

아래는 `R06_INDEPENDENT_STATIC_OBSERVATION.json`에 기록된 한 독립 정적 관찰을 재사용한 것이다. 새로운 review tree나 중복 review 실행은 만들지 않았다. 세 finding의 현재 분류는 **STATIC_CLOSED_RUNTIME_TARGETED_PENDING**이다. 코드에서 수정되었지만 실제 targeted-control PASS는 아직 없다.

| finding | 원래 결함 | 실제 수정 및 실행될 control |
|---|---|---|
| F01 | caller event들이 source electron marginal을 바꾸어도 source label만으로 통과할 수 있음 | `consume_event_union`이 deduplicated events를 `marginal`에 투영하고 모든 selected atom coefficient를 exact 비교. `F01_changed_source_marginal` 및 `double_leg_factor_two_mutation`이 `SELECTED_SOURCE_MARGINAL_MISMATCH`를 기대 |
| F02 | cross event의 한쪽 selected partition claim이 빠지면 개별 합과 union의 의미가 달라짐 | union에 들어간 모든 event가 모든 selected incident partition에 존재하는지 확인. 같은 ID의 content도 동일해야 함. `F02_incomplete_cross_claim`은 `INCOMPLETE_PARTITION_EVENT_CLAIM`을 기대; 이후 count/energy의 partition additivity도 exact 확인 |
| F03 | arbitrary fixture가 canonical source SHA label을 복사하여 actual source로 승격될 수 있음 | `load_pinned_source`가 전체 NPZ SHA·shape·float64·support/order를 확인한 뒤 immutable atom-content digest를 등록. `validate_source`가 payload digest·두 source pins·process-local loader attestation을 확인. fixture는 canonical/NPZ pins null이며 digest mutation·canonical-label forgery·unattested actual provenance를 거절 |

F03의 process-local registry는 과학적 input identity를 확인하는 장치이며 악성 Python caller에 대한 security sandbox라고 주장하지 않는다. canonical source JSON SHA는 귀속 pin이고 실제 새 loader가 읽는 물리 input bytes는 별도의 NPZ SHA로 결속한다. stored attribution을 원래 canonical source의 대체본으로 부르지 않는다.

## 완성도와 실행 후 판정 경계

코드는 하나의 실제 계산 경로를 제공한다. typed atoms/events, 실제 source bytes loader, exact finite-time factor, event ID union, 불완전 claim·겹치는 time return 거절, same-state nb gate, species21·ionic charge·chemical correction, source/native ownership 및 null gates가 entry point에서 연결되어 있다. primary는 세 witness 각각의 모든 3201 atom 비교를 논리 check count와 구분하여 저장하고, 그림은 그 저장 결과만 사용한다.

selected electron count/energy는 중복 parent correction으로 바뀌지 않는다. `RR_correction=0`과 `retained_photon_correction=0`은 이번 correction이 해당 port를 변경하지 않는다는 의미다. 실제 donor work, outside partner, He residual excitation, actual C, actual exclusive measure, actual T와 full physical native25는 null이다. fixture 결과를 실제 physical activation으로 승격하지 않는다.

source fit, old proton quadrature, old H1/HeI/C23E, old RR 또는 transport implementation의 import/호출 경로를 추가하지 않았다. primary와 independent가 저장 atoms로 새로운 event-union 검증을 수행하는 것은 이전 attribution fitting/RR replay가 아니다. 포괄적 full-source physical closure의 부족한 input을 새 코드가 채웠다고 주장하지 않는다.

후속 실행은 C4의 별도 40 CPU-s 계약과 root의 actual reservation 안에서만 진행한다. 실제 실패는 그 attempt와 비용을 보존하고 필요한 최소 수정만 별도 identity로 기록한다. prior implementation bytes나 immutable SOURCE/CLOSEOUT에 후속 영수증을 삽입하지 않는다.

근거: `../IMPLEMENTATION_MANIFEST.json`, 여섯 `../implementation/*.py`, `R06_INDEPENDENT_STATIC_OBSERVATION.json`, `../CONTRACT.json`, C01–C04 evidence. 중앙 참고 baseline 28/88; canonical code 배치 자체의 중앙 집계 변화 0. 실제 C05 게시·이중 백업은 별도 stage receipt가 근거다.
