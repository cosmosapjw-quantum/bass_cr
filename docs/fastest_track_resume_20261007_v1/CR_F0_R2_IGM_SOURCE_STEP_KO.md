# CR-F0-R2: source-fed IGM 시간단계와 current-source import

2026-10-07. 상태: CURRENT_SOURCE_TREE_IMPORT_AND_SOURCE_STEP_NATIVE_VERIFIED__COSMOLOGICAL_DRIVER_PENDING.

기존 CR-off photon-to-IGM point bridge를 재구현하지 않고 source-fed backward Euler 단계, 4가스변수 damped Newton, full/two-half trial과 accepted-only 사건 누적을 구현했다. 현재 receiver의 원 src 27개를 실제 Git tree에 결합한 로컬 library에서 새 module을 컴파일·실행했다. 원격 rei_bianchi 또는 기존 cosmological driver는 변경하지 않았다. F04P/FT03 인증을 Grackle-based IGM 모형에 이전하지 않는다.

## 코드와 입력 identity

bass_cr intake=c277bb4305ccddf5b5d94f83f59f398e7f6c3b62, branch=research/r4q-gap-closure-20261001.

이 문서의 직전 게시 commit=fabb4bee9401d85d6289590b4d7b4d17f7110754. 해당 commit은 research/fastest_rejoin_20261007/source_step/RUN_FROM_ARCHIVE.py를 추가했다. Launcher는 아래 ZIP SHA를 고정한다. Git에는 launcher와 이 summary를 게시하며, 새 Rust source 전체·tests·현재 원 source tree·패치·실행증거의 정본은 ZIP이다. 새 Rust 전체가 Git 경로에 직접 게시됐다고 주장하지 않는다. 이전 bridge core의 기존 Git 파일은 보존한다.

Receiver intake와 최종 재확인 HEAD=84afbe7660ec79e5e43822e7aea49a0a9ee8daea, repo=cosmosapjw-quantum/rei_bianchi, branch=forward/rust-reion-kernels-20260922. 최신 변경은 별도 FT03 cohort 수송 연구이며 그 계산 결과를 이번 IGM의 기준해로 쓰거나 재실행하지 않았다.

현재 원 rust/rei_microphysics/src tree=cb69b4736dd046e4675557577eb8e0ead037d1f3. 27개 원 blob을 각각 검증하고 Git tree 직렬화를 재구성해 일치시켰다. Cargo.toml blob=0771ae64cf1e4c8f51a9fb7f23f216c4056e423b, Cargo.lock blob=ae3e5afb2c63c5323abfaefe8a6fcce46d1c8014. 이전 capsule의 coupled_primary 타입 발췌본을 현재 전체 source로 교체했다. 전체 Git checkout 및 과거 tests/examples를 복구한 것은 아니고 current complete library source와 선택된 tests/examples의 build다. paired_runtime 파일은 보존하지만 해당 history는 실행하지 않았다.

기존 bridge는 namespace를 내부 crate로 연결하는 이식 외의 산술/CR 로직 변경이 없다. 현재 27개 원 scientific source body를 유지하고 lib.rs에는 새 module 두 개의 export만 추가했다. 소스별 회수 archive/member/hash는 inputs/SOURCE_RECOVERY.json, 원 tree는 inputs/UPSTREAM_IDENTITY.json에 있다.

새 핵심 파일:
- crate/src/igm_source_step.rs: SHA256 2adfaa4033b8cc80aabc1ed0aecc1c4028e3b3f49a6b1092bcfe3c9e879b72a6
- crate/tests/igm_source_step.rs: SHA256 9ef327f6219bd837d62fccb2306b55608b61d9975afc39e61dd373f8b76401ec
- crate/examples/igm_source_history.rs: SHA256 60ec322b6c50dcc9bc111793edf0b81184d497843bdcdad19d25f6bcc1664407

직접 Git 네트워크는 DNS 실패했으나 authoritative connector tree와 봉인 archive로 원 bytes를 회수했다. 첨부 환경의 /mnt/data/rust-1.94.1-prefix를 복구해 rustc1.94.1(e408947bf), cargo1.94.1(29ea6fb6a)을 실제 실행했다. 배포자 서명 authenticity를 이번에 새로 검증하지 않았다.

## source-step의 정의와 유도

한 stage에서 proper nH/nHe[cm^-3], photon energy E_j[eV], H[s^-1], Tcmb[K], source S_j[photons/H/s]는 고정한다. 가스 정지계, bin/angular integration이 완료된 p_j[photons/H]를 사용한다. 시간·방출 birth·redshift·새 packet 추가는 외부 driver가 소유한다. c,kB,eV 변환과 atomic threshold는 기존 owner를 유지한다.

흡수율과 photon BE 소거는

    L_j(x)=c*sum_a n_a(x)*sigma_aj [s^-1]
    p_j,new=(p_j,old+dt*S_j)/(1+dt*L_j(x)).

