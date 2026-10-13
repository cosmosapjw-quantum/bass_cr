# BASS_CR branch–geometry 루프: 좁은 원전 비교

- 연구 단위: CR-THEORY-BRANCH-GEOMETRY-20261013.
- 작성 역할: 외부 원전 조사 및 후보 비저자 독립 심사 담당.
- 문헌 조사는 완료됐으며 최종 과학 심사는 review/DECISION.json에 기록한다.
- 조회일: 원시 envelope의 실제 UTC를 따른다. 단위 ID의 날짜와 조회 시각을 동일시하지 않는다.
- 이 문서는 후보의 수식·코드·검산을 저술하지 않는다. 아래의 문헌 정리는 후보에 대한 승인 판정이 아니다.

## 1. 범위와 조사 기록

사용자가 지정한 SciSpace와 Exa를 모두 실제 사용하였다. SciSpace의 자연어 질문 2건에서 각각 10개 레코드를 받았고, Exa 원전 검색 3건에서 각각 4개 레코드를 받았다. Exa 본문 조회는 3건, 요청 URL은 합계 10개다. 중복 URL과 같은 논문의 여러 판본은 새 논문으로 세지 않는다. 이번에 추가로 실제 절을 읽은 원전은 아래의 **4개**다.

직전 FB/KC 루프에서 읽은 Pan–Chen–Fan, Kopecz–Meister, Ziegler, Reynolds 등과 Le–Cambier, SOL-KiT, Ricketson 등, Singleton–Brown은 재검색하지 않았다. 이번 검색으로 전체 분야를 망라했다거나 전 지구적 신규성을 입증했다고 주장하지 않는다. 원자 경계의 반응 후 선택을 직접 해결하는 정리를 이번 4개 문헌에서 확인하지 못했다는 것은 이 비교 집합에 대한 진술이다.

| ID | 새 원전 | 실제 읽은 범위 | 이번 연구와의 관계 |
|---|---|---|---|
| BG-L1 | Liu–Wang–Wang, 2024, arXiv:2402.03731 | §1 식 (1.1)–(1.10), §2 식 (2.1)–(2.7), §3 Theorem 3.1·Lemma 3.1와 경계 증명 전개 | 반응 궤적 좌표와 조건부 비선형 유일성의 비교 |
| BG-L2 | Torlo–Öffner–Ranocha, 2022 | §1 PDS 정의, §2.7, §3 식 (11)–(18), §4 Properties 4.1–4.2, §5 서두와 §5.1 식 (40)–(45) | 비음성·정상상태 보존·안정성·영농도 극한 정확도를 구분 |
| BG-L3 | Rendall, arXiv 1995 | §2 식 (2.1)–(2.9), 공변 운동량으로의 명시적 해와 가정 | 지정된 Bianchi I 배경에서의 massive 수송 및 응력 적분 |
| BG-L4 | Filbet–Sonnendrücker–Bertrand, 2001 | §2 식 (7)–(18), §2.1의 ENO 구분, §2.2 Propositions 2.2–2.3, §4 결론 | 보존적 characteristic remap과 비음 재구성의 비교 |

긴 외부 원문은 로컬 심사 cache인 inputs/literature/의 MCP 응답 envelope에만 보존한다. 배포용 EXTERNAL_REFERENCE_INDEX.json에는 요청, URL, 반환 건수, cache bytes와 SHA256만 담고 외부 초록·본문을 싣지 않는다. 이 bytes/SHA256는 **MCP 응답 JSON**의 값이며 원본 PDF 바이너리의 값이라고 주장하지 않는다.

## 2. BG-L1 — 반응 궤적의 variational implicit 선택

