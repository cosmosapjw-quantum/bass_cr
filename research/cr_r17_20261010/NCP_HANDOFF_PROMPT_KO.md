# NCP local Codex: bass_cr R17B source-kernel goal certification

당신은 NCP에서 cosmosapjw-quantum/bass_cr만 담당한다. 다른 저장소는 read-only donor다. 계획만 작성하지 말고 가능한 범위의 실제 구현/구간계산/검증/게시를 수행한다. 원본, main, producer defaults, 기존 dirty work를 수정하거나 force push하지 않는다.

## P0. 입력과 완료 범위

브랜치 research/cr-r17-source-goal-20261010을 fetch하고 actual HEAD와 AGENTS를 읽는다. R17A 과학 시작 commit은26e8707157217068ad9a294c4185c1b9127fa676, 부모 R16B는997281e566a60c71554192a6d653aa82c29cd2f7이다. README_KO.md, src/causal_source.py, inputs/R17_COMPACT_INPUT.json, portable.py가 이 디렉터리의 Git-only 실행 계약이다. R17A 핵심 exact 계산은 외부 ZIP 없이 python -B research/cr_r17_20261010/portable.py --output NEW_RESULT.json으로 재현 가능하다. 단순 동기화를 위해 완료된 R16B/R17A suite와 부모 native/root를 다시 실행하지 않는다.

동결 R17A: source-only abs radius2.125533135951863662132892058883214693751…e-18. R16B time+[source once]은[1.726968178866034690190055439800249300664…e-17,2.219287238809879417339730677747077477803…e-17]. Generic core는 test한7430bytes, blob a5381e42966ed849f09b550bde894dfb901f8d08이다. 원 whole-data evidence/tests/logs 및 상세 유도는 별도 불변 ZIP과 DELIVERY_RECEIPT.json을 따른다. compact 숫자는 원 selected bytes로부터 exact Fraction으로 만들어 full 경로와4개 결과가 정확히 같다.

Heavy R17B 입력은 NCP의 기존 R16B/R16 cache를 먼저 읽는다. 필요한 원본을 사용자에게 다시 업로드하라고 하지 않는다.

- BASS_CR_NCP_R16B_20261009_v1.zip:26999284bytes,SHA256 c753f152bd6ac55cf12ae264d25ab8297d74e8d15c230d0d73721ce8418be8a3; Drive1mQsDsV73buNoEQPNo6Vaqpn75hxPFu1K,Dropbox id:BSpOijBcT10AAAAAAD3jkg.
- REI_XTHREAD_BRIDGE14_20261008.zip:517269bytes,SHA2565fc3b77d9a17553f7cd34f61711983776edbb992ba9ebd294420b9813a818515; Drive1ECnf_hQSnjUTt60IfpcZO1e5wFwwv-70. BRIDGE13은 R16B→R16→R15의 nested input에 있다.

원 archive/manifest/선택 source identity를 확인하되 부모 proof 전체를 재실행하지 않는다. NCP에 cloud 인증이 없고 원본도 없으면 해당 lane만 BLOCKED_INPUT_AUTH로 기록한다. connector 권한이 NCP에도 자동 존재한다고 가정하지 않는다.

## P1. 정확한 새 연구 목표

동일 FT03 first macro0..1.25e9 proper s,H=f64(1e-14),nH0=f64(1e-4),fHe=f64(.083), 원 .05/H 초기광자와 gas/energy family, 원 six birth-time/positive weight boxes를 유지한다. 비교는 µS=Sdb,S=f64(5e-15) 대µQ=Σwδb이며 HH/RCT/CR OFF다. He photo inactive인 원 에너지 범위만 사용하고 HHe nonphoto/thermal feedback는 유지한다. Grackle IGM/35eV RCT/frozen-hazard toy로 바꾸지 않는다.

새 목표는 R17A가 절댓값 envelope에서 버린 signed source cancellation을 optical goal에 대해 실제 검증하는 것이다. 다음 두 경로 중 첫 bounded panel의 결과를 보고 하나를 선택해 명시한다: (A) positive source homotopy 전체의 kernel enclosure, (B) 한 base kernel과 검증된 nonlinear source remainder. 둘을 무기한 병렬 탐색하지 않는다.

## P2. Source-measure/adjoint 수학 계약

ν=µS−µQ, µθ=(1−θ)µQ+θµS,θ∈[0,1]. 같은 initial photons는 별도 common atom으로 보존한다. 고정 gas path에 대해 R_G(t,b)=exp[-∫b^t κ_G(u,b)du], E(t,b)=Eb exp[-H(t-b)], κ_G=c*nH(t)*(1-h(t))*σHI(E(t,b))다.

Gas RHS는 원 F_nonphoto에 [κR,0,0,(E−χHI)κR/W0]의 µθ 적분 및 original initial-cohort 기여를 더한 것이다. µθ의 gas trajectory는 true coupled path이며 frozen gas로 대체하면 안 된다.

