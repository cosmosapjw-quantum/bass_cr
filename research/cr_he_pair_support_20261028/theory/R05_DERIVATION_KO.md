# R5 구성적 유도 완료

전체 증명은 `THEOREM.md`에 있다. 핵심 전이는 다음과 같다.

1. 비음수 edge 질량 `x`는 각 bin의 electron-leg capacity를 사용한다. 임의 feasible dual `y`에 대해 `1·x <= n·y`를 직접 합산하여 상한 증명서의 의미를 먼저 고정했다.
2. Left/right 복사본 사이에 양방향 counterpart arc를 놓는다. Feasible x를 두 방향으로 복사하면 값2C의 flow가 되고, 반대로 flow를 `(f_ij+f_ji)/2`로 대칭화하면 원래 degree constraints를 만족한다. 따라서 최대유량의 절반이 정확한 optimum이다.
3. `N>0`에서 middle capacity를2N으로 두면 최소 cut은 N 이하이므로 middle arc를 자를 수 없다. Cut indicator 두 개의 평균이 half-integral dual이며 objective가 flow/2와 정확히 같다. `N=0`, empty graph와 isolated bins는 별도로 정의했다.
4. Optimum assignment를 scale하면 모든 `0<=C<=rho`를 달성한다. Fixed internal double mass d를 지정할 때 남은 diagonal legs의 조건 `2(d-C)<=N-2C`는 정확히 `2d<=N`이다. Diagonal event 한 개가 같은 atom의 두 leg를 소비하도록 구성했다.
5. Endpoint bin의 남은 atom queue에서 edge 질량만큼 차례로 떼어 coupling한다. 각 atom marginal을 정확히 보존하며 full Cartesian rectangle 밖의 pairing을 만들지 않는다. 조밀한 pair matrix 없이 sparse event records를 얻는다.
6. 완전 graph는 기존 bound `min(N/2,N-max n_i)`로 환원된다. Mass perturbation에 대한L1 bound와 비음수 동차성을 증명하여 proper-window factor를 한 번만 적용하는 근거를 마련했다.

R6 독립 유도에서 지적한 consumer inventory gate의 적용 범위를 정리 본문 Eq.(8)에 명시했다. 수학적 matching feasibility와 atomwise construction은 임의 finite capacity에 대해 성립하지만, inherited same-state consumer의 실제 수용에는 source/state/window/nb 및 neutral inventory 조건도 필요하다. 이 교정은 정리의 optimum이나 기존 source 값을 바꾸지 않는다.

새 proof의 coefficient와 density 단위, ordered/unordered measure factor2, diagonal two-leg convention, signed species/charge/chemical correction을 명시했다. 일반적인 matching 결과의 신규성, actual graph/kernel 또는 physical closure를 주장하지 않는다. R5에서 미해결 필수 수학 의무는 없으며, 독립 R6 판정과 실제 C-stage 구현 검증은 별도다.
