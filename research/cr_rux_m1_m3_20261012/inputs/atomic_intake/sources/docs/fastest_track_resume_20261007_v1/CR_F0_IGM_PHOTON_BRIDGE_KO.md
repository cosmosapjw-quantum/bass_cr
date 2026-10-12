# CR-F0-R1: fastest-track photon → IGM 소비기 연결

2026-10-07. 판정: SCOPED_NATIVE_PHOTON_IGM_CR_OFF_BRIDGE_PASS__OWNER_IMPORT_PENDING.

사용자의 fastest-track 재결합 요청에 따라 F04P 이론 상계의 추가 개선을 진행하지 않고 실제 광자 입력과 최신 IGM point RHS를 연결했다. F04P의 eps=.01 부호 미해결은 baseline 구현의 새 선행조건이 아니다. CR_ON_SCOPE/정밀원자 lane은 활성화하지 않았다.

## 실제 게시 코드와 입력

새 core code를 먼저 같은 branch에 게시했다.
- repository: cosmosapjw-quantum/bass_cr
- branch: research/r4q-gap-closure-20261001
- intake: fcf542d44d272567acc7cee55ee145bddfbd6794
- code commit: 3129089fe0f52739961cefc65cda71ccce0a07ab
- code tree: 2c8a9178322cbdb3e80b5bf2160328d84cf3dbb8
- code path: research/fastest_rejoin_20261007/cr_off_igm_bridge.rs
- code blob: 295bba19706090e5f889d1a0479715213e00c7f3
- code SHA256: e91aefcfbe9bdbf6c7acf7a50f1355b28cd19b3b813b4960f9c0ba17fcfb45bf

Git directory metadata의 blob/size5853은 시험한 src/lib.rs bytes와 일치한다. 실제 executable package의 Cargo files,23시험,probe,receiver import patch는 아래 ZIP에 있다. Git core source만 단독으로 compile되는 완전한 upstream workspace라고 주장하지 않는다.

Receiver 기준 및 게시 전 최종 read는 rei_bianchi@dbb54009a517242ff5a41c805512471a74dd25f4, forward/rust-reion-kernels-20260922다. 원 TASKS.json의 CR-F0는 실제 off interface의 no-load/no-callback, source0와 scope evidence를 요구한다. Original global DAG/task card의 receiver-binding 상태는 이 후보 결과로 임의 덮어쓰지 않았다.

실행한 원 scientific modules는 현 receiver의 whole-file blob에 결합된다:
- hhe_events.rs 57a63eee1e9d8c4aa2b5ed663dbea15619359f71
- atomic_provider.rs 62211d8910cd332fffa8f94c6989cae77128916e
- igm_state.rs 437365fbe329a10afe292f9dd7eebf549fef804c
- igm_rates.rs dc3cc028a41ac852d94835372ce13545389d1c3a
- igm_thermal.rs 0648618d9822e169e9672ac3c556f86595c3b0b6.

이 중 새 low-temperature IGM는 Grackle subset, 기존 F04P는 FT03 derivative-moment 모형이다. 전자의 실행 연결에 후자의 Q2/C3/finite-shear 인증을 이전하지 않는다. 원 provider의 guard/floor/cap/DR closure와 CMB reservoir를 보존한다.

## 물리식과 실행 계약

Gas-rest frame, proper nH/nHe[cm^-3], node energy[eV], bin-integrated/already angular-weighted p_j[photons/H]를 받는다. 즉시 photon loss와 gas point derivative를 반환하며 입력은 바꾸지 않는다.

    n_gamma,j = nH*p_j
    Gamma_a = c*nH*sum_j p_j*sigma_aj                 [s^-1]
    heat_a = c*nH*eV_erg*sum_j p_j*sigma_aj*(E_j-chi_a)
                                                     [erg/absorber/s]
    R_a = n_abs,a*Gamma_a                            [cm^-3/s]
    dp_j/dt = -c*p_j*sum_a n_abs,a*sigma_aj           [photons/H/s].

