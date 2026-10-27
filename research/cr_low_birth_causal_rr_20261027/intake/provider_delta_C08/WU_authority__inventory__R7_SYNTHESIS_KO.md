# WU R7 최신 접근 가능 입력 조사 — R1/R2 및 C1/C2 근거

## 결론

WU 현재 `research/provider-registry-20261025`의 실제 HEAD는 **0713cb7ef6df5769def878b475ba18f4068331fa**이며, 전달 완료한 R6의 **13/28** 상태를 재사용한다. 이 조사는 새 과학 실행, 다른 owner의 상태 변경, 외부 게시를 수행하지 않았다. 다음 연구 단위를 선정할 실제 새 입력은 HE PHOTON05의 조건부 광핵 사건 어댑터와 진행 중인 ANGULAR06의 각분포 투영 계약이다. 조사한 원문에서 GL2022 native HD reactive arrays 또는 x0/pi/piDot/K/d/h/f/density/clock를 갖춘 named WU molecular consumer가 새로 제공된 사실은 확인되지 않았다.

HE 새 결과는 다른 물리 과정의 완료로 바꾸지 않는다. PHOTON05는 γ + 정지한 bare ⁴He → 2D의 **사건당 상대론적 에너지·운동량·응력**을 제공한다. 실제 사건률, 완전한 실험 각분포, 표적/빔 투영, named nonthermal/deposition consumer는 별도 입력으로 남는다.

## 1. 조사 범위와 재현 가능한 목록

사용자가 지정한 로컬 **physmath-research-loop 1.0.0**의 R1/R2 및 C1/C2를 적용했다. SKILL.md, RESEARCH_POLICY, THEORY_LOOP, CODING_LOOP, EVIDENCE_AND_HANDOFF, RUNTIME_AND_LEGACY를 읽고, 기존 과학의 재실행 없이 변경된 의존성만 조사했다.

| 항목 | 이전 보존 조사 | 이번 실제 조사 |
|---|---:|---:|
| 접근 가능한 owner 저장소 | 51 | 51 |
| 공개 저장소 / branch refs | 35 / 1,871 | 35 / 1,874 |
| 비공개 저장소 / branch refs | 16 / 483 | 16 / 483 |
| 전체 branch refs | 2,354 | 2,357 |
| 실제 exact branch 목록 페이지 | 65 | 65 |
| terminal을 확인한 저장소 | 51 | 51 |

여기서 refs는 **refs/heads, 즉 브랜치**다. tags, arbitrary hidden refs, 모든 commit history를 전수 열람했다는 뜻은 아니다. 공개 브랜치 페이지 관측은 2026-10-27 13:11:38.854–13:11:46.156 UTC, 비공개 exact REST 페이지 보완 확인은 13:13:26.736 UTC까지다. 조사 전체는 원자적 snapshot이 아니다.

`R7_OWNER_BRANCH_INVENTORY_PUBLIC.json`은 공개 35개 저장소의 전체 branch 페이지와 비공개 집계만 포함한다. `R7_PUBLIC_BRANCH_DELTA.json`은 공개 ref 비교다. 이번 공개 변화는 **새 브랜치 3, 삭제 0, 기존 HEAD 변경 5, 기존 HEAD 동일 1,866**이다. 비공개 이전 자료에는 이름별 baseline이 없으므로, 같은 483이라는 합계로 비공개 HEAD가 모두 같다고 추론하지 않았다.

네이티브 PR 도구로 WU 최신 8개와 REC/REI/BASS/CR/HE/VigilODE 각 최신 5개, 총 **38개 PR의 실제 metadata와 body**를 읽었다. 네 개 변경 범위의 compare metadata를 저장하고 핵심 원문 16경로를 요청했다. 15파일은 UTF-8 원문을 저장한 뒤 공급자 Git blob SHA1과 실제 바이트 일치를 확인했다. BASS PR205 HEAD의 root AGENTS.md는 실제 404였으며, 이를 읽었다고 주장하지 않는다.

`private_local/`은 비공개 이름/ref/SHA가 있는 **로컬 전용 자료**다. 공개 Git/패키지/authority 복사에서 디렉터리 전체를 제외한다.

## 2. 고정한 주요 identity

