# CR-F0-R4: 공통 시계의 방출 대조와 독립 연속시간 참조

2026-10-07. 상태: SAME_CLOCK_SOURCE_COMPARISON_AND_FINITE_SOURCE_TIME_REFERENCE_COMPLETE. 결과의 수준은 numerical/implementation verification이며 interval-IVP 또는 물리적 정확성 인증이 아니다.

## 범위와 source identity

기존 Grackle 기반 IGM point bridge, source-step, FLRW driver를 재구현하지 않았다. 원자율·물리 상수·분율/온도 admission·Newton 허용오차·adaptive acceptance를 변경하지 않았다. 새 opt-in example과 시계 helper를 통해 방출 목록 M=4,8,16 및 공통 시간격자 N=64,128을 교차하고, 각 유한 방출원에 대한 독립 연속시간 수치참조를 계산했다. 기존 FT03 F04P Q2/C3 인증을 이 IGM 모형으로 옮기지 않는다.

bass_cr intake 및 게시 직전 HEAD: 9bc156c4fe25fc3dd84473de8db418ed043f6d58, branch research/r4q-gap-closure-20261001.
Receiver intake 및 게시 직전 HEAD: 4dae4a26a5e15b2289b46668f546f0acd2a23417, branch forward/rust-reion-kernels-20260922. 원격 rei_bianchi, owner CURRENT/DAG/production defaults는 변경하지 않았다.

부모 BASS_CR_FASTEST_COSMO_20261007_v1.zip: 777922 bytes, SHA256 2624ce1d5a441eda411b819708c39cb67d1280775ee4a590924520bac00e5002. 실제 archive SHA/CRC를 확인했다. 재사용한 crate/src 30개 및 원 independent C 7개가 부모 manifest와 byte-identical하다. 27개 원 receiver와 bridge/source-step/driver를 포함하며 lib.rs도 바꾸지 않았다. 원 src tree는 cb69b4736dd046e4675557577eb8e0ead037d1f3이다. 현재 igm_background.rs blob cdce6a9f0a9e9df930f33c8521ee720fd463a780을 읽어 absolute ln(a) API를 확인했다. 전체 Git checkout/옛 tests/examples 전체를 다시 만든 것은 아니다.

새 파일은 crate/examples/support/source_clock.rs, crate/examples/cr_source_time.rs, crate/tests/source_clock.rs, research/reference.py, research/analyze.py, research/reproduce.py다. 실제 코드와 시험·원 입력·결과·실패로그는 아래 봉인 ZIP의 정본이며 이 Git 파일은 summary/provenance/backup pointer다.

## 공통 시계와 방출 계약

R3와 같은 제조된 flat FLRW 배경: H0=2.2e-18/s, Omega_r=9e-5, Omega_m=.3, Omega_b=.049, Omega_Lambda=1-.3-9e-5, YHe=.24, Tcmb0=2.7255K. 시작 ln(a)=-ln11, 끝은 시작+2e-5. 초기 가스분율(.9,.3,.05), Tgas=10000K, 초기13.7eV photons=.05/H. S=5e-15 photons/H/s다. 관측 best-fit이나 기존 F08 이력으로 재명명하지 않는다.

Master clock은 absolute ln(a), proper dt는 원 GL8의 integral dln(a)/H다. 64구간의 dyadic 시계를 먼저 고정하고 각 구간에 원 driver의 midpoint를 삽입해128구간을 만든다. 모든 M의 midpoint-ln(a) birth가 두 시계의 정확 경계에 들어간다. Source cell [l,r]의 count=S*proper_interval(l,r)다. 이는 ln(a) 중점과 proper 구간 질량을 조합한 유한 방출 규칙이며 정확 proper-time 중점이나 연속방출원이 아니다.

동일 N에서 모든 M의 실제 accepted-half 시작/중점/끝과 dt가 비트 단위로 일치한다. 동일 M의 ID/방출시각/E/count가 두 N에서 모두 같다. M별 총 방출량의 최대 floating 차이8.673617379884035e-19/H는 보존하며 이를 숨기기 위해 재정규화하지 않았다. 모든 selected photons는 끝까지 fit cutoff13.6eV 위에 있어 문턱 횡단이 없는 범위다.

원 evolve를 공통구간마다 호출하되 max_attempts1, min=max interval로 시계를 고정했다. 원 estimator의 거절 또는 추가 분할이 발생하면 해당 비교가 실패한다. 실제 여섯 profile은 모두 변경·거절 없이 완료됐다. Birth는 경계에서 한 번, 각 BE 내부 source는0이며 accepted 두 half의 장부만 누적한다. CR-on은 승인 부재로 거절한다. 이 opt-in 제약을 일반 production adaptive 정책으로 교체하지 않았다.

