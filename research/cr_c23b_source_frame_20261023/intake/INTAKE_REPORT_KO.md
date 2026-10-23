# C23B 최신 변경분 조사와 재사용 판정

작성일: 2026-10-23 UTC. 작업: `/root/c23b_intake`, 읽기 전용 원격 조사. physmath-research-loop 내장 1.0.0 / approval0.2를 따른다. 이 단원은 새 물리 계산을 실행하지 않았다.

## 1. 확인한 범위

C23A의 7개 저장소 REST head 1,278개를 기준으로 동일한 `git/matching-refs/heads/` 경로를 다시 확인했다. 새 snapshot은 **1,285개, +7 added / 5 changed / 0 removed**다. 이것은 알려진 7개 저장소의 반환된 head 목록이며 git-wire 광고 결과, 소유자의 모든 저장소 또는 모든 역사 파일을 뜻하지 않는다. 정확한 시작·종료 UTC는 API_LIVE_REFS.json에 있다.

| 저장소 | 이전 | 이번 | 추가 | 이동 |
|---|---:|---:|---:|---:|
| bass_cr |175|175|0|1|
| rei_bianchi |263|263|0|1|
| bass |266|267|1|0|
| BASS_HE |94|95|1|1|
| WU088_HH |146|147|1|1|
| rec_bianchi |143|146|3|0|
| vigilode |191|192|1|1|

7개 기존 PR과 10개 변경 branch의 PR 연관을 조회했다. 변경 branch 중 7개에는 해당 PR이 있었고 3개에서는 빈 배열을 받았다. 총 **14개 고유 PR**의 metadata를 확인했으며 모두 open/draft/unmerged였다. PR96의 head는 `7291ecc711b087a6525fab25d82a4e235d24b9f1`다.

최초 snapshot 후 HE37 PR90이 `9932e420535f5ad11c1aa7653f58683eb07f14cf`에서 **C10 보고 commit `a5a670968cb1326375f394faa867c6b260c5840d`**로 이동했다. 이 이동은 POST_SNAPSHOT_HE37_MOVEMENT.json으로 별도 보존했다. 새 commit의 변경 목록은 보고서·handoff·장부·검증기이며 기존 연구 source와 실행 raw를 바꾸지 않는다. C10 보고서와 handoff 2개를 추가로 읽었다. 모든 head를 다시 세어 최초 snapshot 숫자를 소급 변경하지 않았다.

선택 원문 **53개, 625,625 bytes**를 실제 취득하고 고정 Git blob SHA1과 로컬 SHA256을 대조했다. 최초 51개는 tree의 크기와도 일치한다. 마지막 C10 문서 2개는 commit의 blob SHA1과 실제 전체 bytes로 완전성을 확인했다. 53개를 내려받았다는 것은 모든 외부 과학 raw를 독립 재감사했다는 뜻이 아니다. 전체 binding은 ALL_SELECTED_TEXT_BINDINGS.json에 있다.

Personal Context의 실제 응답은 `Personal context is unavailable for this conversation.`이다. 따라서 **전체 다른 대화 전문은 UNAVAILABLE**다. 대화 유래 연구의 접근 가능한 Git handoff와 보고서는 읽었으며, 대화 자체를 읽은 것으로 바꾸어 기록하지 않는다.

## 2. 다음 연구에 영향을 주는 실제 변경

