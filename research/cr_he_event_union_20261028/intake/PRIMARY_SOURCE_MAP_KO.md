# Primary-source 읽기 범위 복원과 실제 He joint source의 경계

기록 유형: `RECONSTRUCTED_FROM_ACTUAL_PRIOR_RETRIEVAL`. 호스트 리셋 전 같은 대화에서 실제 SciSpace·Exa·web 검색과 primary abstract/manuscript extract를 읽었다. 원 응답 파일은 리셋으로 손실됐다. 아래는 대화에 남은 실제 읽기 결과의 복원이며, 새 GET·새 PDF SHA·원문 전체 독해를 주장하지 않는다. 검색결과 또는 manuscript text extraction은 original PDF byte identity가 아니다.

## 1. Retained inclusive electron source

**M. E. Rudd et al., Reviews of Modern Physics64,441–490(1992), DOI10.1103/RevModPhys.64.441.**

- Primary institutional manuscript: https://digitalcommons.unl.edu/cgi/viewcontent.cgi?article=1037&context=physicsgay
- 실제 읽은 범위: 이전 PR111에서 채택한 §II의 DDCS convention 및 관련 extracted text를 재사용했다.
- 핵심 범위: 검출된 electron count를 incident proton에 대해 정의한 inclusive electron differential cross section이다. 한 electron marginal로부터 single/double parent event 분해나 두 electron의 joint distribution을 유일하게 얻지 못한다.
- 채택: 기존 PHYS02 source의 inclusive electron normalization·attribution을 유지한다. Exclusive event kernel 또는 fully differential joint spectrum이라고 부르지 않는다. Source error가 확정됐다고 주장하지 않는다.

## 2. Exclusive double-ionization을 직접 다루지만 source state와 같지 않은 문헌

| 문헌 / primary URL | 실제 읽은 범위와 관찰 | 이 CR 단위의 채택 한계 |
|---|---|---|
| F. Ambrosio et al., PRA92,042704(2015), https://journals.aps.org/pra/abstract/10.1103/PhysRevA.92.042704 | APS abstract 및 기관 accepted manuscript 첫4pages의 text extraction. Eq13은 두 electron energy·direction을 가진 FDCS. Fig1은 **700keV proton와 10+10eV electrons**. Introduction은 total excess6eV의3+3 및1.5+4.5 사례. | 최초 추측1MeV를 폐기하고700keV로 교정한다. 두 electron 조합이 직접 필요한 source라는 개념적 근거다. 현재 PHYS02 projectile/history/0.1–10eV 전체 support의 absolute joint array를 제공한 것으로 사용하지 않는다. |
| X. Guan and K. Bartschat, PRL103,213201(2009), https://link.aps.org/doi/10.1103/PhysRevLett.103.213201 ; https://arxiv.org/abs/0906.1985 | APS abstract와 ar5iv full-text extraction. Total 결과의 projectile range3keV–6MeV. Eq5는 impact-parameter 적분 total. Angular DDCS Fig4는 **6MeV**이며 일부 experimental comparison은 relative normalization. | 넓은 total-energy range를 native1–4MeV,0.1–10eV의 complete absolute joint grid가 존재한다는 증거로 쓰지 않는다. |
| D. Fischer et al., PRL90,243201(2003), https://link.aps.org/doi/10.1103/PhysRevLett.90.243201 | 실제 abstract:6MeV proton의 kinematically complete double-ionization experiment. | Fully differential 사건 측정의 실재를 뒷받침한다. 현재 projectile/support/time state의 numerical kernel을 대체하지 않는다. |
| F. Ambrosio et al., EPJD71,127(2017), https://link.springer.com/article/10.1140/epjd/e2017-70713-x | 실제 abstract:6MeV, coplanar FDCS, finite momentum-transfer bins, relative comparison. | 동일 atomic species라도 energy·angular acceptance·normalization이 다르므로 conditional scientific reference에 한정한다. |

2015 accepted-manuscript URL은 https://ri.conicet.gov.ar/bitstream/handle/11336/149995/CONICET_Digital_Nro.db5f7a22-2305-4d7e-a3a9-7136b0e61907_J.pdf?sequence=11 이다. 읽힌 text와 original PDF bytes는 구분한다.

## 3. Discovery만 수행한 문헌과 실패

Andersen et al. PRL57,2147(1986)의 total0.5–5MeV 및 Olson PRA40,2843(1989)의 differential-angle 자료는 discovery 단계였다. Full primary를 읽었다고 주장하지 않는다. 당시 Exa DOI route의406, accepted URL not-found, arXiv route disabled, PDF403/not-accessible 응답도 있었고 성공한 primary text extraction과 혼합하지 않는다. Root가 이후 일부 APS/ar5iv/Rudd URL을 직접 열려던 시도는 실패했으므로 그것을 새로운 root primary read로 세지 않는다.

## 4. 채택할 과학적 결론

실제 읽은 문헌은 inclusive one-electron marginal과 exclusive two-electron event distribution의 구별을 지지한다. 이 조사 범위에서 현재 retained PHYS02 revision, native energy support, gas-rest frame, finite proper history, isotope/state와 normalization에 정확히 맞는 absolute joint kernel의 실제 입력 bytes는 확보되지 않았다. 이 사실은 문헌 전체에 그런 자료가 없다는 no-go 결론이 아니다.

따라서 새 결과는 다음의 정확한 수학적 범위로 제한한다: **고정된 finite atomic inclusive marginal에서 nonnegative single-event measure S 및 symmetric double-event measure D가 μ=S+2π₁D를 만족할 때의 event-union correction과 attainable mathematical interval**. 실제 He parent event count, exclusive joint spectrum, partner history, donor work, physical native25 full-source closure는 이 수학만으로 생성하지 않는다. Named same-state consumer의 실제 필수 입력이 없으면 null을 유지한다.

Wolfram context retrieval의 무관한 결과는 채택하지 않았다. 새 symbolic evaluator가 필요할 경우, source·history를 추정하는 데 쓰지 않고 미리 고정한 유한 polynomial/rational identity의 검산에만 사용한다. 새 evaluator 결과는 별도 원 응답과 scope로 기록해야 하며 이 문서의 복원은 그 실행을 대신하지 않는다.
