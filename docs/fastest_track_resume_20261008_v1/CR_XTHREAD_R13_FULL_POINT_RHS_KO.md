# CR-XTHREAD-R13: 비광이온화 항을 포함한 전체 point RHS

2026-10-08 KST. FULL_POINT_SOURCE_DIFFERENCE_CHECKED__CONTINUOUS_FLOW_AND_ERROR_OPEN.

## 이번 결과

R12에 남았던 비광이온화 source를 원 HE E5 IGM/RCT point 함수로 실제 평가했다. 같은 Q4에서 H2→H4의 24개 온도 RHS 차이는 모두 양수이며, 비광이온화 항은 기존 광이온화 차이를 0.5850362169%~2.0857667085% 늘렸다. 부호를 뒤집는 경우는 없었다. 모든 24개 쌍에서 가장 큰 개별 비광이온화 차이는 CMB였다. 이는 전체 절대 냉각에서 CMB가 항상 최대라는 뜻은 아니다.

이미 완료된 R12의 spectral sum/decomposition은 cached exact 결과로 사용했다. 새 계산은 full point96회와 unique zero-photo48회, 정확 성분 조립, 별도 고정밀 검산이다. 원 상태를 다시 진화시킨 결과, original accepted rate stage, 연속 tau 또는 실제 미래 온도 차이의 부호는 아니다.

## 고정 입력과 수신 범위

bass_cr intake=890916f8c9e75d82eb0f9523608cb2bf4500feb3, branch=research/r4q-gap-closure-20261001. 게시 직전 ref도 동일했다. 원 AGENTS의 selective R1와 기존 claim ceiling을 유지했다.

수신한 최신 상태:
- HE 0cda8e61601fb6be08617b9550f34f85bb75d2b2: E6의 전체 선언 endpoint finite rate9개 PASS, max three-axis0.9645971372385901. Feedback/노드 사이 오차/physical은 OPEN, 다음 E7. 원 E6 campaign은 실행하지 않았다.
- REI 0ae2ed67a37e4c0093b5b3560c9634dbb23a401f: BRIDGE11 한정 8/16/32 차수 비교 완료, 다음 실제 첫cell continuous defect. 이산 비교를 연속 오차로 가져오지 않았다.
- HH Git649ecb06321d3f7956fc13902666f062dfcde50c. 별도 Library 미조회이므로 전체 진척 없음으로 해석하지 않는다.

직접 계산 입력:
- R12 ZIP 10331973bytes, SHA25671a08718b421509d7b27d728bcdbebcbba0842f51cbbe89913d31535ca817f77, 선택7payload.
- HE E5 ZIP10400054bytes, SHA256d61cda1248a709ecfc3721fd7ef14ba89f6fd49320d346d800088081a1cb56b8, 선택45payload.

52개 선택 bytes를 부모 archive/manifest size/SHA에 결합했다. E5 library src36개와 Cargo파일, 원 cfg 등을 그대로 사용했다. 현재 전체 원격 checkout의 빌드나 최신E6의 재현이라고 주장하지 않는다. E5 science pin91218a1d496fad1b7231f96488a8df56e4fd532a와 최신수신을 분리했다. 모든 선택 identity는 ZIP/inputs/SELECTED_INPUTS.json에 있다.

원 igm_rct_point::point, IGM rate/EOS/background, RCT provider는 불변이다. 기존 KF/GM common-temperature zero-drift 및 mean35eV escaping closure를 그대로 사용했다. 새 원자율/closure/허용오차/상태 clipping은 없다. CR provider는 이 probe에 없으며 전역 무호출을 새로 관측한 것은 아니다.

## 단위와 전체 source 연결

Signature(-,+,+,+), proper seconds. G=(h,y,z,w), w[erg/H], nH/nHe[proper cm^-3], f=nHe/nH는 실제 제공값의 정확 비다.

    Xe=h+f*(y+2z), D=1+f+Xe, T=2w/(3kB D)
    Ce_alpha=hdot_alpha+f*(ydot_alpha+2zdot_alpha)
    Tdot_alpha=2/(3kB D)*(wdot_alpha-w*Ce_alpha/D).

