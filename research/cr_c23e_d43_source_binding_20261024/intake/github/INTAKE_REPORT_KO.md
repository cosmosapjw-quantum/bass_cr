# N5 GitHub 읽기 전용 intake

관측: 2026-10-24 01:50–01:54 UTC / 10:50–10:54 KST. 과학 실행·기존 계산 재실행·원격 변경·clone 0. 7개 저장소 branches 및 open pulls를 per_page=100으로 실제 terminal page까지 읽었다. branches 1310개, open PR 845개다. 전체 branch metadata와 open PR body 범위이며, 모든 branch 파일내용 전수독해가 아니다. 선택 파일은 아래와 로컬 원문만 읽었다. 비공개 대화 전체 접근은 이 작업 범위가 아니다.

## 전수 metadata 및 baseline delta

|repo|branches|open PR|baseline branches/PR|
|---|---:|---:|---:|
|bass_cr|177|98|177/97|
|bass|269|154|269/154|
|rei_bianchi|264|208|263/207|
|BASS_HE|98|93|98/93|
|WU088_HH|151|142|150/141|
|rec_bianchi|149|97|149/96|
|vigilode|202|53|200/52|

기존 refresh compact의 전수 inventory 1306refs/840PRs와 비교한 순증은4refs/5PRs. exact added/changed/removed는 DELTA.json, 각 endpoint 및 terminal counts는 PAGINATION_MANIFEST.json. baseline compact는 각 repo branches와 PR 전체 레코드가 있으며 저장된 이전 page counts와 일치한다. 삭제 branch/closed PR 차이0. 단일 원자적 snapshot은 아니며 여러 read의 짧은 관측창이다.

## 중요한 현재 HEAD

- CR99 `4a0bbc0ed618ab6eae1b7b2714e366d803186b86`; inventory에서99 이후 open PR 없음.
- 중앙 REI222 `8b6e741ceb305cb0a6fde244ee002eb5926559fe`.
- WU142 `0dec9cc128b8cba8d4a7745d603a808563eb1772`, 새 PHYS85 S0 nuclear ownership. 실제 cross section/rate/stopping/consumer history OPEN; 코드 작성 중, Wolfram numerical reference NOT_RUN. 공급자가 아니다.
- WU141 `d5c2c8dbbbd77bc81526dda6e74df534fba3c4e5`; PHYS84 bound-bound H I CE prepared adapter. parentPHYS83 owner 완료132 saved rate rows/66 exact T255–50000K 재사용. 새adapter 검증child0/application0/consumer admission NOT_ISSUED. 7사건/explicit1S2S2P/동일normal-frame proper-seconds/배타적 radiation owner 계약이다.
- HE93 `bf3c21a39b1111497ed77667d05b8a853ffe6646`; prior15053fe4445a32e0544d644e864fe27780d08743는 immutable science이고 최신은delivery metadata. HE94 없음. Hex catalogue948557tmat/86457H1 initial rows, ionf0. physicalHE-ANG SOURCE_INPUT_PENDING. 고정양성자 dynamics에 recoil을 덧붙이는 것만으로finite-mass provider가 되지 않는다고 NEXT_SOURCE_CONTRACT에 명시.
- REC131 `c7cdabd871ab2ef6f722594ff063b8ce8550e6b4`, REI223 `44d0a6d8703f50bf3d7548812a1ab13d9b2c3877`: actualhistory availability와 physicalidentity/uncertainty 구분. H5 INPUT_DEPENDENT_UNCALIBRATED 유지.
- VigilODE83 `577f350407aceec7e304cf0e66427141886f4c50`: standalone adaptive norm consumer, actualBASS client/production/native integration OPEN;negative population samples를 명시.

## 실제 CI/RR/DR/CX/isotope 근거 범위

