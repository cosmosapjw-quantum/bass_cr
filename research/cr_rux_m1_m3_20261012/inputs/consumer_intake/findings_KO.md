# bass_cr M1/M3 — 현재 REI 소비자 수신 조사

작성 시각: 2026-10-12 07:51 UTC. 이 조사는 읽기 전용이며 bass_cr·rei_bianchi 코드, 브랜치, 원격 상태를 변경하지 않았다. 새로운 과학 계산·test 실행·solver interval은 각각 0회다.

## 결론

**M1은 `SCOPED_SNAPSHOT_IDENTIFIED_FULL_HISTORY_BINDING_OPEN`으로 갱신하는 것이 타당하다.** 실제 source-pinned CR receiver와 두 개의 고정 gas-composition packet이 이미 있으므로 “소비자 자체가 없다”는 상태는 지나치게 강하다. 다만 이 receiver는 단일 collisionless proton snapshot에 terminal deposition operator를 적용하며, M0의 scalar source history·cascade kernel과 자동으로 동일한 계산이 아니다.

**M3의 국소 CR-off 구현은 추가 patch가 필요 없다.** 실제 source=0/provider-calls=0 구조, 저장된 실행 receipt와 PASS stdout이 존재한다. 과거 실행본의 public CR derivative 함수와 CR-off 음성 대조군은 현재 PR110 소스와 각각 byte-exact로 같다. 현재 선택할 production whole-history의 zero-call receipt는 별도 범위이며 이번 조사 자료로 닫지 않는다.

## 읽은 현재 identity와 권위 범위

| 자료 | 고정 identity | 역할 |
| --- | --- | --- |
| bass_cr task base | `767273fec673ac0877dc4833da4bef147ae04c40` | 부모가 지정한 현재 task source; injection source를 git show로만 읽음 |
| REI PR110 | `17f8d0daa72e0f76a49cde01b110f650a6688c42` | 현재 integrated 연구 브랜치의 receiver 소스·tests·C12 handoff |
| REI CR PHYS03 | `8d9526a75e85202764e845c7d5d79d7f903e7c55` | xi=.1 source pin과 보존된 PHYS01/03 실행 근거 |
| REI 원 PHYS01 receiver | `69541be1a88f32468494e33158a96d5341e4572c` | 실제 PHYS01 실행 source SHA를 회수하여 현재 OFF 함수와 제한 비교 |
| REI default branch | `ae3402713c4b6530ab2b27f008f5f5d5c6a999ed` | 마지막 commit 날짜가 2026-08-11; 최신 연구 상태로 쓰지 않음 |

PR110은 조회 시 draft/open/unmerged였다. 최신 PR 검색 결과에는 다른 독립 lane도 있지만 해당 lane 전체를 재감사하지 않았다. 이 조사는 처음 선택한 핵심 source 10개와 부모가 요청한 OFF 비교용 과거 파일 2개로 제한했다. 각 원문·Git blob SHA·local SHA256·source URL은 `SOURCE_IDENTITY.json`에, 직접 connector 반환은 `tool_responses/`에 보존했다. GitHub에서 가져온 UTF-8 원문의 Git blob SHA를 직접 계산하여 전부 provider metadata와 일치함을 확인했다.

원 repo에 AGENTS.md가 있다는 가정은 하지 않았다. 해당 경로는 PR110에서 404였고 같은 commit의 root listing에도 없었다. bass_cr AGENTS.md 및 부모가 지정한 M0 HANDOFF/NEXT_DAG, CONSUMER_REQUEST와 Astra v4.0.0 core/routing/state template은 실제로 읽었다.

## M1 — 실제 연결된 입력과 아직 연결되지 않은 입력

### 현재 국소 receiver

현재 [CR receiver 소스](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/17f8d0daa72e0f76a49cde01b110f650a6688c42/rust/rei_microphysics/src/axisym_cr_deposition.rs)는 `CrDepositionPacket`을 받아 primary/secondary H·He ionization event, thermal/internal/escape power를 실제 `AxisymLocalSources`에 공급한다. 외부 proton을 gas nuclei에 더하지 않는다. `full_injection_power`는 audit 정보이며 gas의 `external_power`에는 modelled ionization-loss component만 사용한다.

[현재 compiled pin](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/17f8d0daa72e0f76a49cde01b110f650a6688c42/rust/rei_microphysics/src/axisym_cr_deposition_pin.rs)은 다음 snapshot을 실제 값으로 고정한다.

