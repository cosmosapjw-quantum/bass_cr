# CR-F0-R5: 같은 M16 방출원의 opt-in midpoint 시간정확도

2026-10-07. 상태: SCOPED_MIDPOINT_NATIVE_TIME_ACCURACY_CHECKED__DEFAULT_BE_UNCHANGED.

R4의 같은 Grackle IGM 모형과 16개 유한 방출원을 유지하고 implicit midpoint 후보를 구현했다. 기존 BE 반단계 solver를 재사용하므로 새 Newton/원자율 구현이 아니다. 실제 native IM32/64/128과 BE64 호환성 profile을 실행했다. 같은64구간의 최종온도와 계승 수치참조 사이 절댓값 차이는 약428.599배 작아졌다. 이것은 runtime speedup, interval error certificate, physical source uncertainty의 개선배수가 아니다. 원격 rei_bianchi 또는 production 기본값은 변경하지 않았다.

## 1. 입력과 source identity

bass_cr 시작 및 게시 직전 확인 HEAD는49baf27d0b2ad1e29f8523b97ee7537af92fdbb4, branch는research/r4q-gap-closure-20261001이다. Receiver는cosmosapjw-quantum/rei_bianchi@4dae4a26a5e15b2289b46668f546f0acd2a23417, branch forward/rust-reion-kernels-20260922이며 두 live ref가 R4와 같음을 확인했다.

R4 입력 ZIP: BASS_CR_FASTEST_SOURCE_TIME_20261007_v1.zip,1483065 bytes,SHA2566829e5e2630162c1aaf999763d5c9a93543ce41167a48f12d570c093ecde8ab7. 실제 SHA/CRC와 필요한 identity를 확인했다. 계승 upstream src tree는cb69b4736dd046e4675557577eb8e0ead037d1f3이다.

기존 library30개 중28개가 그대로다. 변경은 own igm_cosmological_driver.rs와 lib export이며, igm_source_step.rs, cr_off_igm_bridge.rs, igm_rates.rs, igm_thermal.rs 등 원 과학 함수와 단위/원자율/guard는 바꾸지 않았다. 새 src/igm_midpoint_step.rs의 SHA256은ee3b8b791068d4bfe26c2d352bc63baae3dfce9008950954569d35e40d50c35c, 새 driver SHA256은407e3d7a057e00096385e07e6e8509f17227746eb0c034de9710821ee745c01a다.

현재 library와 선택된 target의 로컬 빌드다. 전체 Git checkout 및 과거 tests/examples를 복원한 것이 아니다. 원 Cargo의 eval_fixture 선언에 필요한 옛 fixture는 패키지에 없으므로 기록된 명시적 target을 사용하며 cargo test --all-targets 성공을 주장하지 않는다.

## 2. BE 재사용과 사건 평가 위치

동일한 고정 source context에서 y=(fractions,w,photons), w[erg/H],p[photons/H]로 둔다. h는proper seconds다. 내부 source injection은0이고 방출은 외부 경계에서 처리한다.

    z = y_old + (h/2) f(z)
    y_new = 2 z - y_old

이면 y_new=y_old+h f((y_old+y_new)/2)의 implicit midpoint 식이다. z는 algebraic rate stage이며 실제 해의 중간시각 값이라는 인증은 아니다. 내부 BE 허용오차는 요청값/2, 최종 반사 상태 잔차의 허용오차는 기존2e-13을 유지했다. 이를 완화하거나 온도·simplex를 clipping하지 않았다.

고정 photon loss L_j=c sum_a n_a sigma_aj에서

    p_new = p_old*(1-h L_j/2)/(1+h L_j/2).

따라서 양성은 무조건적이지 않으며 hL_j>2에서 음수가 될 수 있다. 반사 endpoint의 photons/fractions/EOS/provider domain을 실제 검사하여 거절한다. 순수팽창 w'=-2Hw의 증폭률도(1-Hh)/(1+Hh)이므로 Hh>1은 거절 대상이다. 선형 stiff decay의 증폭률은무한감쇠에서-1로 가므로 A-stable과 L-stable을 혼동하지 않는다. 이 후보는 L-stable이 아니며 강한 stiffness 전역 자격을 부여하지 않았다.

