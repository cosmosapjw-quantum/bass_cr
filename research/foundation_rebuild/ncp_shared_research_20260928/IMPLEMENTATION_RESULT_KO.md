# R3 구현·실제 archive 검증 결과

상태: R3_CODE_AND_CACHE_AUDIT_COMPLETE_CLOUD_REVIEW_PENDING.
주 구현자: ChatGPT. Cloud Codex는 집중 검토·필요한 수정·준비된 cache-only 실행을 담당한다.

## 구현한 코드
runtime_r3/integrity.py: 파일 해시·strict JSON·ZIP path/type/budget·NPY header 검증, create-only atomic 쓰기.
runtime_r3/cache_bridge.py: pinned source/evidence chain을 읽고297개 finalized task를 원 NPZ/receipt bytes/ID/context 그대로 새 출력에 복사하는 additive reader.
runtime_r3/metric_diagnostics.py: 독립 centered-FD overlap derivative, 원 relative residual 재현, complex triangular-solve whitening, H 비Hermiticity 추가항 및 조건수 진단.
runtime_r3/run_cache_audit.py: code/input/environment 검증과 결과·최초 실패·output manifest 보존. native BASS import, compiler, process pool, fallback API 없음.

## 실제 수행한 신규 검증
- 신규 focused pytest53개 통과, failure/error/skip0. 원18/32/48/30/16 suites 미실행.
- Python6파일 py_compile 통과. CLI --help 및 shell 구문검사 통과.
- 원 builder의 output-path-dependent identity를 fake compiler로 assertion RED 재현. 원 source/binary/numeric이 동일해도 legacy identity는 달라진다.
- 반환 배열의 write flag를 되돌릴 수 있는 결함을 신규 RED로 확인한 후 immutable bytes-backed view로 수정했다.
- 실제297개 task pair,2673개 배열,597개 original member 검증. 두 fresh directory의 원 bytes·IDs 일치를 확인했다.
- 원 source/code·입력/threshold/basis는 변경하지 않았다. R2 generic native resume를 수정했다고 주장하지 않는다. 새 reader의 범위는 finalized-evidence 재사용이다.

다섯 metric sentinel의 기존 relative residual은 모두 정확히 재현됐다. 최대값은2.3253812582402828e-9이고 whitened connection spectral norm의 최대값은1.9772810219871182e-10 per original atomic time다. S 조건수는 약1.00991~1.37563이다. 실제 저장 샘플의 진단이며 continuous supremum/integral eta/최종 fidelity certificate는 NOT_CERTIFIED다.

계산은 Python3.13.5/NumPy2.3.5/SciPy1.17.0의 ChatGPT runtime에서 수행했다. 원 NCP generator는 Python3.12.3이며, 그 사실은 원 receipt 그대로 보존했다. 이식 가능한 배열을 읽은 것이지 새 host native engine을 승인한 것이 아니다. 마지막 독립 cache-only command의 elapsed는 1.734949s이며 NCP wall-clock benchmark가 아니다.

## 산출물·후속 작업
implementation_evidence/의 R3_RETURN, CACHE_AUDIT, METRIC_DIAGNOSTICS, VERIFICATION과 compact IMPORT_BRIDGE_SUMMARY를 읽는다. full IMPORT_BRIDGE와 원 bytes를 포함한 결과 directory는 delivery/dual-backup checkpoint에 있다. 원297개 NPZ를 Git에 중복 추가하지 않는다.

Cloud는 CLOUD_REVIEW_RUN_HANDOFF_KO.md의 single-process command를 사용한다. Code/source/environment가 그대로인 동일 run을 반복하지 않는다. 고칠 결함이 있으면 영향 범위를 테스트하고 작은 patch로 반환한다. 새 기능을 처음부터 재구현하지 않는다.

NEXT_PHYSICS_GATE_DRAFT.md는 다음 finite-span quantity의 정의와 필요한 입력만 고정한다. 실제 capture/production, 새 full trajectory/basis, native compile, F2/F3, 이전3600초/4000원 allowance 재사용은 승인하지 않는다.

독립 reviewer: 미수행, Cloud Codex 검토 대기. Self review와 독립 심사를 구분한다.
