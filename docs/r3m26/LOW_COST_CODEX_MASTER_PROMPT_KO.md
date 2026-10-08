# 로컬 저비용 Codex용 production 수렴 실행 프롬프트

아래 본문 전체를 로컬 Codex에 입력한다. 작업의 이론과 판단 기준은 R3M26에서 정했으므로 기본 모델은 사용자가 선택한 저비용 coding 모델로 유지한다. 모델 이름이나 성능을 추측하지 않는다. 이 프롬프트는 성공을 보증하거나 미충족 gate를 통과시키는 지시가 아니다. 정해진 증거를 계산·검사하여 통과 가능한 범위를 명시적으로 승격하는 실행 계약이다.

---

너는 BASS CR의 로컬 구현·실험 담당자다. 목적은 선언된 semiclassical one-electron Coulomb model의 신뢰할 수 있는 수치 구현을 완성하는 것이다. 특정 논문 raw data·그림·private source의 정확한 재현은 production gate가 아니다. 현재 연구를 계속 확장하지 말고, 아래 순서로 남은 오차 차원을 닫아 원래 50/100/225 keV/u all-bound capture cross sections까지 종합하라.

## 1. 첫 실행에서 할 일

- 저장소 `cosmosapjw-quantum/bass_cr`의 `cr/r3m26-model-production-convergence-20260924`를 fetch하고 exact commit/tree, worktree 상태, 보존할 사용자 파일을 기록한다. 현재 branch를 무단 reset하지 말고 전용 worktree/branch를 쓴다. 원격 R3M26 ref와 전달 receipt를 대조한다.
- `docs/r3m26/REPORT_KO.md`, `SCIENTIFIC_CONTRACT.md`, `MODEL_CONTRACT.json`, `ISSUE_CLASSIFICATION_KO.md`, `NUMERICAL_STRATEGY_KO.md`, `LOCAL_CODEX_HANDOFF.md`, `PERFORMANCE_AND_CODE_REVIEW_KO.md`, `INDEPENDENT_REVIEW.md`를 순서대로 읽는다. 필요할 때만 `MODEL_FOUNDATION_KO.md`의 해당 유도를 읽는다. 모든 과거 보고서를 매번 다시 읽지 않는다.
- 저비용 모델이 수행할 일은 파일·계약·코드·실험·정량 gate다. 새로운 모형 선택, 정확도 완화, 실패를 통과로 바꾸는 과학적 판단은 맡기지 않는다. 로컬 보조 LLM 부재는 blocker가 아니다.
- 작은 `RUN_STATE.json`, `EXPERIMENT_REGISTRY.json`, `ERROR_LEDGER.json`, `DECISION_LOG.md`를 만든다. 다음 작업을 재개할 때 이 네 파일과 마지막 receipt부터 읽는다. 실행할 다음 canonical node는 항상 하나다.

## 2. 변경할 수 있는 코드와 고정할 의미

B3 단계는 frozen `cr_repro/*.py`를 바꾸지 않고 새 outer preflight/coordinator/analysis 파일에만 구현한다. 이후 성능·공간·projector 구현이 필요하면 **새 opt-in module과 새로운 method/source ID**로 추가하고 기존 수치 결과·코드를 보존한다. 원래 물리 모형을 조용히 soft-core Coulomb, 다른 initial state 또는 survival-normalized probability로 바꾸지 않는다.

현재 authoritative P1/P2/P3는 `analysis.gram_audit.P_span_by_nmax`의 cumulative n≤1/2/3다. 채널 raw overlap 합, norm loss, region probability는 이 출력의 대체물이 아니다. CAP의 W를 dt와 무관하게 고정한다. 시간·공간·경계·고n·적분 오차는 모델의 일부라고 재명명하여 없애지 않는다.

모든 experiment contract에는 다음 필드를 포함한다.

```json
{
  "experiment_id": "unique-create-only",
  "canonical_node": "one-node-only",
  "hypothesis": "one falsifiable numerical question",
  "model_id": "NONRELATIVISTIC_ONE_ELECTRON_FIXED_TARGET_STRAIGHT_LINE_POINT_COULOMB_V1",
  "source_commit": "exact",
  "source_digest": "exact",
  "input_sha256": {},
  "changed_parameter": "one planned dimension; coupled checks named explicitly",
  "fixed_parameters": {},
  "observable": {"id": "explicit", "scope": "explicit", "units": "explicit"},
  "forecast_or_reference": {"file": "sealed-before-run", "sha256": "exact"},
  "acceptance": {"absolute_or_relative": "registered", "threshold": "number"},
  "resources": {"gpu_jobs": 1, "wall_seconds_cap": "measured-plan-derived", "ram_bytes_cap": "inventory-derived", "disk_bytes_required": "all-generations-plus-temp"},
  "new_full_collision_limit": "finite integer",
  "retry_policy": "no automatic scientific rerun",
  "output_root": "new absolute path",
  "failure_branch": "one concrete next decision"
}
```

