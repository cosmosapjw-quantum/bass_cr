# 원요청 전체 단계 감사 — R4T 기준

**판정: CR의 최초 STEP 1–10은 실제 유도·코드·검증 산출물을 남겼지만, 전체 연구 단계와 production solver 실행은 완료되지 않았다.** HE의 더 이른 문헌 복구 계약은 별도이며, 선택 논문 24편의 원문 확보 및 이중 백업은 확인된다. 두 프로젝트의 완료를 서로 대신 세지 않았다.

감사 기준은 R4T `e1438233548cf01fa9894d17e194acba49e0ac7b` / tree `a20f9a68f59029d377e4772a589b7458e8a9d999`이다. HEAD는 [게시 receipt](</workspace/scratch/63ee2321a512/deliverables/BASS_CR_R4T_DELIVERY_RECEIPT_20261001.json>)에 근거한다. 로컬 자료는 `.git` 없는 selective snapshot이므로 이번 감사가 새 remote HEAD 검증이라는 뜻은 아니다. 원 CR 계약 [INPUT_CONTRACT.txt](</workspace/scratch/63ee2321a512/recovery/r4r/INPUT_CONTRACT.txt>) 1,739행 및 HE 계약 673행을 모두 읽었다. 동시 진행 중인 R4U 구현은 이 기준 이후 변화이며 그 자체 검증을 기다린다.

기계 판독본 [REQUIREMENTS_MATRIX.json](</workspace/scratch/63ee2321a512/cloud_audit_20261001/contract_audit/REQUIREMENTS_MATRIX.json>)은 CR 37절+10 STEP마다 **유도 / 실행 코드 / synthetic / 기존 physical / 새 physical / closure 근거 / 남은 gap**을 분리하고, HE17절과 완료조건 A–H를 별도 수록한다. 모든 근거 파일의 SHA256·bytes와 Python 정의 위치도 포함한다. 기존 테스트나 물리 실행은 반복하지 않았다. 감사 중 확인한 stale bridge 메타데이터는 요청에 따라 source 한 파일에서 수정했으며, 아래에 발견 당시와 수정 후를 구별했다.

## 생산 실행을 막는 확인된 미완성 항목

| 항목 | 실제 확인한 구현·증거 | 남은 일 |
|---|---|---|
| HPC와 물리 실행의 연결 | [mpi_queue.py:3](</workspace/scratch/63ee2321a512/bass_cr/research/gap_closure_20261001/hpc_optimization_20261001/mpi_queue.py>)는 synthetic CLI만 실행 가능하다고 명시하고, RESULT의 `legacy_executors_modified=false`이다. G02/G03는 여전히 legacy ProcessPool 경로다. | strict Fortran/OpenMP kernel, MPI scheduler, qualified physical provider, cache identity, 전역 raw-attempt 예산을 실제 호출 경로에 연결해야 한다. |
| G12 독립 propagator | [propagate_cf4](</workspace/scratch/63ee2321a512/bass_cr/research/gap_closure_20261001/independent_propagator_20261001/independent_propagator.py>) 구현과 synthetic 비교는 있다. [물리 계약](</workspace/scratch/63ee2321a512/bass_cr/research/gap_closure_20261001/independent_propagator_20261001/PHYSICAL_PARITY_CONTRACT.json>)은 NOT_NATIVE_READY이며 `initial_nstep`, `method_parity_budget`가 null이다. | 같은 physical IVP/provider/Sdot/initial-state hash와 예산을 묶은 실제 비교가 필요하다. 단순 실행 허가 문제가 아니라 입력·adapter 구현도 남았다. |
| G04 실제 복소 연속 enclosure | [validated_majorant._matrix:82](</workspace/scratch/63ee2321a512/bass_cr/research/gap_closure_20261001/majorant_validated_20261001/validated_majorant.py>)는 real symmetric만 허용하고 complex는 미구현이다. generic Proof 검사는 provenance 모양을 검사할 뿐 수학적 입력 정리를 자동 증명하지 않는다. | B0 복소 Hermitian weak residual의 연속 metric·미분·quadrature enclosure와 실제 적분 bound가 필요하다. |
| G02/G03 최소 새 관측 | shrinking-h FD 실행기 및 signed±48 discriminator/return scorer는 구현·synthetic 테스트됐다. 실제66 new FD queries와2 discriminator queries는 실행 기록이 없다. | 독립 Sdot 절단오차·plateau와 asymptotic model 구별을 최소 측정으로 확인해야 한다. |
| G06/G11 window·tail 상태 | 기존±12 temporal 자료와 state-free static matrices는 있으나 nested±16/24/32/48/64 상태·norm·P·integrated-rho acceptance table은 없다. | 최초 확장 window를 위한 실제 상태 전파, collector, 동일 observable 오차 예산이 필요하다. |
| 모델 전이와 오차 합계 | literal archived basis와 repaired H1 reference는 다르다. repaired reference에도 derivative-jump shell이 있어 generic strong-L2 residual 경로는 성립하지 않는다. finite-metric transfer theorem은 있으나 실제 입력 계약이 비어 있다. | 두 계의 metric defect/growth, 공통 embedding/observable, 초기 상태, transfer residual을 수치 bound에 연결해야 한다. |
| 오차 예산 메타데이터 불일치 — 수정됨 | 감사 당시 [R4T registry](</workspace/scratch/63ee2321a512/bass_cr/research/gap_closure_20261001/GAP_REGISTRY.json>)의 새 bridge는 `25227/50 = 504.54`인데 current error budget에는 `55408/11 = 5037.0909…`가 남아 있었다. 요청에 따라 [source budget](</workspace/scratch/63ee2321a512/bass_cr/research/gap_closure_20261001/ERROR_BUDGET_CURRENT_B0.json>)을 certificate에 맞춰 동기화했다. 이전값·history·새 provenance hash를 보존했다. | old bound는 더 보수적이었다. 수정 후에도8개 component.value 및 certified_total은 null, target fail, reference 미채택, state transfer null이다. 기게시 detached budget는 별도 재게시 전까지 이전값이다. |
| G13 및 후속 production | B0/B1/B2/B3 18/46/92/124 ladder는 정의됐지만 higher-l optimized backend와 실제 radial/rank/temporal/window qualification chain이 없다. | fixed-b window·basis·all-bound를 먼저 닫은 뒤 b-grid와 σ를 실행한다. 원계약의 b-grid 보류 자체는 위반이 아니다. |

