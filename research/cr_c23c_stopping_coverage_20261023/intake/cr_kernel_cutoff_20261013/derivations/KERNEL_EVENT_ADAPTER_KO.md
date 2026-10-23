# 실제 BASS_CR daughter kernel에서 보존 사건 열로 가는 구성

연구 단위: `CR-THEORY-KERNEL-CUTOFF-20261013`  
노드: `CR_THEORY_KERNEL_EVENT_ADAPTER`  
기준 commit: `1f32987b2cc3eb521b4e09c736873ce21e9657a4`  
의존 근거: 승인된 FB1–FB7의 shared-capacity map, endpoint feedback 정리, covariant geometry 구성. 이 문서는 이들을 실제 PHYS02C/PHYS02B kernel에 결속하는 새 유도이다.

## 1. 이번에 닫는 대상과 실제 입력

선택한 물리 모형은 PHYS02B의 전자 stopping·projection·CCC excitation에 PHYS02C의 coherent full BED HI/HeI ionization을 결합한 기존 모형이다. 실제 저장된 9600-node array와 실제 source definitions를 읽었다. 원래의 외부 proton/electron injection이나 전체 time evolution을 재실행하지 않고, collision operator의 사건 분해 및 조성 feedback을 구성한다.

| 근거 ID | 실제 Git 경로 | 이번 역할 |
|---|---|---|
| SRC-P | `research/cr_phys02b_20261010/src/causal_cascade.py` | `Cascade.project`, `_sharing`, `stopping_eV_s`, generator의 열 조립식 |
| SRC-B | `research/cr_phys02c_20261011/src/coherent_bed.py` | HI/HeI coherent full BED total/SDCS |
| SRC-G | `research/cr_phys02c_paired_9600_closeout_20261011/raw/THIRD_GRID_LOCAL_20261011_EXEC01/SPECTRUM_fullBED_9600.npz` | 실제 저장된 `energy_eV` |
| SRC-C | `research/cr_phys02b_20261010/inputs/CCC_USED_CHANNELS.json` | 27개 기존 channel·단위·effective cost inventory |
| SRC-H | `research/cr_phys02b_20261010/inputs/ccc/HI/2P.1S` | 실제 HI 1S→2P table |
| SRC-He | `research/cr_phys02b_20261010/inputs/ccc/HeI/t2S.s1S` | 실제 HeI s1S→t2S table |
| SRC-O | `research/cr_phys02c_20261011/research/ionization_sources/SOURCE_ALGEBRA_RESULT.json` | 기존 oscillator algebra의 채택 상수 |

전체 11개 결속 파일의 Git blob SHA-1, SHA-256, bytes는 `inputs/KERNEL_SOURCE_BINDING.json`에 있다. 복원된 local source bytes를 현재 pinned tree의 blob identity와 각각 대조했다. NPZ SHA-256은 `7ee8c1eff7f58cd7175a9bcd3968a27ef065f0e983f05e609dc875f5f06112cc`이고, 저장된 `<f8`, C-order `energy_eV` 9600개의 raw SHA-256은 `6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292`이다. 첫 node는 0.10309375000000001 eV, index 3199는 10 eV, 마지막은 900 eV다. 새 mesh를 생성하거나 저장된 spectrum을 다시 구하지 않았다.

고정한 source 상수는

\[
 W_b=0.1\ {\rm eV},\quad W_{\max}=900\ {\rm eV},\quad
 B_H=13.6057\ {\rm eV},\quad B_{He}=24.587\ {\rm eV},
 \tag{KA.1}
\]

이며 atomic 대상은 HI와 HeI이다. HeII의 추가 ionization rate, recombination rate, thermal-ionization rate는 이 source가 제공하는 이번 event family에 포함되지 않는다. 기존 FB family는 그런 사건을 더할 수 있는 구조 정리로 재사용하고, 실제 원자 자료의 범위는 위 두 종에 결속한다.

원래 고정 bath의 수밀도는 \(n_{HI,0}=138.6\ {\rm m}^{-3}\), \(n_{HeI,0}=11.427127659574467\ {\rm m}^{-3}\), \(n_{e,0}=1.5154255319148937\ {\rm m}^{-3}\), 원래 gas temperature는 100 K이다. 새 continuation에서는 target neutral counts와 thermal electron count를 갱신한다. 이때 stopping에 들어가는 \(n_e\)는 **thermal electron bath의 수밀도**로 명시한다. 핵종을 포함한 EOS의 전체 thermal particle count 또는 active electron까지 포함한 전체 자유전자 수밀도와 구별한다.