Gamma와 absorber당 heat를 직접 계산하므로 n_abs=0에서 총가열/n_abs 나눗셈을 하지 않는다. Photo cross sections는 현재 AtomicProvider의 실제 함수를 호출한다. CR provider 호출0과 모든 원자 provider 호출0은 다른 주장이다. 에너지 fit domain은 광자 수0일 때도 검사하며 physical binding과 fit threshold 사이의 passive gap을 임의 흡수로 채우지 않는다. c,kB,eV/Planck/CMB 상수는 기존 owner를 유지한다.

추가4pi,dE,a^-3,dt 인자는 없고 source injection·redshift·stage weighting은 이 함수 밖의 소유다. 다음 장부를 같은 사건으로 연결한다.

    -sum dp/dt = sum R_a/nH
    -eV_erg*sum E_j*dp_j/dt
       = sum n_abs,a*(chi_a*eV_erg*Gamma_a+heat_a)/nH
    nH*dw/dt+binding_micro+escape+expansion_work
       -photo_input-CMB_to_gas = 0.

w는erg/H이며 heat_per_absorber는 event당 에너지가 아니다. 기존 igm_point_rhs가 photo binding/thermal,CI/RR/DR/CE/freefree,variable-particle EOS와signed CMB를 처리한다. 밖에서 photoheat를 다시 더하지 않는다.

## CR-off 관측의 정확한 범위

CrMode::Off만 실행하고 On은 MissingAuthority("CR_ON_SCOPE_NOT_ADMITTED")로 계산 전에 거절한다. Off의 CR source4성분은 fraction rates3[s^-1]와 thermal rate[erg/H/s]의 양의0 bits다. Baseline RHS에 +0 산술을 추가하지 않는다.

DeferredCrAccess의 load/source_callback를 관측할 수 있는 witness를 전달했다. Off에서 두 호출수 모두0이고, 별도 positive control에서 witness의 각 method를 직접 호출하면1이 된다. Witness는 실제 CR 원자 provider가 아니다. Caller의 경계 밖 eager initialization이나 기존 production history 전체의 무호출을 이 시험으로 주장하지 않는다.

CR_OFF_ACCEPTANCE.json은 새 native candidate 경계에만 SCOPED PASS다. 실제 기존 history/loader의 global counts와 owner import ACK는 null이며 CR-F0의 전체 적용 완료는 아니다. CR-on이나 zero-fill physics를 허용하지 않는다.

## 실제 native 및 이식 경로 검증

첨부 rust_1_94_1_env(4).sh의 /mnt/data/rust-1.94.1-prefix를 복구해 rustc1.94.1(e408947bf),cargo1.94.1을 실행했다. 새 배포 서명 인증은 수행하지 않았고 version/build success와 signature authenticity를 구분한다.

실행 workspace는 독립 source-selected compilation capsule이다. 직접 raw network DNS/cache 실패 후 connector와 immutable archive에서 source를 회수했다. 원 input ZIP은 FLRW_HHe_IGM_foundation_thermal_20261006.zip,450188bytes,SHA25653ce530df98ba1a8e5af83c85abcba5854f9ffc5827b1ef925b39eae9d4835a2다. 위5개 과학 module과 root lib는 현재 bytes, 다른 support modules는 provenance가 고정된 이전 capsule이다. coupled_primary.rs는 현재13–17행의 PrimaryPacket 타입 선언만 포함한다. 다른 coupled stage 함수를 대체 실행한 것이 아니다. 전체 current receiver checkout의 build가 아니다.

receiver_import.patch에는 새 module/test/example와 lib export만 있다. prepare_receiver_patch.py는5원 source hash를 확인하고 기존 목적파일/출력을 덮어쓰지 않는다. 별도 로컬 capsule 복사본에 dry-run/apply 후 내부 module 경로로23시험과6개point probe를 실행했다. 외부 crate 경로와 import 경로 CSV는 byte-identical이다. 원격 rei_bianchi에 패치를 적용하지 않았다.