| 항목 | 확인한 값/범위 |
| --- | --- |
| proper-time snapshot | \(t=10^{10}\ \mathrm{s}\) |
| H number density | \(140\ \mathrm{m}^{-3}\) |
| He number density | \(11.542553191489361\ \mathrm{m}^{-3}\) |
| gas temperature | \(100\ \mathrm{K}\) |
| helium mass fraction | \(Y_{\rm He}=0.248\) |
| gas composition | \(x_{\rm HII}=x_{\rm HeII}=\xi\), \(x_{\rm HeIII}=0\), 정확한 \(ξ=0.01,0.1\) 두 knot |
| geometry | \(H=3.3\times10^{-17}\ \mathrm{s}^{-1}\), \(s=3.3\times10^{-18}\ \mathrm{s}^{-1}\), \(a_{\rm rel}=e^{Ht}, b=st\) |
| source snapshot label | \(z_{\rm source}=8\) |
| active proton collision window | \(1\text{–}4\ \mathrm{MeV}\) |
| deposition closure | FS10 local terminal deposition; excitation/continuum prompt escape, photon 재주입 없음 |

gas/time/geometry와 packet 값은 실제 public ON에서 검사한다. 두 \(ξ\) 사이의 보간은 제공하지 않으며 (ξ=0.05)는 typed missing-authority 오류다. 이 입력을 가진 **국소 component의 존재**는 확인됐지만, evolving bath와 source에 대한 자유로운 full-history consumer의 존재를 뜻하지 않는다.

### q와 spectrum의 실제 provenance

[REI에 보존된 SOURCE_MANIFEST](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8d9526a75e85202764e845c7d5d79d7f903e7c55/docs/research_sync/CR-PHYS01-20261010/evidence/SOURCE_MANIFEST.json)의 injection.py digest는 `c5eda0e60302339af1bbdd0603ae1cd8a8921d9e6489c22d954e0bc92968c27d`다. bass_cr task base의 [실제 injection.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/767273fec673ac0877dc4833da4bef147ae04c40/research/cr_phys01_20261010/src/injection.py)를 회수하여 같은 SHA임을 확인했다.

이 파일에 구현된 \(q_p(K)\)는 angle-integrated proton number injection per proper volume/time/kinetic-energy이다. spectrum은
\[
q_p(K)=A\,\beta(K)^{-1}
\left[\frac{p(K)}{p(K_0)}\right]^{-\alpha},
\qquad K_0=1\ \mathrm{GeV}.
\]
정상화 적분은 **10 keV–1 PeV 전체 injection 범위**를 사용하며 1–4 MeV 충돌창에 재정상화하지 않는다. birth angular measure는 \(d\mu/2\)다. fixed window에서는 선택한 MD14 source snapshot과 \(H,s\)를 고정하고 CR 초기 population을 0으로 두어 birth age를 \(0\ldots t\)에서 적분한다.

소스 코드의 default는 \(α=2.2\), supernova energy \(10^{44}\ \mathrm{J}\), CR efficiency (0.1), escape fraction (1), MD14 \(k_{\rm CC}=0.0068\ M_\odot^{-1}\), normalization order 128이다. **이번 bounded intake에서 실제 provider constructor의 모든 keyword argument까지 별도 회수하지는 않았으므로 이 수치들은 “byte-bound source의 observed defaults”로 기록했다.** consumer manifest에 없는 실제 선택값을 default만으로 확정하지 않는다.

이 proton \(q_p(K)\)와 M0의 scalar source amplitude/history가 같다는 결속은 아직 없다. 또한 같은 \(t=10^{10}\ \mathrm{s}\)라는 사실만으로 selected_record/birth_defined kernel compatibility를 승격하지 않는다.

### identity 해석

SOURCE_MANIFEST 원 파일 SHA256은 `a0088feddcd1ed8932e19b50935f5726a08af831bdd65e28cbbd757ed3bc0565`다. JSON을 sorted keys, compact separators, UTF-8, 마지막 newline 없음으로 canonicalize한 SHA256은 `79835c5eaa891f37f663c1852d6035ee446a25778763164cfea2d20531cdd901`이고 현재 xi=.01 packet pin과 일치한다. 이 차이는 실제 byte identity와 canonical semantic identity의 차이로 보존했다.

### 남겨야 할 미결 항목

실제 채택할 CR-on source history·prehistory·evolving bath/time map, M0 cache의 input/species/normalization/representation 결속, 최종 관측량의 절대·상대 tolerance와 분모, CR heating contribution fraction은 이 자료에서 결속되지 않았다. numerical table heat-correction bound와 유한 refinement 차이는 downstream physical error budget이 아니다. \(\xi\)는 gas ionization knot이고 CR efficiency는 supernova energy fraction이며, 둘 다 관측량 오차 예산의 CR heating contribution fraction으로 대입할 수 없다.