## 무엇이 실제로 진행됐는가

G01 local-rho 항등식·projector rate·covariance, G07 eigensolver conditioning, G08 raw-block 비불변 반례와 metric coupling, G09 rank policy, G10 semantic selector는 코드·synthetic 근거가 있다. G03은 기존 signed8점 fit/holdout과 문헌 기반 분석을 수행했다. G04는 합리수 synthetic continuum certificate에서 실제 radial coefficient의 repaired-reference metric/bridge 정리로 진전했다. R4T는 weak Galilean cancellation·angle bound·strong-domain obstruction과 finite-metric transfer 정리를 추가했다. 이는 단순 문서 계획만은 아니다.

그러나 R4Q 이후 R4T까지 **새 physical operator query=0, 새 physical propagation=0**이다. 저장된 matrix replay와 새 reference coefficient의 exact certification은 새 trajectory 실행이 아니다. gap 상태는 CLOSED 3개(G01/G08/G10), LIMITED 6개(G03/G04/G05/G07/G09/G12), BLOCKED G02, UNRESOLVED G06/G11/G13이다. LIMITED나 “loop complete”는 원 scientific claim 전체 완료를 뜻하지 않는다.

R4S의 strict-FP kernel은 실제 성능 개선을 보였다. 기록된 local8CPU 환경에서 portable single-thread3.6746×/8thread9.2407×, native-arch single-thread6.8478×/8thread15.0100×이고 synthetic MPI queue4rank×2thread는6.156×였다. 이는 64core/128GiB NCP scaling이나 실제 physical end-to-end speedup의 측정치가 아니다. MPI binding_verified도 false였으므로 NCP 실기 topology·affinity·메모리·throughput 확인은 남는다.

검증 수는 재실행을 중복 합산하지 않았다. 기록 범위는 R4Q114, R4R30, R4S19unique(+7 affected architecture rechecks), R4T30new(+33 exact assertions와6 saved-matrix replays)이다. DBv6는 sources31/code_snapshots4/documentation17/report_gaps13/research_gap_status13/research_claims36으로 읽기 전용 조회했다.

## CR 원계약 0–36절 대조

표의 “실행”은 유도·코드·기존자료 검증과 새 physical 실행을 구별한다. 상세 lane별 판정 및 정확한 원문 line 범위는 JSON을 참조한다.

