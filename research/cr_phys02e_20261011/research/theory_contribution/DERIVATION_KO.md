# 저장 격자와 에너지 좌표의 일관성: CR-PHYS02E 이론 기여

기여 역할: `THEORY_CONTRIBUTOR`. 이 문서는 독립 심사 판정, 변경 수락 기준 또는 NCP 실행 허가를 발행하지 않는다. 읽은 원본과 수학적 유도, 작은 유리수 검산의 근거 상태를 구분한다. 실제 원자 자료를 불러오거나 물리 G, pulse, 기존 과학 시험 묶음을 실행하지 않았다.

## 1. 관측된 실패와 이번 유도의 범위

PR33의 `INDEPENDENT_ACTUAL_RETURN_DECISION.json`은 실제 실행을 `HOLD`, `FAILED_BEFORE_PULSE`로 판정했다. fullBED 생성자가 반환된 뒤 저장 NPZ의 `energy_eV`와 생성된 격자의 엄격한 동일성 검사가 실패했다. legacy는 시작되지 않았다. 두 NPZ에서 각각 9,600개 중 340개 노드가 다르고, 최대 차이는 1 ULP, 즉 보고된 최대 절대 차이 $1.1368683772161603\times10^{-13}\,\mathrm{eV}$이다. 이 수치는 해당 기록에서 읽었으며 여기서 재계산하지 않았다.

기록된 저장 격자 바이트 SHA256은

```text
6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292
```

이고, 재생성 격자의 기록된 SHA256은

```text
870cfd5f3f2656371d5fad59e4b24f4b7aa051546b9d78f4f3a9de3197fcc0a4
```

이다. 이 문서에서 직접 바이트 검증한 대상은 진단·판정 파일과 읽은 코드이며, 그 목록은 `SOURCE_IDENTITIES.json`에 있다. 실행 환경의 어느 구현 세부가 차이를 일으켰는지는 `UNRESOLVED`다. Python·NumPy·SciPy 버전 문자열 일치로 CPU SIMD, libm 또는 특정 플랫폼 원인을 확정하지 않는다. 실패한 실행의 G는 보존되지 않았으므로 그 G와 과거 G의 항목별 차이도 평가할 수 없다.

이번 수학적 질문은 두 가지다. 저장된 격자를 모든 격자 의존 연산 이전에 채택하면 어떤 일관성을 회복하는가? 이미 G를 만든 뒤 `self.E`만 바꾸면 왜 에너지 장부가 통과하면서 수 장부는 깨질 수 있는가?

## 2. 정의, 좌표와 단위

실제 원본은 `research/cr_phys02b_20261010/src/causal_cascade.py`이다. `coherent_bed.py`는 원자모형을 바꾸지만 `Cascade=parent.Cascade`로 같은 수송 생성자를 사용한다. 따라서 아래 좌표·투영·장부 논증은 이 두 모형의 공통 수송 표현에 관한 것이다.

활성 노드 $E_i>0$의 단위는 eV이다. 활성 상태는 입자수 자체가 아니라 에너지 좌표

\[
U_i=E_i N_i
\]

다. $N_i$는 전자 수밀도이며 $U_i$는 $\mathrm{eV\,m^{-3}}$ 단위의 에너지 밀도다. 코드에서는 고정 에너지 척도 $U_0$로 나눈 좌표를 사용한다. 활성 성분과 에너지 장부는 $U/U_0$, 수 장부는 $N/U_0$이므로 후자는 $\mathrm{eV}^{-1}$ 단위다. 배열을 구성하는 모든 성분의 물리적 차원이 같다는 가정을 해서는 안 된다. `project` 자체는 입력 count의 단위를 보존하므로, 수학적 설명에서는 정규화 전 좌표를 사용해도 된다.

분리된 에너지 장부는 heat, binding_HI, binding_HeI, excitation_HI, excitation_HeI, cutoff_energy이다. 전역 에너지 선형함수는

\[
\ell_E^T U=\sum_i U_i+H+B_{\mathrm H}+B_{\mathrm{He}}
  +X_{\mathrm H}+X_{\mathrm{He}}+U_{\rm cutoff}.
\]

이온화는 자유전자 하나를 추가하므로, 단순한 자유전자 총수는 보존량이 아니다. 코드의 보정된 수 장부는

