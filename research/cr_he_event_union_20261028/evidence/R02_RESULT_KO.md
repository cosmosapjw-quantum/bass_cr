# R2 — 실제 읽기와 기존 근거의 재사용

단위는 CR_PHYS02_HE_EVENT_UNION_V1이다. 이 단계는 이미 수행한 전체 목록 조사와 리셋 뒤 실제 읽은 관련 owner의 상태를 결합하고, 바뀌지 않은 과학 입력을 정확한 identity로 재사용한다. 중앙 기준은 22a99cb9b1691274e74c122d54521be4f2f51ba5의 **28/88**, 88 nodes/17 edges이며 이번 CR의 집계 효과는 0이다. 각 단계의 실제 게시 시점에는 해당 preflight와 단계 영수증을 우선한다.

## 조사 범위와 읽기 수준

[이전 실제 조사 복원](../intake/HISTORICAL_SURVEY_RECONSTRUCTED_KO.md)은 51개의 접근 가능한 repo, 2,373개 branch refs, CR 111개 PR의 terminal inventory를 기록한다. Library 최근 821개 / 5 pages, Dropbox 지정 parent 3,471개 / 6 pages 및 관련 subtree의 terminal 목록도 이전 실제 관찰이다. 이 수치는 당시 목록을 끝까지 읽었다는 의미이며 모든 repo의 모든 파일 본문이나 모든 개인 대화를 읽었다는 뜻이 아니다. 원 raw 응답은 호스트 리셋으로 손실됐고, 그 SHA를 새로 꾸며내지 않았다.

Drive의 선택 목록은 실제 응답대로 보존하되 전체 inventory는 PARTIAL이다. 이 대화의 Personal Context는 실제 unavailable을 반환했으며 개인 대화 전체 검색은 unavailable이다. 다른 owner가 별도 대화에서 indexed context를 읽었다는 기록은 이 제한을 바꾸지 않는다.

[현재 owner 종합](../intake/CURRENT_OWNER_SUMMARY_KO.md)과 fresh/의 실제 raw는 7개의 정확한 owner branch ref, 공개 PR·선택 source, AGENTS 및 중앙 상태를 리셋 뒤 새로 읽은 증거다. 중앙은 HE AZIMUTH09 반영으로 새 head가 됐지만 28/88이다. WU 20/20, HE 20/20, REI finite thermal 9/20, BASS restart 18/20을 각 scope로 유지한다. REC native의 Git C4와 이전 실제 C9 backup 19/20은 publication과 science evidence의 상태 차이다. 파일명 c905f4c1a128은 ZIP SHA 접두사이며 Git commit이 아니다.

중앙 DAG는 원 URL의 실제 HTTP200 full GET으로 1,638,771 bytes를 확보했다. SHA256은 3be88c48cf02a01b7efdbb75493045efcc643b3c2ef53de2ab6f823cab13a0ae이며 계산한 Git blob f86b94eb2c27ab35158a956cf24d89110b538bf0가 remote metadata와 일치했다. 이 byte identity 확인은 중앙 물리 완료 수의 증가나 과학 실행을 의미하지 않는다.

## 재사용할 source와 이전 결과

직전 PR111의 S=5c50071412964cb42fc06b96acf778ccd1a93e44, D=65e20e40e3c1d9e8384101017dc8940b3d09de09, M=ed6a899fa87ad42fbbb3569e96779bc3af716620을 유지한다. Retained PHYS02 revision은 4ca5a90de79c8fb82a25fd9e83615bec0dfa870b이다. 정확한 source와 복구 결과는 [INPUT_MANIFEST](../inputs/INPUT_MANIFEST.json), [HOST_RECOVERY](HOST_RECOVERY.json), [이전 최종 영수증](../inputs/PREDECESSOR_FINAL_RECEIPT.json)에 결속한다.

| 입력 | 재사용 identity와 의미 |
|---|---|
| ACTUAL_SOURCE_RECORDS.json | SHA256 8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf; 저장 source의 실제 bytes |
| ATTRIBUTION_ARRAYS.npz | 233,050 bytes, SHA256 1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47; 저장 H/He attribution |
| PR111 source archive | 418 payloads의 원 source 복구; 전체 payload SHA/CRC PASS 기록 재사용 |
| PR111 closeout archive | 77 payloads의 원 closeout 복구; D에만 있는 ADMISSION/BUDGET은 exact closeout payload와 live Git blob으로 복구 |
| 기존 source·H1·HeI·C23E·RR 계산 | scope와 identity가 맞는 기존 결과를 재사용; 이번 문서 단계에서 재실행 0 |

새 모델은 저장 inclusive He marginal을 보존하는 사건 표현을 다룬다. Source fit, projection, quadrature 또는 RR response를 다시 계산하지 않는다. 이미 포함된 target density, angle, projectile speed, proper729, clock/energy normalization은 한 번만 소유한다.

## 바뀐 근거가 허용하는 일

새 owner 자료 가운데 현재 retained source와 같은 isotope/state/frame/support/history의 actual atomic-He exclusive joint kernel을 제공한 입력 bytes는 이번 확인 범위에서 없다. 따라서 새 연구는 event-union의 정확한 수학적 보정과 같은 marginal을 가진 구성적 witness를 다룬다. Foreign bath, n_b, temperature, rate, exposure, physical error와 budget은 가져오지 않는다.

Primary 문헌의 실제 이전 읽기와 제한은 [primary map](../intake/PRIMARY_SOURCE_MAP_KO.md)에 있다. 이번 R2 게시 문서 준비에서는 새 SciSpace·Exa·primary 검색과 Wolfram evaluator를 실행하지 않았다. 이전 successful text extraction, discovery-only 및 실패를 구분한다.

## 단계 결과와 남은 판정

조사·입력 재사용의 근거는 준비됐다. 새 파일은 새 byte identity를 가지며 [복사 대응표](../intake/RECOVERY_COPY_RECEIPT.json)가 그 대응을 기록한다. 단계 Git·dual backup의 실제 완료는 root가 발급하는 R02 단계 영수증으로 판단한다. 본 문서만으로 게시 완료나 새 runtime PASS를 선언하지 않는다. Metadata·문서·복사 CPU는 unmeasured이며 0으로 보고하지 않는다.