| 절 | 주제 | 판정과 실행된 범위 | 남은 gap |
|---|---|---|---|
| 0 | CORE OPERATING PRINCIPLE | **FOLLOWED** — 이론·synthetic·physical 층위를 구별하고 claim ceilings를 유지했다. | 운영규칙 준수는 scientific completion이 아니다. |
| 1 | AUTHORITATIVE INPUTS | **COMPLETED_FOR_CHECKPOINT** — v3 authority inventory에서 v4/v5/v6로 연구테이블만 확장했다. | 로컬은 selective snapshot이며 .git이 없어 HEAD는 게시receipt 기준; 별도 현재remote 재확인이 필요하다. |
| 2 | CURRENT DATABASE CONTENT TO EXPECT | **COMPLETED** — 31sources/4code/17docs/13report_gaps와 원 REPORT_GAP ID가 DBv6에 보존된다. | 별도 미해결 항목 없음; 적용조건은 JSON 참조. |
| 3 | FROZEN CURRENT SCIENTIFIC STATE | **PRESERVED_NOT_REEXECUTED** — 18ch/100keV/u/b2/±12 temporal gate와8 static points를 역사적 증거로 보존했다. | tail states 및 새window certificate는 없다. |
| 4 | MASTER GOAL | **DAG_ONLY_END_GOAL_OPEN** — 의존 DAG는 존재하나 production까지 실행되지 않았다. | fixed-b finite window→basis→all-bound→b-grid→cross-section 모두 후속 scientific gate가 열려 있다. |
| 5 | RESEARCH LOOP MECHANISM | **PARTIAL** — 핵심 연구 lanes는 theorem/code/test/DB/backup까지 수행했지만 모든 gap에서 physical return/closure가 완성된 것은 아니다. | RESOLVED_WITH_LIMITATION은 원 unresolved claim 전체 closure가 아니다. |
| 6 | G01 — LOCAL rho TO INTEGRATED PROBABILITY THEOREM | **COMPLETED_CONDITIONAL_THEOREM** — G01의10가지 항등식·정리·가정·단위·constant-basis covariance를 유도·구현했다. | 실제 Sdot compatibility와 integrable physical tail은 정리의 미입증 적용조건이다. |
| 7 | G02 — INDEPENDENT Sdot = D + D† VALIDATION | **IMPLEMENTED_NOT_PHYSICALLY_EXECUTED** — G02 shrinking-h FD postprocessor와66new+6reuse query 실행기까지 구현했다. | 실제64shift+±12centerD가 없어 독립 Sdot convergence/plateau를 확인하지 못했다. |
| 8 | G07 — GENERALIZED EIGENSOLVER / CONDITIONING | **PARTIAL_CONDITIONING_DOMAIN** — eigh(W,S)와Cholesky congruence,100digit 2x2,condition sweep 및8saved matrices를 검사했다. | whole rate assembly cond(S)>=1e8 문제와 uniform forward error는 남아 있다. High-precision lane은 rounded synthetic2x2이며 directed interval이 아니다. |
| 9 | G08 — BASIS-COVARIANCE / DIAGNOSTIC SEMANTICS | **COMPLETED_WITH_DECLARED_DOMAIN** — norm/P/projector/spectrum/rho covariance와raw K_TP 비불변 반례 및 별도metric coupling을 구현했다. | 별도 미해결 항목 없음; 적용조건은 JSON 참조. |
| 10 | G03 — rho ASYMPTOTIC FORM | **PARTIAL_NOT_MODEL_IDENTIFIED** — acquired collision sources 기반 유도, M1–M4 signed fits/holdouts/branch-switch 반례와최소±48선정을 수행했다. | 새±48/offgrid관측이 없어 empirical model identified closure가 아니다. fixed-J 잔차floor 가능성도 남는다. |
| 11 | G04 — CONTINUOUS MAJORANT | **PARTIAL_PHYSICAL_MAJORANT_OPEN** — RouteA/B 실제 유도·코드·syntheticLEVEL2, repaired reference metric와finite bridge 정리가 있다. | B0 complex continuous enclosure engine/input proof가 없다. _matrix는real-symmetric만 지원하고 proof metadata validator는theoremchecker가 아니다. 새reference bridge504.54는5e-6목표실패. |
| 12 | G05 — INFINITE-TAIL INTEGRAL | **PARTIAL_FAR_REFERENCE_ONLY** — p2 integral exact enclosure와named-reference gapped O(Z^-2) far-tail cutoff14312가 계산됐다. | incoming/outgoing originalB0 bound는null. Far-only bound가per-side예산전체를 사용하며bridge/state전이여유가 없다. |
| 13 | G06 — TIGHTNESS OF rho ENVELOPE | **NOT_PHYSICALLY_EXECUTED** — state-aware angle inequality 연구는 있으나 nested B0 window tightness study는 없다. | ±16/24/32/48/64 full-window endpoint/state/norm/integratedrho/uncertainty table가 없다. Scheduler·collector도해당study용구체구현이확인되지 않는다. |
| 14 | G11 — B0 FINITE-WINDOW CLOSURE | **ACCEPTANCE_DEFINED_NOT_CLOSED** — common-observable error composition과finite-metric transfer theorem은 있다. | operator bound/nestedwindow/physicaltail/initialstate transfer가 없어서 executable acceptance pipeline 및 actualwindow closure는 미완성. |
| 15 | G09 — RANK LOSS / BASIS CONDITIONING POLICY | **POLICY_SYNTHETIC_IMPLEMENTATION_ONLY** — canonical truncation/pivotedCholesky/SVD/QR 및newbasisidentity를 synthetic에서검사했다. | realB1+ cutoff/rank/angle/rho/observable sweep및고정physicalthreshold 없음. |
| 16 | G10 — SEMANTIC SELECTED SUBSPACE | **COMPLETED_B0_SEMANTIC_SELECTION** — semantic query가B0five states를 재현하고 reorder/중복/energy/kind검사를 통과했다. | B1+ 실제radialidentity의존부분은그basis생성시별도검증. |
| 17 | G12 — INDEPENDENT PROPAGATOR FAMILY | **PROTOTYPE_IMPLEMENTED_PHYSICAL_PARITY_ABSENT** — Cholesky derivative/CF4 reference와existing midpoint/DOP853 synthetic comparison 수행. | contract NOT_NATIVE_READY; provider/Sdot/initialstate/pinnedbudget/nstep미결. 실제B0독립가족comparison 없음. |
| 18 | G13 — B1/B2/B3 COMPLETENESS | **SYMBOLIC_REGISTRY_ONLY** — 18/46/92/124 ladder와prerequisite를기록했으나B1–B3완전pipeline없음. | higher-l optimizedbackend l>1 unsupported; actualnewradialbank/Gram/qualification/temporal/window/completenessrecords 없음. |
| 19 | ALL-BOUND CAPTURE GATE | **GATE_CONTRACT_ONLY** — L0–L5의의미구별은유지한다. | all-bound capture: basis/window/pseudostatecontamination/asymptotic증거미완성. |
| 20 | b-GRID AND CROSS SECTION | **INTENTIONALLY_NOT_EXECUTED** — 원요청자체가b-grid실행을금지한조건부미래단계다. | adaptiveb quadrature/small-largeb tail/σ errorcertificate는미구현. 현재안한것은원계약위반이아니다. |
| 21 | GLOBAL ERROR BUDGET | **SCHEMA_DONE_NUMERICAL_BUDGET_OPEN** — 8개error component와triangle-composition규칙및1e-5tailtarget사전선언은존재. 감사에서찾은stale bridge값은별도history와certificatehash를남겨source만동기화했다. | certified_total=null; 모든component.value=null; productionbudget미승인. R4Tbaseline은old5037.09였으나audit수정후source는504.54;기게시detachedbudget는수정하지않았다. |
| 22 | STATIC QUALIFICATION AUDIT | **AUDIT_COMPLETED_ABSOLUTE_BOUND_OPEN** — correlatedbias/plateau/preasymptotic/nonmonotone/Richardson반례와threeleveldiagnostic구현. | 기존adjacentagreement는internalconsistency뿐. rigorousoperatorerror estimator는미구현. |
| 23 | LITERATURE USAGE POLICY | **FOLLOWED_WITH_PINNED_SOURCE_RECORDS** — sourceDB/fulltextversion/page/equationprovenance를G03등에기록했다. | 이감사는모든PDF를재독하지않았으며원pin/사용기록을확인한범위다. |
| 24 | WOLFRAM / SYMBOLIC POLICY | **EXECUTED_WHERE_USED** — G01 exactFraction symbolic replay/CASinput-output및G03paritysymbolic기록이존재. | 별도 미해결 항목 없음; 적용조건은 JSON 참조. |
| 25 | NUMERICAL PRECISION POLICY | **FOLLOWED** — FP64production-equivalent경로와Decimal/Fraction감사경로를구분했다. | 100digitDecimal은directedbound가아니며HPCbitwisechecks는물리certificate아님. |
| 26 | CODE / REPO POLICY | **RECORDED_PUBLISHED** — datedadditivefolders,focusedred/green,nonforce같은branch게시기록존재. | 현재selectivesnapshot에는.git이없으므로새실행에는실제checkout/admission필요. |
| 27 | EXTERNAL / NATIVE EXECUTION POLICY | **PARTIAL_EXECUTOR_CONTRACTS** — G02/G03finished narrowexecutors는있으나G12/G06/G11은template수준이남는다. | 감사checkpoint의새physical실행은기록상0. 현재사용자의run지시는구현과현재exactplan으로구체화할수있다. 이전placeholder계약을최종실행설정으로오인하면안된다. |
| 28 | COST / INFORMATION-VALUE ORDER | **ORDER_GENERALLY_FOLLOWED** — 저비용theory/synthetic부터진행했고expensive후속science는미개방. | 더많은audit만으로생산단계가완성되지는않는다. 구현과최소physicaldiscriminator순으로전환필요. |
| 29 | CLAIM-GATE MACHINE-READABLE REGISTRY | **COMPLETED_FOR_CHECKPOINT** — registry13행과claimmatrix/DBv6 research36claims가존재. | section별미구현상태는13gaplabel만으로는보이지않아본matrix가보완한다. |
| 30 | BLOCKER CLASSES | **MOSTLY_RECORDED** — 승인/환경/수치/구현분류와firstfailure기록을보존. | G02resourceblocker해소후에도G04/11numerical, G13implementationblocker는별도로남음. |
| 31 | PERIODIC DURABLE CHECKPOINTS | **RECORDED_DURABLE_CHECKPOINTS** — R4Q/R/R4S/R4T Git및dualbackupreceipt존재;R1/R3의미구분. | 본감사는remote업로드재실행안함. R4Tdetachedreceipt를근거로게시성공기록확인. |
| 32 | STOP RULES FOR RESEARCH LOOPS | **GENERALLY_FOLLOWED** — 경계에서과학gate승격을멈추고추가derivation으로진전했다. | 무기한theoryrefinement대신현재실행가능G02/G03와미구현physicaladapter를우선할것. |
| 33 | REQUIRED PROGRESS REPORT AFTER EACH GAP | **PARTIAL_GRANULARITY** — lane별claimupdate/test/runtimeaccounting이존재하나모든절별완료표는없었다. | 본37절+10STEPmatrix로누락가시화. |
| 34 | REQUIRED END-OF-THREAD RETURN | **COMPLETED_CHECKPOINT_NOT_MASTER_GOAL** — closeout/DB/registry/receipts/gates/nextaction은R4Tdelivery에있다. | Research loop complete라는표현은전체productionprogram완료로읽으면안됨. |
| 35 | NON-NEGOTIABLE CLAIM CEILINGS | **PRESERVED** — capturefalse/productionHOLD/allboundOPEN/bgridNOGO유지. | 새production구현요청이물리gate증거를자동생성하지않는다. |
| 36 | FIRST EXECUTION SEQUENCE | **FIRST_SEQUENCE_PERFORMED_TO_DECLARED_LIMITS** — STEP1–10모두착수및요구된local산출물을남겼으나후속전체gate종결아님. | 아래개별STEP행이실행·계획·physical미실행을구분한다. |

