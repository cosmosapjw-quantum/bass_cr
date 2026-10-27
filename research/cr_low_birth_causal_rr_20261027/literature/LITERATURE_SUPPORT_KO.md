# 유한 ramp forcing 계산법의 원 논문 대조

## 결론과 채택 범위

SciSpace의 자연어 검색 2건과 Exa 검색 3건으로 후보를 찾고, Al-Mohy–Higham (2011)과 Fox–Glynn (1988)의 저자 제공 원 논문 PDF를 직접 읽어 대조했다. 두 PDF에 대한 실제 전체 GET의 크기·SHA256은 `PRIMARY_ACQUISITION.json`에 있다. 이 조사는 계산법의 근거를 보강한다. PHYS02의 source, Milne RR, Coulomb fit, isotope 조건, 100 K 물리 상태 또는 오차를 새로 검증하거나 기존 계산을 재실행한 것이 아니다.

주 유도는 `../theory_survey/THEORY_PROPOSAL_KO.md`의 작성자 `/root/theory_review`가 담당한다. 이 조사자는 문헌·공급자 근거를 정리했으며, 주 유도 및 production 구현의 작성자가 아니다. 이후 R6 독립 검토는 별도 단계로 남아 있다.

| 근거 | 실제 읽은 위치 | 채택할 내용 | 유지할 한계 |
|---|---|---|---|
| Al-Mohy & Higham, SIAM J. Sci. Comput. 33(2), 488–511 (2011), DOI [10.1137/100788860](https://doi.org/10.1137/100788860) | §2, 식 2.2–2.10, Theorem 2.1; §4 Lemmas 4.1–4.2 | 다항식 forcing의 φ 함수 및 보조 상태를 붙인 matrix-exponential action 표현; 전체 dense exponential을 만들지 않는 계산 | normwise backward/forward error는 성분별 양성이나 outward interval을 자동 보장하지 않는다. 특이 생성자에는 entire φ 함수를 사용하며 역행렬로 정의하지 않는다. |
| Fox & Glynn, Commun. ACM 31(4), 440–445 (1988), DOI [10.1145/42404.42409](https://doi.org/10.1145/42404.42409) | Proposition 1; §2 WEIGHTER 및 roundoff 설명; §3과 §4–6의 절단 범위 | Poisson tail 제어, 양의 scaled recurrence, 절단 오차와 부동소수점 오차의 분리 | Proposition 1은 **남긴 가중치를 재정규화한** 분포의 정확산술 기대값 오차에 관한 것이다. 현재 ramp식의 비정규화 확률과 그대로 바꿀 수 없다. |
| Gross & Miller, Operations Research 32(2), 343–361 (1984), DOI [10.1287/opre.32.2.343](https://doi.org/10.1287/opre.32.2.343) | 실제 publisher HTML abstract | CTMC randomization의 transient·누적 occupancy·event count 적용에 대한 원 논문 배경 | 전체 PDF를 확보하지 않았으므로 상세 정리·ramp식·roundoff bound를 읽었다고 하지 않는다. |
| Jensen, Scandinavian Actuarial Journal 1953(sup1), 87–91, DOI [10.1080/03461238.1953.10419459](https://doi.org/10.1080/03461238.1953.10419459) | DOI metadata/abstract; 직접 publisher 접근은 403 | 서지상 역사적 근거 | 원문 정리의 가정과 증명은 미확인이다. |

## 제안 계산법에 적용할 때의 구체적 구분

1. **Ramp 식은 이번 유도의 결과다.** 제안 식 15–16의 \(w_k(x)\), Poisson 지수의 두 칸 이동, 그리고 \(N_{\rm inj}\Pr[\mathrm{Pois}(x)\ge M-1]\) 누락 질량식은 논문의 문구를 가져온 것이 아니다. 일반 uniformization을 실제 \(q(t)=tA\)에 적분한 이번 유도의 specialization으로 표시해야 한다.
2. **재정규화가 누락 질량을 바꾼다.** Fox–Glynn의 \(w_j/W\)는 남긴 확률 질량을 1로 만든다. 현재 finite-ramp 절단식은 실제 비정규화 \(p_n\)을 사용한다. 재정규화 알고리즘을 쓰려면 이 차이와 해당 오차를 따로 전파해야 한다. Proposition 1의 \(2\epsilon\|f\|_\infty\) bound를 현재의 exact missing-mass identity라고 쓰면 안 된다.
3. **확률 보존은 count 상태에 관한 명제다.** active electron + cutoff + RR-H + RR-He count 상태로 구성한 \(P\)의 column stochasticity가 먼저 필요하다. 에너지 ledger의 수치와 count를 섞은 column을 확률 분포로 해석하지 않는다. 에너지 및 photon tail bound에는 이 물리 모델의 경로당 reward 상한이 별도로 필요하다.
4. **양의 절단과 기계 계산의 인증은 다르다.** 정확산술에서 양의 truncation과 Poisson tail bound가 성립해도, 실제 floating-point 합산·underflow·exponential 계산 오차와 outward rounding은 별도다. Al-Mohy–Higham의 normwise 안정성도 작은 성분의 상대 오차나 signed ledger의 성분별 양성을 자동 인증하지 않는다.
5. **가중치 비용과 전체 propagation 비용을 구별한다.** Fox–Glynn scalar weight 생성의 비용을 \(P^k A\) 전체 action의 비용이라고 쓰지 않는다. 실제 \(\nu T\), 필요한 power 수, sparse action, coordinator 비용을 포함한 새 bounded run의 계측은 root가 담당한다.
6. **유한 clock과 물리 수용성은 별도다.** φ/augmented action은 알려진 유한 source history를 처리하는 계산 표현을 제공한다. 이 문헌만으로 100 K source를 10000 K response에 붙이거나, 없는 \(n_b\), 시간 이력, spectrum, 불확도를 생성할 수 없다. Retained photon과 heating의 소유권도 기존 계약을 유지한다.

## 실제 취득과 서지 충돌

- Al-Mohy–Higham 저자 PDF: <https://eprints.maths.manchester.ac.uk/1591/1/alhi11.pdf>. 전체 GET 450,177 bytes, SHA256 `a8bc1d282cbda4aad92d231c84a656482def0f4d1747a92e140c6b32ef4e3c1b`.
- Fox–Glynn 저자 PDF: <https://web.stanford.edu/~glynn/papers/1988/FG88.pdf>. 전체 GET 557,663 bytes, SHA256 `c24f491da9943246229e67840ecbafb02d3c6879627e1563fab9eab431110b00`.
- Al-Mohy–Higham의 SciSpace 날짜와 Exa DOI 날짜는 서로 다르다. 원 PDF의 electronically published 2011-03-01, 연도·권·호·쪽을 채택했다. 원 문서와 검색 discovery metadata를 혼동하지 않는다.
- 원문 전체를 산출물에 재배포하지 않는다. 검색 입력·서지 discovery, 취득 영수증, 읽은 위치와 채택 범위를 저장했다. 참고문헌의 세부 원문 확인은 위 URL 및 DOI로 재현할 수 있다.

## 상태

`SOURCE_CONTRAST_COMPLETE_SCOPED`; R6 검토는 미실행. 이 조사의 scientific execution, source quadrature replay, old science replay는 모두 0이다. 취득·문서화 CPU는 계측하지 않았으며 0으로 표기하지 않는다. 중앙 완료 수와 물리 활성화 상태에 대한 효과는 없다.
