# R4P0A: B0 tail 준비 검토와 기저 공변 확률 변화율

## 결론

`R4P0_PREPARATION_ACCEPTED__B0_OPERATOR_ONLY_NEXT`.

입력 준비 패키지는 현재 목적에 맞게 완료되어 있다. 이를 다시 작은 문구 수정 루프로 돌리지 않는다. 다음 과학 실행 후보는 **B0의 signed operator 8점**이며, B1–B3 higher-l backend 작업과 분리한다. 이번 산출물은 그 준비 검토, 저장 endpoint의 새로운 수학적 진단, 검증된 query-ID/진단 어댑터다. Native launcher를 완성·실행했다고 주장하지 않는다.

완료된 A3/N1536 one-shot은 소비·종결 상태다. 재사용하거나 N3072를 자동 실행하지 않는다. 기존 시간 게이트는 같은 B0, 같은 finite window [-12,+12] a0에만 적용된다.

## 입력 및 이번 실제 검증

Repo `cosmosapjw-quantum/bass_cr`, commit `f7b5eef95895f299327562859ce0b278ffa8679c`, tree `a48f84aa757da786304171c51458002707f72c6a`를 GitHub에서 확인했다.

Google Drive의 `R4P0_PREP_f7b5eef_20260930.zip`을 이번에 받아 확인했다.

- bytes: 75053
- SHA256: `60ed70b65c8fd37fee8a6d7d83602ef20a0de4d745e68655502d9a45f5af5528`
- 원본 ZIP CRC 및 33개 manifest 데이터 파일 검증
- 원본 제공 verifier의 새 디렉터리 추출: **40 passed**, py_compile 및 prepare CLI exit0
- 별도 외부 PYTHONPATH 없음, native operator 호출0, nonce 소비false

원래 Drive+Dropbox 양쪽 restore 성공은 사용자 실행 보고다. 이번 독립 입력 검증은 Drive 사본 하나와 패키지 replay에 한정하며 Dropbox 전체를 다시 내려받았다고 주장하지 않는다.

기존 finite-span 값의 마지막 자리와 1 ULP 차이는 원 receipt 그대로 보존한다. 이번 연구를 이유로 기대값에 맞춰 수치나 threshold를 수정하지 않는다.

## 바로잡는 이전 추론

R4O에서는 coordinate block `||K_TP||` 또는 `||K_TP||/||K||`를 근거로 terminal coupling이 temporal probability error보다 크다고 표현했다. 그 크기 비교는 정당하지 않다.

일반 단위에서 K=S^(-1)(H-i hbar D)는 에너지 차원을 가지며 확률 오차는 무차원이다. 비율은 무차원이지만 여전히 기저 좌표와 시간 의존 위상 convention에 영향을 받는다. 더구나 한 시각의 행렬 크기는 남은 시간 적분의 크기가 아니다.

예를 들어 S=I, H=[[0,g],[g,0]], D=0에서 계수 기저 변환 R=diag(1,r)을 하면 K'=R^(-1)KR의 K'_12=rg로 변한다. 같은 물리 상태와 projector를 변환하면 selected population은 변하지 않는다. 또한 전체 기저에 공통 시간 위상을 주면 K의 대각에 상수 항을 더해 cross/full ratio를 바꿀 수 있다.

따라서 기존 raw block 지표는 같은 좌표 convention에서 비교하는 engineering diagnostic으로 유지하되, tail error가 이미 지배한다거나 asymptotic decoupling의 충분조건으로 해석하지 않는다. finite-window 오차와 basis 오차의 상대 순위는 아직 측정되지 않았다.

## 새 유도: selected-span population의 순간 변화율

가정: 유한 Galerkin basis B(t), S=B†B>0, H=B†Hhat B=H†, D=B†Bdot, Sdot=D+D†. 직전 basis/frame/ETF convention을 유지한다. 단위는 이 일반식에서 hbar를 보존하고, 저장 배열 계산에만 명시된 a0/Eh/atomic-time convention에 따라 hbar=1을 쓴다.

    i hbar S cdot = (H-i hbar D)c,
    A = -(i/hbar) solve(S,H) - solve(S,D),
    cdot = A c.

