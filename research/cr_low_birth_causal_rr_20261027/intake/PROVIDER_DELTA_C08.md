# C8 WU 변경 관찰 — 고정된 source와 이론·delivery 범위

WU `research/provider-registry-20261025`의 실제 `284717f359f186976671e8a540831c628d20108a → 34b1d470059bbb0b812749ab126a6f255859a8be`를 GitHub connector로 비교했다. **1 commit, 반환된 변경 경로68개**이며 giant PR diff는 요청하지 않았다. Actual UTF-8 핵심 원문9개와 실제404 한 건을 저장했고, 성공한9개 payload는 provider Git blob SHA1과 실제 바이트가 일치한다. [전체 exact pins·범위](PROVIDER_DELTA_C08.json), [payload manifest](provider_delta_C08/MANIFEST.json), [실제 compare](provider_delta_C08/WU_COMPARE.json)

## 무엇이 진행됐는가

R7 workflow는 **2/20 → 4/20**으로 R2/C2가 완료됐다. Local DAG는 **13/30** 그대로다. 새로 추가된 것은 state-dependent molecular mass-action source와 conserved-reservoir feedback의 이론 주장6개, causal block comparison, singular-safe exponential bound의 equation map 및 최신 source 조사다. `CLAIMS.json`은 **DERIVED_PENDING_INDEPENDENT_REVIEW_AND_NEW_EXECUTION**이고 independent review도 pending이다. `EXECUTION_LEDGER.json`의 science runs는 빈 목록이며 `CONTRACT.json`과 ledger는 이전 C05에서 읽은 바이트와 동일하다. 이 조사는 WU의 새 증명을 독립 심사한 것이 아니며 CR에 그 이론을 채택하지 않는다. [현재 workflow](provider_delta_C08/WU_WORKFLOW_RECORD.json), [현재 주장](provider_delta_C08/WU_theory__CLAIMS.json), [equation map](provider_delta_C08/WU_theory__THEORY_CODE_MAP.json)

Actual molecular consumer와 GL2022 native reactive state arrays는 여전히 미제공이다. Branch/destruction vector, collider density/history, clock, initial state, named consumer도 INPUT_PENDING이다. R4 formation의 p-H2(v0,j0)와 GL2022 thermal-HD/spin-weighted-product destruction은 state matching 없이 같은 detailed-balance pair가 되지 않는다. Excitation과 reactive destruction의 구분 및 TIQM/SQM 대안 선택을 유지한다. `new_source_rows_acquired=0`, `physical_IVP=0`, `new_Q=0`, `HH_R10=OFF`, `production=NOT_ISSUED`, `L4_ready=false`, physical/central completion delta0이다. [재사용·변경 범위](provider_delta_C08/WU_authority__REUSE_AND_DELTA.json), [고정 계약](provider_delta_C08/WU_CONTRACT.json)

AGENTS는53,117 bytes, SHA256 `3236d4deaeefca34b62d53ee4f2ff3711f42ff0c9b806404a9825e45a74e24fa`로 변하지 않았다. Root의 실제 C08 preflight read와 로컬 snapshot의 byte hash를 대조했다. WU의 새 별도 allowance(primary1/reference1/Wolfram1, CPU60/60·symbolic30)도 바뀌지 않았고, R6/PHYS91 잔여는 각각0/0/0, global remaining과 historical CPU는 null이다. 이 allowance를 CR로 이월하지 않는다.

## Delivery의 실제 진전과 남은 항목

이전 C05가 고정 base에서404로 기록했던 `delivery/S01.json`이 이번 새 commit에 실제 추가됐다. 이 영수증은 S01 source `284717…`의 ZIP **30,983 bytes**,8 payload members, SHA256 `576c749858c6cb4bdcd723adcc425e775bb5e4e4917cddbac3df0ae8bb43d881`에 대해 Dropbox/Drive 각각 원본30,983 bytes full GET, CRC 및 payload SHA/Git blob PASS를 기록한다. Dropbox는 `id:BSpOijBcT10AAAAAAEDHxA`, Drive는 `1rLZLb7by7Pj58SmaMPHkEbXpSzNCfYqo`다. `full_scoped_source=false`도 그대로다. **이는 새 commit에 게시된 실제 provider receipt를 읽은 것이며, 이번 CR reviewer가 backup을 다시 다운로드한 R3는 아니다.** Reviewer의 새 backup GET은0이다. [실제 S01 영수증](provider_delta_C08/WU_delivery__S01.json)

반면 **새 S02**의 checkpoint는 게시됐지만 `delivery/S02.json`은 정확한 새 HEAD에서 실제 **HTTP404**였다. Checkpoint는 upload/readback 후 다음 metadata commit에 영수증을 기록한다고 명시한다. 따라서 이 pin에서 S02 backup ACK는 미확립이며, S01의 검증을 S02의 검증으로 옮기지 않는다. [S02 checkpoint](provider_delta_C08/WU_checkpoints__S02.json), [실제 S02 404](provider_delta_C08/WU_delivery__S02.json_ERROR.json)

## 이번 CR에 대한 결정

새 WU rate·response·physical consumer·T·nb·예산을 채택하지 않았다. CR의 frozen source,100 K 조건부 H1/He4 inventory, operator, tolerances와 실제 C7/C8 결과는 그대로다. 과학 실행·과거 replay0이며 REPORT는 이 변경 확인을 위해 수정하지 않았다.

현재 중앙 programme은 `74aff0740d1812c732466563a9c66108a3a4d8fd`, **28/88**,88 nodes/17 edges, 이번 CR 효과0이다. Foreign B3h의 이미 관찰된+1을 유지하며, WU 조사 문서에 남은 과거0713/13-of-28 또는 CR27-of-88 관찰로 현재 집계를 덮어쓰지 않는다. REC programme `4a8e541030ee2cbd02e26ba671083b705d309d49`와 HE programme `ac6042a6b0610b09d0576538767ee0299389a5eb`는 C08 preflight에서 동일하다. PR236의32/88은 합산하지 않는다.

개인 전체 대화 unavailable, Drive partial inventory, provider별 state/isotope/domain gate와 별도 예산, 기존 failure/UNKNOWN_NO_ACK를 유지한다. 이 확인은 최신 공개 owner 변경의 제한된 provenance 판독이며68개 모든 payload나 WU 전체 새 이론의 독립 검증을 주장하지 않는다.
