# 独立 R6: 질량 의존 EI 에너지 교환 계약

## 판정

**PASS_SCOPED_THEORY_CONTRACT. Blocking finding 0.**

검토 대상은 FROZEN_CONTRACT.md 14613 bytes, SHA256
bfc66b2b84d909813e0c5ef9a2caceea346d494a8e83b0bada43421c9d1f8a39 이다.
이번 검토자는 후보 intake의 이론 구성에 참여했으며 production 구현을 작성하지 않았다.
따라서 독립성은 root/implementation의 식을 그대로 가정하지 않고 Rutherford leading-log velocity moments에서 재유도한 방법 및 production 비참여에 있다.
새로운 완전 독립 referee가 원전 신규성을 확인했다는 뜻은 아니다.

현재 수치 primary/test는 미실행이다. 이 R6 PASS는 coefficient/경계/보존/검증 계약의 이론 상태다.
실제 구현과 raw numerical 결과는 C6–C9의 별도 근거가 필요하다.

## 1. Rutherford leading-log에서 계수 normalization

질량 m의 전자가 질량 M의 이온과 상대속도 u로 충돌한다고 두자.
κ=Z e²/(4πepsilon0), reduced mass μ=mM/(m+M).
작은 angle χ에서 χ≈2κ/(μu²b)이고, 전자의 상대velocity 변화는 reduced-mass 비율 μ/m를 가진다.
impact parameter annulus의 event measure는 n u 2πb db이다.

leading logarithm L=integral_(bmin)^bmax db/b를 고정하면, 상대속도 방향의 평균 velocity change는

    <Δv_parallel>/dt
      = integral n u 2πb db [−(μ/m)u χ²/2]
      = −4πnκ²L/(m μu²).

수직 두 방향 중 하나의 variance는 azimuth average1/2를 포함해

    <(Δv_perp,one)²>/dt
      = integral n u 2πb db [(μ/m)²u²χ²/2]
      = 4πnκ²L/(m²u).

따라서 gamma=4πκ²L/m²를 정의하면 arbitrary background에서

    mean(dv)/dt = gamma(1+m/M) grad H,
    Cov(dv)/dt = gamma Hess g,

H=integral f_b(v')/|v−v'| d³v', g=integral f_b(v')|v−v'| d³v'.
longitudinal velocity variance의 non-log higher-order 부분은 선택된 leading-log 모형의 범위 밖이다.
이 유도는 원 Rosenbluth1957 식의 OCR에서 읽은 mass factor를 가정하지 않고 normalization을 확인한다.

## 2. Maxwell background의 H, g'' 및 trace를 분리 확인

s²=2epsilon_eV theta_b/M, x=v²/s², A(x)=erf(sqrt(x))−2sqrt(x)e^(−x)/sqrt(pi).
정규화된 isotropic Maxwell background의 구면 shell 적분은

    H(v)=n erf(v/s)/v,
    H'(v)=−n A(x)/v²

를 준다. g는 ∇²g=2H를 만족하므로 regularity v²g'(v)→0 at v→0에서

    g'(v)=n[(1−s²/(2v²))erf(v/s)
             +s exp(−v²/s²)/(sqrt(pi)v)],
    g''(v)=n s² A(x)/v³,
    g''+2g'/v=2n erf(v/s)/v

이다. g''와 trace는 별개로 유지했다. 이 단계가 diffusion energy 변환에서 누락되기 쉬운 perpendicular contribution을 고정한다.

## 3. 에너지 좌표 변환과 부호/단위

