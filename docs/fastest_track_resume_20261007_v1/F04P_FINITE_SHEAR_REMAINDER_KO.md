# F04P: 유한 shear의 상태 나머지와 작은 매개변수의 가열량 부호

## 판정

Task: BASS-CR-CHAT-F04P_UNIFORM_FINITE_SHEAR_REMAINDER.
Status: CONDITIONAL_FINITE_PARAMETER_REMAINDER__SMALL_SHEAR_SIGN__EPS001_SIGN_OPEN.

같은 raw-ray real-analytic FT03 가족의 첫 macro 0..1250000000 proper seconds에서, 모든 |epsilon|<=1/100에 대해 실제 상태와 누적 HI 가열량의 삼차 매개변수 나머지를 조건부로 제한했다. F04N의 기하 입력이나 quadratic-state heat 삽입 항만 계산한 결과가 아니다. 전체 nonlinear gas/thermal feedback를 포함한 1·2·3차 상태변분의 균일 상계를 사용한다. F04O의 Q1/Q2 계수 인증은 계승했으며 재실행하지 않았다.

    |Q(epsilon)-Q(0)-epsilon*Q1-epsilon^2*Q2| <= C3*|epsilon|^3
    C3 = 1.23390291975893887828485856751336299848170747518468210837655e-10 eV/H.

C3는 sup|Q'''|/6의 상계이며 실제 Q3 값이나 Q''' 자체가 아니다. 기존 Q1/Q2 구간과 결합하면 1e-8<=|epsilon|<=1e-4 전체에서 DeltaQ=Q(epsilon)-Q(0)<0이다. epsilon=1e-6에서 DeltaQ(epsilon/2)/DeltaQ(epsilon)는 [0.2468813387...,0.2531186613...] 안이다. epsilon=+/-0.01에서도 remainder bound는 유효하지만 contrast 구간은0을 포함해 부호는 미해결이다. 기존 native EPS_HALF/history의 물리적 승격은 없다.

## 소스와 동시 진행 계승

bass_cr 시작 및 게시 직전 HEAD=ddd4928e78d4a20b061250afb92892a168eebba9, branch=research/r4q-gap-closure-20261001. 같은 branch의 새 summary만 추가한다. Producer/CODEX_SYNC/runtime_returns/원자표/물리 angular weights는 변경하지 않았다.

Receiver intake=a0001ca14644fc9fd2fbe52f8cfcae3edbedd110, branch=forward/rust-reion-kernels-20260922. 이전5673fc60 이후3commit의 변경을 읽었다. SPEC04와 별도 IGM foundation/thermal provider가 추가됐지만 이번 원 source는 유지했다. live paired_runtime.rs blob70eed18b07b6dd4297d8ef8da6d7e1be8e44456e, ft03_rates.rs blobb8a85ff37de160ecc576a168e4259ed23920a499를 확인했다. 새 Grackle 기반 IGM provider를 FT03 응답계에 섞거나 그166시험을 이번 시험으로 합산하지 않았다.

ZIP 봉인·업로드 이후 게시 직전 receiver가 dbb54009a517242ff5a41c805512471a74dd25f4로 전진했다. a0001ca 이후1commit의 변경은 SPEC05 문서8개 추가이며 scientific source 변경은 없다. docs/fastest_track_chat/REI-CHAT-SPEC05-20261007/README_KO.md(blob7ee9558e24a570d82e12afb4f496bb0c57b37159)를 읽어 별도 absorption-weighted spectral/thermal 결과를 수신했다. 그 계산을 재실행하거나 F04P의 premise로 가져오지 않았다. 봉인 ZIP의 intake와 새 마지막 readback을 혼동하지 않으며 이 추가 ACK는 본 문서와 detached delivery receipt에 남긴다.

F04O 입력 archive는1828328bytes, SHA256 c1294b628aed13b37bc323c4be3478ddb1343def8d1059bc13dab1346a3bb292다. 실제 archive SHA와CRC를 확인했고 필요한9개 원 파일을 선택 보존했다. inputs/SELECTED_MANIFEST.json이 경로/size/SHA를 고정한다. 기존20cell 계수 인증, F04N goal residual, F04M 두 IVP와 old science suite는 재실행하지 않았다.

## 목표 가족과 단위

Signature(-,+,+,+), H_i=H(1+epsilon*a_i), a=(1,-1,0), rho=1/100이다. Primitive binary64를 정확 실수로 읽고 연산과 초월함수는 실수 함수로 해석한다. H_i는 이 가족의 실수 곱이며 native가 각각 반올림한 H_i 비트와 동일하다고 놓지 않는다. Native hat remap/adaptive 프로그램의 매개변수 미분도 아니다.

