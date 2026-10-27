# 부모 사건 문헌 대조 — 게시 가능한 최소 근거 지도

상태: 새 R1용 intake에서 실제 검색·원문 대조를 수행했다. 이 파일은 새 물리 결과나 독점 He 분기 표를 제공하지 않는다.
SciSpace와 Exa는 discovery 경로이며 아래 primary source와 실제 저장 코드를 대조해 채택 범위를 정했다.
장문 retrieval 원본은 theory/queries 내부 영수증으로 보관하며, 이 요약과 원전 URL·해시 지도만 게시 후보로 삼는다.

## P1. Rudd et al. 1992: electron production의 측정 정의

M. E. Rudd, Y.-K. Kim, D. H. Madison, T. J. Gay, Reviews of Modern Physics 64,441–490 (1992), DOI [10.1103/RevModPhys.64.441](https://doi.org/10.1103/RevModPhys.64.441).
[저자 소속기관 사본](https://digitalcommons.unl.edu/cgi/viewcontent.cgi?article=1037&context=physicsgay).

실제 읽은 범위는 Exa가 반환한 이 기관 PDF의 처음 약45,000자 중 §I–II 및 §IV 일부이다.
§II는 projectile 하나가 표적에서 한 개 이상 전자를 방출할 수 있는 상황에서 검출된 **전자 수**로 DDCS를 정의하고, 각도를 적분해 에너지 SDCS를 만든다.
따라서 여기서 제공된 He SDCS는 독점 ion charge state, 두 전자의 joint energy 또는 He+ 잔류 excitation 분포를 자동 제공하지 않는다.
이는 현재 입력의 정보 범위에 관한 판정이다. 해당 분기를 실험·추가 owner 자료로 구할 수 없다는 보편적 주장이 아니다.
원전의 ionization stopping 정의는 ejected kinetic energy와 binding contribution을 함께 다룬다.

이 문헌으로 하지 않은 주장: PHYS02의 He 전자 수를 실제 HeI→HeII 단일 사건 수로 확정, exact1–4MeV/.1–10eV의 double fraction 계산, ground residual의 독점적 보증.
원 PDF의 direct web open은403이었다. Exa의 primary-document text extraction을 읽었으며 original PDF bytes의 full GET/hash를 했다고 주장하지 않는다.

## P2. CRIPTIC 실제 모델과 fixed code revision

M. R. Krumholz, R. M. Crocker, M. L. Sampson, *Cosmic Ray Interstellar Propagation Tool using Itô Calculus (criptic)*, [arXiv:2207.13838v2](https://arxiv.org/pdf/2207.13838).
실제 PDF web parse에서 §2.3.3, Eq23–26과 ionization-rate 설명을 읽었다.
Eq23의 loss functional은 ∫(W+I_s)(dσ/dW)dW이며 Eq24는 Rudd rational SDCS이다.
이는 PHYS02가 사용하는 per-emitted-electron kinetic-plus-binding 모델 장부와 맞는다. 독점 He branching/partner debit의 데이터는 아니다.

[fixed upstream Ionization.H](https://bitbucket.org/krumholz/criptic/raw/e169dc2e906cf51d5c6a1bba47c10bf3d61c3d92/Src/Losses/Ionization.H)를 Exa로 읽었다.
해당 revision의 H Williams-limit, He threshold24.59, continuous loss와 target-summed density 의미를 로컬 rudd.py port와 대조했다.
PHYS02 port의 SHA256은757e4c8b33618ad6ef88f422919fe813654454c836f0942cf9792be133e8eac2이다.
이 port는 원 Eq26/코드의 F2 항과 SDCS 적분 사이의 square discrepancy를 이미 별도 감사하고 수정한 모델이다.
새 단위에서 upstream total formula를 새 normalization으로 다시 가져오지 않는다.
source는 CODATA2018 계열 상수를 포함하고 PR110 RR은 별도 CODATA2022 pin을 썼으므로, 새 attribution은 원 source lexeme를 바꾸지 않는다.

## P3. 독점 He 문헌의 적용 범위를 실제로 제한

L. Meng et al. (1993), J. Phys. B26,3387–3401, DOI [10.1088/0953-4075/26/19/026](https://doi.org/10.1088/0953-4075/26/19/026).
[기관 PDF](https://scholarsmine.mst.edu/cgi/viewcontent.cgi?article=3632&context=phys_facwork)의 앞16,000자 primary extraction을 실제로 읽었다.
논문이 직접 계산/측정하는 주요 예는300·500keV이며, projectile scattering angle과 recoil-ion transverse energy에 대한 single/double 분포다.
도입부의1MeV 관련 설명은 다른 연구의 논의이다.
따라서 이 논문을 원 PHYS021–4MeV의 .1–10eV selected joint-electron kernel로 대체하지 않는다.

추가 SciSpace discovery는 Olson et al.1989 DOI10.1103/PhysRevA.40.2843(single0.5/1/3MeV, double1MeV angular scattering) 등을 반환했다.
이 discovery abstract는 native selected-energy joint decomposition이 아니다.
publisher direct open은 접근 실패였고 독점 support table을 확보했다고 하지 않는다.
이번 bounded 검색에서 exact Rudd recipe를 분해할 owner data가 확보되지 않았다는 상태만 남긴다.

## 실제 검색·접근 이력

- 최초 SciSpace/Exa 각1회: Rudd parent event, binding, single/double 의미 탐색.
- root가 요청한 추가 bounded SciSpace/Exa 각1회: exact1–4MeV/.1–10eV와 독점 He 분기의 대응 탐색.
- primary contrast: Rudd 기관 사본, CRIPTIC primary PDF 및 fixed upstream code, Meng 기관 사본.
- direct web 접근 실패: Rudd 기관403/DOI 실패, fixed Bitbucket src 실패, Meng IOP/기관 실패, Olson APS 실패.
- 성공한 읽기: Exa의 위 기관/fixed-code extraction, web의 CRIPTIC PDF parse.
- 본 intake의 PDF original-byte full GET0, source/physics numeric run0, Wolfram0, old quadrature/operator/RR replay0.

Raw query/result 파일의 이름과 checksum은 LITERATURE_RECEIPTS.json에 기록한다.
외부 문헌의 불확실성을 수치적 native25 closure residual과 혼합하지 않는다.
실제 primary 내용에서 새로 채택하는 결론은 **전자 marginal과 독점 parent 사건을 구분해야 한다**는 점 및 이미 사용 중인 loss-functional convention이다.