## 시간 오차와 방출 효과의 분리

유한 방출 measure를 mu_M, 그 연속시간 해의 끝온도를 T_*(mu_M), N시계 native 값을 T_N(mu_M)라 쓰고 e_N(M)=T_N(mu_M)-T_*(mu_M)라 두면

    T_N(mu_b)-T_N(mu_a)
      = T_*(mu_b)-T_*(mu_a) + e_N(b)-e_N(a).

같은 시계는 시간규칙만 고정하며 시간오차가 source에 의존하는 것까지 제거하지 않는다. 이번 T_*는 독립 수치해로 근사했으므로 아래 차이는 reference 기반 numerical estimate이며 엄밀한 오차 구간이 아니다. 정확한 continuous-emission 목표는 풀지 않았다.

독립 경로는 변경하지 않은 Grackle 원 C 함수14개와 Python의 별도 EOS/사건/냉각/CMB/팽창일/광흡수 조립이다. Photon energy는 E_birth exp(ln(a)_birth-ln(a)), proper 시간 우변에는 dY/du=(Delta ln(a)/H)*dY/dt를 한 번 적용한다. 각 저장 birth에서 적분을 끊고 실제 count를 해당 cohort에 한 번 더한다. 미래 cohort를 birth 전에 흡수하지 않으며 native endpoint를 참값으로 주입하지 않는다. 가스 H/He 반응은 모두 유지하고 selected photoabsorption만 HI다.

DOP853로 M4/M8/M16, Radau로 M16을 각각 새로 계산했다. rtol2e-12,atol2e-14. 네 trajectory 총48 IVP구간과 reported4094 RHS evaluations다. M16의 DOP853/Radau 온도차7.275957614183426e-12K는 일치 진단이지 적분오차의 엄밀한 상계가 아니다. 두 방법은 같은 독립 RHS를 공유하므로 공통 오류 가능성도 남는다.

## 실제 결과

표의 소수는 저장된 numerical output이며 증명용 interval 끝점이 아니다.

|방출 M|N64 온도[K]|N128 온도[K]|연속시간 유한-source DOP853 참조[K]|
|---:|---:|---:|---:|
|4|9815.841911998195|9815.595379024118|9815.347960987701|
|8|9815.861678076277|9815.615215766593|9815.367868663414|
|16|9815.866628515178|9815.620183954521|9815.372854668714|

M16에서 native-minus-reference는 N64 +0.49377384646322753K, N128 +0.24732928580669977K다. 시간세분화 차이는0.24644456065652776K, reference 기반 오차비는1.9964228855984993으로1차 경향과 일관적이다. 시간오차는 splitting/frozen-context/clock/numerical implementation도 포함하며 pure reaction truncation이라고 축약하지 않는다.

|방출 변경|동일N128 차이[K]|연속시간 유한-source 참조 차이[K]|differential time term[K]|
|---|---:|---:|---:|
|M4→M8|+0.019836742474581115|+0.019907675712602213|-0.00007093323802109808|
|M8→M16|+0.004968187928170664|+0.004986005300452234|-0.00001781737228156999|

유한-source 참조 차이의 successive ratio3.992710499284181은 이 매끄러운 window의 이차 source 추세와 일관적이다. 그러나 continuous-emission 참값·source 절대오차·Richardson-extrapolated 승인 상태는 생성하지 않았다. 마지막 두 M의 차이를 전체 source 오차 상계라고 부르지 않는다. N128/M16의 약0.24733K 시간차는 M8→16 참조차0.004986K보다 약49.6배 크므로, 이 진단에서 M만 늘려서는 지배적인 시간오차가 해결되지 않는다.

별도 frozen-hazard 양성/부정 대조에서 constant k>0,S,T와 M등분 proper-time midpoint 방출은

    P_cont=(S/k)*(1-exp(-kT)),
    P_M/P_cont=[kT/(2M)]/sinh[kT/(2M)]
              =1-(kT)^2/(24M^2)+O(M^-4).

총 방출량이 모두ST여도 생존 광자가 같지는 않다. 네 사례를 검사했지만 이 식을 nonlinear IGM의 source 오차 증명으로 사용하지 않았다.

## 실행·시험·실패