H=1e-14/s, nH0=1e-4cm^-3, fHe=.083, 초기분율(.9,.3,.6), w0=13.620772387478219eV/H, 초기 .05photons/H at13.7eV, continuous source5e-15photons/H/s와 active node16..24를 유지했다. 각 수치는 원 literal의 exact-real 의미다. c=29979245800cm/s, kB와eV환산을 유지한다. 초기 alpha=1/128, source beta=norm(q)^(-3)/sum norm(q)^(-3)는 서로 다르며 raw128ray를 덮어쓰지 않았다. 작은 Q1도0으로 대체하지 않는다.

가스 G=(xHII,xHeII,xHeIII,w/w0), P=sum_d p_d, pstar=.05/H다. 같은 HHe CI/RR/2DR, EOS/전자수, FT03 RR kinetic moment와 gas work를 포함한다. 선택된 에너지에서 광흡수만HI이며 아래 fit-cutoff photons는 no-feedback passive sector다. Physical binding chi와 fit cutoff13.6eV를 구분한다.

    p_d' = h_d K p_d - diag(kappa(G,t))*p_d + S*w_d*e_top
    G' = f(G,P,t)
    Q' = c*nH(t)*(1-xHII)*sum_j (Ej-chiHI)*sigma_j*P_j.

Counts는photons/H, Q는eV/H, t는proper seconds다. Tracefree이므로 nH=nH0 exp(-3Ht)는epsilon에 독립이다. u=t/T로 정규화할 때 T를 우변에 한번만 곱한다. K_jj=-k_j,K_j,j+1=k_(j+1),k_j=Ej/(Ej-E_(j-1))다.

## 유한 parameter 전체의 공통 해 영역

가스 초기좌표의 각 성분에 반경 .02인 box를 잡았다. H/He simplex와 양의 EOS 내부다. h_d>=H(1-rho)>0, 비음수 opacity/source이므로 photon system은 positivity를 유지하고 active total은 initial+source 이하이다.

Lambda_j^+=T*H*(1+rho)*k_j, eta=T*S/pstar,n=top-j라 두고 loss를 버린 downward-chain 비교를 반복 적분하면

    P_j(u)/pstar <= product_(l=j+1..top)Lambda_l^+
                   *[u^n/n!+eta*u^(n+1)/(n+1)!].

전체질량 상계1+eta와 작은 쪽을 취한다. 초기/source의 top-only support를 실제 input에서 확인했다. 이 식은 photon direction을 평균 물리방정식으로 닫지 않고도 얻는 점유 상계다.

이 occupancy와 gas box, 전체시간·parameter에 대해 gas RHS를 구간평가했다. 정규화시간 전체의 drift 상계는 표시값으로

    [1.539155939075032e-4,5.023964269346e-7,
     6.395222099596e-8,3.759851365595e-5].

모두 .02보다 엄격하게 작다. 처음 box를 벗어나는 시각이 있다고 가정하면 그때까지 positivity와 drift bound가 유효하여 경계까지 이동하지 못하므로 모순이다. Compact smooth gas-domain의 국소 존재·유일성과 continuation을 연결해 모든 |epsilon|<=.01의 공통 해 영역을 얻는다. 온도는 [48426.0110...,51611.7493...]K로 FT03 guard 내부다. 새 물리적 불확실성 영역이나 native state projection을 만든 것이 아니다.

## 임의 epsilon 중심의 정규화 도함수

epsilon0가[-rho,rho]의 임의 점일 때 Y_[k]=(1/k!)*partial_epsilon^k Y|epsilon0로 정의한다. 원0에서의 Q1/Q2뿐 아니라 Taylor 나머지의 모든 중간점에 적용한다.

z=epsilon Ht, F_d(z)=sum_i[q_di^2/r_d]*exp(-2a_i z), r_d=sum q_di^2. Tilted mean mu와 central moments를 쓰면

    h_d/H=1+epsilon*mu,
    mu_z=-2Var(a), mu_zz=4central3(a),
    mu_zzz=-8[central4(a)-3Var(a)^2].

A=max|a_i|=1,tau*=HT에서 normalized h derivatives의 전시간 상계는

    |h_[1]|/H <= A+2rho*A^2*tau*
    |h_[2]|/H <= 2A^2*tau*+4rho*A^3*tau*^2
    |h_[3]|/H <= 4A^3*tau*^2+(16/3)rho*A^4*tau*^3.

