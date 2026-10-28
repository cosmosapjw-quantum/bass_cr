# R2 원전·재사용과 실제 차이

PR112의 고정 NPZ와 event_union.py를 INPUT_MANIFEST의 byte identity로 재사용한다. 이전 marginal/source-fit/RR 계산을 실행하지 않는다. 같은 conditional100K inventory, proper window, isotope/frame/normalization이 유지되며 새 입력은 조건부 pair-energy cap K다.

최신 Git51repos/5632refs와CR113PRs, PR112이후Library276 terminal 및 지정Dropbox5296 terminal의 결과를 종합했다. PR113의 일반4bin graph는 각허용edge에서 전체Cartesian rectangle과unconditionaldiagonal을가정한다. 실제THEOREM§3은atom-specific exclusions와forbiddendiagonals에서 feasibleclass가달라짐을명시한다. 본연구의Ea+Eb<=K는이새의무를직접수행한다. REI13/20, WU25/40조건부입력, HEEXFOR11/QUARTIC12의핵반응reference, RECphysical0/313 및 BASS/Vigilode의별도closure는해당source/state권한범위로보존한다.

## 1차 원전과 대응

Ambrosio et al., Phys.Rev.A92,042704(2015), https://doi.org/10.1103/PhysRevA.92.042704 : 읽은authorproof pp1–4의Eq13은두전자energy에대해differential한exclusiveFDCS를정의하며projectilefinalenergy를에너지보존으로결속한다. excess6eV의3+3/1.5+4.5eV분배는두전자합조건의물리적의미를제공한다. 논문의고정excessslice와이번누적지원Ea+Eb<=K는서로다른입력조건으로기록한다.

Guan and Bartschat(2009), https://ar5iv.labs.arxiv.org/html/0906.1985 : Eq6/Fig4본문은실험의전자별cutoff와수렴된angularDDCS의적분범위를구별한다. 이는acceptedjointsupport와full-source정규화를분리할근거다. 그실험수치를retained0.1–10eV source의보정계수로이식하지않는다. 원문에서지적한Foster2008그림의erratum도원자료채택전확인의무로보존한다.

Koperberg, Couplings and Matchings(2022), https://arxiv.org/pdf/2202.02092 : finiteweightedHall/Strassen coupling조건을선행정리로사용한다. 이번증명은nestedhigh-tail관계의직접greedyrecurrence와명시적dual을제공하므로일반matching원리를새정리의novelty로주장하지않는다. Low/high의질량차이는residualsingles가흡수한다.

SciSpace2검색×10metadata,Exa6검색50results/44uniqueURL및4fetch9URL의실제기록은intake/literature/SEARCH_LEDGER.json에있다. ActualK/exclusivejointarray는읽은자료에서공급되지않았다. 논문전문raw는공개재게시하지않고자체요약·URL·읽기범위·responsehash를보존한다.

## 재사용 경계

원래3201개atom별coefficient와저장binary64energy는정확한Fraction으로올린다. 새정리는저장표현의feasibility이며source모형오차의새certificate를제공하지않는다. 원tolerance와물리null을유지하고,도입한지원조건에영향받는pair구성·bound·consumer연결만검증한다.
