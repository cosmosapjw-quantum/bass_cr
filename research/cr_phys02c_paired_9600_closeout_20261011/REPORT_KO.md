# CR-PHYS02C paired 9600 closeout

새 9600-node fullBED/legacy 순차 실행과 Astra 독립 검토는 `PASS_SCOPED`다. 15개 frozen check가 통과했으며 두 transport call의 child/coordinator exit는 0, timeout은 false였다. 총 child wall은 1321.697224491초로 3600초 상한 이내다. Python 3.12.3, NumPy 2.4.2, SciPy 1.17.0, thread 1 환경이다.

95개 행의 raw label은 resolved 66, exact-zero 22, unresolved 7이다. `direct_0p1_10`의 7개 label은 그대로 unresolved다. 작은 low-tag active-electron 차이 2.2679751e-30 및 약 2e-15..3.35e-13 상대차는 subthreshold numerical/roundoff 수준으로 기록하며 물리적 유의성을 부여하지 않는다.

승인 범위는 고정 100 K prescribed bath의 표현 및 4800→9600 empirical 비교다. PHYS02_DELAY OPEN, production_history HOLD, atomic_G02 UNRESOLVED, b_grid NO_GO, all_bound OPEN, R17B2B NO_CERTIFIED_SOURCE_SHARPENING을 유지한다. global physical admission은 HOLD다.

첫 directory guard 실패는 transport 0회이며 raw 실패를 보존했다. 성공 return ZIP만으로는 복구가 완전하지 않다. eight-file first-failure sidecar와 seven-file operational-adapter sidecar를 함께 보존했다. 원래 source commit `f34a0cc1484247caf252afde3d5fbe834640e9e4` / tree `72ccd199e1a2496dd345a7d44b8f8440dc0f00db`에서 additive evidence만 게시하며 historical payload와 manifest를 수정하지 않는다.

이 closeout에서는 solver/test 재실행을 하지 않았다. raw 명령과 exit는 `raw/THIRD_GRID_LOCAL_20261011_EXEC01/ACTUAL_EXIT.json`, 실제 비교는 같은 폴더의 `NUMERICAL_RESULT.json`과 두 NPZ에 있다. 다음 단계는 저장된 결과를 해당 범위 내에서 재사용하고 독립 READY DAG를 진행하는 것이다. 네 번째 grid는 승인되지 않았다.
