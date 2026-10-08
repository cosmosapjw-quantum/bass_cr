# R4AN 원자 weak-K native 단일 cell

새 C++17/GMP 256 fractional-bit 구간 kernel과 immutable R4AM Python reference를 제공한다. 판정은 **CLOSED_NATIVE_THREE_CHART_FIXTURE_PARITY**이며 실제 원자 K 인증이 아니다.

실제 새 변경영역 시험 74건, 독립 검토 75조건. 일반 cell/target 원점/projectile 원점의 통합 fixture 3개, Gauss node 총 3072개. 저장 reference와 24개 실수/허수 구간쌍의 endpoint가 정확히 같다. 실제 candidate 적분과 full-K 호출은 0이다.

`source/weak_cell.cpp`는 실수 node 합만 계산한다. 동일 cell에 정당화된 analytic remainder를 더해야 cubature enclosure다. 공개 adapter는 fixture-only이며 actual candidate를 거절한다. `parent/`는 R4AM 정본의 기존 Git subtree와 같은 source/vendor/fixture 내용이며 수정하지 않는다.

읽기 순서: REPORT_KO.md → DERIVATION_KO.md → RESULT_SUMMARY.json → NEXT_DAG.json → CODEX_HANDOFF_KO.md.

새 환경에서 필요한 경우에만 새 fixture contract를 준비한다:
```
python source/prepare_fixture.py --output /absolute/new/fixture_output --contract /absolute/existing_parent/new_contract.json
python source/run_parity.py /absolute/existing_parent/new_contract.json
```
이 명령은 원자 실행 승인이 아니다. 증거 폴더의 이미 소비된 계약은 다시 실행하지 않는다. Native binary는 새 환경에서 빌드한다. 검증된 S-only 10점, M9, 중심점, 옛318patch를 재실행/재적용하지 않는다.

다음 노드는 R4AO_WEAK_K_FINITE_CANDIDATE_SINGLE_CELL_PILOT다. Candidate/cell/entry/majorant/resource를 새로 고정하기 전 actual integral cap=0. G02=UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO.
