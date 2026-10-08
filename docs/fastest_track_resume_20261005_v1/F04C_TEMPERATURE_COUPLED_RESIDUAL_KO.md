# F04C: 온도의존 FT03의 4변수 BE 잔차와 해석 미분

## 판정과 연구 범위

SCOPED_TEMPERATURE_COUPLED_RESIDUAL_AND_DERIVATIVES_COMPLETE.

CR_OFF_FASTEST에서 실제 온도의존 FT03 source를 읽고 세 분율과 로그 온도의 4변수 BE 잔차, 해석 Jacobian/Hessian, photon Schur 전달식을 구현·검산했다. 수소 RR kinetic coefficient의 온도 미분이 소스의 온도 범위 안에서 부호를 바꾼다는 제한된 결과도 정확 유리수 enclosure로 확인했다. Production Rust 변경, native FT03 실행, root solve, owner box 확장, canonical REI-F04 종결은 하지 않았다.

시작 및 게시 직전 bass_cr HEAD=da8b174267e27f0a70ee7ff12fb130179c1abfab, tree=08622203a1827d787071764cb22c2feb1e68543f. 같은 research/r4q-gap-closure-20261001 branch의 새 문서다. 첫 게시 a0e5fe8839b7dc7d6a310df2fdc4ca6a480b70a1에 섞인 다른 언어의 문장을 이 교정에서 한국어로 고쳤다. 연구 코드·시험·수치·원본 ZIP은 바꾸지 않았고 첫 게시 이력도 보존했다. 이전 F04A/B, native F03 결과와 전체 reference campaign은 재실행하지 않았다.

## 소스와 owner box 확인

고정 receiver snapshot은 cosmosapjw-quantum/rei_bianchi@7a15daa38b60a5174315747b9194564dc2d4eb8b, branch는 forward/rust-reion-kernels-20260922다.

- rust/rei_microphysics/src/ft03_controlled.rs: blob370fd2fa60521f2dc121ee81c7d24013a3b0d1e5. RHS·event·domain·solver 원문을 읽었지만 full local bytes는 보관하지 않았다.
- rust/rei_microphysics/src/ft03_rates.rs: blobb8a85ff37de160ecc576a168e4259ed23920a499. 원문2755 bytes를 보관하고 blob/SHA256을 검증했다. SHA256=1a97cd7a3555deeb4d8700376cd84580c5102127773bc3a235a29c33b0c1542f.
- hhe_events.rs: blob57a63eee1e9d8c4aa2b5ed663dbea15619359f71. 실제 EOS·energy 구간을 읽었다.
- atomic_provider.rs: blob62211d8910cd332fffa8f94c6989cae77128916e. Reference constructor와 Verner cross_section 구간을 읽었다.
- docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_successor_binding.json: blob37af0db4699bdd39c79c0ed6ce8bfb014f5571f3. 전체 계약을 읽었다.
- 같은 prefix의 runtime_returns/REI-F04.json: blob7c0e3f514a16d6fdf435ee27f672e5315b01b58e. Claim·blocker·validation·unresolved·sync 구간을 읽었다.

모형 ID는 REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1이다. Proper/static gas, 양의 nH/nHe, 고정 에너지 광자군3개, 온도의존 RR/CI와 HeII DR 채널2개, Case-A escape를 포함한다. 30000–110000 K inclusive는 구현 guard이며 물리적 rate 정확성을 인증한 범위가 아니다. F03의 zero-nuclear-density 극한을 FT03 API에 임의 이식하지 않는다.

Owner 계약은 ACTUAL_PARENT_DOMAIN_NOT_FROZEN 및 augmented_parent_domain=NOT_FROZEN_FOR_ACTUAL_FT03_SUCCESSOR를 명시한다. Uniform parent/source uncertainty, root inclusion, implicit J/H, same-parent full/half remainder, checker/public width는 미완료다. 이번에는 임의 상자를 만들지 않았고 source temperature guard를 owner joint-parent box로 바꾸지 않았다.

