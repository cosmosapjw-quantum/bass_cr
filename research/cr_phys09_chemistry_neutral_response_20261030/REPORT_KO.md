# BASS-CR PHYS09 | 실제 원본 광자 기반 중성종 응답 및 화학계 연결 연구

## 과제·결론

기존 PHYS08의 흡수 지연시간 계산을 반복하지 않고, 원본 H/He recombination photon의 first-photoionization observable이 **서로 다른 중성종 밀도의 임의 시간 구간 변화에 어떻게 반응하는지**를 계산했다. 원본 100 K H I/He I, 6400 source photon atoms, 네 출생시간 구간, 9 관측시각, 8 neutral perturbation window를 그대로 사용한다.

새 출력: 1728 source-origin×absorber×neutral-density-owner×8 time-window×9 observation-epoch×3 birth-witness causal response rows, 27 epoch chemistry Jacobian rows, 368 original-energy-bin final response rows. 15/15 normal Python tests, 15/15 python -O tests, `compileall`, independent same-author MP70 256 scalar checks PASS, five numerical output byte-replay PASS.

## 대표 수치 (T=1e10 proper s)

단위 `dN_first_absorbed / d ln n_neutral` = `m^-3`:

| Quantity | Earliest birth | Latest birth |
|---|---:|---:|
| `dN_HI/dln(n_HI)` | `1.622081870638181e-26` | `6.2219240623187526e-27` |
| `dN_HI/dln(n_HeI)` | `-1.9049811921263098e-30` | `-5.800499586006325e-31` |
| `dN_HeI/dln(n_HI)` | `-1.9049811921263098e-30` | `-5.800499586006325e-31` |
| `dN_HeI/dln(n_HeI)` | `1.9588001379369733e-28` | `7.368797402280583e-29` |
| `dN_total/dln(n_HI)` | `1.621891372518968e-26` | `6.221344012360152e-27` |
| `dN_total/dln(n_HeI)` | `1.9397503260157102e-28` | `7.31079240642052e-29` |

최종 source-born H/He의 같은 장부에서 정한 `R_source_a - N_first_absorption,a`를 **전체 기간 동안 일정한 중성밀도 섭동이라고 가정**할 때의 1차 보정은 earliest `2.760147434251847e-53 m^-3`, latest `1.1058536357663236e-53 m^-3`이다. 이 숫자는 관측된 바 없음, 실제 시간 진화가 아님. 중성 수의 시간분포는 원본에 주어지지 않았으므로 입증되지 않은 화학 feedback claim으로 확대하지 않는다.

## 과학적으로 중요한 정리

- `n_HI` 증가 -> H I first absorption 증가, He I 경쟁 absorption 감소.
- `n_HeI` 증가 -> He I first absorption 증가, H I 경쟁 absorption 감소.
- 두 target을 합한 총 흡수 응답은 양이며, `sum_a G_ab=k_b*(overlap time)*exp[-k(T-s)]`의 인과식과 일치.
- 전체 8개 perturbation window 응답의 합은 source 전체 기간에 균일한 로그밀도 변화의 직접 미분과 일치.
- H-origin photon은 원본 He I ionization threshold 미만이므로 H→HeI의 원래 rate와 해당 target susceptibility가 0.

이 행렬은 **source-qualified chemistry Jacobian component**이지만, 완성된 BASS21/REI17 chemistry Jacobian이 아니다. 다른 저장소 광자원과 혼합 금지.

## 검사 결과와 수정 이력

- 첫 generator는 전체 인과자료 행 수를 864라고 잘못 예상했다. 실제 grain `9×3×2×2×2×8=1728`로 수정했다. 물리적 수치 변경 없음.
- 최초 MP70 스크립트의 함수 괄호 오류를 수정해 컴파일 및 alternate integral evaluation 진행. 출처와 수용 tolerance 변화 없음.
- 현재 normal 15/15, optimized 15/15, MP70 256/256 PASS. Max relative MP discrepancy 약 `9.93e-14` (representation-level and quadrature method difference; not independent author).
- Original PHYS08 source archive `6,531,870 bytes SHA256=16d0b7c9e2540777ea0e360511e502303e6ea887ae0ecd658282d14d79923ae4`, original 45/45 payload SHA, ZIP CRC PASS. Original nested PHYS07 SOURCE `ff48de4e951e63da4c6a5624bed3975ec22ad43513b67b8c355fc6237fabde98` retained byte-identically.

## Scientific status and DAG

Canonical CENTRAL `28/88 (+0)`, EXTENSION `0/3 (+0)`, 새 scoped auxiliary source data `1/1 REVIEW_HOLD`; R/C workflow `18/20` with **R06 different author NOT_RUN; C09 different author NOT_RUN**. Native subagent invocation NOT_RUN (no exposed native spawn tool). This is valid source-conditional derivation and computational output, but not production/observational admission. Physical exclusive He (e,3e) event, physical K, donor/partner energy ownership, stopping, time-varying 100 K medium/geometry and cosmological transfer unavailable.

## Source crosswalk

PR133 is Git-partial (11/43) but its complete binary SOURCE ZIP was verified and used. External repo PRs are surveyed as candidate science evidence, not numerical inputs. No BASS21↔REI17 source rebind, native25, L4, production or main merge. Next physical step: obtain source-owner event-level He double-ionization data and physical K or genuine common time-dependent neutral/birth/directional photon histories. Do not manufacture rates or new cosmological claims from this static response operator.