**원전:** Chun Liu, Cheng Wang, Yiwei Wang, *On a positive-preserving, energy-stable numerical scheme to mass-action kinetics with detailed balance*, arXiv:2402.03731v1 (2024-02-06). [원문 PDF](https://arxiv.org/pdf/2402.03731) · [arXiv](https://arxiv.org/abs/2402.03731).

논문은 가역 질량작용 반응의 농도를 \(c=c_0+SR\)로 나타낸다. 양의 상세평형 \(c^\infty\)를 가정하고 로그 자유에너지를 사용한다. 식 (2.1)은 역반응 mobility를 이전 농도에서 평가하고, 자유에너지의 반응 궤적 미분을 새 궤적에서 평가하는 첫째 차수 semi-implicit 식이다. 식 (2.2)–(2.5)는 이를 제한된 최소화 문제로 다시 쓴다. Proposition 2.1의 에너지 안정성은 해당 최소화 해의 자유에너지 감소를 뜻한다. Theorem 3.1은 \(M\le N\), \(\operatorname{rank}S=M\), \(c^n>0\) 조건에서 그 이산식의 유일한 허용 해를 진술한다. 논문은 다중 반응 증명을 \(M=2,N=4\)의 경계 분석으로 자세히 전개한다. [§§1–3](https://arxiv.org/pdf/2402.03731)

**적용한 비교:** 반응별 공통 궤적이 화학양론적 보존량을 묶는다는 구조와, 비선형 해의 선택에는 구체적인 목적함수·허용집합·유일성 가정이 필요하다는 원전 맥락을 확인했다.

**수입하지 않는 결론:** 이 논문의 자유에너지 감소는 BASS_CR의 열·비열·결합 에너지 합 보존과 같은 명제가 아니다. 현재의 비평형 일방향 충돌 채널에 상세평형, 모든 농도의 엄격한 양수성, 열 cutoff에 대한 로그 변분 구조를 새로 가정하지 않는다. 해당 Theorem 3.1을 원자 경계 branch의 유일성이나 zero-donor 처리의 증명으로 사용하지 않는다. 논문의 전체 증명을 별도 재심사했다는 주장도 하지 않는다.

## 3. BG-L2 — 비음성과 영농도 극한의 정확도

**원전:** Davide Torlo, Philipp Öffner, Hendrik Ranocha, *Issues with Positivity-Preserving Patankar-type Schemes*, *Applied Numerical Mathematics* **182**, 117–147 (2022), DOI [10.1016/j.apnum.2022.07.014](https://doi.org/10.1016/j.apnum.2022.07.014). [저자 PDF](https://davidetorlo.it/files/publications/Torlo2021StabilityPatankar.pdf) · [arXiv 판본](https://arxiv.org/html/2108.07347v4).

§2.7은 정상상태에서 한 걸음이 그 상태를 그대로 유지하는 성질을 정의한다. §3은 보존적인 두 성분 선형 PDS를 사용하며, §4는 정상상태를 넘지 않는 성질과 올바른 방향으로 이동하는 성질을 별도로 정의한다. §5의 정확도 논의는 고정된 양의 초기 하한에 대한 시간 간격 극한과, 초기 작은 성분 \(\varepsilon\)도 함께 사라지는 \(\varepsilon/\Delta t\to0\) 극한을 구분한다. §5.1 식 (42)–(45)는 MPE와 일부 MPRK 계수 선택이 이 극한에서 달라지는 이유를 실제 이산식으로 설명한다. [§§2.7–5.1](https://davidetorlo.it/files/publications/Torlo2021StabilityPatankar.pdf)

**적용한 비교:** 후보의 허용성, 보존, endpoint residual, 시간 정확도, branch continuation은 각각 그 명제의 가정과 증거로 판단한다. 하나의 성질에서 다른 성질을 자동 추론하지 않는다.

**수입하지 않는 결론:** 논문의 특정 Patankar 가족·선형 PDS에서 얻은 차수 저하를 이번 공통 capacity 사건법의 반례로 제시하지 않는다. 물리적 원자 cutoff의 불연속성이나 반응으로 질량이 변한 prefix 선택은 이 논문의 분석 대상이 아니다. 임의 시간 간격에서 모든 새 branch 해가 유일하다는 주장도 이 원전에서 얻지 않는다.

**서지 처리:** 저자 페이지의 상단은 2021을 표기하지만 같은 페이지의 recommended citation은 2022, 권 182, 117–147과 DOI를 명시한다. 저자 PDF는 2022-06-10 날짜다. 배포 서지는 이 명시된 출판 정보를 사용한다. HTML 변환본에 표시된 2026 날짜를 논문의 출판 연도로 사용하지 않는다. [저자 서지](https://davidetorlo.it/publication/2021-08-18-stability-patankar)

## 4. BG-L3 — 지정 Bianchi I 배경의 massive 운동량 수송

**원전:** Alan D. Rendall, *The initial singularity in solutions of the Einstein-Vlasov system of Bianchi type I*, arXiv:gr-qc/9505017v1 (1995-05-15). 이번에 확인한 판본의 날짜로 인용한다. [원문 PDF](https://export.arxiv.org/pdf/gr-qc/9505017v1.pdf) · [arXiv](https://arxiv.org/abs/gr-qc/9505017).

§2는 Gaussian proper time의 계량 \(ds^2=-dt^2+g_{ij}(t)dx^idx^j\), \(m\ge0\), 비음 분포를 사용한다. 원문의 일반 가정은 각 시각의 compact momentum support와 \(C^1\) 분포이며, 별도 절에서만 분포 일반화를 허용한다. 반변 운동량 좌표의 Vlasov 식 (2.5)을 공변 공간 운동량 \(p_i\)로 표현하면, 주어진 Bianchi I geometry에서 \(f=f_0(p_i)\)가 된다. 식 (2.9)의 에너지 밀도에는
\(\sqrt{m^2+g^{ij}p_ip_j}\)와 \((\det g)^{-1/2}\)가 함께 들어간다. 공간 응력 식 (2.7)은 같은 질량껍질 에너지의 역수를 가진다. 여기서 \(c=1\)인 원전의 단위를 따른다. [§2, (2.5)–(2.9)](https://export.arxiv.org/pdf/gr-qc/9505017v1.pdf)

**적용한 비교:** 공변 momentum 좌표에서의 분포 운반, proper-volume 밀도의 부피 인자, 질량껍질 에너지와 공간 응력의 서로 다른 moment 가중치를 확인했다. 새 코드의 변수명이 momentum이라고만 적혀 있어서는 이 세 좌표·측도 규약을 판별할 수 없다는 비교 기준을 얻었다.

**수입하지 않는 결론:** 이 논문은 Einstein 방정식도 푸는 문제를 포함하지만, 그 자가일관 기하·점근 정리를 지정된 배경의 BASS_CR 수송에 적용하지 않는다. \(T_{0i}=0\) 등 Einstein 해의 조건을 임의의 이동 관측자 분포에 자동 부과하지 않는다. smooth continuum 결과를 유한 원자 remap의 모든 moment 보존 증명으로 바꾸지 않는다. 이번 PDF 추출은 §2의 식 (2.9)까지를 포함한다. 이후 절 전체를 읽었다고 기록하지 않는다.

## 5. BG-L4 — 양의 보존 characteristic remap

**원전:** Francis Filbet, Eric Sonnendrücker, Pierre Bertrand, *Conservative Numerical Schemes for the Vlasov Equation*, *Journal of Computational Physics* **172**, 166–187 (2001), DOI [10.1006/jcph.2001.6818](https://doi.org/10.1006/jcph.2001.6818). [저자 PDF](https://www.math.univ-toulouse.fr/~ffilbet/Papers/paper03.pdf).

§2 식 (7)은 \(\partial_t f+\partial_x(uf)=0\)를 다루며 Lipschitz와 같은 속도 정칙성을 둔다. 양의 characteristic Jacobian을 포함한 식 (9)–(10)에서 셀 적분의 flux balance 식 (11)을 얻는다. §2.1 ENO 재구성은 비음 보장을 주는 PFC 재구성과 구별된다. §2.2 식 (13)–(18)의 slope correction과 Propositions 2.2–2.3은 셀 평균의 보존 및 재구성의 \(0\le f_h\le f_\infty\)를 명시한다. [§2](https://www.math.univ-toulouse.fr/~ffilbet/Papers/paper03.pdf)

**적용한 비교:** 출발 셀의 질량을 도착 셀에 옮기는 보존과 비음 재구성의 분리를 확인했다. 전체 입자수 보존을 주장할 때는 경계 flux의 처리도 포함해야 한다. 이 조건은 식 (11)의 내부 flux 상쇄에서 얻는 적용상 해석이다.

**수입하지 않는 결론:** 재구성의 maximum principle을 임의의 압축 수송 뒤 밀도의 최대값까지 불변이라는 주장으로 확장하지 않는다. 이 논문의 셀 평균 보존 정리에서 임의의 massive 에너지 함수·세 방향 응력·각분포까지 정확히 재현된다는 결론은 나오지 않는다. 기존 PFC 알고리즘을 새 코드가 그대로 구현했다고 주장하지 않으며, 새 remap의 해당 성질은 그 실제 정의로 독립 심사한다.

## 6. 문헌과 후보 판정의 분리

| 항목 | 문헌으로 확인한 맥락 | 이번 후보에서 독립적으로 판정할 대상 |
|---|---|---|
| 반응 변수를 통한 보존 | BG-L1의 화학양론적 궤적 표현 | 실제 사건 증분·원자 질량·열/비열 재결합 |
| 비선형 해 선택 | BG-L1의 특정 상세평형 변분 구조 | 후보가 명시하는 branch 정책, 존재·유일성·예산 종료 상태 |
| 극소 농도 | BG-L2의 특정 방법에 대한 두 극한의 구분 | 실제 zero-donor 정의와 주장된 정확도의 지지집합 |
| 기하 수송 | BG-L3의 공변 운동량과 invariant measure | 후보의 지정 metric, 관측자, 부피와 단위, 에너지·응력의 결속 |
| remapping | BG-L4의 셀 평균·비음성 | 실제 remap의 지지집합, 보존할 moment, 미보존량 또는 오차 표현 |

이 표는 확인 대상을 분리한 문헌 비교다. 후보의 성공·실패 결과나 검산 설계를 선행해 작성하지 않았다. 새 강한 no-go 주장은 없으며, “새 문헌에서 직접 정리를 찾지 못함”을 불가능성의 근거로 사용하지 않는다. 이후 독립 심사에서는 이 문서와 후보 원문을 각각 참조하고, 문헌상 정리와 이번에 유도·실행한 결과를 별도 지위로 기록한다.

## 7. 조회 상태와 재현 범위

8개 tool envelope는 모두 도구 수준의 오류 없이 반환되었다. 다만 “도구 성공”과 “본문 전체 추출”은 다르다. 첫 HTML 조회의 BG-L1/BG-L3 응답은 초록 수준이어서 PDF URL을 이어 조회했다. BG-L3 PDF 응답은 §2 초반까지만 추출되어 그 범위만 사용했다. BG-L2의 HTML·저자 PDF 응답도 요청 문자 예산에 따른 부분 추출이며, 위 표에 열거한 절만 실제 독해 범위로 삼았다. 검색에서 나온 다른 논문의 초록은 검색 후보이며 이번 4개 원전의 본문 증거를 대체하지 않는다.

외부 tool 실행은 문헌 조회뿐이다. 이 담당자는 새 과학 계산·수치 suite·Wolfram 계산을 실행하지 않았고 이전 accepted 자료를 변경하지 않았다.