동일 state의 derivative에 대한 선형 EOS 투영이므로 과정별 합산이 가능하다. Source state에 대한 선형근사라는 뜻은 아니다. Gamma3[/absorber/s]와 incident-energy3[eV/absorber/s]는 R12 정확값을 계승했다. 원 point 함수에 넣을 때 Gamma와 absorber당 excess heat를 각각 한번 f64로 반올림했다. 추가 dt/dE/4pi/a^-3는 없다. Source background의 nH/nHe/H가 입력과 bit동일함을 검사하고 같은 background의 Tcmb를 사용했다.

기록한 14개 비광이온화 과정은 CI3,RR3,CE3,DR,freefree,CMB,expansion,RCT다. Numerical CI floor, CE cap, 제외된 DR cooling은 별도 진단으로 보존했다. 현재 저온 branch의 DR rate는0이며 excluded diagnostic을 물리 sink에 다시 넣지 않았다. RCT 직접 Ce=0은 분율(rate/nH,rate/nHe,-rate/nHe)의 전하 항등식이며 열 source는 원 closure에 따라 비영일 수 있다.

원 전체 source를 F(G,m)=P(G,m)+N(G)라 쓰면 R12의 대칭 귀속은 다음으로 확장된다.

    Delta F = reader + spectral_history + photo_state + (N(G4)-N(G2)).

N은 같은 G에서 reader에 독립이므로 한번만 더한다. 이 네 항의 귀속은 정확한 유한차분 관례이지 유일한 인과 분해나 새로운 혼합 물리 이력은 아니다.

## 산술 객체를 구분했다

(1) Coherent record source Sc는 R12 exact photo와 native nonphoto primitive의 exact Fraction 재조립 합이다. (2) Native combined는 실제 source가 반올림된 photo input을 받아 계산한 f64값이다. (3) 고정밀 counterpart는 같은 binary64상수를 실수로 읽고 별도 함수로 계산한 수치참조다. Sc를 exact-real 원자율이나 정확한 시간해라고 부르지 않는다.

    Native-Sc = photo_input_conversion + native_assembly_difference.

두 항을 분리해 보존했으며 상태나 장부를 보정하지 않았다. Native fullTdot와 Sc의 점별 최대 절대차는4.596979157410003e-26K/s다. 작은 두-state 차이에서는 이런 점별 산술차이가 증폭될 수 있다.

## 실제 결과

같은 Q4 H2→H4, step384. 단위K/s, 표시 소수이며 정확값은 ZIP/results/final/FULL_SOURCE.json이다.

|mode|photo|nonphoto|coherent total|native subtraction|
|---|---:|---:|---:|---:|
|OFF|9.048766069481797e-22|5.4866685042500415e-24|9.103632754524298e-22|9.103768875999627e-22|
|KF|9.048172469113461e-22|5.575271186965358e-24|9.103925180983116e-22|9.103381135087492e-22|
|GM|9.047311147567372e-22|7.041202250328914e-24|9.117723170070660e-22|9.117986042777882e-22|

OFF384의 nonphoto 차이는 CMB+4.890482766944468e-24, HeIII RR+1.5091212315332945e-24, expansion-6.8650849579509465e-25, HII RR-5.784121857947088e-25, freefree+3.5529702407686164e-25K/s 등이 합쳐진 것이다. GM384의 RCT 차이는+1.5490839431433842e-24K/s다.

전체 H2Q2→H4Q4의 OFF384는 photo -4.381201186807785e-19에서 total -4.381146320122742e-19K/s가 된다. 전체 diagonal은 reader가 여전히 지배하고, 같은Q의 history차이와 부호가 다르다. 둘을 혼합하지 않는다.

## CMB의 정확 유한차분

원 CMB식에서 r=Xe/D, K_C=2*A_C/(3kB), A_C=4*sigmaT*a_rad*kB/(m_e*c)로 쓰면

    Tdot_CMB=K_C*Tcmb^4*r*(Tcmb-T)
    Delta Tdot_CMB=K_C*Tcmb^4*((Tcmb-Tbar)*Delta r-rbar*Delta T)
    Delta r=(1+f)*Delta Xe/(Da*Db).

원 CMB상수와 optical readout상수는 구분한다. 이 exact-real secant에는 source의 f64상수와 pi를 사용하되 native곱셈/거듭제곱 rounding을 같다고 놓지 않았다.

