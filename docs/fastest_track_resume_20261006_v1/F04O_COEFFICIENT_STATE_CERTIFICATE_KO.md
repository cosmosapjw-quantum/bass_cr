# F04O: 상태계수 오차를 포함한 Q2의 조건부 음의 구간

## 판정

Task=BASS-CR-CHAT-F04O_COEFFICIENT_STATE_DEFECT.
Status=SCOPED_Q2_NEGATIVE_WITH_STATE_AND_GOAL_ERROR__FINITE_EPSILON_OPEN.

F04M의 같은 raw-ray real-analytic fixed-grid 가족과 F04N의 동일한21표본 Hermite 곡선을 유지했다. 이번에는 가스·광자·보조 모드의57개 상태계수 방정식 전체에서 시간구간 잔차와 Jacobian을 감쌌고,20개 시간cell에서 해가 선언된 오차tube를 벗어나지 않음을 확인했다. F04N의 가열 방정식 잔차와 결합하면 첫macro[0,1.25e9]proper seconds의 Q2에 대해

    -1.500838e-14 < Q2 < -1.498346e-14 eV/H < 0

를 얻는다. 이는 명시한 산술·source·선행 증거 신뢰 기반의 deterministic conditional enclosure다. Q2=Q''(0)/2이며 finite-epsilon contrast의 부호 또는 전체 BI history를 인증한 결과가 아니다. 기존 두solver 일치를 오차상계로 바꾸지 않았다.

## 최신 상태·입력 identity

bass_cr 시작과 게시 직전 HEAD=665d75a72bf5b0615427899150611c5360b44acf, parent tree=67e7036ab88b4eaff1acf27b013e330eaa8cf1b5, branch=research/r4q-gap-closure-20261001. 같은 branch에 새 summary만 추가한다. Receiver 시작 및 최종 확인 HEAD=5673fc60e7e4db2a1c411aefae7dba4cda80d279, branch=forward/rust-reion-kernels-20260922. 새 SPEC03 thermal spectral-feedback 결과를 수신했으나 다른 error target이므로 이번 응답계의 source나 bound로 가져오지 않았다. Producer/runtime_returns/CODEX_SYNC는 변경하지 않았다.

입력 BASS_CR_CHAT_F04N_20261006_v1.zip의 실제 SHA256=7f1c4fa11d1790248baeb0358264770ebabc0e7a3ec5d69b60f896f544cc2d6a. 필요한 원 bytes를 선택 보존했고 inputs/SELECTED_MANIFEST.json의 경로/size/SHA를 실제 계산 전에 검사한다. Inherited goal proof의 curve_sha256와 RECONSTRUCTION.json이 일치한다. 과거 science suite와 native/IVP를 재실행하지 않았다.

Source family는 F04M의 paired_runtime.rs blob70eed18b07b6dd4297d8ef8da6d7e1be8e44456e, ft03_rates.rs blobb8a85ff37de160ecc576a168e4259ed23920a499, raw T0 header에 결합된다. Stored primitive binary64를 정확 실수로 읽고 대수·초월함수를 실수 함수로 평가한다. Native rounded program의 미분이 아니다. F04M float evaluator의 intermediate rate-constant products와 이 real algebra가 다르면 그 차이를 frozen-slope reconstruction residual에 남긴다. F04N과 같은 analytic Verner sigma를 사용한다.

초기 alpha=1/128, emission beta=norm(q)^(-3)/sum norm(q)^(-3)를 유지한다. 정확 유리수 moment intervals와 tiny alpha-beta 차이를 바깥 반올림으로 받아들이며0으로 대체하지 않는다. 이 interval은 원 fixed realization의 계산 enclosure이지 새로운 physical parameter uncertainty가 아니다.

## 정의와 계수 공간

Signature(-,+,+,+), H_i=H(1+epsilon*a_i), a=(1,-1,0), H=1e-14/s, nH0=1e-4cm^-3, fHe=.083, source5e-15photons/H/s, 원 초기분율(.9,.3,.6), w0=13.620772387478219eV/H, .05photons/H at13.7eV와 active16..24를 유지한다. c=29979245800cm/s, kB와 eV-to-erg도 유지한다. Passive below-fit photons의 무피드백 가정은 그대로다.

Y=Y0+epsilon*Y1+epsilon²*Y2이며 Y2=Y''/2. X=[Y0(13),U(9),Y1(13),T1(9),Y2(13)]. Y의 열변수는w/w0, 광자는p/.05. T1은 온도나시각이 아니라 sum_d s_d*p_d1의 에너지별 모드다. 인증좌표 y=S^-1 X에서 Y0/U scale1, Y1 scale1e-16, T1 scale.01, Y2 scale1e-4를 썼다. 각 scale은 고정 binary64의 exact-real 값이다. 이것은 numerical comparison scaling이지 physical angular reweighting이 아니다.

