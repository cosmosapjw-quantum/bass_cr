# R2 문헌·근거 intake: He 사건쌍 제약과 retained marginal의 연결

기준일: 2026-10-28 UTC. 담당: `/root/literature_intake`. 이 산출물은 새 루프의 R2 근거 조사이며, 과학 계산·커널 적합·수치 적분·기존 완료 단위의 재실행을 수행하지 않았다. 최종 단위 scope, 과학 예산, 정리의 수용, DAG 집계는 parent가 결정한다.

## 결과와 다음 단계에 넘길 근거

현재 intake에서 **retained PHYS02의 native 1–4 MeV 양성자 입력과 정확히 결합할 수 있는 절대 정규화된 exclusive He 전자쌍 데이터 bytes를 새로 채택하지 않았다.** 같은 양성자 에너지 범위를 포함하는 single/double 총단면적 문헌은 확인했다. 그러나 읽은 범위만으로는 retained 0.1–10 eV 전자 지지영역에 대한 두 전자의 선택·미선택 분할, birth-bin별 pair 질량, outside partner 응답이 결정되지 않는다. 따라서 actual joint measure, actual C, actual internal double mass, actual outside-partner response는 이 intake에서 null로 유지한다.

새로 연결할 수 있는 구성적 방향은 **명시적으로 주어진 pair-support graph 아래에서 retained atomic marginal을 정확히 보존하는 사건쌍 범위와 증명서를 계산하고, sparse atomwise 사건측도로 올려 기존 same-state partial consumer에 연결하는 것**이다. 이는 fractional matching의 알려진 수학을 현재 물리 입력·정규화·소비자 규약에 연결하는 연구·구현 과제다. 문헌상 일반적인 최초 정리 또는 새 물리 exclusive kernel이라는 주장을 하지 않는다. Parent는 double-cover max-flow와 exact certificate를 사용하는 범위로 수렴 중이다.

## 입력 일치 기준과 실제 확인 범위

| 항목 | 이번 intake가 보존하는 입력 | 근거의 상태 |
|---|---|---|
| Retained PHYS02 revision | `4ca5a90de79c8fb82a25fd9e83615bec0dfa870b` | 이전 완료 단위 및 복원 source pin 재사용 |
| Projectile | 양성자, native 1–4 MeV | 이전 PRIMARY_SOURCE_MAP_KO.md와 retained model mapping 재사용; 원시 projectile weight 함수는 새로 복원하여 읽지 못함 |
| 선택 전자 영역 | direct 0.1–10 eV, active atomic records 3200개; cutoff ghost 별도 | 복원 source metadata와 parent PREPARATION/CONTRACT를 읽음 |
| 상태 | 조건부 frozen 100 K H1/He4 inventory, 명시적 `nb=8750/47 m^-3` | 기존 조건 재사용; absolute volume null |
| 시간·정규화 | gas-rest scalar, fixed proper-volume density, `q_j(t)=t A_j`, proper interval `[0, 1e10] s` | source records metadata를 읽음; target factor가 source에 이미 포함됨 |
| 선택 source JSON | SHA256 `8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf` | `research/cr_proper_injection_20261027/runs/actual_v1/ACTUAL_SOURCE_RECORDS.json`의 재사용 pin |

복원 파일에서 native 에너지 구간과 source provenance는 확인했지만, 원시 에너지별 가중치 식을 이번 intake에서 독립적으로 다시 확보한 것은 아니다. 문헌의 전체 projectile-energy coverage가 1–4 MeV를 포함한다는 사실만으로 retained spectrum convolution 또는 동일 absolute source normalization이 성립했다고 기록하지 않는다. 그런 채택에는 원시 projectile 분포, 단위, target 상태, pair-energy·angle 적분 규약, 전자 중복도, 선택/미선택 partner 분할을 해당 source pin에 맞춰야 한다.

## 원전별 실제 읽은 범위와 사용처

