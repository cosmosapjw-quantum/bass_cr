# R4W G02: 이동 기저의 정확한 미분 항등식과 저장된 FEM 표현의 경계 결함

상태: **derived**, 저장된 계수의 경계 추적은 **numerically checked / exact rational arithmetic on FP64 bytes**. 이 문서는 기존 연산자·기저·허용오차를 바꾸지 않는다. 원래 G02 유한차분 판정은 그대로 보존하며, 아래 결과만으로 production HOLD를 해제하지 않는다.

## 1. 적용 대상과 단위

직접 읽은 구현은 `bass_foundations/two_center.py`의 `basis_values`, `radial_basis.py`의 `FEMRadial.evaluate`와 `atomic_bank`, `full_operator.py`의 `same_center_blocks`, `aligned_cross.py`의 `cross_blocks`, HPC strict Fortran의 경계 래퍼와 연산 순서 계약이다. 실제 새 실행의 교차 블록은 별도 exact s+p moment kernel을 사용하므로, 이 문서에서 일반 basis evaluator의 수식을 읽었다는 사실을 새 native 호출이나 두 kernel의 전역 동등성 검증으로 해석하지 않는다.

기저의 정의는 물리 단위를 복원하면

\[
\chi_{Ca}(\mathbf r,t)=
\exp\!\left[\frac{i m_e}{\hbar}\left(\mathbf v_C\!\cdot\!\mathbf r-
\frac{v_C^2t}{2}\right)\right]
\phi_{Ca}(\mathbf r-\mathbf R_C(t)),\qquad
\mathbf R_C(t)=\mathbf A_C+\mathbf v_Ct,
\]

\[
\phi_{Ca}(\mathbf x)=\frac{u_{Ca}(r)}{r}Y_{\ell_a m_a}(\widehat{\mathbf x}),
\quad S_{ab}=\langle\chi_a,\chi_b\rangle,
\quad D_{ab}=\langle\chi_a,\partial_t\chi_b\rangle.
\]

질량은 전자 질량이다. 핵의 직선 궤도 속도가 전자 translation factor에 들어간다. 내부 단위는 `a0_Eh_ta`, \(t_a=\hbar/E_h\), 속도 단위는 \(a_0/t_a\)이다. 따라서 \(S\)는 무차원이고 \(D,\dot S\)는 \(t_a^{-1}\), 공간 연결 \(A_j\)는 \(a_0^{-1}\)이다. 아래 계산식은 이 원자단위의 수치 변수로 쓴다. 저장된 B0는 고정된 공통 radial bank, \(L=64a_0\), 40개 구간, 구간별 4차 polynomial, \(\ell\leq1\), 9개 채널/중심이다. \(\mathbf v_T=0\), \(\mathbf v_P=(0,0,v)\), \(v=2.00798106651023\), \(\mathbf A_T=0\), \(\mathbf A_P=(2,0,0)a_0\)이다.

원래 초기조건·propagator·선택 상태·collision window는 이 작업에서 사용하거나 바꾸지 않는다. 이는 정적 기저 미분 검증이다.

## 2. 같은 중심에서는 overlap 미분이 정확히 0이다

같은 중심의 위상은 bra/ket에서 상쇄된다. 전 공간 적분에 \(\mathbf x=\mathbf r-\mathbf R_C(t)\)를 대입하면

\[
S^{CC}_{ab}(t)=\int\phi_{Ca}^*(\mathbf x)\phi_{Cb}(\mathbf x)d^3x,
\qquad \dot S^{CC}=0.
\]

이 결론은 기저의 직교성이나 에너지 고유상태 가정을 요구하지 않는다. 고정된 square-integrable 함수들의 공통 translation과 공통 phase만 필요하다. 따라서 저장 polynomial에 미세한 불연속이 있어도 overlap의 시간 불변성 자체는 유지된다. 구현에서 같은 중심 적분의 radial partition은 상대 핵 거리에서 다시 나뉘므로, 유한정밀도 산술에서 계산된 \(S^{CC}\)가 모든 시간에 bitwise 동일하다는 결론까지 따라오지는 않는다.

