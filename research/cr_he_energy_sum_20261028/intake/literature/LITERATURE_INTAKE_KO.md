# R2 문헌 조사 — He 사건의 원자별 에너지합 support

관찰 시점: 2026-10-28 15:45 KST (06:45 UTC). 이 문서는 다음 연구 단위의 문헌 입력이며, 자체적으로 새 과학 노드를 실행하거나 완료 처리하지 않는다.

## 결론

고정된 birth-energy bin 전체를 Cartesian pair로 허용하는 병렬 CR_HE_PAIR_SUPPORT와 구별되는 연결은 원자별 조건 `E_a + E_b <= K`다. 이 조건은 한 bin 안에서도 허용 pair를 나누고, 같은 원자 두 leg의 허용 조건 `2 E_a <= K`도 결정한다. K를 명시적인 조건부 pair-energy support 또는 acceptance 입력으로 두면 문헌의 energy-sharing 정의와 직접 연결할 수 있다. 실제 retained source의 K, exclusive kernel, C, outside-partner response, full-source native25를 제공하는 수치 자료는 이번 문헌 조사에서 취득하지 않았다.

Retained PHYS02 revision은 `4ca5a90de79c8fb82a25fd9e83615bec0dfa870b`, 선행 event-union science S는 `406783036c26e71f3b85568adcfb5e163b012ab1`이다. 실제 projectile 분포·가중치가 이 조사에 아직 공급되지 않았으므로 문헌의 700 keV 또는 6 MeV를 해당 source의 projectile 조건으로 지정하지 않았다.

## 조사 범위와 실제 읽기

Exa 검색 6회에서 요청 슬롯 50개와 실제 URL 결과 50개를 받았고, exact URL 기준 44개였다. 이는 논문 44편의 전문 독해 수가 아니다. SciSpace 두 검색은 각각 논문 메타데이터·초록 10개를 반환했다. Exa fetch는 4회, URL 요청 9개다. DOI의 Ambrosio2015 직접 fetch는 timeout이었으며 기관 저장소 author proof로 복구했다. 그 추출은 논문 전체 10쪽 중 proof pp.1–4에서 끝난다.

Guan–Bartschat의 arXiv HTML/PDF URL은 처음에는 초록·서지정보를 반환했으며, 이후 ar5iv URL에서 Eq.(1)–(6), 결과·그림 설명·결론·참고문헌의 전체 텍스트를 읽었다. 그림의 픽셀 판독이나 수치 digitization은 수행하지 않았다. Koperberg의 PDF 텍스트는 pp.1–10, Theorem 1, Proposition 4 및 Proposition 6과 해당 논증을 읽었다. López2014는 전문 텍스트를 취득했지만 이번 채택에는 초록·서론 및 검색 결과의 지정된 kinematic 사례만 사용했다. Bertsimas–Popescu는 도입부·문제 정의의 부분 추출만 검토했다.

## 물리 원전과 현재 입력의 대응