## 최초 실행 STEP 1–10 대조

| STEP | 실제 수행 | 완료의 한계 |
|---|---|---|
| 1 | v3 authority inventory에서 v4/v5/v6로 연구테이블만 확장했다. | COMPLETED_FOR_CHECKPOINT; 로컬은 selective snapshot이며 .git이 없어 HEAD는 게시receipt 기준; 별도 현재remote 재확인이 필요하다. |
| 2 | registry13행과claimmatrix/DBv6 research36claims가존재. | COMPLETED_FOR_CHECKPOINT; section별미구현상태는13gaplabel만으로는보이지않아본matrix가보완한다. |
| 3 | G01의10가지 항등식·정리·가정·단위·constant-basis covariance를 유도·구현했다. | COMPLETED_CONDITIONAL_THEOREM; 실제 Sdot compatibility와 integrable physical tail은 정리의 미입증 적용조건이다. |
| 4 | eigh(W,S)와Cholesky congruence,100digit 2x2,condition sweep 및8saved matrices를 검사했다. | PARTIAL_CONDITIONING_DOMAIN; whole rate assembly cond(S)>=1e8 문제와 uniform forward error는 남아 있다. High-precision lane은 rounded synthetic2x2이며 directed interval이 아니다. |
| 5 | norm/P/projector/spectrum/rho covariance와raw K_TP 비불변 반례 및 별도metric coupling을 구현했다. | COMPLETED_WITH_DECLARED_DOMAIN;  |
| 6 | staticqualificationsemantics와8componenterrorbudget구조감사완료;absoluteoperatorerror와numericaltotal은미완성. | AUDIT_COMPLETED_ABSOLUTE_BOUND_OPEN; 기존adjacentagreement는internalconsistency뿐. rigorousoperatorerror estimator는미구현. |
| 7 | 기존자료로G02를닫을수없음판정+exactminimal66query실행계약/code작성까지완료;물리실행요구는별도. | COMPLETED_DECISION_AND_MINIMAL_CONTRACT_NOT_RUN; 실제64shift+±12centerD가 없어 독립 Sdot convergence/plateau를 확인하지 못했다. |
| 8 | acquired collision sources 기반 유도, M1–M4 signed fits/holdouts/branch-switch 반례와최소±48선정을 수행했다. | COMPLETED_ANALYTIC_STUDY_NOT_EMPIRICAL_CLOSURE; 새±48/offgrid관측이 없어 empirical model identified closure가 아니다. fixed-J 잔차floor 가능성도 남는다. |
| 9 | ±48두query/22attempt의최소discriminator와후속44/64결정규칙설계·테스트;실행은0. | COMPLETED_MINIMUM_DESIGN_NOT_RUN; 새±48/offgrid관측이 없어 empirical model identified closure가 아니다. fixed-J 잔차floor 가능성도 남는다. |
| 10 | RouteA/B 실제 유도·코드·syntheticLEVEL2, repaired reference metric와finite bridge 정리가 있다. | COMPLETED_BEGIN_AND_SUBSTANTIVE_WORK_NOT_CLOSURE; B0 complex continuous enclosure engine/input proof가 없다. _matrix는real-symmetric만 지원하고 proof metadata validator는theoremchecker가 아니다. 새reference bridge504.54는5e-6목표실패. |

