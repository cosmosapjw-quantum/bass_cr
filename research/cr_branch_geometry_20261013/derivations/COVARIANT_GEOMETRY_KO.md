# 질량 있는 전자의 prescribed Bianchi 에너지 이동

## 결과와 물리 convention

Signature는 $(-+++)$, $n^an_a=-1$, $n^a$는 미래 방향의 unit cosmological normal이다. $c,\hbar,k_B$를 1로 놓지 않는다. 아래 classical geodesic 운동식에는 $\hbar$가 나타나지 않고, 원 collision/stopping kernel의 양자 상수 convention은 그대로 유지한다. Geometry는 지정된 배경 입력이고 Einstein 방정식을 이 절에서 풀지 않는다.

전자 질량을 $m_e$, 관측 총에너지를 $E=m_ec^2+W$라 쓰면, 동기화된 geodesic normal의 homogeneous Bianchi 배경에서

$$\frac{dW}{dt}=-\frac{c^2}{E}K_{ab}q^aq^b
=-\frac{W(W+2m_ec^2)}{W+m_ec^2}\left(H+\sigma_{ab}e^ae^b\right).\tag{BG.1}$$

여기서 $q^a$는 normal에 수직인 물리 운동량, $e^a=q^a/|q|$이고 $W>0$에서 두 번째 식을 쓴다. $W=0$에서는 첫 식이 잘 정의되어 drift가 0이다. $K_{ab}=H\gamma_{ab}+\sigma_{ab}$는 단위가 s$^{-1}$인 팽창률 tensor이다. 양의 $H$가 팽창을 뜻하도록 부호를 고정하며, 다른 ADM extrinsic-curvature 부호 관례를 그대로 대입하지 않는다.

## 1. 공변 유도

공간 projector와 momentum 분해를

$$\gamma_{ab}=g_{ab}+n_an_b,\qquad p^a=\frac Ec n^a+q^a,\qquad n_aq^a=0,\qquad E=-cn_ap^a\tag{BG.2}$$

로 정의한다. 질량껍질 $p^ap_a=-m_e^2c^2$에서

$$c^2q^aq_a=E^2-m_e^2c^4=W(W+2m_ec^2).\tag{BG.3}$$

Geodesic $p^a\nabla_ap^b=0$와 product rule을 사용하면

$$p^a\nabla_aE=-c p^ap^b\nabla_an_b.\tag{BG.4}$$

동기화된 cosmological proper time $t$는 $\nabla_at=-n_a/c$이므로 $p^a\nabla_at=E/c^2$다. 따라서

$$\frac{dE}{dt}=-\frac{c^3}{E}p^ap^b\nabla_an_b.\tag{BG.5}$$

일반 observer normal에 대한 분해를 잠시 쓰면

$$\nabla_an_b=-n_a a_b+\frac1cK_{ab},\qquad n^aa_a=0,\quad n^aK_{ab}=0\tag{BG.6}$$

이며 $a_b=n^a\nabla_an_b$의 단위는 m$^{-1}$다. Vorticity가 없는 normal을 전제로 썼다. 같은 contraction은 local observer clock $dt_{\rm obs}=-n_a dx^a/c$에 대해

$$\frac{dE}{dt_{\rm obs}}=-c^2 a_bq^b-\frac{c^2}{E}K_{ab}q^aq^b\tag{BG.7}$$

를 준다. Accelerated observer에서는 이 local clock을 전역 cosmological time의 gradient라고 가정하지 않는다. 본 연구의 synchronous homogeneous Bianchi normal에서는 $a_b=0$이고 $K_{ab}=c\nabla_an_b$여서 BG.5–7이 BG.1의 첫 식으로 줄어든다. $K=H\gamma+\sigma$와 BG.3을 대입하면 두 번째 식을 얻는다.

삼차원 frame 회전의 반대칭 계수 $\Omega_{ab}$는 $\Omega_{ab}q^aq^b=0$이므로 scalar work를 직접 만들지 않는다. 일반 Bianchi 유형의 구조상수와 frame transport는 $q^a$의 방향 변화에 관여한다. 따라서 BG.1의 순간 scalar 법칙만으로 모든 Bianchi 유형의 방향 경로까지 얻었다고 주장하지 않는다.

## 2. 비상대론 극한과 질량 없는 극한

$R=m_ec^2$로 쓰면

$$\frac{W(W+2R)}{W+R}=2W-\frac{W^2}{W+R}.\tag{BG.8}$$

