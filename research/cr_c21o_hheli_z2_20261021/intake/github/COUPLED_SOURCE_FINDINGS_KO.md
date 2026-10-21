# C21O 최신 GitHub intake와 H/He/Li 구현 source 회수

## 가장 가까운 실제 구현

H/He/Li를 모두 활성화하고 양방향 Einstein·기체 열·광자 반응을 닫은 z20→2 실행본은 **이번에 직접 읽은 후보들에서 확인되지 않았다**. 대신 새 lineage를 구성하는 데 재사용할 수 있는 source와 원 입력을 회수했다. 아래 결손은 해당 source의 실제 코드와 계약에 근거하며, 접근하지 않은 다른 대화나 저장처까지 부재라고 뜻하지 않는다.

1. **BASS_HE HE31:** 기존 non-tilted full40 canonical FV에 전자 donor와 photon-only Thomson을 연결한 실제 Python 경로다. `receiver.py`는 기존 40성분에 optical depth 한 진단 상태를 더하고 기존 RHS를 적분한다. `electron_donor.py`는 proper/comoving census, SI/cgs, 범위 밖 거절 및 PCHIP를 제공한다. 실제 donor는 다른 FLRW Q model의 z20→4 이력이고 HII=HeII=Q, HeIII=0, residual electrons 없음이다. 원 report는 donor→target이 일방향이며 massive nonbaryonic matter와 baryonic census를 구분한다. 실제 on/off/reference 3개 성공 궤적이 있지만, full HHeLi 또는 z2 donor 완성으로 수용하지 않는다.
2. **PR150 Grackle H/He:** `igm_rates.rs`는 Grackle 3.4.1 commit `af7939494ce65007887ada7b98d1813df6843346`의 Case-A CI/RR/DR·냉각 subset을 구현한다. package domain은 1–10^6 K이며 원 literal/floor/cap을 명시한다. 이는 empirical validity 전체의 보장이 아니다. `igm_thermal.rs`, `coupled_primary.rs` 및 `axbi_driver.rs`를 함께 회수했다. 원 AXBI driver는 z_end≥4를 검사하며 metadata에 prescribed-background perturbative feedback이라고 기록한다.
3. **RUN13 H/He/D native:** `full_network.rs`는 처음에 주어진 finite photon bins와 고정 체적의 finite-time reference다. 활성 chemistry는 H1/He4/D이고 나머지 13-state 성분은 spectator다. “full_network”라는 파일명이 cosmological full isotope network의 완료를 뜻하지 않는다. RUN19는 이 native owner를 유지하며 계수 준비·캐시·batch를 추가했다.
4. **PR150/RUN19 Li6/Li7:** `lithium_rates.rs`에는 각 isotope의 q=0,1,2,3, 즉 LiI–LiIV가 존재한다. CI/RR/DR source-backed number kinetics와 전자수 기여를 제공하지만 photo·thermal·abundance closure는 별도다. `ElementalElectronicEquality`를 명시적으로 선택해야 하며 isotope-resolved coefficient 요청은 `MissingSource`, Li8/Li9는 `PendingNuclearDecayDaughterClosure`다. 전체 bundle의 온도 공통 범위는 5 eV/kB≈58,022 K부터 10^7 K다. 10,000 K에서 전체 bundle을 사용하거나 영역 밖 CI를 0으로 대체하는 것은 이 source 계약에 없다. RR의 개별 범위는 q=1/2/3에 각각 10/40/90 K부터라 개별 channel API와 bundle을 구분해야 한다.
5. **R9 Unit8 Python:** `li_thermal_rates.py`는 원저자 Verner shell photo cross section, Milne ground-channel thermal integral, VF1996 total RR를 직접 제공한다. H I/He I/He II/Li I/Li II/Li III 여섯 채널의 원자 계수이며 LiIV는 마지막 charge reservoir다. 원 Python kinetics는 z100000→10000, first13 frozen fully-ionized bath와 trace Li7+Be7 EC의 early 계산이다. 원 독립 BDF reference 실패는 HOLD로 남으며 late EoR 결과로 재분류하지 않는다.

### 원자 입력의 실제 회수

