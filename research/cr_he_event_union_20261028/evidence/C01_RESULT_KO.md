# C01 — 목표, 실제 선행 baseline, 재사용 및 고정 기준

단위: `CR_PHYS02_HE_EVENT_UNION_V1`  
경로: `research/cr_he_event_union_20261028`  
문서 상태: 구현·실행 전 계약 근거. 이 문서는 새 과학 실행의 PASS 영수증이 아니다.

## 목표와 허용되는 결론

같은 저장 PHYS02 He 전자 marginal에 대해 세 조건부 사건 측도(single, within-atom double, half-shift)를 구성하고, 서로 다른 birth-energy partition에 걸친 동일 source-parent 사건의 중복을 제거한다. 명명된 소비자는 `implementation/event_union.py::consume_event_union`이다. 소비자는 같은 state/frame/proper-clock/support에 결속된 partition claims에서 하나의 source-ion union과 별도 보정량을 반환한다.

이번 계산은 유한 비음성 사건 측도에서 `0 <= C <= min(N/2, N - max(n_i))`의 sharp envelope와 실제 저장 atom별 marginal 보존을 평가한다. 실제 exclusive He 사건 kernel이나 실제 C를 추정하지 않는다. source-parent ionization과 이미 저장된 RR target capture는 서로 다른 ownership을 유지한다. 새로운 union source 또는 보정된 partition sum 중 하나만 적용하고, 저장 RR는 한 번만 별도 결합한다.

## 실제 선행 완료 identity

