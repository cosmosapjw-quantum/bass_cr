# R07 중앙 HEAD 변경의 한정 자격 확인

## 판정

**QUALIFIED_CENTRAL_BASELINE_NO_CR_PHYSICS_CHANGE. 중앙 완료 수는 28/88, 이번 CR 단위 효과는 0이다.** 기존 qualified `7de02b3e05705ead4eeb313c8487a21d4e6876a6`에서 새 `b99a9468abd53de77ddae36d93180e60072885bc`로 바뀐 실제 DAG와 owner 기록을 비교했다. 원 88개 계약, 88개 ID의 순서, 17개 integration edge, 모든 top metadata와 모든 CR node가 보존됐다. 새 CR source/state/nb/clock/branch/retained-photon 입력을 제공하는 변경은 없다.

실제 immutable 원문은 **2026-10-27 16:31:01–16:31:55 UTC**에 읽었다. 새 commit의 tree는 **`cc889f25bcace4655b4a7d633087b0862a94b3ca`**, 직접 parent는 `ff724389fc4b7b33d3492aa8ca3b76e1f108a080`이다. commit 시각은 2026-10-27T16:25:22Z다. 현재 CR 자체 HEAD는 거절된 R07 preflight에서 기대값과 일치했으며, 중단 원인은 중앙 기준의 변경이었다.

분석 원문·정확한 byte pin·검사 근거는 [R07_CENTRAL_QUALIFICATION.json](R07_CENTRAL_QUALIFICATION.json)에 있다. `parent_ops/NEW_BASELINE_R07_CANDIDATE.json`은 기존 preflight가 읽을 수 있는 **별도 후보**다. 심사자가 활성 `central_count_baseline.json`을 덮지 않았다. root가 후보를 채택한 뒤 fresh R07 preflight를 다시 통과해야 한다.

## 실제 바뀐 네 node

| ID | 변경과 채택 경계 |
|---|---|
| HE-CLOSURE, index21 | KINEMATIC08의 conditional physical-input reference observation으로 교체됐다. current status는 `CONDITIONAL_OWNERSHIP_IMPLEMENTATION_VERIFIED_PHYSICAL_INPUT_PENDING` 그대로다. |
| B3h-native-finite-absorption, index40 | 이미 완료된 native QSS 결과에 endpoint-channel refinement를 결속했다. current status는 `COMPLETE_SCOPED_ENDPOINT_CHANNEL_FINITE_TRANSACTION`으로 바뀌었다. 기존 QSS observation은 `prior_status_observation_native_qss_channel_completion_20261027`에 정확히 보존됐다. 다음 행동은 현재 단위 종료이며 `AUTO_NEXT_NODE=false`다. |
| HE-EXP-NUCLEAR, index64 | KINEMATIC08의 stationary bare-alpha γ+α→d+d conditional kinematic reference가 관찰 기록에 추가됐다. WU의 실제 nuclear channel/branch 공급을 대신하지 않으며 `SOURCE_INPUT_PENDING`은 그대로다. |
| HE-EXP-CLOSURE, index65 | shared-event 및 rest/binding energy ownership의 한정 reference observation으로 바뀌었다. 실제 common-temperature/velocity closure와 thermal admission은 제공하지 않는다. current status는 그대로다. |

나머지 **84개 node 전체는 semantic identity가 같다**. 위 네 node에서도 원 `contract` 객체는 모두 같다. 세 HE observation과 B3h의 새 observation/current status/stop action/이전 observation 보존 필드만 되돌리면 이전 DAG 전체와 정확히 같은 semantic object가 된다. JSON 실수 token은 Decimal로 읽어 비교했으며, status 문자열을 세어 완료 수를 만들지 않았다.

## 완료 수와 실제 원문 identity

[BASS endpoint return](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/b99a9468abd53de77ddae36d93180e60072885bc/research/orchestration_expansion_20261025/returns/BASS_B3H_ENDPOINT_CHANNEL_INTERPOLATION_20261027.json)의 top-level `original_DAG`는 `completed=28,total=88,delta=0`이다. B3h observation의 같은 count 필드와 `completion_count_effect=0`이 일치한다. HE status도 `declared_complete=28,total_nodes=88,HE_delta=0`을 명시한다. 네 변경 observation 전체가 실제 owner 파일, DAG, CURRENT_STATUS 사이에서 일치하며, CURRENT_STATUS의 88개 current status도 DAG와 일치한다.

| 원문 | bytes | SHA256 | 실제 Git blob |
|---|---:|---|---|
| DAG.json | 1,638,181 | `ab873fd7f5b7d55c3b6fe650323447a23a4fec820fbe8dc29110908501636ccb` | `844a5c5f5bafab6cb0ef03dfb4e3d3f0bfd9046b` |
| BASS endpoint return | 21,947 | `892058b7fe7f025d29724845e3669115722d8d9cd2786fe9b460871862e54f38` | `de92e0330562b862064ef36f237da8f44c60213f` |
| HE KINEMATIC08 status | 66,514 | `196b93c7663e7df1be9cb762d2b34e3c1b19932a28dd90a63431d6e3c65d5f91` | `0741e3afb19d03e71a7ed592543056c592924331` |
| status/CURRENT_STATUS.json | 95,899 | `286de2587c13ee1e9afeed03ad46418aeac30b69ecb3d9be856ff2ae5c817ffc` | `237060bb7784b4c7f127fada79bd75f29f1e7c7a` |

