# CR-XTHREAD-R8: HE 세분화 이력의 전자·광학깊이와 출력격자 분해

2026-10-08 KST. STORED_HISTORY_OPTICAL_REFINEMENT_DECOMPOSED__CONTINUOUS_ERROR_OPEN.

## 선택과 source

R7에서 metadata로만 수신한 HE RCT03E의15개 저장 이력과 이전N48/P512/O4 세 이력을 실제 소비했다. 총18이력2754행이다. 새 native/IVP/root/원자 provider/과거science suite는0이다. R7의 HH 부호 증명, REI energy-family, HE escape 후속을 재실행하지 않았다. 다른repo mutation0.

Intake: bass_cr854e668426998711903662dbd455cca7cbb8403f, HEc883a024ae951ac795589599487e3aeba2f35620, HH649ecb06321d3f7956fc13902666f062dfcde50c, REIe94e41b009723c9077015404503632325f58d16c. 네 HEAD는 R7 종료 상태와 같았다. HE escape FAIL/RCT03E2, HH ON06, REI BRIDGE06, CR actual owner opt-in은 담당별로 유지한다.

R7 archive SHA256=1795b631eb4b57483e3de90826d807ad98005e3289321d0db21294a81f27c0d9,414431bytes. HE RCT03E archive SHA256=0ab0316cc69012dbc195f08ef8800836583b6513542ae0bd20d7b3a4956386b9,1907812bytes. 실제 SHA/CRC와 경로를 확인하고 필요한34파일만 원 bytes로 복사했다. R7 background 함수/projector/constants는 수정하지 않았고 main/옛분석/옛suite는 실행하지 않았다.

## 출력 정의

ne=nH*xHII+nHe*(xHeII+2*xHeIII), Xe=ne/nH. R7의 동일 f64 background로193개 고유 ln(a)시각을 평가했다. 그 출력의 정확 Fraction상으로 q=c*sigmaT*1e6*ne/H를 만들고, 선언된 출력격자에서 q를 선형보간해 적분한다. c=299792458m/s,sigmaT=6.6524587e-29m²,D=1이며 nH/ne는propercm^-3,H는s^-1이다. τ는무차원이다.

이는 proper-time-linear ne와 다른 within-cell 정의이고 참 연속해 τ가 아니다. R7 기준 N48 세 이력의 Xe/τ6개는exact parity다. 새 HE보고의exact3/38을R7의f64density ratio에소급대입하지 않았다. 별도diagnostic 차이만 보존했다. Observer tail/rawVernerGamma/continuous error bound는null이다.

## 새 항등식

C가F의실제저장노드부분집합이고T_G가G의선형적분이면

    T_F(qF)-T_C(qC)
       =T_C(qF|C-qC)+[T_F(qF)-T_C(qF|C)].

첫항은공통시각의stored-history 변화, 둘째는같은finehistory의readout-grid 변화다. Source시간세분화가방출근사에도영향을줄수있으므로첫항을purechemicaltruncation으로읽지않는다. Missingcommonnode를보간해실제matchedclock이라고주장하지않는다.

한cell[a,b]안에m을추가하면grid변화는(b-a)/2*[q(m)-linear_chord(m)]다. m이정확중점일필요가없다. 새helper는전체signed합과cell별절댓값예산을같이보존한다.

## 실제 결과

GM−OFF 자체출력격자 Δτ: N48=4.394738484080101e-13,N96=4.394125638154656e-13,N192=4.393965984436943e-13.
같은49개공통시각에제한한 Δτ: N48=4.394738484080101e-13,N96=4.394805219817001e-13,N192=4.394815717493032e-13.
자체격자에서는감소하지만공통격자에서는증가한다. 이것은다른선형재구성의값이고어느쪽이참해에더가까운지증명한것은아니다.

GM N96→192:
- total=-1.596537177129642e-17
- 공통97시각stored-history항=+1.030780333058417e-18
- finehistory97→193readout항=-1.699615210435484e-17.

