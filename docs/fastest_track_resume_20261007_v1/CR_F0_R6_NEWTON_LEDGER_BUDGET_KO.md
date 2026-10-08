# CR-F0-R6: Newton stopping과 누적 장부 잔차의 분리

2026-10-07. 상태: SCOPED_NEWTON_LEDGER_ATTRIBUTION_AND_TOLERANCE_PLATEAU_VERIFIED.

R5의 같은 M16/N128 implicit-midpoint 실험에서 requested Newton tolerance만 2e-13/2e-14/2e-15로 바꿨다. 2e-14에서 normalized energy residual은 +2.1545977697617825e-9에서 -2.2808264390060974e-14로 줄었다. 2e-14와 2e-15의 공통 수치필드 49024개는 bit-identical이다. 생산 기본값과 과학 소스는 변경하지 않았다. 이 값들은 유한 진단이며 연속 IVP/root/물리오차의 인증이 아니다.

## 입력과 재사용

- bass_cr intake 및 게시 직전 HEAD: 2338a2d1d494fb07c6de62da34fe11f5af26f8e6
- branch: research/r4q-gap-closure-20261001
- receiver intake 및 게시 직전 HEAD: e94e41b009723c9077015404503632325f58d16c
- receiver branch: forward/rust-reion-kernels-20260922
- receiver의 이전4dae4a26 이후 변경: BRIDGE05 BOXJOIN 문서9개, 과학 source 변경 없음. 별도 FT03 결과를 읽었지만 이번 Grackle IGM 수치 입력에 섞지 않았다.
- parent archive: BASS_CR_FASTEST_MIDPOINT_20261007_v1.zip,1629640bytes,SHA256 d328e69bef7581c9f12ca7147024d4f825c8fa248388f26874baba15ec1e1aeb

새 crate의 library source31개는 부모 bytes와 같다. 새 Newton/BE/bridge를 작성하지 않았으며, 새 연구 helper가 기존 공개 NewtonControl을 전달한다. Midpoint의 internal BE tolerance=requested/2, max_iterations40, full/half acceptance, source와 시계, 원자율 및 온도 guard는 그대로다. 요청 tolerance 이외의 과학 설정을 바꾸지 않았다.

같은 제조된 FLRW: H0=2.2e-18/s,Omega_r=9e-5,Omega_m=.3,Omega_b=.049,Omega_Lambda=1-.3-9e-5,YHe=.24,Tcmb0=2.7255K. ln(a) 시작=-ln11,끝=시작+2e-5. 초기 분율(.9,.3,.05),Tgas10000K,13.7eV .05photons/H와16개 유한 birth를 유지했다. 광자 수는 H핵당, 가스 w는erg/H, 시간은proper seconds다. 관측 best-fit이나 정확한 연속방출은 아니다. c,kB,eV/Planck/CMB 상수는 기존 owner를 유지한다.

## 정확한 저장값 장부 분해

한 source leg의 old/endpoint를 y0,y1, 저장된 midpoint rate-state에서 실제 native 함수를 재평가한 RHS를 fhat, 시간간격을 h라 두고

    r = y1-y0-h*fhat

를 구한다. CSV를 round-trip binary64로 읽은 뒤 Fraction.from_float로 정확한 유리수상을 사용했다. 십진문자열을 다른 exact 입력으로 재해석하지 않는다.

Stage의 실제 nHe/nH division을 eta로 고정하고, 상태 순서가 (xHII,xHeII,xHeIII,w,p_j)일 때 inventory row는

    cN=(1,eta,2eta,0,1,...)
    cE=(ev*chiHI,ev*eta*chiHeI,ev*eta*(chiHeI+chiHeII),1,ev*E_j)

다. Signed point ledger rate는 sN=(-CI+RR+DR)/nH, sE=(escape+gaswork-CMB)/nH다. 원 native volumetric rates와 저장 integrated ledger b를 사용하면

    J = c*(y1-y0)+b = P+D+Q
    P = c*r
    D = h*(c*fhat+s)
    Q = b-h*s

가 정확히 성립한다. P는 actual discrete state residual의 projection이며 Newton stopping뿐 아니라 endpoint reflection/elimination/RHS 산술의 영향도 포함한다. D는 rounded RHS와 별도로 조립한 point ledger의 차이, Q는 dt*rate/nH와 half-ledger doubling의 차이다. P를 순수 exact-root iteration error bound로, D를 실수 물리 보존법칙의 실패로 부르지 않는다.

