# C23C source-cutoff binding 독립 C9 검토

## 판정

**PASS_SCOPED_FINDING_CLOSED.** 저장된 C23B photoelectron source를 명시된 frozen-target predictor와 KC4 atomic cutoff에 연결한 C23C의 실제 18 cases를 독립 Decimal80 계산과 대조했다. 977개 scalar comparison의 최대 상대차는 **1.2507493130458459×10⁻⁷⁸**, 사전 수용 기준은 **10⁻⁴⁰**이다. 새 guard finding 1건은 최소 수정과 targeted 실행으로 닫혔다. 기존 18-case production sweep, KC suite, C23B source quadrature를 다시 실행하지 않았다.

실행 근거는 runs/c23c_independent_c9_20261023_v1/RESULT.json이다. 해당 디렉터리의 DISPATCH_COMPLETE.json에서 실제 종료 코드 0을 확인했고 LEASE_RELEASED.json에서 own lease 해제를 확인했다.

## 검토의 독립성과 방법

검토자는 root의 구현 작성자와 별도 agent다. 이 검토자는 앞서 source-to-cutoff 결속 식 B1–B15를 작성했으므로, 완전히 새로운 연구 맥락에서 수행한 blind review라고 표현하지 않는다. 검토의 독립성은 구현 및 수치 경로에 있다.

18 saved case의 oracle은 production numerical function을 import하지 않았다. 원 CSV의 decimal 값을 Decimal precision80으로 읽고 다음을 직접 계산했다.

- proper density와 volume에서 target count로의 변환, proper duration과 per-target source rate를 곱한 packet count.
- HI, HeI, HeII 채널별 사건수, five-fit-label population 변화, nuclei와 ion/electron charge.
- 새 source electron을 제외한 base count 및 base energy, common kinetic inventory.
- 모든 finite prefix candidate의 EOS와 threshold condition. production의 forward-from-zero 선택을 독립적인 첫 consistent prefix와 대조.
- thermal/active × below-FS/inside-FS/above-FS의 6개 cell count·energy.
- electron-only ownership, exact rational output의 13개 conservation/EOS residual, finite caloric temperature change.

이 oracle과 저장된 유리수 결과를 비교한 scientific-output acceptance가 10⁻⁴⁰이다. CUTS.csv는 binary64 presentation이므로 별도로 독립 계산을 binary64로 반올림한 값과 일치하는지 확인했다. 두 정확도 관계를 혼동하지 않았다.

원 source CSV, CONTRACT.json, unchanged KC vendor 파일을 original SOURCE_IDENTITY.json과 byte identity로 대조했다. 실제 사용한 old binding source는 implementation/history/v1/source_cutoff_binding.py에 보존되어 있으며 원 production identity와 일치했다. 당시 source identity에 함께 들어간 미사용 N5 병렬 파일을 이 18-case 계산의 물리 의존성으로 확대하지 않았다.

## 실제 결과

| 검사 | 결과 |
|---|---|
| 원 CSV | 32,592 rows, SHA256 일치 |
| 실제 saved cases | 18/18 PASS |
| scalar comparisons | 977/977 PASS, 최대 상대차 1.2507493130458459×10⁻⁷⁸ |
| 각 case의 source rows | 10,864 |
| finite branch | 모든 실제 case에서 첫 consistent prefix 일치 |
| branch root 수 | 이번 18개의 명시적 입력에서 각각 1개 관찰; 일반 유일성 정리로 확대하지 않음 |
| thermal/active × FS support | case당 6 cells의 수·에너지 대조 PASS |
| 기록된 exact rational residual | case당 13개 모두 0 |
| CUTS.csv presentation | 독립 binary64 값과 일치 |
| 초기 electron/base ownership | source electron을 N_B에 중복 계상하지 않음 |
| physical heating, stopping time, global bound | null 유지 |

새 boundary witness는 실제 저장 source의 최저 kinetic energy
\(K_{\min}=15653959194601441/5000000000000000000\) eV를 사용했다.
\(\chi=3/2\), \(T_0=K_{\min}/[(3/2)k_B]\), proper duration17s를 입력하여
최종 cutoff가 정확히 \(K_{\min}\)인 새 case를 실행했다. equality atoms의 양의 count·energy가 thermal 쪽에 정확히 포함되고, caloric temperature는 초기값과 같았다. 이 witness는 기존 KC toy fixture 재실행이 아니다.