w_d=beta_d exp(f_d)/sum beta exp(f), f_d=-(3/2)ln F_d의 정규화 분모까지 미분했다. Log-normalizer L에 대해 w'''/w=(f'-L')^3+3(f'-L')(f''-L'')+f'''-L'''이다. Sum abs 제삼 z도함수는615A^3 이하이며, epsilon coefficient로 바꾸면

    sum|w_[1]| <= 6A*tau*
    sum|w_[2]| <= (51/2)A^2*tau*^2
    sum|w_[3]| <= (205/2)A^3*tau*^3.

여기서도 sum absolute를 absolute of sum으로 바꾸지 않았다. Exact evenness/alpha=beta를 가정하지 않는다.

## 실제 state 및 heat 나머지의 전파

Gas4 절댓값과 V_kj=sum_d|p_dj,[k]|/pstar의 photon9를 합친13성분 비교계를 쓴다. 물리계의 angular closure가 아니라 도함수의 norm 상계다.

각k에서 gas kth coefficient는 f_G G_[k]+f_P P_[k]+N_k다. Lower-order jets를 넣고 kth coefficient를0으로 평가해 N_k를 구간으로 계산했다. 둘째차수 Hessian, 셋째차수의 first×second와 first^3, nonlinear thermal/전자수 되먹임을 포함한다.

Photon kth 식에는 (h0K-kappa0)p_[k]-kappa_[k]p0, sum_(r=1..k)h_[r]Kp_[k-r], -sum_(r=1..k-1)kappa_[r]p_[k-r], S*w_[k]를 모두 유지한다. Opacity의 affine fraction 구조를 사용했으며 다른 nonlinear opacity에 무조건 적용하지 않는다.

공통 M은 basebox의 gas Jacobian 절댓값, opacity gas-column, downward inflow로 구성한다. 음의 loss 대각은0으로 올려 M>=0을 얻었다. 이는 보수적 상계다. k=1부터3까지 이전차수의 전시간 상계를 lower jets에 넣어

    b_k'=M*b_k+r_k, b_k(0)=0

을 순차 계산한다. M,r_k>=0이므로 endpoint b_k(1)는 전시간 상계다. 원초기조건이epsilon-independent여서 모든 변분의 초기값0은 정당하다. 누적 heat에는 a_k'=ell^T*b_k+sup|N_k^Q|를 사용한다. State13+goal1+constant1의15D 양의 행렬지수 작용을 각차수에서 계산했다. Taylor80항과 명시적 norm-tail을 방향반올림했다.

k3 state sup의 가스부분은 표시값으로 xHII1.4961712821e-9,xHeII7.9126026936e-16,xHeIII4.9823705259e-17,w/w0 9.1148918503e-12다. 이들은 전시간·전parameter에서 |partial^3 G|/6의 상계다. 각 값에 |epsilon|^3를 곱하면 해당 실제 state remainder를 제한한다.

Heat에 대해 C3=sup|partial^3 Q|/6의 상계를 얻었으므로 Taylor 적분나머지에 의해

    R(e)=e^3/2*integral_0^1(1-v)^2*Q'''(v e)dv,
    |R(e)|<=C3*|e|^3.

C3에는 실제 상태의 고차응답과 nonlinear thermal feedback가 들어간다. F04N의 직접 polynomial heat 삽입 항으로 대체한 것이 아니다. 방향별141D lift IVP나 finite-epsilon nonlinear history를 적분하지 않고 이 비교경로로 목표를 닫았다.

## 유한 contrast 결과와 미해결 부호

F04O의 정확 Q1/Q2 구간을 그대로 가져와

    DeltaQ(e) in e*[Q1]+e^2*[Q2]+[-C3*|e|^3,+C3*|e|^3]

를 계산했다. 동일 exact-real family의 차이에서 Q(0)는 대수적으로 소거된다. 서로 다른 native history의 오차가 상쇄된다고 가정한 것이 아니다.

Outward로 느슨하게 쓴 결과:

    e=+1e-4: -2.734741e-22 < DeltaQ < -2.644430e-23 eV/H
    e=-1e-4: -2.734742e-22 < DeltaQ < -2.644436e-23 eV/H.

B=-upper(Q2),L=max|Q1|,e_min=1e-8,e_max=1e-4에서 L/e_min+C3*e_max<B를 정확 유리수로 확인했다. 따라서 두 부호를 포함한 1e-8<=|e|<=1e-4 전체가 음수다. 표본몇개만검사해 전체band를 주장하지 않는다.

반감식 DeltaQ(e/2)-DeltaQ(e)/4=eQ1/4+R(e/2)-R(e)/4를 이용하면 gap<=|e|L/4+(3/8)C3|e|^3다. e=1e-6에서 분모 DeltaQ(e)의0 배제를 먼저 확인한 뒤 비를 계산했다. 안전한 표시범위는

    0.24688 < DeltaQ(e/2)/DeltaQ(e) < 0.25312.

