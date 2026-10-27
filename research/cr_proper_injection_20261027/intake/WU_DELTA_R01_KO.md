# WU 공급자 R01 변경 확인

R01 사전 점검(2026-10-27 09:52:20 UTC)에서 WU의 관찰 HEAD가 사용자 기준 `bfdeed676617c8b75ed81ac5e79e800fa69f83db`에서 `4ea08eb3709c90285946dce2cf824f402056d645`로 진행했다. 새 `AGENTS.md`와 변경에 직접 관련된 admission·실행 원장·다음 입력 계약·실제 게시 영수증을 읽었다. **PHYS02 source 선택, nb=null, 기존 CR bath와의 연결 gate는 그대로 유지한다.** 아래는 pinned revision에 대한 확인이며 후속 WU 진전을 예단하지 않는다.

## 추가된 근거와 유지되는 gate

새 R4는 분자 공급자 6 variants, 77 native coefficient cells, 14 species/state identities, 6 candidate number columns, 29 원래 fit nodes를 source/theory/integer/formula 범위에서 채택했다. 기존 149 columns와 249 checks는 재사용했고 재실행은 0이다. 원 19 targets/28 directions의 primary reference 28/28도 유지된다. 새 28/28 implementation controls, 독립 8/8 groups(1138 assertions), 제한된 Wolfram 1회는 이 범위의 근거다. [R4 admission](https://github.com/cosmosapjw-quantum/WU088_HH/blob/4ea08eb3709c90285946dce2cf824f402056d645/research/provider_registry_molecular_r4_20261027/SCIENTIFIC_ADMISSION.json)

| 항목 | 이번 WU 기록의 판정 | CR 영향 |
|---|---|---|
| physical rate / nuclear Q / energy partition | 모두 false | 외부 실제 rate·heating으로 채택 불가 |
| actual state lift / named consumer / runtime activation / new IVP | 모두 false | 실제 recipient를 새로 연결하지 않음 |
| isotope/state | 선언한 H1/D2/Li7 nuclear ground와 공급자별 qualification을 구별 | 불명확한 isotope/state 자동 상속 금지 |
| RA photon | primary event count 1, cascade/escape yield와 energy null | retained-photon/열 포트로 무근거 이전 금지 |
| method/spin/ensemble | TIQM·SQM 대안은 합산 금지; ortho/para 합산은 spin normalization 전 거절; forward/reverse ensemble 다름 | same-event 중복 및 자동 detailed balance 거절 |

Bovino의 2.258 eV는 native estimate이며 승인된 Q가 아니다. GL2022의 405 K는 fit activation parameter다. Fit residual을 physical covariance나 전역 오차한계로 바꾸지 않는다.

다음 WU 입력은 GL2022 HD(v=0,j=0..8)+H+ 파괴의 실제 state-to-state 배열과 spin·support·energy convention, 그리고 consumer x/π·kinetic T·collider density·proper clock·reference density다. 원문 supplement 존재는 확인됐지만 숫자 배열·SHA256·실제 grid는 아직 없고 consumer binding도 열려 있다. EMAA의 HD excitation은 다른 채널이다. [다음 입력 계약](https://github.com/cosmosapjw-quantum/WU088_HH/blob/4ea08eb3709c90285946dce2cf824f402056d645/research/provider_registry_molecular_r4_20261027/followup/NEXT_INPUT_CONTRACT.json)

## 예산·게시·집계

WU 새 단위 측정 child CPU는 6.824501 s이며 5 attempts의 wall 합은 6.93655899800433 s다. Wolfram kernel CPU는 null이고 source preparation·network·publication·delivery는 미측정이며 0이 아니다. PHYS91 primary/reference/Wolfram 잔여는 각 0, 전역 비용·잔여는 null이다. 이 예산을 CR에 이월하지 않으며 CR의 이전 30 CPU 잔여도 새 단위로 자동 이월하지 않는다. 이번 delta는 읽기·해시·기록만 수행해 source science replay 0을 유지했다. [실행 원장](https://github.com/cosmosapjw-quantum/WU088_HH/blob/4ea08eb3709c90285946dce2cf824f402056d645/research/provider_registry_molecular_r4_20261027/EXECUTION_LEDGER.json)

실제 R10 content source `041224c5123689b58439d1d1949bdfb1fb1e5157`는 expected parent `f949c21cca6e2534b725241068bd6c6e06158495`, force=false로 게시되고 exact-text readback이 기록됐다. 그러나 최종 S10 ZIP·이중 backup·이중 원본 byte readback은 미완이다. S09는 supplier 기록상 Drive raw 검증, Dropbox metadata 확인이며 이 delta에서는 backup GET을 새로 수행하지 않았다. WU workflow는 **18/20**, local DAG **9/24**다. 과거 공급자 runtime SERVICE_ERROR를 현재 능력 제한으로 계승하지 않는다. [실제 게시 영수증](https://github.com/cosmosapjw-quantum/WU088_HH/blob/4ea08eb3709c90285946dce2cf824f402056d645/research/provider_registry_molecular_r4_20261027/delivery/R10_PUBLICATION.json)

중앙은 **27/88**, 이번 WU 변경 집계 효과 **0**이다. WU local 9/24나 미병합 PR236 32/88을 더하지 않는다. L4=false, global physical completion/error/budget remaining/currency=null을 유지한다. R01의 PR108은 `2776752de6952f60d8d690a128f33fec4df2c57b`이며 기존 병렬 owner 작업을 보존한다.

## 이번 CR source에 대한 결론

WU 새 coefficient 표와 candidate event column은 실제 외부 baryon injection이나 finite proper-time history를 제공하지 않는다. PHYS02의 기존 실제 `Qe=tA`와 0≤t≤10^10 s, source revision `4ca5a90de79c8fb82a25fd9e83615bec0dfa870b`를 선택한 근거가 바뀌지 않는다. PHYS02 100 K와 기존 PR107 RR 10000 K bath는 서로 다르고, 같은 상태의 explicit nb가 없으므로 nb/native25 및 bath 연결은 gate를 유지한다. 개인 대화 전체 검색 unavailable과 Drive partial inventory 한계도 유지한다.

정확한 source URL, 실제 읽은 파일 byte 길이·SHA256·Git blob, gate, 비용 및 게시 범위는 `WU_DELTA_R01.json`에 보존했다.