Primary-only이며 해당 bin으로의 재방출은 없다는 조건이다. source/dt/nH/4pi/dE/a^-3를 중복 적용하지 않는다. 기존 bridge에 소거된 광자를 넣어 원 igm_point_rhs를 실제 호출한다. 네 미지수는 (xHII,xHeII,xHeIII,w/w_old), w[erg/H]이고

    R_x=x-x_old-dt*f_x(x,w,p_new)
    R_w=w/w_old-1-dt*f_w(x,w,p_new)/w_old.

Finite-difference 4x4 Jacobian, partial-pivot solve와 damped line search를 구현했다. 기본 max_iterations40, normalized residual tolerance2e-13이다. 도메인 경계에서는 가능한 한쪽 차분을 쓰고 필요시 perturbation을 줄인다. Simplex/온도 clipping은 없고 회수 EOS/provider guard, 비정상 산술 또는 미수렴은 상태 반환 없이 실패한다. Piecewise rate의 전역 smoothness나 Newton 전역수렴, root 존재·유일성의 구간 인증은 주장하지 않는다.

## accepted-only 상태와 사건 계약

trial_source_step은 full dt, half1, half2를 계산한다. Half2는 실제 half1 state에서 시작하며 source는 각 half에 dt/2만큼 한 번씩 들어간다. SourceTrial::accept는 유한하고 비음수인 error_norm<=1만 승인한다. Default error-control 값은 rtol1e-4, fraction atol1e-10, photon atol1e-12/H, thermal atol1e-22erg/H다. 이것은 새 opt-in estimator이며 과거 canonical strict local/public-width gate를 대체하지 않는다.

실패·거절은 immutable old state와 누적 장부를 변경하지 않는다. Accepted ledger는 half1+half2만 포함하고 discarded full의 사건을 버린다. 각 half의 endpoint와 사건을 보존한다. 두 half를 사용한다고 전체 적분법을2차라 부르지 않는다.

각 stage에서 dt*endpoint rates로 photo/CI/RR/DR count[perH]와 escape, signed CMB-to-gas, gas work, injected energy[erg/H]를 누적한다. Material binding+thermal 및 photon energy 장부는

    Delta(w+binding_perH+photon_energy_perH)
      +escape+gas_work-CMB_to_gas-injected_energy=0.

수 장부는

    Delta(electrons_perH+photons_perH)-injected_count-CI+RR+DR=0.

저장 f64 잔차를0으로 보정하지 않는다. 노드 energy가 바뀐 상태 사이의 source-only ledger 계산은 거절한다. 외부 redshift 일을 광흡수에 섞지 않는다.

CR::Off에서 기존 photon_igm_with_deferred_cr 진입점을 반복 호출하며 On은 초기 계산 전에 MissingAuthority로 거절한다. Deferred witness의 loader/callback은 모든 science profile에서0이다. Witness는 실제 CR 원자 provider가 아니므로 global/기존 history counter와 owner production import는null이다. 광흡수 AtomicProvider와 IGM 원자율은 실제 호출했다.

## 실제 시간진화와 수치 결과

제조된 고정밀도 상자: nH1e-4cm^-3,nHe=.083nH,H=0,Tcmb30K,initial fractions(.9,.3,.05),T1e4K. 초기13.7eV photon .05/H와 constant source5e-15/H/s, 시간0..1e10s. 팽창 우주가 아니라 source-fed fixed-box 진단이며 stage API의H>0/work/CMB는 별도 unit에서 확인했다.

|macro 수|끝 xHII|끝 온도[K]|최대 trial error_norm|누적 정규화 energy residual|
|---:|---:|---:|---:|---:|
|8|0.9009192119174194|9995.780524513317|0.01954332220545|1.95720388296e-10|
|16|0.9009195912972634|9995.778792293710|0.00490029538402|2.46973691678e-11|
|32|0.9009197811675513|9995.777925360644|0.00122688908808|3.04752776013e-12|

온도 successive difference ratio=1.9981007487108313. 제한된1차 수렴진단이며 연속해 오차 상계가 아니다. 세 profile56macro,168BE solve,112accepted half가 final science dataset이다. Unit의 추가 stage calls를 이 수에 합산하거나168을 세션 전체 호출수로 주장하지 않는다. Bridge RHS 평가횟수는 profile별368/576/1152이며 FD/line search를 포함한다.

3profile CR loader/callback 모두0. Number ledger 최대3.570691e-13/H, energy absolute 최대7.900932e-24erg/H이고 정규화 residual 최대1.957204e-10이다. 정규화 분모가 작은 총 변화량에 관련되므로 point-test 잔차와 크기가 다르며 이를 숨기지 않는다. 보존식 검사는 시간정확도 인증이 아니다.

## 독립 원 C 경로와 시험