OFF384에서 DeltaXe=-5.445823799220481e-12, DeltaT=+6.064108910157305e-9K. Electron-share항+5.770965996898708e-24, temperature항-8.803039971645888e-25, 합+4.8906619997341186e-24K/s다. 전자비중 감소가 CMB 냉각을 약하게 하는 효과가 조금 높아진 온도가 냉각을 강화하는 효과보다 컸다. 이 formula값과 primitive-record값의 차이는 보존했다.

## 검증과 실행

새Python25tests PASS(1assertion RED/GREEN,24tests-after), 새Rust3tests PASS(모두tests-after). 과학 point144호출은96combined+48cachedzero-photo이며 native시험의2호출은별도다. 같은 96개 입력의 과학 process는1회다. Exact 성분/조립1,440조건,CMBsecant24,선택payload52조건을 확인했다. 새Python6파일 syntaxPASS,원native dependency36source 불변이다.

독립90자리저온실수함수경로에서4,032개성분의최대relative차1.47369e-14,576nativefull양의최대relative차6.32523e-16. 작은nonphoto차분의최대relative차는5.47480e-5이며24개전체차분부호는모두일치했다. 작업정밀도나점별일치를작은차분의물리적정확성으로승격하지 않는다. 최초검사와명시적certificate인수진입점확인검사2회보고서는byte동일이며고유사례는한번만센다. 독립인간/agent심사,proofassistant,intervalroot/IVP인증은없다.

제공prefix의rustc1.94.1(e408947bf),cargo1.94.1을실제복구·빌드·실행했다. 서명진본성은NOT_VERIFIED,invalid판정아님. Cargo로그에compilerwarning은없고rustfmt/Clippy는미실행이다. 의도적RED외새과학실패는없다. Shell TERM문구와과학subprocess exit0를분리했다. 새원자point함수는호출했으므로모든원자함수실행0이라쓰지않는다. 새IVP/root/history/characteristic/옛suite/타repo변경은0이다.

## 정본·게시·실제 이중백업

Core: research/fastest_rejoin_20261008/full_point_source/full_source.py
Code commit:e15da7ff404ff02b869ba95bcc423538a1e6702a
Code blob:888581eb8b1b068e516b93c6821ce59a0eedd62d
Code bytes:5690
Code SHA256:8779daad1eaac18814f3c6ddf4b0f0dbc5be05bf48d5edc5f759bab40840b541

Remote directory metadata의blob/size가시험한localbytes와같다. 전체원자source/nativeprobe/tests/exactrecords/REPORT는ZIP이며Gitcore하나가전체native실행package라고주장하지않는다.

Archive:BASS_CR_XTHREAD_R13_20261008_v1.zip
bytes:1823602
SHA256:3e50431ea832631dc50f2686d3ab88d82b24b4ae649825984b20e0389dbc85ec
105entries/104payload. LocalCRC/size/SHA와testedcode9개hash일치,launcher verify-only exit0. Compiler/nativebinary/target은제외하며실제binaryhash는VERIFICATION에보존했다.

GoogleDrive: uploadsuccess,metadata id1xpMfsi9zN0FPA44pZyxBq1Jm_qngLeLm,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size1823602일치.
Dropbox: completed,id:BSpOijBcT10AAAAAAD3cGg,size1823602,modified2026-10-08T10:00:11Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_XTHREAD_R13_20261008_v1.zip.

동일immutableZIP의create-only R1 UPLOAD_VERIFIED다. Providerchecksum미노출,새ZIPremote전체restore/독립remotebytehash는미수행이다. 실제finalcommit/tree는detachedreceipt에기록한다. ImmutableZIP은미래upload성공을선기록하지않았다.

## 종료·다음 입력

이point집합의전체RHS연결은종료한다. 다음에는동일target의검증된공동state/moment오차또는실제continuousreconstruction/one-sidedbranch자료를fullRHSdefect와연결해야한다. 이새point를과거integrator의ratestage로가장하지않으며R10jump에구적차이를입력하지않는다. 같은144point/시험을동기화목적으로반복하지않는다. HE E7/REI BRIDGE12/HH별도작업은원owner에남긴다.

CR_OFF_FASTEST,precisionatomicPARKED,HH ACTIVE,physical/productionHOLD,G02UNRESOLVED,all_boundOPEN,b_gridNO_GO,capturefalse유지. Owneradoption/globalCRcounter/observer-tail=null. 다른owner의source/CURRENT/defaults변경이나공동ONphysicalhistory는없다.
