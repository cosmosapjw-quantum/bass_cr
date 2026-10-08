# CR-XTHREAD-R9: 새 N384와 별도 cubic optical readout

2026-10-08. ACTUAL_N384_CUBIC_READOUT_CHECKED__TRUE_CONTINUOUS_ERROR_OPEN.

R8의 선형출력을 유지하고 opt-in LN_A_CUBIC4_3CELL_ACTUAL_CLOCK_V1을 구현했다. 새 HE RCT03E2의5개 canonical N384 output/rate 자료와 R8의N48/96/192 P512 O4 9개 저장이력을 소비했다. 총14tracks/2942rows이며 새로운5tracks는1925rows다. 기존9개선형tau는exactanchor로동일함을확인했으며,지난18개선형readout의전수science를반복하지않았다.

## 최신 수신

bass_cr intake3c5148557d1c698ee6f1bf7c895e650a44b08cdf, branch research/r4q-gap-closure-20261001.
HE8b7e5129c67de9e41ae29c7464afff9c5be2b6cd는 N384 targeted escape temporal을세처방모두통과했다. Allowance ratio OFF0.4447812347/KF0.4442006117/GM0.4351969807. GM만N384전체18필드3축finitecomparison이통과했고 OFF/KF전체3축은미평가다. 기존N192escapeFAIL은과거로보존한다. 실제Gammaendpoint는추가됐지만시간/문턱포함spectral정확성은다음HE RCT03E3범위다. 이분석으로그승인을대체하지않았다.
HH649ecb06321d3f7956fc13902666f062dfcde50c와 REIe94e41b009723c9077015404503632325f58d16c는이전과동일했다. HH/REI증명·root를반복하거나IGM에전용하지않았다.

입력HEZIP4554655bytes SHA256c8820730aa8b1249be07abe55fe8117ea57d212557e18f8a58436956ff2f353f. R8ZIP1890190bytes SHA2560894cfcf34a57f1ff2e63462404e7f044c84526a83a4a81aeef70df162811541. 두archive CRC와선택36payload의원bytes를확인했다. 새canonical만읽었고interruptedprefix/SMOKE를완료이력으로쓰지않았다.

## 출력과 충분오차조건

proper ne=nH*h+nHe*(y+2z), ell=ln(a), q=c[m/s]*sigmaT[m²]*1e6*ne[cm^-3]/H[s^-1], tau=integral q d ell이다. R7상수 c299792458,sigmaT6.6524587e-29와D1을유지했다. 배경은원R7f64함수의새385epoch평가다. observer tail은null이다.

각연속3cell의4개실제binary64시각을Fraction으로읽고Lagrangecubic을정확적분한다. w_j=integral L_j d ell이며등간격에서는H*(1,3,3,1)/8이다. 실제clock을정확등간격으로바꾸지않았다. 음의quadratureweight는거절하고clip하지않는다. 모든976개absoluteqpanel은Bernstein계수도비음수여서재구성양성이별도로확인됐다. signedpair에는양성을강제하지않는다. 이함수는원producerdenseoutput이나참해가아니다.

