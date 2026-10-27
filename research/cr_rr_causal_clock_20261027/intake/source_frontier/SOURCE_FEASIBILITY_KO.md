# R1/R2 — 외부 proper-time 입력의 소스 가용성과 다음 계산 단위

작성: 2026-10-27. 역할: source-feasibility child. 이 문서는 실제 source 열람, 문헌 대조, 다음 단위 선택의 근거다. 새 과학 solver, 기존 campaign 재실행, 저장소 수정·게시, 독립 승인 판정은 수행하지 않았다. 부모 연구 루프가 R3 이후 계약·증명·예산·독립 검토·실행·백업·게시를 이어간다.

## 1. 선택 결론

**현재 저장된 HeIII shared operator와 세 source pulse를 사용해, 명시한 관측 시간까지의 RR count·kinetic energy·retained-photon 반환량 및 시간 bin 반환량을 계산하는 단위를 선택한다.** 유한 관측 시간을 가진 새로운 물리적 조건부 응답이다. 이미 완성된 all-time RR 값을 다시 계산하는 단위가 아니다.

제안 방법은 **양의 Erlang-clock resolvent 계산과 deterministic-horizon enclosure**다. 이전 M0/M1/M2의 일반 source convolution 관계는 그대로 재사용한다. 현재 저장된 H1/HeI/HeIII 공통 K에서 finite-age RR 응답이 새 산출물이다. 선택 근거는 저장된 양의 source·삼중대각 K·all-time reward가 모두 있어 새 rate provider나 전 과거 suite 없이 변경 계산을 구성할 수 있다는 점이다.

아래 두 사실을 동시에 보존한다.

1. 과거 실제 실행에는 proper-volume, proper-time의 \(Q_e(W,t)=tA(W)\) source가 있다. “실제 history는 어디에도 없다”는 주장은 틀리다.
2. 그 source의 100 K bath와 현재 HeIII 10,000 K bath는 다르다. 현재 세 redshift source pulse에 대응하는 실제 연속 주입 history, 노출 시간, donor/recipient baryon 정규화는 아직 제공되지 않았다. 과거 값을 이식하거나 평균 지연 시간으로 노출 시간을 만들 수 없다.

## 2. 확인한 authority와 재사용 범위

- bass_cr branch: `research/cr-heiii-ground-rr-20261027`.
- 현재 D: `ec463db0c7e5c7fb5070796071c926caa4db6445`. 2026-10-27 06:03 UTC에 ref를 다시 조회해 동일 HEAD를 확인했다.
- 과학 S: `4e72c89b714431eb4c6ae07def777bbf72a5ae4c`, PR107.
- D의 `AGENTS.md` 전체를 읽었다. 14,446 bytes, SHA256 `8d62d9758fe173263eb3820c7b00ca569193bb7f912fc3d95d145e73d4a40970`.
- physmath-research-loop 사용자 버전 1.0.0의 SKILL, RESEARCH_POLICY, THEORY_LOOP을 읽고 R1/R2에 적용했다. 미제공 source는 데이터 의존성으로 기록하며 no-go로 승격하지 않는다.
- 병렬 최신 조사 결과는 부모와 latest_repo_survey에서 받았다. REI237 ADMISSION 및 REC source-synthesis CODING_CONTRACT 원문도 이 child가 직접 다시 읽었다. 최신 REI/REC 결과는 아래 비교에 반영했다.
- N4/N5의 부분 열린 상태, N6/N7 predecessor gate, 과거 UNKNOWN_NO_ACK와 예산은 변경하지 않는다. 이 source 선택만으로 DAG 완료 수를 올리지 않는다.

8개 public repository text snapshot과 해당 byte 수·SHA256·정확한 원문 URL은 [SNAPSHOT_MANIFEST.json](SNAPSHOT_MANIFEST.json)에 있다. 현재 engine·primary snapshot은 원래 source intake의 해시와 일치한다. 이 문서의 외부 문헌 근거와 실제 열람 범위는 [PRIMARY_SOURCES.json](PRIMARY_SOURCES.json)에 구분했다.