\[
\ell_N(E)^T U=\sum_i\frac{U_i}{E_i}
 +N_{\rm cutoff}-I_{\mathrm H}-I_{\mathrm{He}}.
\]

여기서 $I_{\mathrm H},I_{\mathrm{He}}$는 누적 이온화 사건 수밀도다. `low_cross_energy`, `low_cross_number`는 낮은 에너지 영역 진입의 진단량이며 전역 장부에 다시 더하지 않는다. 이미 세어진 에너지와 수를 중복 계산하게 되기 때문이다.

`functionals()`의 에너지 가중치는 활성 노드와 분리된 에너지 장부에서 1이다. 반면 수 가중치는 활성 노드에서 $1/E_i$다. 이 차이가 생성 후 격자 치환의 문제를 만든다.

물리 시간의 생성자를 $A$라 쓰고 $u=t/T_0$, $T_0=10^{10}\,\mathrm s$라 두면 코드의 행렬은 $G=T_0A$이다. 활성·에너지 행으로 가는 $A$ 항목은 $\mathrm s^{-1}$, 활성 에너지에서 수 장부로 가는 항목은 $(\mathrm{eV\,s})^{-1}$이다. 아래 보존식은 이 혼합 단위를 일관되게 적용한 선형함수에 대한 등식이며, $A$에서 $G$로 바꾸어도 성립한다.

## 3. Barycentric 투영이 보존하는 두 양

한 전자의 에너지 $W$가 두 노드 $E_l\le W\le E_u$ 사이에 있고 입력 수가 $p\ge0$이라고 하자. $E_u>E_l$일 때

\[
\lambda=\frac{W-E_l}{E_u-E_l},\qquad
N_l=p(1-\lambda),\qquad N_u=p\lambda.
\]

그러면 $0\le\lambda\le1$이고

\[
N_l+N_u=p,\qquad
E_lN_l+E_uN_u=pW.
\]

즉 먼저 count를 볼록 분할하고 활성 상태에는 $E_iN_i$를 저장하면 count와 에너지가 동시에 보존된다. 코드의 `frac`, `up_counts`, `down_counts`, `out[:n]=self.E*active_counts`가 바로 이 순서다. 수 장부는 그때 사용한 동일한 $E_i$로 상태를 나누어야 한다.

Cutoff $C=0.1\,\mathrm{eV}$와 첫 활성 노드 $E_1$ 사이에서는 $E_l=C$를 흡수 ghost로 사용한다. 따라서 낮은 쪽 count는 `cutoff_number`에, 그 에너지 $C N_l$는 `cutoff_energy`에 들어간다. $0\le W\le C$이면 수 $p$와 실제 에너지 $pW$를 그 두 장부에 직접 보낸다. 이때 $pC$로 대체하지 않으며 남는 에너지를 heat로 이동하지 않는다.

투영 연산자를 $\Pi_E(W,p)$라 쓰면 이온화 counter가 아직 추가되지 않은 투영에 대해 정확산술에서

\[
\ell_E^T\Pi_E(W,p)=pW,\qquad
\ell_N(E)^T\Pi_E(W,p)=p
\]

다. 여러 에너지와 count 배열에도 선형 합으로 성립한다. 실제 FP64 구현에서의 반올림 잔차는 이 정확산술 등식 자체와 별도다.

## 4. 같은 격자에서 생성한 전이 열의 장부

원본 `_generator`는 각 활성 에너지 열을 누적한다. 다음은 그 산술 구조의 정확산술 유도이며 실제 G 잔차를 측정했다는 뜻이 아니다.

### 4.1 Coulomb drift

노드 $E_j$와 바로 아래 에너지 $E_-$에 대해 stopping rate를 $b_j\,[\mathrm{eV/s}]$라 두면

\[
d_j=\frac{b_j}{E_j-E_-}\quad[\mathrm{s^{-1}}].
\]

열 $j$에는 활성 손실 $-d_j$, 투영 $d_j\Pi_E(E_-,1)/E_j$, heat 유입 $d_j(E_j-E_-)/E_j$가 들어간다. 따라서

\[
\ell_E^T A_{\cdot j}=-d_j+d_j\frac{E_-}{E_j}
 +d_j\frac{E_j-E_-}{E_j}=0,
\]