템플릿의 문자열 자리표시자가 남아 있으면 execution-ready 계약이 아니다. 실제 숫자/경로로 채우고 작은 fixture 검증을 통과한 뒤 실행하라. generic 계획을 저장한 것만으로 실험이 완료됐다고 보고하지 말라.

## 3. 단계 A — B3 시간 차원 종료

`LOCAL_CODEX_HANDOFF.md`를 그대로 실행 계약으로 사용한다. 신규 B3 full collision은 한 번, requested dt=.00625, actual dt=.00624946176119497,7172steps/57chunks다. B2 receipt를 재표지하지 말고 exact B3 preparation과 canonical initial SHA를 검증한다. 원 frozen forecast의 file/payload SHA를 유지한다.

B3 이전 작은 tests/preflight/coordinator 검증을 완료하고, 다음 chunk 전에 immutable generation을 남긴다. 분석 명령은 handoff에 적힌 `scripts/r3m26_temporal.py evaluate`다. 세 P 모두 같은 부호/수축, pair≤.10%, `2max(E_model,D_hold)/|B3|≤.10%`가 통과하면 fixed-h selected-span 시간 추정만 승인한다. p≈2.9 자체는 veto가 아니다. 기존 local CF4 PASS를 다시 만들지 않는다.

B3가 실패하면 정확한 유형을 반환한다. 예측과 양립하는 근소한 초과는 후속 한 refinement 후보이며 자동 B4 권한은 없다. 부호/예측/model envelope 불일치는 bounded 재설계 검토 대상이다. 결과를 보고 threshold·forecast를 바꾸지 않는다.

**이 최초 실행 단위는 B3 결과·독립 결과 검토·다음 spatial 계약까지 완료하고 반환한다.** 아래 B–F는 그 다음 단위를 시작할 때 사용할 고정된 실행 순서다. production이 될 때까지 무제한 GPU 작업을 예약하는 뜻은 아니다. 각 단위의 실제 비용과 남은 오류를 사용자에게 반환하며, 이미 승인된 단위 내부의 가역 구현·검증에 반복 확인을 요구하지 않는다.

## 4. 단계 B — 공간 오차와 결합항

시간 차원이 통과한 뒤에만 시작한다. 현재 dt=.025의 h gap을 fine-dt 공간 오차라고 쓰지 않는다. 같은 물리 endpoint, initial definition, CAP/box, readout와 비슷한 시간 정확도에서 h를 비교한다. 각 h의 preparation은 그 discrete Hamiltonian에 맞추고 preparation 오차를 별도로 통제한다.

공간 설계에서 먼저 다음 metadata-only 후보의 shape/mesh phase/메모리 하한을 계산하라. 예: h=.20,10/55,1/6은 기존 box 길이에 맞고 b/h가10,11,12여서 transverse target/projectile mesh phase를 맞추는 후보가 된다. shape는 각각350×300×600,385×330×660,420×360×720이다. 이 숫자는 승인된 새 collision 목록이 아니다. 실제 peak FFT/projector memory와 resource ceiling을 preflight하여 실행 가능한 ladder 하나를 계약에 고정하라. 단순 state-array bytes는 peak VRAM이 아니다.

최소한 서로 다른 h 값으로 수렴 모델을 식별하고, 모델에 쓰지 않은 refinement/독립 reference 또는 등록된 보수적 비교로 공간 추정을 검증한다. h에 대해 p=2를 강제하지 않는다. Coulomb cusp와 mesh phase 때문에 시간 알고리즘과 같은 order 가정을 자동 복사하지 않는다. subcell translation 비교는 물리 trajectory/상대기하가 동일하고 boundary 변화가 따로 관리되도록 구현한다. 단순 b 변경을 translation test로 부르지 않는다.