`primary_atomic_inputs/`의 여섯 파일을 원저자 URL에서 실제 내려받았다. 각 파일이 R9 frozen contract의 원 SHA256 및 크기와 정확히 일치한다. 총 396,115 bytes이며 전체 archive는 다운로드하지 않았다. `SOURCE_RECEIPT.json`이 입력별 URL/hash를 결속한다.

Python Provider의 최소 초기화 입력은 `phfit2.f`, `photo_table.dat`, `partial_table.dat`, `rrfit.f`, `rr_table.dat`와 `sources/R9_LI_CONTRACT.json`의 `atomic_channels`다. 이 intake에서는 Provider를 실행하거나 새 계수·ODE 결과를 생성하지 않았다. `rr_description.txt`는 단위·표 설명이다. 코드나 수치를 새 lineage에 사용할 때 원 source별 pin, 모델 선택, 온도·에너지 범위와 결손을 다시 명시해야 한다.

## 17/21-state census의 실제 의미

R9 dossier의 core17은 다음 순서다.

```text
n,
H0,H+,
D0,D+,
T0,T+,
He3(q0,q1,q2),
He4(q0,q1,q2),
Li7(q0,q1,q2,q3)
```

LiIV는 빠진 상태가 아니며 마지막 Li7 q3이다. PR150의 registry는 여기에 Li6 q0–q3을 추가한 **21-state union**을 보존하지만 `coupled_21_state_solver_implemented=false`를 명시한다. 기본 runtime `isotope_state.rs`는 Li를 제외한 13-state이다. 따라서 registry 개수와 실제 활성 ODE state를 혼동하면 안 된다.

Be7는 core17/21에 합쳐진 Li7가 아니라 별도 reservoir다. Unit8 early 모델은 살아남은 Be7 q3/q4와 EC-origin Li7를 구분한다. 원 BBN large donor의 59 nuclide inventory는 전체 59원소 late atomic network를 뜻하지 않는다. 작은 BBN8→core17 사상도 `CONDITIONAL_BARE_CHARGE_BOOKKEEPING_NOT_SOLVED_ATOMIC_HISTORY`다. Core를 1로 재정규화하거나 누락 isotope를 측정된 0으로 표시하지 않는다.

## 최신 refs/PR 조사 범위

2026-10-21 14:42:26–14:42:28 UTC에 7 repository의 `git ls-remote --heads`가 모두 성공했다. **1,246개 advertised heads**, 이전 13:06의 1,240 대비 신규6, 변경4, 삭제0이다. 모든 원시 heads와 전체 map 및 delta를 보존했다. 별도로 repo별 최근 갱신 PR 40개, 총280개 metadata를 읽었다. 이는 모든 historical PR 본문 또는 모든 branch source의 전수 독해를 뜻하지 않는다.

| Repository | Heads | 신규 / 변경 | 실제 분류 |
|---|---:|---:|---|
| bass_cr |172|2 / 0|이미 수용한 PR94 NCP4, PR95 sandbox4+동일 NCP4 addendum; 고유129 유지|
| BASS_HE |89|1 / 0|PR84 HE31 electron donor와 prepared evaluator; z20→4 일방향 donor 경로|
| WU088_HH |141|0 / 1|PR132 PHYS77 one-cell signed enclosure; 세 prefix 요청 READY_NOT_RUN|
| bass |264|1 / 1|ACCEL02/03 warm C15 source 및 NCP5×2 저장 분석; 별도 lineage|
| rec_bianchi |136|1 / 0|PR118 160-state tangent/JVP/VJP; tiny parent+augmented2 완료 보고, full-window3 READY_NOT_SUBMITTED|
| vigilode |186|0 / 0|광고 branch ref 변경 없음; 이전 solver 근거 유지|
| rei_bianchi |258|1 / 2|PR217 warm 분석, PR215 native donor, PR199 native time8/16/32 반환·진단|

REI PR217와 BASS PR179는 같은 warm NCP5/two-step 결과의 mirrored 분석이다. 729 warm baseline, NCP5×2, collisionless125+4, HE30/REC117/HH76 z2 tails를 서로 합해 새로운 독립 HHeLi ensemble로 세지 않는다. REI PR199 최신 source에서 time8/16/32가 이미 완료된 것을 확인했으며 다시 실행할 일이 없다. 원0.005 목표 미달과 native age/time convergence HOLD는 그대로다. PR199 문서·PR 본문의 역사적 head와 현재 advertised head는 구분한다.

