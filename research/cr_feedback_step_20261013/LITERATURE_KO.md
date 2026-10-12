# BASS_CR feedback 루프: 원전과 적용 조건

연구 단위: CR-THEORY-FEEDBACK-20261013. 확인일: 2026-10-13 KST / 2026-10-12 UTC.

## 문헌 대조의 결론

반응별로 공통 증분을 사용해 화학양론을 보존하는 방법과, 입자수 변화를 포함한 열적 온도식은 선행연구에서 확인된다. 이번 후보의 수용 여부는 그 위에 구성한 BASS_CR active/thermal/H–He 사건 장부, 양수성 보존 갱신, 온도·조성 피드백 사상의 직접 증명으로 판정한다. 아래 문헌은 수식과 방법의 대응 근거이며, 후보의 일반 정리는 별도의 독립 심사에서 확인한다.

SciSpace의 자연어 검색 한 차례와 Exa의 네 검색(요청 결과 합계 26개)을 사용했다. 중복과 개요만 있는 결과를 제거하고 아래 네 원전의 필요한 절을 읽었다. 검색의 목적은 이번 구성에 가까운 선행 방법과 적용 조건의 확인이다.

## L1. 반응별 공통 가중치와 에너지의 반응 참여

Jianhua Pan, Yu-Yen Chen, Liang-Shih Fan, *Second-order unconditional positive preserving schemes for non-equilibrium reactive flows with mass and mole balance*, Journal of Computational Physics **441**, 110477 (2021). DOI: [10.1016/j.jcp.2021.110477](https://doi.org/10.1016/j.jcp.2021.110477). 읽은 원문: [arXiv:2006.08549](https://ar5iv.labs.arxiv.org/html/2006.08549), §§2–5.

논문은 반응 r에 참여하는 모든 종에 동일한 Patankar 가중치 χ_r를 곱한다. 반응률과 화학양론 계수의 곱을 유지하므로 사건별 원소·질량 장부가 보존된다. §§2–3은 반응물 농도비의 곱으로 χ_r를 구성하고 2차 정확도 조건을 전개한다. §5는 흡열 사건에서 내부에너지를 소비하는 성분으로, 발열 사건에서는 생성되는 성분으로 다루어 열적 양수성을 결합한다.

증명의 적용 조건을 분리했다. §4의 일반 다중 반응물 암시계에 대한 양의 해 존재·유일성은 **Conjecture 1**이다. Theorem 1은 각 반응에 반응물이 하나인 경우, Theorem 2는 다중 반응물·무생성 반응 하나와 선형 단일 반응물 반응들이 있는 경우를 다룬다. 일반 경우의 근거는 해당 논문의 표본 계산이다. 따라서 이번에는 **반응별 공통 가중치와 에너지 참여라는 구성 비교**를 채택하며, 후보의 일반 존재·유일성은 직접 증명으로 심사한다.

## L2. 양의 선형 암시계와 보존량

Stefan Kopecz, Andreas Meister, *On Order Conditions for modified Patankar–Runge–Kutta schemes*, [arXiv:1702.04589](https://arxiv.org/abs/1702.04589). 읽은 원문: [PDF](https://arxiv.org/pdf/1702.04589), Definition 2.1, Lemmas 2.6–2.7, Theorems 3.3–3.4.

논문이 다루는 생산–소멸계는 비음수의 쌍별 전달률 p_ij,d_ij와 p_ij=d_ji를 갖는다. 비음수 Runge–Kutta 계수 및 양의 Patankar 분모를 사용하며, 분모는 해당 단계에서 구할 미지수와 독립이다. Lemma 2.6은 같은 전달을 생성·소멸 양쪽에 배정해 합의 보존을 증명한다. Lemma 2.7은 시스템 행렬의 전치가 엄격한 대각우세 M-matrix임을 사용해 역행렬의 비음성과 단계별 양수성을 증명한다. 정확도는 별도 분모 조건으로 다룬다.

이번 연구와의 대응은 **고정한 계수에서의 양의 선형 갱신과 보존 출력**이다. 다중 반응물을 하나의 수·에너지 사건으로 묶을 때에는 그 사건의 화학양론과 필요한 모든 보존 선형형식을 후보에서 직접 확인한다. L1의 비선형 공통 가중치와 L2의 선형 M-matrix 조건은 서로 다른 증명 구조로 기록한다.

## L3. H/He 화학 변화에 따른 온도식

U. Ziegler, *A chemical reaction network solver for the astrophysics code NIRVANA*, Astronomy & Astrophysics **586**, A82 (2016). DOI: [10.1051/0004-6361/201527262](https://doi.org/10.1051/0004-6361/201527262). 읽은 원문: [공식 HTML](https://www.aanda.org/articles/aa/full_html/2016/02/aa27262-15/aa27262-15.html), §§2.1–2.2, §3, 식 (3)–(13).

원문은 종별 수밀도와 열적 에너지의 반응 부분을 함께 다루고, 전자수는 전하 보존에서 결정한다. 고정 γ의 이상기체와 고정 부피의 source 부분에서 n_tot=Σ_s n_s+n_e 및 ṅ_e=Σ_s q_s R_s를 사용해 식 (12)를 얻는다:

$$
\dot T=\frac{\gamma-1}{k_Bn_{\mathrm{tot}}}S_e-
\frac{T}{n_{\mathrm{tot}}}\sum_s(1+q_s)R_s.
$$

식 (13)은 반응별 열적 source가 종별 반응과 같은 농도곱을 공유하도록 구성한다. 이 결과는 현재 열적 EOS에서 수 변화 항의 부호·단위와 사건별 열 연결을 대조하는 근거다. BASS_CR의 active 전자와 thermal 전자의 분할, cutoff 이관, 초과에너지 상태는 직전 채택 유도에서 가져와 이번 장부에 연결한다. NIRVANA의 source 적분기는 GRK4(3)T이며, 이번 후보의 양수성·수축 조건은 후보 자체의 증명으로 판정한다.

## L4. 자기일관적 화학–열 결합의 암시적 구성

Daniel R. Reynolds, John C. Hayes, Pascal Paschos, Michael L. Norman, *Self-Consistent Solution of Cosmological Radiation-Hydrodynamics and Chemical Ionization* (2009). DOI: [10.1016/j.jcp.2009.06.006](https://doi.org/10.1016/j.jcp.2009.06.006). 읽은 원문: [arXiv:0901.1110v3 PDF](https://arxiv.org/pdf/0901.1110), §§2.1, 3.2–3.2.4, 식 (19)–(43).

논문은 우주론적 화학종, 가스 에너지 보정, 복사 에너지를 하나의 암시적 비선형 잔차로 묶고, 선탐색을 갖춘 inexact Newton 방법으로 푼다. 미시물리 결합이 공간적으로 국소라는 점을 이용해 Schur complement에서 셀별 블록을 소거한다. 물리량 규모가 다른 변수에는 별도의 단위 정규화를 적용하고, 적응 시간 간격에는 정확도 판별량을 사용한다.

이번에는 **화학·열의 동시 피드백과 물리량별 정규화**를 방법론적 근거로 채택한다. 현재 BASS_CR 한 셀의 사상은 자신의 상태공간·정칙성·불변집합·수축 상수 아래에서 증명한다. 논문의 복사 확산 closure와 수치 허용오차는 이번 이론 가정에 추가하지 않는다.

## 근거와 실행 상태

- **literature-supported:** 위 원전에서 확인한 식과 해당 조건의 증명 또는 구성.
- **derived:** 현재 후보의 사건 장부·피드백·오차식은 후보 원문과 독립 심사에서 별도로 판정.
- SciSpace와 Exa 호출은 성공했다. Pan의 arXiv 직접 URL은 Exa가 처음에 서지 레코드만 반환하여, Exa의 ar5iv 원문으로 §§2–5를 읽었다. Kopecz–Meister와 Reynolds는 Exa가 PDF 본문을 반환했고, Ziegler는 공식 HTML 본문을 반환했다.
- 일반 웹 도구에는 일부 URL의 403·503·DisabledError 및 한 차례 무관한 검색 결과가 있었다. 이를 과학적 실패로 분류하지 않았으며, 해당 결과는 문헌 근거에서 제외했다. 채택한 네 원전의 필요한 본문은 Exa로 확인했다.

후속 후보 독립 심사는 이 문헌 대조와 별도 기록이다. 이 파일 작성자는 후보 생성과 작성자 검산 설계에 참여하지 않았다.

