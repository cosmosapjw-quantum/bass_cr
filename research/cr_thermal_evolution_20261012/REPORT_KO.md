# BASS_CR 다음 이론 루프: 완료 결과와 근거

이번 루프는 고정 bath의 전자 source와 cutoff 편입 결과를 출발점으로,
**시간에 따라 변하는 배경에서 열적·비열적 전자의 수와 에너지를 함께 진화시키는 연결**을 완성했다.
핵심 결과는 이동 경계의 보존 법칙, 모든 자유전자를 세는 표현의 초과에너지 상태,
기존 충돌 응답의 시간 변환, 실제 Coulomb 로그의 밀도 보정, 그리고 그 오차를 온도로 옮기는 정리다.
독립 검토에서 지적한 정의·SI 단위·최적 clock의 제약 조건을 반영했다.

## 이번에 닫은 질문

| 열린 연결 | 이번의 완결된 구성 |
|---|---|
| 고정 cutoff를 진화 배경에 연결 | 상대 경계속도에 따른 signed 수·에너지·운동량 flux와 양쪽 상쇄 |
| total electrons와 thermal electrons의 EOS 연결 | $u_{\rm ex}=u_A-\frac32k_BTn_A$ 및 pressure reference로 정확한 변수변환 |
| 고정 collision response의 시간 재사용 | $X=Vx$, $\tau=\int a\,dt$, source $Vs/a$, heat rate의 $a/V$ 변환 |
| 실제 코드의 밀도 변화 | $G(d)=dG(1)-\frac12d\log d\,C_0$ |
| 변하는 연산자의 효과를 계산 | 양의 energy norm에서 Duhamel state·누적 heat 상계 |
| energy error를 temperature error로 전달 | 팽창 integrating factor와 양의 thermal count를 사용한 endpoint 상계 |
| 사용할 clock의 선택 | 명시한 반응률 residual 상계를 최소화하는 weighted median |

모든 결과는 본문에 명시한 kinetic/thermal closure와 유한 연산자의 조건 아래에서 진술한다.
이 연구 단위는 일반적인 변수변환·보존 법칙·Duhamel 방법을 실제 BASS_CR source와 출력 단위에
연결한 구성이다. 우주론 전체 이력에 채택하는 단계는 선택할 scenario와 receiver에 연결된다.

## 출발점과 재사용한 근거

출발 branch는 이전 source-binding 결과이며 최종 commit은
0e706a7ce2fb, science commit은 5fc11143679f다.
해당 source archive를 복원하고 SHA-256 및 내부 177개 파일의 hash를 확인했다.
그 안의 고정 bath source, 원 cascade 코드, cutoff 수·에너지 장부와 독립 판정을 재사용했다.
기존의 완료된 수치 suite와 transport는 재실행하지 않았다.

직전 결과의 물리적 기준은 $Q_e(W,t)=tA(W)$, $T_0=10^{10}$ s,
$T_g=100$ K, $n_H=140$ m$^{-3}$,
$Y_{\rm He}=0.248$, $x_{\rm HII}=x_{\rm HeII}=0.01$이다.
선택된 전자 birth 창은 $0.1$–$900$ eV, proton collision 창은 $1$–$4$ MeV다.
고정된 실제 fullBED source에 대한 저장 진폭과 열적 편입 진단은 다음과 같다.

| 재사용 항목 | 값 |
|---|---:|
| $q_*$ | $1.8012625784277353\times10^{-42}$ J m$^{-3}$ s$^{-1}$ |
| $P_h(T_0)$ | $3.4427310257273833\times10^{-44}$ J m$^{-3}$ s$^{-1}$ |
| $\mathcal E_h(T_0)$ | $1.1921620918578547\times10^{-34}$ J m$^{-3}$ |
| cutoff 수 증가 $N_c$ | $1.8382904526169294\times10^{-16}$ m$^{-3}$ |
| prescribed cutoff 편입의 $\Delta T$ | $3.8418834731514848\times10^{-14}$ K |

이 수치들은 이전 고정 배경의 기록이다.
이번에는 그 연결식의 가정과 단위를 명시한 채 진화 배경의 방정식을 유도한다.
수·에너지·stress 모멘트의 배경 문헌은 Sarbach–Zannias와 Lee–Nungesser를 확인했다.\cite{sz,ln}
양의 행렬과 variation of constants의 추정은 본문에서 직접 증명하며,
logarithmic norm의 문헌은 방법의 배경으로만 사용한다.\cite{soderlind}

## 주요 가정의 역할

