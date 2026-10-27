# R2: HeIII → HeII(1s) ground RR의 원전 자격과 소비 경계

작성: 2026-10-27 12:17 KST / 03:17 UTC  
수행 범위: 다음 연구 노드를 위한 R2 문헌·소스 독해. 이 문서는 R4–R10, C1–C10의 완료나 과학 계산의 실행을 주장하지 않는다.

## 결론

선택 A는 저장된 PR106 HeI 행렬의 대각 `K_diag`를 그대로 기준으로 삼아, 새 HeIII→HeII(1s) spontaneous RR hazard만 더하는 구조다. 이번 원전 독해는 그 새 채널에 필요한 **HeII 광이온화 단면적, Milne 관계, 전자 통계인자**를 지지한다. 기존 H1·HeI 결과, C23E 입력, REI151의 `saha_d=1`을 다시 계산하거나 교체할 이유는 발견하지 않았다.

HeII의 Verner row는 원래의 **54.42 eV** 임계값과 적합계수를 한 묶음으로 소비한다. 전자식 원소 He 데이터의 He4 귀속은 기존과 같은 **조건부 isotope mapping**이다. 원전은 이번 소비 계약에 동위원소별 질량 보정, 표적 반동, 유도 재결합, 모든 들뜬 상태, cascade·stopping·열화의 완성을 제공하지 않는다.

## 1. 실제 읽은 원전과 적용 위치

아래 페이지는 arXiv/저자 PDF의 인쇄 페이지 번호다.