| Owner / 범위 | 실제 확인한 pin | 판독 |
|---|---|---|
| WU PR150 | 0713cb7ef6df5769def878b475ba18f4068331fa | 현재 R6 최종 metadata, 13/28 |
| REC PR139 | d6dbe39a4923439547c01695d9020ba39367ea90 | 기존 source-synthesis와 동일 |
| REI PR240 branch 페이지 | c1b736238a45ff0bd17b1280573ae441780c994d | 조사 도중 R6 단계 관측 |
| REI PR240 후속 PR/원문 | 028ca1f8ed84bc4f827728410f4bb483d763c9c6 | R7 finite-cohort analytic checkpoint |
| REI 중앙 branch | 152b82cac23fedcb75a9effe0c159bae3d800c01 | 변경된 중앙 metadata |
| BASS PR205 branch/원문 | 3c14c6889cc3d3d1948d2676df9cfaacc4a1455c | S1A Phase A actual result |
| BASS PR204 | 02a88bf2f6ca93f38e0e173d663657f6ef7ecad0 | DV2-D 순간 class-B generator |
| CR PR110 | e8ba946d8d9a0223ac4f918ad7a6f1eafc44e9b5 | R8 theory admission, numerical pending |
| HE 자체 GitHub PR102 | ac6042a6b0610b09d0576538767ee0299389a5eb | remote 불변 |
| VigilODE PR90 | 68a28357d960c4c2743c299770f0a33ef63245b2 | 기존 rigorous-performance-audit와 동일 |

BASS PR205의 먼저 읽은 PR metadata/body는 S0 `b581ad6f9ab92ee2efac816e2f2d2a63994c77c6`를 가리켰다. 후속 branch 페이지 및 고정 원문은 이미 S1A `3c14...`다. REI도 branch 페이지와 후속 PR 원문 사이에서 전진했다. 이 차이는 원자적 snapshot 부재로 명시했으며, 각 원문을 실제 읽은 exact commit에 결속했다.

## 3. HE PHOTON05: WU 원자료와 연결되는 새 조건부 사건 어댑터

BASS PR205의 공개 survey 복사본에서 PHOTON05 report와 closeout JSON을 직접 읽었다. 이 파일들은 실제 공개 BASS commit에 존재한다. HE 자신의 GitHub branch가 해당 로컬 commit까지 게시되었다는 근거로 바꾸지는 않는다.

- HE 로컬 scientific source S05: `251c6baa6c3359b1d6997dbce51cea65500b53d6`.
- HE 로컬 delivery D05: `4db5ce7297a7ded4624b93721873aacc9b4ebf30`.
- 과정: photon + stationary bare ground-state alpha → two bare ground-state deuterons.
- 원래 WU EXFOR M0475002의 12개 Eγ/CM각 좌표를 사용한다. Differential cross section을 실제 encounter flux로 바꾸었다고 주장하지 않는다.
- saved tests: 단일 process **24/24 PASS**, CPU 0.241060162 s. 독립 Decimal reference와 검토 identity가 closeout에 보존되어 있다.
- saved plot: artifact는 생성되었으나 CPU **4.407265040 > 4 s**, **FAIL_CPU_CAP_EXCEEDED**를 유지한다. 원인 확정, 재실행, warning-free 또는 전체 PASS로 재서술하지 않는다.
- 사건당 photon −1, alpha −1, deuteron +2, material nuclei +1이다. population rest energy가 binding을 소유하므로 별도 binding RHS를 더하지 않는다.
- Γthermal, Cv, species heating, thermal deposition은 null, birth pool은 UNASSIGNED다.
- caller 예제 flux=0은 실제 물리 사건률이 0이라는 뜻이 아니다.

실제 source-consistent complete angular law, encounter flux, 실험 target/beam/acceptance projection, named nonthermal/deposition consumer는 미제공이다. physical_provider_admitted=false, physical_global_consumer_admitted=false, production NOT_APPROVED, activation=false, L4_ready=false를 유지한다. 이 결과는 새 **광핵 사건의 조건부 운동학**이며 HD molecule destruction coefficient가 아니다.

