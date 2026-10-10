# REI/BASS/REC — CR physical-provider 연결용 최신 intake

2026-10-10 UTC의 공개 Git 원문과 게시된 두 thread-return을 새로 읽었다. 이 파일은 읽기 전용 intake다. source 변경, solver/COMMON18 campaign, commit·push·백업은 수행하지 않았다. 새 사용자 요청의 push 권한은 root가 소유하며 이전 보고서의 no-push hold를 이번 요청에 재적용하지 않는다. 선택 하네스는 GPT-6 Astra v4.0.0, 실제 실행 모델은 UNKNOWN이다.

이번에 확인한 진전은 **warm HM12 조건부 물리 입력, 실제 native receiver, build gate가 이미 생겼다는 점**이다. CR provider를 붙이는 최소 작업은 해당 계층 위의 별도 CR 입력·침적 경계다. frozen warm contract를 수정하여 CR이 이미 켜진 것처럼 만들면 안 된다.

| repo / PR | 현재 head / branch | 실제 상태와 이번 적용 |
|---|---|---|
| REI96 | `528bb69a24ce9345efec78c6d406d3c392e2671d` / `research/physical-provider-20261010` | HM12 photon IC·emissivity, dust+Λ axisymmetric background, 50000 K warm H/He IC, 17 epoch 조건부 interval의 원본 |
| REI97 | `00903cb4433276ad5d8233aca1f9e0c2b6834523` / `codex/physical-provider-integration-20261010` | PR94 temperature-underflow·PR95 current-field residual·PR98 SourceBoundConditional 통합. 이전 PR92/93 sibling 문제는 이 통합 경로에서 진전됨 |
| REI101 | `8722f3ab587399700d96d300b617f0f37f1d831a` / `research/cr-first-build-gate-20261010` | source/binary receipt를 Popen보다 먼저 검사. 새 bounded CR adapter의 권장 출발점 |
| REI99/100 | `05c45c3239adae63e715fd3598dbd0c53b42f667` / `8a80fa9742573e3fdc8d64df9339fa3ef3ad5ef2` | frozen diffuse screen / raw 5000 K coefficient diagnostic. 각각 diffuse closure·cold history를 채택한 결과는 아님 |
| BASS136 | `220d765f1df3803e6d4e3e3ad92d31ff421165ec` / `research/rei-pr96-bass-snapshot-readback-20261010` | REI96 17개 warm snapshot의 실제 ElectronState·legacy receiver readback. CR input·τ 적분 아님 |
| REC81 | `d74fc9e78d1cf707eef2d16fe771b4d8eb72cd7f` / `forward/rust-he-sources-20260922` | 이전 head 그대로. selected-He SI ledger 재사용 가능; CR degradation provider나 cold IC가 아님 |

기존 IGM owner branch `forward/rem-hhe-igm-20261006`은 `39c39eab1cc2f1a215723680accc123e67ef13b6`다. REI83의 별도 `forward/rust-reion-kernels-20260922` head는 `718468dc75cb81fdfe0f2792aab5c8d0dbc54607`로 전진했다. 서로 다른 branch와 물리 입력 패키지를 동일 head로 취급하지 않는다. 각 PR URL·본문·source path/blob·열람 범위는 REI_CURRENT.json에 보존했다.

## 실제 Rust 연결점

**1. 공통 침적 ledger.** REI101의 `rust/rei_microphysics/src/axisym_coupling.rs`에서 `AxisymLocalSources`는 proper SI의 species 13개, electron, photon-number source와 photon/thermal/internal/escape/external power를 받는다. `axisym_coupled_derivative`가 실제 isotope EOS, -3H 희석, -5Hu 열에너지 항, photon -4Hε−2sΔp를 결합한다. 이 소스는 compensated sum으로 baryon/charge/power를 검사한다.

