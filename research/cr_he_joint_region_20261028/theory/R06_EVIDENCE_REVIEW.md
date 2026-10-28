# R06 — 증거 재사용·source interface 독립 정적 검토

**판정: PASS_SCOPED_EVIDENCE_INTERFACE. 이 범위의 구체적 blocker 0.** 공동 달성의 수학 판정은 별도 reviewer의 책임이다. 이 문서는 R6 전체 이론 수용이나 native 실행 PASS를 대신하지 않는다. 과학 프로그램·solver·기존 optimizer 실행0, 외부 게시0, R7+ 작업0. 문서/JSON 정적 조회, 저장 record 식별자 대조, 기존 파일 byte hash 확인만 수행했다.

## 검토 snapshot

- 새 theory/THEOREM.md SHA256: 35a8fe74ff3df650f28e6c4b64bbdf8a73d2545943b719451bb6bedfe799b0b8.
- 새 theory/R03_CLAIMS.md SHA256: 65ae6de2f6c9388449333dcc5fccb159a7e31e09cb8a5e2666f69eb7b373be3c.
- 새 CONTRACT.json, R02_EVIDENCE.md, intake/RECOVERY_RECEIPT.json 및 inputs의 세 selected certificate JSON.
- PR114 local THEOREM.md·R08_ADMISSION_KO.md와 R1에 취득한 [최종 ADMISSION 원문](https://github.com/cosmosapjw-quantum/bass_cr/blob/3d9818b4b91d00beef946aa88540d73c33e51dac/research/cr_he_energy_sum_20261028/ADMISSION.json). 과거 local base에 최종 ADMISSION이 있다고 가정하지 않았다.
- PR115 local THEOREM.md·ADMISSION.json, predecessor의 atom-digest 정의와 원 consumer. 모듈 import·과학 함수 호출 없음.

## 확인 결과

| 의무 | 확인 |
|---|---|
| 기존 결과와 새 주장 | PR114는 energy-permitted pair·diagonal 아래 \(d_{\max}\), PR115는 cross-bin \(C_{\max}\)다. PR115 §4는 joint fixed-d boundary 미계산을 명시한다. 새 J1/J2와 Lemma3의 공동 달성이 별도 의무로 구별된다. |
| 가정의 차이 | 새 정리는 positive-mass low–high 허용쌍이 모두 cross-bin이라는 추가 전제다. 이전 개별 optimum을 그 전제의 검증으로 사용하지 않는다. 모든 energy-permitted pair, divisible mass, singles 허용을 유지하고 추가 mask는 없다. |
| Loop·좌표 | R03의 \(a_i=s_i+2p_{ii}+\sum_{j\ne i}p_{ij}\), THEOREM의 residual/2 diagonal filling이 일치한다. \(d\)는 double 사건 질량, \(C\)는 unequal-bin double 질량이다. Behrend incidence1을 그대로 채택하지 않는다. |
| Unique atoms | PR114 native_atoms는 **3,201 records/3,201 unique keys = active3,200 + cutoff_ghost1**. PR115 K20 atoms도3,201 unique keys이며 두 저장 배열의 내용·순서가 정확히 같다. 여러 case의 반복 records를 unique atom 수로 합산하지 않았다. |
| Reused certificate | PR114 selected cases N001/N002/N003/N005/N007/N009는 max_events·dual_by_key를 보존하며 lower-target events는 선택하지 않았다. PR115는9 bounds, original_witness_present=true는 K0/3/20뿐이다. K6 공동/native primal은 새 coding 의무로 남는다. |
| Threshold | Decimal \(1/5\)와 twice-binary-ghost \(3602879701896397/18014398509481984\)를 별도 exact cap으로 보존한다. Ghost를 active atom에 흡수하지 않는다. |
| Physics·consumer | Full selection \(p=0\), 단일 proper window, W·nb 각1회 적용을 명시한다. Partial selection에는 별도 \(p,C_S\)가 필요하고 inventory는 call별이다. ActualK/kernel/d,C/외부partner/donor/EOS/T/fullphysicalnative25를 수학 증인으로 채택하지 않는다. |
| 미래 실행·예산 | J4의 실제 support/marginal/consumer 검사는 coding 의무다. PR115 closed28.653943/40에서 새 allowance로 이전0이다. |

## 입력 identity

현재 파일 byte hash를 대조했으며 RECOVERY_RECEIPT/CONTRACT와 일치한다.

| 파일 | SHA256 |
|---|---|
| ATTRIBUTION_ARRAYS.npz | 1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47 |
| PR114_SELECTED_WITNESSES.json | ae09b3183cbf7f16bb89983fa5f649a65e284b2d4a4042f9d424d0fe5566f8e5 |
| PR115_SAVED_BOUNDS.json | 9c9359a570de873ff6a7ad172ae2a95a1b3d3c2552bbbb80e7239c474fbeba01 |
| PR115_K20_WITNESS.json | 0cc7d56e82ef3fcab3913f24ed7b69e4e87a123da3727f54afdce960e457c775 |
| 원 event_union.py | 6b1813ccca95cf3843a217132933db373590b9580d7b1160964468e0351b286d |

PR114 source-member SHA4f3cad59...와 PR115 source-certificate SHAc93fc0b6...는 derived selection 파일 hash와 다른 대상이다. Canonical-source SHA8fca44c3...는 이전 고정 근거의 재사용이며 이번에 해당 원문을 새로 생성·검증했다고 기록하지 않는다.

PR114/consumer atom_content_sha2562cfca578...는 tuple-array 표현(energy_sum.py:101, event_union.py:79), PR115 bound.atom_digest b1e67d1f...는 dataclass/dictionary 표현(cross_envelope.py:29–43)의 digest다. 두 값의 차이는 source mismatch가 아니다. 두 selected atom 배열 자체의 정확한 일치도 확인했다.

PR114 원본284payload/CRC 검증은 RECOVERY_RECEIPT에 기록된 부모의 R2 recovery이며 이 reviewer가 원격 GET·전체 archive 검증을 반복한 것이 아니다. 새 joint witness의 pair support·atomwise marginals·원 consumer acceptance는 별도 실증 의무로 남는다.