WU PHYS81 CONTRACT와 FINAL_REPORT를 실제 읽었다. H1/He4/Li7 neutral CI finitewindows는각13.6058–968.61/24.6–60/6–15eV. heavy-stationary-target Maxwellian,255–50000K 범위, common-T thermalpool은 별도closure. He3/Li6 및finite-mass double-Maxwell kinetics 미인정. Li7threshold→6eV gap0.6082793996541902eV. finite-window 밖0은operator 정의이며 물리단면적0이 아니다. 해당unit의 PI/RR/CX/CE/radiativeloss는0이다.

REI221 최신8d10231b1f0f788164d5eadbe1bcee0b802cceca body는 선택21population PI/Case-A recombination fits 및conditionalcapture-heatclosure를 유지한다고 명시한다. RRthermalmoment는same-fitconditionalclosure다.21→9 isotopequotient는eligible동일모형에서의 환원이며source를새로 공급하는 것이 아니다. REI219 6a12f3865d9ea427c1391c41caed8bb7cb7ec00d nuclear18family와atomicfull21ratecoverage는 구분해야 한다.

WU PHYS84 report의OPEN: Liinstrumentresponse/deconvolution/isotope/target-state 및실제sourceuncertainty;He/LiCXstate/photonenergy;DPI/RRmatchedsourcemoments;recombination→z20initialcharge;Liinner-shellspectralcontract. DRfull21coverage를새로닫는공급자는선택원문에서확인되지 않았다. 이 문장은전repository내부부재의증명이 아니다.

소유권: WU85 CONTRACT는CR C23D를reservation으로기록하고WU의범위를nucleardaughterownership으로명시한다. HE93는REI221ownerbranch를변경하지않는다. PHYS84REIrecipient는research/rei_source_pair_binding/**이고namedstate/excitedreservoir/radiativeowner/source/domain/clockbinding미발급이다. N5admission판정은controller권한이며본intake는하지않았다.

## exact source URLs / selected text

- https://github.com/cosmosapjw-quantum/WU088_HH/pull/142
- https://github.com/cosmosapjw-quantum/WU088_HH/pull/141
- https://github.com/cosmosapjw-quantum/BASS_HE/pull/93
- https://github.com/cosmosapjw-quantum/WU088_HH/blob/0dec9cc128b8cba8d4a7745d603a808563eb1772/research/hh_phys85_nuclear_particle_ownership_20261024/CONTRACT.json
- https://github.com/cosmosapjw-quantum/WU088_HH/blob/0dec9cc128b8cba8d4a7745d603a808563eb1772/research/hh_phys81_atomic_nuclear_source_contract_20261023/CONTRACT.json
- https://github.com/cosmosapjw-quantum/WU088_HH/blob/0dec9cc128b8cba8d4a7745d603a808563eb1772/research/hh_phys81_atomic_nuclear_source_contract_20261023/FINAL_REPORT_KO.md
- https://github.com/cosmosapjw-quantum/WU088_HH/blob/d5c2c8dbbbd77bc81526dda6e74df534fba3c4e5/research/hh_phys84_ce_source_adapter_20261023/CONTRACT.json
- https://github.com/cosmosapjw-quantum/WU088_HH/blob/d5c2c8dbbbd77bc81526dda6e74df534fba3c4e5/research/hh_phys84_ce_source_adapter_20261023/FINAL_REPORT_KO.md
- https://github.com/cosmosapjw-quantum/BASS_HE/blob/bf3c21a39b1111497ed77667d05b8a853ffe6646/research/he_ang_source_hex_20261024/NEXT_SOURCE_CONTRACT.json
- https://github.com/cosmosapjw-quantum/BASS_HE/blob/bf3c21a39b1111497ed77667d05b8a853ffe6646/research/he_ang_source_hex_20261024/CONTRACT.json

위 선택원문은repo_path를doubleunderscore로바꾼파일명으로보존했다. PRbodies는*_PR*_BODY.md이며원APIrecord도각prs_page에있다. openPR목록에는fullbody가있으므로동일PRfetch를다시호출하지않았다.
