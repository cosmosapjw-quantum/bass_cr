# R10 — 이론 종료와 코딩 루프의 실행 인계

단위는 CR_PHYS02_HE_EVENT_UNION_V1이며 경로는 research/cr_he_event_union_20261028이다. 이 문서는 완성된 이론 산출물과 다음 코딩 검증의 의존 관계를 보존한다. 새 runtime, 전체20/20 또는 최종 과학 closeout을 앞서 선언하지 않는다. 중앙 기준은 실제 22a99cb9b1691274e74c122d54521be4f2f51ba5의 **28/88**, 88 nodes / 17 edges, CR 집계 효과0이다. 각 단계의 최신 preflight·게시 영수증이 해당 시점의 실제 identity를 정한다.

## 재사용할 완성된 이론

[전체 증명](../theory/THEORY_KO.md), [작은 정확한 예](R04_RESULT_KO.md), [독립 검토 경계](R06_RESULT_KO.md), [주장별 판정](R08_RESULT_KO.md), [계산 계약](R09_RESULT_KO.md)을 재사용한다. 핵심은 finite atomic μ=S+2π₁D, cross-event correction(+C,0,−C), sharp interval[0,min(N/2,N−M)] 및 모든 질량 경우의 half-shift construction이다. 이 결과는 조건부 measure family의 완결된 유도다.

R7의 한정 CAS identity 결과는 root가 실제 원 응답과 식·가정·실행 경계에 결속한다. 이 문서에는 아직 관찰하지 않은 CAS 값이나 새 numerical PASS를 삽입하지 않는다. 이미 완료된 유도와 기존 source/RR 계산을 그 결속을 위해 다시 실행할 필요는 없다.

## 다음 코딩 작업의 의존 관계

| 작업 | 실제 준비된 입력 | 완료 판단에 필요한 반환 |
|---|---|---|
| 코드·입력 identity 고정 | CONTRACT.json, INPUT_MANIFEST.json, 복구한 실제 source와 NPZ, 독립 static review가 본 네 draft | 실제 채택한 구현 bytes와 입력 identity, 현재 AGENTS/local·remote HEAD/preflight |
| Primary bounded 실행 | Pinned loader, all-single·diagonal·half-shift generator, consume_event_union | 실제 pinned NPZ를 읽은 output, witness, 결과와 attempt receipt |
| Targeted controls | F01 atomwise marginal, F02 complete claims, F03 loader/fixture provenance, state/support/window/nb 거절 계약 | 실제 positive/negative outcomes; 실패와 수정 시도 보존 |
| Independent bounded 실행 | Production import 없는 incidence reference, 직접 species transition, 유한 81-case graph reference 설계 | 실제 raw comparisons와 PASS/FAIL, reference/input/code identity |
| 필요한 과학 그림과 해석 | 실제 입증된 witness·bound 결과 | 실제 plot 산출물·제한·비용. 입력이 없는 물리 spectrum/history를 만들지 않음 |
| C9 판정과 C10 closeout | Primary·controls·independent·plot의 실제 결과, 누적 예산과 원 실패 | 실제 scoped admission, source archive, dual backup/R3, 중앙 owner-return, 최종 인계 |

Implementation·controls·independent reference의 초안은 존재하고 새 static review는 READY_FOR_RESERVED_REFERENCE_RUN이다. Formal F01–F03은 static closed/runtime pending이다. F04의 finite-atomic scope는 계약과 증명에 명시됐다. 실제 runtime 결과를 받은 뒤 필요한 최소 판정을 수행하며, 같은 scope의 새로운 검토 층을 반복해서 만들지 않는다.

## 실행 계약과 비용 경계

이 단위의 독립적인 CPU ceiling은 **40 CPU-s**다. Preparation, worker, coordinator, 실패와 plot을 포함한다. 단일 worker/native thread 원칙과 root의 현재 BUDGET.json 및 reservation을 따른다. 이전 PR111의 29.54616, PR110의 15.307989 등 잔여량과 foreign owner 예산은 이관하지 않는다. 실행 전에 실제 누적 비용과 남은 allowance를 읽으며, 문서의 cap만으로40 CPU-s 전체가 아직 남았다고 가정하지 않는다.