원 Grackle C 함수14개와 headers/license를 그대로 보존한 callable wrapper를 gcc로 빌드했다. Python은 C 계수로 EOS, species/events, CI/RR/DR/CE/freefree, signed CMB, photon elimination 및 BE residual을 독립 조립했다. SciPy hybr로 선택된9개 root를 old-state 초기추정에서 풀었다. Native endpoint를 그대로 참값으로 돌려준 검사가 아니다.

9root의 normalized state difference 최대2.298161660974074e-14, C계수 경로에서 평가한 native BE residual 최대2.3016283974205964e-14다. Event/escape/CMB/work117비교 최대 상대차4.017056642876656e-16. Same-BE-map 구현검사이지 연속 IVP 또는 물리적 원자율 정확성의 증명이 아니다. 실제 SciPy1.17.0,NumPy2.3.5를 사용했다.

새 고유 Rust tests23 PASS: source-fed advance, immutable failure, zero/absent species/photon, passive gap, competing He, bad input/underflow/domain, Newton failure, photon/energy residual, source once, half2 chain, accepted-only events, accuracy refusal, work/CMB, changed-energy refusal, NaN acceptance refusal. 2assertion RED→GREEN,21tests-after다. 의도적 RED 로그와 수정 전 source를 보존했다.

기존 bridge23시험은 current full source tree의 새 import 환경에서 한 번 수행했고 PASS다. 46개 신규시험으로 집계하지 않는다. Old166suite와 F04P시험/증명, 원 F08/S0 campaign은 반복하지 않았다. Scoped rustfmt3파일 PASS,clippy exit0. 새 source-step의 needless_range_loop 스타일 경고2개와 원 source 경고가 남는다. Warning-free나 전체 repository lint clean이라고 주장하지 않으며 blanket suppression이 없다. Python3파일 및 detached launcher syntax PASS.

receiver_source_step.patch를 별도 local current-source 복사본에 dry-run/apply하고6개 module/test/example bytes가 시험 파일과 일치함을 확인했다. Lib export2개를 확인했으며 whitespace까지 동일하다고 주장하지 않는다. prepare_receiver_patch.py는 현재26non-lib 원 source identity를 검사하고 existing/conflicting output을 덮어쓰지 않는다.

최종 test/compatibility/fmt/clippy/patch 명령은 모두exit0이다. VERIFICATION.json과 logs/COMMANDS.json,FINAL_ARTIFACT_CHECK.json,PATCH_CHECK.json이 실행과 hash를 고정한다. 원 science dataset은1회 실행했고 launcher의 --verify-only는 실제 실행했다. Launcher로 같은 전체 science를 또 재실행하지 않았다. Source-step의 native 계산 및9개 독립BE roots는 실제 수행했지만 새로운 연속 IVP, cosmological history, 정밀 원자 적분, receiver 원격 mutation은0이다. 독립 human/agent review,proof assistant,interval root/IVP certificate는 없다.

## 봉인 archive와 실제 이중백업

BASS_CR_FASTEST_STEP_20261007_v1.zip
bytes=196491
SHA256=f3156ba8e07d4cfe263cb793c424a66958fa9730cbe9c1779c96007e10a11434
81entries/80payload size,SHA256,CRC와시험source hashes를확인했다.

Drive upload success와metadata readback: id1gHvXdZGWL9LO3QCBHcg0cHZRpyHhRpvt,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size196491일치.
Dropbox completed: id:BSpOijBcT10AAAAAADztpg,size196491,modified2026-10-07T11:29:10Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_FASTEST_STEP_20261007_v1.zip.

동일immutableZIP의create-only저장이다. R1 UPLOAD_VERIFIED이며remotechecksum은반환되지않았다. 새ZIP remote fullrestore/independentbytehash는실행하지않았다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. 이번source복원/로컬hash검증과outgoing R1을구분한다. 실제최종publicationcommit/tree는detached DELIVERY_RECEIPT에기록한다.

## 다음 fastest-track 연결

순간 point bridge에서 실제 source-fed implicit stage까지 진전했다. 다음은 실제 receiver 작업트리의 채택과 cosmological clock에서 nH/nHe/H/Tcmb,sourcebirth,redshift,acceptedstage별 사건과 work를 연결하는 일이다. 이미 구현된step을다시작성하지않는다. 이fixed-context3profile을 FLRW history로재명명하지않고, Grackle IGM에FT03 인증을자동이전하지않는다.

CR_OFF_FASTEST,precisionatomicPARKED,G02UNRESOLVED,physicalproductionHOLD,capture=false,all_boundOPEN,b_gridNO_GO유지. Global CRcounter/ownerproductionimport ACK=null. CR-on/fullK/318patch/소비된원자실행승인재사용없음. 같은bass_cr연구branch의additive게시이며 원격rei_bianchi mutation은없다.
