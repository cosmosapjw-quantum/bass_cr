# 실제 REI CR 침적 receiver — 국소 component 검증

현재 구현·수치 상태는 **SCOPED_IMPLEMENTATION_PASS_PENDING_INDEPENDENT_REVIEW**다. `research/cr-first-build-gate-20261010`의 `8722f3ab587399700d96d300b617f0f37f1d831a` 위에 새 `axisym_cr_deposition.rs`, exact source pin, tests, native example을 추가하고 lib.rs에서 export했다. 기존 `SourceBoundConditional`·FT03·128EPS coupling guard는 수정하지 않았다. Commit/push는 root가 담당한다.

실제 provider packet SHA256은 `1bb0d4e1c4c71a409ca170e8741fabd17fabe02195b86fe24a06875712d0e373`, source manifest는 `79835c5eaa891f37f663c1852d6035ee446a25778763164cfea2d20531cdd901`다. Packet hash는 `packet_sha256` 필드를 제외한 canonical JSON에 대해 확인했고 manifest hash 및 그 안의 5개 source/table bytes도 일치했다. Rust는 이 packet의 모든 숫자를 bitwise, identity/closure 문자열을 exact equality로 검사한다. 이후 proper time·nH·nHe·xi·100 K thermal state와 고정 SI kB 및 source-manifest의 H/s/a/b geometry를 대조한다. 같은 모양의 임의 packet이나 다른 gas state를 물리 입력으로 인정하지 않는다.

Primary `[HI,HeI]`와 secondary `[HI,HeI,HeII]`의 event rates 및 source-specific threshold를 별도로 받는다. Ionization power를 두 dot product의 합과 대조하므로 primary H/He와 FS10에서 선언한 threshold 차이가 감춰지지 않는다. H→H+, He0→He+, He+→He++로 사건 수를 배분하고 electron source는 세 사건 수의 합이다. 외부 CR proton을 ambient gas nuclei에 더하지 않는다.

Heat와 ionization internal power, prompt excitation/continuum escape를 실제 `AxisymLocalSources`로 전달한다. Photon number·energy 재주입은0이며 이는 실제 photon spectrum을 복원했다는 뜻이 아니다. `external_power`는 modelled ionization-loss component이고 full proton injection과 별개다. Raw heat는 threshold-anchor interpolation correction을 포함한 PREPROJECTION 값이다. 그 이전 raw table heat와 threshold correction은 `PROVIDER_AUDIT.json`에 각각 보존된다. 선택한 bounded numerical energy-closure projection의 raw defect·heat correction·bound를 결과에 반환하며, 이를 물리 uncertainty나 단순 print-rounding으로 해석하지 않는다.

| 실제 국소 결과 | 값 |
|---|---:|
| electron source | 5.979293938079537×10⁻²⁵ m⁻³s⁻¹ |
| heat power | 1.2093044641845817×10⁻⁴² J m⁻³s⁻¹ |
| ionization stored-energy power | 1.3963750685843803×10⁻⁴² J m⁻³s⁻¹ |
| excitation escape power | 6.613224299070425×10⁻⁴³ J m⁻³s⁻¹ |
| modelled ionization loss | 3.2670019626760045×10⁻⁴² J m⁻³s⁻¹ |
| full injection power | 5.315371751092545×10⁻³⁴ J m⁻³s⁻¹ |
| raw chosen-interpolation residual | +1.649729386090965×10⁻⁴⁶ J m⁻³s⁻¹ |
| heat projection correction | −1.649729386090965×10⁻⁴⁶ J m⁻³s⁻¹ |
| numerical correction bound | 2.4489321098323726×10⁻⁴⁶ J m⁻³s⁻¹ |
| source-only temperature derivative | +3.811186545594215×10⁻²² K s⁻¹ |
| H=3.3×10⁻¹⁷ s⁻¹ background 포함 temperature derivative | −6.599999618881346×10⁻¹⁵ K s⁻¹ |

최종 native example은 source manifest의 prescribed H=3.3×10⁻¹⁷/s=3.3×10⁻¹⁸ s⁻¹ 및 a_rel=exp(Ht), b=st에 맞춘 ON/OFF local 호출만 실제 coupling 함수로 평가했다. Source-only temperature derivative는 반환된 ledger에서 2Q_heat/(3k_B n_particles)−T S_e/n_particles로 분리한 산술 결과다. Public ON을 H=s=0 배경에 호출하지 않는다. ON−OFF 차이는 cancellation scale을 별도로 기록한 진단값이다. 배경 온도 감소는 −2HT와 variable-particle source를 포함한다. 이 결과는 단일 collisionless CR snapshot에 terminal cascade operator를 평가한 것이다. source turn-on 뒤 10¹⁰ s 내에 해당 침적이 인과적으로 완료됐다는 계산이 아니며 cascade delay·full history는 미승인이다. YHe=.248과 z8 gas에 z10 FS10 terminal table을 적용한 것은 명시한 근사 scenario이고 원 MC abundance의 exact matching이 아니다.

초기 검증은 신규6개와 기존 coupling5/source2/contract6을 합친19개 Rust tests PASS였다. 독립 리뷰가 source packet에 고정된 geometry를 public ON이 검사하지 않는 구체적 누락을 찾았다. 이를 수정하고 H/s/a/b mismatch 및 H=s=0 음성 대조군을 추가한 **최종 신규7개 tests PASS**를 기록했다. 변경되지 않은 기존13개 regression은 초기 PASS 증거를 유지하며 반복 실행하지 않았다. Source identity 변조, ledger를 그대로 둔 full-injection 숫자 변조, gas temperature·HeIII·time mismatch, provider threshold 변경, raw residual 삭제/변경, 부족한 correction bound, NaN 및 spectrum 없는 transport closure를 거절했다. OFF는 provider closure를 전혀 호출하지 않았다. 기존 conservation guard를 느슨하게 하지 않고 corrected ledger를 통과했다.

Native example의 실제 JSON과 binary/source hashes는 `evidence/rei_native/NATIVE_OUTPUT.json`, `NATIVE_EXECUTION.json`에 있다. 독립 Decimal70 산술은 동일 provider packet의 사건/열 원장을 입력으로 사용했으며 electron source·source-only temperature·background temperature의 native 상대차가 각각 약1.06×10⁻¹⁶,1.16×10⁻¹⁶,2.42×10⁻¹⁷이었다. 이는 receiver 산술 검사이지 provider physics를 독립 재실행한 검증은 아니다. 실제 solver interval은0이다. 최종 재검사는 FINAL_NEW_TESTS.json, 최종 native 출력·실행은 NATIVE_OUTPUT.json/NATIVE_EXECUTION.json이며 초기19 PASS와 초기 native 결과는 before_geometry_binding_fix/에 원본 그대로 보존했다.

첫 환경 실패는 task toolchain에 rustfmt가 없었던 것이다. 단일 `rustup component add rustfmt`로 설치한 뒤 새 Rust 파일만 포맷했고 이를 `REI_RECEIVER_INITIAL_BUILD.json`에 기록했다. 처음 수행한 substantive19 tests 및 native probe에는 실행 실패가 없었지만 독립 리뷰에서 발견한 geometry binding 오류로 그 버전의 public admission을 보류했다. 수정 후 신규7 tests와 matched-geometry native probe가 통과했다. 전체 repository CI, cold atomic history, 완전한 CR stopping·transport·EoR·observables는 이번 PASS에 포함하지 않는다.