E=m v²/(2epsilon_eV), r=M/m, b=gamma n m/(epsilon_eV v).
Itô 평균은

    mu = gamma m/epsilon_eV [
            v(1+1/r)H'(v) + (g''+2g'/v)/2 ]
       = b[erf(sqrt(x))−(1+1/r)A(x)]
       = b[A'(x)−A(x)/r].

quadratic variation에서

    2D = gamma m²v² g''/epsilon_eV²,
    D = theta_b b A(x)/r.

따라서 계약의 두 계수와 Var(dE)=2Ddt convention은 정확히 맞다.
b와mu의 단위 eV/s, D의 단위 eV²/s다.
고정L에서 b=C/sqrt(E)이므로

    D' + D(1/(2E)−1/theta_b)=mu

가 직접 성립한다.
같은T의 모든 종에서 p_theta(E)∝sqrt(E)exp(−E/theta)가 zero-current stationary density이고, 양의 D를 더해 같은 pi/conductance 구조를 사용할 수 있다.

r=1은 PR59 equal-mass 계수로 환원한다.
고정E,T에서 r→infinity일 때 mu,D→0이며 angle diffusion은 다른 양이다.
현재 출력의 finite event hazard=null 구분은 적절하다.
저에너지에서는 A'(x) heating이 남으므로 모든 이온을 일괄 cold-ion loss로 치환하면 계약과 달라진다.

He4+ mass=alpha mass+electron의 관성 근사와 Ti=Te, same prescribedlog, pointnetcharge closure는 계약에 명시돼 있다.
이는 binding energy 장부를 수정하거나 full atomic isotope mapping을 승인하지 않는다.

## 4. Maxwell 평균식의 별도 적분

theta_t>0인 normalized Maxwell test density를 곱하면
p_t(E)b(E)=2C exp(−E/theta_t)/(sqrt(pi)theta_t^(3/2)).
a=1/theta_t, s=r/theta_b라 두자.

    I1 = integral_0^infinity exp(−aE) A'(sE)dE
       = sqrt(s)/(a+s)^(3/2),
    I2 = integral_0^infinity exp(−aE) A(sE)dE
       = (s/a) I1.

첫 식은 gamma(3/2) 적분, 두 번째는 부분적분이며 A(0)=0와 exponential decay가 endpoint terms를 없앤다.
그러므로

    <mu> = 2C/(sqrt(pi)theta_t^(3/2)) (I1−I2/r)
         = 2C(theta_b−theta_t) /
           [sqrt(pi) r (theta_t+theta_b/r)^(3/2)].

계약식과 일치한다. theta_t=theta_b에서0, colder test population에서양수, hotter test population에서음수다.
평균식은 조건부 thermal test identity로 사용하고 새 physical rate database라고 세지 않는 범위도 적절하다.

## 5. Same-grid generator와 no-CE MFPT 비교

저장된 pi_i>0와 c_ee,k>0를 읽고 c_b,k=c_ee,k D_b(E_mid)/D_ee(E_mid)로 구성한다.
동일E,T,geometry이므로 각 Q_b의 off-diagonal은 nonnegative이고 columnsum0이며 detailedbalance가 유지된다.
q를 state0에 놓고 transient block을 취할 때 q로의 loss를 diagonal에서 빼지 않는 계약이 맞다.

no-CE backward G T=−1을 pi_i로 곱하면
J_i−J_(i−1)=−pi_i, J_k=c_k(T_(k+1)−T_k).
reflectingtop의 J_m=0에서 J_k=sum_(j=k+1)^m pi_j.
T_0=0를 쓰면 계약의 positive conductance formula를 얻는다.

sameT와 E_mid≥q=chi theta에서
A(r_b E_mid/theta)≤1, A(E_mid/theta)≥A(chi)>0이므로
0≤c_EI/c_ee≤delta_max.
각 positive summand에 reciprocal bound를 적용하면
T_ee/(1+delta_max)≤T_total≤T_ee.
pi normalization상수는 tailmass/c에서 상쇄된다.
원 active source 가중 평균에서도 양의 weight로 유지된다.
계약은 이 결과를 CE 확률 단조성으로 전용하지 않아 적절하다.

## 6. Mark/entry stopping과 에너지 reward

E_t=E_full[1:], a=q absorption-rate vector라 하자.
d_b=(Q_b^T E_full)_transient이고 d_total=sum_b d_b이면

    d_total = G E_t + a q,
    K E_t = h E_t − d_total + a q.

따라서 K H_b=−d_b,
K u_entry=a,
K(r_s+r_p)=hE_t 를 더하면

    sum_b H_b + q u_entry + r_s+r_p = E_t.

CE postevent terminal kinetic을 r_s+r_p−Delta P_CE로 쓰면
atomic internal Delta P_CE를 더하는 계약과 동일하다.
q를 포함한 full energy vector를 써야 q-boundary jump의 kinetic loss가 bath reward에 정확히 들어간다.
q이동에 별도 stopping heat를 더하면 이중계상이므로 금지한 계약은 맞다.

원 active atoms가 q에 투영된 질량의 terminal kinetic은 p_q q이며,
원 W<=q inactive atoms는 자기 원래W에서 진단을 끝내므로 originalinactive kinetic을 더한다.
이 둘을 구별한 계약은 원 source count/energy projection과 일치한다.
각 종의 signed reward는 부호를 자르지 않고 비교해야 한다.

Planned12RHS는2channelprobability+1entry+1stoptime+2eventenergy+2eventtime+4bathreward로 일치한다.
8cases와96primaryRHS계획도 맞다.
기존 no-CE conductance식 평가에는 추가 linear RHS가 필요 없다.

## 7. 확인한 입력 표현과 남은 검증

PR102 finest NPZ를 읽어 key/shape만 확인했다.
2480fullnodes,2479transientnodes; 저장E/pi/conductance/Q/G/hazards/oldsolutions와3fullsourcevectors,3개384atom active masks가 존재한다.
원 C23D CSV header에는 saved EE drift와diffusion이 실제로 존재한다.
어떠한 기존 numerical solver/ODE/science campaign도 실행하지 않았다.

수치 수용 기준은 현재 조건부 유한chain 판정에 맞다.
특히 작은 EI-induced CE difference에 독립 기준을 둔 점과 signed near-zero값을 noncancelling scale로 확인하도록 한 점을 C9에서 그대로 적용해야 한다.
수치 grid 비교 실패가 나면 그 raw와기준을 유지하며 원인을 진단한다.

Original PDF webopen은 INTERNAL_ERROR, root의 sandbox directdownload는 permission error였다는 실제 receipt를 수신했다.
원 PDF image를 봤다고 주장하지 않는다.
정규화 문제는 위 Rutherfordmoment→uncancelledItô 유도로 해결했으며, APS 서지와 Exa 원문text는 배경 provenance다.

## 네 축 상태

EXECUTION: R6 analytic review completed; new numerical execution0.
PUBLICATION: local create-only receipt; parent publicationpending.
BACKUP: parent checkpointpending; inherited PR102 verifiedbackupsunchanged.
DAG: scoped EI child theorycontractPASS; fullN4/N5PARTIAL/OPEN; N6/N7predecessorgated.
global_error_bound=null; global_completion_percent=null.