새 normalization pair는 volume7/3, abundance reference density5/2를 사용하여 기존 production fixture와 다른 정규화 입력을 검증했다. density와 abundance 경로가 같은 count를 반환했으며 Decimal80 직접 계산과 일치했다.

## Finding C9-F1 및 처리

**대상:** implementation/source_cutoff_binding.py의 bind(request).

**관찰:** original v1은 required fields가 있는 request에 추가 top-level field를 넣으면 이를 조용히 무시했다. 예를 들어 preexisting_nonthermal_atoms, initial_free_electron_count 또는 physical_heating_eV_per_s를 첨부한 요청이 initial reservoir 계약과 다른 정보를 전달해도 계산이 진행될 수 있었다.

**영향:** 공개 입력의 의미와 실제 소비 범위가 불명확해지는 API 문제다. 실제 저장된 18 requests는 정확히 허용된 8개 key만 사용했으므로 기존 science 결과는 영향을 받지 않았다.

**최소 수정:** request가 dict인지 확인하고, 허용된 8개 이외의 key를 ValueError로 거부한다. required field가 빠진 경우에는 기존 BLOCKED_MISSING_BATH_OR_SOURCE_CONTRACT 반환을 유지한다.

**원본 및 교정 identity:**

- 실제 original production source SHA256: 1e1771a0eca01cfdbef109c01774937bd5a23a638ce6f87f3a3d8fa99282e7c1.
- 보존 경로: implementation/history/v1/source_cutoff_binding.py.
- 현재 guarded source SHA256: acedb6e893f08dc1207c6fc40a63af0f4d21480cbf226e0266b6d8f81b883401.

**닫힘 근거:** root의 c23c_binding_guard_20261023_v2는 unknown3, nonobject1, valid saved endpoint1의 총5검사를 통과했다. 이번 independent C9는 unknown3와 nonobject1의 거부 및 required8개 각각의 missing-field BLOCKED 반환을 확인했다. 기존 18-case sweep 재실행은 0이다.

**최종 상태:** CLOSED_BY_GUARD_REVISION. 본 범위에 남은 blocking finding은 없다.

## 물리 범위 판정

C23C는 실제 saved source spectrum과 synthetic five-fit-label bath의 finite caloric partition을 결속한다. KC4/KC7을 직접 재사용하며, KC2 cold-target stopping, KC3 continuous effective-capacity certificate, KC6 coupled contraction을 새로 승인하지 않는다.

시간 단계 안에서 targets·UV·volume이 고정되고 newly produced daughters는 재반응하지 않는 1차 predictor임이 구현에 드러난다. 양의 target depletion bound가 검사된다. Threshold fit convention과 source frame은 C23B 원본을 유지한다. Full21 isotope network, Maxwellianization kinetics 또는 thermal heating 공급자가 추가된 것은 아니다.

Caloric ΔT가 음수인 경우에도 source count·kinetic energy는 양수일 수 있다. 이는 새 electron count를 EOS에 포함하는 B15의 직접 결과이며 physical cooling rate로 해석하지 않는다. FS 10eV support edge와 thermal cutoff는 독립적으로 저장된다.

## 실행·게시·백업·DAG

- **EXECUTION:** independent C9 실제 완료. worker CPU1, coordinator CPU0, native threads1, CPU55 미사용. wall2.053914436s, CPU2.052593159s, peak RSS75,292KiB. source quadratures0, newODE0, old KC/C23B suite reruns0.
- **PUBLICATION:** C9 수용 범위가 닫혔으므로 root의 additive C23C 게시 단계로 이동한다. 이 문서는 외부 commit ACK를 자체 주장하지 않는다.
- **BACKUP:** root의 최종 authority와 provider receipt에 결속한다. 이 검토는 삼중 백업 완료를 주장하지 않는다.
- **DAG:** CR_N4_C23B_CUTOFF_BINDING의 구현·독립검토 의무 완료. 물리 stopping/thermal exchange, isotope-resolved rate coverage와 그 다음 energy closure는 다음 node의 의무다.

추가 reviewer recursion이나 같은 scope의 반복 감사를 시작하지 않는다. 남은 조치는 root의 C10 패키징·게시·보존 및 handoff다.