\[
\ell_N(E)^T A_{\cdot j}=-\frac{d_j}{E_j}+\frac{d_j}{E_j}=0.
\]

첫 활성 노드도 $E_-=C$를 cutoff의 에너지·수 장부로 처리하므로 같은 식이 성립한다.

### 4.2 이온화

사건률을 $r_j\,[\mathrm{s^{-1}}]$, 결합 에너지를 $B$, 느린 전자 에너지를 $W$라 두면 빠른 전자 에너지는 $E_j-B-W$다. `_sharing`의 정규화된 가중치가 정확산술에서 $\sum_a p_a=1$일 때, 두 전자 투영의 총 에너지는 $E_j-B$, 총수는 2다. 열은 활성 손실 $-r_j$, 두 투영의 $r_j/E_j$배, 결합 장부 $r_jB/E_j$, 이온화 counter $r_j/E_j$로 구성되므로

\[
\ell_E^T A_{\cdot j}=-r_j+r_j\frac{E_j-B}{E_j}
 +r_j\frac{B}{E_j}=0,
\]

\[
\ell_N(E)^T A_{\cdot j}=-\frac{r_j}{E_j}
 +2\frac{r_j}{E_j}-\frac{r_j}{E_j}=0.
\]

이 식은 총 단면적과 분배 함수의 값이 서로 다른 legacy/fullBED 각각에 적용된다. 두 모형의 물리 단면적이 동일하다는 주장은 포함하지 않는다.

### 4.3 여기

여기 사건률을 $r_j$, 채택된 에너지 비용을 $\Delta$라 쓰면, 한 전자를 $E_j-\Delta$에 투영하고 여기 장부에 $r_j\Delta/E_j$를 적립한다. 총 에너지 잔차는 $-r_j+r_j(E_j-\Delta)/E_j+r_j\Delta/E_j=0$, 보정 수 잔차는 $-r_j/E_j+r_j/E_j=0$이다.

분리된 열들을 더하면

\[
\ell_E^T G=0,\qquad \ell_N(E)^T G=0
\]

이다. 외부 주입을 코드처럼 $dy/du=Gy+u b$, $y(0)=0$로 두면

\[
\ell^T y(u)=\frac{u^2}{2}\ell^T b,
\qquad \ell=\ell_E\;\text{또는}\;\ell_N(E).
\]

이것이 `summarize`의 장부 잔차와 연결된다. 여기서 $b$는 모든 활성·흡수·수·진단 좌표를 포함하는 전체 저장 source vector다.

## 5. 생성 뒤 `self.E`만 바꾸는 방법의 반례

다음은 실제 CR 행렬이 아닌 두 활성 상태와 heat의 해석 예제다. $E_1=1\,\mathrm{eV}$, $E_2=2\,\mathrm{eV}$, $d=1\,\mathrm{s^{-1}}$로 두고 좌표를 $(U_1,U_2,H)$로 쓴다. 첫 상태와 heat를 이 예제에서는 흡수 상태로 두면

\[
A=\begin{pmatrix}
0&d/2&0\\
0&-d&0\\
0&d/2&0
\end{pmatrix}.
\]

두 번째 열은 정확히 원본 drift의 형태다. 이때 stopping rate는 $b=d(E_2-E_1)=1\,\mathrm{eV/s}$이다. 에너지 함수 $\ell_E^T=(1,1,1)$, 수 함수 $\ell_N^T=((1\,\mathrm{eV})^{-1},(2\,\mathrm{eV})^{-1},0)$에 대해 두 장부 모두 영이다.

이제 이미 만든 $A$와 상태 좌표의 숫자를 유지한 채 두 번째 노드의 표기만

\[
E_2'=2\,\mathrm{eV}+\epsilon
\]

로 치환하자. $\epsilon$은 에너지 차원을 가진다. 새 `functionals()`는 두 번째 active weight를 $1/E_2'$로 바꾼다. 그러나 에너지 함수는 그대로이므로

\[
\ell_E^T A_{\cdot2}=0,
\]

