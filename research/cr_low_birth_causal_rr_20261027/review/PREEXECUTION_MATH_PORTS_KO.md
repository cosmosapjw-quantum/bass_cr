# 실행 전 production 수학·port 정적 검토

**판정: PASS_SCOPED_STATIC. 열린 blocking/nonblocking finding은 각각 0건이며, 양의 Poisson tail 나머지 처리 1건을 실행 전에 수정하고 다시 읽었다.** 이 문서는 실제 수치 계산·시험·독립 reference 비교의 PASS를 뜻하지 않는다.

검토자는 `/root/source_qualification`이다. 이전 source/literature qualification과 R6 이론 검토에 참여했으므로 blind review는 아니다. Production 코드와 independent numerical reference를 작성하지 않았으며, 이번에는 텍스트·단위·식·byte identity만 검토했다. 코드 import, compile, 과학 계산, 시험, CAS 및 과거 science replay는 모두 수행하지 않았다. 상세 파일 hash와 검토 항목은 같은 이름의 JSON에 있다.

## 1. 고정 대상과 범위

대상은 `CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1`의 `model.py`, `uniformization.py`, `prepare.py`, `ports.py`, `primary.py`, `controls.py` 및 출력 schema다. CONTRACT SHA는 `0766fa66e643de2b50d797fa94838cb989e69c8d3aaa47fe8c31673764757210`, THEORY SHA는 `d42d88d8adefa0a08f847f7a38440b038b5383ee68f3bfadb9cc5d5ddb18d026`이다. Runtime aggregate enforcement는 별도 reviewer가 검토하며, 이 문서가 C4 gate를 대신하지 않는다.

Exact source record 전체 SHA `8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf`와 두 retained Verner 파일을 실제 로컬 bytes로 재확인했다. Source 계수의 새 합산이나 배열 계산은 하지 않았다. 코드가 선택하는 것은 `direct_0p1_10`의 저장 3200 active atoms와 별도 cutoff atom이다. `selected_total`의 현재 E 조건이나 `low_cross` 진단을 새로운 출생 source로 사용하지 않는다.

## 2. 수학과 물리적 계약의 대응

| 경로 | 정적 확인 |
|---|---|
| Source→proper injection | 저장 `A_j`는 이미 number coefficient다. `q_j(t)=t A_j`로 사용하며 E로 다시 나누지 않는다. Native clock/volume Jacobian은 각각 1이고, source target·angular·proper729 인자를 다시 곱하지 않는다. |
| 동일 상태의 조건부 inventory | 새 100 K H1/He4-only 모델의 `nb=nH+4 nHe`와 source/recipient frame을 명시한다. 이전 PR109의 nb/null 기록을 수정하거나 물리적 전체 baryon inventory를 발견했다고 말하지 않는다. |
| Coulomb+RR | CODATA2022 한 세트를 사용한다. Retained min(classical,quantum) stopping law의 quantum constant 0과 맞고, drift는 `b/Delta E`다. Milne dH=1/dHe=4, ion target density, cm²→m² 인자 1e−4가 각각 한 번 들어간다. HeI residual-ion branch 해석은 여전히 conditional이다. |
| Positive evolution | Downward P의 인덱스 방향, exit rate와 nu 선택, 양의 backward Poisson cumulant가 맞다. φ2·φ3는 같은 M에서 계산하고 가중치를 다시 정규화하지 않는다. Zero-generator는 polynomial branch다. |
| 유한 history | 네 prefix는 같은 absolute source clock으로 계산한다. Observation bin은 prefix occupancy/state 차이를 사용하므로 이전 구간에서 살아남은 cohort를 포함한다. `T=1e10 s` 이후 source를 zero로 연장하지 않으며 T endpoint는 known-history left limit이다. |
| Cutoff | 직접 cutoff source는 active RR 상태에 넣지 않는다. Direct `Acut*(t1²−t0²)/2`와 drift `d0 O0`를 분리하고 cutoff energy는 0.1 eV로 고정한다. |
| Capture·photon | `lambda_j O_j`가 실제 capture atom의 weight다. Kinetic reward `E_j`, photon reward `E_j+I`, binding change `−I`를 한 번씩 기록한다. Photon 배열이 별도로 저장되며 aggregate moment에서 spectrum을 구성하지 않는다. |
| Ownership | Birth family/support/history와 channel별 disjoint observation bins를 사용한다. Prefix는 nonadditive이며 return claim을 생성하지 않는다. Producer revision을 바꿔도 겹치는 물리적 claim을 다시 허용하지 않는다. |
| RR native25 | H1/He4 species ±capture/nb, ζ 감소, capture kinetic의 w_nt 감소를 기록한다. `Delta nb=0`, `q·Delta Y−Delta ζ=0`이며 w_ext=0, logT=0은 frozen diagnostic이다. Full source chemistry/native25와 coupled update는 null이다. |

