# NCP local Codex R16 후속 실행 handoff: bass_cr only

너는 NCP에서 **`cosmosapjw-quantum/bass_cr` 저장소 하나만** 수정·실행·게시하는 local Codex다. 관련 `rei_bianchi` BRIDGE13/14/15, `BASS_HE`, `WU088_HH`는 오직 provenance를 유지한 **read-only donor**로 취급한다. 이 계획은 구현을 시작하라는 실행 계약이다.

## P0: 소스·환경 고정

1. GitHub의 `research/cr-r16-optical-adjoint-20261009` HEAD를 실제로 fetch하여 아래 세 파일을 읽는다: `docs/cr_r16_20261009/REPORT_KO.md`, `docs/cr_r16_20261009/NCP_HANDOFF_PROMPT_KO.md`, `research/cr_r16_20261009/SOURCE_BINDING.json`. 현재 HEAD가 이 프롬프트의 SHA와 다르면 nonforce/compare 후 새 worktree를 만든다. 사용자 dirty branch 또는 main을 reset하지 않는다.
2. 이미 백업돼 있는 immutable `BASS_CR_R16_THEORY_20261009_v1.zip`을 이 보고서에 기록한 Drive/Dropbox object ID에서 회수해 SHA256/size/manifest/CRC를 모두 검증하고 **새 디렉터리**에 복원한다. ChatGPT connector 권한이 NCP에 있다고 가정하지 않는다. 만약 remote credential이 없으면 기존 NCP R15 source path를 탐색하고, 해당 ZIP의 부족함만 `BLOCKED_INPUT_AUTH`로 기록한다. 비밀/토큰 출력을 요구하지 않는다.
3. `python -B reproduce.py --verify-only`를 먼저 실행해 정본 확인. 시간이 허용되면 `python -B reproduce.py --output NEW_DIR`로 **R16 새 코드만** 재현하고 결과를 별도의 checksum receipt로 비교한다. 부모 R15 32-cell certified source 또는 REI BRIDGE14 producer 계산을 동기화 이유로 재실행하지 않는다.
4. 실제 NCP cpuset/cgroup/CPU/RAM/disk/scipy/rustc/MPFR/Wolfram 등 환경을 실측하고 자원 reserve(최소 코디네이터 1 CPU + RAM 16–24GiB)를 잡는다. 저밀도 ODE 지연으로 1·2·4·8 worker pilot 후 실제 RSS 범위에서만 병렬화한다.

## P1: R16B certified time-dependent signed adjoint, **새 heavy 과학 작업**

### 고정 목표 및 수학

원 target은 **FT03 첫 macro `t∈[0,1.25e9] proper seconds`**, 동일 6 finite births, 원 `variant=0` 연속시간 H/He collision/photo/thermal, `HH/RCT/CR OFF`, `H=1e-14 s^-1`, `nH0=1e-4 cm^-3`, `fHe=.083`, `C_T=c_SI σT_SI 1e6`, 동적 `nH(t)=nH0 exp(-3Ht)`다. R15 원 endpoint-binary64 gas linear reconstruction과 native photon pulse identity를 유지하고, 밀도/광자시간/정규화/원 source coefficient를 변경하지 않는다.

각 cell normalized s에서 `e=z_true−zhat`, `r=zhat'−F_s(zhat)`를 사용한다. Born cohort가 생기는 event에 대하여 `e^+=B e^-+δ`, `B`는 old-state embedding, `δ`는 원 source weight와 nominal pulse 차이 및 인터페이스 불연속을 포함한다. 이 6건의 gas jump는0이지만 새 photon 오차/원 parameter family를 0으로 바꾸면 안 된다. Adjoint는

`−λ'=Ahat(s)^T λ+g(s)`, `λ(T)=0`, `λ_before=B^T λ_after`.

목표 항등식

`Δτ = λ(0)^T e0 − ∫λ^T r ds + Σ_events λ(tj+)^T δj + ∫λ^T(F(zhat+e)−F(zhat)−Ahat e) ds`

에서 마지막 비선형 remainder를 **실제 validated interval/Hessian 또는 secant-Jacobian enclosure**로 제한한다. 각 구간의 time-dependent signed Jacobian은 원 FT03 interval AD에 기반해야 한다. 단순 midpoint Jacobian·17/33 node cubic residual interpolation을 interval 증명으로 승격하지 말 것.

추천: 원 16 residual panels/cell 및 R14 첫 64 panels의 signed interval을 활용하고, 32개 physical Picard tube에서 `A(t)`·`D²F`를 outward directed ops로 감싼다. 시변 선형 backward adjoint는 validated fundamental-matrix Taylor/interval Magnus/Volterra remainder로 감싸며, 양/음 offdiagonal과 공통 θ birth coupling을 보존하는 affine enclosure를 우선 검토한다. Source cutoffs는 이번 first macro 내 통과하지 않는다는 donor 가정과 실제 energy trace를 확인하라. 일관된 big-n array는 birth에서 5→11차원으로 변한다.