종료 단계 receiver752e360a80e8622bcbaffae54183258b2e67b810를 수신했다. 비교 결과 한 commit과 REI-CHAT-FLRW04-20261005의 새 문서8개이며 FT03 code/binding 변경은 없다. 그 독립 연구를 재실행하거나 현재 결과에 합산하지 않았다. 기존 actual native F03 bits의 부재 blocker는 폐기된 상태를 유지하며 그 값을 FT03 결과로 재명명하지 않는다.

## 온도를 남긴 4변수 잔차

x=(xHII,xHeII,xHeIII), l=(1-xHII,1-xHeII-xHeIII,xHeII), d=(nH,nHe,nHe), ne=nH*xHII+nHe*(xHeII+2*xHeIII), p=nH+nHe+ne, eta=ln(T/Tstar), Tstar=1K로 둔다.

    U(x,eta)=1.5*kB_EOS*p*Tstar*exp(eta)
    s_ag=c*sigma_ag
    kappa_g=sum_a d_a*l_a*s_ag
    D_g=1+h*kappa_g
    Nbar_g=N_g0/D_g.

h>=0인 물리 분율 영역에서는 D_g>=1이다. 이 소거는 고정 단면적·광자 재주입 부재·정적 기하에 결합되어 있다. 온도의존 RR/CI/DR만으로는 Nbar의 eta 의존성이 생기지 않는다.

A_a(T)=alpha_RR,a+indicator(a=HeII)*sum_k(delta_DR,k), Gamma_a=sum_g s_ag*Nbar_g로 놓으면

    j_a=l_a*Gamma_a+ne*(l_a*beta_a-x_a*A_a)
    F=(j0,j1-j2,j2)
    K_a=kB_rate*T*alpha_a*(1.5+g_a)
    g_a=d ln(alpha_a)/d eta
    H_g=ev_erg*sum_a d_a*l_a*s_ag*(E_g-chi_a)
    P=sum_g H_g*Nbar_g
    W=sum_a d_a*(l_a*beta_a*chi_a*ev_erg+x_a*K_a)
      +nHe*xHeII*sum_k delta_k*E_DR,k
    L=ne*W
    Q=P-L
    R(z)=(x-x0-h*F, (U-u0-h*Q)/Ustar), z=(x,eta).

Ustar는 고정 양수 residual scale이다. Reference의 state derivative에서는 old.u를 고정 숫자로 사용했다. 향후 initial state의 parent derivative를 구할 때 scale의 취급을 별도로 고정해야 한다. Native residual_norm의 max floor까지 미분한 식은 아니다.

EOS의 kB는 gas.kb_erg_k, kinetic/DR moment의 kB는 rate module 내부 상수다. 기본값은 같지만 임의의 public gas 설정에서도 같다고 가정하지 않았다. c,kB,eV-to-erg를 유지했고 N은 proper cm^-3, U는 erg cm^-3, h는 초다. RR kinetic K는 derived controlled coefficient이며 raw Grackle cooling parity가 아니다.

Escape는 해 z가 정해지면 RR의 binding+kinetic과 각 DR의 binding+E_DR를 같은 endpoint에서 평가하여 복원하는 보조값이다. 원 solver는7좌표와 escape의 actual endpoint residual을 다시 평가한다. 이번4변수 표현은 exact-real 등가식이며 새 production integrator를 만들었다는 의미가 아니다.

## 해석 Jacobian/Hessian과 필요한 미분 차수

Nbar_i=-h*N0*kappa_i/D^2, Nbar_ij=2*h^2*N0*kappa_i*kappa_j/D^3이다. EOS·전자밀도 피드백, HeII의 j1-j2, CI/RR/DR와 kinetic moment의 온도 미분을 모두 포함한4x4 Jacobian과4x4x4 Hessian을 src/thermal_residual.py에 구현했다.

