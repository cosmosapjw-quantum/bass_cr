# CR-PHYS02C-P02B-COHORT-ADAPTER01

기존 NIST 경계 source의 실제 Q_BA p_A rate를 proper birth time에서 평가하고, 변경 없는 P02B make_grid(128)/project_daughters에 투영하는 adapter를 구현했다. cohort마다 birth time, 양의 초 단위 quadrature weight, age-zero population, exact energy_meV 및 upstream H/He event metadata를 보존한다.

25개 저장 epoch의 전자수·운동에너지 투영, 1000.001 eV 실제 one-event source의 GL16/32 analytic 및 저장 cumulative 비교, constant/exponential 제조 source의 test-only receiver convolution 및 equal-rate 극한을 검증했다. OFF exact zero, tau=0 finite, 잘못된 clock/normalization/비유한값/에너지/시간 rejection도 검증했다. 최신 repaired 상세 수치는 evidence/VALIDATION_REPAIRED.json에 있다.

최초 별도 moment-scaling 수정은 첫 campaign 이후 이루어졌고 원 첫 JSON은 덮어써져 FIRST_RAW_ARTIFACT_NOT_RETAINED로 기록했다. 남아 있는 수정 후 검증은 PRE_REVIEW_VALIDATION.json에 보존한다. Astra HOLD 검토에 따라 boundary 978.782<E<=1000 eV, tau 0..1e13 s, integer event counters를 적용하고 실제 P02B cutoff slots n+7,n+8로 수정했다. 제조 fixture는 admissible 989.797 eV를 사용한다. 단 한 번의 targeted repair campaign(exit 0, 0.162213205 s)은 VALIDATION_REPAIRED.json에 별도 기록했다.

현재 판정은 독립 Astra repair 검토가 승인한 PASS_SCOPED다. 실제 P02B 물리 진화는 실행하지 않았다. low-energy counters는 0이며 upstream NIST event counts를 중복 계산하지 않는다. HeI singlet/23s closure, volumetric source normalization, continuous physical injection 및 전체 IGM history는 HOLD다.