[PHOTON05 원문 report](https://github.com/cosmosapjw-quantum/bass/blob/3c14c6889cc3d3d1948d2676df9cfaacc4a1455c/research/bass_b3h_qss_channel_completion_20261027/survey/BASS_HE_PHOTON05_REPORT_KO_20261027.md)와 [closeout JSON](https://github.com/cosmosapjw-quantum/bass/blob/3c14c6889cc3d3d1948d2676df9cfaacc4a1455c/research/bass_b3h_qss_channel_completion_20261027/survey/BASS_HE_PHOTON05_CLOSEOUT_20261027.json)에 직접 결속한다.

백업 담당자가 별도 실제 archive에서 확인한 ANGULAR06 S02 `a4745150c30a`는 branch-resolved CM→lab angular pushforward와 identical-daughter normalization을 다룬다. 보고된 archive SHA256은 `b9bdf18b4c1edab61de8fb60a1b98bb2b9bc252eebfb96b1fd8231b6f4a52d83`이다. 이 보완 관측은 **다른 담당자의 원본 판독 보고**로 구분했다. original normalization과 complete angular law는 UNRESOLVED, f_CM은 caller가 명시하는 함수, physical flux/named consumer는 미제공이다. 이후 owner 작업의 추가 관측은 별도 backup intake의 시간 한계와 receipt를 따른다.

## 4. 기타 변경 범위와 다음 연구에 미치는 영향

### BASS PR205 Phase A

[고정 root admission](https://github.com/cosmosapjw-quantum/bass/blob/3c14c6889cc3d3d1948d2676df9cfaacc4a1455c/research/bass_b3h_qss_channel_completion_20261027/reviews/ROOT_PHASE_A_ADMISSION.md)은 **PASS_SCOPED_PHASE_A**다. 단일 실행 67/67 검사를 통과했고, 두 endpoint source operator, 새 diffusion inversion 네 개, represented fixed-TR Maxwellian successful-channel energy moments를 채택했다. 실제 CPU 1.129564 s이며, 독립 검토는 repair/replay를 요구하지 않았다.

오른쪽 Tvv/sv/(1−P)의 최대 상대 차이 약 1.55103138e−8은 고정 허용치 5e−8 이내다. 모든 operand가 bitwise 동일하다는 결과는 아니다. physical radii는 null, 중앙 DAG 27/88과 delta0을 유지한다. finite dynamic Phase B는 계약 준비와 별도로 아직 수행하지 않았다. 원래 QSS 오른쪽 endpoint를 finite-time dynamic 해로 간주하지 않는다.

### REI PR240 finite-cohort enclosure

[새 계약](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/028ca1f8ed84bc4f827728410f4bb483d763c9c6/research/rei_expanded_event_consumer/finite_cohort_enclosure_20261027/CONTRACT_KO.md)은 유한 주입 cohort의 Stieltjes kernel, cell extrema, cumulative-chain LP의 finite-level exact-rational DP를 연결한다. 같은 F를 여러 시간창이 공유하므로 개별 sharp upper의 합을 joint sharp bound로 바꾸지 않는다. [R7 capsule](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/028ca1f8ed84bc4f827728410f4bb483d763c9c6/research/rei_expanded_event_consumer/finite_cohort_enclosure_20261027/checkpoints/R7.md)은 해석 사례와 증명·정적 검토 기록이다.

새 20개 tests와 기존 affine 16개 tests는 미실행이다. [BUDGET_STOP](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/028ca1f8ed84bc4f827728410f4bb483d763c9c6/research/rei_expanded_event_consumer/finite_cohort_enclosure_20261027/BUDGET_STOP.json)의 HOLD_RESOURCE, cumulative spending 및 과거 overrun을 유지한다. source100K와 response10000K가 실제 같은 상태로 결속된 것은 아니며, actual recipient nb와 WU molecular consumer도 공급하지 않는다. 해석 이론의 재사용 가능성과 실제 물리 consumer 완료를 분리한다.

### CR PR110 low-born causal RR

[고정 계약](https://github.com/cosmosapjw-quantum/bass_cr/blob/e8ba946d8d9a0223ac4f918ad7a6f1eafc44e9b5/research/cr_low_birth_causal_rr_20261027/CONTRACT.md)은 기존 PHYS02 direct_0p1_10의 q_j(t)=tA_j와 [0,10¹⁰] proper seconds를 재사용하면서, **새 조건부 100 K H1/He4 inventory**를 명시한다. nH=140 m⁻³, xHII=xHeII=0.01, xHeIII=0 및 nb=8750/47 m⁻³는 이 새 모델의 선택이다. 과거 source가 이미 그 nb를 공급했다는 뜻이 아니다.

Coulomb stopping과 ground-state HII/HeII spontaneous RR, retained-photon atom 처리를 계획하며, 원래 cutoff source와 10000 K 응답을 임의로 혼합하지 않는다. [R08](https://github.com/cosmosapjw-quantum/bass_cr/blob/e8ba946d8d9a0223ac4f918ad7a6f1eafc44e9b5/research/cr_low_birth_causal_rr_20261027/stages/R08.json)은 이론 채택만 완료했고 exact pin에서 수치 실행은 pending이다. 중앙 27/88, delta0, L4false/globalnull을 유지한다. HD reactive source나 named WU molecular consumer는 제공하지 않는다.

### BASS DV2-D와 불변 owner

[DV2-D README](https://github.com/cosmosapjw-quantum/bass/blob/02a88bf2f6ca93f38e0e173d663657f6ef7ecad0/research/dual_lane_dv2d_20261027/README.md)는 Bianchi-V class-B의 full-polarized 순간 generator, sphere measure, energy/flux balance를 다룬다. saved 11 pytest와 828 basis rows 등은 해당 범위의 근거다. finite-time kinetic IVP는 실행하지 않았고 독립 model review는 NOT_RUN이며, geometry/Einstein/physical source의 전체 완료도 아니다. WU molecular rate 입력을 새로 주지 않는다.

REC와 VigilODE의 관련 최신 pin은 이전과 동일해 accepted science를 재사용했다. 전체 이전 blob이나 과학 suite를 다시 읽거나 실행하지 않았다.

## 5. 적용 경계와 후속 루프 handoff

다음 WU 루프는 위에서 확인한 **실제 source identity**를 먼저 선택해야 한다. molecular R6을 계속 적용하려면 GL2022 native reactive arrays 또는 named physical consumer의 x0/pi/piDot/K/d/h/f/density/clock 및 interval-wide bounds가 필요하다. 이번 조사에서 없는 수치를 0으로 채우지 않고, v=UNSPECIFIED와 MISSING_NOT_ZERO를 보존한다. PHOTON05/ANGULAR06를 선택한다면 nuclear event·CM→lab projection의 별도 source contract와 실제 아직 없는 angular/flux/consumer 입력을 명시한다.

[WU 현재 AGENTS](https://github.com/cosmosapjw-quantum/WU088_HH/blob/0713cb7ef6df5769def878b475ba18f4068331fa/AGENTS.md)는 R6 primary76/76, independent reference109/0, 실제 경고가 있는 CAS23 zeros를 재사용하도록 명시한다. HH_R10=OFF, production=NOT_ISSUED, L4_ready=false, central/physical completion delta0이다. 이 inventory는 새 DAG 노드를 채택하지 않았으며 **13/28**을 유지한다.

과거 ChatGPT 전체 대화 원문을 전수 열람한 것은 아니다. 사용자 제공 요약, root 전달 사항, 백업 담당자 관측은 원문 GitHub read와 구별했다. 접근 가능한 모든 저장소의 branch 목록을 조사한 사실과 모든 tip의 파일·전체 과거 대화·전체 backup 원본을 읽은 주장은 서로 다르다.

## 산출물

- `R7_OWNER_BRANCH_INVENTORY_PUBLIC.json`: 공개 원목록과 비공개 집계.
- `R7_PUBLIC_BRANCH_DELTA.json`: baseline 대비 공개 branch 비교.
- `R7_LATEST_PR_INVENTORY.json`: 실제 PR38개 body/metadata.
- `R7_CHANGED_OWNER_COMPARE_METADATA.json`: 고정 변경 범위 네 개의 file-list/stats.
- `R7_SCOPED_PROVIDER_RESPONSES.json`, `scope/`: 원문 response 및 실제 UTF-8 파일.
- `R7_SCOPE_READ_MANIFEST.json`: commit/path/blob/bytes/SHA256 연결과 실제404.
- `R7_CHANGED_INPUT_EVIDENCE.json`: 새 과학 입력의 범위, 누락 필드, 각 source status.
- `R7_PUBLIC_ARTIFACT_INDEX.json`: 공개 산출물의 path/bytes/SHA256.
- `private_local/`: 로컬 전용, 공개 및 공개패키지에서 제외.