| 단원 / 고정 pin | 확보한 내용 | 현재 적용 경계와 C23B의 판단 |
|---|---|---|
| REI ANGTHERM01 / `6daf382ee698835e7a141378c232d1d97c1c5cf1`, PR221 | 저장 C21O grid044/022 배경 위 10개 새 궤적, M4 221→41 유한 isotope/angular 축약, optical-depth 변수, 열·결합·광자·탈출·평균팽창·전단 일 장부 | 소유자의 PASS_SCOPED 결과와 실제 보고/receipt를 취득했다. 이번 intake의 10 raw 재감사는 아니다. 완료 IVP 재실행 금지. prescribed 배경이며 새 trace의 Einstein feedback과 실제 방출사는 열려 있다. |
| HE36 / `6403055c3d574ec0bd1ece80147f9711315902e7`, PR89 | common-bulk/common-T 무한소 Grad incoming-loss, finite-mass pair, central source 변환, event/source lift; 새 IVP0 | 기존 bridge와 centralization을 재사용한다. 모든 product gain·stopping을 이미 해결한 것으로 읽지 않는다. |
| HE37 / 연구 source at `9932e420535f5ad11c1aa7653f58683eb07f14cf`, C10 보고 `a5a670968cb1326375f394faa867c6b260c5840d`, PR90 | Le–Cambier2016 Eq85 + §III.E의 H1 differential sharing, 등방 outgoing, analytic Maxwell moments, net number/energy/electron STF source. C10 과학 판정 PASS_SCOPED; 129T 진단과 bridge 저장 결과 | heavy stationary target, threshold13.6eV, common-bulk infinitesimal electron Grad다. 실제 angular calibration·finite recoil·total gas stress closure는 별도. 최종 archive ACK는 이 intake에서 취득하지 않았으므로 완료 백업으로 선계상하지 않는다. |
| HH PHYS81 / `b3ec271a96cb67e583bffa9b61533802838236f9`, PR137 | finite H1/He4/Li7 CI, 7→3 hazard 좌표, 새 parcel3 ODE, 세 cold-COM radiative capture의 photon/recoil 장부 | 과거 NOT_RUN 문구 이후의 완료 자료로 갱신한다. H13.6058–968.61, He24.6–60, Li6–15eV의 finite support. full physical rate, finite-T event 평균·normal-frame boost·stopping은 열려 있다. |
| HH PHYS82 / `fc66c8d4161f8339a82efd958f47cda23e001234`, PR138 | Li7의 5.39172060034581→6eV source gap에 관한 primary-source 계약, historical measured slope 및 Wannier 비교 후보 | source-gap 연구가 이미 진행 중이다. C23B에서 동일 Li threshold 조사/기존 finite CI 실행을 중복하지 않는다. 조회한 계약은 조건부 모델 연구이며 전체 낮은 T 물리율 coverage는 OPEN. |
| REC ANGULAR01 / `5185c396b7e07076565ca2f5044a5ccd193e6ee1`, PR127 | 405 parameter rows, escape probability B와 PSTF Q, analytic thick branch와 유한 대체 오차 | Q는 photon stress 자체가 아니다. 완료 405rows를 재실행하지 않는다. 최초5행 cancellation 판정 FAIL과 저장값 재판정 이력을 보존한다. |
| REC LINE01 / `b5e330c6918daea256ea0634ad92bd142d5510ae`, PR128 | resolved/effective H 2p card, bound-bound number·energy·PSTF source ownership, exact local thick Lambert-W map 계약 | frozen contract 단계. tree에서 actual LINE01 execution 결과를 찾지 않았으며 planned rows를 완료로 세지 않는다. 중복 line owner 거부와 collapsed-line 가정이 핵심이다. |
| REC C2 / `12068893fab749ae1efb513563d0a86cc1cf649f`, PR126 | 기존512 saved states의 진단·CI/CE 프로파일, 중복평가 경로 분석 | 새 IVP가 아니다. 이 상태 수를 REC119의 실행 수126과 섞지 않는다. 본 intake는 해당 profiler를 재실행하지 않았다. |
| VigilODE / `fbc3c272fa06b443de148631ea78bfa6a34f1b2b` 및 `14c74978b93339a79d7228a324fa77552dae548e` | 외부 diffsol/Julia 새384 process cohort, dense observation과 affine physical error norm Rust 구현·검증 | 기존 P02 C6FAIL을 지우지 않는다. 새로운 smooth nonstiff identity-mass 경로의 scoped 근거다. C23B의 정확한 subflow/각도 적분에 solver를 자동 이식하지 않는다. |
| BASS background / `2bc6a602f199620de735b3d2521b274160db7d4f` | fixed-scale Einstein operator, separate material/radiation balance와 beam source 계약 | 읽은 것은 contract와 tree다. 계획된11-family 궤적 완료를 주장하지 않는다. BASS_CR의 일반 tilted/triaxial HOLD를 바꾸지 않는다. |