| 조건 | 필요한 이유 |
|---|---|
| prescribed Bianchi I comoving cell, 순 momentum 0 | 공간 flux를 생략하면서 비등방 pressure work를 보존 |
| thermal nuclei와 electrons의 공통 비상대론적 온도 | $u_{\rm th}=\frac32k_BTn_{\rm th}$와 $p_{\rm th}=\frac23u_{\rm th}$ |
| active 분포 또는 같은 의미의 유한 energy state | $n_A,u_A,\Pi_A$와 경계 trace를 명시적으로 계산 |
| source·jump·cutoff의 공통 수·에너지 장부 | 실제 daughter energy를 한 번씩 전달 |
| 공통 collision factor 또는 명시한 operator residual | 정확 clock 재사용과 오차 certificate를 구별 |
| positive energy weights와 column inequality | 누적 energy/heat 상계 |
| 같은 expansion history와 $N_{\min}>0$ | thermal energy에서 온도 오차로 가는 안정적인 inversion |

다음 절의 moving-cutoff와 thermal-excess 유도는 물리 부피 $V_{\rm abs}$를 사용한다.
collision-clock 절에서는 $V=V_{\rm abs}/V_{\rm abs}(t_i)$인 상대 부피로 정규화한다.
두 표현의 parcel energy는 초기 부피를 곱하거나 나누어 일치시킨다.
threshold $E_c(t)$ 또는 $W_c(t)$와 누적 편입 에너지 $\mathcal E_{\rm join}$도 구별한다.

# 새 검산과 독립 검토

## 실제로 실행한 판별 계산

검산은 유도에서 생긴 구체적 부호·단위·변수변환 위험을 대상으로 제한했다.

| 방법 | 결과와 의미 |
|---|---|
| 정확 유리수 보존·EOS 예제와 작은 진화 문제 | 15/15 통과 |
| 두 단계 cascade의 정확 기호 대수 | Wolfram Language 21/21 통과 |
| 원 stopping 식의 밀도 보정 | 5 energies × 3 densities × 2 prescriptions, 30개 coefficient |
| 비가환 two-channel evolution | dimensionless 8-state IVP 1회 |
| 별도 검토자의 해석적 검토 | 세 분과와 온도 certificate의 proof·단위·source 대응 확인 |

원 stopping 함수와 $dB_0-\frac12d\log d\,\kappa$의 최대 상대 차는
$2.69\times10^{-16}$였다.
이는 검산한 부동소수점 coefficient identity의 일치이며 원자 물리 모형의 오차 추정은 아니다.

비가환 판별 예제는 $d=e^{-t}$, $V=e^t$, $\tau=1-e^{-t}$를 사용했다.
exact reference clock 해와 별도 DOP853 적분 사이의 최대 절대 차는
$1.12\times10^{-12}$였다.
$t=1$에서 active energy state와 누적 heat의 오차 합은 0.0699155,
증명으로 얻은 상계는 0.2642411이다.
그 누적 certificate를 팽창 energy 식과 EOS로 옮긴 온도 오차는
0.00524825, 상계는 0.1611407이다.
이 표와 그림의 숫자는 일관된 무차원 예제로서 식을 판별한다.

![비가환 두 채널의 새 판별 예제. 왼쪽은 state와 누적 heat 오차, 오른쪽은 팽창 후 thermal temperature 오차다. 실선은 저장된 수치 결과, 점선은 증명에서 계산한 상계다.](../figures/theory_certificates.pdf)

column 최대값과 입력 energy envelope를 사용한 상계에는 여유가 있다.
observable별로 더 작은 상계가 필요하면 이미 유도한 Duhamel 잔차의
$\Delta\widehat X$ 또는 output sensitivity를 사용하면 된다.
이는 더 필요한 입력과 직접 연결되는 개선 경로다.

## 독립 검토에서 수정한 사항

검토자는 후보 유도와 root의 계산을 작성하지 않은 별도 분과로 두었다.
moving boundary에는 Heaviside 분포 미분, all-free에는 exact inverse substitution,
잔차에는 positive propagator와 Duhamel 식, clock 선택에는 convex subgradient를 사용했다.
수정된 항목은 다음과 같다.

1. $P_h$의 정의를 continuous stopping과 선언한 직접 jump heat의 합으로 통일하고,
   전체 medium debit에서 chemical/excitation 항을 분리했다.
2. SI energy state를 입력으로 받는 number row에
   $1/(T_0\epsilon_{\rm eV})$를 명시했다. 전체 mixed state에는 대각 similarity transform을 썼다.
3. weighted median을 양의 허용 clock 구간으로 projection하고,
   source shape의 비음 조건과 zero-weight 경우를 명시했다.
4. 저장 cutoff 총량에 포함된 source ghost를 한 번만 사용하는 대응식을 유지했다.

# 식에서 코드로 옮긴 결과

작은 receiver 모듈은 순수 Python으로 작성했으며,
정확한 유리수 입력을 float로 강제 변환하지 않는다.
기본 $k_B$는 정확한 SI 값이다.

