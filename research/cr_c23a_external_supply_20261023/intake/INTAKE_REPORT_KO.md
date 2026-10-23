# C23A 최신 AVAILABLE-surface intake 및 재사용 결정

작성 기준: 2026-10-23 KST. 담당 범위는 읽기 전용 intake다. 새 ODE, 과거 계산 재실행, NCP 작업, 원격 쓰기는 모두 **0**이다. 이번 자료는 외부 연구자의 수치 결과를 새 독립 계산으로 승격하지 않는다.

## 1. 최신 권위와 실제 조사 범위

현재 권위 저장소의 PR96은 `research/cr-c21o-hheli-z2-sandbox-20261021`, head **ba39fc75521aa18705ec832d789e50dd5c6565bc**이며 open/draft/unmerged이다. PR의 마지막 갱신은 2026-10-22T17:56:41Z다. 이 head가 복구한 C22D 게시 상태이며, 사용자가 제공한 C21O science C / historical D / recovery R을 소급해 같은 identity로 바꾸지 않는다. 근거: [PR96](https://github.com/cosmosapjw-quantum/bass_cr/pull/96), `PR96_FULL.json`.

7개 알려진 저장소의 **REST head refs 1,278개**를 수집했다. 복구한 C22D의 1,271개와 비교하면 **추가 7, tip 변경 6, 삭제 0**이다. 실제 수집은 2026-10-22T22:28 UTC 부근이며 저장소별 시작·종료 시각을 `API_LIVE_REFS.json`에 기록했다. 앞선 보고서의 “advertised heads” 표현은 정확한 절차와 달랐다. 이번과 기준 파일의 실제 방법은 **GET /git/matching-refs/heads/**이며 Git-wire advertisement를 관찰했다는 뜻이 아니다. ref와 SHA identity는 그대로 유효하다. 기준 파일 SHA256는 `efed48b14691a06b9e058f63e70bed963c085c6e7b81eee52bb47a4c222a3c6e`다.

| 저장소 | 기준 → 현재 refs | 추가 | tip 변경 | 삭제 |
|---|---:|---:|---:|---:|
| bass_cr | 175 → 175 | 0 | 1 | 0 |
| rei_bianchi | 263 → 263 | 0 | 2 | 0 |
| bass | 266 → 266 | 0 | 0 | 0 |
| BASS_HE | 92 → 94 | 2 | 1 | 0 |
| WU088_HH | 145 → 146 | 1 | 1 | 0 |
| rec_bianchi | 141 → 143 | 2 | 0 | 0 |
| vigilode | 189 → 191 | 2 | 1 | 0 |
| 합계 | 1,271 → 1,278 | 7 | 6 | 0 |

이는 **알려진 7개 저장소가 반환한 head 집합의 전수 조사**다. 조직의 모든 저장소, 비공개/미노출 저장소 또는 모든 과거 파일의 전수 감사는 아니다. 관련 변경 commit/tree를 좁혀 읽고, 본체 연구와 prior CR 재사용에 필요한 **선택 text 74개, 830,327 bytes**를 취득했다. 각각 tree의 크기·Git blob SHA1과 로컬 SHA256를 확인했다. 전체 bytes 취득과 특정 물리 주장에 대한 의미 검토를 구별한다. 외부 raw trajectory의 새 독립 감사는 **0**이다. 전체 binding은 `ALL_SELECTED_TEXT_BINDINGS.json`이다.

## 2. PR와 최신 외부 실행의 상태

아래는 실제 GitHub API에서 읽은 PR 상태다. 모두 open/draft/unmerged이며 병합·production 승인으로 해석하지 않는다.

| PR | 실제 현재 head | 읽은 결과의 경계 |
|---|---|---|
| bass_cr 96 | ba39fc75521aa18705ec832d789e50dd5c6565bc | C22D까지의 권위 게시 상태 |
| REI 219 | 6a12f3865d9ea427c1391c41caed8bb7cb7ec00d | 이후 DD/18-family passive nuclear 결과가 추가된 scoped 연구 |
| REI 220 | 8be7533cc97b3302bf42608699d6e8313ed6af8a | compact33 125grid+2cancel+2full62 oracle |
| REI 221 | 9620e1fcc4bdda76e0311206f614234926600381 | local isotope/source adapter 및 local thermal/beta flow |
| REI 222 | b4b5d289aaad9ef167f683f19418b0ff87ed8425 | 여러 저장소의 작은 kernel 통합 및 저장 경로 D10 후처리 |
| BASS_HE 85 | 16a424b7290f484c57e97c8ed74f81e6d2043782 | owner가 392nominal+2L24와 이후 recovery 범위를 기록 |
| BASS 180 | 574c3af93810122af0a7977e00e34195e5251a09 | REI220과 같은 compact33 연구의 mirror; bass_cr180이 아님 |

근거: `CURRENT_PR_INSPECTION.json`, `PR_HEAD_SUMMARY.json`. URL은 각 저장소의 /pull/번호다. PR 설명은 owner 보고이며, 이번 intake에서 모든 원 NPZ를 다시 읽었다는 뜻이 아니다.

HE85의 앞선 미완료 상태와 이후 완료 보고를 시간순으로 함께 보존한다. 원 NPZ 상실 뒤 identity를 맞추어 다시 계산한 recovery는 **원 raw bytes 복원**과 다르다. REI219도 과거 미완료 campaign 기록을 지우지 않고, 이후 완료한 조건부 passive network와 production 의존성을 구분한다. REI220/BASS180 최초 127개 결과의 JSON 실패·재적분 이력은 유지한다. 기존 대표 2쌍/raw4개 비교의 PASS_SCOPED를 전체127raw 새 감사로 확대하지 않는다.

현재 실행 중인 외부 host의 process, lease, NCP queue는 이 intake에서 관찰하지 않았다: **UNOBSERVED**. 완료 기록을 읽은 사실과 지금 외부 자원이 유휴라는 주장은 서로 다르다. 새 실행 전 자원·lease 판단은 root의 별도 gate다.

## 3. 원자·핵·열·stress 자료의 채택 범위

### 3.1 HH81: finite-support atomic hazard 계약

HH81 새 head는 **7f54d6b7be4e6b82fb1ec9b2d8d781f8f9dea863**다. `hh_phys81_atomic_nuclear_source_contract_20261023`의 CONTRACT, theory, DAG, STAGE_STATUS를 실제로 읽었다. 상태는 S0/R1 진행, 새로운 finite-CI parcel **NOT_RUN**이다.

H1의 확보된 에너지 창, He4 24.6–60 eV, Li7 6–15 eV를 별개 provider로 다룬다. He3/Li6로 자동 이식하지 않는다. residual excited-channel threshold가 현재 에너지 창 밖이라는 주장과 총단면적의 모든 에너지에서 최종 이온상태를 알 수 있다는 주장은 다르다. chemical binding energy와 source support의 하단을 따로 둔다.

고정 체적·공통 T·명시된 neutral CI만의 H/He/Li parcel에서 hazard 변수 3개로 population과 열을 복원하는 7→3 대수 축약, 그리고 rank≤2 Jacobian 구조는 재사용 가능한 **계약/유도**다. 실제 새 실행, 전체 혼합물 채택, 상대 속도 변화의 측정 speedup은 아니다. PI/RR/CX·stopping·nuclear deposition이 들어오면 동일 invariant manifold를 다시 확인해야 한다.

### 3.2 HE36 및 HE35: moment owner를 분리한다

HE36 head **76f4a8d03d2eb1a9c8e6ae4522f3b5c9614fff5b**의 계약은 common bulk/common T, 두 distinct species, infinitesimal Grad-STF 상태의 reactive loss다. 필요한 세 rate moment는 α=〈K〉, β=〈E_rel K〉, γ=〈E_rel²K〉다. 현재 상태는 **R1 계약**이며 prospective test tolerances를 이미 수행한 결과로 읽지 않는다.

CCC 전자–정지표적의 lab energy를 일반 유한질량 pair의 relative energy로 바꾸어 쓰면 안 된다. 생성 입자의 momentum/second moment, 광자 및 chemical/thermal reservoir의 energy owner가 없으면 reactive gain tensor는 닫히지 않는다. 등방 photon도 anisotropic parent removal의 STF source를 자동 0으로 만들지 않는다.

HE35 head **96338b7d3c04b18e31a080e56b34985d31921104**는 caller-supplied isotropic pseudo-Maxwell κ에 대한 finite-mass pressure exchange를 구현했다. owner는 baseline100검사와 별도의 extreme-mass-ratio 수정 검사를 구별한다. 최종 소스로 baseline100개를 모두 재실행했다고 하지 않는다. 실제 H/He differential transport 데이터, reactive gain, cosmological feedback는 남는다. 이 모듈을 원자 가스의 실제 anisotropic stress source로 바로 켜지 않는다.

### 3.3 REI221: 독립 isotope 상태를 보존하는 준비된 코드

`rei_coupled_isotope_sandbox_20261022`의 실제 `code/atomic.py`, `code/local.py`, 실행 계약, 구현 문서, 보고서를 확보했다. 원자부는 21개 독립 abundance를 유지하면서 H/He/Li의 2/3/4차원 electronic block을 공유한다. frozen T/UV/nB의 PI+RR/DR와 전자 피드백 rank-one Jacobian, 알려진 exponential-midpoint 방법을 구현했다. 알려진 방법 자체의 신규성을 주장하지 않는다.

owner의 156 baseline + 별도2 source-onset 검증은 조건부 국소 모듈 범위다. matrix rank 축약은 정확하나, 이 Python21 환경에서는 guarded structured solve median 1010.487 μs가 dense298.308 μs보다 느렸다. 연산량 감소를 실행 속도 향상으로 바꾸어 적지 않는다.

local.py는 이미 **resolved channel 계수, 명시적 energy ledger, 전하·baryon 보존, 정확한 0에서의 source derivative, absent/support-zero/zero-reactant/underflow 구별**을 제공한다. branching probability와 parent metadata를 조용히 무시하지 않고 caller가 먼저 분해하도록 거절한다. 실제 provider 계수와 에너지 분배를 공급해야 한다.

별도 `rei_coupled_local_flow_20261022`의 pure-H Case-A thermal orbit와 isothermal neutron-beta/H-RR split/Bessel reference도 기존 구성이다. 두 물리 모형을 하나의 coupled beta-thermal history로 합치지 않는다. 103 baseline과96 timing guards는199개의 물리 사례가 아니다.

### 3.4 핵반응 18-family는 물리 조건을 붙여서 재사용한다

`rei_full_nuclear_source_intake_20261022/PROVIDER_CODE_INTAKE.md`와 `rei_tritium_production_audit_20261022`의 계약·decision을 읽었다. 16 supplied labels는13개 family로 중복을 제거하고5closure를 더해18family이며, owner는 **all-bare, instant-thermalization, passive reservoir** 조건으로82저장배경을 분석했다. 이는 온도·전자·복사에 feedback하는 full network가 아니다.

cold DD의 constant S0를100–10000 K Gamow 영역까지 연장하는 것은 명시된 conditional extrapolation이다. thermal neutron p(n,γ)D 및 He3(n,p)T의2200m/s anchors와1/v continuation은 DD에서 생기는 약2.45MeV neutron의 rate/thermalization 공급자가 아니다. Li6 total absorption을 channel-resolved nα로 동일시하는 부분도 근사로 남긴다. β-decay neutrino, fast daughter stopping, 초기 product charge와 energy deposition을 별도로 소유해야 한다.

owner가 밝힌 이전 trapezoid 실패→log-linear repair, event balance와 net stock 구별도 보존한다. 작은 gross-budget residual은 미량 stock의 상대 오차나 실제 nuclear model accuracy를 대신하지 않는다. 새 source 공급자가 없는 채널을 수치0으로 채우지 않는다.

### 3.5 REC의 Compton 두 계열은 서로 다른 실행이다

REC124 **e6ecef7624e39bee66b39e09d99fe355f76e2eae**는 5–200eV/full63/logT restart8개, REC125 **b28b387fecd6cc71fddb98e95f336eba5f8a647f**는5–60eV/compact34 중심의 새8개 전체 z20→2 경로다. 두 cohort의 source·coordinate·saved-time 범위를 합치지 않는다. 이번 intake의 원시 재적분은0이다.

THERM02는 6개 electronic Mao loss factor를13isotope RR channels에 mapping한 **donor rate × Mao factor hybrid**다. thermal coordinate w=(3/2)ηT는 particle-number 변화의 heat capacity를 유지한다. actual-hot grey Compton과 별도 Planck reference는 선택 가능한 다른 모델이며 더해서 하나로 만들지 않는다. external UV의 실제 GL4 node/flux moment를 재사용하는 것은 적절하나5–200eV bin-center를5–60eV provider에 씌우면 안 된다.

Gas, external UV bath, CMB/reference bath, escaped photon 장부의 국소 합0은 유용한 코드 계약이다. opposite bath debit은 실제 radiation hierarchy/Einstein source의 동적 backreaction이 아니다. grey Uγ만으로 recoil/induced spectral moment를 정할 수 없다. Li resonance final-state/charge/energy partition은 **MISSING_EXACT_INPUT**, full physical closure와 production은 **HOLD**다.

### 3.6 VigilODE

추가 nonstiff DOPRI5와 coupled-stage adoption handoff를 actual text로 읽었다. 전자는 명시적 opt-in forward identity-mass 경로이며 automatic stiffness detection/method switching, events, dense output을 공급하지 않는다. 후자의 ConditionalL2는 명시된 가정 아래 f64 estimate다. 어느 쪽도 기존 **P02 C6 FAIL**을 해결했다고 하지 않는다. benchmark/source/report head도 구분한다. 이 intake에서 compiler, solver, benchmark는 실행하지 않았다.

## 4. prior CR에서 이미 완료한 것을 중복 구현하지 않는다

현재 ba39fc7 tree에서 2026-10-12/13/14/15의 CR 연구 자료27개를 추가 확보했다. 역사적 handoff의 READY만 읽고 지금도 미완료라고 결론내리면 안 된다.

| 과거 단위 | 재사용할 결과 | 현재 새 적용에 남는 일 |
|---|---|---|
| cr_source_binding_20261012 | fixed-bath Qe=tA의 SI normalization, source birth별 heat, total/active/thermal 전자와 cutoff energy/count ledger | 새 실제 source/time/bath/initial stock와 observable budget 결속 |
| cr_kernel_cutoff_20261013 | positive full-BED H/He paired event, thermal cutoff EOS, finite branch 조건 | 아래 successor를 먼저 확인 |
| cr_branch_geometry_20261013 | coupled branch endpoint, massive Bianchi momentum, 실제 moved-energy H/He event rebind, positive projection | 새 저장 geometry·energy support·receiver 적용을 명시 |
| cr_source_bound_geometry_20261013 | full-sharing angular/energy certificate의 archive entrypoint | full ZIP bytes는 이번에 미취득 |
| cr_geometry_temporal_20261014 | moving-coordinate term, massive work, stopping surrogate와 source-matched Thomson interval의 archive entrypoint | 100000s budget 실패 및 successor primary ionization 복원 의무 유지 |
| cr_c13_transport_20261015 | source-born photon cohorts의 방향별 redshift/opacity/positive chemistry와 ledger | photon 모형이며 massive proton/CR model로 혼용 금지; gas temporal convergence HOLD |

실제로 재사용할 구현 경로는 다음이다.

- `cr_branch_geometry_20261013/geometry_kernel_rebind.py`: `stable_kinetic_eV`, `momentum_from_kinetic_eV`, generic-mass `bianchi_pushforward(atoms, scale_before, scale_after, mass_si=...)`. Orthonormal momentum, comoving counts, supplied endpoint scale factors, signed geometry work를 사용한다.
- `cr_phys01_20261010/src/injection.py`: proton mass의 stable kinetic conversion과 constant-H,s exact characteristic. MD14 source에는 z≤8의 명시적 fit-use gate가 있으므로 z20까지 무조건 외삽하지 않는다.
- `cr_kernel_cutoff_20261013/kernel_event_adapter.py` 및 `thermal_cutoff_solver.py`: 실제 event/cutoff reference. 새 C22D geometry에 이 코드를 결속하면 “기존 정확 map의 새 입력 적용”이지 새 propagator 유도가 아니다.

고전적인 endpoint 식 pᵢ⁺=(aᵢ⁻/aᵢ⁺)pᵢ⁻, massive mass shell, stable kinetic conversion은 이미 유도·구현되어 있다. geometry 이후 actual kernel rebind도 BG5–BG7에서 끝났다. 다만 branch crossing, 모든 sharing family의 time coupling, 실제 cosmological source 소비자와의 결합은 각각 해당 후속 DAG와 source contract를 확인해야 한다.

Source-bound geometry/temporal의 현재 repo에는 recovery entrypoint만 있다. 글에서 읽은 ZIP hash/Drive/Dropbox ACK는 **역사적 owner receipt**이고 이번 whole-byte readback이 아니다. 원 보고서의 conditional angular certificate 또는 internal0.001K comparison budget을 physical global error bound로 바꾸지 않는다. 원 temporal owner는50000s 통과와100000s 초과를 함께 보존한다. F/HOLD, G/BLOCKED, PHYS02_DELAY/OPEN 등 역사적 독립 gate는 그대로다.

## 5. 대화·백업본 조사

### 대화

personal_context 도구는 “Personal context is unavailable for this conversation.”를 반환했다. 전체 타 대화 스레드는 **UNAVAILABLE**로 기록했다. 사용자 제공 handoff나 검색 snippet을 full transcript authority라고 부르지 않는다. 최초 핵반응 network PNG도 확보하지 못했고 읽었다고 주장하지 않는다.

### Library

2026-10-22T14:40Z 이후 modified-filter, recursive list가21개를 반환했고 next cursor는 없었다. 이 query 범위는 완전하나 전체 과거 Library 목록이라는 뜻은 아니다. 최신 `rei_bianchi_IGM_progress_20261022_2200_KO.pdf`(libfile_7107dcaf010c81918ba62baae4d7c3ba,154643bytes)의 추출 text11쪽과 `CLOSURE_RECEIPT.json`(libfile_d3d52ac49e60819196321a48939c2ae5,6328bytes)의 text를 실제 읽었다. PDF image/figure visual audit는 하지 않았다.

C22D main ZIP, authority, terminal receipt의 metadata도 확인했다. root는 C22D285payload의 SHA/CRC 복원을 완료했다고 알려왔으며, 이 agent는 그 복원을 반복하지 않았다. ORCHESTRATION23 S0/S1/S2의 owner receipt는 stable IDs/size와 source archive identity를 제공하나 remote-byte GET=NOT_RUN인 구간을 유지한다. source receipt를 읽은 사실을 이번 independently verified backup으로 바꾸지 않는다.

### Dropbox

최초 최근파일 검색은 요청한 date/max-results 의미와 달리 오래된100개를 반환했다. 따라서 그 응답으로 최근 파일 부재를 주장하지 않았다. 정확한 dossier 폴더 `/BASS_DERIVATION_DOSSIERS_20260912/bass_cr`의 direct children을 다시 읽어59개, has_more=false를 확인했다.

C22D main ZIP의 metadata는 id:BSpOijBcT10AAAAAAD_kQQ /48727596bytes, authority는 id:BSpOijBcT10AAAAAAD_kpQ /44254bytes, terminal receipt는 id:BSpOijBcT10AAAAAAD_k9g /11336bytes다. 이 agent의 Dropbox byte re-download는 **NOT_RUN**이다.

### Drive

recent BASS native-document 검색은 HE33의4개 문서를 반환했다. C22D/ORCHESTRATION23/C21O_RECOVERY exact-name 조건 검색은0개였다. 이는 그 검색의 결과이며 원격에 파일이 존재하지 않는다는 증거가 아니다. 별도 owner receipt에 기록된 ORCHESTRATION23 Drive ACK를 이0검색으로 취소하지 않는다. 사용자 C21O 원 main UNKNOWN_NO_ACK, 원 document NOT_RUN, recovery NOT_ATTEMPTED 및 Drive 보존 확인 **OPEN**을 임의로 완료하지 않는다. 삼중백업 완료 주장은 하지 않는다.

## 6. 재사용 license와 보존 경계

REI/REC/VigilODE의 현재 선택 LICENSE는 같은 MIT text/Git blob이며 소프트웨어 사본에 notice를 유지한다. HH의 LICENSE_NOTICE는 새 blanket license를 정하지 않으며, 사용자 제공·허가 source의 provenance를 보존한다고 명시한다. BASS_HE 선택 root에서는 LICENSE를 발견하지 못했다. 이를 모든 시점·하위파일의 license 부재라고 일반화하지 않는다. 원자율/단면적 표와 외부 논문의 재배포 권리는 각 upstream notice를 따로 검토한다. 저장소 MIT가 모든 third-party data를 자동 허가하지 않는다. CR geometry_kernel_rebind.py의 실제 SPDX는 GPL-3.0-only다. PHYS01의 RUDD_NOTICE와 GPL-3.0.txt를 추가로 원 blob에 결속하여 보존했다. Rudd notice는 CRIPTIC의 total-ionization 식에서 누락된 F2*wmax² 항의 기존 교정 이력도 명시한다. 그 교정을 새 C23A 발견이라고 주장하지 않는다. 이 intake에서 외부 모듈을 import/실행하지 않았다.

## 7. 네 축과 다음 DAG

| 단계 | EXECUTION | PUBLICATION | BACKUP | DAG |
|---|---|---|---|---|
| 현재 authority/refs/PR | 7repo head snapshot 및7PR read COMPLETE_SCOPED | 실제 draft 상태 확인 | 원자료 로컬 evidence | S0 권위 조사 완료 |
| 선택 source packet | 74text byte binding PASS, 새 science0 | pinned remote blob 존재 확인 | source evidence 묶음 root에 인계 | source adoption 조건 분리 |
| 대화·백업 intake | full chats UNAVAILABLE, metadata/text 범위 확인 | 새 게시0 | Drive OPEN, byte readback 범위 유지 | 보존 미완료를 physics 완료와 분리 |
| 다음 연구 입력 | 기존 map/contract 재사용 결정 | root의 C23A 게시에 통합 대기 | root의 새 delivery에 통합 대기 | contract → 영향받는 코드 → 새 입력 검사 → 분석 → 게시/백업 |

이 intake 노드는 **COMPLETE_SCOPED**다. 전체 목표에 고정된 가중 분모가 없으므로 전체 완성도 percentage와 `global_error_bound`는 **null**이다. 핵물리·CR·IGM 공급자의 존재, finite-support/domain, resolved branching, 단위, 전하·핵종·energy owner를 먼저 묶는다. 기존 source-only exact flow 또는 massive propagator를 반복 발명하지 않는다. 새 C23A 실행은 입력과 run ID, 실제 lease·자원, worker1thread, create-only output을 먼저 고정하고, 완료 cohort를 복원 목적으로 다시 돌리지 않는다.

Machine-readable 핵심: `INTAKE_RECEIPT.json`, `CLAIM_ADOPTION_MATRIX.json`, `FOUR_AXES_DAG.json`, `PRESERVED_GATES.json`, `ALL_SELECTED_TEXT_BINDINGS.json`, `LIVE_REF_DELTA.json`, `PR_HEAD_SUMMARY.json`.

