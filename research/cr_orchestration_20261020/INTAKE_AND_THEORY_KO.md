# bass_cr 결과 통합과 다음 계산의 범위 — 2026-10-20

이번 회수의 핵심 결과는 **GitHub의 C21G보다 새로운 C21H/C21I 구현과 실제 제조 계산이 백업에 완전히 보존되어 있었다는 것**이다. 이를 다시 구현하거나 과학 계산을 반복하지 않고 최종 publication manifest의 파일 단위 identity로 복원했다. 새 native chemistry 계산은 이번 회수에서 수행하지 않았다. 실행, 과학 판정, 게시, 백업은 서로 다른 축으로 유지한다.

## 1. 조회 범위와 근거

최근 창은 2026-10-17T09:55:50Z 이후이다. 현재 GitHub에서 관련 PR80–84와 최신 브랜치를 조사했고, 그중 PR81–84의 실행·검토·refinement 관계를 판독했다. 전체 브랜치 목록 두 페이지와 C21 브랜치 검색을 확인했다. 당시 원격 최신 C21 브랜치는 PR84의 `bf7f7abbe5d2b1844a8fb90bd7e48df23dc5a0c5`였고 C21H/I는 없었다. 이는 모든 브랜치의 모든 파일을 읽었다는 뜻이 아니다. Drive 텍스트 검색은 알려진 파일도 검색하지 못하는 coverage gap이 있었으며, 검색 결과가 비었다는 사실을 백업 부재로 해석하지 않았다.

Dropbox의 실제 네 ZIP을 다운로드하여 archive SHA256, CRC, payload manifest, provider content hash를 검증했다. 이후 Library에서 회수된 최종 delivery receipt로 마지막 Drive ID를 확인했다. Drive/Library는 여기서 ZIP 전체를 다시 다운로드한 것으로 기록하지 않는다. 현재 NCP의 process·CPU/RAM·새 raw 상태는 이 클라우드 회수에서 직접 관측하지 못했다. NCP 실행자는 시작 전에 그 차이를 조사해야 한다.

| 계열 | 확인한 정확한 근거 | 현재 의미 |
|---|---|---|
| C21F 실행 | 실행 content `f8359232df8d0dd4fe91fcdabeb6701eb06089ba`; PR82 head `c4a502e0c931a201edfa3c7046f7a91230c2278f` | 실제 native baseline. Python56/Rust3 및 common-IC/native-source 12-cell 행렬은 기존 근거 재사용 |
| C21F 독립 분석 | PR83 `d780c2c53f869c914add1d5492312d0bc507f976` | 24 histories, 광학깊이 Radau reference2개, accepted steps2160개, 저장 native request/response27140쌍 감사; PASS_SCOPED |
| C21G | PR84 head `bf7f7abbe5d2b1844a8fb90bd7e48df23dc5a0c5`, 실행 content `e742d44f605c51c06615451774ba90af8f41f622` | 8개 reference + 조건부4개 history의 코드 완료. 확인한 근거에서 native NOT_RUN |
| C21H | 2026-10-19 원본, 2026-10-20 handoff/resume/final doc delta | 실제 locked compile와 두 solver 제조 wiring 완료. native NOT_RUN |
| C21I | `BASS_CR_C21HI_OPTIMIZATION_DELIVERY_20261020T073122Z.zip` | 실제 제조 ODE32개 및 FD followup2개 완료, native0. 구현은 이미 완료 |

PR83의 source/raw byte 확인은 168개 대상 중166개였으며 native binary2개의 원격 bytes는 미확인으로 보존한다. 이는 native trajectory의 수치 실패가 아니다. CI workflow 실패, 게시 API의 거절, payload 복원 실패, native process 실패, 물리 수지 실패는 서로 다른 종류의 사건이다.

## 2. 백업 identity와 복원

공통 Dropbox 경로는 `/BASS_DERIVATION_DOSSIERS_20260912/bass_cr/`, Drive 폴더는 `1V4ZQza59dWVC7apeRz9P1TL66eaVYyJy`이다. 아래 ID는 실제 receipt와 조회에서 확인한 객체다. 현재 접근 가능성은 실행 시 별도로 확인한다.