\[
\boxed{\ell_N(E')^T A_{\cdot2}
=d\left(\frac1{2\,\mathrm{eV}}-
\frac1{2\,\mathrm{eV}+\epsilon}\right)
=\frac{d\epsilon}{(2\,\mathrm{eV})(2\,\mathrm{eV}+\epsilon)}}.
\]

잔차의 단위는 $(\mathrm{eV\,s})^{-1}$이며 활성 에너지 밀도를 곱하면 가짜 수밀도 변화율 $\mathrm{m^{-3}s^{-1}}$을 만든다. $\epsilon>0$이면 양수, $\epsilon<0$이고 $E_2'>0$이면 음수이며 $\epsilon\to0$에서 영으로 간다. 첫 상태보다 높은 노드를 유지하려면 이 예제에서는 $E_2'>E_1$도 요구한다.

예를 들어 $\epsilon=2^{-51}\,\mathrm{eV}$는 2 eV 바로 위 binary64 한 ULP다. 이 경우 유리수로 계산한 잔차는

\[
\frac1{9007199254740994}\,(\mathrm{eV\,s})^{-1}>0
\]

이다. 이 작은 값은 **실제 9,600점 G의 오차나 물리적 허용 여부를 평가한 수치가 아니다.** 에너지 장부만 검사하면 모순을 놓칠 수 있다는 반례의 값이다.

일반적으로 원래 $\ell_N(E)^T G(E)=0$였어도 생성 후 치환하면

\[
\ell_N(E')^T G(E)
=[\ell_N(E')-\ell_N(E)]^T G(E)
\]

가 된다. 우연히 영이 될 수는 있지만 항상 영일 이유는 없다. 반대로 올바른 $E'$로 전이 열 전체를 다시 만들면 같은 보존 유도가 적용된다. 이것은 실제 물리 실행을 여기서 재허가한다는 뜻이 아니다.

단순 좌표변환이라는 해석도 주의해야 한다. 실제 가역 좌표변환 $y'=Sy$라면 $G'=SGS^{-1}$, $b'=Sb$, $\ell'^T=\ell^TS^{-1}$를 모두 바꾸어야 한다. 에너지는 전이율과 물리적 투영의 입력이기도 하므로, 노드 숫자만 고치는 작업은 그러한 일관된 좌표변환이 아니다.

## 6. 생성 전에 저장 격자를 채택했을 때 회복되는 일관성

저장 NPZ가 결속하는 $E_*$를 모든 격자 의존 연산보다 먼저 설치하고 원래 연산과 원자 입력을 그대로 사용하면, 하나의 $E_*$가 다음을 공동으로 정의한다.

| 코드 요소 | 격자가 들어가는 자리 | 일관성의 의미 |
|---|---|---|
| `n`, `size`, `ix`, `mesh` | 노드 수와 source·ledger 배열 배치 | 저장 source의 같은 좌표 해석 |
| `_generator` drift | 노드 간격, stopping, $1/E_j$ | 손실·이동·heat 분배가 같은 에너지 기준 사용 |
| `_generator` 원자율 | 속도와 단면적의 평가 에너지 | 고정 원자모형을 저장 노드에서 평가 |
| `_sharing` | 노드·반사 노드의 knots, 적분 패널 | 자식 분배의 격자 경계가 투영 경계와 일치 |
| `project` | bracket, 분할 비율, $E_iN_i$ | count와 에너지의 공동 보존 |
| `source_vectors` | cell edges와 동일 `project` | 저장 원천 $b_*$가 의미한 좌표와 정합 |
| `functionals` | 활성 수의 가중치 $1/E_i$ | 같은 상태 에너지를 같은 입자수로 해석 |

이것은 고정 격자의 재생성을 새로운 물리 입력으로 대신하는 변경이 아니다. 저장 source가 이미 사용했던 격자를 생성자의 명시적 입력으로 삼는 방법이다. 다만 이 결론은 저장 NPZ identity, 전체 배열, 원자 입력, cutoff, ledger map, source vectors, quadrature 및 누적식이 유지되고, 모든 격자 의존 캐시가 실제로 새 입력을 사용한다는 조건부 명제다. 생성자 순서와 저장 source 취급이 이를 충족하는지는 구현 검사와 독립 심사의 대상이며 이 문서는 그 판정을 대신하지 않는다.

특히 다음 pulse의 입력은 기존 NPZ의 **전체** source vectors $b_*$여야 한다. active 부분만 잘라 쓰거나 source를 새로 적분하면 cutoff와 수 장부 및 원천 결속이 달라질 수 있다. 재생성한 source가 근접하다는 사실로 저장 source를 대체해서는 안 된다.

## 7. exact E의 필요성과 충분성은 다르다

저장 원천을 같은 좌표에서 해석한다는 계약 아래에서 exact E는 필요한 결속 조건이다. 다음 명제들은 구분해야 한다.

1. **저장 격자 바이트 결속:** 지정된 dtype·shape·배열 바이트와 전체 노드 값을 확인하는 입력 identity의 문제다. 배열의 수치 동일성 검사는 파일 전체 identity와 같지 않다.
2. **구성상의 일관성:** 같은 E로 투영·전이율·장부를 만드는 문제다. 위 대수적 보존 유도는 이 조건에 해당한다.
3. **연산자 항목 동일성:** 정확히 같은 G를 얻었는지는 모든 입력과 산술 경로에 달려 있다. 속도·로그·단면적·적분 합·sparse 누적의 결과가 E 하나로 결정된다고 볼 수 없다.
4. **응답과 물리 해석:** G의 동일성 또는 허용된 잔차 검사는 해당 고정 모형의 계산을 평가한다. 단면적의 물리적 타당성, 상위 atomic·CCC 입력, 생산 모형 또는 무한 시간 가정의 채택을 자동으로 인증하지 않는다.

같은 E에서도 위 2상태 drift 예의 $d$를 1에서 2 $\mathrm{s^{-1}}$로 바꾸면 두 장부는 계속 영이지만 시간 응답은 달라진다. 그러므로 장부 보존도 G 동일성의 충분조건이 아니다.

또한 1 ULP 노드 차이만으로 $\|\Delta G\|$나 관측량 오차를 제한할 수 없다. 예를 들어 drift의 $d_j=b_j/(E_j-E_{j-1})$에는 노드 간격의 역수가 들어간다. 함수가 매끄럽고 충분히 작은 변화라는 추가 가정 아래의 일차식은

\[
\frac{\delta d_j}{d_j}
\simeq\frac{\delta b_j}{b_j}
-\frac{\delta E_j-\delta E_{j-1}}{E_j-E_{j-1}}
\]

이지만, 이것은 해당 가정이나 도함수·잔차 경계 없이 실제 오차 상계가 되지 않는다. 원자 threshold, interpolation bracket, `searchsorted`, reflected knots와 중복 제거도 별도로 고려해야 한다. 진단의 1 ULP는 격자 차이의 크기를 기술할 뿐, operator error나 scientific PASS를 주지 않는다.

## 8. 검산 및 판정 경계

`exact_toy_check.py`는 표준 라이브러리 `fractions.Fraction`만으로, 위 작은 행렬과 투영의 유리수 등식을 한 번 검산한다. 이온화·여기의 추상 count/energy 항등식도 검사한다. 실제 원자 자료, 과학 모듈, NumPy, SciPy, physical G 또는 pulse는 사용하지 않는다. 실제 명령, exit, 시간, stdout·stderr identity는 `TOY_CHECK_RECEIPT.json`에 있다. 이 검산은 해석 예제의 산술을 확인하며 실행 계약의 수락 시험이나 실제 G 검증을 대체하지 않는다.

근거 상태는 다음과 같다.

- `source-observed`: PR33의 정확 격자 불일치, 원본의 에너지 좌표·투영·장부 정의.
- `derived`: 같은 격자의 투영 및 열별 장부 등식, 사후 치환 반례, exact E의 논리적 한계.
- `numerically checked (exact rational toy)`: 작은 예제의 Fraction 검산 결과.
- `unresolved`: 원래 노드 생성의 플랫폼 원인, 실패한 실제 G와 저장 계산의 항목별 차이.
- `outside this contribution`: 새 구현의 합격 판정, NCP 재실행 예산·허가, 독립 최종 과학 판정.

PR33의 첫 실패와 기존 과학 판정을 이 문서로 소급 변경하지 않는다. 이 문서는 저장 격자 constructor 경로의 물리적·수학적 이유를 제공하는 이론 기여다.
