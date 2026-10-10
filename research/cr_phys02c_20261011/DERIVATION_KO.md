# CR-PHYS02C — 원자 이온화 표현의 일관성

## 물리 질문과 비교의 범위

PHYS02B의 유한시간 수송을 유지하면서 이온화 총률과 방출 전자 에너지 분포를 하나의 BED 식에서 얻으면 결과가 얼마나 달라지는가? 비교 대상은 총률을 BEQ로, 분포 모양을 정규화한 BED로 두는 기존 조건부 모형이다. NIST는 이런 정규화 구성을 설명하고 있으므로 기존 모형을 대수적 오류라고 부르지 않는다. 새 모형은 별도의 원자 근사이며, 물리 정확도가 자동으로 높아졌다는 주장은 하지 않는다.

입사 전자의 운동에너지를 E, 결합에너지를 B, 방출된 두 전자 중 느린 전자의 운동에너지를 W라 두고 t=E/B, w=W/B, u=U/B를 사용한다. 원천 Q(W,t)=t A(W), bath, 0.1–900 eV 범위, 27 CCC 여기 채널, Coulomb 항, 1e10 s 종단시간과 수송 연산자는 이전 연구와 같다. CCC 표의 첫 zero marker는 이번에도 그 표에 붙인 유효 비용이다. 분광학적 에너지로의 교체나 입사 에너지 축의 이동은 하지 않는다.

## 하나의 진동자 세기에서 총률과 분포를 구성

g(w)=df/dw, Ni=∫g(w)dw, K=2−Ni/N, S=4πa0² N(R/B)²라 두면 사용한 BED 분포는

\[
\frac{d\sigma}{dW}=\frac{S}{B(t+u+1)}\left\{K\left[\frac1{(1+w)^2}+\frac1{(t-w)^2}-\frac{(1+w)^{-1}+(t-w)^{-1}}{t+1}\right]+\frac{\ln t}{N}\frac{g(w)}{1+w}\right\}.
\]

정의역은 E>B, 0≤W≤(E−B)/2다. 느린 쪽 반구간을 적분한 사건률에 두 딸전자 W와 E−B−W를 모두 넣는다. 전자 하나의 이온화 사건을 두 번 세지 않는다.

h=(t−1)/2라 하면

\[
\int_0^h[(1+w)^{-2}+(t-w)^{-2}]\,dw=1-1/t,
\qquad
\int_0^h[(1+w)^{-1}+(t-w)^{-1}]\,dw=\ln t.
\]

따라서 D(t)=N^{-1}∫₀ʰg(w)/(1+w)dw를 정의하면

\[
\sigma_{\rm BED}(E)=\frac{S}{t+u+1}\left[D(t)\ln t+K\left(1-\frac1t-\frac{\ln t}{t+1}\right)\right].
\]

E≤B에서는 총률을 0으로 둔다. 이 항등식은 총률과 분포의 정규화 관계를 고정한다. Qdf=(2/N)∫g(w)/(1+w)dw는 진단용 무한구간 모멘트다. BEQ 총률의 Q를 Qdf로 바꾸기만 하면 full BED가 되는 것은 아니다. BEQ에서는 K 대신 2−Q를 쓰고 D(t)를 Q(1−1/t²)/2로 근사하므로 두 항이 모두 다르다.

Kim–Johnson–Rudd 2000 PDF Eq1의 곱셈 모양 문자는 NIST의 가산형 BED 식과 위 적분 항등식에 맞춰 명시적으로 해석했다. 출판사 erratum을 찾았다는 뜻은 아니다. 해석 근거와 미확인 사항은 `research/ionization_sources/ATOMIC_PRIMARY_SOURCE_AUDIT_KO.md`에 보존한다.

## 수소: 전 구간에서 양인 Coulomb 진동자 세기

Rohrmann–Vera Rueda 2022의 광자 에너지 ε=1+w와 k=1/√w를 쓰면

\[
g_H(w)=\frac{128}{3}\frac{\exp[-4\arctan(\sqrt w)/\sqrt w]}{(1+w)^4[1-\exp(-2\pi/\sqrt w)]}.
\]

연속 극한은 gH(0)=128/(3e⁴)=0.781467259252658…이며 gH(w)>0이다. 큰 w에서 w^{-7/2}로 감소하므로 필요한 두 모멘트가 수렴한다. 독립 50자리 적분에서 w 구간과 y=1/(1+w) 구간을 따로 계산해

\[
N_i=0.4349958493251480126\ldots,\quad
Q_{df}=0.5668244319103390418\ldots,\quad
K=1.5650041506748519874\ldots
\]