CR 침적을 받는 새 adapter는 H/He별 ionization event count를 ionic slots 및 electron source에 한 번씩 배정하고, threshold power는 internal, heat는 thermal, 실제 재주입 광자는 photon, 빠져나가는 에너지는 escape로 보낸다. 현재 ledger는 **species baryon source의 합이 0**이어야 한다. 외부에서 들어온 projectile 핵을 ambient gas에 바로 추가하면 이 계약과 충돌한다. 그 경우 CR population·누적 입자 저장소와 열린 baryon 회계를 별도로 명시해야 한다. 비열적 secondary electron을 바로 all-thermal EOS에 넣는 것도 별도의 equilibration/deposition 가정 없이는 허용되지 않는다.

**2. Frozen warm 경로.** `axisym_conditional.rs`의 `SourceBoundConditional::bind`는 고정된 HM12 입력 여섯 개 hash만 받는다. `ConditionalStage`에는 photon node가 있으며 charged injection·CR energy distribution field는 없다. CONTRACT는 CR/RCT/HH OFF, primary-only photoheat와 Case-A recombination escape다. 따라서 새 provider는 별도 이름의 opt-in CR contract/adapter로 연결하고 기존 warm 경로를 regression으로 보존해야 한다. HM12 emissivity를 charged-particle source로 재해석하지 않는다.

**3. 분율 구조체와 provider 구분.** `axisym_sources.rs`의 `ExcessPartition`은 heat·secondary_ionization·excitation·escape의 비음수/합계1 검사와 manufactured photo event ledger를 제공한다. 모듈 주석 자체가 H/He RHS 미연결이라고 명시한다. 이 구조체는 실제 energy/ionization/composition-dependent deposition 표가 아니며, secondary power 하나로 H/He event yields를 결정할 수 없다. 새 provider의 raw bytes, kinetic-energy convention, state coordinates, H/He별 yields 및 interpolation/domain을 먼저 결합해야 한다.

**4. 실제 build gate.** `python/source_bound_interval.py`는 `NativeConsumer` 생성 때뿐 아니라 main 진입 시에도 `validate_build_receipt`를 먼저 부른다. `conditional_build.py`는 Cargo·전체 Rust source·launcher/gate와 실행 파일의 hash를 묶는다. 게시된 closeout은 clean built revision `f9135eca0d41dd00465fcd524c07872a9c3c8fb8`, binary SHA256 `e098111ee8e403c5985fea20cfca7b0408e5d82ea77c2eded50cff72d1392d0f`, build-only PASS, solver interval0/binary launch0을 보고한다. metadata head8722f3ab와 built revision은 다르다. 이번 intake가 binary를 내려받아 재검증한 것은 아니다. 새 CR source를 추가하면 consumed source가 바뀌므로 새 clean build receipt가 필요하다.

**5. 저온 경계.** `ft03_rates.rs`의 실제 `ft03_coefficients`는 30000–110000 K 밖에서 `FT03_TEMPERATURE_DOMAIN`을 반환한다. PR100의 raw 5000 K coefficient parity는 이 guard나 thermal closure를 바꾸지 않는다. CR provider와 침적 adapter 단위는 지금 구현·검증할 수 있지만 cold IGM history가 이로써 자동 완성되지는 않는다.

## BASS/REC 수신 계약

BASS136의 새 `_rustcore/examples/rei_pr96_snapshot_readback.rs`는 `[time_s,nH_cm3,nHe_cm3,xHII,xHeII,xHeIII]` 여섯 열을 받는다. proper cm⁻³→m⁻³를 한 번 바꾸고 `ne=nH*xHII+nHe*(xHeII+2*xHeIII)`를 사용한다. zero material tilt에서 두 직교방향 Thomson rate를 반환한다. legacy photon/group fields는 inert fixture이며 source의 2904개 photon node를 네 그룹으로 축약한 것이 아니다. 새 CR snapshot은 새 source manifest로 이 수신기를 재사용할 수 있으나 기존 REI96 warm validation을 옮겨 붙일 수 없다. nonthermal electron 또는 relativistic CR 산란을 이 thermal Thomson receiver에 자동 포함하지 않는다.

