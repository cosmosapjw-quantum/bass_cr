# PHYS02G 실제 읽기 전용 intake 독립 판정

**PASS_SCOPED_READ_ONLY_INTAKE.** 이번 판정은 저장된 읽기 전용 진단의 사실 기록과 제한된 해석을 수용한다. 과학 상태는 **F HOLD_OPERATOR_BINDING_UNRESOLVED**, **G frontier BLOCKED_BY_F_OPERATOR_BINDING_HOLD**다. 누락된 CSC 값이 확보됐거나 연산자 연결이 통과했다는 판정이 아니다.

심사자는 `/root/g_intake_independent_astra`이며 후보 작성, 수용 기준 설계, 구현에 참여하지 않은 별도 reviewer다. 요청 모델/effort는 `gpt-6-astra / xhigh`이고 관측된 developer 표시는 generic “Codex, an agent based on GPT-6”이다. backend는 **NOT_ATTESTED**, 관측 표시에서 확인 가능한 exact router alias는 **MODEL_UNRESOLVED**다. Pro alias 또는 실제 backend의 인증을 주장하지 않는다.

직접 읽은 주·보완 명령 영수증과 raw stdout/stderr는 exit 0/0, supervisor wall 1.968340949초/0.164529745초를 기록한다. 첫 시작 08:19:34.739130 UTC부터 보완 종료 08:21:01.817706 UTC까지 87.078602552초로 같은 180초 창 안이다. 두 inner wall은 각 supervisor wall과 중첩되므로 합산하지 않는다. exit 0은 metadata 수집 종료이며 과학 실행의 성공이 아니다.

최초 selector가 `actual_run_<timestamp>`를 놓친 사실과 원본 RESULT.json을 보존했다. 주 결과의 `search_exhaustive=true`는 그때 선택된 F 위치에만 한정한다. 보완 기록은 원래 ACTUAL_EXIT의 정확 E `--run-dir`에서 23개 파일을 조사했다. 두 pulse NPZ의 저장 member 목록은 sample_u, pulse_states, integrator_states, energy_eV, source_vectors이며 CSC data/indices/indptr payload가 식별되지 않았다. 원래 F run은 FileNotFoundError다. 따라서 결과는 **MISSING_PERSISTED_OPERATOR_VALUES**, 범위는 **NOT_FOUND_IN_DELIVERED_AND_QUERIED_LOCATIONS**다. 다른 위치나 호스트 전체의 부재를 증명하지 않는다.

원래 E/F의 SkylakeX/Haswell은 저장 runtime의 provenance 차이다. 현재 파일 hash와 package metadata는 현재 읽힌 bytes를 식별할 뿐 과거 binary 동일성·실제 current dispatch·원인을 인증하지 않는다. current BLAS dispatch는 **NOT_OBSERVED_WITHOUT_NUMERICAL_IMPORT**다. 차이 개수·절대/상대/ULP 크기는 측정되지 않았고 roundoff-only, 수치 동등성 및 물리적 동등성/비동등성은 확립되지 않았다. 전체 G digest 차이는 active A 또는 heat h의 어느 값이 달라졌는지도 알려 주지 않는다. `wheel_sha256`은 WHEEL metadata 텍스트 hash이며 전체 wheel archive hash가 아니다.

비차단 한계도 남긴다. 후보 C04 목록의 GOTO_NUM_THREADS는 관측되지 않았고 구현은 LD_LIBRARY_PATH와 VECLIB_MAXIMUM_THREADS를 추가 조회했으며 둘 다 null이다. 원래 계약은 관련 비밀 아닌 runtime 변수를 허용하므로 이 차이가 typed-missing intake를 막지는 않는다. 후보 checklist의 문자 그대로 완전한 충족이나 환경 전체 조사를 주장하지 않는다. 닫힌 창을 다시 열어 키를 채우지 않는다.

양쪽 원래 CSC 값과 provenance가 결합된 pair가 없으므로 저장 비교는 0회다. 세 helper는 정적으로만 읽었다. `compare_saved_csc.py`는 **UNEXECUTED / NOT_NUMERICALLY_VALIDATED**이며 이 판정은 그 수치 구현을 인증하거나 이후 실행을 허가하지 않는다. 새 G·resolvent·solve·pulse·expm·F retry·G frontier도 모두 0이다. 원래 F G 예약/완료 1/1과 execute/collect/wrapper exit 1/0/1은 유지한다. 과거 G 1회/90초 준비 allowance는 미소모·비활성이며 전역 실행 이력은 완전 조사되지 않았다.

G-R01을 보존한다. 원래 FP64 working endpoint 점검 10/10 통과와 exact decimal-token 해석에서 8/10의 약 10⁻¹⁷ 확률 여유 부등호 차이는 함께 남는다. 인증된 exact-input 포함구간, forward-error 구간 또는 물리 불확실성 구간으로 승격하지 않는다. PHYS02_DELAY OPEN, production_history HOLD, atomic_G02 UNRESOLVED, b_grid NO_GO, all_bound OPEN, R17B2B NO_CERTIFIED_SOURCE_SHARPENING, CCC_2026_exporter_identity SOURCE_IDENTITY_UNRESOLVED도 모두 유지한다.

source 복구·manifest 영수증은 복구된 원본과 별도 Git 게시 snapshot을 구분한다. 원래 F tar의 PR37 대비 41/47 일치, 게시 파일 4개 부재와 staging 파일 2개 차이는 보존돼 있으며 별도 47/47 snapshot이 이를 소급해 없애지 않는다. 이번 reviewer는 해당 영수증과 source identity를 읽고 실제 읽은 로컬 파일 49개의 SHA256을 기록했다. 전체 archive 재복원, Git blob 전량 대조, 이전 과학 검산을 반복하지 않았다. 개별 파일의 전체/선택 읽기 범위는 DECISION.json에 명시했다.

최종 완전 return-family 조립, manifest binding, additive 게시 및 Drive/Dropbox의 새 영수증은 후속 사실 확인이다. 이 판정으로 아직 없는 산출물·remote ID·업로드 성공을 선인증하지 않는다. 실제 source 복구의 R3와 통상 신규 게시의 R1 metadata 확인을 구별하며 R1을 byte readback으로 부르지 않는다. 원본 실패 F family, 정확한 source archive, 이번 raw 진단 및 새 판정은 함께 전달해야 한다.

심사 중 새 host/cache/library 조회, numerical import, source 실행, test, 저장 배열 비교, 물리 계산, 원격 작업은 모두 0이다. 수정한 파일은 이 REVIEW_KO.md와 DECISION.json 두 개뿐이다. scope 안의 factual intake blocker는 없지만 과학 binding HOLD는 해소되지 않았다. 이후 물리 실행에는 별도 불변 source·유한 계약·수용 기준·누적 남은 예산과 독립 판정이 필요하다.