ANGTHERM01에서 M4 기준 Li charge-fraction 최대 방향 효과는 약0.049다. M8/M16 차이 약4.64e-5가 남으므로 finite-angle 축약의 대수적 정확성과 연속 각도 정확도는 구별된다. 독립 수치 비교가 있는 완료10궤적 자체는 재사용 가능하다. 원래 n/T0 inventory와 isotopic equal-generator/equal-initial-fraction 조건을 유지한다.

HE37은 한 사건의 outgoing 전자를2개로 세되 event cross section을2배로 만들지 않는다. 동일 threshold I의 kinetic defect는 `-I R`, binding owner는 `+I R`다. mean incoming energy를 추가 열 손실로 빼지 않는다. HE37의 Q와 HE36 donor dEth도 같은 owner이므로 합산하지 않는다. 이 소유권은 C23B source/deposition adapter를 구성할 때 재사용할 수 있다.

HH81의 isotope correction은 Li7 chemical energy에 적용되었으며 CCC incident energy axis는 그대로다. isotope-specific threshold correction과 electronic cross-section isotope calibration을 동일시하지 않는다. finite-source operator 범위의 구간 밖0은 모형 정의이고 absent physical channel을0으로 채우는 근거가 아니다.

## 3. 기존 CR 기하 코드와 C23B의 정확한 차이

직접 읽은 기존 `geometry_kernel_rebind.py`는 `bass_cr@ba39fc75521aa18705ec832d789e50dd5c6565bc`, 19,188 bytes, SHA256 `ef4eecec5380ead4a6b24bf2c7c796b6d42b2102f5e803bb386e483b7aba6ebb`다. GPL-3.0-only notice를 보존해야 한다.

기존 코드는 `K=(pc)^2/(E+mc²)`의 안정 평가, `pc=sqrt(K)*sqrt(K+2mc²)`, diagonal Bianchi endpoint momentum scaling, comoving packet count와 signed geometry work, positive count/energy barycentric projection, 현재 parent energy의 collision rebinding을 이미 제공한다. 이 algebra와 owner 의미를 다시 새로운 발견으로 제시하지 않는다. 기존 source identity와 선택된 알고리즘의 재사용은 CR_SOURCE_REUSE.json에 결속했다.

이번 parent가 구현하는 항목은 **등방 parent-rest massive electron을 bath frame으로 Lorentz 변환한 `K'=A+Bμ`의 정확한 angular marginal, 구간별 count/kinetic energy/parallel pc 적분, finite FS2010 PL 응답의 정확한 contraction, proper lifetime와 physical/comoving normalization**이다. 읽은 기존 CR selected source와 최신 관련 단원에는 이 패키지의 완료 구현을 확인하지 못했다. 이 판정은 해당 선택 원문 범위의 reuse 비교이며 모든 문헌·모든 repo에 대한 novelty 주장이 아니다.

HH81 `nuclear_recoil.py`는 event COM frame 전용이며 `normal_frame_source_adapter_available=False`를 명시한다. HE36의 boost는 Galilean central/reactive source 변환이다. HE34의 Lorentz transport는 heavy-scatterer collision 모형 명칭이다. 이들을 parent-rest→bath Lorentz spectral pushforward 완료 근거로 대체하지 않는다.

새 electron boost는 기존 Bianchi time transport와 서로 다른 단계다. 전자의 angular field가 필요한 anisotropic stress까지 에너지 marginal 하나로 대체할 수 없으며, 새 bin parallel-momentum 장부를 gas-isotropic stress closure와 혼동하지 않는다. 실제 beta spectrum, atomic/molecular initial charge state, composition-compatible FS response, high/low stopping 및 neutrino/recoil owner는 각각 입력 의존성으로 남긴다.

