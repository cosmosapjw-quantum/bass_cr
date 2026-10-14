# CR PHYS02E publication correction 01

이 폴더는 최초 closeout의 잘못된 저장소 조회로 인한 false-HOLD를 교정하는
additive PR35 companion이다. 최초 패키지와 모든 원시 receipt는 보존되며
재작성하지 않는다.

독립 Astra 승인 범위는 기존과 동일한 `PASS_SCOPED_CR_PHYS02E_SAVED_GRID_FROZEN_OPERATOR_PULSE`이다.
fullBED/legacy saved grid, frozen operator, 0..1e10 s pulse 및 resolvent
moments만 포함한다. global evolving-IGM history는 HOLD이고, 다음
`CR_DELAY_FIXED_BATH_INTAKE01` 노드는 별도 worker에서 이미 진행 중이다.

자체 실행 반환은 archive SHA256
`c696c50a1f3836b490d20d64a457282b709403471246c53a6e52940680b679d8`이며,
외부 PR35 raw archive와 동일하다고 주장하지 않는다. 자체 local recovery
backup SHA256 `617f389424cc9cfbc25b64f5d1061c098f4887bec140274126e8cc06c36f38d1`도
별도 identity로 유지한다.

PR34/PR35는 `cosmoapjw-quantum/bass_cr`에서 확인되었고 정확한 head identity가
확인된 뒤 이 폴더만 PR35 branch에 Git Data API로 additive publication한다.