REC81 `ledger.rs`에서 실제 읽은 범위는 83–139,149–166,459–492행이다. `HeEventLedger`의 species·photon number·p_internal·p_gamma·h_kin 분리 및 `HeEnergies::canonical_si`를 확인했다. legacy canonical은 eV이므로 SI 변환을 중복하거나 생략하지 않는다. 이 donor는 selected-He 반응 ledger이지 CR spectrum·cold cosmological IC 공급기가 아니다.

## 지금 가장 가치 있는 bounded 단위

1. 외부 charged injection의 species, kinetic/total energy, spectrum, normalization, proper/comoving/per-H clock·단위와 support/tail을 고정한 record.
2. 실제 침적 표를 H/He ionization event·excitation·heat·escape로 변환하는 component. tabulated energy/state domain 밖은 fail-closed이며 실제 없는 분율을 0으로 채우지 않는다.
3. `AxisymLocalSources`로 연결하는 새 opt-in CR boundary. projectile population과 ambient gas의 baryon/charge 회계를 분리하고 energy 저장소의 소유자를 명시한다.
4. 새 source/binary receipt 및 동일 fixed gas state에서의 bounded receiver 검증. 기존 COMMON18/17-epoch warm campaign 재실행은 필요하지 않다.
5. 새 CR history가 실제로 생긴 뒤 새 identity를 가진 BASS snapshot export. 현재 BASS136 unit/frame 구조를 재사용한다.

## 열람 범위와 실행 가능성

- PR 최근 목록: REI/BASS/REC 각각 updated 순 15개에서 필요한 18개 record를 보존했다. REI의 `cr`, `physical` branch-name 검색을 추가했다. 현재 미공개 local 작업의 부재를 주장하지 않는다.
- pinned source13개를 fetch했고 전체/선택 열람 범위를 JSON에 기록했다. REI/REC complete tree에 해당 root/Rust subtree의 AGENTS.md가 없음을 확인했다. BASS root→_rustcore→examples의 세 directory에도 AGENTS.md가 없다. docs에 보관된 다른 repo의 AGENTS는 이 receiver 지시로 취급하지 않았다.
- 게시된 `PHYSICAL_INPUT_DECISION_MINIMAL_V1.md` version2(실제 본문 V3,110행)와 `SYNTHESIS_REPORT_CR_FIRST_V1.md` version2(본문 CR_FIRST_V3,86행)를 완독했다. 두 문서의 build-blocked 서술 이후 PR101 closeout이 진전됐다. 문서의 미서명 체크리스트는 이번 사용자의 새 bounded 실행 지시를 취소하는 별도 승인 규칙이 아니다.
- `1903`, CR_FIRST, R17B1 및 recent physical-provider 검색에서 19:03의 특정 artifact는 식별하지 못했다. 이는 해당 thread의 업데이트가 없다는 뜻이 아니다. 별도 HE 최신 E13C1 게시물(09:47UTC)은 surfaced했지만 이번 REI/BASS/REC 역할에서 본문을 확장해 읽지 않았다.
- 실제 `git ls-remote https://github.com/cosmosapjw-quantum/rei_bianchi.git`가 exit0으로 PR101/IGM base ref를 반환했다. Git transport 접근은 확인됐고 전체 clone 완료는 아직 시험하지 않았다. pinned raw text download도 성공했다. generic GitHub fetch는 UTF-8만 지원하므로 binary archive 다운로드 가능성을 이 결과로 주장하지 않는다.
- 읽기 실패 한 건: 추측한 `src/ft03.rs`가404였다. 실제 tree에서 `src/ft03_rates.rs`를 찾아 읽었으며 과학 실패로 분류하지 않는다.

전체 scientific admission은 이번 intake의 판정 대상이 아니다. 기존 warm conditional 완료 범위와 이번 CR provider component 목표를 구분해 후속 실제 실행·독립 리뷰로 닫는다.