최신 선행 단위는 [PR111](https://github.com/cosmosapjw-quantum/bass_cr/pull/111)의 `CR_PHYS02_PARENT_EVENT_NATIVE25_V1`이다. 최종 게시 후 identity는 `inputs/PREDECESSOR_FINAL_RECEIPT.json`에서 읽었다. 선행 `ADMISSION.json`의 D/M null은 게시 전 preimage로 보존하며, 아래 실제 최종 값을 거기에 소급 삽입하지 않는다.

| 역할 | 실제 값 |
|---|---|
| Scientific S | `5c50071412964cb42fc06b96acf778ccd1a93e44` |
| Final document D / 새 branch baseline | `65e20e40e3c1d9e8384101017dc8940b3d09de09` |
| Central return M | `ed6a899fa87ad42fbbb3569e96779bc3af716620` |
| 실제 retained PHYS02 revision | `4ca5a90de79c8fb82a25fd9e83615bec0dfa870b` |
| Canonical source JSON SHA256 | `8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf` |
| 저장 attribution NPZ SHA256 | `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47` |
| NPZ 크기 | 233050 bytes |
| 선행 accepted primary RESULT SHA256 | `efbd18ba864982ca6436345b1d25d75ad084b3c5f77db6e3bb40186db07b4901` |
| 선행 C09 review SHA256 | `1cfab538e704664d546f7b8b8b9aaa2862842d6ba0e8127330894b605b373403` |

SOURCE는 `BASS_CR_PARENT_EVENT_SOURCE_20261028_5c5007141296.zip`, 6246339 bytes, 419 members / 418 payloads, SHA256 `b5274f243645e6340e869bc70202519822ef100018675ececbfb72a40a2e4cfb`이다. CLOSEOUT은 `BASS_CR_PARENT_EVENT_CLOSEOUT_20261028_65e20e40e3c1_ed6a899fa87a.zip`, 546116 bytes, 78 members / 77 payloads, SHA256 `a6040c987204447a036ef08a6e94d6d4ad7f0a6a77790af6a8aaac1dcac073e3`이다. 선행 영수증은 두 archive의 Dropbox·Drive original full-GET 및 전체 payload SHA/CRC R3 PASS를 기록한다. 이번 복구와 재사용의 근거는 `inputs/INPUT_MANIFEST.json` 및 보존된 recovery receipts이며, 이 문서 작성 작업이 새 provider GET을 했다고 주장하지 않는다. 봉인된 선행 archive를 재생성하지 않는다.

## 재사용 경계

선행 preparation 15/15, primary 58/58, controls 51 unique / 52 actual evaluations, independent 3450 unique accepted / 3454 actual evaluations는 해당 선행 identity와 scope로 재사용한다. 새 단위의 test count에 더하지 않는다. 선행 source-fit/projection/RR 계산은 재실행하지 않는다. 이미 저장된 `energy_eV_with_cutoff`와 `identified_A_He_m3_s2`를 새 사건 측도의 입력으로 읽는 것은 기존 fitting을 다시 하는 작업이 아니다.

PR111의 preparation 실패 3회, bounded-worker 실패 2회, original primary_v1 및 independent_v1 실패·oracle repair를 보존한다. 선행 비용 10.45384/40 CPU-s와 잔여 29.54616 NONTRANSFERABLE을 이번 40 CPU-s에 합산하거나 이월하지 않는다. PR110 24.692011/40, PR109 10.238419/20, PR107 6.988054525/30, PR108의 별도 60 CPU-s cap 및 다른 owner 예산도 별개다.

## source/state/history 고정

`direct_0p1_10`의 3200 active atoms와 별도 cutoff ghost 1개를 유지한다. ghost는 저장 binary64 0.1 eV 경계이고, E < 0.1 eV spectrum을 뜻하지 않는다. birth-energy partition은 ghost, active (0.1,1], active (1,3], active (3,10]이다. `q_j(t)=t A_j`, proper history [0, 10^10] s 밖은 unknown이다. 네 누적 prefix는 비가산이고 네 disjoint birth-time bins만 같은 사건 family에서 가산할 수 있다. 기존 RR observation-response bins와 혼동하지 않는다.

state는 조건부 frozen 100 K H1/He4 inventory `CR_LOW_BIRTH_100K_CONDITIONAL_H1_HE4_FIXED_INVENTORY_V1`이다. nH=140 m^-3는 총 H nuclei, nHe=1085/94 m^-3, xHII=xHeII=1/100, xHeIII=0, ne=2849/1880 m^-3, nb=8750/47 m^-3이다. 이는 외부 관측이 아니다. gas-rest nonrelativistic scalar, zero recoil, fixed proper-volume density, absolute V=null을 유지한다. foreign T/nb/frame/clock, target/proper729/angle/speed normalization을 새로 곱하지 않는다.

## 고정 허용 기준

| 평가 대상 | 기준 | 해석 |
|---|---|---|
| 저장 NPZ 입력 | 전체 bytes SHA256 exact match | source provenance 필수 |
| atom payload | exact rational atom-content digest | source label만으로 fixture 승격 금지 |
| marginal, 두 leg, 사건 union, species·charge·baryon 보존, sharp witness | `Fraction` exact equality | tolerance로 identity 결함을 숨기지 않음 |
| 독립 report 비교 | 계약의 relative tolerance 1e-12를 상한으로 유지; 현재 reference는 더 엄격한 exact rational equality | 기준 완화 없음 |
| 선행 attribution atom tolerance | inherited 2e-11, 재사용·재실행 없음 | 새 certified source-model error가 아님 |
| negative/nonfinite·mixed state·support 확장·중복/불완전 claim | 해당 refusal 사유와 정확히 일치 | 실제 실패는 run receipt에 보존 |

actual C, exclusive He kernel, outside partner state/energy/history/response, residual excitation, proton donor debit, actual EOS/T, full physical native25 및 global physical error는 null이다. RR와 retained photon은 별도 port이며 photon moments로 spectrum/history를 만들지 않는다. 중앙 참고 baseline은 28/88이고 이 문서 자체의 중앙 집계 효과는 0이다. 각 C-stage의 최신 중앙 값·Git 게시·이중 백업은 그 stage의 실제 preflight와 publication receipt가 우선한다.

근거: `../CONTRACT.json`, `../inputs/INPUT_MANIFEST.json`, `../inputs/PREDECESSOR_FINAL_RECEIPT.json`, `../../cr_parent_event_native25_20261028/ADMISSION.json`, `../theory/THEORY_KO.md`.