사건·escape·CMB·gas work는 BEhalf ledger의 두 배, 즉h*f(z)다. Endpoint의 사건률로 대체하지 않는다. 새 CosmoLeg.source_rate_state와 source_scheme에 실제 평가 위치를 기록했다. SourceScheme::ImplicitMidpoint를 새 with_scheme entrypoint에서 명시해야 하며 기존 cosmological_leg/cosmological_trial/evolve는 BE를 유지한다. CosmoLeg struct에 필드가 추가되어 downstream의 수동 struct initializer는 reconcile이 필요하다.

기존 Ghalf/source/Ghalf, ln(a)중점 background, GL8 proper dt, 흡수후 광자를 사용한 radiation work, source-owned gas2Hw는 유지했다. Full/two-half heuristic 오차 지표도그대로며 /3으로 낙관적으로 줄이지 않았다. Accepted half만 누적한다. 매끄러운 구간의2차 일관성은 유도했지만 rate/cutoff/guard와adaptive분기를 넘는 전역2차 정리가 아니다.

## 3. 실제 수치 결과

R4 제조된 FLRW: H0=2.2e-18/s,Omega_r=9e-5,Omega_m=.3,Omega_b=.049,Omega_Lambda=1-.3-9e-5,YHe=.24,Tcmb0=2.7255K. 초기 ln(a)=-ln11, 총Delta ln(a)=2e-5, fractions(.9,.3,.05),T10000K,13.7eV 초기.05/H. 같은16finite birth의 count는5e-15/H/s와GL8 proper duration의 곱이다. 시간창 약4.53805465e11s이며 관측 best-fit 또는 정확 연속방출로 부르지 않는다. 모든 photon energy는이짧은 window에서13.6eV보다 크다.

계승한 R4 M16 DOP853 numerical reference는9815.372854668714K다. 원 Radau 대조를 재실행하거나 방법차를 엄밀한 오차반경으로 바꾸지 않았다.

|방법/시간구간|끝 온도[K]|수치참조와의 차이[K]|
|---|---:|---:|
|IM32|9815.368246166616|-0.004608502098563|
|IM64|9815.371702603987|-0.001152064727648|
|IM128|9815.372566619202|-0.000288049512164|
|BE64 기본 경로 호환성|9815.866628515178|+0.493773846463228|

IM 차이비는4.000211088807323과3.999537159398946이다. SameN64의 차이비428.5990488321985는 동일 유한-source numerical-reference 기준의 시간정확도 진단이다. Source 이산화·원자fit·연속스펙트럼/각도·observer tail의 오차 개선을 뜻하지 않는다.

R4와 source ID/ln(a)/E/count256필드 및 N64/128 actual clock2304필드가 bit-identical이다. 기존BE64 기본경로도 profile/stage/photon numeric15259필드에서bit-identical이다. Dispatch변경에 영향을 받을 수 있는 옛경로 한건의 회귀검사이며 이전6profile 전체를 반복한 것이 아니다.

## 4. 보존식 오차의 독립 경계

IM32/64의 정규화 에너지 잔차는약-5.05583e-14/-2.62929e-14다. IM128에서는+2.1545977697617825e-9로커지며, 절대에너지 잔차2.1461836877686784e-22erg/H, 수 잔차9.719018653580721e-12/H다. 부호와 크기를 그대로 보존했고 사후열보정은없다.

IM128 acceptedhalf256개 중107개는 내부Newton1회,149개는2회에서종료했다. 실제가스잔차최대1.9880710e-13은최종허용2e-13이내이고독립 C경로도확인했다. 비선형잔차는단계수와함께누적될수있다. 시간참조차가감소한사실과장부오차가감소한사실은별개다. 추가적인장부정확도채택에는독립 nonlinear residual budget이필요하다.

## 5. 검증과 실제 실행

새고유Rust23시험 PASS,1assertion RED→GREEN/22tests-after다. 순수팽창 첫시험에서 반사를하지않은 stub의0.990099가요구0.980198과달라실패한소스·로그를보존했다. 음수광자/열반사거절,CR-on early refusal,입력불변,중점사건,half합성,BE기본값,source0,공통시계및정의역을검사했다.