한정 symbolic identity batch의 요청 경계와 실제 remote CAS 결과는 R7에 기록한다. Remote CAS, metadata/provider/publication CPU는 측정되지 않으면 null/unmeasured로 남긴다. 0으로 계산하거나 측정한 science CPU와 섞어 정확한 global remaining을 만들지 않는다. 모든 실패·UNKNOWN_NO_ACK·preparation/coordinator 비용을 남기고, 근거 없는 preventive aggregate hard-cap proof를 주장하지 않는다.

정확한 rational marginal·보존·bound·witness는 exact equality로 검사한다. Independent report의 수치 비교는 고정 1e-12이며, source 재사용의 기존 2e-11 atom tolerance를 새 계산의 임의 완화에 쓰지 않는다. 같은 사건의 conflicting content, incomplete claim, negative/nonfinite weights, input bytes mismatch, mixed isotope/state/frame/clock, support 확장, 잘못된 nonnull n_b와 시간 중복/replay는 거절한다.

## Source·복원·물리적 null의 보존

PR111 S=5c50071412964cb42fc06b96acf778ccd1a93e44, D=65e20e40e3c1d9e8384101017dc8940b3d09de09, M=ed6a899fa87ad42fbbb3569e96779bc3af716620에서 재사용한다. Retained PHYS02 revision, source JSON SHA와 attribution NPZ SHA는 CONTRACT/INPUT_MANIFEST에 고정돼 있다. Source/closeout은 지속 원본에서 복구됐으며 그 원본 ZIP에 후속 영수증을 삽입해 재생성하지 않는다.

리셋 전에 새 단위의 science run은 없었다. 이전 전체 조사와 수학 검토의 scratch raw는 일부 손실됐으며 대화에 남은 실제 관찰로 복원했다. 복원된 문서는 새 SHA를 갖고, 손실된 파일과 byte-identical하다고 주장하지 않는다. 새 실제 owner raw·중앙 original GET과 역사적 복원 자료는 intake에서 구분한다. Storage ACK, original-byte restoration, 과학적 검증을 서로 대체하지 않는다.

Actual exclusive D, actual C_cross, outside partner state/energy/history/response, residual excitation, proton donor debit, actual EOS/T와 full-source physical native25는 null이다. Conditional 100K·H1/He4·same-state n_b=8750/47을 유지한다. Absolute proper volume은 null이며, q=tA의 proper [0,10¹⁰]s 밖 history는 unknown이다. Source-ion union 또는 corrected partition source sum 중 하나를 한 번 사용하고 저장 RR을 한 번 붙인다. Retained photon은 별도 포트다.

## 게시와 다음 인계

기존 사용자의 additive backup·게시·bounded 실행 승인은 유지한다. 각 단계는 expected SHA와 force=false로 실제 Git 게시 및 dual backup을 완료하고 중앙 completed/total을 기록한다. Source와 closeout의 create-only archive, 필요한 actual R3, 기존 CR node에 대한 scoped owner-return과 copyable final handoff는 실제 runtime 판정 이후 root가 완결한다. Main merge는 이 계약에 없다. 이 20단계 단위 이후 auto-next는 OFF다.

N4/N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED, L4 false 및 global physical completion/error/budget remaining/currency null을 유지한다. 타 owner의 local 19/34·9/13·working 33/88 등은 중앙에 합산하지 않는다. 개인 대화 전체 검색 unavailable과 Drive partial inventory도 최종 인계에 남긴다.

이 문서 자체의 역할은 완료된 이론을 다음 실행에 전달하는 것이다. Final report·budget closeout·source/closeout의 실제 identity·runtime admission은 후속 실제 결과에 의해 작성한다.
