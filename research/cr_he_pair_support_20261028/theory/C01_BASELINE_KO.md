# C1 목표와 baseline

현재 작업 branch는 `research/cr-he-pair-support-20261028`, PR은 [113](https://github.com/cosmosapjw-quantum/bass_cr/pull/113)이며 시작점은 closed PR112 D `729cb95164697d8122b0a85ae6e403b57392e724`다. 실제 remote ref와 현재 AGENTS는 각 publication preflight에서 확인한다. Local mode는 **API-only staging**이다. 현재 host의 Git proxy 및 직접 DNS probe가 실패했으므로 local git HEAD/checkout 성공을 주장하지 않는다. Python3.12.14는 실제 probe로 확인했고, package 실행 조건은 C4 bounded probe에서 확정한다.

계산 대상은 고정 source coefficient marginal과 explicit conditional pair graph의 정확한 cross-event envelope이다. 이론 baseline은 `THEOREM.md`,R06독립 검토,R07실제CAS,R09codecontract다. 원래 source/event consumer는 INPUT_MANIFEST의 byte identity를 그대로 쓴다. 새로운 graph의 primal/dual equality, sparse atomic marginal, physical state/window binding을 검증하는 것이 변경 범위다.

입력은 네-bin exact capacities, canonical graph/provenance, source AtomBundle, 허용 proper window, 요청C와 optionald다. 출력은 exact primal/dual certificate, typed finite event witness, once-only partial consumer return과 null/gate fields다. 실제 kernel이나 graph 관측치를 추정하여 채우지 않는다.

수용 기준은 exact rational residual0과 명시적 거절 규약이며 FP tolerance 완화가 없다. 물리 정확도를 exact rational arithmetic과 혼동하지 않는다. 실제 physical/model error는 null이다. 신뢰할 수 있는 구현 완료에는 primary/controls/independent/numeric evidence, C9와 원본 provider R3가 필요하다. 기존 source-fit/projection/RR suite 재실행은0이다.
