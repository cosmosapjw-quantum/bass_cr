# 새 입력의 원전과 N5 coverage

## 이번에 결속한 행
이번 단위는 기존 PR103의 electron–ion bath 교환에 두 개의 neutral bath 열을 추가한다. 종은 **H1(1S), Z=0, n=0.9 cm^-3**와 **He4(ground singlet), Z=0, n=0.07 cm^-3**이며, 원래 elemental HI/HeI 밀도에 대한 조건부 isotope 배정이다. 양쪽 bath는 T=10000 K, 전자·이온 bath와 같은 정지 frame이다. 이 배정은 실제 isotope abundance를 측정했다는 의미가 아니다.

| 물리 과정 | 현재 종·상태 | 이번 소비자의 범위 | 남은 입력 또는 gate |
|---|---|---|---|
| EE Coulomb | thermal ne=0.14 cm^-3, Maxwell bath | 기존 PR59/C23D/PR102/PR103 배열 재사용 | finite bath 및 coupled history는 별도 |
| EI Coulomb | H1+, He4+, He4++ | PR103의 세 mass-dependent 에너지 reward를 그대로 재사용 | 다른 isotope/charge abundance 및 비공통 T |
| Neutral elastic | H1(1S), He4(1S) | 실제 CCC MTCS를 새 leading-mass-ratio FP와 결속 | exact finite-M angular second moment, data uncertainty, 다른 상태·isotope |
| Bound–bound CE | H1 1s→2s/2p | PHYS83 source-native gap10.20435eV의 저장 first-event hazards/RHS 재사용 | excited-state populations, superelastic 및 전체 원자 network |
| CI | 기존 source별 입력 | 이번 모형에서 새 CI 경쟁률을 도입하지 않음 | tail/secondary-electron energy owner와 species별 coverage; missing=null |
| RR | C23E의 조건부 H/D source binding 재사용 | instantaneous source와 energy bookkeeping의 기존 조건 유지 | microscopic Milne pair, isotope-resolved capture energy |
| DR | 선택 charge-state 수치 supplier 미확보 | 값=null | species/charge/T, autoionization·stabilization 및 유효영역 |
| CX | C23E/WU79 조건부 D43K pair | 기존 특정 pair만 유지 | He/Li partners/products/state/photon-energy owner |
| HE angular | HE99 finite-M shell의 운동학 | 공개 owner 결과를 재사용 가능한 운동학으로 관측 | physical amplitude/event normalization은 SOURCE_INPUT_PENDING |
| Nuclear | PHYS87/88 제한된 source/조건부 remap | N5 전자 stopping provider로 사용하지 않음 | PHYS89 bare-kernel/consumer 계약, tails/covariance; 전체 high-energy network HOLD |

원래 PR101의 21 population rows ×8 process columns=168 cells를 덮어쓰지 않는다. 이번 additive delta는 H1/He4 neutral elastic **에너지 교환 소비자** 두 종이다. 원래 표의 모든 cell을 수치적으로 채웠다고 세지 않는다. Missing rate/species, dominant omitted-process ranking, global_error_bound, global_completion_percent는 null이다.

## 실제 데이터 권위

- **CCC database, www.lxcat.net, retrieved October24,2026.** H(1S) ELASTIC/MTCS process25646, CCC(15,4), provider updated2011-06-20;91rows,[0.01,1000]eV, sigma[m²]. SHA25698ed242085006cc5f73057a7013c9fcd93b973349e9d2235fbbe5fb807f4bff0,8954bytes.
- **CCC database, www.lxcat.net, retrieved October24,2026.** He(s1S) ELASTIC/MTCS process25758, CCC(171), provider updated2013-04-18;87rows,[0.1361,1360.6]eV,sigma[m²]. SHAbcf1bae983ea0f2e75ef6cce184cc3b80d370e677f26409efdabe5c5f1e0f4b1,9224bytes.
- H 재취득: https://nl.lxcat.net/data/preselect.php?t=cs&d=156&a=1&b=52
- He 재취득: https://nl.lxcat.net/data/preselect.php?t=cs&d=156&a=1&b=62
- H 방법: Bray & Stelbovics(1992), https://doi.org/10.1103/PhysRevA.46.6995
- He 방법: Fursa & Bray(1995), https://doi.org/10.1103/PhysRevA.52.1279 . 실제 채택한 He MTCS는 provider가 당시 unpublished로 표시한 2013 record다. 1995 논문에 동일 수치표가 실렸다고 쓰지 않는다.
- 표준 thermal elastic operator: Hagelaar & Pitchford(2005), Eq27,p725, https://doi.org/10.1088/0963-0252/14/4/011 . 저자 공식 안내 https://www.bolsig.laplace.univ-tlse.fr/how-to-use.html 와 manual https://www.bolsig.laplace.univ-tlse.fr/wp-content/uploads/2016/03/bolsigdoc0316.pdf 를 대조했다.