STEP7은 “G02를 새 실행 없이 닫을 수 있는지 판정하고 아니면 최소 계약 작성”, STEP9는 “최소 discriminator 설계”, STEP10은 “G04 작업 시작”을 요구했다. 따라서 이 초기 sequence는 수행됐다고 볼 근거가 있다. 이것을 G02 physical closure, G03 empirical closure, G04 continuum-tail closure까지 끝났다고 해석하면 부정확하다. 원문 마지막 문장이 “with exact evidence … executable minimal contract for”에서 끊겨 있으므로 그 뒤의 미제공 내용을 임의로 보충하지 않았다.

## 다음 production 구현의 우선순위

| 순서 | 구현·실행 | 먼저 해야 하는 이유 |
|---|---|---|
| 1 / P0 | Freeze exact scientific model and observable for candidate production | Literal archived basis is nonconforming; repaired reference is distinct and not dynamically transferred. Strong-L2 residual route invalid. |
| 2 / P0 | Integrate physical qualified provider with strict Fortran/OpenMP/MPI | R4S synthetic queue/kernel is not wired to physical G02/G03/transport executors. |
| 3 / P0 | Run minimal independent Sdot and signed48 discriminators under current exact plan | Ready G02/G03 code can resolve concrete implementation/asymptotic questions; no broad grid needed. |
| 4 / P1 | Implement physical complex finite-interval weak residual/enclosure | Synthetic real-symmetric majorant and 504.54 bridge do not meet5e-6 target. |
| 5 / P1 | Implement same-IVP independent propagator and first nested window pipeline | CF4 prototype exists but physical provider/Sdot/budget/initialstates and run collector are missing. |
| 6 / P1 | Instantiate finite-metric state transfer and conservative total error ledger | All actual component values and certified_total remain null. |
| 7 / P2 | Higher-l backend and B1/B2/B3 qualification/completeness | Current optimized kernel supports only s+p; symbolic channel counts are not an executable completeness study. |
| 8 / P3 | All-bound then b-grid/cross-section production | These are explicitly downstream; finite selected P is not capture cross section. |