| ZIP | bytes / payload 검증 | SHA256 | Dropbox ID | Drive ID |
|---|---:|---|---|---|
| `BASS_CR_C21H_VIGILODE_DIFFSOL_BRIDGE_20261019T171629Z.zip` | 1537408 / 591 | `2d9c90e2c6f4f17c46dcb23761f862ecab021fb29aa45f7e76c4abf00c09282e` | `id:BSpOijBcT10AAAAAAD_R7w` | `15h3XvmbsF-9mN8Ci3pFiFZGXdu4KB83s` |
| `BASS_CR_C21H_C21I_THREAD_HANDOFF_20261020T030354Z.zip` | 320523 / 48 | `74a366d38f53753123913daa7fde074771da427b2036f1ad86fe39138d1e992a` | `id:BSpOijBcT10AAAAAAD_SHQ` | `16TH0MhATcVkGsgEwCOJU8nzktWO_yxEW` |
| `BASS_CR_C21H_RESUME_EVIDENCE_20261020T053224Z.zip` | 302813 / 74 | `db25e7c07edd8ff4b0296164f9904a0d9173b5c3a7ee09060b05f6fa01a93339` | `id:BSpOijBcT10AAAAAAD_SNw` | `1i2MTTYKIQku5gHNTRIdWmRsxAChc1DNJ` |
| `BASS_CR_C21HI_OPTIMIZATION_DELIVERY_20261020T073122Z.zip` | 6145502 / 1690 | `3c30312161d06e85ab42bea38105b9ede26f97303441a47c6ce2aaccc7d0c537` | `id:BSpOijBcT10AAAAAAD_SWg` | `1KlkxM5XII-v11hMCMGnjyEUnRaqKNpb1` |

최종 ZIP의 Library ID는 `libfile_7c60ff7673fc8191b3d7c98b4a33774e`이다. 최종 ZIP의 Dropbox content hash는 `9ac0e691cf022fe8b77874f0616efa7ceddf70cf9efb967736e8c7b4fda08a52`이며, 이번 다운로드에서 직접 계산하여 provider 값과 대조했다. SHA256와 Dropbox의 4MiB-block content hash는 다른 해시 정의다.

최종 `C21HI_PUBLICATION_FILESET.json`에 따라 H595개(4425683bytes), I1674개(31375114bytes)를 복원했다. I의54개 `.npy`는 보존된 제조 근거의 binary payload다. 총2269개 모두 bytes/SHA256/Git blob identity가 최종 manifest와 일치한다. 공개 delta에는 H/I 두 unit만 포함하고, 비공개 intake·native raw·credential·임시 signed URL을 넣지 않는다. material deletion은 없다. 새 과학 실행0회이며 packaging verification을 과학 검증 횟수에 더하지 않는다.

원 백업에 적힌 local Git 객체 `2358d176...`, `a4f64b879...`, `b260260b...`는 당시의 **local** 객체다. 이를 remote ACK로 바꾸어 적지 않는다. 원본의 `user rejected MCP tool call`, `NOT_PUBLISHED_PARENT_PUBLICATION_BLOCKED`는 그때의 게시 사건이다. 현재 사용자의 새 push 지시를 따라 복원본 게시를 진행하며, 현재 게시 여부·실행 content commit은 새 `PUBLICATION_RECEIPT.json`이 정한다. 역사 기록과 원 과학 파일은 그대로 보존한다.

이번 actual remote content ACK는 H=`40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8`, I=`fe6bbaec2de5032b938aed0713623b9618ba70e6`이며 I의 부모가 H다. 후속 receipt/문서/PR 게시 및 선택 readback 상태는 각각 별도 영수증을 따른다.

## 3. 실제 물리 interface와 donor 경계

이번에 PR84의 `src/native_micro.py`, `src/reference_tau.py`, `native/native_point.rs`를 실제로 읽어 현재 donor와 단위를 확인했다. native owner는 `cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4`이며, 기존 재사용 binary SHA256는 `1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40`이다.

`EVAL a nH0 nHe0 xHII xHeII xHeIII w_eV_H` 요청은 총 H 원자핵당 thermal energy를 입력한다. 실제 밀도는 `nH0/a^3`, `nHe0/a^3`이다. Rust는 `IgmGasState`와 `igm_point_rhs`에 expansion rate0, `T_CMB=2.7255/a`, `IgmPhotoInput::default()`를 넘긴다. 따라서 이 bridge가 소유하는 것은 고정 owner의 **non-photo H/He microphysics**다. 외부 event/optical RHS가 photon absorption과 cosmological work를 소유한다.

