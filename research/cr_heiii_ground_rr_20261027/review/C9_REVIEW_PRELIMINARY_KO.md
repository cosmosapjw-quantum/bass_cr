# C9 독립 변경 코드·위험 검토 — 수치 결과 대기

## 판정과 범위

**변경 코드 및 실제 C6 자료에서 material finding 0건. 최종 C9는 수치·그림 근거 대기(PENDING).**

`CR_HEIII_GROUND_RR_ON_HEI_SAVED_CHAIN_V1`의 frozen THEORY, CONTRACT, ACCEPTANCE에 대해 producer 7개 Python 파일과 별도 Decimal 검증기를 한 번의 제한된 읽기 검토로 대조했다. 검토자는 과학 계산·테스트·생산 코드 수정·원격 변경을 수행하지 않았다. 현재 로컬 기반 HEAD는 `b11b2e9255f2b10fb5582376412e045bd1e9151c`이다. 새 단위와 복구한 과거 HeI payload가 로컬 untracked 상태임을 확인했다. 최신 자료에는 C7 디렉터리가 나타났지만, 이 보고서의 실제 실행 근거 범위는 C6까지다.

## 직접 확인한 핵심

| 대상 | 대조한 근거와 결과 |
|---|---|
| 공급자·표적 | HeII `(Z,N)=(2,1)`, threshold 54.42 eV, photon 상한 50000 eV, 통계중량 비 d=1, HeIII 밀도 0.01 cm^-3를 고정한다. 전자 bath 0.14 cm^-3와 구분하며, E>0·유효범위·finite density를 검사한다. |
| 연산자·열 구성 | physical18/conditional5/stable4/new-w1의 28 RHS를 정확히 구성하고, 기존 off-diagonal·저장 열을 재사용한다. 8 case의 총 224 RHS 계약과 각 열 자체의 backward scale·양의 pivot을 보존한다. |
| 작은 RR 효과 | stable4는 `-lambda * saved_HeI_column`의 직접 선형계 해이다. 저장 결과의 뺄셈은 진단 값이다. 독립 Decimal 검증기는 저장 K0와 새 lambda를 각각 정확한 binary64 값으로 옮긴 뒤 고정밀에서 더한다. |
| 소비·단위·동일성 | integrated density/energy의 SI 변환을 한 번 적용하며 rate/exposure/RHS는 null이다. event canonical ID, source/frame binding, duplicate 방지를 확인했다. |
| native25·광자 | 양의 명시적 nb에만 He4III12→He4II11, fast electron count −a, fast energy/nb 감소를 매핑한다. w_ext/logT는 0이고 retained photon은 별도 port다. 실제 export의 nb는 null이다. |
| 비용·실행 보호 | missing/invalid receipt는 UNKNOWN으로 admission을 막고 failed 비용도 합산한다. preparation·coordinator·worker를 새 30 CPU-s에 포함한다. affinity, 한 thread 환경, 512 MiB AS, stage CPU/wall 제한 및 owned child 종료를 확인했다. clean-cache RAM 값은 reserve를 둔 추정치로만 취급한다. |

이 범위에서 수정이 필요한 객체·증거·결과를 갖춘 결함은 발견되지 않았다. 추가 과학 테스트를 제안하지 않는다. 이미 frozen인 primary, 독립 Decimal 비교, 저장 자료 그림 확인이 남은 구체적 위험을 다룬다.

## 실제 C6 근거

`runs/cr_heiii_rr_controls_20261027_v1`의 RESULT, DISPATCH_RECEIPT, CONTROL_RESULTS, runtime readback, 양의 nb native25 event 및 PRE_EXECUTION을 직접 읽었다. **36/36 PASS**, 과거 controls 재실행 0, runtime readback PASS를 확인했다. worker CPU는 0.427652 s, coordinator CPU는 0.052623798 s이며 preparation 0.221624387 s를 포함한 새 단위 누적값은 **0.701900185 / 30 CPU-s**다. 함수 내부 측정치와 dispatcher의 총 worker 비용을 혼동하지 않았다.

PRE_EXECUTION의 producer 소스 7개는 현재 파일 및 EXECUTED_SOURCE 복사본과 모두 byte/hash 일치한다. 실제 worker affinity는 CPU0, RLIMIT_AS soft/hard는 536870912 B, NumPy·SciPy OpenBLAS는 각각 1 thread였다. 양의 nb control은 deltaY11=+0.5, deltaY12=−0.5, deltaζ=−0.5와 별도 photon port를 실제 기록했고, 열입자수 변화는 0이다.

전체 소스·계약·C6 파일 해시와 객체별 판단은 `C9_CODE_REVIEW.json`에 보존했다.

## 독립성의 정확한 한계

검토자는 producer 작성자 및 Decimal 검증기 작성자와 다르다. 다만 이 검토자는 앞서 R5 native25 event-map 구성과 C4 환경 조사에 참여했다. 따라서 이 두 기여를 완전히 새로운 독립 유도로 재검증했다고 주장하지 않는다. 별도 R6 검토와 독립 Decimal 실행이 최종 판정에 필요하다. 재귀 검토 및 producer 수정은 수행하지 않았다.

## 남은 판정 입력과 유지 상태

8 case·224 RHS 및 source 24행의 실제 primary 수치, frozen convergence 검사, 독립 56 RHS·10 coefficient sample·6 source row 결과와 실제 그림 확인이 남아 있다. 이 결과를 같은 C9 검토의 후속 근거로 읽은 뒤 최종 admission을 결정해야 한다. 게시·source ZIP·이중 백업 영수증은 coordinator가 처리한다.

**중앙 DAG 27/88, edge 17, N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED를 유지한다.** 이 검토는 physical heating, thermal assimilation, 전역 물리 완료를 승격하지 않는다. 과거 UNKNOWN_NO_ACK와 예산은 보존되며 새 단위로 이전한 과거 계산 허용량은 0이다.

적용 skill은 `physmath-research-loop 1.3.0`의 C9와 POLICY_INTEGRATION이며, 최신 AGENTS와 frozen 계약 범위에 맞추어 적용했다.