PR95의 현재 REST PR metadata는 여전히 첫 content `e7729092abc6edbe74f31d0ed82aa84d5506b8d5`를 가리키지만 advertised branch는 `8dc5031b3323d4be42a7444843294200aa8887f2`다. 기존의 `PR_HEAD_METADATA_MISMATCH_UNRESOLVED`를 유지한다. 원격 mutation을 하지 않았다.

## 고정 source identity

| 후보 | 고정 HEAD / 실행 pin | 이번 읽기 수준 |
|---|---|---|
| BASS_HE PR84 |HEAD `88e415c45d8607c85cd3ab36aabeaed4378820ce`, 실행 pin `1c8a56aac89d0e40ede8770009f80ebca40a4d2c`|README/report·실제 Python receiver/donor/bindings; 새 raw 전부 재다운로드는 하지 않음|
| REI PR150 |`fd9a21c4d3886a495540b51d780a83b608e72ea2`|실제 HHe/Li/isotope/thermal/coupled/AXBI Rust source 및 species/rate tables|
| REI PR211 RUN19 |HEAD `c9deb933761a8d2593d1176aee028cd423bdbc05`, science `e540256ecf77df1c88fccb57b81d5d60110f367c`|원 RUN13 full_network/mixture, Li backend,19반응 계약·resume|
| REI PR151 Unit8 |HEAD `8a4f5df46f6e3058f5e685b85cc1cf3c20926368`, Unit8 content `6391f3f8bbf34f16c7b36013d424183786a51086`|실제 Python rates/run, Li/17-state 계약, 보고서·공식 atomic source6개|
| REI PR199 |`cce008b3fc32c298185b30550b2cd909d74fcd87`|현재 README의 완료 time8/16/32·HOLD 확인; 이 intake에서 raw 수용이나 검산 반복 없음|

`SOURCE_EXPORT_RECEIPT.json`은 실제 회수한 16 source text, 총302,905 bytes를 결속한다. 그중14개는 별도 GitHub directory metadata의 blob SHA1 및 크기와 대조해 일치했다. 나머지2개는 pinned raw URL 회수/hash 기록 수준으로 명시한다. 공식 atomic6개는 별도 원 계약 SHA256/size 대조를 모두 통과했다. GitHub 본문에서 보고된 build·runtime·검증은 작성자 보고 근거이고 이번 intake가 다시 수행한 빌드·검증으로 세지 않는다.

## 다음 구현에 대한 좁은 권고

완료 collisionless source와 runs는 고정 보존하고, 새 H/He/Li lineage의 활성 species·원자 coefficient policy·초기 isotope abundance·source spectrum·열 closure·에너지 owner를 명시하는 것이 먼저다. HE31의 일방향 donor만으로 gas→H/σ feedback를 얻었다고 쓰지 않는다. PR147 canonical field에 새 gas thermal energy가 자동 반영된다고 가정하지 않는다.

회수한 원자 모듈로 새 trace chemistry 또는 명시적인 축약 coupled 모델을 구성할 수 있지만, 선택한 closure와 빠진 항목을 결과 제목·manifest에 나타내야 한다. Elemental equality·photo-only 또는 prescribed bath 같은 선택은 물리 가정으로 기록해야 하며 source에 없는 핵반응·collision·feedback을 0으로 숨겨 넣지 않는다. 모든 핵종과 전하 단계의 fully coupled history가 목표라면 그것의 미완성 부분도 DAG에 남긴다. 이 intake는 어떤 새 모델의 물리 승격도 부여하지 않는다.

| 상태 | 이번 단위 |
|---|---|
| EXECUTION | READ_ONLY_INTAKE_COMPLETE_SCOPED; 과학 실행/빌드/벤치마크0 |
| PUBLICATION | scratch에 source·receipt 준비; push/PR mutation0 |
| BACKUP | 이 subtask에서 provider 작업0; 별도 담당 intake와 구분 |
| DAG | 최신 delta 분류, reusable source 회수; 완전한 HHeLi z20→2 coupled sweep는 NOT_RUN |

`global_error_bound=null`을 유지한다.