Count/kinetic/total energy closure는 active 상태의 변화와 direct/drift cutoff, Coulomb caloric reward, capture 또는 photon+binding ledger를 함께 검사하도록 작성되어 있다. Bin active change는 누적 state와 달리 signed quantity일 수 있다. Caloric bookkeeping은 physical heating 완료가 아니다. Proper volume의 크기가 없으므로 extensive worldtube totals는 null이다.

## 3. 발견하여 수정한 tail 상계 항목

기존 `positive_tail`은 양의 tail subtotal `tc/to`와 미합산 부분의 geometric upper remainder `rc/ro`를 따로 반환했다. 그러나 downstream 상계 필드는 subtotal만 사용했다. 작성된 종료 조건은 미합산 remainder를 subtotal의 `1e−65` 이하로 제한하므로 허용치 위반을 측정한 finding은 아니다. **Exact-arithmetic upper bound라는 의미와 구현의 일치를 위해 remainder를 더하도록 요청했다.**

수정된 `uniformization.py` SHA는 `065ce3ad523a7acfeca792fa06863ef4dfb4574db6aa42524f3c6b013d552d5e`다. `tail_count_fraction`과 `tail_occupancy_fraction`은 각각 `tc+rc`, `to+ro`를 사용한다. 원 subtotal은 `poisson_tail_subtotal_*_decimal` 필드로 별도 보존하고 φ2/φ3 mass-identity diagnostic에 사용한다. 수정 전 SHA `686a0d7618007c0900ee9d09085a63788c039a2e7c9d7d2331daedecd4509546`도 review JSON에 남겼다.

Tail threshold는 count `M−1`, occupancy `M−2`다. Tiny capture에는 count-tail과 `lambda_max*occupancy-tail` 중 작은 상계를 쓰고, kinetic/photon energy에는 Emax/(Emax+I)를 곱한다. Bin은 두 endpoint 상계를 더한다. Decimal80 및 binary64 계산은 여전히 **outward interval enclosure가 아니다.** 이 한계는 수정 후에도 명시되어 있다.

## 4. 실행으로 확인해야 하는 항목

작성된 actual acceptance는 closure/native stoichiometry 상대오차 `1e−11`, source N/E tail `1e−13`, 각 positive channel 자체의 N/K/photon tail `1e−12`다. Independent reference와의 positive channel 상대 비교 `1e−9`는 아직 실행 전이다. 전체 source 크기로 tiny RR의 상대 오차를 숨기지 않도록 작성되어 있다.

Zero source/generator, one-channel·competing-channel·drift-only analytic case, direct cutoff와 source/state/isotope/support/normalization/ownership 거절 control이 코드에 있다. 이 문서의 16개 항목은 **정적 확인 항목이며 실행된 시험 수가 아니다.** 실제 preparation·primary·controls·independent reference, CPU와 실패 기록, C9 통합 검토는 root가 승인된 새 예산 안에서 수행하고 실제 출력으로 판정해야 한다.

Root R07 preflight를 읽어 최신 owner/source/backup 맥락을 확인했고, 이 검토자가 remote HEAD나 backup full GET을 새로 확인했다고 주장하지 않는다. R06 stage receipt의 dual R2와 과거 canonical R3 재사용을 구분한다. 이 검토의 중앙 집계 효과는 0이며 기록된 중앙 수는 **27/88, 88 nodes/17 edges**다. PR236의 별도 32/88, 기존 실패·UNKNOWN_NO_ACK·각 예산, 개인 대화 전체 검색 unavailable와 Drive partial inventory를 보존한다.
