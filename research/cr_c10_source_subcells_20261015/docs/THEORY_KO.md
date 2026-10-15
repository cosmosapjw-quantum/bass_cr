# SOURCE07 C6: 문턱 분할 양의 source-subcell quadrature 이론

## 정확한 물리 범위

SOURCE07 C5의 50,000 K MD14 source를 동일 native source cell 48개로 보존한다. 그 cell `c`의 조건부 광자 수 분율 `f_c`는 원 Rust `AxbiSource`의 Simpson-32 평가와 같은 것이며, 
\(S(E)=E^2/[\exp(E/(k_B T_\star))-1]\), \(I_c=\int_c S(E)dE\)로 정의한다. Source-conditioned 재구성은 \(d\mu_c(E)=f_c S(E)dE/I_c\)이다. 서로 다른 source epoch, 각도, clock 및 광자의 공변 q_i는 별도 소유한다.

고정 참조 에너지 셀 \([E_i^*,E_{i+1}^*]\)에서 물리 에너지는 \(E=R E^*\), 적분영역은 실제 native source cell들과의 교집합이다. 각각의 교집합에서 부호가 양인 GL8 또는 GL16 점 \((E_j,w_j)\)를 만든다. 가장 안쪽 구간은 원래 native 13.6/24.59/54.42/100 eV source 경계로 끊기므로 모든 원자 fit cutoff의 불연속은 정확히 분리한다. Source Jacobian \(J_\Omega\)와 방향 weight는 owner의 방출률에 한 번만 들어가며 이 코드 내부에서 만들지 않는다.

## 순간 rate/heat

고정 proper 중성 밀도 \(n_k\), 시간 \(\Delta t\)에서 \(\lambda_k(E)=c n_k\sigma_k^{Verner}(E)\), \(\Lambda=\sum_k\lambda_k\)라고 하자. 각 photon의 정확한 constant-rate exponential one-step event probability는
\[
  P_k(E)=\begin{cases}
  (1-e^{-\Delta t\Lambda})\lambda_k/\Lambda,&\Lambda>0,\\
  0,&\Lambda=0.
  \end{cases}
\]
Source q-cell moments and readouts are:
\[
 N_i=\sum_j w_j,\quad U_{i,*}=\sum_j w_j E_j/R,
 \quad A_{ik}=\sum_{j\in i} w_j P_k(E_j),
 \quad H_{ik}=\sum_{j\in i}w_j(E_j-I_{k,bind})P_k(E_j).
\]
원자별 결합에너지 \(I_{k,bind}=(13.598434599702,24.587389011,54.41776)\) eV는 fit cutoff \((13.60,24.59,54.42)\)eV와 구분된다. 남은 photon moments는 \(N'_i=\sum_j w_j e^{-\Lambda(E_j)\Delta t}\), \(U'_{i,*}=\sum_j (w_j E_j/R)e^{-\Lambda\Delta t}\).
따라서 **같은 discrete quadrature measure에서** 다음은 수학적으로 정확하게 상쇄된다:
\[
 N_i=N_i'+\sum_k A_{ik},\quad R(U_{i,*}-U'_{i,*})=\sum_k[H_{ik}+I_{k,bind}A_{ik}].
\]
이는 GL8의 실제 연속 source 적분에 대한 오차 인증이 아니라, **source-conditioned 이산 모형의 광자 수·에너지 장부**다.

## N,U만으로는 모든 source family를 계속 표현할 수 없음

\(\chi=24.59\,eV\)에서 \(\sigma_{HeI}(E<\chi)=0\), \(\sigma_{HeI}(\chi)>0\)인 원 fit를 보자. \(\mu_1=\delta_{\chi}\), \(\mu_2=(\delta_{\chi-\epsilon}+\delta_{\chi+\epsilon})/2\)는 각각 photon count 1, 평균에너지 \(\chi\)를 갖는다. 그러나 HeI rate의 차이는 \(\epsilon\downarrow0\)에서 일반적으로 0이 아닌 문턱 점프의 절반으로 수렴한다. 즉 \(N,U\) 두 moment만으로는 임의 시간의 HeI photoevent를 유일하게 결정할 수 없다. 이번 GL 방식이 재이온화 전체 history의 물리적 폐쇄를 대신하지 못하는 이유다.

**허용**: 원 MD14 source의 독립된 새 주입 사건, 또는 별도로 입증된 shape closure. **금지**: 이미 흡수로 hardened된 임의 q-bin을 항상 원 BB50k 조건부 shape로 되돌리는 것.

## 수치 신뢰성

양의 GL weights와 양의 native source 분율로 positivity가 유지된다. GL8은 구간별 차수 15 이하 다항식을 정확히 적분하지만, 여기 source·Verner·exp는 비다항식이다. GL4/8/12/16 비교 및 독립 SciPy adaptive quadrature는 오차 **관찰**, 전구간의 16차 미분 supremum을 평가하지 않았으므로 엄밀한 절대 오차 상계로 등급을 올리지 않는다.

Source nE64/128/256/512/1024, R=1에서 HeI event는 owner continuum reference와 ~1e-11 상대차(원 native fraction과 owner SciPy 실수 입력차 포함)이며 원 centroid는 nE256에서 -1.21148%, nE1024에서 +0.40774%이다. 이론적 처리 유무가 바뀌는 오차임을 입증한다. 기존 원자·CR/RCT/HH OFF 역사, 기존 source ID와 owner C5 solver는 변경하지 않는다.