| 원전 | 직접 읽은 범위 | 현재 연구에 주는 근거와 채택 범위 |
|---|---|---|
| [Rudd et al. (1992), Rev. Mod. Phys. 64, 441](https://digitalcommons.unl.edu/cgi/viewcontent.cgi?article=1037&context=physicsgay), DOI [10.1103/RevModPhys.64.441](https://doi.org/10.1103/RevModPhys.64.441) | 이번에는 Exa 발견 highlight. PR112의 §II inclusive differential-source 읽기와 mapping을 명시적으로 재사용 | Inclusive 전자 생산 source의 convention을 유지한다. Parent event decomposition은 추가 입력이다. |
| [Marcelo J. Ambrosio et al. (2015), Phys. Rev. A 92, 042704](https://doi.org/10.1103/PhysRevA.92.042704) | 새 본문 추출의 abstract·introduction·theory Eq. (13), (14)까지 및 results 시작. 별도 targeted result extracts | Eq. (13)은 두 전자의 에너지와 방향, 산란 projectile 방향에 대한 FDCS와 `|T|^2`의 정규화를 준다. 700 keV, 20 eV excess의 10+10/5+15 eV 및 6 eV excess의 3+3/1.5+4.5 eV 사례. Native projectile 범위와 다르므로 pair 자유도·정규화의 개념적 원전으로 사용한다. |
| [Guan–Bartschat (2009), Phys. Rev. Lett. 103, 213201](https://ar5iv.labs.arxiv.org/html/0906.1985), DOI [10.1103/PhysRevLett.103.213201](https://doi.org/10.1103/PhysRevLett.103.213201) | 새 abstract와 본문 Eq. (5), Fig. 4 및 다음 angular-DDCS 식 시작까지 | Eq. (5)의 `2π ∫ b P(b,E_i) db` total-cross-section 정규화. Total projectile 범위 3 keV–6 MeV. Fig. 4는 6 MeV에서 두 전자 에너지를 적분한 angular DDCS이며 실험자료의 peak normalization을 명시한다. Native 구간 total coverage와 selected pair-grid의 차이를 추적하는 근거다. |
| [Foster–Colgan–Pindzola (2008), J. Phys. B 41, 111002](https://iopscience.iop.org/article/10.1088/0953-4075/41/11/111002), DOI 10.1088/0953-4075/41/11/111002 | 새 publisher abstract | 6 MeV double ionization의 angular DDCS, unrestricted emitted-electron energy 사례. Native 구간에 직접 대입하지 않는다. |
| [Ambrosio et al. (2017), Eur. Phys. J. D](https://epjd.epj.org/articles/epjd/abs/2017/05/d160713/d160713.html), DOI [10.1140/epjd/e2017-70713-x](https://doi.org/10.1140/epjd/e2017-70713-x) | 새 publisher abstract·날짜 metadata | 6 MeV coplanar FDCS와 momentum-transfer bins 0.8–1.2 및 1.4–2.0 a.u., relative experimental comparison. 출판일 2017-05-25이며 검색 index의 2016-11-15는 접수일이다. |
| [Andersen et al. (1986), Phys. Rev. Lett. 57, 2147](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.57.2147), DOI [10.1103/PhysRevLett.57.2147](https://doi.org/10.1103/PhysRevLett.57.2147) | 새 publisher abstract. 본문은 sign-in wall | 0.5–5 MeV proton/antiproton single/double total cross-section 측정. Native energy와 겹치는 total-data 후보다. 표·본문·selected-support branching은 읽거나 추출하지 않았고, 값을 digitize하거나 retained source에 적분하지 않았다. |
| [Das–Malik (1997), J. Phys. B 30](https://doi.org/10.1088/0953-4075/30/5/016), DOI 10.1088/0953-4075/30/5/016 | 새 DOI-page abstract | Two-coupled-channel plane-wave Born total single/double와 ratio 모델. Single 10 keV–50 MeV, double/ratio 50 keV–20 MeV. Native 구간과 겹치는 모델 문헌이며 same-source selected joint 입력을 제공한 것으로 채택하지 않는다. |
| [Spicer et al. (2025), Phys. Rev. A 112, 032806](https://journals.aps.org/pra/abstract/10.1103/czd2-865z), DOI [10.1103/czd2-865z](https://doi.org/10.1103/czd2-865z) | 새 publisher abstract·날짜 metadata. 본문은 sign-in wall | 75 keV p+He FDCS, ejected-electron energy 1–75.4 eV와 correlated two-electron target. Target wavefunction의 상관성과 two-ejected-electron exclusive observable을 구별한다. 출판일 2025-09-12이며 index의 2025-08-21은 게재 승인일이다. |
| [Behrend (2013), Fractional perfect b-matching polytopes I: General theory](https://orca.cardiff.ac.uk/id/eprint/43147/7/BehrendFractionalPerfectbMatchingPolytopesFinal.pdf), DOI [10.1016/j.laa.2013.10.001](https://doi.org/10.1016/j.laa.2013.10.001) | 새 author manuscript abstract, §§1.1–1.5, Eqs. (1), (2), (8)와 예제; [기관 metadata](https://orca.cardiff.ac.uk/id/eprint/43147/) | Real-valued fractional b-matching polytope의 선행 수학. §1.3에서 graph loop를 incident set에 한 번 센다. 물리적 diagonal double event는 전자 두 leg를 소비하므로 `z_i=2 d_ii`로 변수 변환하거나 incidence coefficient 2를 명시해야 한다. 뒤쪽 정리를 전부 읽었다고 주장하지 않는다. |
| [Majumdar (Spring 2026), Fully Differential Studies on Dissociative Capture in P+D2 Collisions and on Ionization in P+He Collisions](https://scholarsmine.mst.edu/doctoral_dissertations/3463) | 검색 결과 thesis front matter. 새 landing-page fetch는 CRAWL_TIMEOUT | 최신 발견 항목만 보존한다. 본문·데이터·kernel을 채택하지 않는다. |

각 행의 실제 반환 내용은 `PRIMARY_SOURCE_MAP.json`의 `raw` 필드와 같은 디렉터리의 `*_raw.json`에 연결된다. 요약문 또는 abstract만 읽은 자료를 full-text reading으로 승격하지 않았다.

## 실행한 검색 범위

Exa에서 8회 검색하여 총 65개 result slot을 요청했고 SciSpace에서 2회 검색하여 20개 paper entry를 받았다. Exa fetch 4회에서 12개 URL을 요청했으며, Majumdar2026 landing page 1개는 CRAWL_TIMEOUT이었다. 검색은 proton-induced exclusive He joint/branching, native 1–4 MeV 범위, inclusive source와 total cross section의 관계, 2025–2026 신규 항목, fractional matching의 원전을 포함했다.

65개 slot은 unique 논문 수 또는 full-text 읽기 수가 아니다. SciSpace 반환은 발견 metadata로 사용했다. 이 조사 결과는 위 원전과 읽은 구간에 대한 기록이며, 세계 문헌 전체에서 해당 데이터가 존재하지 않는다는 주장은 하지 않는다. 새로 읽은 출판 원전 중 가장 늦은 확인 publication date는 Spicer2025의 2025-09-12이며, 2026 thesis는 discovery-only 상태다.

실제 도구 반환 객체는 JSON 직렬화본으로 저장했다. HTTP wire bytes라는 의미는 아니다. 첫 5-result math discovery 검색의 객체는 보존되지 않아 `MATH_DISCOVERY_OBSERVED.json`에 검색어와 실제 관측 URL을 **비-raw 요약**으로 명시했다. 후속 math 검색과 Behrend 본문 fetch 원본 객체는 별도로 보존했다. 운영·metadata CPU 측정값은 null이다.

## 다음 이론·코딩 단계가 고정할 수 있는 구성 대상

아래는 R2에서 parent에게 전달하는 후보의 정의·연결식이다. 독립 정리 심사, 구현 검증, 새 루프 전체 완료를 이 intake 산출물로 대신하지 않는다.

Birth bins를 `i=1,…,k`, 각 bin의 고정 atomic electron measure를 `μ_i`, 질량을 `n_i=μ_i(A_i)`라 하자. `G`는 서로 다른 bin 사이의 허용 pair graph다. 허용 edge `ij`의 전체 Cartesian rectangle `A_i×A_j`를 사용할 수 있고, singles 및 bin 내부 diagonal double은 허용한다. Graph는 명시적인 조건부 입력이며 실제 물리 graph의 관측값으로 지정하지 않는다.

Cross-event 질량 `x_ij`의 incident electron-leg 소비량을 `Bx`로 쓰면 후보 bound는

\[
\rho_G(n)=\max_{x\ge0,\,Bx\le n}\sum_{ij\in G}x_{ij}
=\min_{y\ge0,\,y_i+y_j\ge1\;(ij\in G)}\sum_i n_i y_i.
\]

이 표현에서 primal은 sparse cross-event witness를, dual은 상한 증명서를 제공한다. Parent가 선택하는 double-cover max-flow는 이 값을 구하는 실제 알고리즘과 exact certificate로 연결할 수 있다. 실수형 solver의 성공 flag만으로 exact bound를 기록하지 않고, 입력 질량에 맞춘 증명서를 소비자에게 넘기는 구성이 적합하다.

후보 attainable interval은 `0≤C≤ρ_G(n)`이다. 추가로 selected-internal 전체 double-event mass `d`가 명시되어 있고 `0≤d≤N/2`, `N=Σ_i n_i`이면 후보 interval은 `0≤C≤min(d,ρ_G(n))`이다. 잔여 `d−C`는 남은 electron marginal의 diagonal double에 배치하며, 필요한 leg 질량 `2(d−C)`가 잔여 `N−2C` 이하라는 조건은 `2d≤N`과 같다. `d`는 조건부 입력 또는 범위 매개변수이며 이번 문헌 검색에서 얻은 실제 native branching 값이 아니다.

Atomic lift를 위한 구체적인 mapping은 각 edge `e`가 bin `i`에서 사용하는 submeasure를 `μ_i^e=(x_e/n_i) μ_i`로 배분하고, 같은 edge 양끝의 동일 질량 submeasure를 sparse interval transport로 결합하는 것이다. Bin 질량이 0인 edge는 질량 0이다. 각 edge coupling `π_e`를 `D_e=(π_e+π_e^T)/2`로 대칭화하면 `2π_1 D_e`가 해당 edge가 소비한 양쪽 electron submeasure와 일치한다. 나머지는 singles 또는 지정된 residual diagonal double로 배치한다. 따라서 retained atom 가중치·에너지·상태를 보존하는 witness를 기존 event-union consumer에 넘길 수 있다. Cutoff ghost, retained photon, RR의 별도 once-only 처리는 기존 계약을 따른다.

완전 graph의 제한 없는 envelope는 기존 PR112 결과로 환원되어야 하며, 제한 graph에서 더 좁아지는 조건부 bound, 독립 certificate, atomwise conservation과 소비자 응답이 새 구현의 판별 대상이다. 4 birth bins이면 graph 종류가 64개이므로 parent는 작은 exact graph case 집합과 retained atomic lift를 예산 안에서 분리해 검증할 수 있다. 이 intake에서는 그 64개 case나 물리 atom 계산을 실행하지 않았다.

## 재사용 context와 남은 물리 입력

`next_work/policy/RESEARCH_POLICY.md`, `THEORY_LOOP.md`, `SUBAGENT_MODE.md`를 읽고 해당 규칙을 적용했다. Exa `c4/Search/references/searching.md`와 `patterns-papers.md`를 읽고 사용자 선택 Exa·SciSpace 실제 도구를 사용했다. 재귀 위임 및 외부 쓰기는 수행하지 않았다. 문헌에 private source text를 검색어로 보내지 않았다.

실제 exclusive kernel을 채택하려면 native projectile distribution에 대한 provenance, 동일 target 상태와 절대 단위, unordered event와 electron-leg의 factor convention, selected-support 안팎 두 전자의 joint mass 및 필요한 시간·환경 mapping이 확보되어야 한다. 이번 다음 노드가 조건부 graph envelope를 완료해도 actual kernel·actual C·outside response·projectile donor work·actual EOS/T·full-source physical native25의 기존 상태는 별도로 보존한다.