## 3. 실제 source와 history의 가용성

| 근거 | 실제 제공되는 것 | time/volume 정규화 | 현재 HeIII 단위에 허용되는 사용 |
|---|---|---|---|
| PR107 saved source, z=2.316, 2.479, 2.649 | 각 384 atom의 \(0<W<10\) eV pulse와 저장된 active-grid projection | `pulse_count_cm3`; 현재 결과의 연속 rate·exposure·instantaneous RHS는 null | pulse를 \(\tau=0\) 초기 측도로 고정한 조건부 응답. 각 z는 대안이며 시계열이 아님 |
| 20261012 CR source-binding | 실제 실행 계보로 연결된 \(Q_e(W,t)=tA(W)\), \(0\le t\le10^{10}\) s | \(q_p\): proper \(m^{-3}s^{-1}eV^{-1}\), \(A\): \(m^{-3}s^{-2}eV^{-1}\), proper-volume 변환 이미 적용 | 기존 실제 history의 존재·scope 증거. 다른 bath이므로 현재 pulse에 묵시 이식 금지 |
| REI237 thermal assimilation | 실제 PW19 background와 제조한 fast-pool moments, prescribed constant \(\nu\) | background \(T=14919.863839279506\) K, \(n_b=10.669321142818111\ m^{-3}\); conditional rate 별도 | native 소비·정규화 인터페이스의 증거. source-matched history 또는 physical stopping provider가 아님 |
| REC source synthesis | HD 24 diagnostics 및 H5 native piecewise-linear history remainder | 313 queries, prefix 5127, physical coverage 0/313 | history-aware 방법과 source 계약의 참고. 현재 CR bath의 실제 주입 history가 아님 |