| native 응답 인덱스 | 의미와 단위 | 확인/소유권 |
|---|---|---|
| 0–3 | a, nH, nHe, T[K] | Python이 density/EOS identity 확인 |
| 4–6 | HII/H, HeII/He, HeIII/He의 시간미분 [s⁻¹] | native non-photo |
| 7 | thermal derivative [eV/H/s] | native non-photo |
| 8–10 | binding change, escaped energy, CMB→gas [eV/H/s] | native 에너지 분해 |
| 11–13,14–16,17 | CI3, RR3, DR [events/H/s] | native non-photo 사건장부 |
| 18–22 | photo events3, photo input energy, expansion work | 모두 정확한0을 요구; 이중계산 금지 |

이 interface에서 energy identity는 `thermal + binding + escape - CMB = 0`이다. 이후 외부 photon/expansion source를 같은 총 H normalization으로 합성한다. source export는 pinned owner의 별·퀘이사 이력과 spectral cells를 읽지만, 이것이 임의 외부 UVB·17-ion network·새 원자 반응률의 채택을 뜻하지 않는다. `bass_he/wu088_cr/bass`의 새 rate/energy/daughter 결과를 사용하려면 종/전하/질량수, 에너지 zero, threshold, continuum normalization, 단위, T/E 적용영역, uncertainty, detailed-balance 방향, native energy ledger의 소유권을 별도 manifest로 결속해야 한다. 현재 G/H/I의 frozen H/He fixture에 새 rate를 섞으면 기존 동등성·실행 identity가 깨진다.

## 4. 재사용 가능한 이론과 이미 완료한 경량화

