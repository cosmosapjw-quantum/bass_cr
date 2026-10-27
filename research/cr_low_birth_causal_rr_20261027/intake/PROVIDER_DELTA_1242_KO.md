# 공급자 추가 관측 — WU S09와 HE photon05

이 부록은 앞선 `PROVIDER_SURVEY_KO.md`의 시점별 관측을 보존하면서, 전체 Dropbox 목록에서 발견한 HE의 새 로컬 산출물과 이후 WU 게시를 추가한다. HE의 원격 programme branch가 ac6042라는 사실만으로 모든 최신 연구가 같다고 판단하지 않는다. 공급자 원본을 읽고 byte identity를 검사했으며 과학 코드 실행은 0이다.

## WU: 원격 S09의 새 채택, 물리 소비자 조건 유지

2026-10-27 12:42:47.293 UTC에 실제 원격 `research/provider-registry-20261025` HEAD를 다시 읽어 `7168ad4807dd1e02aef852bcf428df75b222f0de`를 확인했다. 이전 관측 b81c668 대비 6 commits 앞서 있다. [고정 scientific admission](https://github.com/cosmosapjw-quantum/WU088_HH/blob/7168ad4807dd1e02aef852bcf428df75b222f0de/research/provider_registry_molecular_r6_20261027/SCIENTIFIC_ADMISSION.json)을 직접 읽었고, 최신 AGENTS의 SHA256은 `aa819204f62805caad7f1689fe64a07c4876d88d73332cfe2b285a431cd044a0`로 이전 관측과 같다.

새 채택은 declared literal 100 K HD + para-H2, J=0..8, v=UNSPECIFIED, 9 downward edge의 유한 graph에 대한 exact interval Gibbs 및 lower-polynomial/forced-block certificate다. 주 계산 76 checks/failure0, 독립 Decimal250 등 대조 109 checks/mismatch0, Wolfram 1 call/23 zero residuals가 기록되어 있다. Wolfram warning은 해결되지 않은 채 보존되며 단독 증명이 아니다. 과학 payload SHA256은 `796f399586916847844c7040082a1dce308035d1bce74bf805246574f98b94b4`다.

이 시점 workflow는 **18/20**, scoped DAG는 **13/28**이다. R10/C10은 PENDING이다. GL2022 destruction, named physical consumer, physical density는 여전히 null이고 clock은 \(\tau=n_{\rm coll}(10^{-11}\,\mathrm{cm^3/s})t\)로서 \(n_{\rm coll}\) 미결속이다. HH_R10=OFF, production=NOT_ISSUED, L4=false, central/physical delta0, PHYS91 remaining[0,0,0] 및 global remaining/CPU null을 유지한다. 원문 literal의 outward 산술은 실제 측정 불확도 인증이 아니다.

새 allowance의 primary/reference/Wolfram **실행 횟수 잔여는 각각 0**이다. 기록된 process CPU at finalize는 primary0.791299421 s, reference0.822867308 s, Wolfram kernel0.286018 s다. 각 owner의 60/60 CPU 및 30 s CAS 제한을 CR 예산으로 이전하지 않는다. S08은 566,438 bytes, 83 payload members, SHA256 `09b0d2c7ba6f4a703caed0afd827ba7881678cf2aed7ec1d3307d860f9de9e0d`의 양쪽 original-byte readback PASS 영수증을 실제로 읽었다. 이 부록에서 WU ZIP을 재다운로드한 것은 아니다. S09 이후 최종 전달을 앞당겨 인증하지 않는다. 이 pin의 `followup/NEXT_INPUT_CONTRACT.json`은 실제 404였으며, admission의 next 경로를 접근 완료로 바꾸지 않는다.

## HE: 원격 분기와 별개의 실제 로컬 S05/D05

공개 ref 목록과 GitHub는 ac6042 원격 programme HEAD를 유지한다. 직접 commit 조회 422 및 photon05 branch/commit 검색의 빈 결과는 저장소의 미게시 상태와 일치한다. Dropbox 전달 원본의 [로컬 기록 사본](raw/HE_D05_delivery_PUBLICATION.json)을 읽어, 실제 로컬 S05=`251c6baa6c3359b1d6997dbce51cea65500b53d6`, tree=`80c880cc3881e1e539156d8e077d443f7bd945a5`, D05=`4db5ce7297a7ded4624b93721873aacc9b4ebf30`, tree=`0716e170bdd6caf4d8995daae602d330e1cf8d33`를 확인했다. 이것을 존재하지 않는 원격 commit URL이나 현재 branch HEAD로 인용하지 않는다.

원본 publication은 동일 create_tree 요청의 다섯 번째 시도가 `user rejected MCP tool call`로 끝났고 추가 사유는 null이라고 기록한다. 이후 GitHub writes와 대체 게시 경로는 0이다. Source/central publication은 둘 다 false이며, 중앙 16-file 후보는 과거 M1a38f94 기반의 **로컬 후보**다. 현재 중앙 HEAD 또는 이미 합산할 완료 수가 아니다. 이 조사는 해당 차단을 우회하거나 HE·중앙을 수정하지 않았다.

### 실제 소스와 유효 범위

`MODEL_CONTRACT.json`의 과정은 photon + stationary **bare ground-state alpha → 두 bare ground-state deuteron**이다. NIST2022 질량 중앙값에 조건부이며 covariance는 null이다. EXFOR M0475002의 에너지 **213/258/330 MeV**와 CM polar angle **46/61/73/87°**의 12 native 좌표만 사용한다. 대표 azimuth phi=0은 명시적 예제이며 관측된 방위각 분포가 아니다. DCS/ERR-S는 native NB/SR 그대로 보존하고 event flux·전각 law·에너지/각도 보간으로 바꾸지 않는다.

24-method numerical reference는 PASS, CPU0.241060162 s다. Plot은 exit0 및 파일 생성과 별도로 CPU4.40726504 s가 4 s cap을 넘겨 **FAIL_CPU_CAP_EXCEEDED**다. 원인 미확정, rerender0, budget transfer0이며 unit 전체가 clean PASS가 아니다. Local DAG는 **4 complete + 1 partial + 3 physical open / 8**, workflow PARTIAL이다. HE101 C8 PARTIAL_EXPORT19/20, reserve0, 원 PASS/FAIL/FAIL도 보존한다.

실제 액체-He 전자 spectator, target/beam/acceptance response, 동일입자 event normalization, 전체 angular law, actual encounter flux, global species IDs 및 named deposition이 미결속이다. Adapter의 flux는 caller가 주는 m^-3 s^-1 값이며 native 예제의 flux0은 물리 rate0이 아니다. **이 source는 실제 유한 proper-time history, 같은 상태의 explicit nb, PHYS02 100 K recipient 또는 그 RR operator를 제공하지 않는다.** 상대론적 수백 MeV 핵반응 per-event contract를 CR의 0.1–10 eV scalar 전자 계약에 접합하지 않는다.

단일 에너지 소유권은 photon loss + population rest witness + daughter kinetic이다. Nuclear binding을 독립 항으로 다시 더하지 않으며 material count+1을 thermal count로 승격하지 않는다. Gamma_thermal/Cv/species_heating/thermal_deposition=null, birthpool=UNASSIGNED, physical_rate/provider/global_consumer admissionfalse, activationfalse, L4false, global physical completionnull이다.

### 새로 수행한 실제 byte 확인

| 원본 | 실제 전체 GET | 현재 검증 |
|---|---|---|
| `BASS_HE_HE_EXP_PHOTON05_SOURCE_20261027_251c6baa.zip` | Dropbox `id:BSpOijBcT10AAAAAAEDHdw`, 2026-10-27 12:41:32.213522 UTC, 20,425,864 bytes, SHA256 `d3b574ec5d4b2657d63cc23afd221d1ce6aec59b79192676ffb54fb43af26a90` | 434 members CRC PASS; manifest433 members bytes/SHA256 및 선언된431 Git blob 일치 |
| `BASS_HE_HE_EXP_PHOTON05_DELIVERY_20261027_4db5ce72.zip` | Dropbox `id:BSpOijBcT10AAAAAAEDHew`, 2026-10-27 12:40:17.671565 UTC, 2,203,799 bytes, SHA256 `25ac28965be174457a1b5e57f73f387185fc0674c9c152172a845906c206883a` | 35 members CRC PASS; manifest34 members bytes/SHA256 및 선언된 Git blob 일치 |

원 공급자의 source dual ACK 및 metadata ID/name/size 기록과 이번 **Dropbox 한쪽의 전체 GET**을 구별한다. 이번 조사에서 Drive 원본 GET은 하지 않았으므로 새 dual R3라고 부르지 않는다. Source bundle의 ac6042 prerequisite와 251c6baa HEAD header를 읽었으나 Git 객체를 import하거나 commit object audit를 새로 실행하지 않았다. 원본 HE 기록의 remote-full-download=false는 당시 사실로 보존한다.

## 다음 CR slice에 미치는 영향

새 HE 소스·WU 인증은 실제 진행으로 기록하지만, 둘 다 PHYS02의 같은 물리 상태와 실제 finite history 입력을 대체하지 않는다. 이미 제안된 actual lowbirth q=tA의 유한 horizon에서, 별도 새 예산과 허용치로 100 K Coulomb + ground HII/HeII RR를 구성하는 좁은 목표를 유지할 수 있다. Conditional H1/He4-only nb를 채택할 경우 명시적 새 가정과 source inventory 유도를 따로 결속해야 하며, 이전 CR proper unit의 nb=null을 소급 수정하지 않는다.

중앙 declared27/88, 88 nodes/17 edges, 기존 CR 및 B3h return의 보존을 전제로 이 조사에 의한 완료 효과는 0이다. 현재 중앙 fresh HEAD는 root의 pre-node 관측으로 결정한다. 개인 대화 전체 검색 unavailable, Drive partial inventory 및 모든 historical UNKNOWN_NO_ACK는 그대로다. 다운로드·문서화 비용은 계측하지 않았으며 0으로 쓰지 않는다.