| 원전 | 직접 확인한 범위·내용 | 현재 연구에서 사용할 연결 |
|---|---|---|
| [Ambrosio et al., PRA 92, 042704 (2015)](https://doi.org/10.1103/PhysRevA.92.042704) — [기관 author proof](https://ri.conicet.gov.ar/bitstream/handle/11336/149995/CONICET_Digital_Nro.db5f7a22-2305-4d7e-a3a9-7136b0e61907_J.pdf?sequence=11) | Proof pp.1–4. Eq.(13)은 두 electron energy와 방향 및 projectile 산란 방향에 대한 FDCS를 정의한다. Projectile final energy는 total-energy conservation에 연결된다. 서론 lines150–153은 total excess 6 eV의 3+3 및 1.5+4.5 eV 분배를 설명한다. Fig.1은 700 keV proton, 10+10 eV를 명시한다. | 두 전자 에너지합을 조건으로 고정하는 물리적 의미와 정규화 convention의 근거. 본문의 고정 excess-energy slice와 연구자가 선언하는 누적 support `<=K`의 수학적 계약을 구별한다. 논문의 부분 FDCS를 원 source 전체에 자동 정규화하지 않는다. |
| [Guan & Bartschat, PRL 103, 213201 (2009)](https://doi.org/10.1103/PhysRevLett.103.213201) — [ar5iv 본문](https://ar5iv.labs.arxiv.org/html/0906.1985) | Eq.(5)는 impact parameter에 적분한 channel cross section, Eq.(6)은 두 electron energy를 적분한 angular DDCS다. 6 MeV proton 사례에서 실험의 각 electron cutoff 25 eV와 수렴에 필요한 약 400 eV 범위를 구별하며, 제한된 신호는 수렴 DDCS의 약 1/3이라고 보고한다. | Selection acceptance와 full channel normalization을 구별해야 한다는 구체적 사례. 같은 논문의 적분량도 acceptance에 따라 의미가 달라진다. 이 수치를 retained 0.1–10 eV support의 보정계수로 쓰지 않는다. |
| [Ambrosio et al., EPJD 71 (2017)](https://doi.org/10.1140/epjd/e2017-70713-x) — [공식 초록](https://epjd.epj.org/articles/epjd/abs/2017/05/d160713/d160713.html) | 6 MeV proton, coplanar FDCS, 제한된 energy/momentum acceptance와 상대 scale의 실험 비교. | Joint-energy/angle acceptance를 명시할 필요를 지지한다. 현재 source에 맞는 absolute joint array를 제공받은 상태는 아니다. |
| [López, Otranto & Garibotti, PRA 89, 062709 (2014)](https://doi.org/10.1103/PhysRevA.89.062709) — [기관 PDF](https://ri.conicet.gov.ar/bitstream/handle/11336/76796/CONICET_Digital_Nro.86689f26-e73f-4ffb-bdb5-d61058c68a2b_A.pdf?sequence=2) | 초록·서론에서 first/second Born terms 및 independent-electron/independent-event 모델을 구별한다. 이온-impact FDCS의 electron acceptance 제한과 postcollision correlation의 역할을 설명한다. | 같은 inclusive marginal에 단순 독립 pair를 임의 부여하는 선택에 필요한 추가 모델 가정을 보여 준다. TS-2 등의 특정 모델을 retained kernel로 채택하지 않았다. |
| [Foster, Colgan & Pindzola, JPB 41, 111002 (2008)](https://doi.org/10.1088/0953-4075/41/11/111002) | 초록의 6 MeV proton angular DDCS와 unrestricted electron-energy 결과를 확인했다. Guan2009 본문은 이 논문 Fig.2의 도표·크기 오류와 정정을 언급한다. | 원 수치를 채택하려면 [2009 erratum](https://doi.org/10.1088/0953-4075/42/14/149801)을 함께 읽어야 한다. 이번 조사에서는 수치 kernel을 추출하지 않았다. |

2023–2026 검색에서 나타난 Spicer2023 및 2026 single-ionization 논문, 2025 He2+ projectile 논문, photo/electron-impact 논문은 현재 proton-impact double-event 입력으로 채택하지 않았다. SciSpace의 arXiv0906.1985 결과에 붙은 2022 날짜는 원 논문의 2009 출판일로 사용하지 않았다.

## 수학 원전과 구체적 연결

[Koperberg, Couplings and Matchings: Combinatorial Notes on Strassen's Theorem, arXiv:2202.02092v1 (2022)](https://arxiv.org/pdf/2202.02092)의 Theorem 1은 유한 두 주변분포와 허용 관계 R에 대해 support를 R에 두는 coupling의 존재를 모든 부분집합의 질량-이웃질량 조건으로 특징짓는다. Proposition 4는 같은 내용을 weighted bipartite graph의 vertex mass와 비음성 edge mass로 표현한다. Proposition 6은 허용 support 밖의 질량을 허용한 deficiency 판정을 준다.

부모 연구가 검토하는 energy-threshold 관계에서는 low/high 원자 집합 사이 이웃이 에너지 순서에 따라 중첩된다. 따라서 일반 부분집합 조건을 에너지 tail의 누적 질량 조건으로 축약하는 유도와 sparse witness construction이 구현의 구체적 목표가 된다. Low/high 총질량이 다를 때에는 residual singles에 대응하는 slack/dummy 확장을 명시해야 한다. 같은 low atom의 diagonal double은 두 electron leg를 사용하므로 pair 질량과 marginal 질량의 2배 관계를 보존해야 한다.

이 matching/coupling 원리는 선행 정리다. 이번 프로젝트의 새 작업은 retained atomwise source에 비-Cartesian energy support를 결속하고, sharp bound·exact certificate·동일 상태의 consumer를 실제 구현하는 데 있다. 일반 matching 원리의 신규성을 주장하지 않는다. 후보식 `d_max=(mass_low + m_LH)/2`의 증명, endpoint 구성, equality boundary와 empty-support 처리는 부모의 R5/R6 의무로 남겼으며 이 문헌 intake에서 과학 실행으로 처리하지 않았다.

[Bertsimas & Popescu, SIAM J. Optim. 15, 780–804 (2005)](https://doi.org/10.1137/S1052623401399903)의 moment-constrained sharp bounds는 향후 실제 pair-energy moments가 공급될 때의 배경 원전으로만 정리했다. 현재 threshold-support 단위에 일반 SDP나 추가 moment closure를 도입할 필요는 없다.

## 채택·실행 경계

- Same-source absolute exclusive kernel 또는 다운로드 가능한 joint numerical grid는 취득하지 못했다. 이 결과는 이번 검색·읽기의 상태이며 문헌 전체에 대한 부재 정리가 아니다.
- K는 조건부 support/acceptance parameter다. 실제 K, actual exclusive D/C 및 physical full native25는 계속 null이다.
- 고정 marginal을 유지한다면 support가 막은 pair leg는 선언된 모델에 따라 singles로 남길 수 있다. 이 선택과 실제 physical branching fraction은 서로 다른 입력이다.
- Retained photon·RR once-only 포트, proper history, 같은 상태의 nb와 source factor ownership을 변경할 근거가 새로 생기지 않았다.
- 과학 코드·수치·CAS 실행, 외부 게시·백업은 이 분담에서 수행하지 않았다. 원문 검색 응답은 내부 조사 증거이며 공개 게시에는 본 자체 요약, 원전 URL, 조회 결과의 digest만 사용한다.

## 파일

`SEARCH_LEDGER.json`은 실제 query·결과수·한계, `SOURCE_CATALOGUE.json`은 반환된 검색 metadata를 보존한다. `LOCAL_RESPONSE_HASHES.json`은 취득한 응답 파일의 bytes/SHA이며, 원 PDF 전체의 해시라는 주장은 하지 않는다.