현재 선택자는 J=[e9,e10,e12,e13,e14]로 고정되고 positive pseudostates [11,15,16,17]은 제외된다.

    G = J† S J,
    Q = S J G^(-1) J† S,
    P = c† Q c.

Q는 계수공간에서의 covariant quadratic-form matrix이며, 보통 Q²=Q를 요구하는 것이 아니다. 올바른 projector 항등식은 Q S^(-1) Q=Q다.

고정 J에 대해:

    Qdot = Sdot J G^(-1) J† S
         + S J G^(-1) J† Sdot
         - S J G^(-1) (J† Sdot J) G^(-1) J† S.

따라서

    W = Qdot + A†Q + QA,
    Pdot = c† W c,
    rho = || S^(-1/2) W S^(-1/2) ||_2,
    |Pdot| <= (c† S c) rho.

W는 Hermitian이고 rho의 단위는 inverse time이다. S=L L†의 Cholesky를 쓰면 generalized Hermitian eigenproblem은 L^(-1) W L^(-†)로 계산한다. 입력 행렬을 clipping, regularization, hidden mode deletion으로 고치지 않는다. 검사 통과 후 eigensolver용 roundoff Hermitian part 사용을 코드에 명시했다.

R(t)에 의한 좌표변환에서 S'=R†SR, D'=R†DR+R†S Rdot, J'=R^(-1)J이며 Jdot'도 함께 변환해야 한다. 그러면 W'=R†WR이고 generalized spectrum 및 rho는 불변이다. 원래 J가 상수여도 바뀐 좌표에서 Jdot'=0으로 놓으면 안 된다.

이 진단은 단순 target/projectile block뿐 아니라 같은 중심 안의 selected-bound span과 excluded pseudostates 사이의 변화도 반영한다.

연속적인 정확한 모델에서 정상화 norm=1과 전체 미래 구간의 rho 상계를 확보했다면

    |P(t2)-P(t1)| <= integral_{t1}^{t2} rho(t) dt

가 따른다. 그러나 이번에는 그 적분도 무한구간 지배함수도 확보하지 않았다. 8개 표본이나 empirical power-law fitting은 이 적분의 인증 상계가 아니다. Sdot=D+D†를 대입해 얻은 metric identity residual도 독립 finite-difference derivative 검증은 아니다.

## 저장된 endpoint에서 실제 계산한 값

13개 pinned input의 bytes를 대조하고 기존 S,H,D 및 N1536 final c만 읽었다. 새 operator 평가나 시간전파는 없다.

- P_selected = 0.009653428615023815
- Pdot = +1.6382726202381236e-4 / atomic time
- rho = 6.2271258107070085e-3 / atomic time
- v=2.00798106651023 a0/atomic time 이므로 dP/dz=8.1588051180450567e-5 / a0
- norm = 1.0000000000000189
- W Hermiticity defect ~2.67e-18
- metric algebraic identity residual ~1.87e-16

이는 같은 유한 Galerkin 모델에서 archived state를 지나는 local derivative다. Numerical one-step difference도, 실제 전체 Hilbert-space 해의 derivative도 아니다. 이 endpoint에서 local slope가 0이 아니지만 이 한 값만으로 총 window error를 추정하지 않는다. 새 ±16/20/24/32에는 c(t)가 아직 없으므로 Pdot 값을 만들어 넣지 않고 상태 비의존 rho만 계산할 수 있다.

## 검산 상태

Wolfram의 exact rational 3x3 예제에서 S 양정치, Q/W Hermitian, metric 부호 항등식, 시간 의존 좌표변환 Q/W 공변성, generalized characteristic polynomial 불변성 7개를 확인했다. 이는 일반 증명의 대체가 아니라 독립 exact algebra 회귀다. 첫 호출의 별도 basis-count Table iterator 오류는 보존하고 Map으로 고쳐 18/46/92/124와 8×11=88을 확인했다.

Python 연구 코드 `projector_rate_probe.py`의 synthetic 검증15개와 `tail_plan_adapter.py`의 신규 RED→GREEN 검증10개가 **총25 passed**했다. 입력 package의40개와 별개인 테스트다. Wolfram이 18×18 실제 endpoint를 다시 계산했다고 주장하지 않는다. 해당 실데이터는 Python에서 계산했고 Wolfram은 정확한 유도 항등식 및 반환 산술을 확인했다.