g'=dg/deta, g''=d2g/deta2이면

    alpha_eta=alpha*g
    alpha_etaeta=alpha*(g*g+g')
    K_eta=kB*T*alpha*((1+g)*(1.5+g)+g')
    K_etaeta=kB*T*alpha*((1+g)^2*(1.5+g)+(3.5+3*g)*g'+g'').

따라서 thermal residual Hessian에는 ln(alpha)의3차 log-temperature 미분이 필요하다. Source가 반환하는 g와 g'만으로 K_etaeta를 채우면 안 된다. HII/HeIII에서 v=(lambda/0.522)^r, a=1.503, b=1.923, r=0.470이면

    g=-a+b*r*v/(1+v)
    g'=-b*r^2*v/(1+v)^2
    g''=b*r^3*v*(1-v)/(1+v)^3.

HeII의 순수 멱법칙에서는 g'=g''=0이다. CI와 각 DR의 log-slope/2차 미분도 소스 식에서 직접 유도했다. 현재 구현은 state-z 미분까지이며 R_parent, R_z,parent, R_parent,parent API는 다음 작업으로 남아 있다.

## 정확 부호 판정: 수소 RR kinetic coefficient의 비단조성

K_eta=kB*T*alpha*Phi, Phi=(1+g)*(1.5+g)+g'를 평가했다.

|T[K]|Phi 표시값|판정|
|---|---:|---|
|30000|+0.09493740758406525315|정확 구간 하한>0|
|50000|+0.05173459970477654396|고정밀 진단값만 계산|
|110000|-0.01585101975280847647|정확 구간 상한<0|

두 인증점에서 K 자체는 양수다. 연속성에 따라 source guard 내부에 적어도 하나의 stationary point가 있으며 K는 해당 구간에서 단조가 아니다. Root 탐색은 실행하지 않았다. 이는 해당 RR kinetic coefficient의 성질이지 총 냉각률의 비단조성, BE 다중해, solver 불안정성, 실제 원자 냉각의 관측 사실을 의미하지 않는다.

부호 증명은 source binary64 literal의 정확 유리수상으로 정의한 실수 식을 대상으로 한다. ln의 atanh 급수와 exp의 Taylor 급수에 명시적 remainder를 붙여 Fraction interval로 전파했다. Native powf/exp의 반올림 경로를 감싼 것은 아니다. Exact JSON의 분자·분모는 signed hexadecimal integer 문자열이며 Fraction(int(num,16),int(den,16))로 가역적으로 읽는다.

## Photon Schur와 열 피드백

Candidate의 exact EOS 온도를 고정하고 rN=D*Nhat-N0로 두면, 주어진 온도에서 source가 광자 수밀도에 선형이므로

    R_x=r_x+h*M*D^(-1)*rN
    R_E=(r_u+h*H^T*D^(-1)*rN)/Ustar.

F04B의 선형 thermal denominator를 이 식에 가져오지 않는다. Native가 반환한 반올림 온도와 exact EOS 온도의 차이도 별도로 취급해야 한다. 이번에는 native FT03 bits의 재관측이나 결합을 실행하지 않았다.

J=[[A,b],[c^T,d]]에서 A가 가역이면 열 결합에 필요한 판정은 S=d-c^T*A^(-1)*b이며 d만으로는 충분하지 않다. 실제 root와 고정 scale에서 eta_u0=1/(Ustar*S), x_u0=-A^(-1)*b/(Ustar*S)다. 따라서 F03의 x_u0=0을 일반 FT03에 옮길 수 없다. S의 uniform 부호나 root 가역성은 인증하지 않았다.

같은 original parent의 implicit derivatives와 half composition 공식은 보고서에 정리했다. Half1 root enclosure와 의존관계를 half2 old-state에 전달하고 각 half의 endpoint events/temperature를 유지해야 한다. Full 후보나 마지막 endpoint 하나로 대체하지 않는다. Mixed parent derivatives와 실제 half assembly의 구현·인증은 이번 범위 밖이다.

## 실제 검증과 실패 기록

새 focused tests23 PASS, symbolic11조건 True, Python syntax PASS. Jacobian48성분·Hessian128성분·rate derivative66값을 별도 고정밀 수치미분 경로와 대조했다. 유한점 구현 검증이며 uniform certificate나65자리 정확성 보장은 아니다. 실행 argv/exit와 전체 로그를 ZIP에 보관했다.

2시험은 assertion RED→GREEN,20시험은 tests-after,1시험은 실제 serialization exception을 재현한 회귀수정이다. 마지막1건을 assertion TDD로 재분류하지 않는다. 독립 human/agent review와 proof-assistant 검증은 수행하지 않았다.

초기 diagnostics에서는 미분 결과 JSON 저장 뒤 거대한 유리수의 십진 문자열화가 Python4300자리 제한에서 실패했다. 수학적 부호 판정 실패가 아니다. 원 serializer와 실패 로그를 보존하고 lossless signed hexadecimal 저장으로 고쳤다. 기존 derivative JSON을 유지한 채 직렬화만 복구한 뒤 최종23시험과 문법 검사를 다시 실행했다. 허용오차·수식·proof inequality는 바꾸지 않았다.

Direct raw GitHub 네트워크는 DNS 실패였고 rustc는 PATH에 없었다. 소스는 connector로 읽었다. 새 native 실행0, root solve0, 원자 적분0, cosmological history0, owner box expansion0, 기존27/42시험·reference campaign 재실행0이다. Arbitrary precision reference의 성공으로 native checked_product의 underflow 거절 조건을 무효화하지 않는다.

## 정본 패키지와 이중백업

파일=BASS_CR_CHAT_F04C_20261005_v1.zip
bytes=2596825
SHA256=bd39f3e8de95d48115a425211580d412f820f751d0ea773ce33f90c1c7419b85
ZIP48 members,47payload SHA256/CRC를 local에서 검증했다.

Drive는 success ACK를 반환했다. id=1Fm8x-NwlyuzaWcypvOFs3b-CyuSSrL_b, parent=1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ. Metadata readback으로 이름·size2596825·parent를 확인했다.
Dropbox는 completed를 반환했다. id=id:BSpOijBcT10AAAAAADyUQg, size2596825, modified=2026-10-04T16:37:31Z.
Dropbox path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04C_20261005_v1.zip

동일 immutable archive를 두 provider에 create-only로 저장했다. R1 UPLOAD_VERIFIED(ID/name/size/path 또는 parent)이며 remote checksum은 응답에 노출되지 않았다. Full restore와 독립 remote bytehash는 실행하지 않았다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. 이 Git 문서는 summary/sync이고 code/tests/상세 증명/exact JSON의 정본은 ZIP이다. ZIP 안에는 미래 업로드 성공을 미리 기록하지 않았다.

## 다음 노드와 유지한 제한

다음 보조 노드는 BASS-CR-CHAT-F04D_ORIGINAL_PARENT_DERIVATIVES_AND_TWO_HALF_ASSEMBLY다. Live owner 계약을 읽고 필요한 mixed parent derivatives와 same-parent half composition을 구현·검산한다. 실제 box가 미정이면 형식 유도와 구현을 진행하되 임의 box의 uniform certification을 선언하지 않는다. 이번 J/H/sign proof/23시험과 이전 native probe·old suite를 같은 목적으로 반복하지 않는다. 조건부 공식과 actual runtime 인증을 구분한다.

CR_OFF_FASTEST, precision atomic PARKED, G02=UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO를 유지한다. CR-F0=WAIT_FOR_ACTUAL_CR_OFF_DISPATCH_BINDING이며 source/loader/callback 관측=null이다. 기존 S-only 두 window 상계5.599633283869504e-17과7.49726779045559e-17 ta^-1을 계승한다. CR-on/full-K/R4AQ/318patch/소비된 승인은 재사용하지 않았다. 이번 결과를 canonical REI-F04 완료나 새 mandatory gate로 만들지 않는다.