를 얻었다. Ni는 원문의 Table1 값 0.4349958493과 인쇄 정밀도 내에서 일치한다. 이는 수소 Coulomb 쌍극자 진동자 세기의 확인이다. BED 전체 전자 충돌 근사가 정확해졌다는 인증이 아니다. 유한질량·미세구조를 새로 넣지 않고 부모의 B=U=13.6057 eV를 유지한다.

## 헬륨: 2000년 원 논문의 인쇄 정밀도

y=1/(1+w)일 때 원 논문의 식은

\[
g_{He}(w)=8.24012y^3-10.4769y^4+3.96496y^5-0.0445976y^6.
\]

원문과 같은 B=24.587 eV, U=39.51 eV, N=2를 쓴다. 이 다항식은 y³p(y)이고, 0≤y≤1에서 p'(y)<0, p(1)=1.6835824>0이므로 gHe≥0이다. 계수 c_k로 직접 적분하면

\[
N_i=\sum_k\frac{c_k}{k-1}=1.61008048,\quad
Q_{df}=\frac2N\sum_k\frac{c_k}{k}=0.9130407333333333\ldots,\quad
K=1.19495976,
\]

\[
D_{He}(t)=\frac1N\sum_k\frac{c_k}{k}\left[1-\left(\frac2{t+1}\right)^k\right].
\]

NIST의 Q=0.8841과 Müller 2009 표의 K=1.1860이 이 인쇄 계수와 정확히 어떻게 연결되는지는 여전히 확인되지 않았다. 새 모형에서 수치만 맞춰 끼우지 않는다.

## 양성, 에너지와 전자 수

t>1의 허용 구간에서 (1+w)^{-1}와 (t-w)^{-1}는 각각 1/(t+1)보다 크다. K>0이고 g≥0이므로 위 BED 분포는 음이 아니다. 각 사건에서 W+(E−B−W)+B=E이며, 전자 하나가 두 전자로 바뀌므로 자유전자 수는 정확히 하나 늘어난다. 기존의 양의 선형 투영은 두 딸전자의 수와 에너지를 보존한다. binding ledger와 이온화 횟수 ledger를 함께 쓰면 연산자 왼쪽 에너지·수 항등식이 성립한다.

수치적으로는 근처 임계값에서 expm1와 연속 극한을 사용한다. 분포의 projection-knot별 Gauss 적분은 기존처럼 정규화하지만 이 보정은 동일 full-BED 총률 적분과의 수치 오차만 수정한다. 이전의 물리적 BEQ/BED 재정규화와 구분해 실제 계수를 기록한다.

## 사전에 고정한 비교와 해석

새 모형은 2400=(800+1600), 4800=(1600+3200) node에서 종단 상태만 계산한다. 이전 R002의 같은 두 격자 결과는 실제 복구하고 해시 검증한 저장 결과를 사용한다. 기존 과학 suite를 다시 돌리지 않는다. 각 양 q에 대해 Δq_h=q_fullBED,h−q_legacy,h를 계산하고, r=|Δq_fine−Δq_coarse|/|Δq_fine| 및 두 격자 부호를 보고한다. r<1/3이고 부호가 같을 때에만 그 행을 경험적으로 분리되었다고 표시한다. 이 규칙은 오차 상계나 통계적 유의성이 아니다.

격자 channel 2%, cutoff·low-cross 전자 수 3%, 적분 2e−8, 연산자 보존 5e−12, 종단 ledger 1e−9의 기존 허용값을 유지한다. source convention, 다른 원자 모형 간 차이, 수치 수렴, 원격 파일 identity와 production 권위는 각각 별도 판정한다. 최종 채택에는 구현·후보 설계에 관여하지 않은 Astra 검토자가 필요하다.

## 1차 출처

- Kim, Johnson & Rudd (2000), Phys. Rev. A61,034702, DOI https://doi.org/10.1103/PhysRevA.61.034702 ; 읽은 원문 https://scispace.com/pdf/cross-sections-for-singly-differential-and-total-ionization-18cqvgiyli.pdf
- Rohrmann & Vera Rueda (2022), https://arxiv.org/abs/2208.02111 ; Eq5/9/10, Table1 https://arxiv.org/pdf/2208.02111v2
- NIST Electron-Impact Ionization Cross Section Database, 식과 정규화 설명 https://physics.nist.gov/PhysRefData/Ionization/intro.html 및 https://physics.nist.gov/PhysRefData/Ionization/Eqs/latex.html
- Kim & Rudd (1994), Phys. Rev. A50,3954, DOI https://doi.org/10.1103/PhysRevA.50.3954

원 논문의 전체 PDF를 배포 묶음에 넣지 않는다. 위 URL, 사용 식·계수, 출처 감사, 독립 재현 스크립트와 실제 결과를 전달한다.