## 2. 상태와 lower absorber의 표현

고정 physical volume \(V_*>0\)에서 저장된 grid node를 \(W_j\), 그 node의 raw count를 \(A_j\)라 하자. source eV를 SI energy로 바꾸는 상수는 \(\epsilon_{\rm eV}=1.602176634\times10^{-19}\ {\rm J/eV}\)이며, \(\mathcal W_j=\epsilon_{\rm eV}W_j\)로 쓴다. 표기상의 eV 좌표와 별도로 상태의 energy 좌표는 SI J로 유지한다.

Raw node measure와 source lower absorber를 분리한 상태는

\[
 y=(\{A_j\},X_H,X_{H^+},X_{He},X_{He^+},N_{e,B},U_B,
                   E_{exc,H},E_{exc,He})\ge0.
 \tag{KA.2}
\]

여기서 \(N_{e,B},U_B\)는 source의 \(W\le W_b\) absorber와 이미 분해되지 않는 thermal bath에 남긴 count/energy이다. \(U_B\)에는 해당 bath의 열적 에너지가 들어간다. Source의 `heat`와 `cutoff_energy`는 각각 감사 가능한 관측 장부로 보존하면서, 물리 상태에는 그 합을 \(U_B\)에 한 번만 더한다. 이미 ion stage count의 chemical energy로 계산한 `binding` 역시 에너지 합에 중복해서 더하지 않는다.

물리적 active cutoff \(E_c^n\)가 \(\epsilon_{\rm eV}W_b\) 이상인 결합에서는 raw \(A_j\)에 thermal-owned retained atoms도 들어갈 수 있다. Collision의 초기 donor mask는

\[
 m_j^n=\mathbf1_{\{\mathcal W_j>E_c^n\}},\qquad
 A_{j,\mathrm{donor}}^n=m_j^n A_j^n.
 \tag{KA.3}
\]

으로 고정한다. Trial endpoint cutoff가 변해도 이 초기 mask나 사건 열을 누적 수정하지 않는다. 매 trial은 같은 collision raw output을 분류한다. 선택된 thermal-owned atoms를 \(\mathcal I_{th}\)라 할 때

\[
 N_{e,th}=N_{e,B}+\sum_{j\in\mathcal I_{th}}A_j,\qquad
 U_{th}=U_B+\sum_{j\in\mathcal I_{th}}\mathcal W_jA_j,
 \tag{KA.4}
\]

이며 \(N_{th}=X_H+X_{H^+}+X_{He}+X_{He^+}+N_{e,th}\)를 EOS에 사용한다. Raw inventory를 유지하는 표현과 aggregate \(U_{th},N_{e,th}\) 표현 사이를 변환할 때 (KA.4)의 atom 기여를 두 번 세지 않는다. 이번 source absorber는 \(W_b\) 아래의 **각 actual energy trace**를 저장하지 않으므로, 그 band를 다시 통과하는 하향 cutoff에는 trace를 추가 보존하거나 cutoff domain을 제한해야 한다. 원래 source semantics를 보존한 이번 adapter는 그 조건을 인터페이스에 남긴다.

## 3. 기존 projector의 양의 count–energy 분해

한 daughter energy \(w\)에 대해 count projector \(P_N(w)=(\{b_i(w)\},n_B(w),u_B(w))\)를 정의한다. 이는 SRC-P의 energy-coordinate projector를 count coordinate로 읽은 것이다.

\(0\le w\le W_b\)이면

\[
 b_i(w)=0,\quad n_B(w)=1,\quad u_B(w)=w.
 \tag{KA.5a}
\]

\(W_b<w\le W_{\max}\)이면 \(w\)를 감싸는 두 source nodes \(\ell\le w\le u\)를 잡고

\[
 \beta={w-\ell\over u-\ell},\qquad
 P_N(w)=(1-\beta)P_N(\ell)+\beta P_N(u),\quad0\le\beta\le1.
 \tag{KA.5b}
\]

내부 grid node는 그 node에 한 count를 넣는다. 첫 active node 아래에서는 \(\ell=W_b\)를 ghost absorber로 읽어, \((1-\beta)\) count와 \((1-\beta)W_b\) energy를 base에 넣는다. 따라서 source는 \(W_b<w<W_0\)에서도 작은 ghost fraction을 쓴다. 이는 원래의 first-cell closure다. 이 ghost contribution은 실제 \(w\le W_b\) daughter가 전부 흡수된 경우와 출력 JSON에서 별도로 기록한다.

각 분해의 계수는 비음수이고,