현재 사용자의 구현·실행 요청은 다음 작업을 진행할 근거다. 과거 placeholder의 NOT_AUTHORIZED 문자열만으로 현재 작업을 정지시킬 이유로 삼지 않는다. 다만 그 문자열을 삭제하는 것만으로 provider, 독립 Sdot, 상태 identity, 오류 예산이 생기는 것도 아니다. R4U 결과는 자체 코드·parity·실행 결과를 대조한 뒤 이 baseline의 해당 항목을 갱신해야 한다.

메타데이터 수정 증거는 [ERROR_BUDGET_SYNC_VALIDATION.json](</workspace/scratch/63ee2321a512/cloud_audit_20261001/contract_audit/ERROR_BUDGET_SYNC_VALIDATION.json>)에 있다. exact certificate의4개 입력 SHA를 확인했고, budget의 named-reference 블록 이외 부분이 동일함을 검증했다. 수정 전 snapshot은 [ERROR_BUDGET_CURRENT_B0_BEFORE_R4T_SYNC.json](</workspace/scratch/63ee2321a512/cloud_audit_20261001/contract_audit/ERROR_BUDGET_CURRENT_B0_BEFORE_R4T_SYNC.json>)이다. 이 수정은 numerical target 달성이나 gate 승격이 아니다.

## 별도 부록 — 더 이른 BASS_HE 문헌 복구 계약

[최초 HE 원계약](</workspace/scratch/63ee2321a512/cloud_audit_20261001/inputs/Pasted text(20260930-213213).txt>)은 solver 실행을 요구하지 않고 source acquisition과 dual backup을 요구한다. [v3 외부 receipt](</workspace/scratch/63ee2321a512/cloud_audit_20261001/drive/receipts/BASS_HE_BACKUP_RECEIPT_20261001_v3.json>)와 [검증 기록](</workspace/scratch/63ee2321a512/cloud_audit_20261001/drive/intake/he_v3/BASS_HE_PRIMARY_SOURCE_ARCHIVE_20261001_v3/VERIFICATION.json>)을 직접 읽었으며, fresh Drive raw download identity도 확인했다. 뒤에 생성된 HE A1/B1/C1B/C2/HPC 연구 패키지는 별도 단계이므로 이 acquisition 계약의 solver=0을 뒤집는 증거로 사용하지 않았다. WU088 계약도 제외했다.

선택 source39개는 publishedPDF24 + raw dataset6 + code source9이며 code archive3개다. v3에서 새로 들어온19편과 기존20source를 구별한다. search-lead metadata197개는 별도이며 “metadata-only0”은 selected39 범위에만 해당한다. 선택 문헌의 미확보 DOI는 없다. 아래는 이후 B1의 정정·전사까지 반영한 numerical material/metadata 상태다.