현재 HeIII bath는 \(T=10000\) K, \(\theta=0.8617333262145178\) eV, \(\ln\Lambda=20\)이다. target density는 \((n_{\rm HI},n_{\rm HII},n_{\rm HeI},n_{\rm HeII},n_{\rm HeIII})=(0.9,0.1,0.07,0.02,0.01)\ {\rm cm}^{-3}\), 전자 bath는 \(n_e=0.14\ {\rm cm}^{-3}\)이다. 이 고정 bath 정보가 외부 source donor와 recipient의 정규화 또는 시간 이력을 대신하지 않는다. REI의 \(T,n_b,\nu\)를 이 bath로 옮기지 않는다. [현재 동결 계약](https://github.com/cosmosapjw-quantum/bass_cr/blob/ec463db0c7e5c7fb5070796071c926caa4db6445/research/cr_heiii_ground_rr_20261027/FROZEN_CONTRACT.md)

### 3.1 현재 pulse를 손실 없이 소비하는 법

현재 `engine.py::atoms/source_average`는 세 CSV를 읽고 저장된 projection을 그대로 소비한다. `projection[0]`은 경계 진입 mass이며, RR transient population은 `projection[1:]`이다. 경계 진입 mass는 RR 기여가 0이지만 원 source count·energy ledger에는 남아 있어야 한다. 저장된 active mask 또는 grid를 새로 만들거나 source를 다시 정규화하지 않는다. [실제 engine](https://github.com/cosmosapjw-quantum/bass_cr/blob/ec463db0c7e5c7fb5070796071c926caa4db6445/research/cr_heiii_ground_rr_20261027/implementation/engine.py)

원 pulse의 count/cm³에 곱한 결과와 active conditional probability를 구분한다. 전자는 실제 저장된 pulse amplitude의 조건부 반환량이고, 후자는 count로 나눈 무차원 값이다. 현재 export는 24 case/source alternatives를 additive population 또는 time history로 취급하지 않는다. [실제 primary](https://github.com/cosmosapjw-quantum/bass_cr/blob/ec463db0c7e5c7fb5070796071c926caa4db6445/research/cr_heiii_ground_rr_20261027/implementation/primary.py)

| 저장 source | bytes | SHA256 |
|---|---:|---|
| ATOMS_2.316.csv | 43,446 | `463275c98366137ef2987857dc55ca7707581406b4fbdf2595d17e1f62a138f0` |
| ATOMS_2.479.csv | 43,485 | `2a330ffcd520eec96dae5b24658b3c8d801ced37e392b6f3f46a0a9155ed85f7` |
| ATOMS_2.649.csv | 43,453 | `a18585f5cfdc534a7d54dbe59179775bb44b5b104df250cfaad111213a46dfb8` |

이 표는 기존 INPUT_MANIFEST와 source intake 핀의 전사이며, 이 child가 CSV를 다시 계산했다는 뜻이 아니다. 바이너리 NPZ/CSV의 canonical ZIP 복원·검증은 부모 작업이다. 기존 H1 RR, HeI/HeIII ground-state source와 isotope mapping 및 C23E의 재사용 경계가 그대로 적용된다.

### 3.2 과거 실제 \(Q_e=tA\) 이력

실제 launcher/API 해시와 transitive constructor, 저장된 source array를 연결한 archive는 다음 source를 사용한다.

\[
 A(W)=\sum_{s=H,He}n_{s,0}
 \int_{1\,{\rm MeV}}^{4\,{\rm MeV}}
 q_p(K)v_p(K)\frac{d\sigma_{p,s}}{dW}\,dK,
 \qquad Q_e(W,t)=tA(W).
\]

\(q_p\)는 각도 적분된 proper-volume 양성자 주입률이다. 전체 source-energy 정규화 창은 10 keV–1 PeV이고, 선택 collision window 1–4 MeV를 전체 power로 다시 정규화하지 않는다. \(z=8\)의 proper-volume 인자 \((1+z)^3=729\)는 이미 적용되므로 추가 \(4\pi\), 729 또는 window-renormalization을 곱하지 않는다.

이력의 배경은 \(n_H=140\,m^{-3}\), \(Y_{\rm He}=0.248\), \(T_g=100\) K, \(x_{\rm HII}=x_{\rm HeII}=0.01\), \(x_{\rm HeIII}=0\), 초기 비열적 population 0, \(T_0=10^{10}\) s이다. \(N_p=tq_p+O(Ht^2q_p)\)의 초기 국소 근사이며, 정확 collisionless Bianchi 수송 PHYS01과 같은 시간 이력이라는 주장은 하지 않는다. 저장된 energy endpoint injection \(q_*=1.8012625784\times10^{-42}\ {\rm J\,m^{-3}s^{-1}}\)와 \(q(t)=q_*t/T_0\)는 이 source의 값이다. [정확한 source 계보](https://github.com/cosmosapjw-quantum/bass_cr/blob/ec463db0c7e5c7fb5070796071c926caa4db6445/research/cr_source_binding_20261012/inputs/source_lineage/SOURCE_FINDINGS_KO.md), [당시 보고서](https://github.com/cosmosapjw-quantum/bass_cr/blob/ec463db0c7e5c7fb5070796071c926caa4db6445/research/cr_source_binding_20261012/REPORT_KO.md)

### 3.3 새 병렬 결과가 해결한 것과 남긴 것

REI237의 admission은 `source_matched_history=false`, `physical_provider_qualified=false`, `physical_nu_s_inverse=null`을 명시한다. 제조한 \(\zeta=0.2191163469802296\), \(w=7.010531745782858\times10^{-19}\) J/baryon과 prescribed \(\nu=8.160348695705333\times10^{-18}\ s^{-1}\)가 native thermal join을 시험한다. 같은 수치의 H를 사용해도 \(\nu\)는 독립적으로 처방된 conditional law다. 이를 empirical stopping이나 현재 CR의 실제 주입으로 바꾸지 않는다. [REI237 원문](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/ee6746ab172f862dddfdec63b59e5e3707b59eaa/research/rei_expanded_event_consumer/thermal_assimilation_20261027/ADMISSION.json)

REC source synthesis의 native history remainder는 H5 이력의 exact-rational grid에서 causal endpoint와 knot remainder를 다룬다. physical coverage 0/313이 유지되고, 현재 CR source history를 공급하지 않는다. [REC 계약](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/eb3b390eb59a4c48b5aa2d3bec928465b9c35f2e/research/rec_source_synthesis_20261027/CODING_CONTRACT.json)

## 4. 중복하지 않을 기존 이론

기존 M0는 고정 kernel \(H_0,F\)에 대해

\[
P(T)=H_0\int_{[0,T]}q(T-\tau)\,dF(\tau)
\]

와 \(p,R,S\)를 이미 사용했다. quadratic source에서 \(P/(H_0q_*)=ap+bR+cS\)이고, M1/M2는 \(C^2\) source의 positive one-delay closure와 curvature error도 구성했다. 따라서 일반 convolution 식, 평균 지연으로 closure를 만든다는 사실, 또는 \(p,R,S\) 이름을 새 단위의 독자적인 과학 결과로 세지 않는다. 이 archive의 heating kernel과 현재 HeIII shared RR K는 동일 operator가 아니다. [M0](https://github.com/cosmosapjw-quantum/bass_cr/blob/ec463db0c7e5c7fb5070796071c926caa4db6445/research/cr_m0_quadratic_20261012/README_KO.md), [M1–M3](https://github.com/cosmosapjw-quantum/bass_cr/blob/ec463db0c7e5c7fb5070796071c926caa4db6445/research/cr_rux_m1_m3_20261012/REPORT_KO.md)

## 5. 제안 단위의 수학적 구성과 변경 계산

아래 식은 feasibility를 위한 구성이다. R5에서 가정·증명·부동소수점 오차 분리를 정식 검토해야 하며, 아직 수치 PASS나 새로운 물리 error certificate가 아니다.

### 5.1 양의 finite-age RR measure

현재 저장된 실제 표현 행렬 \(K\)를 finite nonsingular M-matrix로 채택하고, \(w\ge0\)를 저장된 transient pulse population, \(r\ge0\)를 RR reward column으로 둔다.

\[
k_r(t)=w^\top e^{-Kt}r,\qquad
F_r(T)=\int_0^T k_r(t)\,dt,\qquad
P_r=F_r(\infty)=w^\top K^{-1}r .
\]

\(-K\)가 Metzler이고 stable이면 \(k_r(t)\ge0\), \(0\le F_r(T)\le P_r\)다. 이 양의 finite reward measure 성질에는 exact row-substochastic 조건을 별도로 가정할 필요가 없다. 확률·입자 보존을 주장할 때는 generator/row balance 오차를 별도로 확인한다.

- count reward \(r=\lambda_j\): \(F_r\) 단위 \({\rm cm}^{-3}\).
- kinetic reward \(r=\lambda_jE\): \(F_r\) 단위 \({\rm eV\,cm}^{-3}\).
- retained photon: \(F_{\lambda_jE}+I_jF_{\lambda_j}\).
- internal ledger: \(-I_jF_{\lambda_j}\).

\(j\)는 기존 source-qualified H1, HeI, HeIII의 채널이다. 새로운 atomic/isotope provider나 hazard를 생성하지 않는다. 기존 all-time reward를 재사용해 \(P_r\)와 새 유한 시간 결과의 관계를 평가한다.

저장된 `K_diag/K_lower/K_upper`와 intended \(K_0+\operatorname{diag}\lambda\) 사이에는 이전 binary64 diagonal-addition 이슈가 있다. **이번 계산이 저장된 표현 K를 대상으로 하는지 명시해야 한다.** 원래 hazard 합의 더 정확한 실수 행렬이나 continuum physical generator를 계산했다고 말할 수 없다.

### 5.2 Erlang clock으로 작은 양의 shifted solves만 수행

\(H\sim {\rm Erlang}(m,\gamma)\)를 proper-second 관측 clock으로 잡으면

\[
 A_m(\gamma)=\mathbb E[F_r(H)]
 =\sum_{\ell=0}^{m-1}
 \gamma^\ell w^\top(K+\gamma I)^{-(\ell+1)}r .
\]

따라서 \(K+\gamma I\)를 한 번 factor하고

\[
 v_0=(K+\gamma I)^{-1}r,\quad
 v_{\ell+1}=\gamma(K+\gamma I)^{-1}v_\ell,\quad
 A_m=\sum_{\ell=0}^{m-1}w^\top v_\ell
\]

를 계산한다. 모든 항은 exact arithmetic에서 음이 아니다. \(P_r-\text{nearby term}\)의 상쇄로 작은 RR 응답을 계산하지 않아도 되고, dense matrix inverse나 전체 시간 ODE가 필요 없다. 동시에 여러 reward RHS와 세 source weights를 공유할 수 있다.

Stiff transient/cumulative reward에 Erlang random-time 방법을 쓰고 sparse/banded 구조를 유지하는 방향은 문헌 P2와 부합한다. 실행 비용·정확도는 실제 shifted-system conditioning과 선택 \(m,T\)에 달려 있으므로 benchmark를 했다는 주장은 하지 않는다.

### 5.3 deterministic horizon과 시간 bin 반환

평균이 각각 \(T\)보다 작은 \(H_-\), 큰 \(H_+\)를 잡는다. \(q_-\ge\Pr(H_->T)\), \(q_+\ge\Pr(H_+<T)\), \(q_\pm<1\)이면

\[
 \max\!\left(0,\frac{A_- - P_rq_-}{1-q_-}\right)
 \le F_r(T)\le
 \min\!\left(P_r,\frac{A_+}{1-q_+}\right).
\]

부모 제안의 analytic Chernoff tail을 사용하면 special-function probability evaluation이 필요 없다. \(a=\gamma T/m\)에 대해, \(a>1\)에서는 upper clock tail, \(0<a<1\)에서는 lower clock tail을

\[
q\le \exp\{m(\log a+1-a)\}
\]

로 bound한다. 이는 exact real-arithmetic clock-tail bound다. log/exp 및 shifted-solve를 binary64로 계산할 때의 rounding bound가 자동으로 포함되는 것은 아니다.

\(0\le T_1<T_2\)의 RR bin return은 \(F_r(T_2)-F_r(T_1)\)이며, endpoint bounds에서 안전한 차분 enclosure를 만든다. 양의 bin 폭으로 나눈 값은 **declared pulse·declared horizon에 대한 평균 반환률**이다. 이것을 source-matched continuous injection의 physical rate나 pointwise instantaneous rate로 노출하지 않는다. 기존 `event_rate_m3_s=null`, `exposure_s=null`의 뜻을 바꾸지 않도록 별도 조건부 bin 필드와 clock 의미가 필요하다.

### 5.4 외부 실제 이력이 공급되면 연결할 계약

앞으로 실제 외부 source \(b(t)\)가 주어지면 forward population은

\[
 n(t)=e^{-K^\top t}n_0+
 \int_0^t e^{-K^\top(t-s)}b(s)\,ds,
 \qquad j_r(t)=r^\top n(t).
\]

\(b(t)=wq(t)\), \(q\) 단위 \(s^{-1}\)인 분리 가능한 source라면 누적 반환은

\[
Y_r(T)=\int_0^T q(s)F_r(T-s)\,ds.
\]

\(q\), proper/comoving volume, native clock, source/recipient density가 입력되지 않은 상태에서는 이 관계만 제공한다. 실제 \(j,Y\)를 산출했다고 기록하지 않는다. 현재 3 snapshots의 redshift 간격에서 시간 차를 추정하거나 pulse amplitude를 임의 기간으로 나눌 수 없다. 이 단위는 causal RR return을 개선하며 전체 photon/electron/baryon cascade 또는 stopping을 완성하지 않는다.

## 6. R3 이후로 넘길 구체적인 판정 항목

- 저장된 K와 raw projection을 정확한 핀으로 읽고, actual represented finite operator를 계약 대상으로 선언한다.
- source-pulse 초기 시점 \(\tau=0\), 관측 horizon/bin, Erlang orders, tail 선택, 허용 비용·attempt 수를 실행 전에 부모 계약에 고정한다. 과거 완료 campaign을 다시 돌리지 않는다.
- 현재 pulse 결과를 finite-age count·kinetic·retained-photon bin return으로 낸다. 외부 time-history/nb/null과 기존 canonical rate null을 보존한다.
- 정확한 finite-K 해석적 clock bracket, numerical shifted-solve/rounding 오차, 과거 grid/physical model 오차를 서로 구분한다. finite-K 결과로 global physical error를 채우지 않는다.
- baseline all-time 결과는 그대로 재사용한다. 변경된 finite-time 계산에 대해서만 분석 가능한 작은 positive systems와 독립된 reference 또는 residual enclosure를 선택한다.
- N6/N7, isotope mapping, WU/REC/HE provider validity, UNKNOWN_NO_ACK·과거 budget을 유지한다. caloric partition 또는 retained-photon bookkeeping을 물리 heating 완료로 승격하지 않는다.
- 독립 검토, 최종 source ZIP, 이중 백업, expected-SHA non-force publication 및 DAG 변화 판정은 부모의 단계별 workflow에서 수행한다. 이 child의 파일 생성은 해당 게시 영수증을 대신하지 않는다.

## 7. 문헌과 구성의 경계

**P1.** Bladt, Meini, Neuts, Sericola (2002), *Distributions of reward functions on continuous-time Markov chains*, DOI 10.1142/9789812777164_0003. 저자 측 PDF의 초록·서론·변환/모멘트·uniformization 부분을 제한된 길이로 읽었다. finite CTMC reward transform, uniformization, convolution의 일반 근거다. [Primary PDF](https://www-id.imag.fr/Laboratoire/Membres/Sbeity_Ihab/Sure-Paths/publi_general/BMNS-MAM4.pdf)

**P2.** de Souza e Silva, Leão, Marie (2013), *Efficient Transient Analysis of Markovian Models Using a Block Reduction Approach*, INFORMS Journal on Computing 25(4), 743–757, DOI 10.1287/ijoc.1120.0537. SciSpace 검색 뒤 공식 publisher 초록과 서지 정보를 직접 읽었다. Erlang random-time와 stiff sparse/banded transient/cumulative reward가 근거다. 전문을 읽지는 않았다. HAL 원문 접근은 실패했으며 전문 열람으로 기록하지 않는다. [Official abstract](https://pubsonline.informs.org/doi/abs/10.1287/ijoc.1120.0537)

**P3.** Bladt, Asmussen, Steffensen (2019), *Matrix calculations for inhomogeneous Markov reward processes, with applications to life insurance and point processes*, arXiv:1905.04605. 초록·서론·행렬 product-integral 배경과 모델 도입을 부분 열람했다. 시간 의존 reward와 matrix formulation의 일반 근거다. [Primary arXiv](https://arxiv.org/abs/1905.04605)

P1–P3가 현재 CR source를 인증하거나 위 deterministic-horizon inequality, source-matched injection, physical heating을 증명했다는 뜻은 아니다. 위 bracket과 CR-specific 연결은 부모 R5에서 직접 증명하고 독립 검토할 구성이다. 새 방법의 문헌상 독창성도 주장하지 않는다.