\[
 \sum_i b_i(w)+n_B(w)=1,\qquad
 \sum_iW_i b_i(w)+u_B(w)=w.
 \tag{KA.6}
\]

증명은 내부 cell에서 \((1-\beta)+\beta=1\), \((1-\beta)\ell+\beta u=w\)이고, lower absorber에서는 (KA.5a)를 대입하면 끝난다. 임의의 양의 daughter weights에 선형으로 확장된다. Grid spacing이 \(\Delta_{\min}>0\)이면 한 cell에서 count 계수의 \(\ell^1\) 변화율은 \(2/\Delta\le2/\Delta_{\min}\)이다. 이 bound는 exact rational completion과 원래 float evaluation 사이의 작은 energy-rounding 차이를 비교하는 데에도 쓰인다.

## 4. 실제 full BED에서 양의 quadrature weights

SRC-B의 \(t=E/B>1\), \(w=W/B\), \(u=U/B\), \(y=(1+w)^{-1}\), \(r=(t-w)^{-1}\)에 대해 SDCS는

\[
 {d\sigma\over dW}={S\over B(t+u+1)}
 \left\{K\left[y^2+r^2-{y+r\over t+1}\right]
                  +{\log t\over N}g(w)y\right\}.
 \tag{KA.7}
\]

원래 상수에서 \(K=2-N_i/N>0\)이다. 또 \(y+r=(t+1)yr\)이므로 첫 항의 대괄호는

\[
 y^2+r^2-yr=(y-r)^2+yr>0.
 \tag{KA.8}
\]

HI oscillator는 source의 양의 exponential/rational 식이며 \(w=0\)의 연속 값도 \(128/(3e^4)>0\)이다. HeI에서는

\[
 g(w)=y^3 q(y),\quad q(y)=8.24012-10.4769y+3.96496y^2-0.0445976y^3.
 \tag{KA.9}
\]