$W/R\ll1$일 때 $\dot W=-2W(H+\sigma ee)+O(W^2|H+\sigma ee|/R)$다. 고정된 방향 rate에 대해 leading nonrelativistic work와 exact work의 차이는 정확히 $W^2|H+\sigma ee|/(W+R)$다. Isotropic 경우 비상대론 kinetic energy가 $a^{-2}$로 줄어드는 것은 이 식의 극한이다. Massless limit $R\to0$에서는 $\dot E=-E(H+\sigma ee)$를 회복한다.

원 BASS_CR ionization rate가 사용하는 $v_{\rm NR}=\sqrt{2W/m_e}$는 그대로 둔다. 본 절에서 kinematics를 정확한 massive form으로 썼다는 사실은 기존 atomic cross section이나 그 nonrelativistic speed 모델의 물리 정확도를 바꾸지 않는다. 새 에너지에서 source 함수를 다시 평가하고 그 원 domain을 유지한다.

## 3. Bianchi I에서 실제 유한 geometry map

Diagonal Bianchi I metric

$$ds^2=-c^2dt^2+\sum_{i=1}^3 a_i(t)^2(dx^i)^2,\quad a_i(t)>0\tag{BG.9}$$

의 spatial Killing directions에서 covariant coordinate momentum $P_i=a_iq_{\hat i}$가 일정하다. 여기서 $q_{\hat i}$는 직교 frame의 물리 momentum이다. 따라서 두 지정 시점 사이에서

$$q_{\hat i}^{\,+}=r_iq_{\hat i}^{\,-},\qquad r_i=\frac{a_i(t_-)}{a_i(t_+)}>0,\qquad
E^+=\sqrt{m_e^2c^4+c^2\sum_i(q_{\hat i}^{\,+})^2}.\tag{BG.10}$$

이는 prescribed Bianchi I의 collision-free geodesic map이다. 일반 Bianchi에서 covariant spatial momenta가 모두 상수라는 가정으로 확장하지 않는다. BG.10을 미분하여 $H_i=\dot a_i/a_i$를 쓰면 $\dot W=-\sum_iH_i c^2q_{\hat i}^2/E$가 되며 BG.1과 일치한다.

낮은 kinetic energy에서 $E-R$의 cancellation을 피하기 위해

$$W^+=\frac{p_c^{+\,2}}{\sqrt{R^2+p_c^{+\,2}}+R},\qquad p_c^+=c|\mathbf q^+|\tag{BG.11}$$

를 쓴다. 실제 구현은 `hypot`와 이 rationalized 식으로 FP64 geometry energy를 얻고, 그 **유한 계산값**을 exact rational 장부에 넣는다. Rational 장부의 보존은 FP64 geometry 해석 오차를 0으로 만드는 것이 아니다. 별도 high-precision scalar 비교로 작은 입력 오차를 관찰하고, projection의 representation 오차와 구분한다.

## 4. 수, pressure work, cutoff 이동의 장부

고정 comoving cell의 packet counts $N_j$와 raw angular energies를 보유하면 geometry map에서 $N_j^+=N_j^-$다. Kinetic energy 변화는

$$\Delta U_{\rm geom}=\sum_jN_j(W_j^+-W_j^-).\tag{BG.12}$$

지정된 배경과의 work를 기록하는 signed accumulator $G^+=G^- -\Delta U_{\rm geom}$를 두면 $U_{\rm packets}+G$는 이 단계의 정확한 장부 invariant다. $G$는 배경의 work accumulator이며 국소적인 중력 에너지 tensor나 일반 시공간의 전역 보존 에너지를 정의한 것이 아니다. $\Delta U_{\rm geom}$를 thermal collision heat로 동시에 더하지 않는다.

물리 volume $V\propto a_1a_2a_3$와

$$P^{ab}=\frac1V\sum_jN_j\frac{c^2q_j^aq_j^b}{E_j},\quad u_A=\frac1V\sum_jN_jW_j,\quad n_A=\frac1V\sum_jN_j\tag{BG.13}$$

를 쓰면 경계/충돌이 없는 raw packet sector에서

$$\dot n_A+3Hn_A=0,\qquad\dot u_A+3Hu_A=-K_{ab}P^{ab}.\tag{BG.14}$$

따라서 count 보존과 density 희석은 같은 진술이 아니다. Event rate의 target density를 다시 계산할 때에는 새 물리 volume이 필요하다. 이 루프의 실제 rebind witness는 새 volume과 target counts가 별도로 주어지는 interface를 고정한다.