| 대상 | 남은 자료 |
|---|---|
| 10.1088/0953-4075/41/13/135201 | **P04 Appendix A1–A12가 실제 존재한다. B1에서 A3의 native5keV/u63cells를 확인했다.** v3의 table-header 미발견은 색인 false negative로 철회됐다. lab/CM·H1s 교차출처·mass/provenance 제한, 별도 author raw 미확보 및 나머지11표 미전사는 남는다. |
| 10.1088/1361-6587/ab2e7a | P10 논문은 확보. 별도 WP-CCC raw supplement 미확보. |
| 10.1016/j.adt.2019.05.002 | P09 tables1–114는 존재. B1이25–30의300 value cells와300convergence tokens를 전사했다. 나머지108표는 미전사, native velocity 보존, author raw export 별도 미확보. |
| ScienceDB 10.57760/sciencedb.j00113.00114 | 4CSV raw bytes 확보. energy-frame/cross-section-unit 일부 불확실성이 남으며 benchmark readiness를 승격하지 않음. |

[B1 erratum](</workspace/scratch/63ee2321a512/cloud_audit_20261001/drive/intake/he_postdb/BASS_HE_POST_DATABASE_A1_B1_20261001_v1/B1/SOURCE_RECOVERY_ERRATA.json>), [B1 결과](</workspace/scratch/63ee2321a512/cloud_audit_20261001/drive/intake/he_postdb/BASS_HE_POST_DATABASE_A1_B1_20261001_v1/B1/RESULT.json>), [13행 benchmark matrix](</workspace/scratch/63ee2321a512/cloud_audit_20261001/drive/intake/he_postdb/BASS_HE_POST_DATABASE_A1_B1_20261001_v1/B1/BENCHMARK_MATRIX.csv>) 및 ZIP의 verify_source_cells.py 본문을 직접 읽었다. B1은 총1,131 source value cells(ScienceDB743/P03 9/P04 63/P08 16/P09 300)를 보존하며 P09 convergence300은 별도다. verifier는 source bytes와 보존 전사기록을 대조하고, 새 독립 PDF 전사나 물리 재현을 주장하지 않는다. 제한된 표·격자에서 exact0.5keV/u authority는 확립되지 않았고, 이는 전체 문헌에 없다는 주장이 아니다. 물리 비교 gate는 SOURCE_AUTHORITY_UNRESOLVED다.

이 부록의 “전체” 범위는 최초 HE acquisition 계약0–16절/A–H와 이후 B1 source 정정이다. HE A1/C1B/C2/NCP64 등 모든 후속 연구 계약을 독립적으로 전부 감사했다는 뜻은 아니다. 해당 패키지들의 실행·closure는 별도 cloud-content 감사 결과와 합쳐야 한다.

v3 ZIP는 **26,874,721 bytes**, SHA256 `0f9dc51cc013aa0b91e7f3ff560bbca5afd1ee1551b67c8bb33278c445b1cd84`,254members/252manifest payloads,CRC/MANIFEST PASS다. Drive `10cFFUiYVvA-vKZbofgnmbdyB56NB3IgS`는 역사적 R3 raw restoration과 현재 raw SHA/CRC가 일치한다. Dropbox `id:BSpOijBcT10AAAAAADxPyA`는 receipt 정의의 R0 ACK+size이며 Dropbox raw restore는 수행하지 않았다. 양쪽을 R3라고 부르지 않는다.

