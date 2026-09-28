# R4B reference-path finite-span diagnostic

상태: **REFERENCE_PATH_FINITE_SPAN_DIAGNOSTIC_COMPLETE__TRANSPORT_GATE_OPEN**

이 노드는 새 native BASS 계산이나 capture execution이 아니다. R4A에서 provenance가 고정된 archived DOP853 reference final state와 같은 final time의 qualified overlap matrix S를 읽어, pinned projectile negative-energy finite subspace [9,10,12,13,14]에 대한 metric projector postprocessing만 수행했다. Positive projectile pseudostates [11,15,16,17]은 제외했다.

## 수치 결과

metric projector

    Q = S J (J^† S J)^(-1) J^† S,
    P_sel = c^† Q c

를 inverse를 직접 만들지 않고 linear solve로 평가했다. Reference-path finite-span 값은

    P_sel = 0.0096534323761618517

이다. 이것은 **finite-basis, finite-time, reference-path diagnostic**이며 production capture probability가 아니다.

Final metric norm은 0.99999999999649503, final S condition number는 1.00991058951이다. Selected Gram condition number는 1로 사실상 1이다. Projector checks는 Q Hermiticity max-abs 5.551e-17, ||Q S^(-1) Q-Q||_2 1.110e-16로 1e-12 numerical gate를 통과했다.

Candidate ladder의 동일 observable은 N=24,48,96,192,384에서 reference 값으로 2차 수렴한다. N=384 값은 0.0096533721810255144, reference와의 absolute difference는 6.020e-08, relative difference는 6.236e-06이다. Observable의 최근 observed order는 2.000648949이다.

이 observable-level convergence가 frozen TP2D state-metric gate를 대체하지는 않는다. Historical return은 여전히 TEMPORAL_REFINEMENT_UNRESOLVED이며 N=384 state distance가 reference 2.635e-06, N=192→384 refinement 7.905e-06로 둘 다 1e-6 screen을 닫지 못했다.

## 다음 temporal gate

State-distance ladder의 최근 observed order는 reference-distance 2.000148765, refinement-distance 2.000748231로 매우 안정적인 ~2차다. 단순 continuation extrapolation은 N=768에서 reference distance 약 6.586e-07, refinement distance 약 1.976e-06를 주므로 첫 screen만 통과하고 refinement screen은 실패할 가능성을 시사한다. N=1536에 대한 대응 extrapolation은 각각 1.646e-07, 4.939e-07다. 이것은 **conjectural planning estimate**이지 certificate가 아니다.

따라서 다음 새 native workload가 승인될 경우 최소 계획은 N=768을 먼저 실행해 observed order와 두 frozen screens를 재평가하고, refinement가 여전히 실패하면 N=1536까지 한 단계만 확장하는 것이다. 새 operator query/evaluation이 필요할 수 있으므로 현재 authorization 없이 실행하지 않는다.

## claim ceiling

- capture_execution_allowed = false
- production_admission = HOLD
- all_bound = OPEN
- b_grid = NO_GO
- original_capture_gap_resolved = false
- continuous_global_supremum_bound = false

R4B는 original capture gap을 닫지 않는다. all-bound completeness, asymptotic extraction, b integration도 여전히 별도 gate다.