Final science:6 native profiles,576 accepted macro,1152 accepted half,1728 complete BE solves,0 rejected trial. 관측 경계의 deferred CR loader/callback은 여섯 모두0이다. 실제 광흡수/IGM atomic provider는 호출했으며 global/original-history CR counter와 owner production import ACK는null이다.

새 고유 Rust tests14 PASS: unaligned birth 거절1개 assertion RED→GREEN,13개 tests-after. 원 R3 26/R2 23/bridge23/166suite/F04P 증명은 반복하지 않았다. 새 Rust3파일 rustfmt check 및 Python3파일 syntax PASS. 독립 인간·에이전트 심사, proof-assistant, interval-IVP verifier는 미수행이다.

새 native accepted stage12개에서 원 C 계수 경로의 156개 output과 BE residual을 확인했다. 최대 normalized BE residual1.2975337729986044e-16, output relative difference1.3712730216401109e-14, background relative difference4.226680300242132e-16이다. 새로운 독립BE root는0이며 대신 위 네 연속 IVP를 실행했다. Native number ledger max1.27569936967203e-15/H, energy absolute max1.715930241036745e-26erg/H, normalized energy max1.7226575243489908e-13. Reference energy ledger max6.15e-15eV/H 미만. 보존식 검사는 연속시간 오차 인증이 아니다.

첫 새 example에 module 선언 뒤 내부 문서주석을 놓아 Rust E0753 compile 오류가 발생했다. 과학 실행 전에 주석위치/unused import만 수정했고 원 snippet/stderr를 보존했다. 형식 정리 뒤 새14시험과6native를 final로 다시 실행했다. Development/final의7개 데이터 파일은 byte-identical이므로 독립참조를 다시 적분하지 않았다. 최종 입력hash가 reference 입력hash와 동일함을 확인했다. 전체 preformat+final 성공native12profiles/1152macro/3456BE이며 final6개와 중복 집계하지 않는다. Unit의 추가 stage call은 이 수에 포함하지 않는다.

첨부 prefix에서 rustc/cargo1.94.1을 실행했으나 배포서명을 새로 인증하지 않았다. Runtime SciPy1.17.0,NumPy2.3.5,Python3.13.5. 문서의 최신버전과 실행버전은 구분한다. 새 관측 export는 properne1158행이지만 tau/visibility/BASS observer는 실행하지 않았고 observer tail은null이다.

## 정본·실제 이중백업

BASS_CR_FASTEST_SOURCE_TIME_20261007_v1.zip
bytes=1483065
SHA256=6829e5e2630162c1aaf999763d5c9a93543ce41167a48f12d570c093ecde8ab7
128entries/127payload의SHA256와CRC를로컬에서검증했다. 전체구성실행명령과 source hashes는 VERIFICATION.json, 결과는 results/reference01/RESULTS.json 및 results/native_final에 있다.

Drive upload success 및 metadata readback: id1sCtVbRcuhQx7DxYVIp30BLkLpZN4JOgF, parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ, name/size1483065 일치.
Dropbox completed: id:BSpOijBcT10AAAAAADzv2Q, size1483065, modified2026-10-07T12:55:28Z, path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_FASTEST_SOURCE_TIME_20261007_v1.zip.

동일 immutable ZIP을 create-only로 저장했다. R1 UPLOAD_VERIFIED이며 remote checksum은 응답에 노출되지 않았다. 새 ZIP의 remote fullrestore/독립 remote bytehash는 미수행이다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. 이 게시 문서의 실제 commit/tree는 ZIP 밖 detached DELIVERY_RECEIPT에 기록한다. 봉인 ZIP에는 미래 게시·업로드 성공을 미리 기록하지 않았다.

## 다음 경계

이 공통시계 source 비교와 유한-source 연속시간 수치참조는 제한된 범위에서 종료한다. 다음은 실제 owner opt-in adoption 또는 같은 M16의 time-error/목표 정확도 단위다. Source 절대정확성을 주장하려면 별도의 continuous-emission 목표해 또는 검증된 source-response bound가 필요하다. 같은6native/4reference와 옛 suite를 동기화 목적으로 다시 실행하지 않는다.

원격 receiver mutation/precision atomic simulation/CR-on/fullK/318patch/소비된원자승인재사용은없다. CR_OFF_FASTEST, precision atomic PARKED, physical production HOLD, G02 UNRESOLVED, capture=false, all_bound OPEN, b_grid NO_GO를 보존한다. 참고문헌은 SciPy 공식 solve_ivp 인터페이스이며 source-specific 분리식과 frozen-hazard 대조는 직접 유도했다.