768개 accepted source leg의 수/에너지1536항등식을 확인했다. Global reader의 초기 eta0와 stage eta 차이, 실제 pre/post survivor를 사용하는 photon geometry, source 장부합과 global accumulator 차이, birth 에너지 곱, 상태 연결, 최종 scalar readout도 따로 보존했다. 세 profile 모두 state stitch 항은 정확0이다. 그 밖의 작은 항을0으로 만들지 않았다. 전체 합이 실제 native reported 수/에너지 잔차에 정확히 일치한다(6개 global identities).

기본 설정의 에너지[erg/H]:

|항|표시값|
|---|---:|
|상태잔차 projection P|+2.1461899379872005e-22|
|그중 HII 결합에너지|+2.1174498051105388e-22|
|그중 thermal w|+2.8514011319071402e-24|
|RHS balance D|+7.282290986066832e-30|
|Stage ledger rounding Q|+2.920699943591397e-33|
|최종 scalar readout|-6.364983672516807e-28|
|실제 reported global residual|+2.1461836877686784e-22|

HII binding은 projection의 약98.66088%다. 이는 저장값의 기여분해이지 물리적 가열오차의 비율이 아니다. 표에 생략한 He-frame/geometry/accumulation/birth와 정확 끝점은 results/final/EXACT_GLOBAL.json에 있다. 소수 몇 개를 더해 exact identity를 재현할 수 있다고 주장하지 않는다.

## 실제 tolerance 결과와 중단 결정

|requested tolerance|Newton1회/2회 accepted half|끝T[K]|수 잔차[/H]|에너지 잔차[erg/H]|정규화 에너지 잔차|
|---|---:|---:|---:|---:|---:|
|2e-13|107/149|9815.372566619202|+9.719018653580721e-12|+2.1461836877686784e-22|+2.1545977697617825e-9|
|2e-14|0/256|9815.372566656370|-9.259967351950418e-16|-2.271919407036514e-27|-2.2808264390060974e-14|
|2e-15|0/256|동일 bits|동일|동일|동일|

2e-14/2e-15는49024numeric fields가 같고, 기본설정은 이전R5 IM128의37238numeric fields와 같다. 같은 세 설정의 clock/context7680fields, birth192fields도 같다. 이전 R5의 나머지3개 profile은 실행하지 않았다.

Signed energy residual은94465.66배 작아졌지만, 상쇄를 쓰지 않는 관측 절댓값 예산은2.1496132364105185e-22에서5.267951229268573e-25erg/H로 약408배 줄었다. Tight 예산은 signed residual 절댓값보다 약231.87배 크다. Signed 합이 작다는 이유로 개별 stage 잔차까지 그 크기라고 주장하지 않는다.

T 변화는+3.7167410482652485e-8K다. 계승한 R4 same-finite-source numerical reference9815.372854668714K와 남는 차이는-2.8801234475395177e-4K로, 이번 tolerance 변화보다 약7749배 크다. Reference를 재적분하지 않았고 그 차이를 엄밀한 시간오차 반경으로 쓰지 않았다.

2e-14는 이 M16/N128에서1회 Newton 종료를 제거한 충분한 진단 설정이며,2e-15는 추가 이득이 없어 더 엄격한 값 탐색을 종료한다. Accepted-half 내부 RHS 평가수는5074->6144로21.0879% 늘었다. Full trial 및 별도 telemetry를 제외한 값이며 walltime/HPC 비교가 아니다. Production default2e-13, midpoint opt-in 및 양성 거절 조건은 그대로다. 다른 밀도/T/시간/source/stiffness로 이 선택안을 자동 이전하지 않는다.

## 예산의 의미

관측 예산은 각 leg의 sum_i|c_i*r_i|+|D|+|Q|와 모든 외부 보정항의 절댓값을 합한다. 실제 reported ledger를 덮지만 root/IVP state error를 덮는 것은 아니다. +3과-3의 signed cancellation을0 budget으로 처리하면 실패하는 시험을 먼저 기록했다.

조건부로 exact component |r_i|<=scale_i*tau_i가 성립하면 |c*r|<=sum|c_i|scale_i*tau_i다. Native rounded scalar stopping criterion 자체가 이 exact 전제를 증명하지는 않는다. Photon 판정에는 max(tau,64*machine_epsilon) floor도 있다. Gas tolerance만 계속 줄여도 RHS/ledger/geometry/누적/최종readout 항 모두가0이 되는 것은 아니다. 새 read-only budget helper는 제공된 기여와 명시된 budget만 검사하며 driver acceptance나 새 물리 threshold를 변경하지 않는다.