| ID | 실제 독해한 원전·위치 | 확인한 내용 | 이번 재사용 |
|---|---|---|---|
| P1 | Verner, Ferland, Korista & Yakovlev (1996), *ApJ* **465**, 487, [DOI](https://doi.org/10.1086/177435), [원문 PDF](https://arxiv.org/pdf/astro-ph/9601009), §3 pp.4–5 Eq.(1), Table1 p.21 | ground-state PI 적합식, eV/Mb 단위, HeII `Z=2,N=1` row, 비상대론적 범위 | 고정된 표와 provider를 그대로 소비한다. |
| P2 | Verner & Ferland (1996), *ApJS* **103**, 467, [원문 PDF](https://arxiv.org/pdf/astro-ph/9509083), §1 pp.1–3, §2 pp.3–6, Eqs.(4)–(5) | RR의 species 이름은 생성된 이온을 뜻한다. ground와 excited 합을 구별하며, ground에는 Milne 관계를 사용한다. Eq.(4)/Table1은 총 thermal RR이다. | 총 thermal fit을 비열적 ground hazard로 바꾸어 넣지 않는다. |
| P3 | Nahar (2021), *Atoms* **9**, 73, [DOI](https://doi.org/10.3390/atoms9040073), [저자 PDF](https://www.astronomy.ohio-state.edu/nahar.1/papers/atoms-hyd-pirc.pdf), §2.2 p.7 Eqs.(30)–(31), p.8 Eq.(36) | detailed balance의 모멘텀·통계인자, 개별 상태 RR과 전체 bound-state 합의 구분 | 아래 ground-state 역과정 식의 명시적 출처. |
| P4 | NIST, [HeII energy levels](https://physics.nist.gov/PhysRefData/Handbook/Tables/heliumtable6.htm), ground row | `1s, ²S, J=1/2, 0 cm^-1` | bound 전자 통계무게 `2J+1=2`의 원자료. |

추가로 저자의 [photoionization 자료 페이지](https://www.pa.uky.edu/~verner/photo.html)와 [recombination 자료 페이지](https://www.pa.uky.edu/~verner/rec.html)를 읽어 논문의 서지와 자료 종류를 확인했다. P2 arXiv 원고는 1995년 제출본이고 저널 출판연도는 1996년이다.

### P1의 식·단위·row

\[
x=\epsilon/E_0-y_0,\qquad y=\sqrt{x^2+y_1^2},
\]
\[
\sigma_{\rm PI}(\epsilon)
=10^{-18}\sigma_0[(x-1)^2+y_w^2]\,
y^{P/2-5.5}(1+\sqrt{y/y_a})^{-P}\ {\rm cm}^{2}.
\]

\(\epsilon,E_0\)는 eV, \(\sigma_0\)는 Mb이며 \(1\,{\rm Mb}=10^{-18}\,{\rm cm}^{2}\)다. Table1 p.21의 HeII 세 번째 데이터 행을 렌더 이미지에서 직접 확인했다.

| Z | N | I/eV | Emax/eV | E0/eV | σ0/Mb | ya | P | yw | y0 | y1 | 품질 표기 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | 1 | 54.42 | 50000 | 1.720 | 13690 | 32.88 | 2.963 | 0 | 0 | 0 | A |

P1 §3은 H-like/He-like의 ground shell을 1s로 한정하고 표에 Emax=50 keV를 둔다. Class A hydrogenic **적합 rms**는 0.2%보다 작다고 기술한다. 이 수치를 모든 에너지에서의 엄밀한 상한, He4 질량 오차, 또는 전체 수송·열화 모델의 오차로 해석하지 않는다. 이번 소비자는 자신의 고정 에너지 격자와 표의 지원 범위를 함께 지켜야 한다.

### P2의 ground/total 구분

P2 §1에서 “HeII의 RR”은 HeIII가 전자를 포획해 HeII를 만드는 반응이다. ground RR은 개별 광이온화 역과정에서 얻고, excited contribution은 별도 합이다. 총 PI만 있는 자료는 residual-ion channel을 구분하지 못해 Milne 사용에 문제가 있을 수 있다고 설명한다. HeII hydrogenic ground 역과정은 bare residual ion을 가지므로 여기에서 새로운 들뜬 core channel을 추가하지 않는다.

P2 Eq.(4)의 열적 rate fit과 Table1을 \(\sigma_{\rm RR}(E)\)나 tagged-electron hazard로 사용하지 않는다. 비열적 분포의 현재 계산에는 선택한 ground 단면적을 직접 소비한다. Maxwell 평균이나 새로운 thermal quadrature는 이번 R2에서 수행하지 않았다.

## 2. Milne 관계와 d=1의 대응

P3 p.7 Eq.(30)의 PDF를 시각 확인했다. 자동 텍스트 추출은 분수 배치를 잃으므로, 추출 문자열의 순서만으로 모멘텀 인자를 읽으면 안 된다. 실제 식은

\[
\sigma_{\rm PI}\frac{g_b}{p_e^2}
=\sigma_{\rm RR}\frac{g_i}{p_\gamma^2},
\qquad
p_\gamma=\epsilon/c,\quad p_e^2=2m_eE.
\]

따라서 P3 Eq.(31)은

\[
\sigma_{\rm RR}(E)
=\frac{g_b}{g_i}\frac{\epsilon^2}{2m_ec^2E}
  \sigma_{\rm PI}(\epsilon),
\qquad \epsilon=E+I.
\]

여기에서 \(g_b\)는 광이온화되는 bound atom의 전자 통계무게, \(g_i\)는 residual ion의 전자 통계무게다. 원문은 이를 각각 \(g_i,g_j\)로 쓴다. 위 표기는 project의 ion/bound 구분과 충돌하지 않도록 이름을 바꾼 것이다.

P4의 \(J=1/2\)로부터 \(g_b=2\). bare HeIII의 전자 상태는 하나이므로 \(g_i=1\)이다. 후자는 빈 전자계의 상태 수를 세는 적용 단계이며 NIST 표의 직접 인용은 아니다. project convention

\[
d=\frac{2g_i}{g_b}=1,\qquad
\sigma_{\rm RR}(E)=
\frac{\epsilon^2}{d\,m_ec^2E}\sigma_{\rm PI}(\epsilon)
\]

가 REI151의 HeII `saha_d=1`과 일치한다. 전자 spin factor를 이 식에 한 번 더 곱하지 않는다. P3 Eq.(36)은 모든 bound-state rate를 합해야 total RR이 됨을 명시하므로, 1s 식만으로 total RR을 완성했다고 말할 수 없다.

### 기존 CR 단위계에 대한 적용

\(E_{\rm eV}>0\), \(\epsilon_{\rm eV}=E_{\rm eV}+54.42\),
\(M_{\rm eV}=m_ec^2/q_{\rm eV}\)로 놓으면

\[
\sigma_{\rm RR,cm^2}
=\frac{\epsilon_{\rm eV}^2}{d\,M_{\rm eV}E_{\rm eV}}
 \sigma_{\rm PI,cm^2}(\epsilon_{\rm eV}),
\]
\[
\lambda_{\rm HeIII}
=n_{\rm HeIII,cm^{-3}}\,
100\sqrt{2E_{\rm eV}q_{\rm eV}/m_e}\,
\sigma_{\rm RR,cm^2}.
\]

\(q_{\rm eV}\)는 J/eV 변환이고 100은 m/s→cm/s 변환이다. \(\lambda\)의 단위는 s\(^{-1}\)다. 표적은 포획 이온 HeIII이며, 배경 전자 밀도를 대신 곱하지 않는다. 고정 bath의 \(\mathrm{n}_{HeIII}=0.01\,{\rm cm}^{-3}\)는 **project 입력**으로 재사용하며 문헌의 측정값으로 표현하지 않는다. CR의 전자 질량 상수와 REI151의 상수가 다른 것은 이미 존재하는 계약 차이이므로 여기서 통합하지 않는다.

이 식은 \(E=0\)의 수치 평가나 임의 rate floor를 정당화하지 않는다. 소비 격자의 양의 에너지 조건, \(\epsilon\le50{,}000\) eV 조건 및 비상대론적 해석을 별도로 확인한다.

## 3. 보존할 물리·소스 경계

| 항목 | 이번 노드에서 허용되는 진술 | 계속 미완료인 내용 |
|---|---|---|
| 채널 | HeIII + e → HeII(1s) + γ의 source-qualified spontaneous ground RR | excited-state RR, stimulated RR, 모든 상태의 total RR |
| 원소/동위원소 | 원소 He 전자 단면적을 기존 조건부 He4 mapping으로 소비 | isotope-specific fit, 유한 핵질량·동위원소 shift 보정 |
| 표적 운동학 | stationary-heavy-target, zero recoil 계약 | ion thermal motion, recoil/relativistic 보정 |
| 방출 광자 | 이 계약 안에서 \(E_\gamma=E+I\)인 event reward | 방출각, 재흡수, cascade, 외부 photon 전파 |
| 에너지 장부 | 전자 제거, bound internal energy, photon reward의 분리 | 실제 baryon stopping·thermalization·heating 완료 |
| 미시 공급자 | 고정 WU/REC/HE 유효범위와 isotope mapping 보존 | 다른 원소·동위원소 또는 새로운 유효범위로의 확장 |

NIST의 더 정밀한 분광 이온화 에너지로 54.42 eV만 바꾸면 P1의 적합계수와 입력 정의를 섞게 된다. 이번 선택은 원래 row를 유지하는 것이다. HeI에 이미 있던 source qualification과 rounding loss도 그대로 상속한다.

## 4. 선택 A의 재사용 연결

- 과학 기준: PR106 S=`4caf4273eefd51f2c605a8667c3533d8489dd0f5`, 문서 기준 D=`b11b2e9255f2b10fb5582376412e045bd1e9151c`.
- 기존 NPZ의 **저장된 HeI `K_diag`**를 새 baseline으로 사용한다. H1 원본에서 HeI 대각을 재구성하지 않는다.
- 새 항만 \(\operatorname{diag}\lambda_{\rm HeIII}\)로 추가한다. 독립 Decimal 검산도 `Decimal(stored_HeI_K_diag)+Decimal(new_lambda)`라는 동일한 선택을 명시한다.
- 고정 C23B/C23E 표와 provider를 가져오되 기존 source projection, H1 solver, HeI solver를 다시 실행하지 않는다.
- 원전 독해가 새로운 solver 결과, 새 bound의 증명, source-weighted event export의 검증을 대신하지 않는다. 그 내용은 root의 후속 R4–R10/C 단계에 속한다.

네이티브 표 SHA256:
`a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`.

고정 photo provider SHA256:
`71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d`.

REI151 contract SHA256:
`ce7ba9f2c4114098ab1f36e3f2da26e4999fb947e742f66d4383cb61855a2aec`.
REI151 source 기준은 `8a4f5df46f6e3058f5e685b85cc1cf3c20926368`이다.

## 5. 검색·독해 영수증과 제한

SciSpace에 완전한 자연어 질문을 보내 10개 후보를 받았다. Exa는 세 방향으로 8+7+5개 결과를 제공했고, 실제 반환된 20개 URL을 검토했다. URL 수는 서로 다른 논문 수가 아니다. 원전 3편의 전문을 가져와 위 식·표·범위를 읽었고, 저자 자료 페이지 2개와 NIST 표 1개도 읽었다.

SciSpace에는 P1의 arXiv 사본을 2022년으로 표시하고 저자 명단을 잘못 연결한 중복 레코드가 있었다. P1의 첫 페이지와 저자 페이지로 1996년 논문·네 저자를 확인해 교정했다. HeI 논문 한 후보의 DOI 불일치도 발견했지만 이번 HeII 결론에는 채택하지 않았다. 검색 메타데이터는 발견 도구이며 원전의 권위를 대체하지 않는다.

P1 Table1과 P3 Eqs.(30)–(31)은 로컬 PDF 렌더에서 직접 시각 확인했다. PDF 및 이미지 해시·경로는 `R2_SOURCE_MAP.json`과 `private_reading/DOWNLOADS.json`에 남긴다. 저작권 있는 원문 전문을 공개 연구 산출물에 재전재할 필요는 없다. 공개에 필요한 것은 이 작성 노트, 원문 링크, 최소 메타데이터와 source hashes다.

이 child 작업에서 원격 변경·게시·백업·과학 계산·기존 실행 재현은 모두 **0**이다. N6/N7 gate, 과거 UNKNOWN_NO_ACK 및 예산을 바꾸지 않는다. 새로운 strong no-go를 주장하지 않는다. 백업·게시·DAG 갱신은 root가 맡는다.

