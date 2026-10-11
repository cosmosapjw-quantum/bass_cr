# CR-PHYS02D 실제 NCP pulse 실행 반환

판정: **FIRST_FAILURE_PRESERVED / 독립 HOLD**. 과학 PASS 없음.

고정 science `6ed83ff61aff24fe51ff0370736f70e0e52893f8`, publication `a2486869dba5c2d43257c13e33a31b66752d5e10`. 정확한 Dropbox ID/rev로 시작 문서와 ZIP을 복원했고 외부 크기/SHA256, CRC, 360 entry 집합, 359 payload 및 259 dependency를 검증했다. PR32 기존 소스와 입력·허용값·원본 adapter는 변경하지 않았다.

실제 단 한 번 명령은 `venv/bin/python ncp/launch_pulse.py --execute --run-dir <EXECUTION_SUMMARY.json의 절대 run_dir>`이다. cwd는 동일 복원 study다. UTC 2026-10-11 00:27:45–00:29:29, launcher/worker exit **1/1**, coordinator wall **103.797892739 s**. 제공 wrapper는 실패 반환 수집 뒤 exit0이지만 물리 성공이 아니다. wrapper 전체 wall104.81s, peak RSS4,149,932KiB. Python3.12.3/NumPy2.4.2/SciPy1.17.0, 실제 pool thread1. admission READY와 resources admitted=true; reserve16,881,319,936bytes, 초기 작업 가능115,396,161,536bytes, disk53,410,729,984bytes. 각 단계의 실제 resource는 raw receipt를 따른다.

fullBED G 생성 한 번이 반환된 뒤, matching NPZ의 `energy_eV` exact array_equal 검사가 실패했다. 두 saved NPZ와 재구성 격자 모두 340/9600 node에서 최대1ULP, 최대1.1368683772161603e-13eV 차이다. 다른 필드/time/source shape/tags는 맞다. SIMD/libm 원인은 확정하지 않았다. exact guard를 allclose로 바꾸거나 입력을 덮어쓰지 않았다. G는 메모리에만 있었으며 반환 행렬 파일은 없다.

| 모델 | 실제 도달 | CDF / 지연 모멘트 / ramp 잔차 |
|---|---|---|
| fullBED | G constructor 반환; 입력 격자 guard 실패 | 계산되지 않음 |
| legacy | 시작하지 않음 | 계산되지 않음 |

G build reservation1, pulse reservation0; 실제 pulse0, 기존 ramp/과학 suite0. 자동 재시작0. 모든 worker/coordinator 종료와 terminal receipt를 확인한 뒤 동일 run을 수집했다. 최초 wrapper 수집 ZIP과 영수증은 보존하고, terminal 이후 진단·wrapper·resource·독립 검토 sidecars를 추가한 최종 수집 ZIP을 별도로 만든다. RETURN manifest exact entry, 모든 size/SHA256, source-unit FILE manifest, dependency manifest, review bindings와 별도 새 위치 복원을 검증한다.

독립 요청 route gpt-6-astra 검토는 HOLD다. 실제 backend는 reviewer가 독립 확정하지 못했음을 기록했다. 다음 bounded amendment 요청은 G 생성 **전** exact grid 검증과 동일 saved-grid/runtime 재구성 방법에 대한 별도 심사다. 추가 물리 호출을 승인하지 않는다. one-shot 호출 budget을 새 이름으로 재사용하지 않는다.

PHYS02_DELAY OPEN; production_history HOLD; atomic_G02 UNRESOLVED; b_grid NO_GO; all_bound OPEN; R17B2B NO_CERTIFIED_SOURCE_SHARPENING; CCC SOURCE_IDENTITY_UNRESOLVED 유지.
