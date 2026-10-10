# CR-PHYS02C 원자 입력의 일관성: 독립 원문 조사와 대수

작성: `/root/phys02c_helium_sources`, 2026-10-10 UTC. GPT-6 Astra Pro의 호스트 모델 정보에 따라 research harness 4.0.0의 진입점·공통 core·모델 라우팅을 읽었다. 이 실행자는 후보의 원문 조사와 검산에 참여했으므로 최종 독립 decision reviewer가 아니다.

## 결론

**H에는 양의 정확한 비상대론적 Coulomb 연속 진동자 세기, He에는 Kim–Johnson–Rudd (2000)의 원계수를 쓰고, 각각의 동일한 진동자 세기로부터 `Ni`, `K`, SDCS 및 total을 도출하는 비교 경로가 명확하다.** 별도의 BEQ total에 맞추는 정규화는 이 경로에 들어가지 않는다. 이 결론은 원자 표현의 내적 일관성을 뜻하며 전자충돌 단면적의 물리 정확도 인증은 아니다.

He의 새 계수를 만들거나 기존 계수를 관측량에 맞춰 조정할 이유는 없다. Müller (2009)의 인쇄 `K_BED=1.1860`과 현재 NIST의 `Q=0.8841`은 선택한 2000년 다항식에서 유도되지 않는다. 이 숫자의 정확한 역사적 계보와 정오표는 이번에 확인하지 못했다. 따라서 이를 반올림 오차 또는 확정된 전사 오류라고 단정하지 않는다.

## 직접 읽은 주요 원문

