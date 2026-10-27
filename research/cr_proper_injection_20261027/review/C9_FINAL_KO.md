# C9 최종 독립 검토

**판정: bounded core numerical/contract PASS_SCOPED. 과학적 blocking finding은 0개다.** 모든 runtime attempt가 통과했다는 판정은 아니다. `independent_v1`의 실행 전 메모리 거절과 `plot_v1`의 예약 초과를 실패 상태로 보존한다. 전체 판정과 정확한 identity는 [C9_FINAL.json](C9_FINAL.json), 실제 파일·snapshot·debit 대조는 [C9_READBACK_AUDIT.json](C9_READBACK_AUDIT.json)에 있다.

검토자는 production ports, controls, consumer, runner, plot을 작성하지 않았다. 초기 이론 memo와 독립 Decimal 기준 코드는 작성했다. 이 저자 관계를 공개하며, 자기 코드에 대한 독립 심사라고 주장하지 않는다. 별도 R6 이론 검토와 root의 실행·최종 채택 책임을 유지한다.

## 확인한 수치와 물리 범위

실행 snapshot 24개가 네 manifest의 byte/hash와 일치한다. Synthetic controls는 **103/103**, 실제 source 결과는 **3 tags × 6 windows = 18행**, 독립 검사는 **153/153 PASS**다. 추가 과학 실행이나 source/transport 재계산은 하지 않았다.

| 검사 | 통과 | 최대 상대 차이 | 고정 허용치 |
|---|---:|---:|---:|
| 원 저장 source moments | 6/6 | 1.16895e-15 | 2e-12 |
| 독립 Decimal 비교 | 90/90 | 2.38324e-16 | 2e-13 |
| 반구간 합 | 9/9 | 1.17262e-16 | 2e-14 |
| low+high=total | 30/30 | 1.78926e-16 | 2e-14 |
| eV→J 변환 | 18/18 | 1.31321e-16 | 2e-14 |

실제 입력은 PHYS02의 저장된 `Qe=tA` 전자 source, proper time `[0,1e10] s`, 100 K bath와 native `[0.1,900] eV` 범위다. 원 energy-coordinate `B_i`를 number로 옮기는 `B_i/E_i`, 공통 `U*/T²`, cutoff count/energy의 한 번 반영, low-cross 진단값 제외를 확인했다. 실제 atomic measure를 보존했고 moment에서 spectrum을 재구성하지 않았다. 구간 밖 continuation이나 shutoff도 추정하지 않았다.

100 K source와 PR107의 10000 K RR bath는 서로 다른 상태다. Explicit same-state `nb`도 없다. 따라서 실제 18행 모두 **nb/native25/RR return/retained-photon port는 null**이다. Photon·baryon interface는 이번 단위의 typed contract와 synthetic controls 범위다. 물리 가열, 전역 오차, 전역 완성도 또는 L4를 승격하지 않는다.

## 실패와 비용

| Attempt | 보존 상태 | 누적 최종 charge, CPU-s |
|---|---|---:|
| controls_v1 | completed | 0.219374 |
| actual_v1 | completed | 6.526079 |
| independent_v1 | worker 시작 전 메모리 admission 실패 | 0.066297 |
| independent_v2 | 첫 실제 독립 계산, completed | 0.355319 |
| plot_v1 | 출력 생성, reservation 실패 | 3.071350 |

Immutable debit 7개와 receipt 사본을 **5개 unique attempt**로 대조했다. 같은 attempt의 amendment는 최대 누적 비용 한 번으로 집계된다. 총 실측 worker+coordinator는 **10.190599 CPU-s**, 예약 tail은 **0.047820 CPU-s**, 총 charge는 **10.238419 / 20 CPU-s**다. 이전 단위나 다른 프로젝트의 잔여 예산을 가져오지 않았고 다음 단위에 자동 이월하지 않는다.

`independent_v1`은 수치 실행 전에 거절됐다. Raw child CPU까지 포함한 실제 debit이 기록·집계됐으므로, C9S03의 누락된 preworker 비용 경로가 실제로 복구됐음을 확인했다. 초기 reference의 coordinate 오류와 C3 검사 추가는 첫 reference 실행 전에 수정됐으며 이전 draft/hash를 보존했다.

Plot worker는 exit 0으로 PNG/SVG를 만들었고 두 파일의 hash와 manifest를 확인했다. 그러나 aggregate child CPU **2.764225 > 2**, coordinator+tail **0.307125 > 0.3**이므로 runner 실패를 유지한다. 그림은 저장 결과의 진단 표시로만 사용한다. 기존 PNG를 확인했으며 다시 렌더링하지 않았다. 이 사례에서 per-process `RLIMIT_CPU`가 전체 descendant CPU의 선제적 hard cap을 증명했다고 주장할 수 없다.

## 게시·인계 경계

C9 preflight에서 local/remote CR HEAD는 `4a9f07d86a97306326e6879d8b72aa5ab59dd123`으로 일치했다. WU·REC·HE·중앙의 최신 관찰과 정책 상태를 읽었고, REC AGENTS의 HTTP404 한계도 보존했다. C8의 expected-SHA/non-force 게시, 182-member ZIP 및 Dropbox/Drive R2 receipt를 확인했다. 이 R2를 raw R3로 표시하지 않는다. C10 최종 source ZIP·이중 R3·중앙 owner-return은 root의 별도 delivery gate다.

원 중앙 집계는 **27/88**, 17 edges, 이번 효과 0이다. N4/N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED를 유지한다. 미병합 PR236의 32/88와 WU의 11/26을 중앙 수에 더하지 않는다. 과거 HeIII 실패·stale lease·비용, UNKNOWN_NO_ACK, 개인 대화 전체 검색 unavailable 및 Drive partial inventory 한계를 그대로 남긴다.