**승인 기준**: (i) every-cell right/left clock and photon birth; (ii) R15 old certified signed interval `[1.84951686695,2.10105887627]e-17`과 실제 새 interval의 비어 있지 않은 교집합; (iii) independent high-precision/primal-dual check; (iv) full-time interval backend 소스/상수/pins·부동소수점 provenance; (v) 보수적 bound가 기존 R15보다 좁으면 실제 개선, 같거나 넓으면 `NO_CERTIFIED_SHARPENING`으로 정직하게 보고. Certification이 성립하지 않는다면 `NUMERICAL_DIAGNOSTIC_ONLY`를 유지한다.

수치 참고 기준 (certification input 금지): R16 한 cell당 midpoint A, 33 residual interpolation sample의 forward goal `1.9731044416400455e-17`, backward dual `1.97310444167335e-17`; archived nonlinear R15 DOP853 `1.9731045074324378e-17`. Adjoint sign 및 이벤트 transpose를 틀리게 구현하면 5→11D 테스트가 실패해야 한다.

### Source+time 결합 결과를 유지

R16A `COMBINED_TAU.json`는 REI BRIDGE14의 **조건부 source-only partial τ bound**와 R15 time error를 같은 model/source family에서 합한 정확 유리수 결과다.

`Δτ_continuous_constant_S_minus_native ∈ [8.277438669507532e-18,3.122831876267941e-17]`.

이 구간은 **같은 θ 첫 macro에 한정된 조건부 sign result**로 닫힌 것으로 취급한다. 시변 adjoint가 검증되면 원 R15 시간항을 갱신해 source-upper와 다시 합하되, BRIDGE14 source 오차를 두 번 넣거나 상대 project의 추후 BRIDGE15 native ledger f64 결과로 τ를 좁히지 말라. BRIDGE15 조건부 no-FMA ledger는 별도의 native owner gate다. 실제 continuum emission S와 여섯 birth의 차이를 단순한 frozen κ fourth-derivative로 대체하지 말라.

## P2: 선택적 Grackle owner 연결 (distinct model)

`bass_cr` R13 full Grackle IGM point, R6 midpoint+ledger path는 기존 완료 연구다. 실제 동일 source/config/clock/accepted owner stage/whole-time state+Gamma+incident-energy moment가 **제공된 경우만** 새 source residual bound를 계산한다. 없으면 `BLOCKED_OWNER_INPUT`. R13 96 point/R6 tolerance sweep을 반복하지 말고 R15/R16의 FT03 결과를 Grackle 물리자격으로 승격하지 말라.

## P3: G02 evidence gate (independent)

기존 `G02_READINESS.json`에서 원 bank/candidate/SCIENCE_CONTEXT/native SHA와 actual bytes를 확인한다. 없다면 `BLOCKED_INPUT`; b-grid `NO_GO`, G02 `UNRESOLVED`, all_bound `OPEN` 유지. 무단 production 50/225keV/u campaign 금지.

## 테스트·Git·백업·반환

- baseline source ZIP/data는 immutable이며 업데이트할 수 없다. 신규 module은 **new bass_cr research branch**에서 독립 구성하고 source·unit·numeric·interval·loss-of-correlation·wrong-birth-injection 검사를 TDD RED→GREEN으로 기록하라. Python/Julia/Rust 등 계산 내용은 명시적으로 재현 가능해야 하고 원 연구 suite의 불필요한 rerun 금지.
- 새 진단과 인증의 의미를 구분하라: model/clock/θ/source identity, local residual, f64 arithmetic, goal enclosure, continuous emission source error, native ledger, physical fit, observational tail. 원 `CR_OFF_FASTEST`, precision atomic `PARKED`, HH research `ACTIVE`, `G02=UNRESOLVED`, `b_grid=NO_GO`, `physical/production=HOLD`, global CR counter/owner ACK/tail=null 유지.
- git non-force push + 선택적 readback(R1), Google Drive folder `1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ`와 Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1`에 새 봉인 ZIP create-only upload. 실제 provider 완료 ACK/name/size/remote ID 확인 전에는 이중백업 완료 주장 금지. R1≠full restore/R3.
- 새 산출물: `R16B_REPORT_KO.md`, `R16B_THEORY.md`, `R16B_SOURCE_BINDING.json`, `R16B_EXECUTION.json`, `R16B_VERIFICATION.json`, `R16B_RESULTS.json`, `R16B_CLAIM_GATE.json`, `RECOVERY_INVENTORY.json`, `R16B_NEXT_HANDOFF_KO.md`, `BASS_CR_NCP_R16B_RETURN_KO.md`, `BASS_CR_NCP_R16B_RETURN.json`, detached `DELIVERY_RECEIPT.json`, immutable ZIP+manifest+selected failed logs.
- 무거운 작업은 시작 즉시 실제 실행하고 입력이 부족한 각 lane은 해당 blocker만 보고한 후 다른 독립 lane을 계속한다. 사용자에게 기존 hash/파일명을 다시 묻지 말고 저장한 input manifest와 원격 repo/backup을 먼저 확인한다.