u_{θ,b}(t)를 b에서 단위 photon injection에 대한 전체 gas+photon linear response로 정의한다. gas는 b에서 jump하지 않고 test photon만1/H 주입된다. κ의 gas dependence와 survival feedback를 모두 미분한다.

    Kθ(b)=CT∫b^T nH(t)*(1,fHe,2fHe,0)·u^gas_{θ,b}(t)dt,
    Kθ(T)=0.

Common positive solution-map의 source-measure differentiability를 정당화하면

    τS−τQ=∫0^1dθ∫Kθ(b)dν(b)
           =−∫0^1dθ∫Dν(b)*∂bKθ(b)db.

Kθ(T)=0이 아닌 관측량에는 mass defect Dν(T)Kθ(T)를 포함한다. 원 weight boxes를 총질량이 맞도록 바꾸지 않는다. θ 평균을 사용하지 않고 한 base의 K만 쓰면 nonlinear remainder를 별도로 제한한다.

R16B의 기존5→11D adjoint는 이미 존재한 여섯 cohort의 time-residual용이다. 임의의 연속 birth b에서의 injection kernel을 그 여섯 값의 interpolation으로 인증할 수 없다. 공통 birth-coordinate Volterra/transport response 또는 동등한 validated formulation을 실제 구성한다. Point finite differences/fit/midpoint Jacobian/수치 수렴비는 proof premise가 아니다.

각 atom birth는 θ family의 명시적인 경계다. Gas의 고차 미분이 global C4라고 가정하지 않는다. High-order Peano/Gauss를 쓰려면 regular intervals, jumps, stored-node/weight representation defects가 모두 필요하다. 원 첫 macro에 없는 future cutoff를 끌어오지 않는다.

## P3. Bounded implementation/acceptance

먼저 실제 하나의 source 구간에서 K'_θ 또는 signed action+nonlinear remainder의 전시간 포함을 닫고, 그 후3source cells/6birth/32timecells로 확장한다. 같은 θ의 birth labels와 gas source correlation, nonzero incoming errors, accumulated tau를 보존한다. No reset at births.

새 signed source interval 또는 절댓값 상단을 제공한다. R17A radius보다 더 좁힌 인증이 없으면 NO_CERTIFIED_SOURCE_SHARPENING으로 종료하고 R17A를 유지한다. 수치점 추정이 작다는 이유로 성공이라 하지 않는다. 새 source interval은 원 R16B time interval에 정확히 한 번만 더한다. 기존 R17A total에 또 source bound를 더하지 않는다.

Focused tests: orientation µS−µQ, K(T)/terminal mass term, source mass mismatch, constant kernel, same-mass different birth-time, θ correlation loss, missing nonlinear remainder, wrong scale/clock/domain. 실제 새 heavy kernel에는 independent MPFR/고정밀 또는 별도 interval propagation을 둔다. 공유 interval RHS 여부를 밝히며 propagation 독립성을 full RHS proof라고 부르지 않는다.

자원: 실제 NCP cpuset/cgroup/RAM/disk를 확인하고 coordinator1CPU 및16–24GiB RAM을 예약한다. independent b/θ subproblems에 한해 bounded process를 쓰고 BLAS/OMP thread1. fastmath/Ofast/무제한병렬/허용오차 완화 금지. 기존8worker가 현재도 자동 승인됐다고 가정하지 않는다. Command/exit/peakRSS/실패를 기록한다.

## P4. 배포와 반환

새 bass_cr-only branch에 non-force push한다. README/DERIVATION/SOURCE_BINDING/RESULTS/CLAIM_GATE/VERIFICATION/RECOVERY_INVENTORY/NEXT_HANDOFF, 실제 source/raw logs/failure records와 immutable ZIP을 반환한다. 과학적으로 종료한 parent suite를 동기화만으로 반복하지 않는다.

Drive parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ, Dropbox /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1에 create-only 백업하며 actual ACK/ID/size가 있을 때만 R1이다. 없으면 NOT_UPLOADED를 정확히 기록한다. R1은 restore와 다르다.

최종 BASS_CR_NCP_R17B_RETURN_KO.md 및 BASS_CR_NCP_R17B_RETURN.json과 detached receipt를 제공한다. R17A core/compact input은 Git에 있으므로 그 재현에 사용자 파일전달이 필요하지 않다.

CR_OFF_FASTEST,precision atomic PARKED,HH ACTIVE,G02 UNRESOLVED,b_grid NO_GO,all_bound OPEN,physical/production HOLD 유지. Grackle BLOCKED_OWNER_INPUT와 G02 BLOCKED_INPUT는 실제 새 input이 없는 한 유지한다. REI BRIDGE17의 canonical checkpoint 업무를 대신 수행하지 않는다.