참q가panel별C4이고 nodeerror e_j와 M4>=sup|q''''|가별도로주어지면

  |tau_true-C(qhat)| <= sum_panels sum_j |w_j|e_j + sum_panels K_panel*M4_panel
  K_panel=(1/24)*integral |prod_j(ell-ell_j)|dell.

K는nodalpolynomial의부호가고정된세subcell에서정확적분했다. 최적Peanoconstant라고부르지않는다. 실제M4,정칙partition,nodeerror는없어실제continuousenclosure는null이다. API는누락시MissingPremise를발생시키며finite-refinement차이나재구성cubic의4차미분0을참해오차로사용하지않는다. 현재source/cutoffanchor구간의C4를새로증명하지않았다.

## 실제 결과

GM-OFF의linear/cubic표시값:
- N96:4.394125638154656e-13 /4.393899082831514e-13
- N192:4.393965984436943e-13 /4.3939093324182763e-13
- N384:4.3939282866297126e-13 /4.393914120357170e-13.

같은nestedclock에서
 C_F(q_F)-C_C(q_C)=C_C(q_F|C-q_C)+[C_F(q_F)-C_C(q_F|C)]
를정확분해했다. GM192->384의linear전체변화-3.769780723003209e-18은history+4.794311027096657e-19와grid-4.249211825712875e-18의합이다. Cubic전체변화+4.787938893379904e-19는history+4.790234664112217e-19와grid-2.295770732312903e-22의합이다. 두분해잔차는정확0이다. Cubicgrid항의크기는linear보다18508.868배작지만참오차·실행속도·물리정확도향상배수는아니다. KF의같은비는1986.846이다.

GM최종cubic종별기여H+2.3203306692308455e-10,HeII+2.3152355609828894e-10,HeIII-4.6311723160933775e-10이며sumabs/abssum2108.994를유지한다. 서로상쇄하는원자기여를고차보간으로제거한것이아니다. 최신cubic시간차이비는약2.14로전체solver의4차수렴을주장하지않는다.

GM N384의P256->512/O2->4 절대cubic출력차는1.0684604329355689e-19/9.409362324407628e-19다. 대응OFFcontrols가없으므로GM-OFF차이의정확한spectralbudget으로승격하지않는다. 실제Gamma파일은densityreadout확인에만사용했고새rateaccuracycampaign은실행하지않았다.

N384에서sumK=3.338623221300326e-31,sum|w|=1.9999999999997797e-4이다. 부호를보존하려면예를들어uniformeta/M4에대해 sum|w|eta+sumK*M4<|DeltaC|가충분하다. 이조건의각단일항한계eta2.196957060178827e-9,M4 1.316085652410286e18은요구조건이지실제측정오차가아니다. 실제전제는null이다.

## 실행과검증

새19unitPASS,1assertionRED→GREEN/18tests-after. Unequalclockcubic이기존trapezoid구현에서실패한원로그를보존했다. 원자/미시물리library와기본driver는수정하지않았다. 새6Python파일syntax와76artifact조건PASS.

독립mpmath90경로는Vandermonde계수와GL2적분으로14절대/8pairedcubic값을확인했다. Exact128합성사례의512moment및128quarticremainder도통과했다. 실제background1155성분의고정밀대조최대상대차7.9447e-16, native밀도3850대조최대2.6156e-16이다. 작업90자리정밀도는물리정확성자릿수가아니다. 해당독립검사의portablecertificate인수변경후재실행했고보고서byte-identical이며사례수를중복집계하지않았다.

메인새science는1회이며결과를final로byte동일봉인했다. 새native/IVP/root/원자provider/oldscience/다른repo변경0. Independenthuman/agentreview와proofassistant는없다. 잘못된Drivequery문법HTTP400은knownfolder목록으로복구했고과학실패와구분했다. 부속skill문서not-found도실행전제로만들지않았다. 제공Rust스크립트/도구체인은실행하지않았다.

## 실제 코드·백업

Core commit b116e23e1872ffce960d3f0c2614d6a3fbef1a49
Path research/fastest_rejoin_20261008/optical_cubic/cubic_readout.py
Blob c492a25cc896f49712b402ff9bf49f86c404f99f
SHA256 bb9507d5c55cc5fa5dbf69d66dbbcfa96596b56a169c8d9113ad84b9dbbf9b3d
Size6392. Remote directory metadata와testedbytes가일치한다.

Archive BASS_CR_XTHREAD_R9_20261008_v1.zip
2456901bytes,88entries/87payload
SHA256 7d45de8687487431edba6664fe51243e30bf50ea7658b16eb844eaa6df975207
localCRC/payloadSHA/testedsourcehash와verify-onlyexit0확인.

Drive id1A5Mv_ZT1SqXDSORes8ISMmfuIsySTxFS,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,uploadsuccess+name/size2456901metadata확인.
Dropbox completed id:BSpOijBcT10AAAAAAD3QHg,size2456901,modified2026-10-08T00:20:49Z,path /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_XTHREAD_R9_20261008_v1.zip.

같은immutableZIP의create-onlyR1UPLOAD_VERIFIED다. Remotechecksum미노출,새ZIPfullrestore/독립remotebytehash미수행. Incominginputarchive의실제bytes검증과outgoingbackup의R1을구분한다. Fullcode/tests/원입력/정확JSON/보고서는ZIP이고Git은core+요약+반환이다. 최종commit/tree는detachedDELIVERY_RECEIPT에기록한다.

## 다음 조건

기존R8선형계산을유지하고새cubic은opt-in이다. 같은14이력에대한다항식선택을반복최적화하지않는다. 연속tau정확성이필요하면동일source/clock에서검증된nodeerror및정칙구간C4상계또는동등한dense-output/defect증거를연결한다. 없으면새N768/campaign/허용오차를임의추가하지않는다. HE RCT03E3/HHON06/REIenergyfamily/CRowneroptin담당은보존한다.

CR_OFF_FASTEST,precisionatomicPARKED,HH연구ACTIVE,physical/productionHOLD,G02UNRESOLVED,all_boundOPEN,b_gridNO_GO,capturefalse. GlobalCRcounter/ownerACK/observer tail=null이다. Lagrange나머지/보간구적일반근거는NISTDLMF3.3.E5,3.5.iv이며실제source-specific수치는이번직접계산이다. 문헌최초결과나newphysicalcertificate로표현하지않는다.