Readout항이총변화의106.45635%이고다른항이일부상쇄한다. KF의같은세값은-9.38389105116136e-19,+6.16796041275355e-20,-1.0000687092436714e-18이다. 소수는display이며정본결과는exacthex정수분자/분모다.

같은N192에서GM의P256→512 변화는-2.32274333413e-22,O2→4는+1.66773164446e-21이다. P128/P256의전자readout일치를spectraluncertainty=0으로읽지않는다. 공급자의N/U정확성으로VernerGamma를승격하지않는다.

GM N192의종별τ기여는(+2.320330566390142e-10,+2.315235395374276e-10,-4.631171995779981e-10),합4.393965984436943e-13이다. cancellationcondition은2108.96898이며끝전자condition1403.40508보다크다. 이condition은물리오차나확률신뢰도를직접뜻하지않는다.

## 검증과실패

새unit17PASS,artifact조건21PASS,새Python6파일syntaxPASS. 두시험은assertionRED→GREEN이며15개는tests-after다. Exact합성128case/384identity,별도symbolic1개를검사했다. 독립100자리표현식으로background579성분,2754행,absoluteτ18개,pairedτ/끝전자24개를대조했다. 최대background상대차6.48391215303e-16,exactreadout상대차2.07078824155e-93이다. 유한점검산이며source/IVP의구간오차인증이아니다. Independenthuman/agent/proofassistant없음.

새analyzer에서n이density로덮여Nmetadata가잘못되고anchor검사가건너뛰어진오류를발견했다. 재현시험RED후ne_value로분리하고6anchor검사를강제했다. 초기analysis01과수정전코드를보존했다. 새independentchecker의args가symbolic변수로덮여recordingexception이난것도이름만수정해검사를재실행했다. 공급자의물리식/tolerance/입력은불변이다. 최종수치결과는검증된analysis02와byte-identical이다.

## 코드·아카이브·실제백업

새core=research/fastest_rejoin_20261008/optical_refinement/nested_readout.py
Codecommit=c8162b33a59fecf8835303c6ce15119ae43db107
CodeSHA256=42c7080a03d403a927b9963c20a7cd482b3ee010af43c324a18e5f34a717a06f.
Fullanalyzer/tests/selectedinputs/REPORT/정확JSON/logs는immutableZIP에있다. Core를제외한전파일이Git에게시됐다고주장하지않는다.

Archive=BASS_CR_XTHREAD_R8_20261008_v1.zip
bytes=1890190
SHA256=0894cfcf34a57f1ff2e63462404e7f044c84526a83a4a81aeef70df162811541
97entries/96payload의CRC/SHA/size와launcherverify-only를local검증했다.

Drive:uploadsuccess및metadata에서id1ziTN5aQDRaqG-EpnKtU_W2wkHCgmLgES,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size일치.
Dropbox:completed,id:BSpOijBcT10AAAAAADz6yg,size1890190,modified2026-10-07T23:47:43Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_XTHREAD_R8_20261008_v1.zip.

같은ZIP의create-onlyR1UPLOAD_VERIFIED다. Remotechecksum미노출,새ZIPremote전체복원/독립bytehash미수행. UPLOAD_VERIFIED!=RESTORE_VERIFIED. 실제최종commit/tree는detachedDELIVERY_RECEIPT에기록한다.

## 다음 경계

새output/trajectory 자료가반환될때먼저최종관측량의출력격자를고정하고dense결과의readoutdefect를별도로보고한다. 참연속τ에대한판정에는source/trajectory/interpolation오차상계가추가로필요하다. 같은18이력/17시험을동기화만으로반복하지않는다. HE의escapeFAIL은이optical결과로닫히지않는다.

CR_OFF_FASTEST,precisionatomicPARKED,physicalHOLD,G02UNRESOLVED,all_boundOPEN,b_gridNO_GO,capturefalse;HH자체ACTIVE,canonicalS0OFFcontrol. OwnerACK/globalCRcounter/tail은null. 다른repo/CURRENT/default/공동F09mutation없음. NISTDLMF3.5(i)와Pythonfractions문서는일반산술배경이며새분해와계산은직접수행했다.