서로 다른 focused tests23개 PASS,그중1개 assertion RED→GREEN/22tests-after. Same23을 두 연결경로에서 실행했으며46개의 독립시험이라고 합산하지 않는다.6개의 manufactured/source-shaped point는 HI13.7eV at1e4/5e4K,HeI-active30eV,HeII-active80eV,passive13.599eV,zero photons다. 관측자료나 actual F08 endpoints가 아니다.

원 명목 fractions=[.9,.3,.05],nH=1e-4cm^-3,nHe=.083*nH,H=1e-14/s,Tcmb30K. EOS로 회수한 실제온도를 기록했다. 저온HI에서Gamma_HI=9.327373886494715e-13/s,photon loss=9.327373886494712e-14/H/s,absorbed power=2.0473417681607323e-24erg/H/s다.6point의 최대 normalized energy residual=1.293106815379842e-16이며 정확0이 아니다.6point 모두deferred CR loader0/callback0/source4zero다.

Python 독립 scalar Verner 식/number/energy 비교30개의 최대 relative discrepancy=4.0595910393851045e-16. Same fit의 독립 계산경로이지 다른 원자자료나uniform error certificate가 아니다. Zero absorber/ne/He,단위변환,128개 angular-weighted packet분할,unchanged direct RHS,invalid/underflow/NaN/on-refusal를 검사했다.

새3Rust파일fmt 및 scoped clippy --no-deps exit0, Python2파일syntax PASS. 기존166시험/F04P32시험/원자가속suite는 재실행하지 않았다. 새 native point evaluation은 실제 수행했고 physicalIVP/history/nonlinear solve/precisionatomic simulation은0이다. 독립human/agent reviewer와formal verifier는 없다. 실행 명령/exit는 logs/COMMANDS.json,실행코드hash는VERIFICATION.json에 있다.

## 정본과 실제 백업

BASS_CR_FASTEST_BRIDGE_20261007_v1.zip
bytes=118512
SHA256=a63740c08c95b4c720690b2d75cc96ce0e13e81db54bbcf5160175a28c4f6f03
75members/74payload size/SHA256/CRC local검증,tested source hashes일치.

Drive upload success 및metadata:id1v4RHed_y80LDWxlyZiBCDXWHBuMUQZvX,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size118512일치.
Dropbox completed:id:BSpOijBcT10AAAAAADzsog,size118512,modified2026-10-07T10:54:55Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_FASTEST_BRIDGE_20261007_v1.zip.

동일immutablearchive의create-only이중백업이다. R1 UPLOAD_VERIFIED(ID/name/size/path/parent)이며remotechecksum미노출,새ZIPfullrestore/독립remotebytehash미수행이다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. 이summary의actualcommit/tree는detacheddeliveryreceipt에추가기록한다. ZIP은미래backup성공을미리기록하지않는다.

## 다음 실행 연결

준비된패치를실제owner작업트리에적용하고source-driven IGM integrator의허용된callsite에서이진입점을호출하는것이남았다. 재구현이나새원자이론루프가아니다. Integrator가dt/sourcebirth/redshift/acceptedstep이력과temperatureguard를소유하고,이module이instantaneous photoevent/heat와off dispatch를소유한다. 현재는point source bridge까지며timeevolution/관측calibration/intervalcertificate는없다.

CR_OFF_FASTEST,precisionatomicPARKED,G02UNRESOLVED,physicalproductionHOLD,capture=false,all_boundOPEN,b_gridNO_GO를유지한다. 기존theoryF04P는별도FT03인증으로보존하며IGM승격에사용하지않는다. 실제CRcounter(global)/ownerimport/rawnativehistoryheat=null,FullK/318patch/CR-on/소비원자승인재사용없음. Samebranch는bass_cr이며receiver원격변경은없다.
