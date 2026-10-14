# BASS_CR: 실제 thermal-prefix 사건과 사건시각 오차

2026-10-14, 선택 노드 `NT_ACTUAL_PREFIX_EVENT`, R5 구성적 유도와 단계 내 검산. 실제 PR53 head `cc3249947a1fc93f2bacf2190604371dfde2f42f`의 HANDOFF/DAG를 읽고 수행했다. 외부 독립 과학 심사와 native subagents는 NOT_RUN이다.

## 전체 원본과 실제 이중 백업

- Archive: `BASS_CR_PREFIX_EVENT_20261014_SOURCE.zip`,3034250bytes,61members/60manifest payloads, font binaries0 (nested archives 포함).
- SHA256:`543c976bd748a1896e44c0b6e2852a2c793f5342cfec9e99546b32871140124b`.
- Manifest SHA256:`8dca76d4c8bb5ba90aaad2551faafc5892a26e84628ac4a9879b7fc322bce370`.
- [전체 한국어 증명·코드·입력·검산·실패·DAG ZIP](https://drive.google.com/file/d/1Q0yul9U4DVBa50fp_NiNOuvAkbYdX7xR/view?usp=drivesdk).
- Drive ID:`1Q0yul9U4DVBa50fp_NiNOuvAkbYdX7xR`, parent:`1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`. Upload success와 후속 metadata의 ID/name/parent/3034250bytes가 일치했다.
- Dropbox:`/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_PREFIX_EVENT_20261014_SOURCE.zip`, ID:`id:BSpOijBcT10AAAAAAD47OA`, completed ACK/name/size3034250.
- Local CRC,60payload hashes, nested immutable original CRC와 font absence를 확인했다. Remote 검증은 R1 ACK/ID/name/size/parent이지 원격 전체 restore가 아니다. 기존 파일·권한·production code는 바꾸지 않았다.

ZIP의 `REPORT_KO.md`가 전체 증명이다. `CONTRACT.json`, `CLAIMS.json`, `results/PREFIX_CERTIFICATE.json`, `results/EVENT_SENSITIVITY.json`, `results/INDEPENDENT_MP.json`, `NEXT_DAG.json`을 함께 읽는다. Git에는 본 실질 결과/증명 진입점, 전체 실행 payload는 위 immutable ZIP에 있다.

## 정확한 모형 범위

**새로 선언한 두-간선 finite witness이며 이전 full HI/HeI trajectory의 연장이 아니다.** 원 grid, anchored Coulomb alpha/L0, U0, V0, cv와 H=(2,4,6)e-15/s를 재사용한다. 핵13,thermal electron1,총free electron3,HI7/HeI3/HII3. Active spectrum만 high399/200 at grid288, low1/200 at grid23으로 바꾼다. High edge288->287의 daughter287은 추가 collision을 하지 않고 기하 운반만 한다. Low23->22는 기존 b/(E23-E22) hazard를 쓰며 node22가 thermal-owned이므로 사건 heat는 전체E23이다. 모든 에너지는 HI threshold 아래이고 원 ionization rate0을 직접 확인했다.

높은 pair는 z축, 낮은 pair는 x축의 antipodal population으로 spatial current0이다. Signature=(-,+,+,+), 시간proper seconds, 에너지eV/cell, 밀도는physical volume으로 나눈다. cv=3kB/(2epsilon_eV), theta=sum H, ag=2theta/3, V=V0 exp(theta t). Source exact rationals/원배열 identity는 CASE.json에 있다. 원 binary64 입력을 exact-real 계수로 선언하며 물리적 원자율/상수 불확실성은 별도다.

각 축의 에너지는 E=z/[sqrt(M^2+z)+M], z=E0(E0+2M)exp(-2Hi t), M=me c^2이고 E'=-ri E, ri=Hi(E+2M)/(E+M)이다.

## 사건과 reset의 구성

상태 y=(d,a,U), Nth=1+a0-a, B=13+Nth=14+a0-a, T=U/(cv B). Rates는 실제 source로부터

    lambda_j = alpha_j sqrt(Ej0/Ej) n [L0_j+1.5log(Ej/Ej0)-0.5log(n/nref)]/(Ej-Etarget), n=Nth/V.

따라서 사건 이후 thermal electron 수가 바뀌면 high rate도 바뀐다. Pre-flow는

    d'=-lambda_D d,
    a'=-lambda_A a,
    U'=-ag U+(ED-EB)lambda_D d+EA lambda_A a.

Guard는 g=EA-eta U/B, eta=40/3 (cutoff20kBT). 첫 descending g=0에서 d+=d-, a+=0, U+=U-+EA a-, Nth+=Nth-+a-이다. Post-flow는 a=0, Nth=1+a0 및 같은 high edge를 쓴다.

Guard 위에서 U-=EA B-/eta이므로 직접

    T+/T-=1+(eta-1)a-/(B-+a-),
    Ec+-EA=EA(eta-1)a-/(B-+a-)

를 얻는다. eta>1이면 편입한 atom은 thermal-consistent지만, Ec+<E24도 검사해야 단일 사건이다. B-=14,a-=1/20이면 Ec+/EA=880/843으로 실제 next-node ratio를 넘는 음성 대조군이다. 에너지 보존만으로 다음 branch가 자동으로 맞는다고 하지 않는다.

## 실제 root와 전 구간 포함

    g'=-rA EA+eta ag U/B-eta(ED-EB)lambda_D d/B
       -eta lambda_A a(EA B-U)/B^2.

Density/rate의 전 구간 box, d>=d0 exp(-lambda_D^+ t), U<=U0+(ED0-EB0)d0+EA0 a0, EA B-U>0을 사용한다. 같은 축의 gap은 mean-value theorem으로 gap0 exp(-2Hi t)<=gap(t)<=gap0이다. Coulomb logs>1/2, positive rate, T'>0을 직접 닫고 전체0..6500000s에서 -g'>2.67632039207147e-10eV/s를 얻는다.

실제 integration은 directed Decimal65 Taylor6, stepwise strict Picard tubes 및 tube 전체의 order7 derivative remainder다. Refinement 차이를 error bound로 쓰지 않는다. 양끝 guard 부호와 위 transversality에서 유일한 첫 event:

    t* in[6035789.4019193793,6035789.4019193851]s,
    a-=0.001893541014206046...,
    T- in[101.10436169302695,101.10436169302696]K,
    T+ in[101.27295563463095,101.27295563463096]K,
    jump in[0.1685939416040007,0.1685939416040040]K,
    Ec+-E23>0.00029056603615606eV,
    E24-Ec+>0.00280318388915107eV,
    T(6500000s) in[101.34676866393188,101.34676866393190]K.

Post5step의 전체 tube에서 양쪽 prefix margin이 양수다. 이 좁은 숫자는 exact-real 모형의 계산 포함이며 물리적 사건시각을 ns 정확도로 안다는 뜻이 아니다.

## 실제 saltation: 보존 subspace에서도 증폭

에너지 X=(KD,KB,KA,U)에서 fixed-time reset은 R(X)=(KD,KB,0,U+KA)이다. R>=0,1^T R=1^T,||R||1=1. 이 chart에서 Rt=0이며 count chart의 time-dependent heat reset과 혼동하지 않는다.

Perturbed guard의 root shift delta t=-gx delta X/(gt+gx f-)와 pre/reset/post 동기화를 직접 미분하면 표준 saltation

    S=DR+(f+-DR f--Rt) outer gx/(gt+gx f-)

를 얻는다. 이 일반 공식의 novelty를 주장하지 않는다. 현재 b=f+-Rf-는

    b=(-deltaLambda KD, (EB/ED)deltaLambda KD, 0,
       (1-EB/ED)deltaLambda KD+(rA-ag)KA).

여기서 deltaLambda=lambda_D(n+)-lambda_D(n-)>0은 thermal-density jump이고 1^T b=(rA-ag)KA는 바뀐 stress의 geometry work다. 고정시각 energy conservation은 서로 다른 모드에 머문 시간의 work까지 같다는 뜻이 아니다.

실제 interval:

    ||S||1 in[2.02089789724012428,2.02089789724186176].

v=(1,0,0,-1)은 1^T v=0이지만

    ||Sv||1/||v||1 in[1.50373838433032189,1.50373838433120205].

따라서 fixed reset norm1만으로 이 사건의 비증폭을 주장할 수 없다. 특정 local synchronized direction의 결과이며 장기 instability나 전체 방법에 대한 no-go가 아니다. 별도60-digit event finite difference는 S에 대한 차이가5.38e-8,5.38e-9,5.38e-10으로 감소하고 R-only 오차는0.503738386에 남는다.

## 유한오차와 현재 HE clock 재사용

같은 첫 event sequence의 pre-state error epsilon, guard error epsilon_g, Lipschitz Lg, speed floor nu에서 |delta t*|<=(Lg epsilon+epsilon_g)/nu다. 공통 final time의 H(s)=Phi+(Tf,s,R(s,x-(s)))를 실제 사건시각 간격에 적분하면 G+[LR epsilon+BR|delta t|+epsilon_R]+post residual bound가 된다. Saltation의 first-order 수치를 유한 bound로 대신하지 않는다.

현재 초기T0만 +/-1microK인 family는 pre-count/rate가U와 무관하여 deltaU(t)=deltaU0 exp(-ag t)이다. 두 reset 이후 Nth=1+a0이 같고 post-energy flow가 비증폭이므로

    |delta t*|<6.439687331662s,
    ||deltaX(Tf)||1<=|deltaU0|+BR |delta t*|,
    |deltaT(6500000s)|<2.309527681775e-6K.

실제 perturbed roots의 변화는 약+5.299896/-5.299893s이고, 별도 계산의 final T 차이는-1.00117724944e-6/+1.00117725005e-6K다. **두 경로 모두 reset을 지난 공통 final time의 비교다. 한쪽만 reset한 중간 window의 순간 temperature 차이가 초기섭동에 비례해 작다는 주장은 하지 않는다.**

총free count는항상3이다. Nth jump와 active-count jump가 상쇄되므로 total electron current와 Thomson opacity에 impulse가 없다. Thermal-only census는 가짜 jump를 만든다. Stress work 차이(rA-ag)KA는 실제 xAct contraction으로 확인했다. Same-clock tau(6500000s)=3c sigmaT/V0*(1-exp(-theta Tf))/theta=3.86573178163551218e-13...이며 사건시각에 무관하다.

최신 HE42 head a4874b6483e66c310b76d645b2326f3b71721b49의 실제 R7_RESULT를 읽었다. Material age q=c gradTheta에서 A=q.k와 D=-u.k는 다르고 optical weight는D/A다. Event source age를 ray parameter로 바꾸는 factor는1/A이며 동일한 양의 time reparametrization은 S를 바꾸지 않는다. HE의 다른 물리적 age field와 fixed-volume interval을 본 모형에 그대로 넣지 않았다. HH59 head200bcc3e8c815d3426b850c6adc1f9b583d84049의 tight-rate 새 결과를 읽되 HH coefficients는 수입하지 않았다. REI114 heada5c958c414dea41216b445c05f58df837f05cacb의 FT03 CaseA CR/RCT/HH OFF를 보존했다.

## 검증과 남은 작업

Actual Wolfram15.0.1:25scalar literalzeros와 zero-mass limit0. Actual xTensor1.3.0:7tensor literalzeros, official3package hashes matched. 별도 mpmath60 Gauss4 collocation100000/50000s step의 root/finalT가 interval에 포함된다. Final93checks와7unit cases가 통과했고 일부 검사수는 중복된다. 실제 R-only candidate의 assertion RED/같은 test GREEN을 보존했다.

최초 interval run의60s host timeout 뒤40step/4e6s의 certified endpoint를 복구했다. 첫40개 상세 trace는 없고 endpoint는 보존되어 있으며 이후21pre/5post step 상세 trace가 있다. 전 구간 analytic envelope와 별도 처음부터의 numerical integration을 추가 확인했다. 최초 final checker의 누락된 Rt 인자, Wolfram formal undefined-symbol warning, 느슨한 interval mismatch와 그 대수적 개선을 보존했다. 허용차 변경이나 upstream science replay는 없다.

SciSpace와 Exa에서 Kong et al2024 arXiv2306.06862v3/doi10.1109/JPROC.2024.3440211의 primary text와 Burden et al arXiv1811.03956v2 abstract를 비교했다. 표준 hybrid 이론과 이 source-specific 직접 유도를 구분한다. 전체 cascade/HPC/production/native receiver/external review/main merge는 수행하지 않았다.

빠른 재현: python -m unittest discover -s checks -p 'test_*.py'; python checks/verify_result.py. 새 사본의 전체 재현: python src/run_certificate.py --fresh; python src/event_analysis.py; python checks/independent_mp.py; python checks/verify_result.py. --fresh는 실행 뒤 추가한 interface이며 원 실행driver는review에 보존한다.

다음 ready node는 `NT_PREFIX_EVENT_FULL_SOURCE_BINDING`: 기존 actual HI/HeI full-sharing와 corrected2Eparent donor residual을 event-producing scenario에 연결하고 finite tube, 필요한 reset batch, post-event error를 계산한다. 본 two-edge 수치나 이전 no-event bound를 새 source에 그대로 옮기지 않는다. 선택하지 않은 DAG node와 기존 F/G/atomic/b-grid/globalREI 상태는 그대로다.