독립변수는 \(x=\ln a\), cohort 생존량은 \(N_i=A_i e^{-\tau_i}\)이다. \(\tau_i'=\lambda_i/H\)를 적분하면 작은 생존량으로 나누지 않는다. inactive cohort와 underflow를 구조적0/log-survivor로 구별한다. H/He gas4개와 passive ledger15개를 유지하며 Y=0에서는 He unknown2개를 정확히 제거한다. 현재 strict gas domain과 event birth/cell/clamp 규약은 그대로다.

양의 고정 대각행렬 D에 대해 u=Dz이면 \(F_z=D^{-1}F_u(x,Dz)\), \(J_z=D^{-1}J_uD\)이다. physical atol=αD를 scaled scalarα로 옮기는 것은 각 backend의 같은 오차 norm 안에서 정확하다. VigilODE와 Diffsol 자체의 norm 정의가 다르므로 두 backend 사이 tolerance 동등성을 과장하지 않는다. H는 해석 tau 열, 영 ledger 열, physical-domain represented-node gas FD와 explicit time FD를 결합한다. `fd_half`는 두 probe 크기만 절반으로 하고 tolerance를 그대로 둔다.

순서 (τ,g,ℓ)의 Jacobian은

\[
J=\begin{pmatrix}0&A&0\\ B&C&0\\ P&Q&0\end{pmatrix}.
\]

\((I-\sigma J)k=b\)에서

\[
(I_G-\sigma C-\sigma^2BA)k_g=b_g+\sigma Bb_\tau,
\quad k_\tau=b_\tau+\sigma Ak_g,
\quad k_\ell=b_\ell+\sigma Pk_\tau+\sigma Qk_g.
\]

G≤4와 ledger15가 고정되면 조립·JVP·Schur solve는 cohort 수 M에 선형인 구조를 갖는다. 그러나 현재 H backend는 dense JSONL bridge를 사용한다. standalone Schur 검증을 production backend 도입 또는 native speedup으로 승격하지 않는다. shift/Jacobian bytes가 바뀌면 factorization cache를 재사용할 수 없다. 구조화 backend 연결은 이후 별도 구현·residual·실제동일문제 검증이 필요한 단계다.

C21I는 이미 cohort Jacobian vectorization과 full physical-state binary64-key exact cache를 구현했다. 성공한 finite 값만 cache하고 signed zero·ledger·cell/source/provider identity, copy ownership, 원 deadline, 실제 process/stream/file lease를 보존한다. 실제 original RHS/native call 수를 cache hit와 별도로 센다. 자료형 `.kind` 문자열만으로 provider purity를 인정하지 않는다.

| 완료한 I 근거 | 실제 결과 | 적용 한계 |
|---|---|---|
| optimized callback 계약 | unique18개 PASS_SCOPED; native-cache stub14개 | native 호출 증거가 아님 |
| standalone block solver | Rust12tests;312solve+240JVP; unique12개 Decimal100자리 residual 최대9.45936549e-16 | H backend 미연결 |
| component 비용 | 216batches/432tasks/3888outputs bitwise동일 | threadpool2는36개 중31그룹에서 악화; 자동 병렬 확대 금지 |
| 실제 제조 ODE | 32jobs,96segments COMPLETE;24nonself+8self 비교; 원 trace/endpoint/ledger/FD node/solver counter bitwise동일 | native0; self8개는 독립 검증이 아님 |
| 원 RHS calls | VigilODE423→372, Diffsol74→71 | 작은 제조 trajectory |
| paired process median speedup | VigilODE vectorized0.845647 / exact0.920985; Diffsol1.045230 /0.985440 | 일관된 end-to-end 가속 미확립 |
| 추가 FD2개 | gas/T 차이0; VigilODE photon6.166244974933198e-22/H, log-survivor4.404571325722362e-20; Diffsol0 | native0, 전역 IVP 오차 상계 아님 |

제조 ODE32개 총 process35.48594687099103s의 근거를 재사용한다. 이번에 이를 재실행하지 않았다. warm-cache4.82–11.19배는 best case이며 실제 native trajectory hit rate가 아니다. 모든 수치·성능 결론에 `global_error_bound=null`, `native_performance=NOT_EVALUATED`를 유지한다.

## 5. 다음 DAG와 실행 준비도

| node | 코드/로컬 근거 | 다음 실제 작업 | 의존성 / 완료 판정 |
|---|---|---|---|
| recovered H/I publication | 2269개 exact bytes 복원 COMPLETE | 새 ACK 기반 H→I 게시·receipt | 코드 동일성과 게시를 별도 기록 |
| G reference | 구현·focused35개 및9제조IVP 근거 완료 | 두fixture×L1/L2/L3/L3M 8개 | 기존 L0 재사용, 300s/200000각job |
| G history refinement | 구현 완료 | native_source×두method×n128/256 최대4개 | reference8개 operational완료 + native pilot READY |
| H native base | locked Rust compile·manufactured wiring완료 | 두fixture×VigilODE/Diffsol 최대4개 | 현재resource/build/native admission |
| H derivative sensitivity | 구현·제조검증완료 | 동일context의 완료base마다 fd_half 최대4개 | 기존complete base 재실행 금지 |
| I native callback pilot | 코드·제조ODE32개·FD2개 완료 | 우선 common_ic/VigilODE/vectorized 1개 | H/I actual publication + 동등Hbase + 동일build/native |
| I exact-cache 비교 | 구현·stub/제조검증완료 | 필요할 때 같은fixture의 vectorized_exact 추가 | guard비용/hitrate 실제기록; 무조건 전체matrix 금지 |
| structured Schur backend | 이론·standalone까지 완료 | 이후 ChatGPT 쪽 별도 backend 통합 | NCP에 새기능 개발 전가 금지 |

G/H/I는 수학적으로 같은 frozen RHS에 대한 서로 다른 검증 lane이다. 단일 현재 할당 CPU를 공유하므로 실제 job은 순차 실행하며, 외부의 다른 repo campaign과는 승인된 자원 partition으로 병행할 수 있다. 완료 matching job을 재사용하고 현재 실행 중인 job을 복제하지 않는다. 과거 full-native8/16/32/48-worker profile,10000/12h campaign, C21F n8/16/32/64, full9600 PHYS02H를 새로 제출하지 않는다.

Full48, source-age, spectral, angular, Case B, signed Bianchi, full EoR, standalone Grackle driver parity의 기존 HOLD는 이 통합으로 닫히지 않는다. b-grid NO_GO, capture false, all_bound OPEN과 기존 atomic production gate 역시 해당 별도 근거가 생기기 전까지 유지한다. 정확한 실행 절차와 반환 계약은 [NCP_ORCHESTRATION_KO.md](NCP_ORCHESTRATION_KO.md)를 따른다.
