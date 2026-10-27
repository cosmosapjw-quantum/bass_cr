# R1 — 최신 저장소·브랜치·PR 관측과 다음 CR 단위

## 결론과 기준

현재 중앙 기준은 `rei_bianchi`의 `research/orchestration-sandbox-20261022`, commit **`5abe0d19df95db730e3e33bae0373c81ba37ce89`**다. 원 DAG는 **88개 노드·17개 integration edge**이며, 최신 CR HeIII 반환이 명시한 전달물 기준 진행은 **27/88**, `current_status`가 문자 그대로 `COMPLETE`로 시작하는 노드는 **18/88**이다. 별도 REI 작업의 **32/88**은 working branch 수치이며 shared 기준에 가져오지 않는다. 이 R1 관측으로 중앙 완료 수는 증가하지 않는다.

다음 CR 단위의 중앙 parent는 **`CR_ALL_EXTERNAL_PHOTON_BARYON_SOURCE_INTERFACE`**, DAG index **15**다. 현재 상태는 `IMPLEMENTATION_VERIFIED_SCOPED_SOURCE_AND_EVENT_CONSUMER`이고, 검증된 source/event interface에 실제 평가 source/history 또는 source-qualified cascade/stopping 공급자를 연결하는 것이 다음 행위다. 원 계약은 source의 proper volume, clock, momentum measure, species/state/isotope, 에너지·운동량·입자수 정규화를 한 번씩 적용하도록 요구한다. 없는 intensity·density·isotope를 0으로 만들지 않는다.

이번 관측에서는 현재 HeIII bath와 맞는 새로운 연속 외부 주입 이력을 발견하지 못했다. root가 검토 중인 다음 범위는 **이미 저장된 HeIII pulse에 인과적인 finite-age Erlang proper-time clock을 붙여 입자수·운동에너지·잔류 photon bin 반환을 구성하는 단위**다. 이것은 이후 이론·구현·독립 검토로 판정할 후보이며, 이 R1 조사에서 실행하거나 통과 판정을 내린 결과가 아니다. 실제 continuous source history는 계속 `null`이다.

## 실제 조사 범위

연결된 owner 목록은 **51개**를 반환했고, offset 51의 다음 페이지가 **0개**인 것을 확인했다. 전체 owner inventory는 `OWNER_REPOSITORIES.private.json`에 보존하며 공개 산출물·ZIP에는 포함하지 않는다. 연구 관련 9개 repo의 branches와 open/closed PR 목록은 아래와 같이 모든 endpoint를 마지막 페이지까지 읽었다. 각 목록의 row identity는 중복이 없었다.

| 저장소 | 브랜치 | 열린 PR | 닫힌 PR |
|---|---:|---:|---:|
| bass_cr | 185 | 106 | 1 |
| rei_bianchi | 279 | 222 | 14 |
| WU088_HH | 159 | 150 | 0 |
| rec_bianchi | 157 | 104 | 34 |
| BASS_HE | 107 | 102 | 0 |
| bass | 278 | 163 | 30 |
| vigilode | 215 | 59 | 30 |
| bianchi_phase_r | 1 | 0 | 0 |
| MOSAIC-ODE | 1 | 0 | 0 |
| **합계** | **1,382** | **906** | **109** |

이 목록 관측 구간은 **2026-10-27 05:56:44.054–05:56:53.021 UTC**다. 병렬 연구가 진행 중이므로 원자적인 한 시점의 snapshot이라고 주장하지 않는다. 선택한 10개 branch ref를 **06:02:31 UTC**에 다시 확인했다. 목록 전체를 무기한 재시작하지 않고, 이후 각 노드 시작 전에 관련 HEAD·AGENTS·병렬 변경을 다시 확인한다.

전수 열람한 것은 이 9개 repo의 branch/PR **목록**이다. 모든 branch의 모든 파일, 모든 PR diff, 비공개 대화 전체를 읽었다는 뜻은 아니다. 실제 본문은 현재 권한·계약·중앙 상태와 새로 발견된 관련 frontier를 선택하여 읽었다. 대화·백업 전체 조사는 별도 담당자의 결과와 root가 통합한다. 원본 페이지별 URL·반환 수·시각·terminal 여부는 `RELATED_REPO_INVENTORY.json`에 있다.

## 유지할 CR·중앙 고정점