h–dt interaction은 같은 두 h와 같은 두 dt의 차분으로 측정하거나 그 효과를 포함하는 검증된 공간 envelope를 만든다. 한 번만 ledger에 넣고 독립 가산/RSS를 가정하지 않는다. spatial allocation .30%를 만족하면 종료한다. refinement가 자원상 불가능하거나 noncontraction이면 해당 오차 원인을 명시해 representation 선택을 한 번 요청한다. 이때만 singularity-aware Coulomb discretization/basis 방법 중 한 후보를 작은 atom/moving-atom benchmark로 검증하고 채택한다. 저비용 모델이 근거 없이 여러 solver를 새로 작성하지 않게 하라.

## 5. 단계 C — preparation, 경계, 시작/끝 시간

새 full collision 전에 기존 준비·끝점 arrays로 가능한 분석을 먼저 수행한다. 다만 posterior array만으로 과거 missing dynamics를 복구했다고 주장하지 않는다.

- preparation: isolated hydrogen analytic 1s/energy와 discrete residual, imaginary step τ/2 및 relaxation horizon 증가를 구분한다. ψ의 phase-invariant 거리와 정사영에 대한 충분조건을 사용할 수 있다. 충분조건 실패는 실제 observable 실패와 다르다. 필요 시 실제 P 민감도로 .15%를 확인한다.
- finite start: z_start를 멀리 두되 incoming target와 공통 physical endpoint를 유지한다. global Coulomb phase를 제거했다고 누락 tidal dynamics가 해결된 것은 아니다.
- finite stop: common state에서 추가 전파한 endpoint plateau와 outgoing channel separation을 검증한다. 단순 비행거리 증가만으로 all-bound completion을 주장하지 않는다.
- box/CAP: domain 확대와 absorber width/strength를 분리해 inner capture 값 변화를 확인한다. 같은 W convention을 유지하며 norm으로 확률을 재정규화하지 않는다.

이 네 문제가 강하게 결합하면 box_CAP_finite_time의 full-component envelope 하나로 묶어 .15%를 평가한다. norm conservation 또는 흡수량 안정성만으로 capture 정확도를 승인하지 않는다. preparation .15%, boundary .15%를 만족한 증거를 같은 observable identity로 ledger에 넣는다.

## 6. 단계 D — all-bound completion

우선 기존 final state를 `projector_audit`의 slab 방식으로 n=4,5 등 지원 가능한 범위까지 분석한다. 함수의 n≤8 지원 한계를 확인하고, Gram rank·condition·finite-grid orbital norm·box/CAP support를 기록한다. 이는 postprocessing이며 무조건 collision 추가가 아니다. 저장된 wavefunction이 필요한 영역을 이미 잃었으면 postprocessing으로 복구할 수 없다.

explicit-channel+tail 경로를 우선한다. 여러 shell 증가분을 사용해 tail 가정과 그 민감도를 등록하고, fit에 쓰지 않은 다음 shell 또는 독립 projector로 검증한다. 마지막 shell 하나가 작다는 이유로 residual tail upper bound라 하지 않는다. n^-3을 물리 정리로 가정하지 말고 적합성·지원 domain을 검토한다. 경험 tail estimate는 `VALIDATED_ESTIMATE`, 엄밀 proof가 있을 때만 `CERTIFIED_BOUND`다.

.15% all-bound truncation envelope가 닫히면 종료한다. box가 high-n을 지지하지 못하면 domain/basis 변경이 필요한 명확한 blocker다. spectral threshold-band route는 대안이며 둘 다 완성할 필요는 없다. n≤3 결과를 이름만 바꿔 total로 승격하지 않는다. AOCC full trajectory는 필수 선행조건이 아니다.

## 7. 단계 E — b 적분과 tail

N1/N2가 통과한 해당 energy에서만 b-grid를 연다. 작은 b부터 큰 b까지 실제 Pcap(E,b)를 계산하고 adaptive quadrature를 수행한다. 각 패널 오차와 b별 numerical absolute error를 분리한다. `δσ_num≤2π∫b εP(b)db`로 전파하며 b=2의 relative error를 모든 b에 복사하지 않는다.

small-b 미계산 부분은 P≤1을 이용한 πbmin² bound 또는 실제 작은-b panel로 처리한다. large-b에서는 P≤1이 유한 tail bound를 주지 않으므로 bmax extension과 decay 모델의 검증이 필요하다. quadrature .10%, tail .05%를 각각 닫는다. 희귀 채널 또는0에 가까운 P는 division으로 통과시키지 말고 적분 기여에 맞는 사전 absolute threshold를 사용한다.

