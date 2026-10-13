# BASS_CR branch–geometry 후보 독립 심사

연구 단위: CR-THEORY-BRANCH-GEOMETRY-20261013  
판정: **PROMOTE_SCOPED / PASS — BG1–BG7**  
심사자: /root/feedback_literature_review  
기준: physmath-research-loop 1.0.0, theory loop 및 evidence-reuse 정책

## 1. 판정과 독립성

실제 두 사건의 고정 branch 자기일관적 endpoint, 반응으로 변하는 원자 inventory의 유한 branch 선택, 지정된 massive Bianchi 기하에서의 에너지 수송, 이동 후 실제 HI/HeI kernel 재결속, 보존적 에너지 표현의 조건부 오차 상계를 명시된 범위에서 수용한다. 열린 과학 차단 사유는 없다. 아래 판정은 현재 동결된 수식·구현·입력·실행 원출력에 붙는다.

심사자는 외부 원전 조사 및 이 독립 심사 문서를 작성했다. 후보의 핵심 유도, reference solver, 검산 설계, 실제 Wolfram/xAct 실행의 저자가 아니다. 후보 수식과 코드, 원 source, 저장된 수치·기호 원출력을 직접 읽고 적용 조건·부호·단위·branch·오차 의미를 확인했다. 이 독립 심사 단계의 scientific execution은 **0회**다. Hash 비교, JSON field 대조, DAG 경로와 위상 순서 확인은 읽기 전용 기록 검토다.

심사 기준은 직전 KC1–KC7의 수용 상태다. 직전 branch HEAD는 c450b00108dc05885a25d0d9c042cdcfe41bd659, 직전 science commit은 a5c29ad4070acb931d92d2bec42a927a57f479ca다. 복사된 기존 보존 정리·kernel·grid·cutoff 근거의 identity를 재사용했으며, 이전 과학 suite나 완료된 원 실험을 반복하지 않았다.

| Claim | 수용한 결과 | 주요 근거 | 범위의 끝 |
|---|---|---|---|
| BG1 | 실제 HI sharing 기여와 실제 stopping 사건을 결합한 고정 branch map의 self-map, 수축, 유일한 endpoint | COUPLED_BRANCH_KO.md, 입력·solver·COUPLED_BRANCH_CHECKS.json | 지정된 두 사건과 \(D=[0,1/20]\times[0,1]\); 전체 sharing family의 결합 해를 뜻하지 않음 |
| BG2 | 엄밀한 log enclosure와 residual로 얻은 유한 모델의 extent·온도·cutoff 오차 certificate | CB 유도, exact 구현·원출력, 일반 기호식 Wolfram 결과 | 유한 source 상수를 정확한 실수로 해석한 endpoint 오차; 물리 모형·시간 적분·FP64 전체 오차는 별도 |
| BG3 | 반응으로 가중치가 변하는 원자 inventory에서 inherited prefix를 유한 횟수에 repair | REACTION_BRANCH_KO.md RB.1–9, continuation 구현 | 유한 ordered support, 양의 base count/energy, \(\chi\ge3/2\), equality thermal |
| BG4 | 실제 source의 생성 daughter가 cutoff를 통과하는 보존적 구성, 두 roots와 inherited 선택의 명시 | RB.10–18, REACTION_BRANCH_CHECKS.json | 별도의 \(\chi=4\) 구성; 실제 시간 이력이나 ODE 해의 물리적 온도 불연속으로 채택하지 않음 |
| BG5 | observer convention에 맞는 massive 에너지 법칙, 지정된 Bianchi I momentum map과 geometry work | COVARIANT_GEOMETRY_KO.md BG.1–14, xAct·scalar raw, geometry 실행 | 지정된 배경과 raw angular packets; Einstein 방정식이나 bath 기하 closure는 포함하지 않음 |
| BG6 | 이동한 parent의 실제 에너지에서 HI/HeI total rate와 sharing 배열을 새로 평가한 사건 열 | GEOMETRY_REBIND_KO.md, rebind 구현·witness·원출력 | named packet과 실제 source 지원 범위; daughter angular closure와 full nonlinear collision step은 후속 작업 |
| BG7 | count·kinetic first moment 보존, cell별 Lipschitz/\(C^2\) weak error, HeI total coefficient의 적용 가능한 미분 상계 | GR 유도, rational bound 구현·원출력, scalar barycentric 항등식 | 부드러운 cell별 관측량과 명시된 source 모델; cutoff indicator·massive momentum·stress에는 자동 확장하지 않음 |

## 2. 실제 원전과 후보의 관계

사용자가 지정한 SciSpace와 Exa를 모두 사용했다. 심사자 원전 조사에는 SciSpace 자연어 검색 2건, Exa 검색 3건 및 본문 조회 3건의 실제 raw envelope가 있다. 새로 절을 읽은 primary paper는 4개다. 원전에서 가져온 정의·정리와 이번 후보에서 직접 구성한 결과를 구별했다.