## 4. 백업과 외부 실행 확인 수준

| 대상 | 이번 확인 | 여전히 별도인 항목 |
|---|---|---|
| HE36 final archive | Git FINAL_ACK 본문 + 실제 Dropbox metadata ID `id:BSpOijBcT10AAAAAAD_swQ`,842860B 일치 | remote byte 재다운로드 NOT_RUN; owner도 metadata ACK 범위를 명시 |
| REI ANGTHERM01 final archive | Git FINAL_DELIVERY + 실제 Dropbox metadata ID `id:BSpOijBcT10AAAAAAD_v1g`,15397188B 일치 | owner의 Drive ID `1p2ElUGvZfkwCxEjHme4ryXIjiCxGi6DW`는 Git receipt로 읽음; 이 agent의 Drive 재조회/remote-byte 확인 NOT_RUN |
| HH81 | S2 checkpoint ACK와 최종 handoff를 읽음 | external final-delivery JSON과 최종 ZIP byte 재다운로드는 이 intake에서 NOT_RUN |
| HE37 | C10 science/report checkpoint를 확인 | 그 이후 final archive/provider ACK는 이 snapshot에서 NOT_FETCHED |
| C23A/C22D/C21O 보존 | root가 알려진 최종 authority와 별도 backup reconciliation을 담당 | 이 intake가 기존 byte restore를 반복한 것으로 세지 않음 |

외부 science 실행 상태는 저장된 owner 보고/receipt에서 확인했다. 각 외부 host의 현재 process와 lease는 **UNOBSERVED**다. 실행 source commit과 보고 commit을 구별하며, 다른 thread의 누적 CPU와 결과 수를 C23B 실행 수에 합산하지 않는다.

## 5. 유지할 과학 경계와 다음 DAG

REI220/BASS180 mirror와 원127 JSON 실패/재적분, historical representative2pairs/raw4 PASS_SCOPED, C21O와 다른 RR/DR·UV/T·tolerance, HE85 과거 loss/recovery, REI219 조건부 핵계 및 VigilODE P02 C6FAIL은 그대로 보존한다. 62→33 등의 상태 감소만으로 측정 speedup을 만들지 않는다. 원 핵반응망 PNG는 UNAVAILABLE_NOT_READ다. `global_error_bound=null`, 전체 목표 완료율도 고정 분모 부재로 null이다.

| 순서 | 실행 | 게시 | 백업 | DAG |
|---|---|---|---|---|
| 최신 delta intake | COMPLETE_SCOPED, science0/ODE0/NCP0 | 원격 변경0; 로컬 산출물 root 전달 | 위 provider metadata 확인; 새 intake의 원격 저장은 root 담당 | C23B 입력·재사용 조사 완료 |
| source frame/normalization | root의 새 조건부 유도·구현 | 새 science packet에 결속 예정 | root release 대상 | READY, 기존 geometry와 구별 |
| actual source coverage | HH81/HE37 scoped evidence 재사용, HH82 source gap 진행 관찰 | 각 owner pin 유지 | 각 owner의 실제 수준 유지 | beta spectrum/FS composition/threshold/final states OPEN |
| admitted coupling | source 수·전하·핵종·열·radiation·fast/tail ledger를 동일 기준계로 결합 | 입력과 code가 확정된 뒤 | 새 run과 분석을 보존 | 실제 공급조건 이후 실행 |

이 조사 결과를 통해 다음 물리 작업은 이미 진행 중인 Li gap/line source를 반복하는 대신 parent의 source-frame/finite-tail component에 집중할 수 있다. 완료된 C21O–C23A, 새 ANGTHERM01 10궤적, HH81 parcel3, HE37 provider·진단, REC ANGULAR01405행은 복원 목적으로 재실행하지 않는다.