## M3 — 구현·과거 실행·현재 production receipt의 구분

현재 `cr_deposition_derivative(false,...)`는 `AxisymLocalSources`의 species13개와 electron, photon number/power, thermal/internal/escape/external power를 모두 0으로 둔다. provider closure는 ON 분기 내부에서만 평가한다. 따라서 OFF는 packet/provider를 조회하지 않으며 audit는 None이다. 다만 geometry의 dilution·thermal work는 정상적으로 남으므로 **total derivative=0**를 요구해서는 안 된다.

[PHYS01 NATIVE_EXECUTION](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8d9526a75e85202764e845c7d5d79d7f903e7c55/docs/research_sync/CR-PHYS01-20261010/evidence/rei_native/NATIVE_EXECUTION.json)은 실제 native example command, exit0, binary SHA `376b20bb80ebb95b66140c04e90073ff4a572af3a102f777f6d574bdfeb1a8bc`, source SHA들과 `off_no_call=true`를 기록한다. solver interval은 0이다. [최종 test stdout](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8d9526a75e85202764e845c7d5d79d7f903e7c55/docs/research_sync/CR-PHYS01-20261010/evidence/rei_native/final_new_tests.stdout.log)에 provider closure를 panic으로 둔 OFF 음성 대조군을 포함해 7 passed/0 failed가 남아 있다.

후속 [PHYS03 VALIDATION](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8d9526a75e85202764e845c7d5d79d7f903e7c55/docs/research_sync/CR-PHYS03-20261010/VALIDATION.json)은 xi=.1을 포함한 8 passed/0 failed와 native probe의 `off_provider_calls=0`, `solver_intervals=0`를 기록한다. 이는 저장된 후속 validation summary이며 이번 turn에서 실행한 결과가 아니다.

### 실행 source와 현재 source의 제한 비교

원 PHYS01 commit에서 회수한 module SHA256은 `5f672ec60a1bcb110cc91dd4d1a21217913c002a65d9282f484d2880d7e0bdd3`로 NATIVE_EXECUTION의 executed source digest와 정확히 같다. 현재 PR110 module 전체 SHA는 `c5461915caf2595a4053f33c026ff1fcaec7b4ab7914188ee5e56535a6f562ba`이므로 module 전체 byte identity를 주장하지 않았다.

두 원문에서 **complete public `cr_deposition_derivative` 함수**를 추출한 결과는 byte-exact 동일했다. 같은 방식으로 `off_calls_provider_zero_times_and_preserves_geometry_only` test 함수도 byte-exact 동일했다. `OFF_BRANCH_COMPARISON.json`과 빈 실질 diff를 보존했다. 이 범위에서는 기존 실행 결과를 재사용하는 것이 타당하며 새로운 wrapper/patch나 오래된 suite 재실행은 필요하지 않다.

### 현재 production 범위

[PR110 C12 handoff](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/17f8d0daa72e0f76a49cde01b110f650a6688c42/research/accel02_20261011/q1b/c12/HANDOFF.json)는 현재 full-history 진행과 identity를 보존하지만 CR provider call-counter/zero-source receipt를 제공하지 않는다. PR 설명의 CR/RCT `OFF_NONCOMPLETION` 문구도 그러한 실행 receipt 자체는 아니다. 이번에 선택한 자료만으로 현재 production whole-history의 CR-off receipt를 닫지 않는다. 이것은 repo 전체를 검색해 receipt가 어디에도 없다고 판정한 결과가 아니다.

## 부모 계획에 필요한 최소 변경

1. M1을 “실제 snapshot 확인, full-history binding OPEN”으로 갱신하고 실제 packet·source·commit pointer를 CONSUMER_REQUEST에 추가한다.
2. M3를 `LOCAL_CR_OFF_CONTRACT: COMPLETE_REUSED`와 `SELECTED_PRODUCTION_OFF_RECEIPT: CONDITIONAL`로 분리한다.
3. **국소 코드 patch는 `NONE_JUSTIFIED`**로 둔다. 실제 선택한 production 시나리오가 다음에 실행될 때 그 call-site/source/counter receipt를 기록하는 일은 receiver 소유자의 범위로 남긴다.
4. 위 입력 존재를 M0 kernel compatibility, causal deposition history, full CR closure 또는 heavy job 활성화의 자동 근거로 사용하지 않는다.

Machine-readable 전달은 `CONSUMER_INTAKE.json`이다. 이 문서의 근거 상태는 현재 source inspection, 실제 과거 실행 receipt의 수신, byte comparison, 그리고 명시한 unresolved 영역의 조합이며 새 scientific promotion 판정이 아니다.