각 file의 실제 full body에서 계산한 Git blob과 size를 같은 immutable revision의 GitHub directory metadata에 대조했다. 네 파일 모두 일치했다. 실제 AGENTS 9,351 bytes의 SHA256 `ab29a05cac922bd393dc04f7f280a0d4e1d7289ae6ea24291f48fd7cf7b2e8eb`도 이전 qualified 정책 및 R07 preflight와 같다.

## 새 owner 범위·예산·게시의 의미

**BASS.** source S1은 `e35673b96c94dfad576c76c5b0b12f4873dd13e4`, tree는 `5de97e7ad1c702cf547ee1a291ac7ca20d070ef6`이다. 실제 native knots5126/5127의 proper-time endpoint-tagged channel mixture, 선택 native Lyα clock/incoming trace, 유한 atomic/gas/radiation stocks 및 한 번의 B3i consumption에 한정된다. owner return은 새 trajectory1, B3i RHS1, checks50/50 및 pre-driver import failure1을 기록한다. 이것들을 CR의 새 실행·검사 수에 합산하지 않는다.

별도 allowance는 CPU120 s/wall300 s이고 child CPU22.634567, wrapper CPU0.09323300000000002다. preparation/metadata 비용은 `UNMEASURED_UNKNOWN_NOT_ZERO`, 과거 잔여는 null, 이전 allocation 재개는 false다. 더 실행할 권한은 없으며 예산을 CR로 옮기지 않는다. S1 source ZIP과 dual-provider ACK는 owner 원문에 있지만 provider bytes의 full GET/hash는 false다. 이 immutable return의 final source commit/ZIP은 아직 forthcoming/null이다. 과거 root-admission의 pre-ACK 문구와 뒤에 추가된 actual S1 ACK를 구분한다. physical radii, global radius 및 L4 완성은 제공하지 않는다.

**HE.** local admission commit `f68150d78a60883c5697527111242a1fd7416438`과 실제 remote same-tree admission `8c7153f72ac1d1a6310ed250526003733022062f`를 구분한다. remote delivery는 `e56573a5961623c49428f6f8d566fb13edf8a6b9`다. 실제 선언 A,M,e, stationary bare-alpha γ+α→d+d, full-azimuth polar window와 degree≤8의 nonnegative Bernstein density에 대한 conditional reference다. empirical DCS normalization, actual photon flux/history, deposition/thermalization 및 global species binding은 열려 있다. atomic He 부모 사건의 joint branch를 공급하는 결과가 아니다.

validation은 한 번의 scientific suite에서 14 tests/0 failures이며 이전 environment failure1과 bounded repair를 보존한다. validation CPU는 observed outer를 포함해 0.4848311419999999/10 s이고 repair reserve는 0이다. 별도 saved plot은 CPU7.040661/6 s로 **FAIL_CPU_CAP_EXCEEDED**이며 outer CPU0.03521463700000001도 기록돼 있다. child exit0이나 읽을 수 있는 그림을 resource PASS로 바꾸지 않는다. workflow PARTIAL, local DAG8 complete+1partial+3physical-open/12, physical provider/rate/activation false, production NOT_APPROVED를 유지한다. PHOTON05·HE101의 과거 실패와 각각의 예산도 보존돼 있다.

HE 파일의 `central_published=false`와 `publication_performed=false`는 명시된 **PRE_CAS_CANDIDATE_SNAPSHOT** 값이다. 현재 b99a9468 commit에서 그 metadata가 실제 게시됐다는 관찰과 분리한다. 해당 false 원문을 다시 쓰거나, 보지 않은 post-CAS 외부 receipt가 존재한다고 주장하지 않는다.

## CR 적용과 보존한 한계

새 BASS의 V0=1m³·native knot·temperature convention이나 HE의 nuclear isotope/state를 현재 PHYS02 100K·H1/He4·nb=8750/47·finite proper history에 가져오지 않는다. He s,p,d 및 partner의 actual-null, RR capture/retained-photon port, frozen source support·허용치·예산은 모두 유지한다. N4/N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED, L4false와 global completion/error/budget remaining/currency null도 바뀌지 않았다. PR23632/88 및 별도 working33은 더하지 않았다.

첫 metadata 비교 명령은 닫는 괄호 오류로 입력 처리 전에 중단되어 한 번 고쳤다. CURRENT_STATUS를 잘못된 상위 경로에서 요청한 실제 HTTP404도 acquisitionV1에 남겼으며, 기존 acquisition manifest에 있던 정확한 `status/CURRENT_STATUS.json` 경로를 사용한 V2 읽기가 성공했다. 이 읽기 실패를 과학 실패로 분류하거나 지우지 않는다.

이번 작업은 metadata 읽기·동일성 비교만 수행했다. 과학 실행·CAS·기존 science replay·provider backup GET·Git/remote mutation은 모두 **0**이다. metadata CPU는 측정하지 않았으므로 null이며 0으로 채우지 않는다. 현재 **CR_PHYS02_PARENT_EVENT_NATIVE25_V1 한 단위**만 계속할 수 있고, 후속 과학 단위의 자동 시작은 허용하지 않는다.