## 다음 실행을 작게 고정

현재 구현 패키지 README는 명시적으로 preparation-only이며 native launcher가 없다. `40 passed`를 native executor 검증으로 오독하지 않는다. 전달한 어댑터는 다음을 이미 구현했다.

1. 기존 signed z/time_hex를 그대로 보존한다.
2. PLAN_ONLY query_id와 qualified-provider runtime query_id를 구분한다.
3. 새 B0_STATIC_TAIL_CONTEXT를 만들고 기존 provider schema로 8개 runtime ID를 생성한다.
4. static operator에서 실제 sample z/R/time을 사용해 양방향 TP/PT block 지표와 rho를 계산한다.
5. 없는 미래 c(t)를 합성하지 않는다.
6. static에서 실제 실행하지 않은 metric-derivative/temporal screen은 true로 표시하지 않는다.

네이티브 어댑터와 기존 worker/provider/supervisor 연결은 아직 수행하지 않았다. 이는 원본 준비 패키지의 결함이 아니라 다음 실행 단계의 남은 경계다. 새로운 승인 가능한 source identity는 이 연결과 native-trap 검증 이후 고정해야 한다.

다음 workload는 B0 고정8점: z=-16,+16,-20,+20,-24,+24,-32,+32 a0, E=100 keV/u, b=2 a0. max88은 전체 static raw-operator evaluation 상한으로 내부 contraction call 수가 아니다. 11개 기존 ladder와 3개 static screens를 유지하고, exhaustion 시 보존·중단한다. 희박한 tail에서 상대오차 screen이 실패해도 tolerance/floor를 자동 변경하지 않는다.

32 worker pilot을 반복할 이유가 없다. 4 worker(최대8) single-thread 사용은 자원 제안일 뿐 미승인이다. 공유호스트 정책은 COOPERATIVE_SHARED_HOST로 유지한다. 실제 CPU/RAM/wall/cost와 새로운 ID는 한 번의 완성된 proposal에 묶는다. 권장 wall3600s도 측정된 runtime 상계가 아니며 새 native 승인 전까지 값은 제안이다.

B1–B3의 higher-l blocker는 B0 tail workload를 막지 않는다. 18/46/92/124는 registry count이고 수치적인 중첩공간/Gram/continuum completeness 증명이 아니다. Higher-l backend/actual coefficient binding은 별도 후속 scope다.

## 문헌 근거와 선택

Artacho–O’Regan, PRB95 115155 (2017), DOI10.1103/PhysRevB.95.115155: moving/nonorthogonal basis의 connection과 derivative를 기하학적으로 구분한다. 위 W 식은 이 응답에서 직접 유도한 것이며 논문의 특정 식을 확인 없이 인용하지 않는다.

Toshima, PRA59 1981 (1999), DOI10.1103/PhysRevA.59.1981: pseudostate placement에 따라 convergence가 달라진다는 원 연구. Symmetric basis를 크게 만들기만 하면 항상 최적/완전하다는 주장은 하지 않는다.

Runge–Micha, PRA53 1388 (1996), DOI10.1103/PhysRevA.53.1388: ETF, basis type/size, time-dependent populations 관련. 논문의 에너지 범위는 주로10keV 이하로, 현재100keV/u endpoint cutoff의 정량 근거로 쓰지 않는다.

위 문헌은 SciSpace 검색과 primary publisher abstract까지 교차확인했다. 이 루프에서 원문 전체를 읽었다고 주장하지 않는다.

## 종료 및 claim

이번 종료: R4P0 준비 승인 + B0 tail 연구진단/계획 어댑터 구현·테스트 완료. New native0, 새 nonce0, N1536 재전파0. 다음은 기존 검증된 자원/worker/supervisor를 이용한 얇은 runtime binding 및 단일 승인 proposal 생성이다. Native 승인 전에는 stop. 새 기저/full window/참조/impact-parameter 적분은 수행하지 않는다.

capture=false; production=HOLD; all_bound=OPEN; b_grid=NO_GO;
original_capture_gap_resolved=false; continuous_global_supremum_bound=false;
continuous_trajectory_error_bound=false.