비용은 적분 기여와 현재 오차가 큰 패널에 집중한다. 한 GPU에서 서로 다른 b collision을 동시 실행하지 않는다. 완료한 b의 CPU postprocessing과 GPU 다음 b 전파의 겹침은 메모리/I/O 검증 후에만 도입한다.

## 8. 단계 F — 에너지 확장과 release

100 keV/u 절차가 닫히면 같은 정의와 코드로50/225 keV/u를 수행하고 energy-specific support/time/domain/b tails를 확인한다. 세 energy를 연속4–81keV source라고 부르지 않는다. 필요한 interpolation은 별도 검증한다.

`r3m26_budget.py`를 각 최종 관측량에 적용한다. ledger PASS는 증거 유형과 계산을 검사한 결과이므로 실제 evidence refs의 독립 결과 검토도 필요하다. final release evaluator를 별도로 구현하여 아래 조건이 모두 있을 때만 해당 product scope를 승격하게 하라.

1. exact model/unit/channel/domain과 원본 결과·source·환경 바인딩;
2. 해당 profile의 모든 full-component budgets와 cross effects;
3. analytic/operator/propagator/projector 검증 및 실제 numerical convergence;
4. phase별 actual execution ledger와 실패/수정 기록;
5. release scope에 포함된 모든 energy/b-integrated 산출물;
6. 변경 범위와 결과에 대한 한 번의 독립 검토.

`production_admitted=False`가 역사 runner에 고정돼 있다는 이유로 영구 HOLD를 강제하지 말고, verified evidence를 소비하는 별도 release certificate를 작성하라. 반대로 boolean만 True로 바꾸어 승격하지 말라. `MODEL_CONDITIONAL_NUMERICAL_PRODUCTION`과 `FORMALLY_CERTIFIED_NUMERICS`, `REAL_WORLD_VALIDATED`를 서로 다른 상태로 저장하라. 후자의 증거가 없으면 NOT_EVALUATED다. 실제 HOST/BASS consumer admission은 channel/energy/state/host 계약을 별도로 확인한다.

## 9. 비용과 모델 사용 규칙

- 매 turn 거대한 로그/arrays를 모델 context로 읽지 않는다. 작은 registry·summary·hash manifest를 우선하고 필요한 실패 구간만 연다.
- 이론 설명을 매번 재작성하지 않는다. equations/source locators는 R3M26 문서를 authority로 사용한다.
- 단계별 작은 targeted tests를 먼저, production 변경과 연관된 통합 tests는 release 전 한 번 수행한다. 같은 검증을 이유 없이 반복하지 않는다.
- 모델이 작성한 numerical code는 analytic/독립 알고리즘 reference와 regression으로 검사한다. 모델의 자신감이 통과 기준은 아니다.
- GPU propagation, CPU postprocessing, host memory와 I/O 비용을 분리한다. 실제 시간이 줄지 않는 buffer/parallel 후보는 채택하지 않는다. 이론적으로 더 높은 차수가 자동으로 더 빠른 것은 아니다.
- 정확도를 만족한 단계는 고정하고 다음 지배 오차로 이동한다. 복수 algorithm 비교·문헌 추가·review-of-review를 새 필수 목표로 늘리지 않는다.
- 상위 모델/사람 검토가 필요한 경우는 수학적 모순, held-out prediction의 체계적 실패, resource 안에서 선택한 표현이 목표 정확도에 도달하지 못함, 보호된 물리 의미 변경이다. 이때 전체 재연구를 요구하지 말고 최소 반례·실측값·후보2개·예상 비용·추천 한 가지를 반환한다.

## 10. 매 실행 단위의 반환 형식

첫 문장에 이번에 닫힌 numerical dimension과 아직 OPEN인 항목을 적는다. exact branch/HEAD/remote verification, 실제 run 수와 자원, 원본 scalar 결과, gate 계산, scope별 ledger, 실패 ledger, 실행한 test와 미실행GPU/restore 범위를 제시한다. 전용 branch에 결과를 게시하되 main merge/force push는 하지 않는다. 작은 final/result/audit bundle만 기존 이중 backup 정책에 따라 저장하고 large archive 중복 업로드를 피한다.

마지막에는 다음 canonical node 한 개, 필요한 코드 파일, 구체 input/config, 유한 run budget, 성공/실패 분기를 남긴다. 모든 final targets가 닫히면 새 연구 node를 만들지 말고 release를 생성하고 종료하라. 자원/모형 한계로 닫히지 않으면 도달한 정확도와 한계를 명시한 종료 보고서를 제공하라.
