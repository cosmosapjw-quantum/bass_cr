# R6 — 기존 독립 수학과 새 static 검토의 판정 범위

단위 CR_PHYS02_HE_EVENT_UNION_V1. 중앙 관찰22a99cb9b1691274e74c122d54521be4f2f51ba5의 **28/88**, 88 nodes/17 edges를 유지하며 이 단계의 집계 효과는 0이다. 수학 재사용, 새 static implementation review, 후속 runtime admission을 구분한다.

## 기존에 실제 관찰된 독립 수학 검토

리셋 전 별도 에이전트 /root/backup_survey_next는 유한 원자 event measure와 sharp cross bound를 PASS_DERIVED_SCOPED로 검토했다. 이 관찰은 대화에 남았지만 당시 원 review 파일과 scratch identity는 리셋으로 손실됐다. [복원 유도](../theory/THEORY_KO.md)는 그 수학적 내용을 완결해 보존하며, 새 파일의 SHA를 이전 review 파일의 SHA로 대체하지 않는다. 기존 검토의 재사용은 새 코드가 실행돼 합격했다는 뜻이 아니다.

## 새 독립 static 검토의 실제 원 기록

리셋 뒤 별도 reviewer /root/union_independent가 남긴 원 JSON을 [R06_INDEPENDENT_STATIC_OBSERVATION.json](R06_INDEPENDENT_STATIC_OBSERVATION.json)에 byte-identical하게 복사했다. 실제 decision은 READY_FOR_RESERVED_REFERENCE_RUN이며 current_code_blockers는 빈 배열이다. Scientific execution by this reviewer는 NOT_RUN이다.

검토된 event_union.py, primary.py, controls.py, independent.py의 현재 bytes/SHA가 review의 네 identity와 모두 일치함을 문서 복사 시 확인했다. 이 확인은 source identity 검사이며 scientific runtime 검증이 아니다. 해당 매핑은 ../intake/RECOVERY_COPY_RECEIPT.json에 있다. 이후 코드가 바뀌면 이 static 판정의 적용 identity도 다시 판단해야 한다.

| 발견 항목 | 조치와 실제 검토 근거 | 아직 주장하지 않는 것 |
|---|---|---|
| F01: atomwise marginal | Union events의 incidence를 한 번 projection하고 모든 selected atom coefficient를 pinned bundle과 exact하게 비교하도록 구현됐다. Fresh independent status는 STATIC_CLOSED_RUNTIME_TARGETED_PENDING. | 실제 rejection control 실행 PASS |
| F02: complete selected claims | Event ID를 일관되게 합친 뒤 해당 사건의 모든 selected incident partition claim을 요구한다. Missing cross side의 전용 control이 있다. Fresh independent status는 STATIC_CLOSED_RUNTIME_TARGETED_PENDING. | 실제 incomplete-claim runtime rejection PASS |
| F03: actual source loader와 fixture 구분 | Pinned NPZ SHA, shape, binary64 payload, atom identity와 loader provenance를 검사한다. Fixture의 canonical provenance는 null이다. Fresh independent status는 STATIC_CLOSED_RUNTIME_TARGETED_PENDING. | 실제 원 NPZ를 읽은 primary/independent run의 PASS |
| F04: 주장의 유한 원자 범위 | 현재 CONTRACT와 THEORY는 finite atomic nonnegative measure family로 범위를 제한한다. 이전 독립 수학의 scoped 결론과 일치한다. | Fresh JSON에 별도의 F04 finding/status가 있다고 주장하지 않음. Arbitrary continuous-measure theorem 또는 physical FDCS sharpness를 채택하지 않음. |

새 static JSON의 formal findings는 F01–F03이다. F04의 조치는 현재 계약·유도에 명시된 scope correction으로 기록한다. JSON의 reference-design 설명에 continuum이라는 표현이 함께 있어도 이 단위의 채택 범위는 finite atomic proof로 제한한다. 실제 원 review를 그 이유로 고쳐 쓰지 않는다.

## 독립 reference의 예정된 구별 능력

새 independent reference는 production imports 없이 실제 pinned NPZ를 다시 읽고, witness의 event leg incidence로 3,201개 atomwise marginal을 비교하도록 설계됐다. Union과 partition의 species transition을 직접 조립하여 charge, chemical energy, native correction 및 null 경계를 비교하도록 작성됐다. 또한 nᵢ∈{0,1,2}의81가지 capacity에 대해 여섯 cross-edge multiplicity를 살피는 exact multigraph reference가 포함돼 있다.

이 문서 작성 시 그 reference의 scientific 실행은 아직 없다. 유한81-case 검사는 실행되더라도 일반 증명의 대체물이 아니며, 일반 finite-atomic sharpness는 R5의 half-shift 구성에 의존한다. 실제 primary, controls, independent 결과와 bounded-run receipt가 반환된 뒤에만 runtime admission을 판단한다. 새 검토 층을 반복해 추가할 필요는 없다.

## 단계 판정

수학적 범위는 기존 독립 관찰과 완결된 복원 유도로 재사용한다. 새 구현은 관찰된 static blockers가 없고 예약된 bounded reference run으로 진행 가능한 상태다. **C9 runtime PASS는 아직 선언하지 않는다.** Source mismatch, 실제 실패, 잘못된 claim 또는 예산 문제는 후속 실제 결과에서 보존하고 필요한 최소 조치만 한다. 이번 문서 준비는 Git 게시·backup 또는 과학 실행을 수행하지 않았으며, 단계별 실제 완료는 root의 영수증에 결속한다.
