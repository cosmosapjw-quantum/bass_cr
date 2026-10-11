# CR-PHYS02G 읽기 전용 operator provenance intake

실제 결과는 MISSING_PERSISTED_OPERATOR_VALUES다. 진단 수집 exit 0은 F/G 과학 성공이 아니다.
F HOLD_OPERATOR_BINDING_UNRESOLVED, G BLOCKED_BY_F_OPERATOR_BINDING_HOLD를 유지한다.

2026-10-11 08:19:34.739130–08:21:01.817706 UTC의 동일 180초 창 안에서 두 읽기 전용
명령을 실행했다. 전체 창은 87.078602552초이며 main 1.968340949초, 보완 0.164529745초다.
두 명령의 exit은 0/0이다. 배열 비교, G/resolvent/solve/pulse/expm/F retry/G frontier는 모두 0회다.
최초 main의 timestamped E run 경로 누락을 원본 그대로 보존했고, 기록된 --run-dir를
직접 사용한 보완으로 같은 창 안에서 추가 조사했다. 새 진단 창이나 물리 retry를 열지 않았다.

원래 E 기록에 연결된 /root/CR_PHYS02E_NCP_20261011_0412/actual_run_20261011T0418Z의
일반 파일 23개를 조사했다. 두 NPZ의 member는 sample_u, pulse_states, integrator_states,
energy_eV, source_vectors이며 CSC data/indices/indptr 값은 없다.
원래 F 기록의 /tmp/CR-PHYS02F-EXECUTION-20261011.euer7hqa/run은 현재 호스트에 없었다.
원래 F source/return 및 /home/cosmosapjw의 기록된 library 경로도 존재/부재를 기록했다.
이것은 명시한 경로의 관측이며 다른 호스트·다른 cache 전체의 부재를 증명하지 않는다.
기록에서 별도 cache root가 식별되지 않았고 unbound cache 채택은 0이다.

기존 pinned Python3.12.3/NumPy2.4.2/SciPy1.17.0의 경로·metadata·실제 binary hash와
CPU flags 및 비밀이 아닌 allowlist 변수를 기록했다. numerical package/source import나
환경·package·dispatch 변경은 없다. WHEEL metadata hash는 전체 wheel archive hash가 아니다.
과거 reference SkylakeX/failed F Haswell은 보존된 provenance이고 현재 실행 중인 BLAS dispatch는
수치 import 없이 관측하지 못했다. 원인·오차 크기·roundoff-only·동등성은 확립되지 않았다.
전체 G digest로 active matrix/heat row 차이를 국소화하지 않는다.

원래 F의 G 예약/완료 1/1 및 execute/collect/wrapper exit 1/0/1은 소비된 기록이다.
107.954172934초 coordinator와 109.790418950초 wrapper는 중첩되며 합산하지 않는다.
기존 G frontier 1회/90초 준비 allowance는 미소모·비활성이다.
새 물리 실행에는 실제 입력·기준·누적 예산이 고정된 별도 유한 계약과 독립 심사가 필요하다.

G-R01을 유지한다. FP64 horizon 8/10의 약 1e-17 확률 여유 끝점 부호 차이는
directed-rounding exact-input 인증, forward-error 보장 또는 물리 불확실성 구간이 아니다.
PHYS02_DELAY OPEN; production_history HOLD; atomic_G02 UNRESOLVED; b_grid NO_GO;
all_bound OPEN; R17B2B NO_CERTIFIED_SOURCE_SHARPENING;
CCC_2026_exporter_identity SOURCE_IDENTITY_UNRESOLVED.

완전 반환의 originals/에는 정확한 현재 outer ZIP 원본을 담았다. 그 안의 G core에는
완전 F 준비본·E 반환·두 canonical Astra v4.0.0 하네스가 있다. original_F_family/에는
실제 실패 numerical ZIP과 모든 family sidecar/log를 별도로 바이트 그대로 담았다.
원래 F tar와 후속 PR37 47-file snapshot의 4개 publication 추가 및 2개 staged 차이를
정상화하지 않았다. source pointer만 반환한 것이 아니다.

source R3는 안전한 실제 복구, manifest/bytes/SHA256 및 Git blob 대조로 수행했다.
새 외부 backup의 R1 게시 확인은 별도의 publication receipt로 기록한다.
canonical 역할은 Astra 후보/해석, lower 기계적 구현, 새 독립 Astra 판정으로 분리했다.
모델 요청 label과 관측된 generic metadata/미인증 backend를 분리하며 Pro attestation은 없다.

최소 결손 입력은 원래 reference와 failed-current CSC data/indices/indptr 전체 및
각 original execution에 연결된 저장 경로/member·raw identity·출처 기록이다.
비교 helper는 실행하지 않았으며 수치 검증 완료로 표기하지 않는다.

새 독립 판정: PASS_SCOPED_READ_ONLY_INTAKE. 허용 범위는 이번 사실 기록에 한정된다.
후보 체크리스트의 GOTO_NUM_THREADS는 조회되지 않았고 실제 allowlist는 추가로
LD_LIBRARY_PATH/VECLIB_MAXIMUM_THREADS를 조회했다(둘 다 null). 이 literal 차이는
독립 심사의 비차단 한계로 보존했으며, 조회하지 않은 값을 채우거나 진단을 재실행하지 않았다.
모델 backend는 NOT_ATTESTED이며 최종 backup 자체는 독립 과학 판정의 범위 밖이다.
