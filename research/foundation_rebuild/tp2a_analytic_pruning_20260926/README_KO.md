# BASS TP2A analytic pruning: 독립 연구·검증 패키지

이 패키지는 직전 HP full geometry run을 대신 자동 실행하지 않는다. 기존 repo와 사용자 run을 수정하지 않는 독립 실행형 연구 산출물이다. 원격 source anchor는 fa5903a54c57326c12d7f60cb2444c68a8eb2392이며, 입력 물리 데이터는 제공된 HP 진단 패키지의 동일 finite FEM coefficient bytes이다. 최신 사용자 raw48-task archive를 받았다고 주장하지 않는다.

## 이미 실행한 범위

- Wolfram: 약한 gradient contraction 각도차수, 여섯 Bessel moment, Cartesian unitary 및 reflection, polar Jacobian 검사.
- 신규해석식과 원래 unpruned ring의 arbitrary-velocity s+p raw six-block 검사.
- 실제18-channel z=-4,-2의 선택된 중앙 snapshot과 z0의 h2q56/h2q64 전체 중앙차분 stencil.
- 고정 collision-plane에서18→14 even sector의 직접 계산과 full projection 일치.
- 기존 native ring 대비 같은 호스트/같은 규칙의 성능 비교와3-process parity.
- Polar-shell 적분 대안은 raw screen FAIL로 탈락. code/polar_shells.py는 탐색 기록이며 canonical runner는 사용하지 않는다.

보고서와 MATHEMATICS_KO.md에 증명·근거·비채택 대안·미검증 범위를 나눠 기록했다. 낮은차수 실패, fixture 작성 오류, 새 disjoint-guard 결함의 RED/GREEN도 evidence에 보존한다. 본 응답 이전 중단된 scratch는 사용하지 않고 source archive에서 복원한 사실을 PLAN.json에 기록했다.

## 1. 새 계산 없는 검산

```bash
python3 verify_research.py --out VERIFY_LOCAL.json
```

manifest·NPZ를 읽어 원래 연구 결과와 새 결과를 재계산한다. C++/Wolfram 설치, 새 quadrature, GPU/전파를 하지 않는다. 잘못된 극소오차 PASS만 검사하는 것이 아니라 탈락한 polar route의 FAIL도 재현한다.

## 2. 새 커널의 로컬 확인

기존 Python, NumPy, SciPy, pytest와 g++를 사용한다. 자동 pip/apt 설치는 없다. 공유라이브러리는 배포하지 않으므로 새 해석 커널을 한 번 별도 경로에 빌드한다. 기존 libring_sp.so와 다른 라이브러리다.

```bash
BUILD="native_local_$(date -u +%Y%m%dT%H%M%SZ)"
python3 code/build.py --out "$BUILD"
OUT="runs/analytic_z0_$(date -u +%Y%m%dT%H%M%SZ)"
echo "OUT=$OUT"
python3 code/run_validation.py --native-build "$BUILD" --workers 6 --out "$OUT"
echo "ANALYTIC_EXIT_CODE=$?"
```

6개 독립 node만 실행하므로 worker 상한도6이다. 작은 CPU/cgroup에서는3 또는 그 이하로 지정한다. Worker당 BLAS/OpenMP는1 thread다. 물리basis는 입력파일에서 읽으므로 새 고유벡터 계산이 없다. Target1s even pruning의 증명과 테스트는 포함되지만 이 canonical six-node verification은 full18 matrix를 검사한다. 현장에서 epsilon·order·phase budget을 변경하는 flag는 없다.

정상 상태는 ANALYTIC_Z0_QUALIFICATION_PASS. q56/h2 및 q64/h2의 z=-1e-4,0,+1e-4 여섯 고유 계산을 수행하고, 후보/reference 역할9개 중3개 중복은 같은 raw결과를 참조한다. 이 alias를 독립증거로 세지 않는다. 원래의 별도ring 적분으로 생성한 세 reference 파일과도 비교한다.

```bash
jq '{status,scope,connection_relative,max_external_relative,max_refinement_relative,unique_operator_evaluations,role_requests,aliased_requests,failed_screens,first_failure,capture_execution_allowed}' "$OUT/RETURN_REPORT.json"
sha256sum "$OUT/RETURN_REPORT.json" "${OUT}_RETURN.zip"
```

각 완료node의 NPZ/receipt는 보존하지만 이 제한된 연구 runner는 자동 재시도나 옛9-geometry task의 import/resume을 구현하지 않는다. 실행 중단 시 먼저 보존된 결과를 확인하며 무조건 재실행하지 않는다. 기존 원격 qualification pipeline을 교체하는 것은 별도 integration gate다.

## 3. 로컬 성능 실험(선택적 별도 실행)

```bash
PERF="runs/analytic_perf_$(date -u +%Y%m%dT%H%M%SZ)"
python3 experiments/benchmark.py --native-build "$BUILD" --workers 6 --out "$PERF"
```

이 명령은 동일h2q56,z0에서 원래native/full analytic/even analytic을 각각한번 계산하고 병렬 처리량을 측정한다. 원본kernel 재계산은 성능실험에서만 의도적으로 수행한다. 물리적 정확도 확인만 원하면 이 별도실험을 추가할 필요 없다. 벤치마크의 I/O/CLI는 현재 create-only판이며, 보고서의 실측 당시 전체 스크립트는 evidence/benchmark_executed.py로 보존했다.

## 제한과 상태

지금 제공한 source는 원래 물리적FEM과 적분모델을 보존한 새 analytic backend다. 원래root/cross기능이나 GPU forward를 바꾸지 않았다. GitHub 쓰기도구가 현재 노출되지 않았고 container Git DNS 조회도 실패했으므로 이번 응답에서 원격push는 수행하지 않았다. 이전 HP apply_and_push.py를 이 패키지에 실행하지 않는다.

항상 production=HOLD, all_bound=OPEN, b_grid=NO_GO, capture=false. 14-dimensional pruning은 exact planar and even-initial-state finite model에만 허용하며, 일반18-channel basis completeness나 capture cross section을 뜻하지 않는다. 전체양의z geometry, 새로운전파, 원래GPU3% 차이는 미검증이다.