한편 미분이 약한 의미에서 잘 정의되고 \(\phi_a\in H_0^1\)이면

\[
A_{j,ab}=\int\phi_a^*\partial_j\phi_b\,d^3x,
\quad D^{CC}=-\mathbf v_C\cdot\mathbf A-\tfrac i2v_C^2S^{CC},
\quad A_j+A_j^\dagger=0.
\]

마지막 식은 integration by parts와 0인 경계 trace에서 유도된다. 따라서 \(D^{CC}+D^{CC\dagger}=0\). 이 등식은 `D`를 반대칭화해서 얻는 정의가 아니라 독립적으로 만족해야 하는 결론이다. 원시 `D`를 투영하거나 0으로 덮어쓰면 기존 결함을 숨기므로 여기서는 수행하지 않는다.

## 3. B0의 s–p_z 연결: 큰 항 두 개를 더하지 않는 독립 계산식

실수 Condon–Shortley \(Y_{00},Y_{10}\)에 대해

\[
\int Y_{00}\cos\theta Y_{10}\,d\Omega=\frac1{\sqrt3}.
\]

\(I_{sp}=\sum_e\int_{r_{e-1}}^{r_e}u_su'_p\,dr\),
\(I_{ps}=\sum_e\int_{r_{e-1}}^{r_e}u_pu'_s\,dr\),
\(J_{sp}=\sum_e\int_{r_{e-1}}^{r_e}u_su_p/r\,dr\)라 놓으면

\[
A_{z,sp}=\frac{I_{sp}+J_{sp}}{\sqrt3},\qquad
A_{z,ps}=\frac{I_{ps}-J_{sp}}{\sqrt3}.
\]

따라서 \(J_{sp}\)를 수치적으로 두 번 계산한 뒤 상쇄시킬 필요 없이

\[
A_{z,sp}+A_{z,ps}
=\frac{1}{\sqrt3}\sum_e
\left[(u_su_p)(r_e^-) -(u_su_p)(r_{e-1}^+)\right]
\equiv\frac{B_{sp}}{\sqrt3}.
\]

\(s,p_z\) 사이에는 각운동량 직교성으로 \(S_{sp}=0\)이므로

\[
\boxed{D_{sp}+D_{ps}^*=-\frac{v}{\sqrt3}B_{sp}}.
\]

이 식은 저장된 구간 polynomial의 **strong derivative를 구간별로 적분한 연결**에 대한 항등식이다. 이상적인 연속 FEM이라면 내부 endpoint들이 정확히 망원경 합으로 상쇄되고, 양 끝 Dirichlet 조건으로 \(B_{sp}=0\)이다. 저장된 실수 polynomial이 구간 경계에서 불연속이면 \(B_{sp}\)는 일반적으로 0이 아니다.

구현 가능한 안정적 oracle은 각 FP64 계수를 그 정확한 이진 유리수로 변환하고, 구간별 \(u(0)=c_0\), \(u(1)=\sum_{k=0}^4c_k\)와 위 endpoint product 합을 `Fraction`으로 계산하는 것이다. 이 단계에는 quadrature, native library, \(D\) 배열, \(1/r\) 적분이 필요 없다. 마지막 \(v/\sqrt3\)만 명시한 고정밀도로 평가한다. 따라서 기존 18×18 연산자나 누적 순서를 바꾸지 않는 독립 진단이다. 각 \(I\), \(J\)를 별도 고정밀도로 계산하면 큰 두 `D` 원소 각각도 검증할 수 있으나, endpoint 합이 필요한 이유는 상쇄되는 큰 수의 차이에 의존하지 않는 데 있다.

보다 일반적으로

\[
B_{ab}=u_a^*(L^-)u_b(L^-)-u_a^*(0^+)u_b(0^+)
 +\sum_{e\text{ internal}}\big[(u_a^*u_b)(r_e^-)-(u_a^*u_b)(r_e^+)\big].
\]

부호는 `left trace − right trace`이다. radial 변수의 \(dr=h_e ds\)는 미분의 \(1/h_e\)와 정확히 상쇄되어 구간별 endpoint 식에 mesh 길이가 남지 않는다. 차원상 \(u_au_b\)는 \(a_0^{-1}\)이고, 속도를 곱하면 \(t_a^{-1}\)이 된다.

## 4. 저장된 계수와 이상적인 FEM 공간을 구별해야 한다

`atomic_bank`는 연속 nodal coefficients에 양 끝 0을 붙인 뒤 구간 monomial coefficients로 변환한다. 이 변환의 FP64 rounding 때문에, 저장된 monomial 계수를 정확한 수로 해석한 함수는 원래의 연속 nodal 함수와 미세하게 다르다. `FEMRadial.evaluate`는 구간 내부 polynomial derivative를 계산하고 \(r\geq L\)에서 0을 반환한다. 내부 interface와 외곽에서 생기는 distributional derivative는 계산하지 않는다.

`BASIS.npz`의 실제 FP64 bytes를 유리수로 변환하여 읽으면 다음과 같다. `max jump`는 \(|u(r_e^-)-u(r_e^+)|\)이고 값은 표시를 위해 실수로 반올림했다.

| radial mode | \(\ell\) | max internal jump | outer trace \(u(L^-)\) |
|---|---:|---:|---:|
| 0, bound 1s | 0 | 1.587618925213974e−14 | −2.828709605818753e−34 |
| 1, bound 2s | 0 | 1.071365218763276e−14 | 1.292469707114106e−25 |
| 2, positive s | 0 | 5.051514762044462e−15 | 1.013078509970455e−15 |
| 3, bound 2p | 1 | 9.603429163007604e−15 | −1.486340163181222e−25 |
| 4, positive p | 1 | 7.660538869913580e−15 | 1.360023205165817e−15 |

이 수치들은 문서의 정리 조건을 실제 representation이 byte 수준에서 완전히 만족하는지를 확인한다. 이것만으로 전체 연산자 오차를 bound할 수는 없다. 특히 원시 \(D+D^\dagger\)의 작은 잔차를 모두 summation rounding이라고 단정할 수 없다. 최소한 (a) 저장된 representation의 endpoint defect, (b) quadrature error, (c) floating arithmetic error를 분리해야 한다. 정확한 endpoint oracle과 개별 원소의 고정밀도 적분이 그 구분을 제공한다.

불연속 함수에는 공통 translation에 대한 overlap 불변성과, 구간별 strong derivative를 사용한 \(D+D^\dagger\) 항등식이 동일한 명제가 아니다. 불연속 함수의 translation은 일반적으로 \(L^2\)에서 강미분 가능하지 않으므로, 이상적인 \(H_0^1\) 증명을 저장된 discontinuous polynomial에 그대로 적용하면 안 된다.

향후 representation을 고친다면 원래 nodal 정보를 보존한 평가 또는 endpoint constraints를 정확히 만족하는 별도 basis representation이 후보가 된다. 그러나 저장된 원본을 조용히 연속화하면 기저 byte/context identity가 바뀐다. 그것은 별도 수정·정확도 검증 대상이며 이번 작업에서는 시행하지 않는다.

## 5. 교차 블록의 시간 위상은 중점 좌표에서 이미 상쇄된다

\(\mathbf q=\mathbf v_P-\mathbf v_T\), \(\mathbf R=\mathbf R_P-\mathbf R_T\),
\(\mathbf M=(\mathbf R_P+\mathbf R_T)/2\), \(\mathbf x=\mathbf r-\mathbf M\)라 두면

\[
S^{TP}_{ab}=e^{i\theta(t)}F_{ab}(\mathbf R(t)),
\quad F_{ab}(\mathbf R)=\int e^{i\mathbf q\cdot\mathbf x}
\phi_{Ta}^*(\mathbf x+\mathbf R/2)\phi_{Pb}(\mathbf x-\mathbf R/2)d^3x,
\]

\[
\theta(t)=\mathbf q\cdot\mathbf M(t)
-\tfrac12(v_P^2-v_T^2)t
=\mathbf q\cdot\frac{\mathbf A_P+\mathbf A_T}{2}=\theta_0.
\]

따라서 일정한 두 속도에서 이 uniform carrier는 정확히 시간 독립이다. B0에서는 impact parameter가 속도에 수직이므로 \(\theta_0=0\). `aligned_cross.py`의 lab-frame 식에서 보이는 \(-v^2t/2\)만 제거하면 geometric midpoint에서 상쇄되던 위상을 오히려 추가한다. 그러므로 단순 phase-demodulated FD가 반드시 더 안정적이라는 결론은 성립하지 않는다. 특정 원소의 geometry-dependent oscillation은 남을 수 있으나, 그것은 모든 원소에 공통인 알려진 carrier가 아니다.

형식적으로 임의 위상 \(\vartheta(t)\)를 제거해 \(\widetilde S=e^{-i\vartheta}S\)를 쓰려면

\[
\dot S=e^{i\vartheta}(\dot{\widetilde S}+i\dot\vartheta\widetilde S)
\]

를 함께 사용해야 한다. 이 보정 없이 기존 \(D+D^\dagger\)와 비교하면 다른 미분을 비교하는 것이다.

\(H_0^1\) 기저와 고정된 속도에서는 중점 표현에서 직접

\[
\boxed{\dot S^{TP}_{ab}=
\frac{e^{i\theta_0}}2\int e^{i\mathbf q\cdot\mathbf x}\,
\mathbf q\cdot\left[(\nabla\phi_{Ta}^*)\phi_{Pb}-\phi_{Ta}^*(\nabla\phi_{Pb})\right]d^3x}
\]

를 얻는다. 원자의 공간 argument는 앞의 \(\mathbf x\pm\mathbf R/2\)와 같다. 이 식은 basis gradients로 직접 구성할 수 있는 독립적인 geometric derivative oracle이다. 공통 속도 \(\mathbf V=(\mathbf v_P+\mathbf v_T)/2\)에 의한 항은 integration by parts에서 \(i\mathbf V\cdot\mathbf q\,S\)를 만들고 ETF의 \(-i(v_P^2-v_T^2)S/2\)와 상쇄된다. 고정 target의 원래 lab representation에서는 \(D^{PT}=0\)이고, 이상적인 연속 기저에서는 \(\dot S^{TP}=D^{TP}\)이다.

저장된 미세한 불연속 representation에는 움직이는 interface의 항이 추가될 수 있다. 이 geometric-gradient oracle을 구현하더라도 그러한 interface 항을 무시한 상태로 고차 유한차분과의 완전한 수학적 일치를 주장할 수 없다. 이번 same-center endpoint 실험은 그 문제가 가장 단순하고 독립적으로 평가 가능한 부분이다.

## 6. 판정과 다음 단계의 경계

이번 이론에서 직접 구현할 최우선 실험은 PP의 s–p_z 원소에 대해 exact-coefficient endpoint oracle, 고정밀도 개별 적분, 보존된 원시 `D`의 합을 나란히 비교하는 것이다. 물리 호출 0회로 representation defect를 arithmetic/quadrature discrepancy와 분리할 수 있다. 이 결과는 기존 large-\(h\) 2차 FD의 truncation error를 없애주지 않으며 원래 G02 gate의 실패를 PASS로 바꾸지 않는다.

Richardson R8은 기존 \(S(t\pm h/v)\)만을 이용한 독립적인 수치 증거다. 그러나 \(H_0^1\) 조건만으로 9차 시간미분이나 균일한 \(O(h^8)\) remainder가 보장되지 않는다. 짧은 ladder에서 얻은 작은 잔차를 연속 trajectory error certificate로 해석하면 안 된다. 교차 블록의 개선은 고차 stencil의 추가 독립 검증 또는 interface-aware geometric derivative 구현이라는 별도 단계로 남는다.

수학적 극한은 일관적이다. 두 속도가 같으면 \(\mathbf q=0\), 상대 위치와 교차 overlap이 불변이다. compact supports가 떨어지면 모든 교차 적분은 0이다. 같은 중심에서는 velocity와 무관하게 overlap 미분이 0이다. 가속하는 중심, time-dependent radial coefficients, 다른 중심별 추가 phase, 비소멸 boundary trace는 위 고정 조건 밖이며 추가 항을 필요로 한다.