| 원전 | 읽은 범위와 가져온 맥락 | 이번 후보에 자동 적용하지 않은 내용 |
|---|---|---|
| Liu–Wang–Wang, 2024, [arXiv:2402.03731](https://arxiv.org/pdf/2402.03731) | §§1–3의 reaction trajectory, detailed-balance free energy, 특정 비선형 이산식의 존재·유일성 조건 | strictly positive initial concentration, reversible mass action, detailed balance와 rank 조건을 요구하는 정리를 zero-support·sharp cutoff branch에 이식하지 않음 |
| Torlo–Öffner–Ranocha, 2022, [저자 PDF](https://davidetorlo.it/files/publications/Torlo2021StabilityPatankar.pdf) | PDS 정의, 정상상태 보존, monotonicity와 영농도 극한 정확도를 구별하는 §§1–5의 해당 절 | 특정 Patankar 반례를 이 공통 capacity map의 반례로 간주하지 않음; positivity만으로 정확도를 결론 내리지 않음 |
| Rendall, 1995 preprint, [gr-qc/9505017](https://export.arxiv.org/pdf/gr-qc/9505017v1.pdf) | §2 식 (2.1)–(2.9)의 Bianchi I 공변 운동량, 분포와 stress 적분 | 원문의 정칙 분포·Einstein–Vlasov 가정이나 이후 singularity 정리를 finite atom remap에 이식하지 않음 |
| Filbet–Sonnendrücker–Bertrand, 2001, [저자 PDF](https://www.math.univ-toulouse.fr/~ffilbet/Papers/paper03.pdf) | §2 식 (7)–(18), ENO 구분, Propositions 2.2–2.3, 결론의 보존적 characteristic remap과 양의 재구성 | 그 수치법의 positivity 또는 cell conservation을 arbitrary massive energy·momentum·stress의 동시 exactness로 확대하지 않음 |

원문의 절·추출 한계·적용 여부와 원 URL은 derivations/LITERATURE_KO.md 및 SOURCES.json에 기록되어 있다. 넓은 분야 전체를 조사했다거나 전역 신규성을 확인했다고 주장하지 않는다. root가 직접 열어 본 primary pages와 별도의 Wolfram context 응답은 보조 retrieval 기록이며, 그 안의 관련 없는 검색 snippet을 과학적 근거로 채택하지 않았다.

## 3. BG1–BG2: 실제 coupled endpoint

### 3.1 사건과 장부의 결속

HI 사건은 저장된 9600-grid의 \(j=4762\), \(W_p=30.00976971818039\) eV 및 실제 sharing index 38을 사용한다. 선택한 sharing 기여의 원 확률과 rate coefficient를 유지했다. 선택된 점을 확률 1인 전체 ionization family로 바꾸지 않았다. Stopping 사건은 다른 parent \(j=290\), \(W=1.00028125\) eV에서 \(j=289\)로 이동하며 실제 source energy gap을 열 장부에 더한다.

두 parent donor가 서로 다르므로 이 구성에서는 각각의 공통 capacity 분모를 명시적으로 전개할 수 있다. Ionization extent \(x\)는 HI를 감소시키고 HII를 증가시키며 한 free electron을 만든다. Slow daughter의 lower part와 retained raw \(A:0\)를 thermal state에 정확히 한 번 포함한다. Stopping extent \(s\)의 \(\delta W\,s\)는 thermal energy로 들어간다. 화학 binding energy, raw kinetic energy, thermal base를 중복 계상하지 않는다.

검토한 thermal closure는

\[
 N_{\rm th}=N_0+x,\qquad n_{e,\rm th}=(n_0+x)/V,
\]
\[
 U_{\rm th}=c_vN_0T_0+\epsilon_{\rm eV}(w_{\rm slow}x+\delta W\,s),
 \qquad T(x,s)=\frac{U_{\rm th}}{c_v(N_0+x)},\quad c_v=\tfrac32 k_B .
\]

여기서 \(N\)은 cell count이며 \(n\)은 밀도다. 실행의 \(V=1\,{\rm m}^3\)에서 숫자가 같다는 이유로 두 양의 단위를 동일시하지 않았다. Thermal EOS에는 nuclei와 thermal electron이 들어가지만 Coulomb screening rate에는 thermal electron density만 들어간다.

### 3.2 Self-map과 수축

\[
 \Phi_I(x)=\frac{a(X_0-x)}{1+b\,a(X_0-x)},\qquad
 \Phi_S(x)=\frac{h\lambda(n_0+x)}{1+h\lambda(n_0+x)},
\]
\[
 a=h\kappa_I/V,\quad b=1+1/X_0,\qquad
 \lambda(n)=A_S n\left[L_0-\tfrac12\log(n/n_0)\right].
\]

코드는 source의 유한 \(A_S,L_0\)를 정확한 binary rational로 고정한다. 이 cold-target source는 여기서 새 온도 의존 atomic rate를 만들어 사용하지 않는다. \(x\)가 thermal electron density를 바꾸어 stopping rate를 바꾸는 실제 피드백과 EOS에서 얻는 \(T\)를 계산한다.

명시된 \(D=[0,0.05]\times[0,1]\), 가중 norm
\(\|(\Delta x,\Delta s)\|_*=\max(20|\Delta x|,|\Delta s|)\)에서 ion image가 D 내부에 있고 \(\lambda>0\)여서 \(0<\Phi_S<1\)이다. 실제 domain 전체의 Coulomb logarithm 하한은 약 29.3951로 양수다. \(\lambda'\), \(\lambda''\), \(\Phi_I'\), \(\Phi_S'\)와 가중 norm 변환을 직접 확인했다.

\[
 q_I=0.0003046579321861247,\qquad
 q_{S,*}=2.9138861430824442\times10^{-9},
 \qquad q<\bar q=0.00031 .
\]

온도 단조 미분과 domain bound로 모든 trial의 cutoff가 동일한 grid 간격 안에 머무는 것이 보인다. 안전한 소수 경계로

\[
 0.1723466652429\le E_c\le0.1729952378230\ {\rm eV}
\]

이며 아래·위 grid 경계와의 엄밀한 양의 여유가 저장되어 있다. 따라서 같은 prefix로 얻은 map을 domain 전체에서 사용한 논리적 순환이 없다. 이 self-map과 \(q<1\)로 D 안의 고정점 존재·유일성을 수용한다.

### 3.3 오차 certificate

Ion fixed-point polynomial의 작은 root 식과 discriminant 전개는 올바르다. 코드의 정확한 scalar update 및 decimal rational 후보는 source의 부동소수 결과 자체를 임의의 exact root로 선언하지 않는다. \(\log(1+x/n_0)\)는 \(t=x/(2n_0+x)\)로 바꾸고, 8항 양의 급수와 기하 tail로 위아래에서 감싼다. Log interval에서 stopping map으로 가는 부등식 방향과 residual norm의 scaling을 확인했다.

저장된 후보는

\[
 \hat x\simeq0.04417772517583427,\qquad
 \hat s\simeq0.9999999126593523,\qquad
 \hat T\simeq100.35047955672445\ {\rm K}.
\]

가중 residual 상계 \(2.1528949384235443\times10^{-25}\)에서
\(\|\hat z-z_*\|_*\le\|\hat z-\Phi(\hat z)\|_* /(1-\bar q)\)를 적용한다. Domain 전체의 \(T\) Lipschitz 상계를 곱한 결과는 다음과 같다.

| 오차 | 유한 모델에서의 저장 상계 |
|---|---:|
| 가중 fixed-point radius | \(2.1535625428118157\times10^{-25}\) |
| ionization extent | \(1.076781271405908\times10^{-26}\) |
| \(T\) | \(8.106869987934281\times10^{-26}\) K |
| \(E_c\) | \(1.397192007978251\times10^{-28}\) eV |

온도 상계에는 \(x\) 방향의 norm weight 0.05가 들어가며 stopping 방향은 단위 weight다. 이 certificate는 JSON에 저장된 exact rational 후보에 붙으며, 위에 반올림해 인쇄한 소수를 정확한 입력으로 다시 사용했을 때의 오차 상계가 아니다. 작은 certificate는 정확한 유한 coefficient 모델의 endpoint 방정식에 대한 결과다. 이것을 atomic model 정확도, source quadrature 정확도, 실제 ODE time error, arbitrary FP64 연산의 물리 오차로 해석하지 않는다. Scalar Wolfram 배치는 일반 기호식을 실행했으며 examples/COUPLED_BRANCH_WOLFRAM_INPUT.json의 숫자를 주입해 이 작은 certificate를 계산한 배치가 아니다.

## 4. BG3–BG4: 반응으로 변하는 원자 branch

고정 support \(0<w_1<\cdots<w_M\), nonnegative \(a_j(s)\), positive \(N_B(s),U_B(s)\)에 대해

\[
 N_k=N_B+\sum_{j\le k}a_j,\quad
 U_k=U_B+\sum_{j\le k}w_j a_j,\quad
 T_k=U_k/(c_vN_k),\quad
 w_k\le\alpha T_k<w_{k+1},
 \qquad \alpha=\chi k_B .
\]

Zero-weight support를 임의로 지우지 않고, 같은 에너지의 atoms는 묶고, threshold equality는 thermal로 정하는 convention이 코드와 유도에 일치한다. 반응 step의 초기 active donor mask와 원자 분류를 trial마다 서로 다른 reference에서 다시 만들지 않는다.

Inherited branch의 upper violation에 대해서는 다음 atom을 넣었을 때

\[
 \alpha T_{\rm new}
 =\frac{N_k\alpha T_k+(\alpha/c_v)a\,w}{N_k+a}\ge w
\]

이므로 방금 획득한 lower bound가 유지된다. Lower violation에서 최고 thermal atom을 빼는 식 역시 upper bound를 유지한다. 이 방향 불변성 때문에 **한 raw endpoint의 repair는 최대 M번의 index 변화로 끝난다**. 실제 온도의 단조성을 가정하지 않는다. 가중치가 0인 경우에는 non-strict inequality가 충분하다.

원자 inventory가 바뀌면 thermal/active 사이의 분할은 같은 raw count와 energy를 보존한다. Ionization 반응 동안 free-electron 총수가 일정하다는 잘못된 보존 명제는 사용하지 않는다. H nuclei, He nuclei, charge, thermal+active+binding energy의 사건 불변량이 별도로 확인된다.

실제 HI daughter를 쓰는 별도 \(\chi=4\) 구성에서 \(s_*=1/4\)의 crossing을 해석적으로 정한다. \(s=0.2\)에서는 두 prefix가 자기일관적이지만 inherited selection은 낮은 branch를 유지하고, \(s=0.25\)의 equality에서는 높은 branch로 이동한다. 실제 5개 extent \(0,0.2,0.25,0.3,0.5\)의 선택은 \(0,0,1,1,1\)이다. Crossing에서 계산된 prefix 온도는 약 299.0883 K와 306.7483 K다.

이것은 finite atom cutoff 모델의 branch 구조다. \(\chi>3/2\), 양의 crossing atom과 주어진 crossing 방향에서 생기는 jump 식은 올바르다. 여러 root를 삭제하거나 물리적 연속 온도 이력의 불연속 증거로 승격하지 않는다. 임의의 \(C^1\) path 전체에서 crossing 횟수가 유한하다고도 주장하지 않으며, 그런 시간 continuation에는 분리·횡단성 등 추가 조건이 필요하다.

## 5. BG5: observer와 massive geometry

후보는 metric signature \((-+++)\), unit normal \(n\), 물리적 공간 운동량 \(q\),
\(p=(E/c)n+q\), \(E=mc^2+W=-c\,n\cdot p\)를 사용한다. 따라서
\(c^2q^2=W(W+2mc^2)\)다. \(\nabla t=-n/c\)인 synchronous proper time에서 \(p\cdot\nabla t=E/c^2\)이며, accelerated observer의 국소 clock을 임의의 전역 시간 gradient로 바꾸지 않는다.

\[
 \nabla_a n_b=-n_a a_b+K_{ab}/c,\qquad
 K=H\gamma+\sigma
\]

에서 \(a=n\cdot\nabla n\)의 단위는 \(1/{\rm m}\), \(K,H,\sigma\)는 \(1/{\rm s}\)다. \(H>0\)를 expansion으로 정한 부호 convention과

\[
 \frac{dE}{dt_{\rm obs}}
 =-c^2 a\cdot q-\frac{c^2K_{ab}q^a q^b}{E}
\]

를 확인했다. Geodesic synchronous Bianchi normal에서는 \(a=0\), \(W>0\)이면

\[
 \dot W=-\frac{W(W+2mc^2)}{W+mc^2}
       (H+\sigma_{ab}e^a e^b).
\]

\(W=0\)에서는 방향 \(e\)를 정의하지 않고 \(q\)를 쓰는 원 식에서 drift 0을 얻는다. Antisymmetric frame rotation의 work는 0이다. 비상대론적 leading term과 exact remainder, \(W>0\)의 massless limit을 구별한 식도 맞다.

Diagonal Bianchi I에서 conserved covariant momentum \(P_i=a_i q^{\hat i}\)로
\(q^{\hat i,+}=(a_i^-/a_i^+)q^{\hat i,-}\)를 정한다. Count는 같은 comoving cell에서 보존되고 물리 volume은 \(\prod_i a_i\)에 비례한다. Geometry work는
\(\Delta U_{\rm geom}=\sum_j N_j(W_j^+-W_j^-)\), 외부 ledger에는 그 음수를 넣는다. 이 ledger를 thermal heat나 일반상대론의 국소 gravitational energy tensor로 해석하지 않는다.

후보의 kinetic energy density 식
\(\dot u+3Hu=-K_{ab}P^{ab}\)는 volume 변화 및 stress work에 맞는다. Thermal bath의 geometry work, Einstein 배경의 자기일관성, 일반 Bianchi의 방향 dynamics는 별도 closure다. Energy projection을 거친 뒤 모든 massive momentum·stress 성분이 정확히 보존된다는 결론도 사용하지 않는다.

## 6. BG6: moved parent와 실제 kernel

geometry_kernel_rebind.py는 positive finite scale factors와 방향을 가진 raw packet을 받는다. Stable kinetic formula는 같은 에너지 단위의 \(p=c|q|\), \(R=mc^2\)를 사용하여

\[
 W=\frac{p^2}{\sqrt{R^2+p^2}+R}
\]

를 cancellation이 작은 형태로 계산한다. 입력 zero momentum, 부적합 scale·overflow·nonzero component underflow, source 지원 밖 에너지를 구별한다.

실행은 서로 반대 방향인 두 half-count packets를 사용했다. 저장 source 에너지 30.00976971818039 eV에서 초기 momentum을 만들면 다시 평가한 에너지는 30.009769718180387 eV다. 이 초기화 차이 \(-3.55\times10^{-15}\) eV를 숨기지 않았다. Scale ratio \((0.5,1,1.5)\) 이후 \(W^+=36.678368111778816\) eV이며 geometry work는 \(+6.66859839359843\) eV다. Finite represented energies로 만든 rational 장부의 residual은 정확히 0이다.

90-digit 비교에서 약 \(7.51\times10^{-15}\) eV의 차이가 기록되어 있으나, 이는 이미 FP64로 계산된 \(q\)의 energy evaluation에 대한 진단이다. 전체 물리 geodesic roundoff의 엄밀한 certificate로 부르지 않는다. \(10^{-20}\) eV의 tiny arithmetic 예도 source cold-target 적용 증거가 아니다.

Moved parent는 예전 grid key가 아닌 P:forward 같은 고유 key와 현재 \(W^+\)에 묶인다. 그 에너지에서 원 HI/HeI total rate 및 sharing 배열을 다시 평가한다. Positive finite probabilities를 exact rational로 정규화하고 fast daughter는 \(W_p-B-W_{\rm slow}\)의 exact complement로 만든다. Barycentric grid와 실제 lower atoms/ghost를 모두 에너지 장부에 반영한다. 확률 합의 exactness가 물리 quadrature error 0을 뜻하지 않는다.

| 실제 이동 후 평가 | HI | HeI |
|---|---:|---:|
| Sharing 배열 크기 | 17,564 | 13,888 |
| Total coefficient \({\rm m}^3/{\rm s}\) | \(2.143100169002381\times10^{-14}\) | \(5.0171422373973835\times10^{-15}\) |
| 직접 사건 열을 확인한 index | 0, 32, 8782, 17563 | 0, 52, 6944, 13887 |

8개 사건 모두 4개 불변량 residual이 0이고, 원 source projector와 parity가 exact하며 한 사건의 양의 extent 예가 있다. Threshold equality와 팽창 후 below-threshold zero branch, 초기 cutoff mask, 상한 900 eV 밖 거절도 실제 기록에 있다. 전체 31,452 sharing 점 각각에 대한 새 full event 검산이나 full nonlinear family solver를 실행했다고 세지 않는다. Same-parent competing families는 이전 공통 capacity 규칙으로 함께 묶어야 한다는 조건을 유지한다.

Raw lower trace는 다음 cutoff 분류에 사용할 수 있도록 보존한다. Aggregate absorbed fields와 그 atom lift는 같은 물리량의 두 표현이므로 한 번만 사용한다. 역사적으로 사라진 lower trace나 scalar SDCS에 없는 daughter angles를 복구했다고 주장하지 않는다.

## 7. BG7: representation error와 적용 한계

\(x\in[l,u]\)를 두 끝점에 양의 barycentric weight로 옮길 때 count와 first energy moment는 정확히 보존된다. 각 mass \(n\)의 두 geometry factor

\[
 B_1=\frac{2n(x-l)(u-x)}{u-l},\qquad
 B_2=\frac{n(x-l)(u-x)}2
\]

로 \(|\Delta\langle\varphi\rangle|\le L B_1\), 또는 \(\le M_2B_2\)를 얻는 유도와 구현을 확인했다. 여러 packets는 합한다. Quadratic observable의 exact error \(2B_2\)와 Lipschitz kink의 bound는 직접 실행 기록에 있다. Geometry energy error \(\epsilon_j\)가 별도로 인증된 경우의 추가 \(L\sum_j n_j\epsilon_j\)도 conditional error map으로 타당하다.

Cutoff indicator는 이 \(C^2\) 식의 적용 대상이 아니다. 후보는 crossing cells의 weighted indicators로 \(\delta N,\delta U\)를 직접 계상하고,

\[
 \widetilde T-T
 =\frac{\delta U-c_vT\,\delta N}{c_v\widetilde N}
\]

를 통해 count와 energy 오류를 함께 EOS에 연결한다. \(\widetilde N\ge N_{\min}>0\) 같은 하한이 필요하다. 이것은 고정 cutoff에서의 표현 비교이며, 변화하는 implicit root의 유일성이나 branch 선택까지 대신하지 않는다.

HeI total coefficient의 closed-form 부분은 actual frozen BED constants를 정확한 실수로 읽고 \(1<t_0\le t\le t_1\)인 threshold-separated cell에서 미분한다. \(D(t)\), \(\log t\), \(f(t)\), \(g(t)=\sqrt t/(t+a)\)의 0–2차 미분 triangle bounds와 rational square-root upper bound를 원 source와 대조했다. 부호가 섞인 coefficients는 절댓값 상계에 반영되어 있다.

실제 cell \([36.66802549168974,36.69381567205715]\) eV에서 저장된 상계는

\[
 L_\kappa=2.6047684754190833\times10^{-15},\qquad
 M_{2,\kappa}=3.039380196849831\times10^{-16}
\]

이며 각각의 단위는 \({\rm m}^3/({\rm s\,eV})\), \({\rm m}^3/({\rm s\,eV}^2)\)다. \(C^2\) weak bound는 \(2.4279822340661305\times10^{-20}\ {\rm m}^3/{\rm s}\), 관찰된 FP64 source weak error는 약 \(2.5760\times10^{-22}\ {\rm m}^3/{\rm s}\)다. 이 숫자 비교와 ideal-real derivative bound를 구별한다. FP64 transcendental error는 별도의 \(\eta(w)\) bound가 있어야 엄밀한 전체 bound로 더할 수 있다.

HeI derivative bound는 이번 Wolfram scalar 24항목의 일부가 아니다. 원식·실제 코드에 대한 직접 수학 심사와 rational bound 실행 기록으로 지지된다. HI sharing quadrature의 모든 energy derivative나 topology가 바뀌는 지점까지 같은 상계를 제공한다고 주장하지 않는다.

## 8. 실제 실행 근거와 identity

| 새 실행 기록 | 실제 내용 | 독립 심사에서 한 일 |
|---|---|---|
| REACTION_BRANCH_CHECKS.json | 5개 extent의 crossing 구성, branch 선택, 사건·장부 불변량 | proof/code/raw 및 원 source 결속 확인 |
| COUPLED_BRANCH_CHECKS.json | 실제 두 사건 endpoint, D 전체 수축·branch margin, exact/log error certificate | 도함수·norm·interval 방향·정확한 endpoint JSON 비교 |
| GEOMETRY_REBIND_CHECKS.json | 3개 focused group: geometry/trace, 실제 moved HI/HeI, weak representation | source 4개 및 원 kernel 11개 identity, 8개 witness 공통 fields와 raw 대조 |
| WOLFRAM_XACT_RAW.json | **8개** tensor residual 0, AllZero True | 실제 package/version/body/script·출력·조건 확인 |
| WOLFRAM_SCALAR_RAW.json | **24개** scalar residual 0, **4개** inequality True | 각 계산의 주장 대응·가정·단위·표현 확인 |

합계는 **새 Python reference 프로그램 3개**, **Wolfram/xAct zero identity 32개와 inequality 4개**다. Python의 세 프로그램 내부 case 수와 Wolfram residual 수를 같은 test 단위처럼 더하지 않는다. 이전 과학 suite, full generator, physical ODE, NCP 실행은 모두 0이다.

xAct는 실제 Wolfram 15.0.1 Linux 64-bit 환경에서 xTensor 1.3.0, xPerm 1.2.4 및 pinned official xCore/xPerm/xTensor bytes를 사용했다. Canonicalization에는 지원되는 Wolfram backend인 \(\$xpermQ=False\)가 적용됐다. 실행 script의 inline tensor body가 별도 xact_branch_geometry_body.wl과 같은 것을 확인했다. 이전 loop의 xPerm external-backend 문제를 이번 후보의 물리적 장애로 계상하지 않는다.

Coupled module과 입력 JSON에는 실행 후 한 가지 label 교정이 있다. “KC1-KC8 accepted”가 “KC1-KC7 accepted”로 바뀌었다. COUPLED_BRANCH_METADATA_PATCH.json이 이를 기록한다. 심사자는 현재 bytes에서 그 문자열만 역치환하면 **실제 실행 때의 bytes와 SHA256가 정확히 복구됨**을 확인했다. 식·상수·branch·연산은 바뀌지 않아 과학 실행을 반복할 이유가 없다. Manifest는 교정된 현재 bytes와 과거 실행 raw 및 patch 기록을 함께 동결한다.

실제 시각도 구별한다. Reaction 실행은 2026-10-12 23:48 UTC, coupled는 23:54 UTC, geometry는 23:55 UTC에 기록되었다. 연구 단위의 20261013이라는 달력 이름을 raw 실행 UTC로 대신하지 않는다.

## 9. 검토 finding의 종결

아래는 구체적인 발견과 최소 수정의 기록이다. 모두 원자료 또는 실제 수정 bytes로 종결했다. 최종 동결 시 열린 scientific blocker는 0이다.

| ID | 대상 → 관찰한 근거 | 영향 → 최소 수정 | 최종 상태 |
|---|---|---|---|
| BG-DOC-01 | REPORT의 cutoff upper bound 0.1729952378229는 저장 최대값 0.1729952378229299보다 작았음 | 엄밀한 상계 문구의 반올림 방향 오류 → 0.1729952378230으로 outward rounding | 교정 확인, CLOSED |
| BG-DOC-02 | GR의 energy 변수 \(p=c|q|\) 뒤 초기화 문장에서 pc를 사용 | 같은 문단에서 energy와 momentum 기호가 충돌 → \(c|q|\)로 명시 | 교정 확인, CLOSED |
| BG-DOC-03 | GR 서두가 존재하지 않는 GEOMETRY_REBIND_ASSUMPTIONS.json을 참조 | 가정·error map의 근거를 따라갈 수 없음 → 실제 문서 §1, §§5–6을 참조 | 교정 확인, CLOSED |
| BG-DOC-04 | GR에 U+001C 문자가 있었고 실행일을 10-13 UTC로 적음 | 수식 렌더링 및 provenance 오해 → 문자 제거, 실제 10-12 23:55 UTC와 KST 구별 | 교정 확인, CLOSED |
| BG-META-01 | DAG 본체는 35→38, 65→69인데 current preservation/reference가 이전 FB/KC 단계를 가리킴 | 이번 결과 및 inherited output의 origin 오해 → historical exact 보존과 current origin group의 분리 | 33 inherited 및 current 5개를 정확히 덮는 것 확인, CLOSED |
| BG-DOC-05 | REPORT에서 branch HEAD를 source commit으로 부름 | 전달 commit과 과학 commit의 역할 혼동 → 두 이름과 hash를 각각 표시 | 교정 확인, CLOSED |
| BG-META-02 | 문헌 조사 단계의 pending 상태가 최종 보고서의 현재 과학 판정으로 보일 수 있음 | 판정 주체·시점 혼동 → 문헌은 완료, 최종 과학 심사는 DECISION 참조로 명시 | 본문 1줄 수정 확인, CLOSED |

Root의 PDF 시각 검토와 문서 reflow는 별도 publication 작업이다. 여기서는 고쳐진 부호·단위·수치·참조가 과학 본문과 맞는지를 확인했다. SOURCES/EXTERNAL_REFERENCE_INDEX에 남은 문헌 수집 시점의 pending label은 수집 단계 기록이며, 최종 science authority는 이 DECISION이다.

## 10. Overformalization watchdog

| 대상 | 관찰한 근거 | 영향 | 필요한 처리와 판정 |
|---|---|---|---|
| Conditional fixed-point 가정을 결과로만 반복하는 문제 | CB는 actual coefficients로 D의 image, \(\bar q\), log positivity, cutoff margin을 계산함 | 이전 caller contract 중 선택된 실제 사례가 구성적으로 채워짐 | BG1–2 수용. Full-family 조건은 이름 붙인 다음 작업에 남김 |
| Index 단조성과 온도 단조성의 혼동 | RB weighted-average 식은 \(\chi\ge3/2\)에서 index 방향을 유지하며 \(T\)는 내려갈 수도 있음 | 잘못된 온도 단조성 요구는 타당한 scan을 막음 | 유한 index repair를 수용하고 온도 path의 별도 조건을 명시 |
| 실제 coupling과 가상의 rate 의존성 혼동 | HI depletion과 생성 thermal electron의 Coulomb feedback은 존재하고 source는 cold-target 형태임 | 없는 \(T\)-rate 의존성을 넣으면 source identity가 깨짐 | 실제 연결만 채택하고 cold-domain 및 새로운 thermal-rate 모델을 구별 |
| Exact invariant와 모든 물리 moment exactness의 혼동 | 양의 두-node energy map은 count와 energy를 보존하지만 massive \(q(W)\)는 비선형임 | Energy map의 유용성은 유지되며 angular/stress 요구는 별도 | BG7을 조건부 수용하고 angular-moment node를 열어 둠 |
| 작은 rational certificate와 FP64 진단의 혼동 | CB certificate와 geometry 90-digit 비교의 의미가 명시적으로 다름 | 진단 숫자를 전체 물리 오차로 읽으면 과장 | Exact finite-model/ideal-real/FP64/model/time error를 분리한 현 문구 수용 |
| 승인되지 않은 전역 상태 승격 | 기존 19-node global overlay가 object 전체 exact equal이며 65개 old edges가 보존됨 | 국소 이론 성과가 application gate를 우회하지 않음 | 현재 두 theory node의 scoped completion만 허용 |

환경 제약, source 원문 조회의 제한, 이전 실행의 미재실행을 과학적 불가능성으로 바꾸지 않았다. 명확한 현재 구성과 소비자 조건이 있는 결과에 전역 sharpness·필요충분성·full ODE 실행을 추가 gate로 요구하지 않는다.

## 11. NG1–NG7 심사

이번 후보는 새 strong no-go를 주요 성과로 내세우지 않는다. 원자 multiplicity와 energy-only remap의 비보존 moment는 제한된 구성의 특성을 보이는 반례·범위 진술이다.

| 기준 | 확인 |
|---|---|
| NG1: 정확한 대상·조건·양화 | 두-event D, \(\chi\ge3/2\) finite prefix scan, 지정된 Bianchi I, threshold-separated smooth projection cell을 각각 한정함 |
| NG2: 완결된 증명 | Shared extent 장부, self-map와 수축, log tail, scan 방향 불변성, observer clock, barycentric bound와 HeI 미분 전개를 확인함 |
| NG3: 비자명성·기초 모델 | 실제 pinned HI/stopping/HeI source 및 저장 grid를 사용하며, 별도의 명시된 양의 stock construction이 있음 |
| NG4: 장애 기작 | Branch multiplicity는 finite atom의 EOS 편입에서, energy remap의 momentum 차이는 \(q(W)\)의 비선형성에서 나옴 |
| NG5: 과학적 귀결 | Inherited branch continuation, off-grid actual rebind, energy weak error budget 및 다음 composition/angle 작업이 구체적으로 이어짐 |
| NG6: 원전 비교 | 네 primary paper의 실제 절을 읽고 적용 조건과 비적용 정리를 구분함. 전역 novelty를 선언하지 않음 |
| NG7: 독립 검토 | 후보 비저자가 proof·code·source·raw를 확인했고 수정 후 파일 identity를 동결함 |

예를 들어 무차원 \(R=10\)에서 \(W=2\)를 양 끝 \(1,3\)의 같은 가중치로 바꾸면 count와 energy는 같지만
\((\sqrt{21}+\sqrt{69})/2<\sqrt{44}\)여서 같은 방향의 massive momentum magnitude는 달라진다. 실제 scalar 배치가 이 부등식을 확인한다. 이것은 지정된 two-node energy projection의 제한이며 모든 양의 angular remap의 불가능성을 증명하지 않는다.

**새 strong no-go 채택 수: 0.**

## 12. DAG 및 다음 작업의 범위

직전 DAG의 35 nodes와 65 edges에서 이번에는 38 nodes와 69 edges가 됐다. 기존 33 node objects, 기존 모든 65 edge 및 19-node global overlay object가 그대로 보존되었다. 두 selected node만 범위가 갱신되었다. 저장 topological order가 모든 edge를 만족하는 것을 독립적으로 확인했다. Current reference group 5개와 네 ancestral group의 33개가 중복 없이 전체 38개를 덮는다. 과거 metadata는 historical_immediate_prior_metadata에 원문 그대로 남긴다.

이번 결과로 completion을 수용할 node는 다음 두 개다.

- CR_THEORY_COUPLED_BRANCH_SOLVER: BG1–BG4의 실제 고정 branch endpoint와 생성 atom crossing 구성.
- CR_THEORY_GEOMETRY_KERNEL_REBIND: BG5–BG7의 prescribed massive geometry, 실제 moved-source rebind, 조건부 representation error.

이어지는 구체적 과학 작업은 열어 둔다.

1. CR_THEORY_MULTI_FAMILY_BRANCH_CONTINUATION: 둘 이상의 실제 상호작용 family, prefix에 따라 rate feedback이 달라지는 crossing, 인접 branch map의 compatibility 및 선택된 continuation, refinement/error 근거.
2. CR_THEORY_GEOMETRY_COLLISION_COMPOSITION: geometry → rebind → collision → classification의 순서, 하나의 work 장부, threshold-separated local splitting error와 crossing 대응 및 step refinement.
3. CR_THEORY_ANGULAR_MOMENT_REMAP: daughter angular/recoil closure 및 finite positive representation의 요구 moment를 구체화하고 가능 집합이나 오차를 분석하는 별도 이론.

기존 F hold, G blocked, PHYS02_DELAY open, production hold, G02 unresolved, all-bound open, bgrid no-go 및 기존 source/consumer budget/admission 상태는 그대로 유지한다. 새 이론 수용을 selected cosmological history, full generator, physical production adoption 또는 새로운 NCP 실행 허가로 바꾸지 않는다.

## 13. 최종 파일 동결과 사후 binding

review/CANDIDATE_MANIFEST.json에는 **113개 파일**을 exact bytes·SHA256로 동결했다. 이 중에는 current derivation 5개, reference implementation 3개, verification source 6개, input/witness 4개, execution evidence 8개, current source binding 1개, literature metadata 2개, inherited source/evidence 72개, external raw cache 10개, candidate CONTRACT/CLAIMS snapshot 2개가 있다.

CONTRACT.json과 CLAIMS.json의 심사 당시 bytes는 review/candidate_metadata에 보존한다. 최상위 live 문서는 명시된 status와 review_reference 경로만 갱신할 수 있다. 해당 경로를 제거한 canonical scientific-body SHA256가 같은지 사후에 비교한다. 가정·수식·claim scope·결과·입력·evidence 목록을 바꾸는 행위는 허용에 포함되지 않는다.

REPORT, PDF/LaTeX, DAG, RESULTS, HANDOFF, project policy 및 publication 파일은 이 결정을 소비하는 산출물이다. 최종 status 전환과 보고서/PDF source identity는 POST_REVIEW_BINDING에서 연결한다. 이 분리는 승격 근거가 된 science bytes를 바꾸지 않고 판정 문구와 전달 상태를 기록하기 위한 것이다.

외부 원문이 담긴 retrieval cache 10개는 로컬에 유지하고 Git 및 배포 archive에서 제외한다. 그중 8개는 심사자의 SciSpace/Exa 원응답, 2개는 root 보조 원응답이다. EXTERNAL_REFERENCE_INDEX에는 URL·query·규모·SHA256·읽은 범위 및 cache 배포 제외를 기록한다. Hash는 MCP JSON envelope에 대한 것이며 원 PDF 바이너리의 hash라고 주장하지 않는다. 나머지 과학 코드·자체 원출력·원 grid와 입력은 배포 범위에 남는다.

이 동결 후보에 대한 최종 판정은 **BG1–BG7의 PROMOTE_SCOPED / PASS**다. 과학 재실행이나 새로운 근거 확대 없이, 명시된 claim 범위와 위의 후속 작업 구분을 유지하여 보고서와 연구 handoff에 반영할 수 있다.