| 원문 | 읽은 부분 | 이 조사에서의 용도 |
|---|---|---|
| [Kim & Rudd 1994, PRA 50, 3954](https://scispace.com/pdf/binary-encounter-dipole-model-for-electron-impact-ionization-9lx87pf4e9.pdf) | §III–V, Table I, H·He 논의; 공식 UNL 표지 포함 PDF. Eq35·38·39의 페이지 이미지는 확인, Table I 이미지 요청은 차단되어 텍스트만 확인 | BED와 BEQ의 정의, `Ni`와 `Q`가 서로 다른 모멘트라는 사실, 이전 He 실험 적합의 존재 |
| [Kim, Johnson & Rudd 2000, PRA 61, 034702](https://scispace.com/pdf/cross-sections-for-singly-differential-and-total-ionization-18cqvgiyli.pdf) | 전체 4쪽 텍스트, 첫 2쪽 이미지; Eq1–6의 계수·범위 대조 | He RRPA 기반 원계수와 total의 직접 적분 정의 |
| [Müller et al. 2009, PPCF 51, 105014](https://backend.orbit.dtu.dk/ws/portalfiles/portal/4857374/Naulin_paper.pdf) | Table I, Eq42–48, 인용47·49 | PHYS02B의 중간 출처와 원문 간 불일치 확인 |
| [NIST 이온화 식](https://physics.nist.gov/PhysRefData/Ionization/Eqs/latex.html), [설명 §A–B](https://physics.nist.gov/PhysRefData/Ionization/intro.html) | Eq1–4, 정규화 설명 | 공식 BEQ total과 BED SDCS의 관계, 덧셈 부호 대조 |
| [NIST He differential 입력](https://physics.nist.gov/cgi-bin/Ionization/ion_data.php?differential=Y&id=HeI&initial=&ision=I) | orbital 표 | B=24.5870, U=39.5100, N=2.0000, Q=0.8841의 현재 표시 확인 |
| [Rohrmann & Vera Rueda 2022, arXiv:2208.02111v2](https://arxiv.org/pdf/2208.02111v2) | §2 Eq5·8–11, §3 Table1; PDF 둘째 쪽 이미지 확인 | H 정확 진동자 세기의 단위·변수·문턱값 및 연속 f-sum |

2000년 논문은 RRPA 연속 진동자 세기를 네 항으로 적합하고, 그 식을 적분해 total을 얻는다. 1994년 논문의 He 표는 실험 photoionization 기반의 다른 적합과 `Ni=1.605`, `M_i²=0.489`를 제시한다. 따라서 논문·데이터베이스 사이에서 서로 다른 원자 표현이 사용될 수 있다는 사실은 원문으로 확인된다. 그러나 NIST `Q=0.8841`의 정확한 버전 계보까지 이로써 입증되는 것은 아니다.

## 공통 정의와 직접 유도

`T`는 입사 전자의 운동에너지, `W`는 두 자유전자 중 느린 전자의 운동에너지다. `B`는 채택한 결합에너지, `U`는 표적 궤도의 평균 운동에너지이며,

\[
t=T/B,\quad w=W/B,\quad u=U/B,\quad
S=4\pi a_0^2N(R/B)^2,\quad 0\le w\le h=(t-1)/2.
\]

`g(w)=df/dw`로 놓으면 서로 다른 두 모멘트는

\[
N_i=\int_0^\infty g(w)\,dw,\qquad
Q=\frac2N\int_0^\infty\frac{g(w)}{1+w}\,dw,
\qquad K=2-N_i/N.
\]

`N_i/N=Q`는 일반적인 항등식이 아니다. 특수한 BEQ 근사에서만 이를 채택한다. 따라서 `Q`를 다른 값으로 바꾸는 것만으로 BEQ 식이 full BED 식이 되지 않는다.

올바른 덧셈 형태의 BED SDCS는

\[
\frac{d\sigma}{dW}
=\frac{S}{B(t+u+1)}\left\{
K\left[\frac1{(1+w)^2}+\frac1{(t-w)^2}
-\frac1{t+1}\left(\frac1{1+w}+\frac1{t-w}\right)\right]
+\frac{\ln t}{N(1+w)}g(w)\right\}.
\]

직접 적분하면

\[
\sigma_{\rm BED}(T)=\frac{S}{t+u+1}
\left\{K\left[1-\frac1t-\frac{\ln t}{t+1}\right]+D(t)\ln t\right\},
\qquad
D(t)=\frac1N\int_0^{(t-1)/2}\frac{g(w)}{1+w}\,dw.
\]

여기서 첫째 역수항의 적분은 `ln(t)`, 제곱 역수항의 적분은 `1−1/t`이다. `T<B`에서 단면적을 0으로 두며 `T=B`는 연속적인 문턱극한이다.

### 양성 확인

`A=1/(1+w)`, `C=1/(t−w)`라 두면 `(A+C)/(t+1)=AC`이므로 Mott 괄호는

\[
A^2+C^2-AC=(A-C)^2+AC>0
\]

이다. 따라서 `K>0`, `g≥0`, `t≥1`이면 SDCS는 음수가 되지 않는다. 이는 구현에 의존하지 않는 대수 검사다.

### 교환항과 반구간의 해석

Mott 부분은 입사·방출 전자의 교환을 반영하지만 BED의 dipole 부분은 완전한 교환대칭 진폭 이론이 아니다. 이는 1994·2000년 원문이 명시한 근사다. 느린 전자 `W`를 반구간에서 한 번 표본화하고 다른 전자를 `T−B−W`로 생성하면 이 모형의 사건 수를 중복 세지 않는다. 두 딸전자에 에너지 `W`와 `T−B−W`, 결합 장부에 `B`를 기록하면 사건 단위 에너지와 자유전자 수 변화가 고정된다. 이 사건 구성 자체가 원래 BED 근사의 부족한 진폭 물리를 보충하지는 않는다.

## H: 전구간에서 양인 정확한 Coulomb 진동자 세기

Rohrmann & Vera Rueda의 Eq5는 photon energy를 Rydberg로 나타내어 `ε=1+1/k²`로 정의한다. Eq9에 `k=1/√w`, `ε=1+w`를 대입하면

\[
g_H(w)=\frac{128}{3}
\frac{\exp[-4\arctan(\sqrt w)/\sqrt w]}
{(1+w)^4[1-\exp(-2\pi/\sqrt w)]},\quad w>0,
\]

\[
g_H(0)=\frac{128}{3e^4}=0.781467259252658\ldots
\]

이다. 논문은 이 식의 기원을 Sugiura (1927), Menzel–Pekeris (1935)로 인용한다. 이 조사에서는 그 고전 논문들을 직접 읽지 않았으며, 현재 수식을 직접 명시하고 검산한 2022년 연구 논문을 사용했다.

이 식은 전구간에서 양이며 큰 `w`에서 `w^(−7/2)`로 감소하므로 필요한 모멘트가 수렴한다. 소수점 계수를 반올림한 H 다항식의 전구간 음수 꼬리 문제가 사라진다. **정확하다는 말은 이 비상대론적 Coulomb 진동자 세기에 한정된다.** BED 전자충돌 단면적 전체의 정확해라는 뜻은 아니다. 부모와 비교할 때 `B=U=13.6057 eV`라는 모델의 에너지 척도와 실제 분광학적 H 문턱은 구분해야 한다.

## He: 원문2000의 계수를 그대로 사용

\[
g_{He}(w)=8.24012y^3-10.4769y^4+3.96496y^5-0.0445976y^6,
\qquad y=(1+w)^{-1}.
\]

`B=24.587 eV`, `U=39.51 eV`, `N=2`를 함께 사용한다. 계수 적분은 유리수 연산으로 닫힌다.

\[
N_i=\sum_{m=3}^6\frac{c_m}{m-1}=1.61008048,
\quad Q=\sum_{m=3}^6\frac{c_m}{m}
=0.913040733333\ldots,
\quad K=1.19495976.
\]

\[
D(t)=\frac1N\sum_{m=3}^6\frac{c_m}{m}
\left[1-\left(\frac2{t+1}\right)^m\right].
\]

양성은 표본만으로 판단할 필요가 없다. `g=y³p(y)`의 `p(y)=8.24012−10.4769y+3.96496y²−0.0445976y³`는 `0≤y≤1`에서 감소하고, 최소값 `p(1)=1.6835824>0`이다.

### 보존해야 할 원문 불일치

| 비교 | 값 | 판정 |
|---|---:|---|
| 원문2000 계수의 `K` | 1.19495976 | 동일 `g`에서 도출 |
| Müller2009 Table I 인쇄 `K` | 1.1860 | 2000 다항식과 불일치; 정확한 역사적 원인 미확인 |
| 원문2000 계수의 `Q` | 0.913040733333… | 동일 `g`에서 도출 |
| 현재 NIST orbital 표의 `Q` | 0.8841 | 같은 `g`의 모멘트로 식별할 수 없음 |

또한 열람한 2000년 PDF Eq1은 둘째 Mott 항 앞에 곱셈 기호 `×`를 인쇄하고 있다. 그대로 곱하면 문턱 부근의 음수 SDCS와 Eq3의 total 불일치가 생긴다. 올바른 덧셈은 공식 NIST Eq3, Müller2009 Eq42, 1994년 각 항의 합 구조 및 2000년 자체 Eq3–4와 일치한다. **이것은 대수와 교차 원문에 근거한 전사 수선이다. 출판사 정오표를 발견했다고 주장하지 않는다.**

## 실제 경량 검산

`ALGEBRA_CONTRACT.json`을 먼저 고정하고 `source_algebra.py`로 다음만 수행했다.

| 모멘트 | 50자리 계산 |
|---|---:|
| `Ni_H` | 0.43499584932514801259832562569039603180653769862624 |
| `Q_H` | 0.56682443191033904178643632014098937270906506686167 |
| `K_H` | 1.5650041506748519874016743743096039681934623013738 |

H 모멘트를 `w∈[0,∞)`와 독립 재표현 `y=1/(1+w)∈[0,1]`에서 적분했고 두 표현은 50자리에서 일치했다. 논문의 Table1 연속 f-sum `0.4349958493`과도 인쇄 정밀도 내에서 일치했다. 선택된 `T=15,20,25,30,60,100,500,900 eV`의 `D_H(t)`는 JSON에 있다. 이 수치는 적분 오차의 구간 산술 인증이 아니다.

첫 시도는 `mpmath` 미설치로 어떤 수치적분도 하기 전에 exit1로 실패했다. 원로그와 실행 파일을 `ATTEMPT01/`에 보존했다. 전용 의존 경로에 `mpmath==1.3.0`을 설치한 뒤 **같은 계약·같은 과학 스크립트**로 실제 exit0, 1.0478초, 세 검사 PASS를 얻었다. `SOURCE_ALGEBRA_ACTUAL_EXIT.json`에 실제 세션·종료·해시를 기록했다. 캐스케이드 코드는 import하거나 실행하지 않았다.

## 남은 범위와 인계

원문 재현 비교는 원자 입력의 선택을 구체화한다. 최종 과학 판정에는 루트가 구현한 연산자·수렴·차이 분석과 별도 독립 검토가 필요하다. 동일 원천과 매질에서 PHYS02B hybrid와 새 일관 BED를 비교할 수 있다. 차이는 이 두 모델의 차이이며 관측적 오차막대로 쓰면 안 된다.

현재 NIST CGI와의 정확한 수치·버전 동일성, He RRPA 원테이블 및 실험 재분석, 여기 채널의 표적 에너지 문제, 생산 이력과 전체 PHYS02의 미해결 상태는 이 원문 조사로 닫히지 않는다.
