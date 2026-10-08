# R3M14 production 반환

최종 판정: **NO_GO**. 준비 쌍 판정은 **NO_GO**, 실제 동일 격자 충돌 비교는 **PASS_PAIR_ONLY**이다. 허용오차를 바꾸지 않았다.

## 준비 쌍

production 격자 280×240×480, dx=.25 a0, 총 imaginary time 30 t_a. d=0.00044669380764377305, d_star=0.00043930987793803502, d/d_star=1.01680802112, trace distance=0.00044669379650237183. 조건부 구간 [0.0076797863650457775, 0.007837167464429794], 최대 상대 변화 상한 1.016850535%. 이는 floating 평가이며 roundoff enclosure가 아니다.

| 준비 | E (Eh) | Hamiltonian residual (Eh) | no-CAP 1-step ray defect | CAP 1-step norm |
| --- | ---: | ---: | ---: | ---: |
| 0.025 × 1200 | -0.487338777413932 | 0.0210782026615061 | 0.00404689251137921 | 0.9999999999999999 |
| 0.0125 × 2400 | -0.487346907506266 | 0.00545139008063829 | 0.00353663610878953 | 0.9999999999999999 |

Hamiltonian residual과 target-only ray defect는 다른 진단이다. 이 값을 capture 확률 오차로 등치하지 않는다. real dt_actual=0.049967825809688213 t_a.

## 실제 collision 및 binding

v2 wrapper가 inherited relaxed_initial()의 원 객체를 그대로 반환했으며, 저장 preparation과 typed array digest·norm·환경 일치를 전파 전에 확인했다. binding=PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED. state 대입·cast·정규화는 하지 않았다. 총 897 step을 최대 128-step씩 8 chunk, 7 sealed restart로 완료했다. 각 chunk의 stdout/stderr, state metadata, seal 및 wrapper receipt를 보존했다.

P_span(n≤3)=0.0077575635652400738. 지정 R3M12 reference/분모=0.00775827737938, 상대 변화=0.009200678%. P_region=0.025905823322482605, final norm=0.97873858639038569, Gram condition=1.0002122829449316, eigenvalue range=[0.9997877809601232, 1.0000000188545721]. 전체 nested-span·gap·eps·cross-term 진단은 DECISION.json의 gram_audit 및 collision0125/result.json에 있다.

과거 기준의 raw config는 .025 준비 설정과 일치하고 저장 state/seal 해시는 검증했다. 과거 source digest와 현재 값의 차이는 02546302의 checkpoint seal 저장 수선으로 분류했다. propagation·preparation·analysis 메서드 AST는 동일하며 옛 seal을 변경하거나 재시작하지 않았다. 과거 initial.npy 자체는 저장·binding되어 있지 않아 조건부 정리의 reference_anchor_verified는 false로 유지한다. 실제 reference 결과의 full precision은 0.007758277379377454; 판정 분모는 사용자 지정값을 그대로 사용했다.

## 환경과 소스

Ubuntu 24.04.5 LTS, kernel 7.0.0-31-generic; Python 3.12.3, NumPy 2.5.3, SciPy 1.18.1, CuPy 14.2.0, CUDA runtime 12090, driver API 13020, NVIDIA driver 595.84, RTX 3090. GPU UUID와 라이브러리 경로 및 전체 버전은 receipts/environment.json에 있다.

source commit 0c068e902e59ad001c4a2ae1be4168d1d29907b8는 d04124e8a1b83f29fd26baa13f11cd68a8f33c15의 후손이다. cr_repro source digest=581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b. canonical helper SHA=6e5dab152ec89a3145268d349b4cb0dd5dcec6b8566f0ac5a746e258317a3535; witness SHA=f4137f1e2c7562e532e812481673cd9bad4877a69e93b84bbfae9b769fa22e92. 준비·설정·state·seal의 SHA와 enriched config hash는 DECISION.json에 모두 기록했다.

필수 pytest **52 passed**, wrapper --help PASS. 이 결과는 해당 네 테스트 파일 범위이며 full-suite/독립 리뷰 PASS를 주장하지 않는다. MLflow는 외부 subprocess orchestration에만 적용했고 scientific interpreter와 고정 소스는 유지했다. 최초 .025 준비는 tracing 도입 전 실행됐고 canonical receipt/stdout/stderr가 있다. 이후 trace 검증은 receipts/MLFLOW_VERIFICATION.json 참조.

## 판정 한계와 반환

준비 쌍 d>d_star이면 실제 collision 선별 결과이 1% 이내라도 전체 준비 제어 PASS를 선언하지 않는다. inherited spatial NO_GO(.3125→.25 변화 2.289941%), b-grid NO_GO를 유지한다. finite n≤3 sampled span은 all-bound/continuum 확률이 아니다. dx=.20, b-grid, physical rate는 실행하지 않았다. 이번 결과의 다음 행동: OWNER_DECISION_REQUIRED_ON_PREPARATION_PAIR_NO_GO. R3M15는 두 선별 기준의 scoped PASS가 있을 때만 다음 node가 된다.

큰 배열은 immutable production archive에 보존하고 Git에는 작은 결과·receipt·archive pointer만 넣는다. 두 provider 완료는 detached DELIVERY_RECEIPT.json의 실제 ID·크기·readback 검증으로만 판정한다. R3M12 Drive 1/19 문제는 별도로 미완료 상태를 유지한다.

이번 NO_GO는 준비 쌍의 사전 충분조건 미충족이라는 계약 판정이다. 실제 capture 확률이 1% 넘게 달라졌다는 뜻이 아니며, 측정된 동일 격자 변화는 0.00920068%다.

Gap 진단: region_minus_span=0.018148259757242532, eps_selected_outside=2.9483471110077604e-08, eps_complement_inside=0.018150410384596694, cross_term=-2.1211438830516287e-06, gap_identity_residual=0, gap_bound=0.04188247957447333, slabwise_orthogonality_bound=0.00051660043387870345. eps_complement_inside는 continuum 확률이 아니다.
