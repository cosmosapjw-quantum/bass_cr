# BASS_CR: 움직이는 primary 이온화 복원, 2026-10-14

선택 노드 `NT_GEOMETRY_IONIZATION_RESTORE`의 구성적 이론 유도와 단계 내 검산을 완료했다. 기준은 PR52 head `110724bf8e4fc0d937d3098ee78f441aa22802c2`, 보존한 geometry 원본 ZIP이다. 먼저 원본 백업/게시를 복구한 commit은 `368b135229644ab09814d4dd3ca86865d0346cc8`이며, 그 뒤에 본 연구를 수행했다. 독립 external scientific review는 미수행이다.

## 전체 원본 및 실제 보존

- 새 archive: `BASS_CR_IONIZATION_RESTORE_20261014_SOURCE.zip`.
- Bytes:2759736; members39; manifest-bound payloads38; font binaries0.
- SHA256:`5e48631308ff68dc89287463094cb04561735fcd26fea1e3309b558ed555e4d8`.
- Manifest SHA256:`091f2d7a5b605f37be31e0ac822cf2cfeeea275993b367fcd957fa3bb9f86626`.
- [전체 유도·코드·입력·검산·실패·DAG ZIP](https://drive.google.com/file/d/1EQS2Bw7vk1Jg3AoROlJYKLgBKylhiEcS/view?usp=drivesdk).
- Drive ID:`1EQS2Bw7vk1Jg3AoROlJYKLgBKylhiEcS`, parent:`1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`. 실제 업로드와 후속 metadata가 이름·ID·parent·크기2759736을 확인했다.
- Dropbox:`/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_IONIZATION_RESTORE_20261014_SOURCE.zip`, ID:`id:BSpOijBcT10AAAAAAD47MA`. 완료 ACK와 크기2759736을 확인했다.
- Local archive와 nested original ZIP의 CRC,38개 manifest payload를 확인했다. Remote 검증은 R1 ACK/ID/name/size/parent이며 full restore가 아니다. 원본 ZIP·권한·production code를 바꾸지 않았다.

전체 한국어 증명은 ZIP의 `REPORT_KO.md`, 정확한 수치는 `results/RESTORED_CERTIFICATE.json`, 독립 산술 대조는 `results/VALIDATION.json`, 다음 실행은 `HANDOFF.json`과 `NEXT_DAG.json`이다. Git의 본 문서는 실질 정리와 전달 진입점이며 전체 immutable execution payload는 위 ZIP에 있다.

## 1. 물리적 범위와 exact source

동일한 post-G1 셀의 P/S 전자 각각1개, thermal electron1개, 핵13, HI7/HeI3/HII3를 사용한다. 모든 수치는 eV/cell, proper seconds, 실제 V(t)로 나눈 밀도다. H=(2,4,6)e-15/s, V=V0 exp(theta t), theta=sum H, h=100000s. Signature=(-,+,+,+), c와 k_B 및 eV/J 변환을 유지한다. Massive geometry와 원 cold-target/nonrelativistic collision model, monatomic thermal EOS를 구분한다.

Full comparison에는 모든 active donor의 HI/HeI ionization과 downward Coulomb stopping이 남는다. 작은 reference에만 후속 반응을 생략한다. 다른 원자 채널, 외부 주입, recoil, native REI CR-ON은 추가하지 않는다. 이 certificate는 선언한 finite anchored source의 방법 간 오차이며 실제 단면적·quadrature model·측정상수의 물리 불확실성을 포함하지 않는다.

실제 NPZ mass와 이전 MODEL beta/heat의 exact completion에는1e-18수준 차이가 있었다. 원본을 모두 보존하고 이번 reference의 beta=2-sum m_j, q=Ep-B-sum Ej m_j를 실제 mass에서 Fraction으로 재정의했다. 원래 값과 정확한 차이는 결과 JSON에 있다. 허용차를 넓히거나 기존 결과를 소급 재인증하지 않았다.

## 2. Birth-time full-sharing 구성

M=me c^2일 때 생성시각s의 운동에너지w, 물리 방향n에 대해

    W(t,s;w,n)=z/(sqrt(M^2+z)+M),
    z=w(w+2M) sum_i n_i^2 exp[-2 H_i(t-s)].

반드시 생성시각부터 운반한다. 공통 초기 angular label을 쓰면 A=diag(exp(-H_i t)), n(t)=A n0/|A n0|, J=det(A)/|A n0|^3이다. 따라서 매 생성시각에 물리적으로 등방인 source는 초기 label에서는 J_s 가중치를 갖는다.

원 HI15600개와 HeI6812개 sharing samples를 모두 재사용한다. xi_k=w_k0/(Ep0-B), w_k(E)=xi_k(E-B),

    p_k(E) = normalize[p_k0 f_BED(E,w_k(E))/f_BED(Ep0,w_k0)].

이것은 기존 quadrature label을 운반하는 명시적 positive exact-real extension이다. 매 에너지에서 adaptive binary64 generator를 재실행한 것과 동일하다고 주장하지 않는다. Total rate는 이전 anchored BED total-shape ratio다. 두 daughter의 합은 Ep-B이며, 현재 에너지 grid의 양의 인접-node weights로 count와 first energy moment를 보존한다. Prefix23의 thermal/active ownership은 그대로다.

Actual birth source는 integral_0^t G(t,s) P_s[J_s K_a(Ep(s))] rho_a(s) P(s) ds로 정의한다. Reference는 저장된 mass*m_a ionization extent를 co-moving label에 둔다. 둘을 동일시하지 않고, source reweighting·grid displacement·angular Jacobian을 별도 defect로 상계한다.

Positive BED decomposition y(y-a)+r(r-a)>0 및 실제 HI/HeI g 함수를 이용한 전 domain logarithmic-derivative bounds를 유도했다. E in[29.9,30]eV, xi in[0,1/2]에서 SDCS derivative upper는 HI0.537728/eV, HeI0.445957/eV 미만이다. 두-node hats의 L1 Lipschitz bound와 normalized weights derivative를 결합하면

    ||m_a(t)-m_a0||1 <= delta_a0 + C_ma t,
    C_ma=4(vP+vg)/gap_min+4 M_a vP exp(2 M_a vP h)
          +2 S_ang exp(S_ang h).

vP=2H1 Ep0, vg=2Hmax Ep0, S_ang=max|3Hi-theta|. 실제 원 re-projection 차이 delta_a0는 HI8.401e-17, HeI9.024e-17미만이며0으로 버리지 않는다. Energy column defect는2Ep0(delta_a0+C_ma t)로 제한된다.

## 3. 보존 전파자와 전체 온도 certificate

P depth2/S depth3 retained chains에 primary HI/HeI를 복원한다. P의3개 stopping state와2개 ionization absorbing state, S의4개 state를 initial-rate CTMC로 계산한다. Passive daughters에는 exact moving energy lift가 적용되고 이후 모든 생략 반응은 full model과의 defect다.

Energy-coordinate full collision 생성자는 gas를 고정하면 Metzler/zero-column-sum이다. Moving-coordinate dot(R) R^-1 및 bath work를 포함한 D_G는 현재 모든 축의 팽창에서 비양수이므로 선형 전파자 norm은1이하이다. Gas feedback만 별도 L을 필요로 한다.

각 retained lineage count<=1과 born mass<=t sum_a rho_a0 m_ja0를 사용하여

    L=max_P Gamma_j+max_S Gamma_j
      +h sum_j Gamma_j sum_a rho_a0 m_ja0,
    ||error(t)||1 <= B(t)=sum_r C_r t^(r+1) phi_(r+1)(L t),
    phi_m(x)=sum_(k>=0) x^k/(k+m)!.

C_r에는 born donor의 전체 후속 충돌, P1/P2 ionization, P/S terminal stopping, 실제 energy·density·volume·neutral 변화의 frozen-rate defect, moving full-sharing defect와 별도 adiabatic heat-lift defect를 모두 포함한다. Stopping 비용은 항상2Eparent다. Positive series/tail을 outward Decimal65로 평가했다.

Thermal count를 total free count minus active count로 복원하고 동일한 EOS에 투입하여

    |delta T| <= [1/(cv Nmin)+Tref_max/(Nmin Emin)] B,
    Nmin=14

를 얻는다. 동일한100000s에서:

- 총 온도 반경 <5.696978365109e-6 K.
- Reference T=99.61609675244046225... K.
- Full endpoint in[99.61609105546209,99.61610244941884] K (outward display).
- Full path cutoff in[0.17165864555709,0.17168625303868]eV.
- Prefix23 first-exit bootstrap closes; unchanged0.001K budget is met.

온도 반경 주요 항은 S terminal3.27674e-6K, P terminal7.82281e-7K, P1 ionization6.58593e-7K, frozen-rate5.73946e-7K, born collisions3.77910e-7K, moving-sharing2.74395e-8K다. 이전 stopping-only100000s 충분 반경 대비 약216.37배 감소이며, 실측 full-model 오차나 속도개선 배수는 아니다.

## 4. 최신 HE energy quotient를 움직이는 source에 결속

실제로 읽은 HE PR42 commit9617376418b9de61eaaf5ce54a25127f70d337c3의 R6는 total-energy difference Delta가 있으면 |delta Nfree| <= (B+|Delta|)/(2Bmin)을 제공한다. 현재 geometry에서는 Delta=0으로 둘 수 없다.

Conservative source/rate/omission 열은 합계0이므로 새로

    |Delta(t)| <= gmax integral_0^t B(s)ds + C_U t^2/2,
    gmax=max(2Hmax,2theta/3)

를 얻는다. C_U는 reference heat-lift defect다. Current observable은 같은 source/clock/frame에서 직접 계산한다:

    tau_ref = c sigmaT/V0 integral exp(-theta t)[3+xH+xHe]dt,
    R_tau <= c sigmaT/(2V0 BH) [Bint+gmax Bdouble+C_U h^3/6].

Bint=integral B, Bdouble=integral(h-t)B이고 positive phi 지수가 한 단계씩 올라간다. Discounted CTMC integral을 실제 positive uniformization으로 평가했으며, old static center는 가져오지 않았다.

    tau_ref=5.94727990495093831576...e-15,
    R_tau<1.528609867904e-25,
    tau_full in[5.9472799047980773,5.9472799051037994]e-15.

기하 work를 포함한 개선은 일반 energy-only current bound 대비1.99999175배이며 정확히2배가 아니다. Initial-census surplus도[1.2367901235,1.2673623210]e-23>0으로 분리된다. 이것은 matched Thomson supplier result이며 KN/native consumer 실행은 아니다. Nonzero spatial electron current가 있으면 -sigmaT k_a j^a 항을 유지해야 한다.

## 5. 실제 검산, 남은 범위

Wolfram15.0.1:27 scalar literal-zero residuals,2 helium domain inequalities True. 실제 xTensor1.3.0:6 tensor literal-zero residuals. 공식 package hashes를 대조했다. 별도 Fraction/mpmath85/SciPy:135checks passed; helper unittest4passed. 두 작은 reference ODE의98/122calls 결과는99.61609675244047/99.61609675244046K이며 이를 full moving-source trajectory로 부르지 않는다.

First completion mismatch와 NumPy longdouble serialization failure를 보존했고, 새 reference 정의 및 serializer를 수정한 뒤 새 검사 명령을 통과했다. Stub NotImplemented 오류는 strict assertion-based TDD의 RED로 표시하지 않는다. 실제 submitted Wolfram inputs와 selected normalized observed outputs는 원본 묶음에 있다. Same-author separate CAS/arithmetic이며 external independent review는 없다.

SciSpace와 Exa에서 Le-Cambier2017(arXiv1711.05946), Taitano et al2019(arXiv1903.05467)의 보존형 plasma kinetics/moving-coordinate inertial terms를 비교했다. 이 문헌이 본 source-specific certificate를 증명한다는 주장은 하지 않는다. 일반 정리의 최초성도 주장하지 않는다.

WU088_HH PR58 head0fad7e43b5131440ee15863e4295341c42c78f80의 최신 결과를 읽었으나 HH rate는 본 source에 수입하지 않았다. REI PR114 heada5c958c414dea41216b445c05f58df837f05cacb의 warm FT03 CaseA CR/RCT/HH OFF를 보존했다. 기존 F/G/atomic/b-grid/globalREI 상태와 선택하지 않은 두 DAG node는 그대로다.

다음은 기존 ready node `NT_ACTUAL_PREFIX_EVENT`: 실제 transversal crossing, post-reset thermal consistency, event-time/saltation contribution. 완료한 no-event certificate를 반복하지 않는다. 전체 cascade,9600-generator, cosmological history,HPC,외부심사,main merge는 이번에 수행하지 않았다.
