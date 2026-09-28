F1 Intel/native engine admission 구현을 시작해줘.

Repository:
cosmosapjw-quantum/bass_cr

Implementation branch:
research/fnd-ncloud-f1-engine-admission-20260928

Minimum plan commit:
d42bf11e2bac8dbffa449c64229e81de6bb00d44

현재 main checkout은 변경하지 마.
branch를 fetch하고 별도 detached worktree를 만들어 그 안에서만 구현해.
이 F1 세션에 한해 새 worktree 생성과 F1 branch로의 non-force push를 승인한다.

authoritative handoff:
research/foundation_rebuild/ncloud_f1_engine_admission_20260928/F1_CODEX_HANDOFF_KO.md

먼저 F0 execution host의 실제 artifacts가 남아 있으면
F0_ARTIFACT_IMPORT_CONTRACT.json에 따라 f0_evidence/로 import하고 exact hash를 검증해.
없으면 합성하지 말고 F0 import pending으로 남기되 F1 code 구현은 계속해.

그 다음 TDD로 다음을 구현해:
- runtime/native/archive_evidence.py
- runtime/native/cloud_engine.py
- runtime/native/engine_admission.py
- runtime/run_f1_engine_admission.py
- runtime/tests/*

F1_CONTRACT.json과 F1_REPRESENTATIVE_QUERIES.json을 변경하지 마.
기존 TP2A/TP2D scientific source도 변경하지 마.

이번 세션에서 허용:
- focused unit/integration tests
- fake compiler seam
- py_compile
- CLI --help
- commits and non-force push to F1 branch

이번 세션에서 금지:
- 실제 15-point BASS native admission run
- 새 scientific moment-engine execution
- worker scaling
- CF4/DOP853
- F2/F3
- threshold 변경
- main merge
- force push
- current main reset/clean/stash/rebase

runner는 RUN_AUTHORIZATION.json 없이는 실제 native science를 시작하지 못하도록 firewall을 구현해.
이번 세션에서는 authorization 파일을 생성하지 마.

완료 시 F1_RETURN_CONTRACT.json에 따라
F1_IMPLEMENTATION_COMPLETE_EXECUTION_NOT_RUN,
F1_IMPLEMENTATION_COMPLETE_F0_IMPORT_PENDING,
F1_IMPLEMENTATION_BLOCKED
중 정확히 하나를 반환해.

F1_ENGINE_ADMISSION_PASS는 아직 주장하지 마.

claim ceiling:
capture=false
production=HOLD
all_bound=OPEN
b_grid=NO_GO
original_capture_gap_resolved=false
continuous_global_supremum_bound=false
