# CR-XTHREAD-R7: 타 스레드 결과의 총전자·유한 광학깊이 전달

2026-10-08 KST. Status=SCOPED_ELECTRON_TRANSFER_AND_CONDITIONAL_HH_TAU_SIGN.

BASS_HE, WU088_HH, rei_bianchi의 최신 결과와 bass_cr R6를 read-only로 연결했다. 다른 source를 하나의 optional-ON 모형으로 합치지 않았다. 새 결과는 HH의 총전자·finite-slab Thomson 부호 정리, HE의 direct-RCT charge null과 간접 전자 반응의 분리, REI fixed-energy root의 Xe 투영 및 CR stopping 설정의 추가 readout이다. 새 native/IVP/root/atomic-provider/old-suite 실행과 다른 repo mutation은 모두0이다.

## 최신 수신과 실제 계산 입력의 구분

- bass_cr intake: b196768e2a2d99581c1ae1b14cc59b2f4380a056, research/r4q-gap-closure-20261001. R6의 세 tolerance 진단과 같은 M16/N128는 종료된 상태로 유지했다.
- HE intake: 985969ad244e521cc95244c49b992e0a8cdc4b48, RCT03D. 실제12개 저장 history444행을 소비했다. 게시 직전 c883a024ae951ac795589599487e3aeba2f35620의 RCT03E1을 추가 수신했다. 2commit/새7문서이며 기존 입력은 불변이다. 주요6필드 finite refinement 기준은 통과하지만 escape allowance ratio OFF1.77860067,KF1.77628483,GM1.74015781의 FAIL을 보존한다. 다음은 RCT03E2 escape 시간 예산과 실제 rate 관측량 계약이다. 새15history/2592step은 공급자 보고로 수신했으며 여기서 재실행하거나 기존 RCT03D 읽기의 증거로 바꾸지 않았다.
- HH live HEAD:649ecb06321d3f7956fc13902666f062dfcde50c. Science pin47accb0b3ac9adca40913dc06c797a509c1a7b49의 TH05. HII 순서와 photon absorption optical memory가 닫혔고 실제ON06는 owner의 별도 작업이다. HH 연구ACTIVE, canonical S0 OFF control을 유지한다.
- REI live HEAD:e94e41b009723c9077015404503632325f58d16c의 BRIDGE05 BOXJOIN. 9source의 gas/count root는 fixed energy/sigma/density/dt에 한정된다. 다음 BRIDGE06 parametric energy/sigma/heat lift를 복제하지 않았다. 실제 IGM owner branch forward/rem-hhe-igm-20261006의 HEAD39c39eab1cc2f1a215723680accc123e67ef13b6도 구분했다.

HE/CR의 Grackle IGM, HH exact-decimal FT03+LCS, REI FT03/S0는 모형·초기조건·시간창이 다르다. 결과를 합산하거나 서로 직접 비교해 총 물리 신호를 만들지 않는다. 원 epoch/closure/tolerance/승인범위는 그대로다. 특히 HE의35eV closure를 CR/HH에 새로 이식하지 않았다.

## 공통 정의

    Xe = ne/nH = h + f*(y+2*z), f=nHe/nH.
    Delta Xe = Delta h + f*(Delta y+2*Delta z)

후자는 같은 background/clock/source family에서만 적용한다. 서로 다른 시계/모형/방출 identity는 새 pair contract에서 거절한다. 누락된 helium bounds나 observer tail, energy parameter를0으로 채우지 않는다.

Thomson readout의 source는 SYNC03 loop1/CONTRACT.json blob88eefba542e0c7fe6f0684cf274e938cb50281ab, BASS pin1e45e0f48cd83dcb21c23d4087fa5526195331d7이다. c=299792458m/s,sigmaT=6.6524587e-29m²,cm^-3→m^-3=1e6의 exact binary64 값을 유지한다. D=1, finite proper-time slab이며 actual observer tail=null이다. BASS source module/native를 새로 실행하지 않았다.

## 새 HH 조건부 정리

