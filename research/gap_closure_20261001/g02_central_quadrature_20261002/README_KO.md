# R4Y 중앙 공간 적분 연구

R4X 연속 기저의 b=2a₀,100keV/u,z=0 한 점에서 공간 적분 qualification을 확보했다. 실제13개 완전한 cross-operator 평가, 원래 threshold, 수정하지 않은 raw S/H/D를 근거로 한다. G02 전체는 UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO다.

`TASK_CONTRACT.json`은 고정 입력·수치·24회 전역 cap·성공조건을 정의한다. `DERIVATION_KO.md`/`THEORY.json`은 횡위상 해상도 진단, 세 동일 s–s 중앙 raw D 대각이 정확히0이라는 유도, θ 경계 분할의 수학적 의미를 기록한다. `phase_pairs.py`는 원래 FEM/삼각 경계를 보존하고 inner 패널만 추가하며, `runner.py`는 별도 context와 task identity를 만들고 자원·예약·실패 정리를 관리한다. 원래 기저나 기존 production provider를 교체하지 않는다.

최종 선택은 기존 q56,h2↔q64,h2에 q48,h4 비교를 추가하고, 새 q40,β24↔q48,β24에 q40,β12 비교를 추가한 것이다. 여기서 q는 Gauss 차수, h는 기존 subdivisions 수, β는 inner 위상 budget(rad)다. 여섯 raw block 최대 상대 차이는 각각1.24002e−14와1.19516e−14이며, 두 규칙 사이도2.95605e−14 이내다. 원래 기준은1e−9이고 각 해상도의 full screens와 세 s 대각 절대값≤1e−12/ta도 동시에 통과했다. q32,β24와 기존 낮은 해상도 실패는 그대로 보존한다.

재현 자료의 기준 경로는 작업공간 root 아래 `runs_r4y/central_v1/`다. `CONTEXT.json`의 SHA256은 `2b28f6ee484de9075e769ded2e9777edd50017dd6b3338f6662a2294a8d021c6`이다. `batches/`의 stage1_parity, stage2_legacy, stage3_refinement, stage4_phase_order에 완료2/4/6/1회가 각각 있고, `reservations/`에는 총13개 예약이 있다. 실행된 numerical source/input pin을 바꾸면 이 context를 재사용하지 않는다. 새 환경에서 물리 재실행할 때는 입력·native·자원을 새로 binding하고 새 output/context를 생성한다. 기존 완료 디렉터리를 덮어쓰거나 실패 task를 재시도하지 않는다.

실행 후 분석을 재현하려면, 완전한 복원 경로와 원래 source/input binding을 먼저 확인한 뒤 `RUNNER_API.md`의 환경 변수를 적용하고 아래처럼 **새 결과 경로**를 지정한다. 분석은 물리 연산자를 실행하지 않는다.

```bash
python recovered_r4u/source/research/gap_closure_20261001/g02_central_quadrature_20261002/analyze_results.py \
  --root runs_r4y/central_v1 \
  --context-sha256 2b28f6ee484de9075e769ded2e9777edd50017dd6b3338f6662a2294a8d021c6 \
  --out runs_r4y/CENTRAL_RESULT_REPLAY.json
```

분석기는 context 안의 절대 경로와 source/input pins도 확인하므로 패키지를 다른 경로에 풀었다는 이유만으로 기존 context를 편집해서 통과시키지 않는다. 경로가 달라졌으면 보존된 raw payload와 manifest를 이용한 별도 read-only 복원 분석을 구별되는 identity로 작성하거나 원래 경로에 복원한다. 위 명령은 원래 binding이 성립하는 환경에 대한 재현 명령이다.

새 테스트20개는 `test_phase_pairs.py`8개와 `test_runner.py`12개이며 실제 physics 호출을 하지 않는다. DB·패키지 builder는 context 생성 전에 작성되어 실행 source pins에 포함되어 있다. `analyze_results.py`와 이 README·보고서는 실행 후 추가된 분석·서술이며 기존 실행 source freeze에 소급 포함되지 않는다. 최종 독립 검토는 `PASS_LOCAL_CENTRAL_SPATIAL_ONLY`이며 원자료13개와78쌍 비교의702개 norm 값이 재계산과 일치했다. 근거는 `runs_r4y/INDEPENDENT_REVIEW.json`, 해석·제한은 R4Y 한국어 보고서를 따른다. 같은 중심 적분 order20은 고정했으며 이번 연구에서 독립적으로 세분하지 않았다.

새 패널의 성공한 차수 쌍은 기존 쌍보다 radial pair 점 수가3.01065배 적다. 단회 worker 시간은 통제된 benchmark가 아니며 OpenMPI/NCP64 scaling은 아직 측정하지 않았다. 다음 작업은 공간 qualification을 미분 stencil의 각 위치로 확장한 뒤 독립적인 `dot S=D+D†` 검증을 수행하는 것이다. phase budget은 위상 변화 제한이며 연속 적분 오차 인증이 아니다.