| 함수 | 입력과 역할 |
|---|---|
| thermal_transfer_tdot | thermal 수·energy 전달과 expansion으로 $\dot T$ 계산 |
| total_moment_tdot | total source와 active 모멘트에서 동일한 thermal 식을 구성 |
| advance_thermal_packet | 적분된 comoving 수·energy를 더하고 EOS inversion |
| temperature_error_bound | endpoint energy·number certificate를 온도 상계로 전달 |

source와 전달률을 같은 시각·부피·단위로 입력하도록 docstring에 정의했다.
positive thermal count, physical endpoint energy, finite inputs를 확인한다.
실제 time integrator에 연결할 때는 수·energy·pressure work를 같은 step의 적분량으로 공급한다.

# 이론 루프의 판정과 이어갈 연구

이번 R1–R10은 근거 복원, 가정 정리, 후보식 구성, 실제 유도,
독립 검토, 판별 계산, 결과 판정, 코드 인터페이스와 원고, 다음 DAG까지 진행했다.
명시한 조건의 보존식·변수변환·잔차 정리는 이번 연구의 완료 결과다.

다음 이론 루프의 중심은 **온도와 이온화 조성이 collision coefficients에 되먹임되는 계를
양수성과 수·energy 보존을 유지하면서 한 step으로 연결하는 구성**이다.
현재 결과를 그대로 사용하면 작업 순서는 구체적이다.

1. 고정된 반응별 energy-transfer 행렬에
   $n_e(t)$, $n_{\rm HI}(t)$, $n_{\rm HeI}(t)$와 thermal variables의 coefficient를 결합한다.
2. active state, chemical count, thermal energy를 함께 갱신하는 conservative positive step을 구성한다.
3. 현재 Coulomb residual과 source mismatch를 사용해 step 안의 coefficient 변화 오차를 제한한다.
4. fixed cutoff에서 시작하고, 필요한 경우 이번 signed interface와 하부 trace로 moving cutoff를 결합한다.
5. 선택된 실제 scenario에는 initial stock, source history, background와 원하는 observable budget를 입력한다.

현재 실제 응용의 scenario·receiver 채택 노드와 원래의 전역 연구 상태는 각각 보존했다.
DAG에는 이번에 완료한 이론 노드와 그것을 사용하는 다음 구성을 추가했다.
새 NCP 작업이나 대규모 원자·transport 계산은 이 연구 단위에 필요하지 않았다.

# 출처와 재현 자료

직전 DERIVATION_KO.md §4, §6.1–§6.4와
SOURCE_BOUND_RESPONSE.json을 inputs/prior에 포함했다.
원 causal_cascade.py는 source identity를 유지하여 inputs/prior_code에 보관했다.
세 유도문, 검산 코드·기호 스크립트·실행 결과, independent review,
CONTRACT, NEXT_DAG와 PLAN을 같은 묶음에 제공한다.

전체 계산은 checks/run_theory_checks.py로 재현할 수 있다.
이 명령은 이번의 15개 focused checks와 작은 IVP만 수행한다.
Wolfram의 정확한 두 단계 예제는 checks/verify_analytic_case.wl에 따로 제공한다.
PDF는 LaTeX 원고와 포함한 font·figure로 다시 컴파일할 수 있다.

\begin{thebibliography}{9}
\bibitem{prior}
BASS\_CR, \emph{실제 전자 birth source와 M0 응답의 정규화 결속},
CR-RUX-M1B-SOURCE-BINDING-20261012, science commit 5fc11143679f.
보존 원문과 결과: 이 묶음의 inputs/prior.
\bibitem{cascade}
BASS\_CR, \emph{causal\_cascade.py}, CR-PHYS02B.
SHA-256 d87a9cc12212\ldots f39313c7b72.
stopping, project, generator와 moment functionals.
\bibitem{sz}
O. Sarbach and T. Zannias,
\emph{Relativistic Kinetic Theory: An Introduction} (2013).
\url{https://arxiv.org/abs/1303.2899}.
Proposition 6, Eqs. (62)–(63), collision moment Eq. (76).
\bibitem{ln}
H. Lee and E. Nungesser,
\emph{Bianchi I solutions of the Einstein--Boltzmann system with a positive cosmological constant}.
\url{https://arxiv.org/abs/1705.07009}.
직교기저 §1.1, Bianchi I의 kinetic moments §3.
\bibitem{soderlind}
G. Söderlind,
\emph{The logarithmic norm. History and modern theory},
BIT Numerical Mathematics 46, 631--652 (2006).
\url{https://doi.org/10.1007/s10543-006-0069-9}.
서지·abstract를 확인한 방법론 배경이며 본문의 inequality는 직접 증명했다.
\end{thebibliography}