정확한 끝점은0.2468813387254800...와0.2531186612745200...다. 작은 비영 Q1을 보존한 결과이며 exact1/4 또는 epsilon^4 remainder를 가정하지 않는다.

|e|=.01에서 remainder upper는1.233902919758939e-16eV/H로 quadratic contribution약1.5e-18보다 크다. 실제 contrast enclosure는0을 포함한다. 이는 상계가 해당 부호판정에 충분히 날카롭지 않다는 뜻이며 실제 부호역전이나 이차응답 실패가 아니다. 원 native EPS_HALF, 원 rounded H_i, 전체 history/physical fit/spectral-angular continuum은 미승인이다.

## 실행·검증·실패

최종32focused tests PASS,24artifact conditions PASS,12개 새Python 파일syntax PASS. Factorial계약1개는 assertion RED→GREEN,31개는tests-after다. 기존F04O34시험/계수증명/F04M IVP는 재실행하거나 수량에 합산하지 않았다.

독립 mpmath110자리 경로에서 gas/heat jet60값, 실제 augmented matrix exp42성분, raw-ray geometry caps3456개, normalized source L1 caps27개, independent h derivatives54개를 검사해 모두 구간 내 포함됐다. 이는 finite implementation 대조이며 formal full verifier/110자리 물리정확성이 아니다. 독립human/agent review와proof assistant는 수행하지 않았다.

새 bound는 개발1회와final1회 계산했고 공통scientific fields가 정확히 일치했다. 각run은3개의 양의 비교행렬 action이다. 새 physical/coefficient IVP,native,root,history,oldscience replay,원자적분,receiver mutation은0이다. 첨부Rust 환경 script의toolchain도 호출하지 않았다.

독립검사에서 Decimal을mpmath.mpf에직접넣어 TypeError가 났다. 검사adapter만str(Decimal)로 바꾸고 원파일/실패로그를 보존했다. Scientificbound/code/tolerance는 바꾸지 않았다. 별도로 문서조립 Python 문자열의 triple apostrophe 충돌로 SyntaxError가 발생해 Markdown과JSON 조립을 분리했다. 이 문서오류도 과학실패와 구별해 기록했다.

VERIFICATION.json이12개 source/test SHA와최종 proof SHA256 0621ab3c0918d51a06305785df20cf6bc8883154b655d31413b33357c566479a를 고정한다. Logs FINAL_COMMANDS.json의3개 최종명령은exit0이다. 정본은results/final/CERTIFICATE.json이며attempt01은개발출력이다.

## 봉인 정본과 실제 이중백업

File=BASS_CR_CHAT_F04P_20261007_v1.zip
bytes=690469
SHA256=f7fdd34dbc66c3681873bc3d6019ef629ec4bf39419f00f3502e8f86d1a00e48
ZIP70entries/69payload size,SHA256,CRC 및testedcode hash를local에서확인했다.

Google Drive upload success와metadata readback: id1GzmYetEAdY_ERde6378VWS-RJenMZ6qk,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size690469일치.
Dropbox completed: id:BSpOijBcT10AAAAAADzjvQ,size690469,modified2026-10-07T10:19:21Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04P_20261007_v1.zip.

동일immutableZIP을create-only로두provider에저장했다. R1 UPLOAD_VERIFIED이며remotechecksum은응답에노출되지않았다. 새ZIP의fullrestore/independentremotebytehash는미수행이다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. Git은summary/provenance/backup pointer,전체유도/code/tests/inputs/정확결과/logs는ZIP이다. 실제publicationcommit/tree와late receiver ACK는봉인ZIP밖detached DELIVERY_RECEIPT에기록한다.

## 다음 연구 경계

이F04P의uniformC3state/heat remainder와작은parameterband의sign은위범위에서종료한다. .01의부호는열려있다. 다음은그폭을줄이기위해signedangular/permutationdefect와4차변분,또는goal-specific/time-dependentcomparison을검토한다. Exactraw-evenness나원가중치변경으로해결하지않는다. 같은3차proof/기존Q2certificate를단순동기화를위해반복하지않는다.

CR_OFF_FASTEST,precisionatomicPARKED,physicalproductionHOLD,G02UNRESOLVED,capture=false,all_boundOPEN,b_gridNO_GO,actualCRcounter=null유지. OwnerimportACK/rawnativeheat도null이며실제BItransaction-dependent인증은별도다. FullK/318patch/CR-on/소비된원자승인재사용,새mandatorygate,producer수정은없다. 산술신뢰기반은F04O의Decimal/Taylor/AD primitive와새비교구현 및계승한조건부Q1/Q2인증이다. Formal independent verifier를통과했다고주장하지않는다.