## 실행·검증·실패

Release build1회와 native1process에서3profile을각1회 실행했다. Final384acceptedmacro/768half/1152internal BE solve, rejected0이다. 추가 raw telemetry는 저장 rate-state에서 point RHS768회 재평가한 것이며 Newton 내부 interception이 아니다. CR witness load/callback은 science와 telemetry 경계에서0이고, actual production global counters와 owner ACK는null이다. 광흡수/IGM 원자 provider는 실제 호출했다.

새 Python21tests PASS:1assertion RED->GREEN,1serialization-exception regression,19tests-after. Exact Fraction128합성사례도 확인했다. Artifact assertions3129는 field/identity/연결 검사이며 독립 물리사례 수가 아니다. Python6파일 syntax와 새 Rust research2파일 rustfmt --check PASS. 기존 library31개 및 tested source8개 hashes는 봉인 시점에 일치한다. Clippy는 이번에 실행하지 않았다.

원 Grackle C 함수14개와 독립 point assembly로12stage(기본6,tight6)의RHS48성분/사건156성분을 비교했다. 최대relative 차이는RHS4.13484247437e-16,event3.75084157241e-16이다. Tight두결과가bit-identical이므로 같은 C검사를 반복하지 않았다. 새 independent root/IVP, old suite/history, precision atomic 계산, receiver mutation은0이다. 독립 인간·에이전트 심사나 proof-assistant/interval-IVP 검증은 없다.

큰 유리수의 선택적 float 표시가 overflow한 오류는 정확num/den을 유지하면서 display=null 및 OUTSIDE_BINARY64_RANGE로 처리하도록 고쳤다. 입력/과학식/허용오차를 바꾸지 않았고 수정 전 serializer와 실패로그를 남겼다. 실제 과학3JSON은 수정 전후byte-identical이다. 초기 interactive container 실행환경 오류도 실행전 실패로 따로 보존했다.

첨부 환경 prefix의 Rust1.94.1로 실제 build/run했다. 선택 component를 복원하면서 제공 tarstream 끝까지 읽었다. 제공 archive SHA256294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40과 실행 버전은 고정했지만 배포자 signature authenticity는 NOT_VERIFIED다.

## 정본·실제 이중백업

File=BASS_CR_FASTEST_NEWTON_20261007_v1.zip
bytes=2439037
SHA256=5ea7e2727d078f98ada161d895e65db9595869a92d054caf72247e2a1f1a6f96
129entries/128payload size,SHA256,CRC 확인. 봉인 후 reproduce.py --verify-only 실제 실행 성공.

Drive upload success 및metadata readback: id1U3hO8She7XQu4sqUdm_ZX_5Pp4Kp7mW7,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size2439037일치.
Dropbox completed: id:BSpOijBcT10AAAAAADzxAw,size2439037,modified2026-10-07T14:47:34Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_FASTEST_NEWTON_20261007_v1.zip.

동일immutableZIP의create-only R1 UPLOAD_VERIFIED다. Remote checksum은 반환되지 않았고 새ZIP의remote fullrestore/독립remote bytehash는 하지 않았다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. Git은 이 요약과RETURN의정본pointer이며 실제 source/tests/nativeCSV/exactJSON/로그는ZIP이다. Actualpublicationcommit/tree와provider metadata는ZIP밖detached DELIVERY_RECEIPT에기록한다.

## 종료 및 다음 연결

같은M16/N128의Newton-stopping/장부 기여 진단은 종료한다. 기존 public NewtonControl에2e-14를 명시하는 opt-in 채택은 이 입력에 대한 제한적 선택안이다. 다음은 실제 owner caller의 채택 또는 명시 global ledger 예산을 요구하는 변경scope의 검증이다. 새로운 source/longhistory에 기본보장으로 옮기거나 같은세tolerance를 동기화마다 반복하지 않는다. Continuous-source, threshold-crossing, 강한 stiffness, 정확IVP오차는 별도 열린 문제다.

CR_OFF_FASTEST,precisionatomicPARKED,physicalproductionHOLD,G02UNRESOLVED,capture=false,all_boundOPEN,b_gridNO_GO를 유지한다. FT03이론을GrackleIGM에승격하지않으며 original/globalCRcounter,ownerimportACK,observerTail은null이다. 원격rei_bianchi,productiondefault,globalpolicy는 변경하지 않았다.