Sample과 old scale의 곱은 Fraction으로 계산한 뒤 새 scale로 나누었다. Frozen Hermite slopes도 같은 방식으로 변환했다. Source initial state와 모든 initial response/goal이 정확히 맞음을 검사했다. 전역 s=t/T와 cell local u∈[0,1]에서 RHS timefactor Delta s를 한 번만 적용했다.

## 전 시간구간 state residual

각 cell의 잔차는

    r_i(u)=yhat_i'(u)-Delta s*F_i(s_a+Delta s*u,yhat(u);theta).

Parameter second-order Jet, time fourth-order Taylor algebra, sparse state AD를 중첩했다. RR kinetic/CI/RR/2DR, EOS/electron feedback와 response order간 결합을 모두 포함한다. Time Taylor coefficient도 derivative/k!다.

u=0에서 r의0..3차 계수를 평가하고 cell 전체에서 r''''/4!의 interval C4를 구하면

    r_i(u) in c0+c1*u+c2*u²+c3*u³+C4*u⁴.

이를 Bernstein 기저로 바꿔 R_i>=sup|r_i|를 얻는다. 전 cell을 감싼 결과이며 점표본이나 유한차분을 uniform bound로 대신하지 않는다. 새 proof에57개 residual intervals와 upper를 cell마다 보존했다. N의 goal residual은 기존 proof를 읽어 계승했으며 재계산하지 않았다.

## Tube 자기일관성과 오차 전파

각 cell에서 Hermite curve의 Bernstein range에 인증좌표 반경 rho=1e-4를 더한 box B를 잡았다. 이 영역은 새로운 물리 domain이 아니라 계수 IVP를 검증하기 위한 수치적 enclosure다. First/second coefficient는 음수일 수 있고, baseline photon의 작은 음수를 포함하는 analytic extension도 native state로 주입하지 않는다. Gas/EOS/real-power domain은 직접 확인한다.

시간·B·원 moment interval 위에서

    M_ii >= sup Delta s*dF_i/dy_i,
    M_ij >= sup |Delta s*dF_i/dy_j| (i!=j)

를 계산했다. Signed diagonal을 보존한 Metzler M이며, level0=(Y0,U), level1=(Y1,T1), level2=Y2의 triangular 구조를 검사했다. Baseline/first error가 higher response를 구동하는 아래 block은 제거하지 않았다.

Dini 비교로 exact solution이 tube 안에 있는 동안

    |e(u)|<=b(u), b'=M*b+R, b(0)=b_in.

M의 음의 대각을0으로 올린 Mplus는 entrywise nonnegative이고 해당 bplus(u)는 증가한다. 실제 모든 cell에서 bplus(1)<rho를 확인했다. 첫 exit가 있으면 경계에서 |e|가rho에 도달해야 하지만 이 엄격부등식과 모순이다. 국소 존재와 compact smooth-domain continuation을 연결해 구간 전체의 존재와 오차 enclosure를 얻는다. 이 검사를20cell에 순차 적용하며 이전 b_in을 재사용한다. Discrete root width로 continuous error를 reset하지 않는다.

최대 whole-cell error=1.0188811169206771e-8(표시값), rho=1e-4. 모든20cell 통과. Baseline temperature tube의 바깥쪽 표시범위는[49987.48,50007.97]K이며 기존 FT03 guard[30000,110000]K 안이다. Sharp endpoint bound를 모든 중간시각의 동일 bound로 바꾸지 않았다.

## 가열 계수 오차와 실제 결과

같은 box 위 L_ki>=sup|Delta s*dq_k/dy_i| 및 inherited RQ_k로

    a_k'=sum_i L_ki*b_i+RQ_k

를 전파했다. State57+goal3+constant1의61차원 augmented matrix [[M,0,R],[L,0,RQ],[0,0,0]]에 대한 exp action이다. Shifted nonnegative Taylor72항과 norm-geometric tail을 바깥 반올림하고 q/(N+2)<1을 검사했다. Incoming state error와 incoming accumulated goal error를 모두 보존한다. Constant coordinate만 정확1로 놓는 것은 state error reset이 아니다.

정본은 results/final/CERTIFICATE.json의 decimal endpoint 문자열이다. 전체 Q2 error radius:

    1.24562621622235824207383113339461707530299044441803315408199e-17 eV/H.

Q2:

    [-1.50083751841394950632064880334570386314425735529232106864330e-14,
     -1.49834626598150478983650114107891462899365137440348500233511e-14] eV/H.

Q1:

    [2.85134009075075984401373379276699166847785828202312689194441e-25,
     2.85134011140690141388225533555738922220298125530436502066736e-25] eV/H.

Q0의 표시범위는 약[1.1811319285335526e-5,1.1811319285360660e-5]eV/H다. Q2 error radius는 중앙값 절댓값의0.083065% 미만이다. N의 goal-only2.6141e-21을 total error로 잘못 사용하지 않고, 그 밖의 state-response error와 moment/slope arithmetic 차이를 새로 포함했다.

이제 Q1/Q2 coefficient integration-error와 Q2 sign은 해당 신뢰 기반에서 조건부로 닫혔다. Confidence interval이 아니며 물리 원자율오차를 포함하지 않는다. Raw first response를0으로 만들지 않았다. Finite epsilon에서는 여전히 |epsilon|E1+epsilon²E2 외에 실제 state Taylor remainder가 필요하다. 따라서 EPS_HALF 1/4나 finite BI contrast sign을 승인하지 않는다.

## 실제 검증과 실패 분류

새 focused34tests PASS, Python8파일syntax PASS. Tube gate1개는 assertion RED→GREEN. Zero tangent의 정수제곱을 log/exp로 처리해 ValueError가 난1개는 exception 재현·회귀수정이다. 나머지32개는tests-after다. 모델오류가 아니라 새 AD power implementation의 domain 오류였고, nonnegative integer powers를 곱셈으로 계산하도록 고쳤다. 수정 전 코드와 로그를 보존했고 donor/source/tolerance는 바꾸지 않았다.

새 interval arithmetic는 정확 Fraction240개 사칙연산과 대조했다. 독립 mpmath110자리 경로에서 scalar rates/epsilon differentiation으로 만든 RHS171성분, Jacobian34성분, 실제 마지막cell의 unshifted61D matrix-exponential action61성분이 모두 interval에 포함됐다. 기존 두solver Q0/Q1/Q2 여섯 저장값도 범위에 포함됐지만 그 IVP는 재실행하지 않았다. 110자리는검산정밀도이지물리정확성자릿수가아니다.

Final certificate/test/inline artifact checker의3명령은exit0. logs/09_FINAL_CERTIFICATE,10_FINAL_TESTS,11_FINAL_CHECK와 VERIFICATION.json을 보존했다. Source hashes8개와 최종 proof SHA256=7830141f9f73fd873431933228796244745e53e4aeb3d64d95a081f694fc826c를 고정했다. 독립대조에 쓴 full01과 final은 elapsed time 제외 모든 scientific fields가 정확히같아 대조를 반복하지 않았다.

개발2cell probe, 예비20cell 및 최종20cell 계산은 구분한다. results/attempt01은 incomplete 개발자료이며 그때의 full-endpoint display는 유효한구간claim이아니다. 현재runner는 incomplete Q_intervals를null로 반환한다. ARTIFACT_MAP.json과 results/final이정본기준이다.

새 native/physicalIVP/root/history/oldscience/원자적분/receiverproductionmutation은0이다. 새 interval RHS/J/time-Taylor/matrix계산은실제수행했다. 독립human/agentreview와proofassistant는없다.

신뢰기반은 Python Decimal directed arithmetic와 correctly-rounded exp/ln 계약, 새 nested AD/Taylor 구현, 이전 F04M moment enclosure 및 F04N goal residual이다. Formal verifier나 독립 구현의 전범위검증으로표현하지않는다. Python공식decimal/fractions와SUNDIALS CVODES FSA를배경자료로확인했으며source-specific비교정리와결과는직접유도/계산했다.

## 정본·실제 이중백업

File=BASS_CR_CHAT_F04O_20261006_v1.zip.
bytes=1828328.
SHA256=c1294b628aed13b37bc323c4be3478ddb1343def8d1059bc13dab1346a3bb292.
ZIP78entries/77payload의size/SHA256/CRC와testedsourcehashes를local검증했다.

Drive upload success 및metadata readback:id1ZJ_QpR0xFMXqz3Ird23vUS3v_ARslKX0,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size1828328일치.
Dropbox completed:id:BSpOijBcT10AAAAAADzg6w,size1828328,modified2026-10-06T05:22:13Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04O_20261006_v1.zip.

동일immutableZIP을두provider에create-only저장했다. R1 UPLOAD_VERIFIED이며remotechecksum은응답에노출되지않았다. 새ZIPfullrestore/independentremotebytehash는미수행이다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. 이Git문서는summary/provenance/backup pointer,fullcode/tests/REPORT/증거는ZIP이다. 실제publicationcommit/tree는detached DELIVERY_RECEIPT에기록한다.

## 다음 이론

Q2 coefficient-error/sign node는이범위에서종료한다. 다음F04P는 finite-epsilon STATE remainder다. F04N directional lift 또는동등한재구성,비선형thermaldefect,epsilon전체의공통tube와stability를구성해야한다. 이번계수인증이나기존IVP를동기화만을위해반복하지않는다. ActualBItransaction-dependent인증과ownerimportACK는별개다.

CR_OFF_FASTEST,precisionatomicPARKED,physicalproductionHOLD,G02UNRESOLVED,capture=false,all_boundOPEN,b_gridNO_GO,actualCRcounter=null. OwnerimportACK/rawnativeheat=null유지. FullK/318patch/CR-on/소비된원자승인재사용·새mandatorygate·producer변경은없다.