기존 TH05는 각 같은 eps∈[-.01,.01], 0<lambda<=1 대OFF, 0<t<=L=8e11s에서 Delta h>=lambda*g(t), g=(m/d)*(1-exp(-d*t))를 준다. TH04의 동시에 유효한 |Delta y|<=lambda*By, |Delta z|<=lambda*Bz와 f=.083을 사용한다. nH=n0 exp(-3Ht), n0=1e-4cm^-3,H=1e-14/s는 그 exact-decimal 모델이다.

    beta=f*(By+2Bz)=2.1879074055355079...e-11
    Delta Xe/lambda >= g(t)-beta
    Delta Xe/lambda <= Bh+beta.

endpoint의 바깥쪽 안전한 표시값은

    6.1786e-9*lambda < Delta Xe(L) < 2.8733e-7*lambda
    6.0320e-13*lambda < Delta ne(L)[cm^-3] < 2.8733e-11*lambda.

1-exp(-x)>=x/(1+x)를 사용한 충분조건 beta/(m-d*beta)는 약1.8598986448080535e9s다. 따라서 1.86e9<=t<=8e11s에서 총전자 반응이 양수다. 최초 crossing의 위치를 구한 것은 아니며 더 이른 구간의 부호는 이 충분조건만으로 주장하지 않는다.

전체 적분의 부호는 후기 양성만으로 가정하지 않았다. g>=0이므로

    integral nH*Delta Xe dt/lambda >= nHmin*I_g - n0*beta*L
    I_g=integral g dt=(m*L-g(L))/d.

TH05의 이미 감싼 g(L)의 upper를 빼 I_g의 lower를 정확유리수로 얻었다. 그 하단은 약2849.9693528378157s다. 결과는

    5.514159811432804380867215794...e-15
       <= Delta tau/lambda
       <=4.584290742352500747420367191...e-13.

안전한 표시로 5.5141e-15*lambda<Delta tau<4.5843e-13*lambda다. 이는 HH의 photon absorption optical memory와 다른, 총전자에 의한 finite-slab cold-Thomson 적분이다. 기존 TH04/TH05의 source/first-exit/차이 증명이 유효하다는 조건부 결과이며 이전proof를 재실행하지 않았다. 임의 positive-lambda pair, 온도 순서, Bianchi−FLRW 차이, nativeON06 또는 물리적 원자율/Thomson 정확성을 승인하지 않는다.

## HE 저장값의 새 전자·optical readout

원 igm_rct_point의 반응 HeIII+HI→HeII+HII+photon에서 사건J/H의 분율 변화는 (J,J/f,-J/f)다. 따라서 직접전자 변화는 J+J-2J=0이다. 동시에 Delta kappa=c*nH*J*(sigmaHeII-sigmaHI)일 수 있으므로, 직접전자0이 이후 모든 thermal/photo/재결합 경로의 Delta ne0을 의미하지 않는다.

RCT03D N48/Gauss4 GM−OFF의 종별 electron/H 기여는 (+1.5860471639136953e-5,+1.5807798402721119e-5,-3.1623172507670055e-5), 합은+4.5097534188017146e-8이다. J=1.5879576947850556e-5/H를 사건당전자1개로 잘못 더하면 추가편향이 실제저장DeltaXe의 약352.1163배다. 기존owner에 그버그가있다고판정한것이아니라 부정대조다.

새HE readout은 same stored ln(a) endpoints 사이에서 c*sigmaT*ne/H를 선형보간한 함수의 정확 적분이다. nH/nHe/H는 보존된source식의 새Pythonf64평가이며 native/interval background를 새로 실행한 것이 아니다. 초기native3값은같았고 1332개 고정밀식 대조의 최대상대차5.94053e-16이다.

GM N48/G4의 Delta tau_ln_a≈4.3947384840801014e-13, Delta ne_end≈1.8693918882370553e-11cm^-3다. N24→48의 이delta tau변화는 약-2.2342226206e-16, 상대-0.05083858%다. 이는 stored-history numerical surrogate이며 실제연속tau의오차상계가아니다. RCT03E1의 새로운정확fHe=3/38 분석을이전D의f64densityratio에소급대입하지않았다. E1 numerical values는추가수신기록에별도로남겼다.

## REI/CR의 다른 근거수준

REI의 fixed-literal root box를 Xe로투영하면 최종1.25e9s에서 [1.024624289152583867690272274...,1.024624289152766152322105615...]다. 모든9stagepoint가해당범위안에있다. Source-mid density를state-endpoint density로재명명하지않았으며 continuous history범위가없어tau는null이다. 새로운energy family를주면거절한다.

