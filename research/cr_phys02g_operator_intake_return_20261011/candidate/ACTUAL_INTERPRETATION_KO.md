# 실제 provenance intake의 후보 해석

결과는 **MISSING_PERSISTED_OPERATOR_VALUES**다. 이 판정은 실제 조회 위치에 한정하며 호스트 전체에서 값이 없다는 결론이 아니다. F는 HOLD_OPERATOR_BINDING_UNRESOLVED, G 실제 frontier는 BLOCKED_BY_F_OPERATOR_BINDING_HOLD를 유지한다. 이 문서는 후보 해석이며 최종 독립 판정이 아니다.

주 진단은 supervisor wall 1.968340949초, exit 0이었다. 최초 경로 선택이 `actual_run_<timestamp>` 이름을 놓쳐 E 기록 경로가 inventory에서 누락됐다. 원래 RESULT.json과 원시 기록을 보존한 채, 같은 180초 창 안에서 보완 명령을 실행했다. 보완 supervisor wall은 0.164529745초, exit 0이며 최초 시작부터 총 경과는 87.078602552초다. 내부 wall과 supervisor wall은 중첩 시간이므로 합산하지 않는다. 주 결과의 `search_exhaustive=true`는 당시 선택된 경로 목록에만 해당하며 전체 기록 경로 또는 호스트 전체 검색 완료를 뜻하지 않는다.

보완 조회는 E 원래 실행 디렉터리 `/root/CR_PHYS02E_NCP_20261011_0412/actual_run_20261011T0418Z`의 파일 23개를 기록했다. 두 NPZ는 `PULSE_fullBED_9600.npz`, `PULSE_legacy_9600.npz`이며 저장된 member 목록은 sample_u, pulse_states, integrator_states, energy_eV, source_vectors다. 이 inventory에서 CSC data/indices/indptr 값 payload는 식별되지 않았다. F 원래 `/tmp/CR-PHYS02F-EXECUTION-20261011.euer7hqa/run`은 FileNotFoundError였다. 기록된 위치 밖의 추가 cache가 없다고 주장하지 않는다.

양쪽 원본 CSC 값과 provenance가 결합된 pair가 없으므로 저장 배열 비교는 0회다. 주·보완 기록의 G 생성, resolvent, linear solve, pulse, expm, F retry, G frontier 호출도 모두 0이다. 원래 F의 G 예약/완료 1/1, execute/collect/wrapper exit 1/0/1을 보존한다. 과거 G 1회/90초 준비 allowance는 미소모·비활성이다.

현재 진단 기록은 Python 3.12.3 및 import 없이 읽은 NumPy 2.4.2·SciPy 1.17.0 metadata를 담는다. 현재 `/usr/bin/python3.12` SHA256은 1643dacd9feaedc58f3cc581e4d22577dfe25c09b10282936186ccf0f2e61118이다. 원래 E runtime에 기록된 NumPy OpenBLAS 경로의 현재 파일 SHA256은 c0f0784c075afdeb2d57cb78e6225221f7c97ef8d03e512b3c98e105054e73c2다. 이는 현재 파일 bytes의 identity이며, 원래 실행 당시 binary와 동일하다는 인증이 아니다. F runtime의 원래 library 경로는 조회 위치에서 찾지 못했다.

현재 BLAS dispatch는 NOT_OBSERVED_WITHOUT_NUMERICAL_IMPORT다. 원래 E의 SkylakeX와 실패 F의 Haswell은 저장된 runtime에서 확인되는 provenance 차이일 뿐이다. 버전·CPU feature·현재 파일 hash로 원인, 오차 크기, roundoff-only, 수치적 동등성 또는 물리적 동등성/비동등성을 확정할 수 없다. RESULT의 wheel_sha256은 함께 기록된 WHEEL metadata 범위로 해석하며 전체 wheel archive hash로 승격하지 않는다.

G-R01의 원래 FP64 10/10 끝점 점검과 exact decimal-token 8/10 부등호 차이 제한을 함께 보존한다. 이를 인증된 exact-input 포함구간 또는 물리 오차로 바꾸지 않는다. PHYS02_DELAY OPEN, production_history HOLD, atomic_G02 UNRESOLVED, b_grid NO_GO, all_bound OPEN, R17B2B NO_CERTIFIED_SOURCE_SHARPENING, CCC_2026_exporter_identity SOURCE_IDENTITY_UNRESOLVED를 유지한다.

최소 미확보 입력은 원래 E 및 실패 F 양쪽의 정확 CSC data/indices/indptr와 원래 실행 provenance다. 이 후보는 새 조회·재구성·재시도·frontier 실행을 허가하지 않는다. 동결된 결과와 실제 종료 기록을 새 독립 reviewer에게 전달해야 한다. 본 작성자는 후보 계약 해석에 참여했으므로 최종 독립 reviewer가 될 수 없다. 요청 Astra 역할과 관측된 generic GPT-6 표시는 별도로 기록했으며 backend 독립 인증은 없다.
