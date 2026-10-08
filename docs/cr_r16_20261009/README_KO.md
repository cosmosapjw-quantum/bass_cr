# BASS CR R16, 소형 이론+검산 및 NCP 인계 패키지

새 실제 수학 결과: R15 signed first-macro time error에 REI BRIDGE14의 동일 모형 source-only partial optical bound를 적용해 연속 constant-S 해 대 native gas-fraction 선형 출력의 구간 **[8.2774386695e-18,3.1228318763e-17]**을 조건부로 얻었다. 하한은 양수다. 독립 FT03 whole proof를 재발급한 것은 아니다.

새 signed adjoint: REI original source AD의 32개 cell midpoint signed Jacobian을 실제 평가, 기존 native error residual 33-node diagnostic cubic spline와 backward dual/forward linearized ODE를 따로 실행해 optical goal을 대조했다. 이 부분은 아직 numerical diagnostic으로만 분류한다.

추가 global Fubini exact rational recomposition: 560 residual panel을 한 커널로 재표현해도 R15 interval 폭은 유의미하게 줄지 않았다. 목표함수 민감도와 파라미터 상관을 무시하고 absolute majorant만 재배치하면 이득이 없음을 실제 자료로 확인했다.

**오프라인 재현**: `python -B reproduce.py --verify-only` 또는 `python -B reproduce.py --output NEW_EMPTY_DIRECTORY`. SciPy·NumPy 설치 필요; `requirements.txt` 참조. 출력은 create-only다. 전체 R15/REI14 source ZIP 2개를 inputs/에 고정했으며 R15 내부에 REI13 donor가 있다. R15 원본 32-cell root, REI13/14 proof, R13 Grackle scientific suite는 재실행하지 않는다.

읽는 순서: `SOURCE_BINDING.json` → `CLAIM_GATE.json` → `REPORT_KO.md` → `VERIFICATION.json` → `results/{COMBINED_TAU,GLOBAL_FUBINI_EXACT,ADJOINT_JAC050_RES33}.json` → `NCP_HANDOFF_PROMPT_KO.md`.
