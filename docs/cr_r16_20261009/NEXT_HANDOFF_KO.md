# R16 → NCP R16B 다음 연구 단위

이번 R16A의 조건부 source+time τ sign은 `results/COMBINED_TAU.json` 정본으로 CLOSED_SCOPE. R16B의 실제 32-cell signed midpoint-AD adjoint 진단은 `results/ADJOINT_JAC050_RES33.json`에 보존했지만 CERTIFIED_ERROR는 OPEN이다. 560 residual panel의 전역 Fubini 재배치는 R15 interval을 넓히거나 좁히는 유의미한 효과가 없다.

NCP은 원 script·ZIP의 source hash를 확인한 뒤, 실제 time-dependent signed interval Jacobian/Hessian에 따른 dual-weighted residual enclosure와 birth error family correlation을 가장 작은 다음 연구 단위로 삼는다. `NCP_HANDOFF_PROMPT_KO.md` 전체가 NCP 실행 계약이다. R15/REI donor root와 old science suite는 중복 재실행하지 않는다. 조건부 upper bound가 좁아지지 않으면 실험을 종료하고 `NO_CERTIFIED_SHARPENING`을 반환하라. Grackle R13/BASS F0-R6와 G02는 actual owner/bank availability가 없으면 각각 BLOCKED_OWNER_INPUT/BLOCKED_INPUT로 둔다.

누적 광학깊이/출생 jump는 절대 reset 금지. source-only BRIDGE14 error를 같은 훈련 구간의 time error에 두 번 적용하지 않는다. `CR_OFF_FASTEST`, precision atomic `PARKED`, HH research `ACTIVE`, physical/production `HOLD`, G02 `UNRESOLVED`, all_bound `OPEN`, b_grid `NO_GO` 고정.