2026년 Curtin 직접 ZIP의 README는 integrated cross section임을 명시한다. 이것이나 H의 asym 열을 MTCS로 바꾸지 않았다. MTCS는 angular differential cross section의 (1−cosχ) 적분이다. Scalar/unpolarized 에너지 closure가 DCS 자체의 각도 등방성을 뜻하지 않는다.

LXCat ELASTIC은 elastic MTCS이고 EFFECTIVE/MOMENTUM은 inelastic 기여를 포함하는 별도 양이다. He header의 추가0와 g1/g0=0 placeholder를 탄성률의 가중치로 곱하지 않는다. 계산 질량은 rH=1837.152673426,rHe=7296.29954171이고 header의 반올림 m/M을 사용하지 않는다. Bound-electron inertia는 포함하고 binding mass defect는 생략한 기존 convention을 명시했다.

## 보존과 에너지 소유권
Elastic channel은 tagged electron과 target의 수, 전하, 핵종, target ground internal state를 보존한다. 에너지 reward는 같은 generator의 -Q_species^T E로 정의하며 neutral bath가 전자 운동에너지 변화의 반대 부호를 받는다. 여기에 stopping heat나 ionization energy를 다시 더하지 않는다. CE excitation storage의 gap10.20435eV는 bath heat와 별도 열이다.

서로 다른 isotope를 묶으려면 PQ=Qbar P와 reward descent 조건이 성립하거나, 누락된 isotope 분율과 질량 가중을 명시하는 조건부 closure가 필요하다. 전자적 MTCS가 같아도 inverse mass는 남는다. D/T/He3/Li6/Li7은 null이다.

## 적용 구간
초기 선택은0<W<10eV이고 exposure10000proper s는 pulse population 정의다. 새 FP grid는 q=chi theta에서 U=Rtheta까지이며 chi=(1.5,3), R=(40,80),theta=.8617333262145178eV. 두 표 모두 이 활성 구간을 덮으므로 외삽0이다. 표 밖의 rate나 below-q 초기 neutral coefficients는 null/out-of-scope로 남긴다. 초기10eV를 경로의 상단으로 바꾸지 않는다.

원 데이터는 heavy-target/nucleus-rest incident-energy convention이다. 이번 finite-T recoil/thermal FP는 질량비의 선도 모형이며 정확한 finite-M isotope-resolved cross section을 공급하지 않는다. Native PLsigma의 절점에서 conductance는 D로 직접 만들고, 진단용 도함수는 오른쪽 interval(마지막 endpoint는 왼쪽)을 쓴다.

## 원자료와 게시
원 데이터·원전 PDF와 dense coefficient arrays는 사용자의 비공개 연구 백업에 보존한다. 공개 Git은 식·코드·source ID/hash·재취득 절차 및 source 적분 결과를 담는다. LXCat 원표나 그것을 재구성할 수 있는 조밀한 곡선은 공개하지 않는다. 조건: https://nl.lxcat.net/instructions/how_reference.php ; https://nl.lxcat.net/instructions/redistribution.php .

SciSpace·Exa는 실제 discovery/fulltext 수집에 사용했다. 작업 공간 소실 후 원 검색 raw응답은 LOST_NOT_RECOVERED이며 요약은 재구성 표시를 유지한다. 두 실제 MTCS와 필요한 PDF는 동일 SHA로 회수했고, Wolfram algebra 실제 응답은 evidence/WOLFRAM_NEUTRAL_FP_CHECK.json에 보존했다. 원전 식을 재사용한 소비자 결속이며 새 strong no-go 또는 문헌 최초성 주장은 없다.