원Grackle C와독립Python조립으로 acceptedstage576개를검사했다. Gas잔차최대1.988070488399482e-13,photon잔차최대4.1610218157415483e-16,7488개event/escape/CMB/work의최대상대차2.843246256117716e-14다. 새독립root/IVP를풀지는않았다. Exact Fraction의4조건(5hazard scalar 포함)도통과했다.

Rust5파일fmt,Pythonsource3파일syntax PASS. ScopedClippy exit0이나library22+helper1경고를보존했다. Warning-free와전체repo lint PASS를주장하지않는다. VERIFICATION.json의8개시험sourcehash와최종archivebytes가일치한다. logs/FINAL_COMMANDS.json의9개최종명령은모두exit0이다.

Final science4profile/288acceptedmacro/576half/864내부BEsolve,거절0이다. 형식정리전development를포함하면8성공profile/1728내부BEsolve이며 unit호출은별도다. Pre/postformat7개native출력파일과portableanalyzer수정전후결과가byte-identical이다. 같은576stage를두번읽었다고1152개의독립사례로집계하지않는다.

Rust1.94.1은첨부prefix에서실행했고배포자서명진본성은이번미검증이다. 실제환경Python3.13.5/NumPy2.3.5/SciPy1.17.0/GCC14.2.0. 독립human/agentreview,proofassistant,interval-IVP인증은미수행이다. 기존F08/BASS/IGM-long,정밀원자,CR-on,receiverremote mutation은0이다. 새native후보의계산은실제수행했다.

## 6. 적용과 정본

receiver_midpoint_delta.patch를R4기반별도local복사본에dry-run/apply하여6개파일bytes가시험파일과일치함을확인했다. 원격R1-R4채택을대신하지않으며productionimportACK는null이다. 실행은ZIP을풀고 python research/reproduce.py --verify-only, 실제재현은 --rustc /path/to/rustc --output NEW_DIRECTORY다. Network/새provider는없으며모든실행구성단계는검증했다. 동일end-to-end를추가폴더에서또실행하지않았다.

정본: BASS_CR_FASTEST_MIDPOINT_20261007_v1.zip
bytes:1629640
SHA256:d328e69bef7581c9f12ca7147024d4f825c8fa248388f26874baba15ec1e1aeb
145members/144payload size/SHA256/CRC와testedcodehash확인,manifest verify-only exit0.

GoogleDrive:upload success 및metadata,id1HtGCMSW05cJ9LQ7SFUY1G6i_DaiQghYA,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size1629640일치.
Dropbox:completed,id:BSpOijBcT10AAAAAADzwvw,size1629640,modified2026-10-07T14:10:47Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_FASTEST_MIDPOINT_20261007_v1.zip.

같은immutableZIP을create-only이중백업했다. R1 UPLOAD_VERIFIED,remotechecksum미노출,새ZIPremote fullrestore/independentbytehash미수행이다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. Git에는이summary/RETURN과정본위치를게시하며fullcode/tests/results/logs는ZIP이다.

봉인후detached archive receipt를만드는스크립트에서변수p가PosixPath로덮여returncode속성접근에실패했다. ZIP생성·검증은이미끝났으며기존ZIP을변경/재포장하지않고receipt만복구했다. 복구전후SHA동일,science재실행0이다. 실패스크립트hash/원인/복구는ZIP밖PACKAGING_RECOVERY와DELIVERY_RECEIPT에남긴다.

## 다음 단위

R5의 opt-in2차시간진단과BE호환성은위범위에서종료했다. 다음은실제owner채택또는같은M16/N128의Newton stopping과누적장부예산을분리하는한정진단이다. L-stable대안/문턱횡단/연속방출오차는별도입력·검증이필요하다. 같은23시험/4profile/이전IVP를동기화목적으로반복하지않는다.

CR_OFF_FASTEST,precisionatomicPARKED,physicalproductionHOLD,G02UNRESOLVED,capture=false,all_boundOPEN,b_gridNO_GO유지. FT03F04P를다른IGM으로전이하지않고global/originalCRcounter,ownerimportACK,actualobserver tail은null이다.