| HE 절 | 판정 | 근거와 한계 |
|---|---|---|
| 0. 현재 입력 상태 | PRESERVED | 원입력·gate identity를 보존했다. HE 연구 상태와 CR 연구 상태는 별개다. |
| 1. 최우선 입력 검증 | VERIFIED | v1 SHA/CRC/51 manifest payload와 safe paths를 확인했고 v3에 원본을 보존했다. |
| 2. 문헌 원문 확보 정책 | COMPLETED_SELECTED_SCOPE | 대체 경로 및 user upload를 통해 선택 논문 24편 모두 published full text를 확보했다. |
| 3. publisher 원문이 막혔을 때의 fallback 규칙 | COMPLETED_SELECTED_SCOPE | published/preprint/accepted/metadata를 구별한다. 최종 선택집합은 published24, preprint0, accepted0이다. |
| 4. 동일성 검증 | IDENTITY_AUDITED | DOI·title·author·page/render identity 및 P07/P14 특수 확인 기록이 있다. |
| 5. 우선 확보 대상 문헌 | PAPERS_COMPLETE_NUMERICAL_MATERIAL_LIMITED | 우선 10편을 포함한24편 원문과 ScienceDB4CSV는 확보. 이후 B1이 P04 table-header false negative를 정정하고 native5keV/u63cells 및 P09 tables25–30을 전사했다. 별도 author raw와 physical comparability는 한계가 남는다. |
| 6. 데이터 확보 정책 | RAW_BYTES_PRESERVED_METADATA_GAPS_EXPLICIT | raw6files 보존. ScienceDB 단위/energy-frame 일부 미확정, 5keV 보간·shell sum·digitization 없음. 수치 benchmark 준비 완료로 승격 불가. |
| 7. 코드 확보 정책 | PINNED_SELECTED_SNAPSHOTS_ONLY | code source9, archive3. BASS_HE는 pinned7module subset, full checkout/dependency closure가 아니다. treeSHA 미반환과 license 제한이 명시되어 있다. |
| 8. 파일 구조 | ARCHIVE_LAYOUT_PRESENT | catalog JSON/CSV/SQLite/XLSX 및 paper/data/code/provenance 구조가 archive에 있다. selective intake에서 없는 파일을 archive 누락으로 오인하지 않았다. |
| 9. source status taxonomy | TAXONOMY_APPLIED | 39 selected source와197 search metadata leads를 구별한다. leads를 원문으로 집계하지 않는다. |
| 10. 검증 | VERIFIED | SHA/CRC/manifest/safe paths/duplicate-member checks PASS. 동일 payload alias8은 문헌 추가8편이 아니다. |
| 11. 클라우드 이중백업 | DUAL_ACK_DRIVE_RAW_VERIFIED | 현재 v3 외부 receipt가 양 provider ACK를 정확한 ZIP identity에 연결. Drive raw R3, Dropbox ACK+size R0이며 Dropbox raw restore는 하지 않았다. |
| 12. mutation 정책 | FOLLOWED_IN_ACQUISITION_SCOPE | v3 acquisition에서 scientific code execution/production/Git mutation0, private PDF 백업. 이후 별도 연구 패키지와 범위를 구별한다. |
| 13. 실패 정책 | BLOCKERS_EXPLICIT_WITH_LATER_ERRATUM | 선택 논문 access-blocker0. v3 numeric material4개 항목 중 P04 table 미발견 문구는 이후 B1에서 철회·정정됐다. immutable v3의 오래된 gap을 현재 truth로 쓰면 안 된다. |
| 14. 완료 조건 | COMPLETE_WITH_EXPLICIT_BLOCKERS | A–H의 해당 증거를 확인했다. 원문 확보와 numerical-material 완비는 동일하지 않다. |
| 15. RETURN | RETURN_EVIDENCED | counts/catalog/ZIP identity/provider IDs/tier/restore/gaps/not-run/handoff가 archive와 detached receipt에 있다. |
| 16. 절대 실행 금지 | FOLLOWED_IN_ACQUISITION_SCOPE | v3 acquisition은 solver/Eq55/보간/새 digitization/production mutation을 실행하지 않았다. |

| 완료조건 | 판정 | 확인 내용 |
|---|---|---|
| A | VERIFIED_SELECTED_AND_SEARCH_ROWS | 39selected primary rows plus197 preserved search-lead rows; no claim that search leads are acquired fulltext |
| B | VERIFIED_SELECTED_SOURCE_BYTES | 39 recovered:24 publishedPDF+6rawdataset+9code source;3code archives |
| C | EXPLICIT_WITH_ERRATUM | Selected paper access blockers0;v3 documented4numeric-material/metadata gaps;B1 subsequently corrected P04 and supplied selected P09 transcriptions |
| D | VERIFIED | Recovered payload SHA256 in manifest/catalog |
| E | PASS | ZIP CRC, manifest and safe path checks; current Drive intake SHA+CRC independently matches |
| F | ACK_RECEIPT_VERIFIED | Drive and Dropbox completed ACK in exact-v3 detached receipt, current Dropbox listing agrees ID/size |
| G | DRIVE_RAW_VERIFIED | Drive historical R3 plus fresh independent raw SHA/CRC intake; Dropbox R0 ACK+size only |
| H | ZERO_IN_V3_ACQUISITION_SCOPE | science_solver_runs=0/new_physics_calculations=0; separate later studies are not attributed to this acquisition action |

## 감사 산출물과 범위

- [REQUIREMENTS_MATRIX.json](</workspace/scratch/63ee2321a512/cloud_audit_20261001/contract_audit/REQUIREMENTS_MATRIX.json>): 모든 원계약 행, 단계별 lane, exact path/SHA256, HE 부록, 우선순위.
- [build_audit.py](</workspace/scratch/63ee2321a512/cloud_audit_20261001/contract_audit/build_audit.py>) 및 [finalize_audit.py](</workspace/scratch/63ee2321a512/cloud_audit_20261001/contract_audit/finalize_audit.py>): 읽기 전용 inventory와 보고서 생성.
- [FIRST_AUDIT_BUILDER_FAILURE.json](</workspace/scratch/63ee2321a512/cloud_audit_20261001/contract_audit/FIRST_AUDIT_BUILDER_FAILURE.json>): 최초 section20 제목 파싱 오류와 수정 기록. 과학 테스트 실패가 아니다.
- 근거는 계약·소스 함수·테스트 정의·저장된 결과·DB·게시 receipt다. 이 감사에서 새 physical run, 이전 테스트 재실행, cloud write는 하지 않았다. 소스 변경은 명시적으로 요청된 ERROR_BUDGET_CURRENT_B0.json의 메타데이터 동기화 한 파일뿐이다.
- 보고서의 미구현 판정은 검사한 R4T selective snapshot에 대한 것이다. 외부 모든 branch에 코드가 전혀 없다는 전역 주장은 하지 않는다.

