# 다음 물리 gate 초안: 동일 finite input의 selected-span 관측량

상태: DRAFT_NOT_EXECUTION_AUTHORIZATION. 실제 capture 계산을 이번 R3에서 실행하지 않았다.

## 이미 사용할 수 있는 근거
F0의 동일 finite-input M4 qualification과 R2의 새 engine admission, R3의 byte-preserving finalized-cache import 및 다섯 저장 sentinel 진단을 재활용한다. F0/F1/R2의 scientific run을 다시 실행하지 않는다. R3 cache에는 전체 M4 trajectory의 모든 노드가 있다는 보장이 없으므로, R2의297개 operator만으로 완전한 새 전파를 구성하지 않는다.

## 정의와 추가 입력
기저 B의 Gram 행렬 S=B†B가 양의 정부호이고, 채택할 projectile bound span의 selector J가 정확히 주어지면

    Q = S J (J† S J)^-1 J† S,
    P_selected = c† Q c,
    Q S^-1 Q = Q,  0 <= Q <= S.

원 basis의 positive pseudostates를 bound 채널로 잘못 포함하지 않는다. J의 column ordering 및 원 target1s 초기상태는 pinned channel registry로 확정해야 한다. 기록된 final coefficient vector와 그 S, time, frame/ETF convention이 바이트로 연결돼야 한다. 보고서 scalar norm만으로 final c를 합성하지 않는다.

## 승인 전 acceptance 초안
- Exact basis/channel/initial-state/time/trajectory 및 archived c의 provenance를 확인한다.
- 물리 projector 공식과 Gram 양성/conditioning을 검사한다. NaN/Inf 또는 clipping/regularization으로 실패를 지우지 않는다.
- 해당 수치는 finite-span, finite-time quantity로만 명명한다. 다른 중심의 subspaces가 겹칠 때 임의 probabilities 합을1로 만들지 않는다.
- Temporal discretization error, basis omission, asymptotic extraction, state-classification error를 분리한다.
- M4 qualification은 동일 source/input 구간에만 적용된다. 새 basis/b/timewindow는 새 검증 대상이다.

CF4 또는 모든 worker profile sweep는 이 postprocessing 정의의 수학적 필수조건이 아니다. 그러나 radial/angular convergence, asymptotic tail, all-bound completeness, impact-parameter integration은 최종 cross section의 별도 미해결 의무다.

R3의 whitened residual은 한 epsilon과 다섯 점으로 계산했다. 이것으로 continuous supremum, integral eta, 최종 fidelity를 인증하지 않는다. capture=false, production=HOLD, all_bound=OPEN, b_grid=NO_GO를 유지한다.
