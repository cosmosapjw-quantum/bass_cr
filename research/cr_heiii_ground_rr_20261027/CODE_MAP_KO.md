# C2 — 식·저장 입력·코드 대응

이 표는 C2에서 실제 읽은 구현 초안의 함수명을 사용한다. `intake/C2_DRAFT_FUNCTION_IDENTITIES.json`은 AST만 읽은 당시 초안 hash이며 실행 source identity가 아니다. C5의 최종 소스 및 각 실행 snapshot은 별도로 결속한다.

| 이론·단위 | 저장 입력 | 새 구현 함수 | 반환·검사 |
|---|---|---|---|
| Native HeII PI, photon eV → cm² | 원 provider/table 두 고정 byte hash | engine.provider | Verner96.from_table('HeII'); 원 scalar point provider만 호출 |
| Milne σ_RR(E), target density cm^-3, v cm/s, λ s^-1 | ground I54.42, d1, nHeIII.01 | engine.coefficients | PI/RR σ, v, λ_HeII; positive E와 native support 검사 |
| 정확한 stored K0와 K1=K0+D | PR106 HeI K_diag/K_lower/K_upper | engine.consume / positive_pivots | 세 RR와 CE/entry의 shared operator, strict Z/positive pivots, addition loss 기록 |
| G1 b, proper seconds | immutable old first6/H1pair/HeIpair/bath6 + 새 λ/λE | engine.solve / consume | physical18 및 각 RHS scaled residual |
| G1 p_j, conditional time | 새 physical indices [0,1,6,8,10] | engine.consume | conditional5, 분모0에서는 null |
| −G1 D hhat0 | 저장 HeI CE/time/H1/HeI columns | engine.consume | stable4, 이름에 stored-column response; direct subtraction으로 대체하지 않음 |
| w=G0 λ | exact old K0, 새 hazard | engine.consume | w1 및 single-added-channel lower/upper bound |
| μᵀp와 μᵀr | PR104 projection/mask/p[0], 3×384 atom CSV | engine.source_average |24 source rows, integrated cm^-3/eV cm^-3; 재투영0 |
| count·energy SI 변환 | source moments와 source qualification | export_adapter.integrated_event |m^-3/J m^-3, rate/exposure null, 별도 retained photon |
| He4III12→He4II11, Δζ=−a | native basis와 explicit nb 또는 null | export_adapter.validate_event / IntegratedBook |핵·전하·에너지, native25, same-frame/case/z, canonical ID 중복 거부 |
| byte provenance, 오래된 계산 재실행 방지 |21 immutable files와 theorem/review pins | prepare_inputs / engine.verify |create-only 복사·manifest, 실제 source/input byte hash |
| finite resource contract |새30 CPU-s와 이전 실제 attempt receipts | dispatch.prior_attempts / snapshot / acquire_lease |missing/invalid prior cost 차단, affinity/thread/RAM 및 create-only run 기록 |

Source cases의 nominal N과 실제 active array length를 구별한다. 예를 들어 chi1.5_R80_N2048 active size는2479다. RHS는 기존 `rhs_physical16[:,:10]`, 새 두 열, 기존 `[:,10:16]` 순서여서 새 bath slice는12:18이다. H1/HeI reward를 이전 결과 값으로 최종 합산하지 않고 새 shared operator로 푼 값을 사용한다.

코딩 단계의 경계는 physical/spectral provider와 consumer 사이의 단위·source domain 보존이다. 현재 adapter는 integrated return이므로 기존 rate-only Event.extent_m3_s에 값을 주입하지 않는다. Actual nb_m3=null이며 positive-nb control만 per-baryon 사상을 검증한다. Native w_ext는 external photon transfer 의미를 유지하고, 내부 RR photon은 별도 retained port를 사용한다.

Primary CLI는 `--unit --output --run-id`, dispatcher는 `--unit --run-id --mode {controls,primary,review,plot}`, 독립 checker는 `--unit-dir --primary-dir --controls-dir --out-dir`다. C5에서 실제 최종 CLI와 이 mapping의 일치를 확인한 뒤 C6부터 실행한다. 이 단계의 AST/source 읽기는 scientific run이 아니다.