CR science S는 `4e72c89b714431eb4c6ae07def777bbf72a5ae4c`, 문서 D는 `ec463db0c7e5c7fb5070796071c926caa4db6445`, 열린 PR은 [bass_cr #107](https://github.com/cosmosapjw-quantum/bass_cr/pull/107)이다. 마지막 ref 확인까지 `research/cr-heiii-ground-rr-20261027`의 D는 바뀌지 않았다. source/event interface 기반 branch `research/program-expansion-20261025`도 `b11b2e9255f2b10fb5582376412e045bd1e9151c`로 유지되었다. 기존 H1 RR·C23E·He4/HeIII 성과와 이미 만들어진 M0/M1M2 closure는 재사용 대상이다.

중앙에서 다음 경로의 원문을 실제로 확보했다. 아래 경로는 모두 위 M commit 기준이다.

| 역할 | repo 내부 경로 |
|---|---|
| root 권한 | `AGENTS.md` |
| 조립·owner 범위 | `research/orchestration_expansion_20261025/authority/ROOT_SCOPE_AND_ASSEMBLY_CONTRACT.md` |
| 전체 DAG | `research/orchestration_expansion_20261025/DAG.json` |
| 현재 parent wrapper | `research/orchestration_expansion_20261025/contracts/CR_ALL_EXTERNAL_PHOTON_BARYON_SOURCE_INTERFACE.json` |
| parent 계획 | `research/orchestration_expansion_20261025/node_plans/CR_ALL_EXTERNAL_PHOTON_BARYON_SOURCE_INTERFACE.md` |
| 현재 상태 projection | `research/orchestration_expansion_20261025/status/CURRENT_STATUS.json` |
| 원 계약 pointer | `research/orchestration_expansion_20261025/authority/atomic/EXPANDED_NODE_CONTRACTS.json#/nodes/15` |
| 현재 27/88 명시 반환 | `research/orchestration_expansion_20261025/returns/CR_HEIII_GROUND_RR_20261027.json` |

[고정 중앙 wrapper](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/5abe0d19df95db730e3e33bae0373c81ba37ce89/research/orchestration_expansion_20261025/contracts/CR_ALL_EXTERNAL_PHOTON_BARYON_SOURCE_INTERFACE.json)와 [조립 계약](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/5abe0d19df95db730e3e33bae0373c81ba37ce89/research/orchestration_expansion_20261025/authority/ROOT_SCOPE_AND_ASSEMBLY_CONTRACT.md)이 다음 단위의 현재 scope 기준이다. `node_plans`의 큰 JSON block은 과거 `fc2c6044…` expansion snapshot이며, 그 아래의 scoped owner return과 현재 wrapper가 최신 상태를 명시한다. 과거 block의 `PROPOSED_EXPANDED_SCOPE`를 현재 상태로 덮어 읽지 않는다. 또한 `audit/PROGRAMME_PROGRESS_KO.md`의 87-node 서술은 과거 expansion 설명으로 남아 있다. 실제 최신 DAG 88개와 최신 반환 27/88을 사용한다.

큰 DAG는 connector에서 HTTP400(size/unsupported)으로 읽기에 실패했다. 이후 공개 raw URL을 실제 GET하여 **1,592,174 bytes**, SHA256 **`007b79e22a52c3701b9dd8a6cf8dfee62f3a7a3cb50367e56e998ece9dfec8b0`**를 확인했다. 실패와 성공 receipt를 모두 남겼다. 과학을 다시 실행한 것은 아니다.

## 새로 발견한 병렬 연구와 사용할 수 있는 범위

### REI thermal assimilation — PR237

[PR237](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/237)의 현재 head는 **`ee6746ab172f862dddfdec63b59e5e3707b59eaa`**, source science는 **`600503e559eb5763a97dad6ae6d661761bc9b02a`**다. `research/rei_expanded_event_consumer/thermal_assimilation_20261027/ADMISSION.json`과 `REPORT_KO.md`를 실제로 읽었다.

결과는 `PASS_CONDITIONAL_NATIVE_COUPLED_LOCAL_SOURCE`다. 21 species, fast count, fast energy, signed external-radiation ledger, logT의 25개 source row를 다루며 118/118 새 국소 검사를 보고한다. normalization은 reference density와 baryon density를 구분하고 eta-clock 변환을 모든 row에 적용한다. 이 source/normalization 구조는 다음 CR 반환 interface를 설계할 때 참고할 수 있다.

그러나 **`source_matched_history=false`**, fast pool은 제조 입력이며, 처방한 상수 collision rate는 **8.160348695705333e−18 s⁻¹**다. 실제 stopping provider는 없고 physical nu/uncertainty는 `null`이다. 실제 선택 배경도 **T=14919.863839279506 K**, **nb=10.669321142818111 m⁻³**, z=2.479로 현재 CR의 고정 HeIII bath와 다르다. 이 결과에서 새로운 실제 CR 연속 주입 history나 physical heating 완료를 끌어오지 않는다. working32/88은 shared27/88에 자동 합산하지 않는다.

백업 담당자가 동일 source S의 ZIP과 delivery를 발견했다. 이 조사에서는 provider 원격 ZIP을 다시 검증하지 않았으므로 producer의 backup tier와 실제 새 read-back을 혼동하지 않는다.

### REC source synthesis — R10 진행 중

`research/rec-source-synthesis-20261027`은 초기 **`eb3b390eb59a4c48b5aa2d3bec928465b9c35f2e`**에서 최종 ref 확인 때 **`f9d2e979939949a9da8c4bcd04d7d83390bd3724`**로 한 commit 전진했다. 초기 `RESEARCH_CONTRACT.md`, `CODING_CONTRACT.json`, `SOURCE_SYNTHESIS_KO.md`와 새 `THEORY_HANDOFF_KO.md`를 읽었다. 추가 commit은 R10 이론 인계와 복구·stage receipt이며 기존 연구 계약을 바꾸지 않았다.

두 단위는 HD 원자료의 준위·주파수 불일치 진단과 실제 native H5 piecewise-linear history의 knot-crossing remainder다. 원래 35 Hz 비교의 7/8 실패를 보존한다. HD 8개 선×50/100/200 K의 24개 진단, history 1,240 retiming·313 chord·12 causal skip은 **향후 runner가 확인할 수**이지 이 pin에서 실행 통과한 결과가 아니다. 이론의 R6 독립 유도와 R7 기호 검산은 handoff에 기록돼 있다.

H5 history는 z≈1100 계열이며 현재 CR HeIII source history가 아니다. 표현된 history에 대한 정확한 remainder 정리가 physical tube·defect·stability 입력을 만들어 주지 않는다. **physical epsilon `null`, 물리 coverage 0/313, L4 false**를 그대로 둔다. REC의 개별 CPU 한도는 이 단위의 예산이며 CR에 이전하지 않는다.

### WU molecular R4 — source recovery checkpoint

`research/provider-registry-20261025`는 기존 `bfdeed676617c8b75ed81ac5e79e800fa69f83db`에서 초기 **`94ba73928d2e2055cf07ad8801f7e83ccb827818`**, 최종 **`e9276ea2ba8af2d73197a6852931fcafbf39ddf5`**로 전진했다. 초기 최신 AGENTS·R4 계약과 마지막 S02 R2/C2 checkpoint를 읽었다. 마지막 delta는 AGENTS나 CONTRACT를 수정하지 않았다.

현재 R4는 LiH/HD 원문 4개·공급자 변형 6개·native rate cell 77개를 고정하여 회수한 단계다. local WU DAG는 **7/24**이고 source 회수 두 child를 닫았다. native fit 실제 평가, 새 compiler, 새 Wolfram 계산은 이 checkpoint에서 실행하지 않았다. 이전 검토의 exact source packet은 재사용하지만 소실된 review serialization은 별도 reconstruction receipt로 구분한다.

Bennett, Bovino, Honvault, Gonzalez-Lezana 계열의 state-lift 및 isotope/species projection은 향후 molecular 공급 범위다. 405 K 같은 fit scale을 반응 Q로 바꾸지 않는다. source가 제공하지 않는 covariance·최종 state population·runtime consumer는 `null`이다. 6개 변형은 inactive candidate이며 rate/Q/energy partition 활성화나 CR 새 연속 source history가 아니다. 기존 원 19 target/28 direction 범위는 유지한다. PHYS91 잔여 0과 global 잔여 `null`도 유지한다.

### BASS DL2 및 다른 공급자

[BASS PR193](https://github.com/cosmosapjw-quantum/bass/pull/193)의 head는 **`e3e829903294f437373369420b1dff95f6592e85`**다. 이 조사자는 공개 PR 본문을 읽었고, 백업 담당자는 실제 archived report를 읽었다. 범위는 cold/rest Thomson bolometric polarized source dictionary다. electron clock `chi=∫ne sigmaT c dt_e`와 source/memory dictionary는 finite-frequency 실제 spectrum, tilted normal clock history, recoil 또는 전체 Einstein history의 공급을 뜻하지 않는다. 현재 CR proper-time injection history로 바로 쓰지 않는다.

REC 기존 공급 branch는 **`4a8e541030ee2cbd02e26ba671083b705d309d49`**, HE는 **`ac6042a6b0610b09d0576538767ee0299389a5eb`**로 유지되었다. HE의 조건부 caloric 범위와 Tstar 50–50000 K, 물리 공급 미승인 경계는 그대로 둔다. VIGILODE는 별도 solver/client 계약을 갖고 있으므로 metadata 또는 delivery 발견만으로 coupled physical execution을 인정하지 않는다. REI PR236 `ee94bef85b56d879dc38f184856a5c613575e9e1`도 별도 작업으로 유지한다.

## 다음 단위에서 적용할 소유권·게이트·예산

현재 중앙 조립 계약은 WU의 미시 species/reaction, REC의 상태·history, HE의 충돌·thermal, CR의 외부분포·주입·cascade·stopping, BASS의 geometry, VIGILODE의 적분, REI의 scenario 조립 역할을 구분한다. 하나의 physical event에는 하나의 microscopic owner와 하나의 transport consumer만 둔다. WU/REC/HE의 source support·유효 범위·isotope mapping을 CR에서 재명명하거나 넓히지 않는다.

관측한 목록과 선택한 최신 계약에서 CR proper-time injection 단위와 같은 추가 active owner는 발견하지 못했다. 이는 모든 미게시 대화의 부재를 증명하는 명제가 아니다. source 담당자가 확인한 과거 `Qe=tA` actual proper-volume history는 **T=100 K, nH=140 m⁻³, T0=1e10 s, z=8** 조건이다. 현재 **T=10000 K** HeIII chain에 그 이력을 이식하지 않는다. 기존 finite-age p/R/S 및 C2 convolution 결과도 새로운 결과로 다시 세지 않는다.

다음 단위는 source-shape provenance, pulse normalization, proper-time origin, baryon/reference-density 변환의 입력 유무, retained photon-bin 의미를 분리하여 고정해야 한다. 실제 time history나 nb가 없으면 `null`과 conditional scope를 유지한다. N4/N5는 partial, N6/N7은 predecessor gate다. caloric partition 또는 energy bookkeeping을 physical heating 완료로 승격하지 않는다. global physical completion·global error bound는 `null`, L4는 false다.

과거 `UNKNOWN_NO_ACK`는 현재 새 ACK로 소급해서 고치지 않는다. budget도 초기화하지 않는다. 중앙 원 계약의 PHYS91 잔여 0, CR105/C23E의 별도 lineage 기록과 overlap 미확정, global 남은 CPU·금액 `null`을 보존한다. WU·REC의 새 한도는 각각의 단위에 속한다. 이 R1 조사의 scientific run·역사 science replay·remote mutation은 각각 **0**이며, metadata 처리 CPU는 측정하지 않았으므로 **0이라고 쓰지 않는다**.

## 권한 읽기와 산출물 상태

자기 CR D, 중앙 M, HE, REI237의 root AGENTS 원문을 읽었다. WU 최신 root AGENTS는 exact snapshot을 확보하고 새 우선순위 delta를 읽었으며 마지막 e927 delta에서 추가 변경이 없음을 확인했다. REC base·REC synthesis·BASS DL2·VIGILODE에서 요청한 root AGENTS는 실제 HTTP404였고 다른 branch의 파일로 대체하지 않았다. 중앙·CR의 가까운 `research/AGENTS.md`와 해당 단위의 AGENTS 경로도 실제404였으며 결과를 보존했다.

`INVENTORY_SUMMARY.json`은 완료된 metadata 조사와 현재 제한을 기계가 읽을 수 있게 정리한다. `CENTRAL_PARENT_EXCERPT.json`은 exact DAG/status에서 parent를 투영한 자료다. `SELECTED_SOURCE_MANIFEST.json`은 실제 읽은 파일의 pin·URL·byte 수·SHA256을 담는다. 최신 source 두 head가 이동한 delta는 `WU_FINAL_DELTA.json`, `REC_FINAL_DELTA.json`에 있다. **이 조사자는 게시·업로드를 하지 않았다. root가 R1 checkpoint를 게시하고 이중 백업할 때 공개 요약과 필요한 관련 증거만 포함한다.**

R1 종료 시 중앙 표시: **27/88**. 다음 전체 이론·코딩 루프의 완료 여부는 이 보고서에서 주장하지 않는다.