그다음 sharp cutoff를 재분류하면, 같은 이동 후 원자들의 실제 에너지로

$$\Delta U_{\rm cut}=\sum_{\rm newly\ thermal}N_jW_j^+-\sum_{\rm newly\ active}N_jW_j^+$$

를 계산한다. 이 값은 thermal/active 두 장부 사이의 이동이며 BG.12의 배경 work와 중복하지 않는다. 이전 covariant cutoff-current 항등식은 동일 reference inventory와 trace 조건 아래 그대로 재사용한다. 기저 thermal fluid의 geometry work는 그 fluid에 채택한 stress/EOS closure로 별도 제공해야 하며, raw active packet map만으로 자동 결정되지 않는다.

## 5. 새 에너지의 사건과 표현 오차

한 packet의 에너지가 바뀌면 $v(W),\sigma_a(W)$, channel threshold, sharing support, 두 daughter의 합 $W-B_a$를 함께 새 $W$에 결속한다. 이전 grid index의 rate만 가져오고 daughter 에너지를 바꾸는 혼합은 일관된 사건 열이 아니다. 새 helper는 moved parent를 별도 key로 저장하며 원 `_sharing` 함수를 새 에너지에서 실제 호출한다.

양의 barycentric energy projection은 count와 첫 energy moment를 보존한다. 이 두 조건만으로 vector momentum이나 massive stress moment까지 보존되지는 않는다. 실제 운동량은 $p_c(W)=\sqrt{W(W+2R)}$이고, collinear 방향을 유지해도 일반적으로 $(1-\beta)p_c(l)+\beta p_c(u)\ne p_c(x)$다. 따라서 geometry transport에는 raw angular atoms를 유지하며, projection을 쓰는 observable은 해당 weak-error bound의 범위를 명시한다.

Projection 및 실제 새 kernel event의 구성, derivative bound와 계산값은 `GEOMETRY_REBIND_KO.md`에 이어진다. Threshold indicator는 smooth test function이 아니므로 smooth Taylor 오차식을 그대로 적용하지 않는다. Source lower boundary 아래 packet은 energy trace를 보유하거나 thermal owner로 명시적으로 이전해야 하고, 900 eV 위 입력은 이 source로 extrapolate하지 않는다.

## 6. 실제 Wolfram + xAct 확인

공식 xCore/xPerm/xTensor 소스를 SHA256로 확인한 뒤 Wolfram Language evaluator에서 실제 xTensor를 불러 새 tensor 식을 계산했다. Wolfram 15.0.1 Linux x86-64, xTensor 1.3.0, xPerm 1.2.4가 보고되었다. 계산에서는 `$xpermQ=False`로 pure Wolfram canonicalization을 사용했다. Package 초기화가 외부 executable 연결을 보고한 사실과 실제 canonicalization 설정을 구분한다.

새 검사 여덟 개는 observer energy, mass-shell decomposition, observer clock, geodesic product rule, normal derivative contraction, observer work, expansion/shear decomposition, antisymmetric frame work다. **여덟 residual 모두 정확히 0**이며 `AllZero -> True`다. 이 tensor 결과는 기재한 normalization/spatial constraints 아래 algebra를 검증한다. Prescribed geometry의 Einstein equation 적합성이나 source kernel의 경험적 정확도를 검증하는 계산은 아니다.

실행 식: `checks/wolfram_xact_branch_geometry.wl`, 실제 출력: `results/WOLFRAM_XACT_RAW.json`, 시작·종료 및 script hash: `results/WOLFRAM_XACT_EXECUTION.json`. Bianchi I scalar map, barycentric moments와 reaction branch 식은 별도 새 scalar 검사에 결속한다.

## 7. 원전 대응

Rendall의 Bianchi I Einstein–Vlasov 논문에서 covariant momentum을 쓴 분포와 energy/stress 적분을 비교한다. 본 유도는 그 논문의 Einstein–Vlasov asymptotic 결론을 사용하지 않고, spatial Killing symmetry와 mass shell만으로 BG.10을 독립 유도한다. 보존 remapping 문헌은 positivity와 count conservation을 비교하는 근거로 사용하며, 본 massive momentum/stress exactness에 대한 추가 보장을 수입하지 않는다. 정확한 원전 절·URL과 가정 대응은 `LITERATURE_KO.md`에 있다.