\(0<y\le1\)에서 \(q'(y)=-10.4769+7.92992y-0.1337928y^2<0\), \(q(1)=1.6835824>0\)이므로 \(g>0\)이다. 따라서 허용된 slow-electron interval 전체에서 (KA.7)은 양수다.

Total cross section의 source식도

\[
 \sigma(E)={S\over t+u+1}\left[D(t)\log t+
     K\left(1-{1\over t}-{\log t\over t+1}\right)\right]\ge0
 \tag{KA.10}
\]

이다. \(D(t)\)는 \(g(w)/(N(1+w))\)의 양의 적분이다. 나머지 함수 \(H(t)=1-t^{-1}-\log t/(t+1)\)는 \(H(1)=0\),

\[
 H'(t)={t+1+t^2\log t\over t^2(t+1)^2}>0\quad(t>1)
\]

을 만족한다. Threshold 이하에는 source가 rate를 0으로 둔다. 원래 source의 oscillator integral 및 total/SDCS 일치는 채택한 SRC-O 근거를 재사용한다.

Source `_sharing`은 \([0,(E_j-B_a)/2]\)에 기존 grid knots와 reflected knots를 함께 넣고, 각 interval에 order-4 Gauss–Legendre rule을 적용한다. 실제 sampling energies를 \(w_{ja\ell}\), 양의 raw quadrature weight를 \(q_{ja\ell}\)라 하면

\[
 p_{ja\ell}={q_{ja\ell}\over\sum_\nu q_{ja\nu}}>0,\qquad
 \sum_\ell p_{ja\ell}=1.
 \tag{KA.11}
\]

이번 구현은 그 함수를 변경 없이 읽어 사용한다. 이 식은 원래 total rate \(\sigma_a(E_j)\)를 각 공유 사건에 분배하며, 새로운 cross section을 가정하지 않는다.

## 5. Paired fractional ionization event

Species \(a\in\{H,He\}\), parent \(j\), 실제 sharing point \(\ell\)에 대해

\[
 w_1=w_{ja\ell},\qquad w_2=E_j-B_a-w_1
\]

를 같은 사건 안에 둔다. 두 projector를 합쳐 \(b_i=b_i(w_1)+b_i(w_2)\), \(n_B=n_B(w_1)+n_B(w_2)\), \(u_B=u_B(w_1)+u_B(w_2)\)라 쓰면 그 사건 열은

\[
 \Delta A_i=-\delta_{ij}+b_i,\quad
 \Delta X_a=-1,\quad\Delta X_{a^+}=1,\quad
 \Delta N_{e,B}=n_B,\quad\Delta U_B=\epsilon_{\rm eV}u_B.
 \tag{KA.12}
\]

\(X_a^n>0\)인 초기 support에서 실제 trial composition proposal은

\[
 f_{ja\ell}(z;y^n)=m_j^n A_j^n\,
       v_j\sigma_a(E_j)p_{ja\ell}{X_a(z)\over V_*},\qquad
 v_j=\sqrt{2\epsilon_{\rm eV}E_j/m_e}.
 \tag{KA.13}
\]

이 식의 속도는 SRC-P의 비상대론적 prescription을 그대로 쓴다. \(X_a^n=0\) 또는 \(m_j^nA_j^n=0\)인 채널은 그 step에서 비활성이다. 기존 frozen-mass factor \(A_j^nX_a^n/V_*\)를 유지하려면 \(\widehat\kappa(z)=v_j\sigma_a p_{ja\ell}X_a(z)/X_a^n\)로 읽으면 같은 식이다. Trial target를 \(X_a^n\)에 고정한 것은 이 구성의 더 단순한 특수 경우다. \(z=y^n\)에서는 정확히 \(A_j^n n_a^n v_j\sigma_a p_{ja\ell}\)이므로 원래 continuous mass-action rate와 일치한다.

(KA.6)에서 곧바로

\[
 \sum_i\Delta A_i+\Delta N_{e,B}=1,
\quad
 \sum_i\epsilon_{\rm eV}W_i\Delta A_i+\Delta U_B+\epsilon_{\rm eV}B_a\Delta X_{a^+}=0
 \tag{KA.14}
\]

가 따른다. 핵종 수는 \(\Delta X_a+\Delta X_{a^+}=0\)이고, ion charge가 1 늘면서 자유전자도 1 늘므로 전하가 보존된다. 두 daughter를 합친 열의 계수는 fractional counts일 수 있다. 이것은 mean-measure deterministic event이며, 정수-valued Monte Carlo collision을 주장하는 것이 아니다. 두 daughter를 따로 독립적인 grid outcome으로 추첨하는 분해를 사용하지 않으므로 각 사건 열이 에너지 관계를 유지한다.

## 6. 실제 CCC excitation과 stopping 사건

SRC-C의 excitation 채널 \(c\)는 native zero marker를 effective energy loss \(C_c>0\)로 쓴다. Native sigma를 HI의 \(a_0^2\)이면 \(a_0^2\), HeI의 \({\rm cm}^2\)이면 \(10^{-4}\)를 곱해 \({\rm m}^2\)로 변환하고 piecewise-linear interpolation을 적용한다. 표본 sigma가 비음수이므로 interpolated sigma도 비음수이다. Lower marker 아래는 0이고, 선정 domain은 마지막 tabulated energy 이하다.

Excitation의 한 사건은

\[
 \Delta A_i=-\delta_{ij}+b_i(E_j-C_c),\quad
 \Delta N_{e,B}=n_B(E_j-C_c),\quad
 \Delta U_B=\epsilon_{\rm eV}u_B(E_j-C_c),\quad
 \Delta E_{exc,a}=\epsilon_{\rm eV}C_c.
 \tag{KA.15}
\]

핵종·ion stage count는 그대로이며 proposal은 (KA.13)에서 \(\sigma_ap_{ja\ell}\)를 \(\sigma_c\)로 바꾼다. Neutral target는 rate의 co-reactant이고, 이 effective excitation/radiation closure에서 그 neutral count의 **net increment**는 0이다. 따라서 capacity matrix에 가상의 neutral depletion을 추가하지 않는다. \(\Delta N_{free}=0\)이고 \(\Delta E_{kin}+\Delta U_B+\Delta E_{exc}=0\)이다. 이번에 직접 평가한 effective cost는 HI 1S→2P의 10.20435 eV와 HeI s1S→t2S의 19.7179 eV다. 이는 source가 채택한 truncated model cost라는 의미를 보존한다. 별도의 정확한 spectroscopic transition energy 또는 excited population kinetics로 확대 해석하지 않는다.

Stopping은 \(E_{j-1}\)를 이전 node, 첫 node에서는 \(E_{-1}=W_b\)로 두고

\[
 \Delta A_i=-\delta_{ij}+b_i(E_{j-1}),\quad
 \Delta N_{e,B}=n_B(E_{j-1}),\quad
 \Delta U_B=\epsilon_{\rm eV}\{u_B(E_{j-1})+E_j-E_{j-1}\},
 \tag{KA.16}
\]

\[
 f_j^{stop}(z;y^n)=m_j^nA_j^n\lambda_j(n_e(z)),\qquad
 \lambda_j(n_e)={b(E_j,n_e)\over E_j-E_{j-1}}.
 \tag{KA.17}
\]

로 정한다. 내부 node에서는 한 active electron이 이전 node로 가고 차이만 heat가 된다. 첫 node에서는 한 thermal electron을 추가하고 총 \(\epsilon_{\rm eV}E_0\)를 \(U_B\)에 넣는다. 그중 \(\epsilon_{\rm eV}W_b\)는 source cutoff-energy 장부, 나머지는 source heat 장부라는 분해가 그대로 남는다. Count와 에너지 보존은 (KA.6)을 대입하면 각각 0이다.

## 7. 원래 generator와의 일치

원래 SRC-P는 active energy-density coordinate \(u_j=E_jA_j/V_*\)와 energy/number observers에 행렬 \(G\)를 작용시키며, 저장한 \(G\)에는 \(T_{END}\) factor가 들어간다. Physical generator는 \(G/T_{END}\)다. 고정 원래 bath로 (KA.13), (KA.17)을 평가하고 모든 sharing events를 더하면

\[
 {dA_i\over dt}=\sum_r S_{ir} f_r,\qquad
 {du_i\over dt}={E_i\over V_*}\sum_r S_{ir} f_r.
 \tag{KA.18}
\]

Parent energy-coordinate 한 단위에 해당하는 count는 \(V_*/E_j\)이므로 source column은 정확히 \(-\lambda_j\)와 \(\lambda_j P_E/E_j\) 형식을 얻는다. Ionization의 binding observer에는 \(\lambda_aB_a/E_j\), ionization-number observer에는 \(\lambda_a/E_j\), excitation observer에는 \(\lambda_cC_c/E_j\), stopping heat에는 \(\lambda_j(E_j-E_{j-1})/E_j\)가 들어간다. 이는 SRC-P `_generator`의 실제 조립식 각각과 일치한다. 원래 `low_cross_energy/number`는 이미 센 성분의 겹치는 관측량이므로 독립 보존 energy에 더하지 않는다.

따라서 이 adapter는 선택된 원래 discrete collision generator를 count·species·thermal 상태의 공통 사건 표현으로 확장한다. 원래 고정 bath를 회복하면 그 active/observer operator가 돌아오고, trial composition을 켜면 같은 사건 열에 nonlinear rate가 연결된다.

## 8. 실제 stopping feedback와 rate derivative bound

Source의 Coulomb 상수는 \(\mathcal K=e^2/(4\pi\epsilon_0)\)이며 \(e=1.602176634\times10^{-19}\ {\rm C}\)는 elementary charge이다. Energy-conversion 상수 \(\epsilon_{\rm eV}\)와 \(e\)의 SI 수치가 같지만 차원을 구별한다. Fixed \(E_j,v_j\)에 대해

\[
 \omega_p(n)=\sqrt{ne^2/(\epsilon_0m_e)},\quad
 L_j(n)=\min\left\{
 \log{v_jE_j\epsilon_{\rm eV}\over\mathcal K\omega_p(n)},
 \log{2E_j\epsilon_{\rm eV}\over\hbar\omega_p(n)}+q
 \right\},\quad q\in\{0,-\tfrac12\}.
 \tag{KA.19}
\]

실제 baseline의 \(q=0\)을 이번 witness에 사용한다. 두 log에 같은 \(-\frac12\log n\)이 들어가므로 fixed \(E_j\)에서 어느 branch가 작은지는 density에 의존하지 않는다. \(n_0=n_{e,0}\)로 두면

\[
 L_j(n)=L_j(n_0)-\tfrac12\log(n/n_0),\quad
 b_j(n)=\alpha_jnL_j(n),\quad
 \alpha_j={4\pi\mathcal K^2\over m_ev_j\epsilon_{\rm eV}}.
 \tag{KA.20}
\]

따라서

\[
 b'_j(n)=\alpha_j(L_j(n)-\tfrac12),\qquad
 b''_j(n)=-{\alpha_j\over2n}.
 \tag{KA.21}
\]

정의역 \(0<n_{min}\le n\le n_{max}\), \(L_j(n_{max})>0\)에서

\[
 M_j=\sup|\lambda'_j(n)|
 ={\alpha_j\over E_j-E_{j-1}}
 \max\{|L_j(n_{min})-\tfrac12|,|L_j(n_{max})-\tfrac12|\}
 \tag{KA.22}
\]

가 유한하다. Density continuation은

\[
 n_e(z)={N_{e,th}(z)\over V_*},\qquad
 L_{f_j^{stop}}\le m_j^n A_j^n M_j {L_{N_{e,th}}\over V_*}.
 \tag{KA.23}
\]

로 이전 FB Lipschitz contract에 들어간다. \(\|\delta z\|_{\infty,a}=\max_i|\delta z_i|/a_i\)에서 atomic proposal의 bound는

\[
 L_{f_{ja\ell}}={m_j^n A_j^n v_j\sigma_a(E_j)p_{ja\ell}\over V_*}a_{X_a},
 \quad
 L_{f_{jc}}={m_j^n A_j^n v_j\sigma_c(E_j)\over V_*}a_{X_a}.
 \tag{KA.24}
\]

이들은 target count에 선형이므로 이 bound는 직접적이다. 선택된 source에서는 fixed energy의 total/SDCS/CCC coefficient에 직접적인 \(T\) 의존이 없고, stopping도 thermal bath density 외에 \(T\)를 인자로 쓰지 않는다. 따라서 fixed \(E\), fixed target/electron density에서 \(\partial_T\kappa=0\)이다. Trial cutoff가 thermal ownership을 바꾸는 경우의 온도 간접 효과는 \(N_{e,th}(z)\)를 통해 (KA.23)에 들어간다. Atom branch가 고정된 곳은 이 count가 선형 함수이며, branch jump나 smooth spectral reconstruction에 관한 bound는 cutoff 분과의 contract를 사용한다.

원래 cold-target 모형의 유효범위는 active \(\mathcal W_j\gg k_BT\), positive Coulomb log, dilute targets, 선정된 0.1–900 eV domain 및 원래 excitation closure를 포함한다. \(W_b/(k_BT_0/\epsilon_{\rm eV})\simeq11.60\)이다. Cutoff 존재 정리의 \(\chi\ge3/2\) 조건은 cold-target 근사의 정량적 정확도 조건을 대신하지 않는다. Finite-temperature Coulomb diffusion, all-free-electron screening 또는 thermal cross-section average를 원하면 별도로 rate closure를 유도한다.

## 9. 기존 shared-capacity map에 그대로 연결

각 사건 열을 모아 \(S\), \(C_{ir}=\max(-S_{ir},0)\), base stock \(y^n\)을 둔다. 초기 zero donor를 요구하는 채널은 끄고, 같은 trial \(z\)에서

\[
 c_i(z)=\sum_r C_{ir}f_r(z),\quad
 d_r(z)=\sum_{i:C_{ir}>0}{c_i(z)\over y_i^n},\quad
 \xi_r(z)={h f_r(z)\over1+h d_r(z)},\quad
 \mathcal F(z)=y^n+S\xi(z)
 \tag{KA.25}
\]

를 적용한다. 각 donor \(i\)에 대해 \(d_r\ge c_i/y_i^n\)인 같은 분모를 쓰므로

\[
 \sum_rC_{ir}\xi_r\le {h c_i\over1+h c_i/y_i^n},\qquad
 (\mathcal F(z))_i\ge{y_i^n\over1+h c_i/y_i^n}\ge0.
 \tag{KA.26}
\]

원래 ion target depletion, active parent depletion, thermal/chemical/observer increments는 한 \(\xi_r\)를 공유한다. 서로 다른 coordinate를 별도로 보정하지 않는다.

이번 family의 선형 invariant는

\[
 \begin{aligned}
 H_{tot}&=X_H+X_{H^+},\\
 He_{tot}&=X_{He}+X_{He^+},\\
 Q/e&=X_{H^+}+X_{He^+}-N_{e,B}-\sum_jA_j,\\
 E_{tot}&=\sum_j\mathcal W_jA_j+U_B+\epsilon_{\rm eV}B_HX_{H^+}
                     +\epsilon_{\rm eV}B_{He}X_{He^+}+E_{exc,H}+E_{exc,He}.
 \end{aligned}\tag{KA.27}
\]

앞 절의 사건별 등식으로 각 row \(\ell\)가 \(\ell^TS=0\)이므로, 모든 \(h\ge0\)와 trial \(z\)에서 \(\ell^T\mathcal F(z)=\ell^Ty^n\)이다. Thermal repartition도 (KA.4)로 동일 raw count·energy를 옮기므로 이 invariant를 유지한다. \(N_{th}>0\), \(U_{th}\ge0\)이면 \(T=2U_{th}/(3k_BN_{th})\)가 비음수 EOS를 준다. 온도 양수성 \(T>0\)에는 \(U_{th}>0\)가 필요하다. Stopping/ionization/source excitation events는 base thermal energy를 감소시키지 않는다.

Rate bound (KA.23)–(KA.24)를 FB의 \(L_c,L_d,L_\xi\) 식에 넣으면 그대로

\[
 L_{c_i}=\sum_r C_{ir}L_{f_r},\quad
 L_{d_r}=\sum_{i:C_{ir}>0}{L_{c_i}\over y_i^n},\quad
 L_{\xi_r}\le hL_{f_r}+h^2 F_rL_{d_r},\quad
 q_{FP}=\max_i{\sum_r|S_{ir}|L_{\xi_r}\over a_i}
 \tag{KA.28}
\]

를 얻는다. 지정된 invariant domain 안에서 \(q_{FP}<1\)이면 FB의 고정점 유일성·Picard 수렴·residual error bound가 적용된다. 각 proposal이 \(f(y^n;y^n)=R(y^n)\)이고 branch별로 locally Lipschitz이면 \(\xi=hf(y^n)+O(h^2)\), \(y^{n+1}=y^n+hSR(y^n)+O(h^2)\)이므로 사건 분해가 기존 first-order consistency를 보존한다. 강한 positivity는 큰 \(h\)에서도 성립하지만, 그 사실만으로 큰 시간 간격의 정확도를 주장하지 않는다.

**실제 sharing distribution의 보존.** 저장된 전체 grid의 최대 gap은 0.6325633326908928 eV로, 최소 ion binding 13.6057 eV보다 작다. 따라서 두 ion daughter 모두 \(w\le E_j-B_a<E_{j-1}\)이며, 그 projector의 active support는 parent node를 포함하지 않는다. 모든 \((j,a,\ell)\) 사건의 negative increments는 정확히 \(A_j\)와 \(X_a\)의 각 1이다. 그러므로 capacity denominator는 같은 \((j,a)\) 안에서 \(\ell\)에 의존하지 않아

\[
 \xi_{ja\ell}=p_{ja\ell}\,\Xi_{ja},\qquad
 \Xi_{ja}={h\,m_j^n A_j^n v_j\sigma_a(E_j)X_a(z)/V_*
  \over1+h\{c_{A_j}(z)/A_j^n+c_{X_a}(z)/X_a^n\}}.
 \tag{KA.29}
\]

가 성립한다. Active positive support에서 읽는 이 식은 큰 \(h\)에서도 각 ionization family의 실제 daughter sharing probability를 유지한다. Total family extent가 공통 capacity에 맞게 줄어든다. 다른 target species 및 다른 parent family 사이의 상대 extent에는 각각의 shared stock 조건이 반영된다. 최소 CCC effective cost 10.20435 eV도 최대 grid gap보다 크므로 excitation daughters 역시 parent node에 재투영되지 않는다.

## 10. 실제 새 계산과 검증 결과

`kernel_event_adapter.py`는 11개 input hash를 확인하고 실제 saved array를 읽은 뒤, SRC-P/SRC-B에서 필요한 함수·class AST만 변경 없이 실행한다. Module-level 전체 atomic loading, source evaluation, `_generator`, matrix exponential, ODE, NCP를 호출하지 않는다. 실제 선택한 node/채널에서 원래 sharing와 projector를 평가하고, 새 exact event construction을 비교했다.

| 새 평가 대상 | 실제 parent energy (eV) | sharing points / 사건 역할 |
|---|---:|---:|
| HI threshold 바로 위 | 13.606407443000693 | 4 |
| HI 중간 node | 30.00976971818039 | 15620 |
| HeI threshold 바로 위 | 24.595094858493628 | 4 |
| HeI 중간 node | 30.00976971818039 | 6888 |
| HI 1S→2P | 10.205990538235602, 30.00976971818039 | 실제 table 두 점 |
| HeI s1S→t2S | 19.722795822410312, 30.00976971818039 | 실제 table 두 점 |
| stopping | 0.10309375000000001, 10, 30.00976971818039 | 세 실제 grid edge |

위 네 ionization component에서 source-projected daughter count residual은 0이고, 에너지 상대 residual의 최대 절댓값은 \(1.19\times10^{-16}\)이다. 실제 sharing weights는 모두 양수다. 각 component의 first/last 및 source ghost band의 실제 quadrature sample을 고른 exact witnesses, CCC 사건 및 stopping을 합한 **17개 사건 열**에서 (KA.27)의 네 invariant residual은 Fraction arithmetic으로 모두 정확히 0이다.

Reference의 exact layer는 saved float inputs를 binary rational로 읽고, fast daughter를 \(E-B-w_1\)로 정확히 완성하며, barycentric weights 및 sharing probability의 합을 exact arithmetic으로 계산한다. 원래 floating projection과의 최대 scale-normalized 차이는 \(8.42\times10^{-14}\)이다. 이 차이는 고정된 grid interpolation의 rounding sensitivity와 일치하며, floating generator를 bitwise identical rational matrix라고 주장하지 않는다. Exact 사건 장부와 원래 floating implementation과의 수치 일치는 각각 별도 근거로 기록한다.

이 중 **7-event 실제 sparse subfamily**에 기존 `inputs/prior/event_capacity_step.py`를 byte 그대로 사용했다. 초기 상태는 이번 검증용으로 구성한 neutral 상태이며 저장된 historical spectrum이 아니다. \(h=10^{14}\,s\)에서 최대 raw donor load \(hc_i/y_i^n\)는 \(3.065250663\times10^7\)이었다. 결과는 모두 비음수이고, 네 invariant 변화는 정확히 0이며, 초기 양의 stock 대비 최소 retained fraction은 0.0281752였다. EOS temperature는 100 K에서 103.81591145887886 K로 계산되었다. 이 수치는 **양수성·장부 보존 stress witness의 EOS 값**이며, 그 거대한 step의 실제 시간 정확도 또는 BASS_CR 상태 예측으로 해석하지 않는다.

초기 cutoff를 20 eV로 둔 별도 proposal 확인에서는 13 eV parent의 donor rate가 0이다. Trial target count를 절반으로 바꾸면 실제 atomic proposal이 정확히 절반으로 바뀐다. 원래 bath density에서 새 stopping continuation과 원래 `stopping_eV_s`의 차이는 상대 \(2.19\times10^{-16}\) 이하이다. 세 stopping node에서 \([n_{e,0}/2,2n_{e,0}]\)의 log minimum은 모두 양수이며, (KA.22)의 finite derivative bound를 JSON으로 남겼다.

결과의 exact values, source parity, sparse final raw \(\{A_j,W_j\}\), actual subcut count/energy와 ghost contributions는 각각 `results/KERNEL_ADAPTER_CHECKS.json`, `examples/ACTUAL_KERNEL_EVENT_COLUMNS.json`에 있다. 이번 check는 새 adapter 의무를 대상으로 하며, 유지된 atomic source 검증이나 이전 full physics suite를 재실행하지 않았다.

KA.29의 강화 결과에는 별도의 `checks/check_sharing_capacity.py`와 `results/SHARING_CAPACITY_CHECKS.json`을 두었다. 이 실행은 actual HI 30.00976971818039 eV family의 source quadrature indices 0, 38, 15619 세 점에서 negative donor columns가 같고 \(\xi_\ell/p_\ell\)가 정확히 같은 값을 갖는지 확인했다. 실제 실행 UTC와 source/runtime hashes는 그 결과에 저장되어 있다. 초기 adapter runner가 UTC를 포착하지 않은 retained execution의 시간은 추정하지 않고, `results/KERNEL_ADAPTER_EXECUTION.json`에 unknown으로 두고 당시와 동일한 현재 source hashes 및 실제 exit status를 결속했다.

## 11. 닫힌 의무와 다음 연결

이번 구성으로 실제 saved-grid/kernel identity, 양의 paired daughter columns, threshold/binding/excitation/heat/count 보존, source generator의 count-coordinate 동치, thermal-bath density continuation, 그 derivative bounds, unchanged capacity-map 연결이 닫혔다. 사건 열은 현재 collision reference의 actual energy와 target threshold를 사용한다.

Root의 cutoff adapter에는 raw node measure, base thermal state, species·excitation reservoirs, 초기 active donor mask를 전달한다. Trial cutoff가 raw measure를 분류한 뒤 endpoint thermal electron density와 EOS를 반환하면 (KA.13), (KA.17)의 coefficients가 갱신된다. Thermal ownership history를 보존하는 방법, global atom-branch 선택 또는 smooth reconstruction, covariant geometry 이후 현재 actual energies에 대한 재결속은 해당 분과의 계약에 따른다. Redshift 후에도 illustrative source energy ratios를 그대로 쓰지 않는다.

실제 source가 제공하지 않는 finite-temperature rates, further HeII ionization/recombination, cutoff 아래 trace의 역분류 및 27개 excitation raw tables 전체를 포함한 production kernel generation은 각각 다음 구체적 adapter 의무로 남는다. 이 문서의 27-channel algebra는 동일한 positive-table/effective-cost 조건으로 적용되며, 이번 새 numerical witnesses의 직접 평가 범위는 두 원본 table이다.