CR R6의771개proper-ne endpoint는같은properseconds의linear-ne 함수로읽었다. T14−T13의 Delta tau≈-5.8067066035470202e-18, Delta ne_end≈-2.3380023941914761e-15cm^-3다. T14/T15 전자series는같다. 이차이는Newton선택의수치반응이지CR물리source 또는globalerror bound가아니다. 기존tolerance sweep을반복하지않았다.

## 검증과 실행

새22unit tests PASS,1assertion RED→GREEN/21tests-after. Exactbox128사례/1024corner, symbolic4조건, HH endpoint/2scalar적분/후기양성충분조건, HE1332background/초기native3/444전자/12적분/8차분, CR771행/3적분, REI72corner의별도검사도PASS다. 새Python5파일syntax PASS. 기본계산은Fraction이며 별도mpmath100자리/SymPy1.14.0은같은작성자의독립계산경로다. 독립human/agent심사나proofassistant가아니다.

새native/IVP/root/atomicprovider/과거suite/BASS실행은0이다. 새Pythonbackground및readout·bound함수적분은실제로수행했다. 제공Rust스크립트는읽었지만실행하지않았다. 과거다른thread의broken compilerarchive를이번실행실패로가져오지않는다. Unknown owner/globalCR/tail은null이다.

수치결과는 results/analysis01에서 results/final로바이트동일복사했다. 마지막HE문서수신에따른v2는metadata/plan만추가하며시험한5source와모든수치결과hash는동일하다. 최초localv1은외부게시하지않고보존했다. Fullnewscience pipeline을추가폴더에서다시실행하지않았고 개별구성명령과launcher verify-only는실행했다.

## 코드·정본·백업

Core는 research/fastest_rejoin_20261008/cross_thread_transfer/electron_transfer.py에실제게시했다. Code commit3e3e04b5dd4bc1e832c1089b3a48775b1a001394, blob5f2c4230692644cde768ffc62b74a2c151ef80be,size7611,SHA256b81f408a82f4e93728e8435802a2484f9d94669128830ce13695952e5d8bd2c6. Remote directory metadata의blob/size가시험bytes와같다. Fullanalyzer/tests/inputs/REPORT/정확결과/owner별handoff는ZIP이다.

Archive=BASS_CR_XTHREAD_R7_20261008_v2.zip
bytes=414431
SHA256=1795b631eb4b57483e3de90826d807ad98005e3289321d0db21294a81f27c0d9
109entries/108payload의CRC/SHA256/size와launcher verify-only exit0을확인했다.

Drive uploadsuccess/metadata: id1W1q2W7KJk6drRFmfYgPeb8Ff9i34Vspj,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size414431일치.
Dropbox completed: id:BSpOijBcT10AAAAAADzymQ,size414431,modified2026-10-07T15:45:44Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_XTHREAD_R7_20261008_v2.zip.

동일immutableZIP의create-only R1 UPLOAD_VERIFIED다. Remotechecksum은응답에없고새ZIP fullrestore/독립remotebytehash는미실행이다. Incomingarchive content검증과outgoingupload를구분한다. 실제최종commit/tree는detached DELIVERY_RECEIPT에기록한다.

## 갱신한 다음 단위

HE RCT03E2 escape시간예산/실제rate출력, HH ON06 coherent실행, REI BRIDGE06 energy-family, CR 실제owneropt-in은각owner의담당으로남긴다. R7은공통consumer이며다른owner의source/CURRENT/DAG를덮어쓰지않는다. 같은입력/모형/clock/closure/error budget이고정되기전에는새jointF09를실행하지않는다. 실제전자/광학깊이전달이구현됐다고physicalintegration완료라고표현하지않는다.

CR_OFF_FASTEST,precisionatomicPARKED,G02UNRESOLVED,physicalproductionHOLD,capturefalse,all_boundOPEN,b_gridNO_GO유지. HH자체는ACTIVE이며legacy24/289,265unbounded,epsilonC/Rnull,B22OPEN과과거rawarchive백업공백도보존한다. OwnerexecutionACK/globalCRcounter/tail은null이다. 동일22시험이나이미끝난nativecampaign을동기화만을위해반복하지않는다.
